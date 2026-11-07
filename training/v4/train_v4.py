# -*- coding: utf-8 -*-
"""Fine-tune YOLOv8-cls from models/v3/best.pt and copy the result to models/v4.

Runs on the Windows machine that holds the datasets. This script does not
start a server and does not commit weights.

Defaults match D:\\Projects\\YOLOv8_PlantDisease (override with flags or env):

    python training/v4/train_v4.py

The v3 checkpoint has 67 classes. v4 has more, and alphabetical order moves
the old Chinese classes, so the old classification layer is the wrong shape
and the wrong index alignment. Ultralytics rebuilds that layer and keeps the
backbone. Do not copy the 67-way head onto the first 67 outputs of the new head.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.v4.wheat_labels import OTHER_DISPLAY, V3_OTHER_INDEX  # noqa: E402


class _Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()

    def isatty(self):
        return False


def default_root() -> Path:
    return Path(os.environ.get("PLANT_DISEASE_ROOT", r"D:\Projects\YOLOv8_PlantDisease"))


def env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw) if raw else default


def other_display_index(mapping: dict) -> int | None:
    hits = []
    for key, value in mapping.items():
        if value == OTHER_DISPLAY:
            hits.append(int(key))
    if not hits:
        return None
    if len(hits) > 1:
        raise SystemExit(f"class_names.json 里有多个「{OTHER_DISPLAY}」: {hits}")
    return hits[0]


def count_class_dirs(data_dir: Path) -> int:
    train = data_dir / "train"
    names = [
        p.name for p in train.iterdir()
        if not p.name.startswith(".") and (p.is_dir() or p.is_symlink())
    ]
    return len(names)


def build_parser() -> argparse.ArgumentParser:
    root = default_root()
    parser = argparse.ArgumentParser(description="从 v3 best.pt 微调 YOLOv8-cls，写出 models/v4")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--data", type=Path, default=None, help="dataset_v4 目录（含 train/ 与 val/）")
    parser.add_argument("--model", type=Path, default=None, help="v3 权重，默认 models/v3/best.pt")
    parser.add_argument("--deploy-to", type=Path, default=None, help="复制目标，默认 models/v4")
    parser.add_argument("--project", type=Path, default=None, help="Ultralytics project 目录，默认 <root>/output")
    parser.add_argument("--name", default=os.environ.get("V4_RUN_NAME", "plant_disease_v4"))
    parser.add_argument("--log", type=Path, default=None, help="日志文件，默认 retrain_run/train_v4.log")
    parser.add_argument("--imgsz", type=int, default=int(os.environ.get("V4_IMGSZ", "384")))
    parser.add_argument("--epochs", type=int, default=int(os.environ.get("V4_EPOCHS", "30")))
    parser.add_argument("--batch", type=int, default=int(os.environ.get("V4_BATCH", "32")))
    parser.add_argument("--workers", type=int, default=int(os.environ.get("V4_WORKERS", "4")))
    parser.add_argument("--patience", type=int, default=int(os.environ.get("V4_PATIENCE", "10")))
    parser.add_argument("--device", default=os.environ.get("V4_DEVICE", "0"))
    parser.add_argument("--amp", action=argparse.BooleanOptionalAction, default=True)
    return parser


def resolve(args):
    root = args.root
    data = args.data or env_path("DATASET_V4", root / "dataset_v4")
    model = args.model or env_path("V3_WEIGHTS", root / "models" / "v3" / "best.pt")
    deploy = args.deploy_to or env_path("V4_MODEL_DIR", root / "models" / "v4")
    project = args.project or env_path("V4_PROJECT", root / "output")
    log_path = args.log or env_path("V4_LOG", root / "retrain_run" / "train_v4.log")
    return data, model, deploy, project, log_path


def open_log(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a", encoding="utf-8")
    handle.write("\n===== train_v4 =====\n")
    handle.flush()
    # 替换发生在 import ultralytics 之前，这样它的日志流进同一个文件。
    sys.stdout = _Tee(sys.__stdout__, handle)
    sys.stderr = _Tee(sys.__stderr__, handle)
    return handle


def train_and_copy(args, data, model, deploy, project) -> None:
    names_path = data / "class_names.json"
    if not (data / "train").is_dir() or not (data / "val").is_dir():
        raise SystemExit(f"数据集需要 train/ 和 val/: {data}")
    if not names_path.is_file():
        raise SystemExit(f"缺少 {names_path}，先运行 prepare_dataset_v4.py")
    if not model.is_file():
        raise SystemExit(f"找不到 v3 权重: {model}")

    mapping = json.loads(names_path.read_text(encoding="utf-8"))
    measured = other_display_index(mapping)
    n_dirs = count_class_dirs(data)
    print(f"data={data}")
    print(f"weights={model}")
    print(f"classes json={len(mapping)}  train folders={n_dirs}")
    print(f"OTHER_CLASS_INDEX={measured}  （v3 约定是 {V3_OTHER_INDEX}，展示名「{OTHER_DISPLAY}」）")
    if measured != V3_OTHER_INDEX:
        print(
            "WARNING: other 的下标不是 1。新文件夹若被改成英文名，或 v3 里排在 other 前面的"
            "文件夹不止一个，下标就会变。以这次 class_names.json 为准。"
        )
    if len(mapping) != n_dirs:
        raise SystemExit("class_names.json 的条数和 train 文件夹数不一致，拒绝开训。")

    from ultralytics import YOLO

    yolo = YOLO(str(model))
    yolo.train(
        data=str(data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        workers=args.workers,
        device=args.device,
        project=str(project),
        name=args.name,
        exist_ok=True,
        patience=args.patience,
        amp=args.amp,
        pretrained=True,
        optimizer="auto",
        # 与 training/train_yolov8.py 相同的叶面增强
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
    )

    best = project / args.name / "weights" / "best.pt"
    if not best.is_file():
        raise SystemExit(f"训练结束但没有找到 {best}")
    deploy.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, deploy / "best.pt")
    shutil.copy2(names_path, deploy / "class_names.json")
    print(f"best.pt → {deploy / 'best.pt'}")
    print(f"class_names.json → {deploy / 'class_names.json'}")
    print("COPIED")


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    data, model, deploy, project, log_path = resolve(args)
    saved_out, saved_err = sys.stdout, sys.stderr
    handle = open_log(log_path)
    try:
        print(f"log={log_path}")
        train_and_copy(args, data, model, deploy, project)
    finally:
        sys.stdout = saved_out
        sys.stderr = saved_err
        handle.close()


if __name__ == "__main__":
    main()
