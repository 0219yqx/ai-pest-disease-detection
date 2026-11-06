# -*- coding: utf-8 -*-
"""清洗数据集目录与部署文件的小工具（不导入 ultralytics）。"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ai.class_names import (  # noqa: E402
    describe_issues,
    load_class_names,
    mapping_from_train,
    mapping_mismatch,
    write_class_names,
)


class PipelineError(RuntimeError):
    """清洗、训练或部署无法继续。"""


def needs_clean(data_dir) -> tuple[bool, str]:
    """清洗结果是否还不能直接拿去训练。"""
    root = Path(data_dir)
    if not (root / "train").is_dir() or not (root / "val").is_dir():
        return True, "缺少 train/ 或 val/"
    names_path = root / "class_names.json"
    if not names_path.is_file():
        return True, "缺少 class_names.json"
    try:
        mapping = load_class_names(names_path)
    except (OSError, ValueError) as exc:
        return True, f"class_names.json 无法使用: {exc}"
    problems = describe_issues(mapping) + mapping_mismatch(mapping, root / "train")
    if problems:
        return True, "；".join(problems)
    return False, f"已对齐：{len(mapping)} 类"


def ensure_class_names_file(data_dir) -> Path:
    """训练前保证 class_names.json 与 train 文件夹顺序一致。

    没有这个文件时按文件夹写一份。已有但不一致则失败，避免悄悄换成另一套编号。
    """
    root = Path(data_dir)
    path = root / "class_names.json"
    expected = mapping_from_train(root / "train")
    if not expected:
        raise PipelineError(f"{root / 'train'} 下没有类别文件夹")
    if path.is_file():
        current = load_class_names(path)
        mismatch = mapping_mismatch(current, root / "train")
        if mismatch:
            detail = "\n".join(mismatch)
            raise PipelineError(
                "数据集里的 class_names.json 与 train 文件夹不一致。\n"
                f"{detail}\n"
                "请重新运行 fix_dataset_labels.py --apply，或删掉这份 json 后重训。"
            )
        return path
    write_class_names(path, expected)
    return path


def deploy_files(best_pt, class_names_path, deploy_to, train_dir=None) -> None:
    """把 best.pt 和 class_names.json 复制到部署目录（通常是仓库 models/）。"""
    best = Path(best_pt)
    names = Path(class_names_path)
    dest = Path(deploy_to)
    if not best.is_file():
        raise PipelineError(f"找不到训练权重: {best}")
    if not names.is_file():
        raise PipelineError(f"找不到 class_names.json: {names}")
    mapping = load_class_names(names)
    problems = describe_issues(mapping)
    if train_dir is not None:
        problems.extend(mapping_mismatch(mapping, train_dir))
    if problems:
        detail = "\n".join(f"- {item}" for item in problems)
        raise PipelineError("拒绝部署不一致的类别映射:\n" + detail)
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, dest / "best.pt")
    shutil.copy2(names, dest / "class_names.json")


def deploy_instructions(best_pt, data_dir, run_name="plant_disease_v2") -> str:
    best = Path(best_pt)
    data = Path(data_dir)
    names = data / "class_names.json"
    return "\n".join([
        "训练结束。权重和类别名要一起换，只换 best.pt 会把病名对错位。",
        f"  权重: {best}",
        f"  类别: {names}",
        "部署（确认验证结果可以接受之后再覆盖仓库里的模型）:",
        f"  copy /Y \"{best}\" models\\best.pt",
        f"  copy /Y \"{names}\" models\\class_names.json",
        "或: python training/pipeline.py --deploy-only "
        f"--weights \"{best}\" --data \"{data}\" --deploy-to models",
        "验证（打印的是与当前验证集文件夹的一致率，不是实地病名准确率）:",
        "  python training/validate_cls.py "
        f"--weights \"{best}\" --data \"{data}\"",
        f"本次训练目录名: {run_name}",
    ])
