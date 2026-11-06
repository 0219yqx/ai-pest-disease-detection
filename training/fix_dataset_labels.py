# -*- coding: utf-8 -*-
"""
fix_dataset_labels.py — 训练数据标签清洗（先审计，再按需复制）

背景
----
合并 PlantVillage、AI Challenger 和自采图片时，有些文件夹的中文名和图片内容对不上。
例如标成「玉米叶斑病」的目录里，文件名解码出来是玉米锈病。本脚本只根据
PlantVillage 文件名里的病害码移动「已经对得上码」的图片，其余原样保留并写进报告。

它还会：
- 把「玉米健康_2」这类重复健康类合并成「玉米健康」
- 丢掉训练+验证合计少于 --min-per-class 的类（以及训练集里一张都没有的类）
- 写出 YOLOv8-cls 需要的 train/<类别名>、val/<类别名> 目录
- 写出与文件夹 Unicode 排序一致的 class_names.json（编号 0..N-1，无空缺）

用法
----
# 只审计，不写图片
python training/fix_dataset_labels.py --train D:/data/train --val D:/data/val \\
    --name-map models/class_names.json --report audit_report.md

# 复制到新目录（不改原始数据）。目录已存在时加 --force
python training/fix_dataset_labels.py --train D:/data/train --val D:/data/val \\
    --out D:/data/cleaned --name-map models/class_names.json \\
    --min-per-class 5 --apply

说明
----
- 默认不修改任何图片。--apply 只往 --out 复制，不会移动或删除原始数据。
- --out 不能和 train/val 是同一目录，也不能互相包含。
- 健康(HL)文件名看不出作物，不跨作物搬动；同作物重复健康类会合并。
- 文件名对不上码的图片留在原类（用 --name-map 补中文名，否则保留 class_N）。
"""

from __future__ import annotations

import argparse
import collections
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ai.class_names import (  # noqa: E402
    load_class_names,
    normalize_healthy,
    write_class_names,
)

# 已核对过的 PlantVillage 病害码 -> (作物, 中文名)
CODE_TABLE = {
    "C.Rust": ("玉米", "玉米锈病"),
    "GLSp": ("玉米", "玉米灰斑病"),
    "NLB": ("玉米", "玉米大斑病"),
    "B.Rot": ("葡萄", "葡萄黑腐病"),
    "B.Msls": ("葡萄", "葡萄黑麻疹"),
    "L.Blight": ("葡萄", "葡萄叶枯病"),
    "HLB": ("柑橘", "柑橘黄龙病"),
    "Citrus_HLB": ("柑橘", "柑橘黄龙病"),
    "GHLB": ("柑橘", "柑橘黄龙病"),
    "GHLB2": ("柑橘", "柑橘黄龙病"),
    "GHLB_PS": ("柑橘", "柑橘黄龙病"),
    "CREC_HLB": ("柑橘", "柑橘黄龙病"),
    "Bact.S": ("番茄", "番茄细菌性斑点病"),
    "Bact.Sp": ("番茄", "番茄细菌性斑点病"),
    "BS": ("番茄", "番茄细菌性斑点病"),
    "B.Spot": ("番茄", "番茄细菌性斑点病"),
    "YLCV": ("番茄", "番茄黄化曲叶病毒"),
    "L.Mold": ("番茄", "番茄叶霉病"),
    "Leaf.Mold": ("番茄", "番茄叶霉病"),
    "Sept.L.S": ("番茄", "番茄斑枯病"),
    "SpM": ("番茄", "番茄红蜘蛛"),
    "TgS": ("番茄", "番茄靶斑病"),
    "Pwd.M": ("番茄", "番茄白粉病"),
    "Powd.M": ("番茄", "番茄白粉病"),
    "L.Scorch": ("草莓", "草莓叶焦病"),
    "L.B": ("马铃薯", "马铃薯晚疫病"),
    "LB": ("马铃薯", "马铃薯晚疫病"),
    "Late.B": ("马铃薯", "马铃薯晚疫病"),
    "Early.B": ("马铃薯", "马铃薯早疫病"),
    "Erly.B": ("马铃薯", "马铃薯早疫病"),
    "Scab": ("苹果", "苹果黑星病"),
    "FrgE.S": ("大豆", "大豆蛙眼叶斑病"),
}

