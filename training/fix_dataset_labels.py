# -*- coding: utf-8 -*-
"""
fix_dataset_labels.py — 训练数据标签清洗工具（先审计，再按需移动）

背景
----
当前模型的部分类别存在标签污染（合并多个数据集时未按图片内容重新标注），
例如 class_4/5（玉米叶斑病）里实际是玉米锈病图片、class_18（葡萄健康）里
实际是葡萄黑腐病等。本脚本通过 PlantVillage 文件名规则解码图片内容，
产出逐类审计报告；--apply 时把"已确证错标"的图片复制到正确的类别文件夹，
合并同作物重复"健康"类，并用旧映射为未确证类补中文名，
最后生成新的 dataset.yaml 与 class_names.json。

用法
----
# 1) 只审计（不修改任何文件，推荐先跑这个）
python fix_dataset_labels.py --train D:/data/train --val D:/data/val

# 2) 清洗：确证错标图片归位 + 健康类合并 + 中文名填充
python fix_dataset_labels.py --train D:/data/train --val D:/data/val \
       --out D:/data/cleaned --name-map models/class_names.json --min-per-class 5 --apply

# 3) 用生成的数据集重训：python training/train_yolov8.py --data D:/data/cleaned/dataset.yaml ...

说明
----
- 只移动"确证"的错标（文件名规则与多个类别交叉验证一致），其余图片保持原位，
  并在报告中标出需要人工复核的类别。
- 健康(HL)类无法仅凭文件名区分作物，不做跨作物移动；但同作物重复健康类会合并。
- 未确证图片所在的原 class_N 类若旧映射有中文名且不冲突，则自动补中文名；
  否则保留 class_N 占位标签，请在生成的 class_names.json 中人工补填。
"""

import argparse
import collections
import json
import os
import re
import shutil

# ============================================================
# 已验证的 PlantVillage 病害码 -> (作物, 中文名)
# 依据：文件名解码 + 多类别交叉验证（见项目 README 的"已知问题"）
# ============================================================
CODE_TABLE = {
    # 玉米（PlantVillage Corn 系）
    'C.Rust': ('玉米', '玉米锈病'),
    'GLSp': ('玉米', '玉米灰斑病'),
    'NLB': ('玉米', '玉米大斑病'),
    # 葡萄（PlantVillage Grape 系）
    'B.Rot': ('葡萄', '葡萄黑腐病'),
    'B.Msls': ('葡萄', '葡萄黑麻疹'),
    'L.Blight': ('葡萄', '葡萄叶枯病'),
    # 柑橘黄龙病（HLB 多种写法）
    'HLB': ('柑橘', '柑橘黄龙病'),
    'Citrus_HLB': ('柑橘', '柑橘黄龙病'),
    'GHLB': ('柑橘', '柑橘黄龙病'),
    'GHLB2': ('柑橘', '柑橘黄龙病'),
    'GHLB_PS': ('柑橘', '柑橘黄龙病'),
    'CREC_HLB': ('柑橘', '柑橘黄龙病'),
    # 番茄
    'Bact.S': ('番茄', '番茄细菌性斑点病'),
    'Bact.Sp': ('番茄', '番茄细菌性斑点病'),
    'BS': ('番茄', '番茄细菌性斑点病'),
    'B.Spot': ('番茄', '番茄细菌性斑点病'),
    'YLCV': ('番茄', '番茄黄化曲叶病毒'),
    'L.Mold': ('番茄', '番茄叶霉病'),
    'Leaf.Mold': ('番茄', '番茄叶霉病'),
    'Sept.L.S': ('番茄', '番茄斑枯病'),
    'SpM': ('番茄', '番茄红蜘蛛'),
    'TgS': ('番茄', '番茄靶斑病'),
    'Pwd.M': ('番茄', '番茄白粉病'),
    'Powd.M': ('番茄', '番茄白粉病'),
    # 草莓
    'L.Scorch': ('草莓', '草莓叶焦病'),
    # 马铃薯
    'L.B': ('马铃薯', '马铃薯晚疫病'),
    'LB': ('马铃薯', '马铃薯晚疫病'),
    'Late.B': ('马铃薯', '马铃薯晚疫病'),
    'Early.B': ('马铃薯', '马铃薯早疫病'),
    'Erly.B': ('马铃薯', '马铃薯早疫病'),
    # 苹果
    'Scab': ('苹果', '苹果黑星病'),
    # 大豆
    'FrgE.S': ('大豆', '大豆蛙眼叶斑病'),
}

