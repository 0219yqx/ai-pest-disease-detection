# -*- coding: utf-8 -*-
"""
fix_dataset_labels.py — 训练数据标签清洗工具（先审计，再按需移动）

背景
----
当前模型的部分类别存在标签污染（合并多个数据集时未按图片内容重新标注），
例如 class_4/5（玉米叶斑病）里实际是玉米锈病图片、class_18（葡萄健康）里
实际是葡萄黑腐病等。本脚本通过 PlantVillage 文件名规则解码图片内容，
产出逐类审计报告；--apply 时把"已确证错标"的图片复制到正确的类别文件夹，
并生成新的 dataset.yaml 与 class_names.json。

用法
----
# 1) 只审计（不修改任何文件，推荐先跑这个）
python fix_dataset_labels.py --train D:/data/train --val D:/data/val

# 2) 清洗：把确证错标的图片复制到 --out 下的新分类结构
python fix_dataset_labels.py --train D:/data/train --val D:/data/val \
       --out D:/data/cleaned --min-per-class 5 --apply

# 3) 用生成的数据集重训：python train_yolov8.py --data D:/data/cleaned/dataset.yaml ...

说明
----
- 只移动"确证"的错标（文件名规则与多个类别交叉验证一致），其余图片保持原位，
  并在报告中标出需要人工复核的类别。
- 健康(HL)类因无法从文件名区分作物，不做跨作物移动。
- 未确证图片所在的原 class_N 类会保留为占位标签（class_N 字符串），
  请在生成的 class_names.json 中人工补填中文名后再用于训练。
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


def clean_split(src_dir, out_dir, cls_of, dry_run=True):
    """复制清洗后的图片到 out_dir。cls_of: 标签名 -> class_N 目录名"""
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
                target_cls = cls_of[name]
            else:
                # 未确证：保留在原类（原 class_N 作为占位标签）
                target_cls = cls_of.get(cls, cls)
            tdir = os.path.join(out_dir, target_cls)
            os.makedirs(tdir, exist_ok=True)
            if not dry_run:
                shutil.copy2(src, os.path.join(tdir, fn))
            moved[target_cls] += 1
    return moved


def main():
    ap = argparse.ArgumentParser(description='训练数据标签清洗工具')
    ap.add_argument('--train', required=True, help='train 目录（含 class_N 子目录）')
    ap.add_argument('--val', default='', help='val 目录（可选）')
    ap.add_argument('--out', default='', help='清洗输出目录（--apply 时必填）')
    ap.add_argument('--min-per-class', type=int, default=5, help='样本少于该数的类别将被剔除')
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

    # 3) 标签表：确证类=中文名；未确证类=原 class_N 字符串（占位，需人工补中文）
    verified = sorted(set(name for _, name in CODE_TABLE.values()))
    labels = sorted(set(verified + list(train_audit.keys())))
    cls_of = {}
    for idx, label in enumerate(labels):
        cls_of[label] = f'class_{idx}'

    # 4) 清洗（复制到 out）
    out_train = os.path.join(args.out, 'train')
    out_val = os.path.join(args.out, 'val')
    moved = clean_split(args.train, out_train, cls_of, dry_run=not args.apply)
    if args.val:
        clean_split(args.val, out_val, cls_of, dry_run=not args.apply)

    # 5) 剔除小样本类 + 生成 dataset.yaml / class_names.json
    # 注意：文件夹名是 class_{新索引}，标签要用回中文名（或原 class_N 占位名）
    folder_to_label = {v: k for k, v in cls_of.items()}
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

    print("\n下一步：python train_yolov8.py --data " + yaml_path)


if __name__ == '__main__':
    main()
