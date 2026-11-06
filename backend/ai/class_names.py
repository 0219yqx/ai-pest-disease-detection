# -*- coding: utf-8 -*-
"""类别名的单一解析规则。

仓库里的 models/class_names.json 同时服务两代模型，键的含义不一样：

- 现役 best.pt（遗留）：权重里的类别名是文件夹名 class_N，N 可以跳号
  （0–60、75–77）。JSON 的键就是这个 N，不是模型内部下标。
  Ultralytics 按文件夹名字母序编号，所以 class_10 的模型下标是 2，
  不能用下标去查 JSON。
- 清洗后重训：train/ 下每个文件夹是一个类别，JSON 键是 0..N-1，
  与 sorted(文件夹名) 的下标一致，也就是新模型的下标。

resolve_label 按「映射是否从 0 连续」区分这两种文件。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_CLASS_N = re.compile(r"^class_(\d+)$")
# 「玉米健康」「玉米健康_2」算同一健康类；「番茄健康_早期」不含纯数字后缀，不合并。
_HEALTHY = re.compile(r"^(.+健康)(?:_(\d+))?$")


def load_class_names(path) -> dict[int, str]:
    """读取 {id: 中文名}。键必须能转成 int，值必须是非空字符串。"""
    file_path = Path(path)
    with open(file_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{file_path} 必须是 {{\"0\": \"类别名\"}} 这种对象")
    mapping: dict[int, str] = {}
    for key, value in data.items():
        try:
            index = int(str(key))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{file_path} 的键无法转成整数: {key!r}") from exc
        if isinstance(value, str):
            name = value.strip()
        elif value is None:
            name = ""
        else:
            name = str(value).strip()
        if not name:
            raise ValueError(f"{file_path} 的类别 {index} 没有名称")
        if index in mapping:
            raise ValueError(f"{file_path} 的类别编号 {index} 重复")
        mapping[index] = name
    return mapping


def is_dense(mapping: dict[int, str]) -> bool:
    """键是否正好是 0 .. len-1。空映射不算连续。"""
    if not mapping:
        return False
    keys = sorted(mapping)
    return keys == list(range(len(keys)))


def normalize_healthy(label: str) -> str:
    """把「玉米健康_2」收成「玉米健康」。不是健康类则原样返回。"""
    text = (label or "").strip()
    match = _HEALTHY.fullmatch(text)
    if not match:
        return text
    return match.group(1)


def _coerce_index(index):
    """接受 Python int，也接受 numpy 整数（带 .item()）。不接受 bool 和字符串。"""
    if isinstance(index, bool) or index is None or isinstance(index, str):
        return None
    if type(index) is int:
        return index
    item = getattr(index, "item", None)
    if callable(item):
        try:
            index = item()
        except Exception:
            return None
        if isinstance(index, bool) or isinstance(index, str):
            return None
        if type(index) is int:
            return index
    try:
        value = int(index)
    except (TypeError, ValueError):
        return None
    return value


def resolve_label(index, raw_name, mapping: dict[int, str]) -> str:
    """模型下标 + 权重里的原始类名 → 展示名。

    连续映射（清洗后重训）优先用下标，这样 class_10 不会误撞到第 10 号类。
    有空缺的遗留映射只用 class_N 里的 N，不用模型下标。
    """
    raw = "" if raw_name is None else str(raw_name).strip()
    match = _CLASS_N.fullmatch(raw)
    folder_id = int(match.group(1)) if match else None
    index = _coerce_index(index)
    index_ok = index is not None and index >= 0 and index in mapping

    if is_dense(mapping) and index_ok:
        return mapping[index]
    if folder_id is not None and not is_dense(mapping) and folder_id in mapping:
        return mapping[folder_id]
    if raw and folder_id is None:
        return raw
    if raw:
        return raw
    if index is not None:
        return f"class_{index}"
    return ""


def _compress_ranges(values: list[int]) -> str:
    if not values:
        return ""
    ranges = []
    start = prev = values[0]
    for value in values[1:]:
        if value == prev + 1:
            prev = value
            continue
        ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
        start = prev = value
    ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
    return ", ".join(ranges)


def describe_issues(mapping: dict[int, str]) -> list[str]:
    """列出空缺编号、重复类名、重复健康类。没有问题则返回空列表。"""
    if not mapping:
        return ["类别映射为空"]

    issues = []
    keys = sorted(mapping)
    if keys[0] != 0 or keys != list(range(keys[-1] + 1)):
        if keys[0] != 0:
            issues.append(f"类别编号不是从 0 开始（最小 id={keys[0]}）")
        missing = [i for i in range(keys[0], keys[-1] + 1) if i not in mapping]
        if missing:
            issues.append(
                "类别编号有空缺: "
                + _compress_ranges(missing)
                + f"（共 {len(mapping)} 个名字，编号 {keys[0]}–{keys[-1]}）"
            )

    by_name: dict[str, list[int]] = {}
    for index, name in mapping.items():
        by_name.setdefault(name, []).append(index)
    duplicates = {name: ids for name, ids in by_name.items() if len(ids) > 1}
    if duplicates:
        text = ", ".join(
            f"{name}（id {sorted(ids)}）" for name, ids in sorted(duplicates.items())
        )
        issues.append("重复类别名: " + text)

    families: dict[str, list[str]] = {}
    for name in mapping.values():
        match = _HEALTHY.fullmatch(name)
        if not match:
            continue
        families.setdefault(match.group(1), []).append(name)
    for base, names in sorted(families.items()):
        extras = sorted({name for name in names if name != base})
        if extras:
            issues.append(f"重复健康类 {base}: 另有 {', '.join(extras)}")
    return issues


def train_folder_names(train_dir) -> list[str]:
    """YOLOv8-cls 的类别顺序：train 下子目录名的 Unicode 排序。"""
    root = Path(train_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"训练集目录不存在: {root}")
    return sorted(path.name for path in root.iterdir() if path.is_dir())


def mapping_from_train(train_dir) -> dict[int, str]:
    return {index: name for index, name in enumerate(train_folder_names(train_dir))}


def mapping_mismatch(mapping: dict[int, str], train_dir) -> list[str]:
    """JSON 必须与 train 文件夹顺序逐项相同。"""
    expected = mapping_from_train(train_dir)
    if mapping == expected:
        return []
    problems = [
        f"class_names.json 有 {len(mapping)} 类，train 文件夹有 {len(expected)} 类，"
        "或顺序与 sorted(文件夹名) 不一致"
    ]
    shown = 0
    all_ids = sorted(set(mapping) | set(expected))
    for index in all_ids:
        left = mapping.get(index)
        right = expected.get(index)
        if left != right:
            problems.append(f"  id {index}: json={left!r} 文件夹={right!r}")
            shown += 1
            if shown >= 8:
                problems.append("  ...")
                break
    return problems


def write_class_names(path, mapping: dict[int, str]) -> None:
    payload = {str(index): mapping[index] for index in sorted(mapping)}
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(destination, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def format_issue_report(mapping: dict[int, str]) -> str:
    issues = describe_issues(mapping)
    if not issues:
        return f"类别映射正常：{len(mapping)} 类，编号 0–{len(mapping) - 1} 连续。"
    return "类别映射需要处理：\n" + "\n".join(f"- {item}" for item in issues)
