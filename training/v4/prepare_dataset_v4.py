# -*- coding: utf-8 -*-
"""Build dataset_v4 for the wheat fine-tune. Runs on the Windows PC, not CI.

1. Download Project-AgML/wheat_disease_detection (HF mirror by default).
2. Crop detection boxes into Ultralytics classify folders.
3. Junction (Windows) or symlink (elsewhere) every dataset_v3 class, including
   ``other``, and add the wheat folders beside them.
4. Write ``dataset_v4/class_names.json`` in alphabetical YOLO index order.

Dry run does not download or write the dataset::

    python training/v4/prepare_dataset_v4.py --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.v4.wheat_labels import (  # noqa: E402
    CATEGORIES,
    DEFAULT_MIN_CROPS,
    OTHER_DISPLAY,
    OTHER_FOLDER,
    V3_OTHER_INDEX,
    ZENODO_IMAGE_COUNTS,
    assign_image_splits,
    boxes_look_normalized,
    build_class_names,
    decide_classes,
    dedup_crops,
    filter_kept,
    is_other_folder,
    other_index,
    padded_rect,
    sorted_class_names,
    v3_display_by_folder,
    wheat_folders,
    yaml_id_for_category,
)

HF_DATASET = "Project-AgML/wheat_disease_detection"
HF_MIRROR = "https://hf-mirror.com"
ZENODO_DOI = "https://doi.org/10.5281/zenodo.15621359"
WIN_REPARSE = 0x400


def default_root() -> Path:
    raw = os.environ.get("PLANT_DISEASE_ROOT", r"D:\Projects\YOLOv8_PlantDisease")
    return Path(raw)


def env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw) if raw else default


def is_junction(path: Path) -> bool:
    """Windows directory junction. False on other platforms."""
    if os.name != "nt":
        return False
    try:
        attrs = os.lstat(path).st_file_attributes  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        return False
    return bool(attrs & WIN_REPARSE) and not path.is_symlink()


def remove_dir_entry(path: Path) -> None:
    """Remove a link, junction, or directory without following a junction into v3."""
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or is_junction(path):
        if is_junction(path):
            os.rmdir(path)
        else:
            path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)
        return
    path.unlink()


def link_directory(src: Path, dst: Path) -> str:
    """Point ``dst`` at ``src``. Junction on Windows, symlink elsewhere."""
    if dst.exists() or dst.is_symlink():
        remove_dir_entry(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        cmd = ["cmd", "/c", "mklink", "/J", str(dst), str(src)]
        subprocess.check_call(cmd)
        return "junction"
    os.symlink(src, dst, target_is_directory=True)
    return "symlink"


def list_class_dirs(split_dir: Path) -> list[str]:
    if not split_dir.is_dir():
        return []
    names = []
    for entry in split_dir.iterdir():
        if entry.name.startswith("."):
            continue
        if entry.is_symlink() or is_junction(entry) or entry.is_dir():
            names.append(entry.name)
    return sorted_class_names(names)


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"{path} 不是 JSON 对象")
    return data


def find_v3_class_names(dataset_v3: Path, root: Path) -> tuple[dict | None, str]:
    candidates = [
        dataset_v3 / "class_names.json",
        root / "models" / "v3" / "class_names.json",
    ]
    for path in candidates:
        data = load_json(path)
        if data is not None:
            return data, str(path)
    return None, ""


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def image_id_for(pil_image) -> str:
    hasher = hashlib.sha256()
    hasher.update(pil_image.tobytes())
    hasher.update(repr(pil_image.size).encode("ascii"))
    hasher.update(pil_image.mode.encode("ascii"))
    return hasher.hexdigest()[:20]


def crop_payload(pil_image, rect) -> bytes:
    crop = pil_image.crop(rect)
    if crop.mode not in ("RGB", "L"):
        crop = crop.convert("RGB")
    buf = io.BytesIO()
    crop.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def iter_hf_rows(dataset, hf_names, pad_ratio: float, min_side: int, stage_dir: Path):
    """Yield crop records from a datasets split. One row is one photo.

    JPEG bytes go to ``stage_dir`` immediately so a few thousand field crops
    are not held in memory at once.
    """
    stage_dir.mkdir(parents=True, exist_ok=True)
    for index, example in enumerate(dataset):
        image = example["image"]
        if image is None:
            continue
        objects = example.get("objects") or {}
        boxes = list(objects.get("bbox") or [])
        cats = list(objects.get("categories") or [])
        if len(boxes) != len(cats):
            raise SystemExit(f"第 {index} 行 bbox 与 categories 数量不一致")
        source_split = example.get("split")
        if source_split is None:
            raise SystemExit("数据集没有 split 列，无法按原图划分 train/val")
        image_id = image_id_for(image)
        normalized = boxes_look_normalized(boxes)
        width, height = image.size
        for box_index, (box, category) in enumerate(zip(boxes, cats)):
            yaml_id = yaml_id_for_category(category, hf_names)
            rect = padded_rect(box, width, height, pad_ratio, normalized)
            if rect is None:
                continue
            if min(rect[2] - rect[0], rect[3] - rect[1]) < min_side:
                continue
            payload = crop_payload(image, rect)
            folder = CATEGORIES[yaml_id]["folder"]
            filename = f"{image_id}_{box_index}.jpg"
            staged = stage_dir / filename
            staged.write_bytes(payload)
            # 哈希带上类别：同一类里的重复像素只留一份；不同病名不互相吞掉。
            # 跨 split 的泄漏由 image_id 归并到同一个 split 再挡住。
            yield {
                "image_id": image_id,
                "source_split": str(source_split),
                "yaml_id": yaml_id,
                "folder": folder,
                "digest": f"{yaml_id}:{digest_bytes(payload)}",
                "filename": filename,
                "payload_path": str(staged),
            }


def hf_class_names(dataset):
    """Read ClassLabel names. None if the feature shape is not the one we know."""
    try:
        features = getattr(dataset, "features", None)
        if not features or "objects" not in features:
            return None
        objects = features["objects"]
        inner = getattr(objects, "feature", objects)
        if "categories" not in inner:
            return None
        feature = inner["categories"]
        feature = getattr(feature, "feature", feature)
        names = getattr(feature, "names", None)
        if not names:
            return None
        from training.v4.wheat_labels import names_as_list
        return names_as_list(names)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        print(f"  读不到 HF ClassLabel 名字（{exc}），改为按整数值核对 yaml id。")
        return None


def load_hf_dataset(dataset_id: str, cache_dir: Path, endpoint: str):
    os.environ["HF_ENDPOINT"] = endpoint
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")
    cache_dir.mkdir(parents=True, exist_ok=True)
    from datasets import load_dataset

    return load_dataset(dataset_id, split="train", cache_dir=str(cache_dir))


def plan_rows(rows: list[dict], min_crops: int, keep_test: bool):
    assigned = assign_image_splits(rows, keep_test=keep_test)
    kept_rows, dup_dropped = dedup_crops(assigned)
    kept_ids, small_dropped = decide_classes(kept_rows, min_crops=min_crops)
    final_rows = filter_kept(kept_rows, kept_ids)
    absent = {
        str(cid): {
            "en": CATEGORIES[cid]["en"],
            "folder": CATEGORIES[cid]["folder"],
            "reason": "源数据里没有这个 id 的裁剪，不造空类，也不并进别的病",
        }
        for cid in CATEGORIES
        if cid not in kept_ids and cid not in small_dropped
    }
    return final_rows, {
        "input_crops": len(rows),
        "after_dedup": len(kept_rows),
        "duplicate_crops_dropped": len(dup_dropped),
        "images_with_conflicting_splits": len({r["image_id"] for r in assigned if r.get("split_conflict")}),
        "kept_class_crops": {str(cid): n for cid, n in kept_ids.items()},
        "classes_with_no_crops": absent,
        "dropped_small_classes": {
            str(cid): {
                "crops": n,
                "en": CATEGORIES[cid]["en"],
                "folder": CATEGORIES[cid]["folder"],
                "reason": f"crops {n} < min_crops {min_crops}; not merged",
            }
            for cid, n in small_dropped.items()
        },
    }


def clear_split(split_dir: Path) -> None:
    if not split_dir.exists():
        return
    for child in list(split_dir.iterdir()):
        remove_dir_entry(child)


def write_dataset(dataset_v3: Path, dataset_v4: Path, rows: list[dict], v3_json: dict | None, keep_test: bool) -> dict:
    v3_train = list_class_dirs(dataset_v3 / "train")
    if not v3_train:
        raise SystemExit(f"dataset_v3 的 train 下没有类别文件夹: {dataset_v3 / 'train'}")
    if not any(is_other_folder(name) for name in v3_train):
        raise SystemExit(
            f"{dataset_v3 / 'train'} 里没有名为 {OTHER_FOLDER} 的文件夹。"
            "v4 需要把 v3 的拒识类一起接过来。"
        )
    v3_display = v3_display_by_folder(v3_train, v3_json)
    kept_ids = sorted({int(row["yaml_id"]) for row in rows})
    wheat_names = wheat_folders(kept_ids)
    overlap = sorted(set(v3_train) & set(wheat_names))
    if overlap:
        raise SystemExit(
            "v3 里已经有和小麦类同名的文件夹，拒绝写入，避免通过目录联接改到 v3: "
            + ", ".join(overlap)
        )
    folders = sorted_class_names(list(v3_train) + wheat_names)
    mapping = build_class_names(folders, v3_display)
    measured = other_index(folders)
    splits = ["train", "val"] + (["test"] if keep_test else [])
    link_kind = "junction" if os.name == "nt" else "symlink"

    if (dataset_v4 / "class_names.json").exists() or (dataset_v4 / "train").exists():
        for split in ("train", "val", "test"):
            clear_split(dataset_v4 / split)

    for split in splits:
        (dataset_v4 / split).mkdir(parents=True, exist_ok=True)
        for folder in folders:
            dest = dataset_v4 / split / folder
            if folder in WHEAT_FOLDERS:
                dest.mkdir(parents=True, exist_ok=True)
                continue
            src = dataset_v3 / split / folder
            if src.is_dir():
                link_directory(src, dest)
            else:
                dest.mkdir(parents=True, exist_ok=True)

    written = {split: 0 for split in splits}
    for row in rows:
        split = row["split"]
        if split not in written:
            raise SystemExit(f"裁剪 split={split} 没有对应输出目录（keep_test={keep_test}）")
        dest = dataset_v4 / split / row["folder"] / row["filename"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        payload = row.get("payload")
        payload_path = row.get("payload_path")
        if payload is not None:
            dest.write_bytes(payload)
        elif payload_path:
            shutil.copy2(payload_path, dest)
        else:
            raise SystemExit(f"缺少图像字节: {row['filename']}")
        written[split] += 1

    for split in splits:
        present = list_class_dirs(dataset_v4 / split)
        if present != folders:
            raise SystemExit(
                f"{split} 的类别文件夹与 train 的字母序不一致，YOLO 下标会对不齐: {present}"
            )

    class_names_path = dataset_v4 / "class_names.json"
    with class_names_path.open("w", encoding="utf-8") as handle:
        json.dump(mapping, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    report = {
        "dataset": HF_DATASET,
        "license": "cc-by-4.0",
        "zenodo": ZENODO_DOI,
        "yaml": "xiaomai/xiaomai.yaml names block (ids 0..6)",
        "hf_endpoint": os.environ.get("HF_ENDPOINT", ""),
        "link": link_kind,
        "v3_folders": v3_train,
        "v3_other_index": other_index(v3_train),
        "v4_other_index": measured,
        "v4_other_display": OTHER_DISPLAY,
        "v3_contract_other_index": V3_OTHER_INDEX,
        "other_index_note": other_index_note(measured),
        "class_count": len(mapping),
        "class_names": mapping,
        "wheat_folders": wheat_folders(kept_ids),
        "crops_written": written,
        "keep_test": keep_test,
        "min_crops_policy": (
            "少于阈值的小麦类直接删除，不并进别的病。"
            "健康麦穗(id 5)和健康麦叶(id 6)在 yaml 里是两类，保持分开。"
            "Zenodo 压缩包里每一类都超过 400 张原图，预计 7 类都会留下。"
            "不使用 ashu010/agridrone-data：数据集卡片写明 MIT 只覆盖打包代码，原图许可各不相同。"
        ),
        "zenodo_image_counts": {str(k): v for k, v in ZENODO_IMAGE_COUNTS.items()},
    }
    report_path = dataset_v4 / "prepare_report.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return report


WHEAT_FOLDERS = {spec["folder"] for spec in CATEGORIES.values()}


def other_index_note(measured: int | None) -> str:
    if measured is None:
        return "v4 文件夹里没有 other。"
    if measured == V3_OTHER_INDEX:
        return (
            "v3 的 other 在 YOLO index 1。"
            "新增文件夹都以「小麦」开头，Unicode 码点在 ASCII 的 other 之后，"
            "所以 other / 「非植物/无关图片」在 v4 仍是 index 1。"
            "会后移的是排在这些新文件夹后面的原有中文类。"
        )
    return (
        f"按本机 dataset_v3 的真实文件夹，other 的 v4 下标是 {measured}，不是约定的 1。"
        "请以 class_names.json 里「非植物/无关图片」的键为准，不要沿用 v3 的 OTHER_CLASS_INDEX。"
    )


def print_category_table() -> None:
    print("Zenodo xiaomai.yaml 类别（不要改这些 id）")
    print(f"  来源: {ZENODO_DOI} 内 xiaomai/xiaomai.yaml")
    print(f"  HF: https://huggingface.co/datasets/{HF_DATASET}  (CC-BY-4.0)")
    print(f"  HF README 的 class_label 名字是字符串 '0'..'6'，与 yaml id 相同。")
    for cid, spec in CATEGORIES.items():
        images = ZENODO_IMAGE_COUNTS.get(cid, 0)
        print(f"  {cid}: {spec['en']}  # {spec['zh_comment']}  → 文件夹 {spec['folder']}  （zip 内约 {images} 张原图）")


def print_other_rule(dataset_v3: Path | None) -> None:
    print()
    print("other / 「非植物/无关图片」")
    print(f"  v3 约定: 文件夹 {OTHER_FOLDER} 按字母序在 YOLO index {V3_OTHER_INDEX}。")
    print("  v4 新文件夹是「小麦…」。它们的码点大于 'other'，不会插到 other 前面。")
    print(f"  因此在 v3 仍然是「恰好有一个文件夹排在 other 前面」时，v4 的 other 下标仍是 {V3_OTHER_INDEX}。")
    print("  后移的是排在新小麦文件夹之后的中文类。prepare 会按本机目录重算并写入 class_names.json。")
    if dataset_v3 and (dataset_v3 / "train").is_dir():
        folders = list_class_dirs(dataset_v3 / "train")
        wheat = [spec["folder"] for spec in CATEGORIES.values()]
        v3_idx = other_index(folders)
        v4_idx = other_index(folders + wheat)
        print(f"  本机 {dataset_v3 / 'train'}: v3 other index = {v3_idx}, 加上 7 个小麦文件夹后 = {v4_idx}")
    else:
        print("  本机还没有 dataset_v3/train，正式运行时会测量真实下标。")


def build_parser() -> argparse.ArgumentParser:
    root = default_root()
    parser = argparse.ArgumentParser(description="准备小麦 v4 分类数据集（本机运行，不在服务器上训练）")
    parser.add_argument("--root", type=Path, default=root, help="工程根目录，默认 PLANT_DISEASE_ROOT 或 D:\\Projects\\YOLOv8_PlantDisease")
    parser.add_argument("--dataset-v3", type=Path, default=None)
    parser.add_argument("--dataset-v4", type=Path, default=None)
    parser.add_argument("--cache-dir", type=Path, default=None, help="Hugging Face 缓存，默认 <root>/retrain_run/hf_cache")
    parser.add_argument("--hf-dataset", default=os.environ.get("WHEAT_HF_DATASET", HF_DATASET))
    parser.add_argument("--hf-endpoint", default=os.environ.get("HF_ENDPOINT", HF_MIRROR))
    parser.add_argument("--pad", type=float, default=float(os.environ.get("WHEAT_CROP_PAD", "0.06")), help="框四周留白，相对框宽高的比例")
    parser.add_argument("--min-side", type=int, default=16, help="裁剪后短边小于此像素则丢弃")
    parser.add_argument("--min-crops", type=int, default=int(os.environ.get("WHEAT_MIN_CROPS", str(DEFAULT_MIN_CROPS))))
    parser.add_argument("--keep-test", action="store_true", help="保留原 test 划分；默认把 test 整图并入 val")
    parser.add_argument("--dry-run", action="store_true", help="只打印类别映射和 other 下标规则，不下载、不写数据集")
    parser.add_argument("--force", action="store_true", help="dataset_v4 已存在时清空 train/val/test 下的链接和小麦文件夹后重建")
    return parser


def resolve_paths(args):
    root = args.root
    dataset_v3 = args.dataset_v3 or env_path("DATASET_V3", root / "dataset_v3")
    dataset_v4 = args.dataset_v4 or env_path("DATASET_V4", root / "dataset_v4")
    cache_dir = args.cache_dir or env_path("HF_DATASETS_CACHE", root / "retrain_run" / "hf_cache")
    return dataset_v3, dataset_v4, cache_dir


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    dataset_v3, dataset_v4, cache_dir = resolve_paths(args)
    print_category_table()
    print_other_rule(dataset_v3 if not args.dry_run or dataset_v3.exists() else None)
    if args.dry_run:
        print()
        print("dry-run：未下载数据，未写入 dataset_v4。")
        print(f"  正式命令会使用 HF_ENDPOINT={args.hf_endpoint}")
        print(f"  dataset_v3 = {dataset_v3}")
        print(f"  dataset_v4 = {dataset_v4}")
        print(f"  裁剪留白 pad={args.pad}，少于此作物数则丢弃该类: {args.min_crops}")
        print("  同一张原图的所有裁剪只进入一个 split；重复哈希只保留 train 里的那份。")
        return

    if not (dataset_v3 / "train").is_dir() or not (dataset_v3 / "val").is_dir():
        raise SystemExit(f"需要已有的 dataset_v3（含 train/ 与 val/）: {dataset_v3}")
    already = (dataset_v4 / "class_names.json").exists() or (dataset_v4 / "train").exists()
    if already and not args.force:
        raise SystemExit(f"{dataset_v4} 已经准备过。确认要重做请加 --force（不会删除 dataset_v3）。")
    dataset_v3 = dataset_v3.resolve()
    dataset_v4 = dataset_v4.resolve()

    print()
    print(f"下载 {args.hf_dataset}")
    print(f"  HF_ENDPOINT={args.hf_endpoint}")
    print(f"  cache={cache_dir}")
    dataset = load_hf_dataset(args.hf_dataset, cache_dir, args.hf_endpoint)
    hf_names = hf_class_names(dataset)
    if hf_names is not None:
        print(f"  HF ClassLabel 名字: {hf_names}")
    else:
        print("  HF 特征里没有 ClassLabel 名字，按类别整数值当作 yaml id，对不上就停止。")

    stage = cache_dir.parent / "wheat_stage"
    if stage.exists():
        shutil.rmtree(stage)
    try:
        rows = list(iter_hf_rows(dataset, hf_names, args.pad, args.min_side, stage))
        final_rows, stats = plan_rows(rows, args.min_crops, args.keep_test)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        if not final_rows:
            raise SystemExit("没有可写入的小麦裁剪。检查阈值和标注。")

        v3_json, v3_json_path = find_v3_class_names(dataset_v3, args.root)
        if v3_json_path:
            print(f"v3 类别映射: {v3_json_path}")
        dataset_v4.mkdir(parents=True, exist_ok=True)
        report = write_dataset(dataset_v3, dataset_v4, final_rows, v3_json, args.keep_test)
        report.update(stats)
        with (dataset_v4 / "prepare_report.json").open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

        measured = report["v4_other_index"]
        print()
        print(f"OTHER_CLASS_INDEX={measured}")
        print(report["other_index_note"])
        print(f"class_names.json → {dataset_v4 / 'class_names.json'}  （{report['class_count']} 类）")
        print(f"其中 other 文件夹展示名为「{OTHER_DISPLAY}」。")
        for cid, spec in CATEGORIES.items():
            key = str(cid)
            if key in report.get("dropped_small_classes", {}):
                print(f"  丢弃 {spec['folder']}: {report['dropped_small_classes'][key]['reason']}")
        if measured != V3_OTHER_INDEX:
            print("WARNING: other 下标与 v3 约定的 1 不同。训练前请阅读上面的说明。")
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
