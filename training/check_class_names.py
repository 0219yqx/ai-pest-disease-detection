# -*- coding: utf-8 -*-
"""
检查 class_names.json。

默认只报告问题，退出码 0（现役模型的文件有空缺和重复健康类，这是已知状态）。
下面两种情况退出码为 1：
- 给了 --data，但 JSON 和 train 文件夹顺序不一致
- 给了 --strict，并且存在空缺、重复类名或重复健康类

用法
----
python training/check_class_names.py --class-names models/class_names.json
python training/check_class_names.py --class-names D:/data/cleaned/class_names.json \\
    --data D:/data/cleaned --strict
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ai.class_names import (  # noqa: E402
    describe_issues,
    format_issue_report,
    load_class_names,
    mapping_mismatch,
)


def evaluate(class_names_path, data_dir=None):
    mapping = load_class_names(class_names_path)
    issues = describe_issues(mapping)
    mismatch = []
    if data_dir:
        train_dir = Path(data_dir) / "train"
        if not train_dir.is_dir():
            mismatch.append(f"找不到训练集目录: {train_dir}")
        else:
            mismatch.extend(mapping_mismatch(mapping, train_dir))
    return mapping, issues, mismatch


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="检查 class_names.json 是否能安全用于模型")
    parser.add_argument("--class-names", required=True)
    parser.add_argument("--data", default="", help="清洗后的数据集根目录，用来核对 train 文件夹")
    parser.add_argument("--strict", action="store_true", help="有空缺或重复健康类时也失败")
    args = parser.parse_args(argv)

    path = Path(args.class_names)
    if not path.is_file():
        raise SystemExit(f"找不到类别文件: {path}")
    try:
        mapping, issues, mismatch = evaluate(path, args.data or None)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"无法读取类别文件: {exc}") from exc

    print(format_issue_report(mapping))
    for item in mismatch:
        print(f"[FAIL] {item}")
    if mismatch or (args.strict and issues):
        raise SystemExit(1)
    if issues and not args.strict:
        print("未加 --strict：现役模型仍可按 class_N 里的编号查这个文件。重训并部署后再用 --strict。")


if __name__ == "__main__":
    main()