# 文件名里需要忽略的地点/拍摄前缀（按 "_" 分段后命中即跳过）
LOCATION_PREFIXES = {
    'UF.GRC', 'UF.NREC', 'FREC', 'GCREC', 'NREC', 'JR', 'FAM', 'RS', 'R.S',
    'GH', 'Rutg', 'Rut', 'CREC', 'UMD', 'MD', 'Com.G', 'Matt.S', 'PSU',
    'Crnl', 'Mt.N.V', 'Keller.St', 'Lab', 'Field', 'Leaf', 'PS', 'Day', 'FL',
}

# 作物清单（用于合并同作物重复健康类）
CROPS = ['玉米', '番茄', '葡萄', '黄瓜', '樱桃', '草莓', '水稻', '小麦',
         '苹果', '柑橘', '马铃薯', '棉花', '大豆']


def normalize_healthy(label):
    """把 '玉米健康_2' 这类同作物重复健康类合并为 '玉米健康'"""
    for crop in CROPS:
        if label.startswith(crop + '健康'):
            return crop + '健康'
    return label


def decode_filename(fn):
    """返回 (kind, info)：
    kind: pv_ok(可解码) / pv_hl(健康) / pv_unknown(码未知) / md5(AI-Challenger) / other"""
    base = os.path.basename(fn)
    if re.match(r'^[0-9a-f]{32}\.(jpg|jpeg|png)$', base, re.I):
        return ('md5', 'AI-Challenger')
    if base.startswith(('IMG_', 'u=')):
        return ('other', 'field/other')

    m = re.search(r'___([A-Za-z._ ]+?)(?:\s+|-?\d)', base)
    if not m:
        return ('other', 'no_pattern')

    seg = m.group(1)
    parts = [p for p in seg.split('_') if p not in LOCATION_PREFIXES]
    if not parts:
        return ('pv_unknown', seg[:60])
    # 优先匹配更长的码（避免 HLB 被 HL 误判、Bact.S 被 Bact.Sp 误判）
    codes_sorted = sorted(CODE_TABLE.keys(), key=len, reverse=True)
    for p in parts:
        for code in codes_sorted:
            if code in p:
                return ('pv_ok', code)
    if any(p == 'HL' for p in parts):
        return ('pv_hl', 'HL')
    return ('pv_unknown', seg[:60])


def audit(split_dir):
    """逐类审计：返回 {class_name: Counter((kind, info))}"""
    result = {}
    if not os.path.isdir(split_dir):
        return result
    for cls in sorted(os.listdir(split_dir)):
        d = os.path.join(split_dir, cls)
        if not os.path.isdir(d):
            continue
        cnt = collections.Counter()
        for fn in os.listdir(d):
            kind, info = decode_filename(fn)
            cnt[(kind, info)] += 1
        result[cls] = cnt
    return result


def print_audit(audit_map, title):
    print(f"\n{'=' * 70}\n【{title}】逐类审计\n{'=' * 70}")
    for cls, cnt in sorted(audit_map.items()):
        total = sum(cnt.values())
        parts = []
        for (kind, info), n in cnt.most_common(6):
            tag = {'pv_ok': '✅可解码', 'pv_hl': '🟡健康', 'pv_unknown': '❓码未知',
                   'md5': '⬜AI-Challenger', 'other': '⬜其他'}[kind]
            parts.append(f"{tag}{info}×{n}")
        print(f"{cls} (n={total}): " + " | ".join(parts))


def build_label_plan(train_audit, name_map_path):
    """返回 (cls_to_label, label_to_folder)：
    - 确证类：中文名
    - 未确证类：旧映射中文名（唯一时）或 class_N 占位
    - 同作物重复健康类合并"""
    verified = sorted(set(name for _, name in CODE_TABLE.values()))
    old_map = {}
    if name_map_path and os.path.exists(name_map_path):
        with open(name_map_path, encoding='utf-8') as f:
            old_map = json.load(f)

    final_labels = set(verified)
    cls_to_label = {}
    for cls in sorted(train_audit.keys()):
        label = cls
        m = re.match(r'^class_(\d+)$', cls)
        if m and str(int(m.group(1))) in old_map:
            cn = old_map[str(int(m.group(1)))]
            if cn and cn not in final_labels:  # 与确证类不冲突才填充
                label = cn
        label = normalize_healthy(label)
        final_labels.add(label)
        cls_to_label[cls] = label

    final_labels = sorted(final_labels)
    # 分类训练(YOLOv8-cls)的类名直接取文件夹名，因此文件夹直接用标签（中文名）命名
    label_to_folder = {label: label for label in final_labels}
    return cls_to_label, label_to_folder