LOCATION_PREFIXES = {
    "UF.GRC", "UF.NREC", "FREC", "GCREC", "NREC", "JR", "FAM", "RS", "R.S",
    "GH", "Rutg", "Rut", "CREC", "UMD", "MD", "Com.G", "Matt.S", "PSU",
    "Crnl", "Mt.N.V", "Keller.St", "Lab", "Field", "Leaf", "PS", "Day", "FL",
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
VERIFIED_LABELS = {normalize_healthy(name) for _, name in CODE_TABLE.values()}
_CODES_BY_LEN = sorted(CODE_TABLE, key=len, reverse=True)


def decode_filename(filename: str):
    """返回 (kind, info)。

    kind:
      pv_ok       病害码能对上 CODE_TABLE，info 是码
      pv_hl       健康叶片（HL），看不出作物
      pv_unknown  像 PlantVillage 文件名，但码不在表里
      md5         AI Challenger 那类 32 位十六进制文件名
      other       自采或无法解析
    """
    base = os.path.basename(filename)
    if re.match(r"^[0-9a-f]{32}\.(jpg|jpeg|png|bmp|webp|tif|tiff)$", base, re.I):
        return ("md5", "AI-Challenger")
    if base.startswith(("IMG_", "u=")):
        return ("other", "field/other")

    matched = re.search(r"___([A-Za-z._ ]+?)(?:\s+|-?\d)", base)
    if not matched:
        return ("other", "no_pattern")

    segment = matched.group(1)
    parts = [part for part in segment.split("_") if part not in LOCATION_PREFIXES]
    if not parts:
        return ("pv_unknown", segment[:60])
    for part in parts:
        if part in CODE_TABLE:
            return ("pv_ok", part)
    for part in parts:
        for code in _CODES_BY_LEN:
            if code in part:
                return ("pv_ok", code)
    if any(part == "HL" for part in parts):
        return ("pv_hl", "HL")
    return ("pv_unknown", segment[:60])


def _is_image(name: str) -> bool:
    return Path(name).suffix.lower() in IMAGE_EXTS


def list_class_dirs(split_dir: Path) -> list[str]:
    if not split_dir.is_dir():
        return []
    return sorted(path.name for path in split_dir.iterdir() if path.is_dir())


def load_name_map(path: str) -> dict[str, str]:
    if not path:
        return {}
    file_path = Path(path)
    if not file_path.is_file():
        raise SystemExit(f"找不到 --name-map: {file_path}")
    mapping = load_class_names(file_path)
    return {str(index): name for index, name in mapping.items()}


def build_label_plan(class_names: list[str], name_map: dict[str, str]) -> dict[str, str]:
    """原文件夹名 → 清洗后的类别名。

    文件名确证过的病害名（如「玉米锈病」）不会套到对不上码的残留图片上，
    那些图片继续用 class_N。重复健康类会收成同一个名字，方便合并到一个文件夹。
    """
    plan = {}
    for class_name in class_names:
        label = class_name
        match = re.fullmatch(r"class_(\d+)", class_name)
        if match:
            mapped = name_map.get(str(int(match.group(1))))
            if mapped and normalize_healthy(mapped) not in VERIFIED_LABELS:
                label = mapped
        label = normalize_healthy(label)
        if not label or label in {".", ".."} or "/" in label or "\\" in label:
            raise SystemExit(f"非法类别名 {label!r}（来自文件夹 {class_name}）")
        plan[class_name] = label
    return plan


def decide_label(class_name: str, filename: str, label_plan: dict[str, str]):
    """返回 (目标类别, 原因, kind, info)。"""
    planned = label_plan.get(class_name, normalize_healthy(class_name))
    kind, info = decode_filename(filename)
    if kind == "pv_ok":
        _crop, disease = CODE_TABLE[info]
        label = normalize_healthy(disease)
        reason = "confirmed-ok" if label == planned else "move"
        return label, reason, kind, info
    if kind == "pv_hl" and not planned.endswith("健康"):
        return planned, "healthy-in-disease", kind, info
    if kind == "pv_hl":
        return planned, "healthy", kind, info
    return planned, "stay", kind, info


def iter_images(split_dir: Path):
    for class_name in list_class_dirs(split_dir):
        folder = split_dir / class_name
        for name in sorted(os.listdir(folder)):
            path = folder / name
            if path.is_file() and _is_image(name):
                yield class_name, path


def collect_plan(split_dirs: dict[str, Path], label_plan: dict[str, str]):
    """split -> list of (src, label, reason, kind, info, class_name)。"""
    planned = {split: [] for split in split_dirs}
    for split, directory in split_dirs.items():
        if not directory.is_dir():
            continue
        for class_name, path in iter_images(directory):
            label, reason, kind, info = decide_label(class_name, path.name, label_plan)
            planned[split].append((path, label, reason, kind, info, class_name))
    return planned


def count_labels(planned) -> tuple[dict, dict]:
    total = collections.Counter()
    train = collections.Counter()
    for split, rows in planned.items():
        for _path, label, _reason, _kind, _info, _class_name in rows:
            total[label] += 1
            if split == "train":
                train[label] += 1
    return total, train


def classes_to_drop(total: dict, train: dict, min_per_class: int) -> dict[str, str]:
    dropped = {}
    labels = set(total) | set(train)
    for label in sorted(labels):
        train_n = train.get(label, 0)
        all_n = total.get(label, 0)
        if train_n < 1:
            dropped[label] = f"训练集 0 张（验证集 {all_n} 张），分类训练用不上"
        elif all_n < min_per_class:
            dropped[label] = f"训练+验证共 {all_n} 张，少于 {min_per_class}"
    return dropped


def _paths_overlap(left: Path, right: Path) -> bool:
    left = left.resolve()
    right = right.resolve()
    return left == right or left in right.parents or right in left.parents


def _unique_destination(folder: Path, filename: str) -> Path:
    target = folder / filename
    if not target.exists():
        return target
    stem, ext = os.path.splitext(filename)
    index = 1
    while True:
        candidate = folder / f"{stem}__dup{index}{ext}"
        if not candidate.exists():
            return candidate
        index += 1


def render_report(args, label_plan, planned, dropped, kept) -> str:
    lines = ["# 标签清洗审计", ""]
    lines.append(f"- train: `{args.train}`")
    lines.append(f"- val: `{args.val or '（未提供）'}`")
    lines.append(f"- 模式: {'apply 复制到 ' + args.out if args.apply else '仅审计，不写图片'}")
    lines.append(f"- 最少样本: {args.min_per_class}（训练+验证合计，且训练集至少 1 张）")
    lines.append("")

    kind_names = {
        "pv_ok": "文件名可解码",
        "pv_hl": "健康 HL",
        "pv_unknown": "码未知",
        "md5": "AI-Challenger",
        "other": "其他/自采",
    }
    grand = collections.Counter()
    move_pairs = collections.Counter()

    for split, rows in planned.items():
        split_total = len(rows)
        reasons = collections.Counter(row[2] for row in rows)
        kinds = collections.Counter(row[3] for row in rows)
        grand["images"] += split_total
        for key, value in reasons.items():
            grand[key] += value
        for key, value in kinds.items():
            grand["kind:" + key] += value
        lines.append(f"## {split}（{split_total} 张）")
        lines.append("")
        lines.append(
            f"- 确证且与规划标签一致: {reasons['confirmed-ok']}"
        )
        lines.append(f"- 确证错标，将改放到解码出的类别: {reasons['move']}")
        lines.append(f"- 健康文件名，留在原类: {reasons['healthy']}")
        lines.append(
            f"- 健康文件名出现在非健康类（无法凭文件名改作物，请人工看）: "
            f"{reasons['healthy-in-disease']}"
        )
        lines.append(f"- 未能解码，留在原类: {reasons['stay']}")
        lines.append("")
        for class_name in sorted({row[5] for row in rows}):
            bucket = collections.Counter()
            moves = collections.Counter()
            for _path, label, reason, kind, info, src_class in rows:
                if src_class != class_name:
                    continue
                bucket[(reason, kind, info, label)] += 1
                if reason == "move":
                    moves[label] += 1
                    move_pairs[(src_class, label)] += 1
            class_n = sum(bucket.values())
            planned_label = label_plan.get(class_name, class_name)
            move_text = ""
            if moves:
                detail = ", ".join(f"{name}×{count}" for name, count in moves.most_common(4))
                move_text = f"；错标去向 {detail}"
            lines.append(
                f"- `{class_name}` → `{planned_label}`（{class_n} 张）{move_text}"
            )
        lines.append("")
        lines.append("文件名类型: " + ", ".join(
            f"{kind_names[kind]} {kinds[kind]}"
            for kind in ("pv_ok", "pv_hl", "pv_unknown", "md5", "other")
            if kinds[kind]
        ))
        lines.append("")

    lines.append("## 汇总")
    lines.append("")
    lines.append(f"- 图片合计: {grand['images']}")
    lines.append(
        f"- 确证错标（解码病害 ≠ 文件夹规划标签）: {grand['move']}。"
        "只有这一项是按文件名确认的标签污染。"
    )
    lines.append(f"- 确证且已经在正确类别: {grand['confirmed-ok']}")
    decoded = grand["kind:pv_ok"]
    lines.append(
        f"- 文件名可解码合计: {decoded}。"
        "旧脚本曾把这一项全部当成错标；其中已经放对的不算错标。"
    )
    lines.append("")

    healthy_sources = collections.defaultdict(set)
    for rows in planned.values():
        for _path, label, _reason, _kind, _info, src_class in rows:
            if label.endswith("健康") and src_class != label:
                healthy_sources[label].add(src_class)
    lines.append("## 将合并的重复健康类")
    lines.append("")
    if not healthy_sources:
        lines.append("- 无（只列出确实有图片并入的健康类）")
    else:
        for label, sources in sorted(healthy_sources.items()):
            lines.append(f"- {', '.join(sorted(sources))} → {label}")
    lines.append("")

    lines.append("## 样本过少，不会进入训练集")
    lines.append("")
    if not dropped:
        lines.append("- 无")
    else:
        for label, reason in sorted(dropped.items()):
            lines.append(f"- {label}: {reason}")
    lines.append("")

    lines.append("## 保留的类别（按 YOLOv8-cls 排序，即 class_names.json 的编号）")
    lines.append("")
    if not kept:
        lines.append("- 无。检查 --min-per-class 是不是太大，或 train 目录是不是空的。")
    else:
        for index, label in enumerate(kept):
            lines.append(f"- {index}: {label}")
    lines.append("")

    if move_pairs:
        lines.append("## 错标搬动最多的去向")
        lines.append("")
        for (src, label), count in move_pairs.most_common(15):
            lines.append(f"- `{src}` → `{label}` × {count}")
        lines.append("")

    lines.append("## 指标怎么读")
    lines.append("")
    lines.append(
        "- 现役模型大约 86.6% 的 Top-1 是在污染验证标签上测的："
        "模型和验证集用同一套错误文件夹名，所以高分不能当成实地病名准确率。"
    )
    lines.append(
        "- 清洗之后的 top1/top5 只表示「和清洗后的文件夹一致」。"
        "文件名对得上的类比较可信；md5 和自采图片没有复核，文件夹仍可能是错的。"
    )
    lines.append(
        "- 清洗前后的准确率不能直接比：类别集合变了，标签含义也变了。"
    )
    lines.append("")
    return "\n".join(lines)


def _write_report(text: str, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(text, encoding="utf-8")
    print(f"[OK] 审计报告: {report_path}")


def _prepare_output(out: Path, sources: list[Path], force: bool) -> None:
    for source in sources:
        if source.exists() and _paths_overlap(out, source):
            raise SystemExit(
                f"--out ({out}) 和数据目录 ({source}) 重叠。"
                "清洗只会复制到一个新目录，不会在原始数据里改标签。"
            )
    occupied = [
        name for name in ("train", "val", "class_names.json", "dataset.yaml", "audit_report.md")
        if (out / name).exists()
    ]
    if occupied and not force:
        raise SystemExit(
            f"输出目录已有文件（{', '.join(occupied)}）: {out}\n"
            "加上 --force 会删掉其中的 train/、val/、class_names.json、dataset.yaml、audit_report.md 后重写。\n"
            "原始数据目录不会被删除。"
        )
    if force:
        for name in occupied:
            target = out / name
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
    out.mkdir(parents=True, exist_ok=True)


def _copy_kept(planned, kept_set: set[str], out: Path) -> dict[str, int]:
    copied = collections.Counter()
    for split, rows in planned.items():
        for src, label, _reason, _kind, _info, _class_name in rows:
            if label not in kept_set:
                continue
            dest_dir = out / split / label
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = _unique_destination(dest_dir, src.name)
            shutil.copy2(src, dest)
            copied[split] += 1
    return copied


def _write_dataset_yaml(out: Path, names: list[str]) -> Path:
    yaml_path = out / "dataset.yaml"
    lines = [
        f"path: {out.resolve().as_posix()}",
        "train: train",
        "val: val",
        "",
        "# YOLOv8-cls 训练请把数据集【目录】传给 --data，不要传这个 yaml。",
        "# 下面的编号必须与 class_names.json、sorted(train 文件夹名) 一致。",
        "names:",
    ]
    for index, name in enumerate(names):
        escaped = name.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  {index}: "{escaped}"')
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path


def run(args) -> None:
    train_dir = Path(args.train)
    if not train_dir.is_dir():
        raise SystemExit(f"训练集目录不存在: {train_dir}")
    val_dir = Path(args.val) if args.val else None
    if args.apply and (val_dir is None or not val_dir.is_dir()):
        raise SystemExit(
            " --apply 需要真实的 --val 目录（YOLOv8-cls 要 train/ 和 val/ 两套文件夹）。"
            f" 当前 --val={args.val!r}"
        )
    if val_dir is not None and not val_dir.is_dir():
        raise SystemExit(f"验证集目录不存在: {val_dir}")

    try:
        name_map = load_name_map(args.name_map)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    class_names = list_class_dirs(train_dir)
    if val_dir is not None:
        for name in list_class_dirs(val_dir):
            if name not in class_names:
                class_names.append(name)
        class_names = sorted(set(class_names))
    if not class_names:
        raise SystemExit(f"{train_dir} 下没有类别子目录")

    label_plan = build_label_plan(class_names, name_map)
    split_dirs = {"train": train_dir}
    if val_dir is not None:
        split_dirs["val"] = val_dir
    planned = collect_plan(split_dirs, label_plan)
    total, train_counts = count_labels(planned)
    dropped = classes_to_drop(total, train_counts, args.min_per_class)
    kept = sorted(label for label in total if label not in dropped and train_counts.get(label, 0) > 0)
    report = render_report(args, label_plan, planned, dropped, kept)
    print(report)

    report_path = Path(args.report) if args.report else None
    if args.apply:
        out = Path(args.out) if args.out else None
        if out is None:
            raise SystemExit("--apply 必须同时给出 --out，指向一个空的新目录")
        sources = [train_dir] + ([val_dir] if val_dir is not None else [])
        _prepare_output(out, sources, args.force)
        if not kept:
            raise SystemExit("清洗后没有可训练的类别。请调低 --min-per-class 或检查数据目录。")
        copied = _copy_kept(planned, set(kept), out)
        # 再按实际落盘的文件夹写编号，避免和 YOLOv8 的 sorted(目录名) 不一致。
        written = sorted(path.name for path in (out / "train").iterdir() if path.is_dir())
        if written != kept:
            raise SystemExit(
                "写出的类别文件夹和计划不一致:\n"
                f"  计划: {kept}\n  实际: {written}"
            )
        mapping = {index: name for index, name in enumerate(written)}
        write_class_names(out / "class_names.json", mapping)
        yaml_path = _write_dataset_yaml(out, written)
        if report_path is None:
            report_path = out / "audit_report.md"
        _write_report(report, report_path)
        print(
            f"[OK] 已复制 train {copied['train']} 张、val {copied['val']} 张到 {out}，"
            f"保留 {len(written)} 类。"
        )
        print(f"[OK] {out / 'class_names.json'}")
        print(f"[OK] {yaml_path}")
        print("下一步: python training/train_yolov8.py --data " + str(out))
        return

    if report_path is not None:
        _write_report(report, report_path)
    elif args.out:
        _write_report(report, Path(args.out) / "audit_report.md")
    print("[OK] 审计结束。确认报告后再加 --apply --out <新目录>。原始图片没有改动。")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="训练数据标签清洗（默认只审计）")
    parser.add_argument("--train", required=True, help="train 目录，子文件夹是类别")
    parser.add_argument("--val", default="", help="val 目录。--apply 时必填")
    parser.add_argument("--out", default="", help="清洗结果目录。--apply 时必填，且不能和原始数据重叠")
    parser.add_argument("--min-per-class", type=int, default=5, help="训练+验证少于此数的类别不进入结果")
    parser.add_argument("--name-map", default="", help="旧的 class_names.json，用来给 class_N 补中文名")
    parser.add_argument("--report", default="", help="审计报告路径。--apply 时默认写到 <out>/audit_report.md")
    parser.add_argument("--apply", action="store_true", help="把清洗结果复制到 --out。不加这个参数就不会写图片")
    parser.add_argument("--force", action="store_true", help="--out 里已有 train/val 时先清掉这些产物再重写")
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    if args.min_per_class < 1:
        raise SystemExit("--min-per-class 至少为 1")
    run(args)


if __name__ == "__main__":
    main()
