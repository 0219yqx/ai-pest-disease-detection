# -*- coding: utf-8 -*-
"""
validate_cls.py — 在清洗后的验证集上打印 top1 / top5 和混淆摘要。

这里的分数是「预测文件夹」和「验证集文件夹」一致的比例。
验证集如果还是合并数据时的错误标签，分数高只说明模型记住了错误标签。

用法
----
python training/validate_cls.py --weights output/plant_disease_v2/weights/best.pt \\
    --data D:/data/cleaned --imgsz 384
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ai.class_names import mapping_from_train  # noqa: E402

CAVEAT = """\
指标含义
- top1 / top5 是模型和当前验证集文件夹标签的一致率。
- 污染标签上的高分（例如旧模型在错误验证集上的 Top-1 ≈ 86.6%）不能当成实地病名准确率。
- 清洗后，文件名对得上的类比较可信；md5 和自采、未复核的类仍可能标错。
- 清洗前后的 top1 不能直接比较：类别个数和标签含义都变了。
"""


def _as_rows(matrix):
    if matrix is None:
        return None
    if hasattr(matrix, "tolist"):
        matrix = matrix.tolist()
    rows = []
    for row in matrix:
        if hasattr(row, "tolist"):
            row = row.tolist()
        rows.append([float(value) for value in row])
    return rows


def summarize_confusion(matrix, names) -> str:
    """按「行 = 真实类，列 = 预测类」摘要。对不上尺寸就说明原因，不编造数字。"""
    rows = _as_rows(matrix)
    if not rows:
        return "没有拿到混淆矩阵，跳过逐类摘要。"
    lengths = {len(row) for row in rows}
    if len(lengths) != 1:
        return "混淆矩阵各行长度不一致，跳过逐类摘要。"
    side = len(rows)
    width = lengths.pop()
    if side != width or side not in {len(names), len(names) + 1}:
        return f"混淆矩阵尺寸 {side}x{width} 与 {len(names)} 个类别对不上，跳过逐类摘要。"
    if side == len(names) + 1:
        rows = [row[: len(names)] for row in rows[: len(names)]]

    lines = ["逐类（召回 = 对角 / 该行合计；只列出支持数 > 0 的类）"]
    weak = []
    for index, name in enumerate(names):
        support = sum(rows[index])
        correct = rows[index][index]
        if support <= 0:
            lines.append(f"- {name}: 验证集 0 张")
            continue
        recall = correct / support
        lines.append(f"- {name}: 召回 {recall:.3f}（{int(correct)}/{int(support)}）")
        if recall < 0.5:
            weak.append(name)

    confusions = []
    for truth, name in enumerate(names):
        for pred in range(len(names)):
            if truth == pred:
                continue
            count = rows[truth][pred]
            if count > 0:
                confusions.append((count, name, names[pred]))
    confusions.sort(key=lambda item: (-item[0], item[1], item[2]))
    lines.append("")
    lines.append("最常见的错分（真实 → 预测）")
    if not confusions:
        lines.append("- 无")
    else:
        for count, truth, pred in confusions[:12]:
            lines.append(f"- {truth} → {pred}: {int(count)}")
    if weak:
        lines.append("")
        lines.append("召回低于 0.5 的类: " + ", ".join(weak))
    return "\n".join(lines)


def read_topk(metrics):
    """从 ultralytics 的验证结果里取 top1/top5。读不到就返回 None，不填假数字。"""
    results = getattr(metrics, "results_dict", None) or {}

    def pick(attr, keys):
        value = getattr(metrics, attr, None)
        if value is not None:
            return float(value)
        for key in keys:
            if key in results and results[key] is not None:
                return float(results[key])
        return None

    top1 = pick("top1", ("metrics/accuracy_top1", "accuracy_top1"))
    top5 = pick("top5", ("metrics/accuracy_top5", "accuracy_top5"))
    return top1, top5


def confusion_matrix_of(metrics):
    matrix = getattr(metrics, "confusion_matrix", None)
    if matrix is None:
        return None
    return getattr(matrix, "matrix", matrix)


def format_report(top1, top5, matrix, names) -> str:
    def fmt(value):
        return "未能从 ultralytics 结果中读取" if value is None else f"{value:.4f}"

    parts = [
        "验证集一致率（对当前文件夹标签，不是实地病名准确率）",
        f"top1: {fmt(top1)}",
        f"top5: {fmt(top5)}",
        "",
        summarize_confusion(matrix, names),
        "",
        CAVEAT.strip(),
    ]
    return "\n".join(parts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="打印分类验证 top1/top5 和混淆摘要")
    parser.add_argument("--weights", required=True, help="best.pt")
    parser.add_argument("--data", required=True, help="含 train/ 与 val/ 的数据集目录")
    parser.add_argument("--imgsz", type=int, default=384)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--device", default="0")
    parser.add_argument("--split", default="val")
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    weights = Path(args.weights)
    data_dir = Path(args.data)
    if not weights.is_file():
        raise SystemExit(f"找不到权重: {weights}")
    if not (data_dir / "train").is_dir() or not (data_dir / "val").is_dir():
        raise SystemExit(f"数据集目录需要 train/ 和 val/: {data_dir}")
    names = list(mapping_from_train(data_dir / "train").values())
    if not names:
        raise SystemExit(f"{data_dir / 'train'} 下没有类别文件夹")

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit(
            "没有安装 ultralytics，无法验证。pip install ultralytics\n" + str(exc)
        ) from exc

    model = YOLO(str(weights))
    metrics = model.val(
        data=str(data_dir),
        split=args.split,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        plots=False,
        verbose=False,
    )
    top1, top5 = read_topk(metrics)
    print(format_report(top1, top5, confusion_matrix_of(metrics), names))


if __name__ == "__main__":
    main()