def clean_split(src_dir, out_dir, cls_to_label, label_to_folder, dry_run=True):
    """复制清洗后的图片到 out_dir"""
    moved = collections.Counter()
    if not os.path.isdir(src_dir):
        return moved
    for cls in sorted(os.listdir(src_dir)):
        d = os.path.join(src_dir, cls)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            kind, info = decode_filename(fn)
            src = os.path.join(d, fn)
            if kind == 'pv_ok':
                crop, name = CODE_TABLE[info]
                label = normalize_healthy(name)
            else:
                # 未确证：保留在原类（映射到其规划标签）
                label = cls_to_label.get(cls, cls)
            folder = label_to_folder.get(label, label)
            tdir = os.path.join(out_dir, folder)
            os.makedirs(tdir, exist_ok=True)
            if not dry_run:
                shutil.copy2(src, os.path.join(tdir, fn))
            moved[folder] += 1
    return moved


def main():
    ap = argparse.ArgumentParser(description='训练数据标签清洗工具')
    ap.add_argument('--train', required=True, help='train 目录（含 class_N 子目录）')
    ap.add_argument('--val', default='', help='val 目录（可选）')
    ap.add_argument('--out', default='', help='清洗输出目录（--apply 时必填）')
    ap.add_argument('--min-per-class', type=int, default=5, help='样本少于该数的类别将被剔除')
    ap.add_argument('--name-map', default='', help='旧类别映射JSON(class编号->中文名)，用于给未确证类自动补中文名（如仓库 models/class_names.json）')
    ap.add_argument('--apply', action='store_true', help='真正执行清洗（默认仅审计）')
    args = ap.parse_args()

    # 1) 审计
    train_audit = audit(args.train)
    print_audit(train_audit, '训练集')
    if args.val:
        print_audit(audit(args.val), '验证集')

    # 2) 统计确证错标量
    bad = 0
    total = 0
    for cls, cnt in train_audit.items():
        for (kind, info), n in cnt.items():
            total += n
            if kind == 'pv_ok':
                bad += n
    print(f"\n总计 {total} 张，其中按文件名确证应移动到其他类别（错标）的约 {bad} 张。")

    if not args.apply:
        print("\n（审计模式）如需清洗请加 --apply --out <目录>。")
        return

    if not args.out:
        raise SystemExit("--apply 模式下必须提供 --out 输出目录")

    # 3) 标签规划：确证类=中文名；未确证类=旧映射中文名或 class_N 占位；健康类合并
    cls_to_label, label_to_folder = build_label_plan(train_audit, args.name_map)

    # 4) 清洗（复制到 out）
    out_train = os.path.join(args.out, 'train')
    out_val = os.path.join(args.out, 'val')
    moved = clean_split(args.train, out_train, cls_to_label, label_to_folder, dry_run=not args.apply)
    if args.val:
        clean_split(args.val, out_val, cls_to_label, label_to_folder, dry_run=not args.apply)

    # 5) 剔除小样本类 + 生成 dataset.yaml / class_names.json
    folder_to_label = {v: k for k, v in label_to_folder.items()}
    keep = {}
    for folder, n in moved.items():
        label = folder_to_label.get(folder, folder)
        if n < args.min_per_class:
            print(f"⚠️  剔除小样本类 {label} (n={n})")
            continue
        keep[label] = n

    names = {}
    for idx, label in enumerate(sorted(keep.keys())):
        names[idx] = label

    # 6) 清理输出目录中被剔除的小样本类文件夹（避免被当成类别参与训练）
    for split in ('train', 'val'):
        split_dir = os.path.join(args.out, split)
        if os.path.isdir(split_dir):
            for folder in os.listdir(split_dir):
                if folder not in keep:
                    shutil.rmtree(os.path.join(split_dir, folder))
                    print(f"🗑️  已清理小样本类文件夹: {split}/{folder}")

    yaml_path = os.path.join(args.out, 'dataset.yaml')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(f"path: {os.path.abspath(args.out)}\ntrain: train\nval: val\n\nnames:\n")
        for idx, label in names.items():
            f.write(f"  {idx}: {label}\n")
    print(f"\n✅ 已生成 {yaml_path}（{len(names)} 类）")

    cls_json = os.path.join(args.out, 'class_names.json')
    with open(cls_json, 'w', encoding='utf-8') as f:
        json.dump({str(k): v for k, v in names.items()}, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成 {cls_json} —— 请人工核对未确证类的中文名后复制到仓库 models/ 覆盖 class_names.json")

    print("\n下一步：python training/train_yolov8.py --data " + yaml_path)


if __name__ == '__main__':
    main()
