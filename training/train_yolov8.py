# -*- coding: utf-8 -*-
"""
train_yolov8.py — 病虫害分类重训练（YOLOv8-cls）

默认：yolov8s-cls、imgsz 384、100 轮、patience 30。
--data 必须是数据集目录（里面有 train/ 和 val/），不是 yaml。
类别名就是文件夹名，编号按文件夹名排序，要和 class_names.json 一致。

用法
----
python training/train_yolov8.py --data D:/data/cleaned --device 0
python training/train_yolov8.py --data D:/data/cleaned --device cpu --batch 16 --epochs 50

训练前请先跑 fix_dataset_labels.py。脚本不会下载数据集。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.dataset_layout import (  # noqa: E402
    PipelineError,
    deploy_instructions,
    ensure_class_names_file,
)


def check_dataset_dir(data_dir: Path) -> None:
    if not data_dir.is_dir():
        raise SystemExit(
            f"数据集目录不存在: {data_dir}\n"
            "分类任务的 --data 是目录（含 train/ 与 val/），不是 dataset.yaml。"
        )
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    if not train_dir.is_dir() or not val_dir.is_dir():
        raise SystemExit(f"数据集目录需要 train/ 和 val/ 两个子目录: {data_dir}")
    train_classes = [path for path in train_dir.iterdir() if path.is_dir()]
    val_classes = [path for path in val_dir.iterdir() if path.is_dir()]
    if not train_classes:
        raise SystemExit(f"{train_dir} 下没有类别文件夹")
    if not val_classes:
        raise SystemExit(f"{val_dir} 下没有类别文件夹")
    empty = [path.name for path in train_classes if not any(path.iterdir())]
    if empty:
        preview = ", ".join(empty[:8])
        raise SystemExit(f"这些训练类别是空的，请先清洗或删除: {preview}")


def train(args):
    data_dir = Path(args.data)
    check_dataset_dir(data_dir)
    try:
        names_path = ensure_class_names_file(data_dir)
    except PipelineError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"类别文件: {names_path}")

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit(
            "没有安装 ultralytics。请在带 torch 的环境里执行: pip install ultralytics\n"
            f"原始错误: {exc}"
        ) from exc

    model = YOLO(args.model)
    model.train(
        data=str(data_dir),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        exist_ok=True,
        patience=args.patience,
        optimizer="auto",
        degrees=15.0,
        shear=5.0,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        flipud=0.1,
        mosaic=1.0,
        mixup=0.1,
        cutmix=0.1,
        erasing=0.4,
        auto_augment="randaugment",
        seed=0,
        deterministic=True,
        amp=True,
    )
    best = Path(args.project) / args.name / "weights" / "best.pt"
    if not best.is_file():
        raise SystemExit(f"训练结束但没有找到权重: {best}")
    print()
    print(deploy_instructions(best, data_dir, args.name))
    return best


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="YOLOv8 病虫害分类训练")
    parser.add_argument("--data", required=True, help="清洗后的数据集目录（含 train/ 与 val/）")
    parser.add_argument("--model", default="yolov8s-cls.pt", help="预训练权重，默认 yolov8s-cls.pt")
    parser.add_argument("--imgsz", type=int, default=384, help="输入边长，默认 384")
    parser.add_argument("--epochs", type=int, default=100, help="最大轮数，默认 100")
    parser.add_argument("--patience", type=int, default=30, help="早停耐心，默认 30")
    parser.add_argument("--batch", type=int, default=32, help="批大小。显存不够就改成 16 或 8")
    parser.add_argument("--device", default="0", help="GPU 编号；没有 GPU 用 cpu")
    parser.add_argument("--name", default="plant_disease_v2", help="本次训练的子目录名")
    parser.add_argument("--project", default="output", help="训练输出根目录")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.epochs < 1:
        raise SystemExit("--epochs 至少为 1")
    if args.imgsz < 32:
        raise SystemExit("--imgsz 太小")
    return train(args)


if __name__ == "__main__":
    main()
