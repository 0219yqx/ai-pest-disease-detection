# -*- coding: utf-8 -*-
"""
train_yolov8.py — 病虫害分类模型重训练脚本（YOLOv8-cls）

相比旧脚本的改进：
- 完整 100 轮 + 更充分的增强（旋转/剪切/mixup/cutmix）
- 默认 yolov8s-cls（比 nano 高 2~4 个点），可 --model 指定
- 默认 imgsz 384（原 224 偏低）
- 类别数自动从 dataset.yaml 读取

用法
----
python train_yolov8.py --data D:/data/cleaned \
    --model yolov8s-cls.pt --imgsz 384 --epochs 100 --batch 32 --device 0

说明
----
- YOLOv8 分类训练要求 --data 指向数据集【目录】（内含 train/ 与 val/ 子目录，
  子目录下的文件夹名即类别名），不是 yaml 文件。
- 训练前请先用 fix_dataset_labels.py 清洗标签（见 README"已知问题"）。
- 训练完成后把 output/<name>/weights/best.pt 复制到仓库 models/best.pt，
  并核对 models/class_names.json 与数据集类别一一对应。
"""

import argparse
from pathlib import Path
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser(description='YOLOv8 病虫害分类训练')
    ap.add_argument('--data', required=True, help='数据集【目录】（内含 train/ 与 val/；cls 任务不需要 yaml）')
    ap.add_argument('--model', default='yolov8s-cls.pt', help='预训练权重（n/s/m/l）')
    ap.add_argument('--imgsz', type=int, default=384, help='训练分辨率')
    ap.add_argument('--epochs', type=int, default=100)
    ap.add_argument('--batch', type=int, default=32)
    ap.add_argument('--device', default='0', help="GPU 编号；CPU 用 'cpu'")
    ap.add_argument('--name', default='plant_disease_v2', help='输出目录名')
    ap.add_argument('--project', default='output', help='输出根目录')
    ap.add_argument('--patience', type=int, default=30, help='早停耐心值')
    args = ap.parse_args()

    data_dir = Path(args.data)
    if not data_dir.is_dir():
        raise SystemExit(f"数据集目录不存在: {args.data}（分类任务需传目录而非 yaml）")
    if not (data_dir / 'train').is_dir() or not (data_dir / 'val').is_dir():
        raise SystemExit(f"数据集目录需包含 train/ 与 val/ 子目录: {args.data}")

    model = YOLO(args.model)

    # 关键训练参数（针对作物叶面病害场景调优）
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        exist_ok=True,
        patience=args.patience,
        optimizer='auto',
        # 增强：旋转/剪切（叶面角度多变），mixup/cutmix 提高泛化
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
        auto_augment='randaugment',
        # 其他
        seed=0,
        deterministic=True,
        amp=True,
    )

    best = Path(args.project) / args.name / 'weights' / 'best.pt'
    print(f"\n训练完成，最优模型: {best}")
    print("请复制到仓库 models/best.pt，并核对 models/class_names.json 与 dataset.yaml 一致。")


if __name__ == '__main__':
    main()
