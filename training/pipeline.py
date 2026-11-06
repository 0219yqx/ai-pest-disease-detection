# -*- coding: utf-8 -*-
"""
一条龙：需要时清洗 → 训练 → 把 best.pt 和 class_names.json 复制到部署目录。

不会下载数据集，也不会在清洗结果不合格时覆盖 models/。

用法
----
python training/pipeline.py ^
    --raw-train D:/data/train --raw-val D:/data/val ^
    --data D:/data/cleaned --name-map models/class_names.json ^
    --deploy-to models --device 0

已经洗好、且 class_names.json 与文件夹一致时，会跳过清洗。
强制重洗: --force-clean
只部署已有权重: --deploy-only --weights output/plant_disease_v2/weights/best.pt --data D:/data/cleaned --deploy-to models
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.dataset_layout import PipelineError, deploy_files, needs_clean  # noqa: E402
from training.fix_dataset_labels import main as fix_main  # noqa: E402


def ensure_cleaned(args) -> None:
    data_dir = Path(args.data)
    if args.force_clean:
        reason = "指定了 --force-clean"
        clean = True
    else:
        clean, reason = needs_clean(data_dir)
    if not clean:
        print(f"[OK] 使用已有清洗结果: {data_dir}（{reason}）")
        return

    raw_train = Path(args.raw_train) if args.raw_train else None
    raw_val = Path(args.raw_val) if args.raw_val else None
    name_map = Path(args.name_map) if args.name_map else None
    missing = []
    if raw_train is None or not raw_train.is_dir():
        missing.append(f"RAW_TRAIN / --raw-train 不存在: {args.raw_train or '（空）'}")
    if raw_val is None or not raw_val.is_dir():
        missing.append(f"RAW_VAL / --raw-val 不存在: {args.raw_val or '（空）'}")
    if name_map is None or not name_map.is_file():
        missing.append(f"NAME_MAP / --name-map 不存在: {args.name_map or '（空）'}")
    if missing:
        detail = "\n".join(missing)
        raise PipelineError(
            "需要先清洗标签，但原始路径不齐。\n"
            f"原因: {reason}\n{detail}\n"
            "请把原始数据集的 train、val 指到本机目录，或先单独跑 fix_dataset_labels.py。"
        )
    print(f"[1/3] 清洗标签 → {data_dir}")
    print(f"      原因: {reason}")
    fix_argv = [
        "--train", str(raw_train),
        "--val", str(raw_val),
        "--out", str(data_dir),
        "--name-map", str(name_map),
        "--min-per-class", str(args.min_per_class),
        "--apply",
        "--force",
    ]
    fix_main(fix_argv)


def run_training(args):
    from training.train_yolov8 import main as train_main

    print("[2/3] 训练")
    train_main([
        "--data", args.data,
        "--model", args.model,
        "--imgsz", str(args.imgsz),
        "--epochs", str(args.epochs),
        "--patience", str(args.patience),
        "--batch", str(args.batch),
        "--device", args.device,
        "--name", args.name,
        "--project", args.project,
    ])


def deploy(args, weights: Path) -> None:
    data_dir = Path(args.data)
    print(f"[3/3] 部署到 {args.deploy_to}")
    deploy_files(
        weights,
        data_dir / "class_names.json",
        args.deploy_to,
        train_dir=data_dir / "train",
    )
    print(f"[OK] 已更新 {Path(args.deploy_to) / 'best.pt'}")
    print(f"[OK] 已更新 {Path(args.deploy_to) / 'class_names.json'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="清洗、训练并部署病虫害分类模型")
    parser.add_argument("--raw-train", default="", help="原始 train 目录。已有合格清洗结果时可以不存在")
    parser.add_argument("--raw-val", default="")
    parser.add_argument("--data", required=True, help="清洗输出目录，也是训练用的 --data")
    parser.add_argument("--name-map", default=str(ROOT / "models" / "class_names.json"))
    parser.add_argument("--min-per-class", type=int, default=5)
    parser.add_argument("--model", default="yolov8s-cls.pt")
    parser.add_argument("--imgsz", type=int, default=384)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--patience", type=int, default=30)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--device", default="0")
    parser.add_argument("--name", default="plant_disease_v2")
    parser.add_argument("--project", default="output")
    parser.add_argument("--deploy-to", default=str(ROOT / "models"))
    parser.add_argument("--force-clean", action="store_true")
    parser.add_argument("--deploy-only", action="store_true", help="不训练，只复制已有权重和类别文件")
    parser.add_argument("--weights", default="", help="--deploy-only 时的 best.pt；默认 output/<name>/weights/best.pt")
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if args.deploy_only:
            weights = Path(args.weights) if args.weights else Path(args.project) / args.name / "weights" / "best.pt"
            deploy(args, weights)
            return
        ensure_cleaned(args)
        run_training(args)
        weights = Path(args.project) / args.name / "weights" / "best.pt"
        deploy(args, weights)
    except PipelineError as exc:
        raise SystemExit(f"[FAIL] {exc}") from exc


if __name__ == "__main__":
    main()
