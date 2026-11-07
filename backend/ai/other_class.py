"""YOLOv8-cls v3 dedicated non-plant class.

v3 has 67 classes. Alphabetical training folders put the folder ``other`` at
YOLO index 1. The matching ``models/class_names.json`` entry is the display
name 「非植物/无关图片」. ``best.pt`` and ``class_names.json`` must be deployed
together; the weights file stays out of git.

Index 1 is not a universal reject. The 64-class checkpoint in this repo stores
``class_1`` (樱桃白粉病) at YOLO index 1. That index is rejected only when the
label is an other/non-plant name, when the loaded head has 67 classes
(v3 contract, even if the json was not updated), or when
``OTHER_CLASS_FORCE_INDEX=1``.
"""
from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence

OTHER_CLASS_MSG = "未检测到植物叶片或病虫害（判定为非植物/无关图片），请上传作物叶片或病斑特写"

# Normalized with casefold and with spaces / underscores / hyphens removed.
_EXACT_LABELS = {
    "other",
    "others",
    "nonplant",
    "notplant",
    "noncrop",
    "notcrop",
    "irrelevant",
    "unrelated",
    "非植物",
    "无关图片",
    "非植物/无关图片",
    "其他",
    "其它",
    "其他类",
    "其它类",
    "非作物",
    "非农作物",
    "无关内容",
}


def other_class_index() -> int:
    return _env_int("OTHER_CLASS_INDEX", 1)


def v3_num_classes():
    """Class count that arms the index shortcut. ``0`` / ``off`` disables it."""
    raw = os.getenv("OTHER_CLASS_MODEL_NC", "67").strip()
    if raw.lower() in {"", "0", "none", "off", "false"}:
        return None
    try:
        return int(raw)
    except ValueError:
        return 67


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _force_index() -> bool:
    return os.getenv("OTHER_CLASS_FORCE_INDEX", "0").strip().lower() not in {
        "",
        "0",
        "false",
        "off",
        "no",
    }


def normalize_label(name) -> str:
    if name is None:
        return ""
    text = str(name).strip().casefold()
    text = text.replace("／", "/").replace("\\", "/")
    return re.sub(r"[\s_\-]+", "", text)


def is_other_class_name(name) -> bool:
    """True for the dedicated reject class and common name variants."""
    text = normalize_label(name)
    if not text:
        return False
    if text in _EXACT_LABELS or text.startswith("nonplant") or text.startswith("notplant"):
        return True
    raw = str(name)
    return "非植物" in raw or "无关图片" in raw


def embedded_class_id(raw):
    """``class_10`` -> 10. Semantic folder names (v3) return None."""
    if isinstance(raw, str) and raw.startswith("class_"):
        tail = raw[6:]
        if tail.isdigit():
            return int(tail)
    return None


def iter_model_classes(model_names):
    if isinstance(model_names, Mapping):
        items = []
        for key, value in model_names.items():
            try:
                idx = int(key)
            except (TypeError, ValueError):
                continue
            items.append((idx, "" if value is None else str(value)))
        items.sort()
        return items
    if isinstance(model_names, Sequence) and not isinstance(model_names, (str, bytes)):
        return [(i, "" if value is None else str(value)) for i, value in enumerate(model_names)]
    return []


def raw_model_name(model_names, index) -> str:
    try:
        idx = int(index)
    except (TypeError, ValueError):
        return ""
    for class_index, name in iter_model_classes(model_names):
        if class_index == idx:
            return name
    return f"class_{idx}"


def _candidate_labels(class_index, raw_name, display_name, class_map):
    labels = [raw_name, display_name]
    if not class_map:
        return labels
    try:
        labels.append(class_map.get(int(class_index)))
    except (TypeError, ValueError):
        pass
    embedded = embedded_class_id(raw_name)
    if embedded is not None:
        labels.append(class_map.get(embedded))
    return labels


def is_other_class(class_index, raw_name="", display_name="", class_map=None, model_nc=None) -> bool:
    """Whether this top-1 must be returned as a rejection instead of a disease."""
    if any(is_other_class_name(label) for label in _candidate_labels(class_index, raw_name, display_name, class_map)):
        return True
    try:
        idx = int(class_index)
    except (TypeError, ValueError):
        return False
    if idx != other_class_index():
        return False
    if _force_index():
        return True
    target = v3_num_classes()
    if target is None or model_nc is None:
        return False
    try:
        return int(model_nc) == int(target)
    except (TypeError, ValueError):
        return False


def other_class_reject_result(class_index, confidence, raw_name="", display_name="", class_map=None, model_nc=None):
    """Same reject shape as the plant-gate / low-confidence responses, or None."""
    if not is_other_class(class_index, raw_name, display_name, class_map, model_nc):
        return None
    try:
        conf = round(float(confidence), 4)
    except (TypeError, ValueError):
        conf = 0.0
    try:
        idx = int(class_index)
    except (TypeError, ValueError):
        idx = -1
    shown = display_name or raw_name or ""
    return {
        "disease": "非农作物",
        "confidence": 0,
        "crop": "",
        "symptoms": "未检测到植物叶片或病虫害",
        "treatment": "请上传作物叶片或病斑特写",
        "source": "rejected",
        "is_confident": False,
        "low_confidence": True,
        "message": OTHER_CLASS_MSG,
        "class_id": -1,
        "reason": "other_class",
        "model_confidence": conf,
        "other_class_index": idx,
        "other_class_name": str(shown),
    }


def class_pair_report(model_names, class_map) -> dict:
    """Check that best.pt labels and class_names.json describe the same head.

    - ``class_N`` weights resolve json by the embedded id (64-class checkpoint;
      YOLO index is not the class number).
    - Any other folder name resolves json by YOLO index (v3 alphabetical folders).
    """
    items = iter_model_classes(model_names)
    nc = len(items)
    mapping = class_map or {}
    missing = []
    other_indices = []
    for idx, raw in items:
        key = embedded_class_id(raw)
        if key is None:
            key = idx
        label = mapping.get(key)
        if mapping and not (isinstance(label, str) and label.strip()):
            missing.append(idx)
        if is_other_class_name(raw) or is_other_class_name(label):
            other_indices.append(idx)
    warnings = []
    if nc and not mapping:
        warnings.append("未加载 class_names.json，best.pt 无法与类别映射成对使用")
    elif missing:
        preview = ", ".join(str(i) for i in missing[:6])
        suffix = "..." if len(missing) > 6 else ""
        warnings.append(
            "class_names.json 缺少 %d 个模型类别（YOLO 下标 %s%s）。"
            "部署 v3 时必须同时替换 models/best.pt 与 models/class_names.json，不能只换权重。"
            % (len(missing), preview, suffix)
        )
    if nc and mapping and len(mapping) != nc:
        warnings.append(
            "类别数不一致: best.pt=%d, class_names.json=%d。"
            "v3 是 67 类，index %d 为拒识类 other / 「非植物/无关图片」，两个文件必须成对部署。"
            % (nc, len(mapping), other_class_index())
        )
    target = v3_num_classes()
    return {
        "model_nc": nc,
        "map_count": len(mapping),
        "missing_indices": missing,
        "other_indices": other_indices,
        "warnings": warnings,
        "paired": not warnings,
        "v3_other_index_armed": bool(target is not None and nc == target),
    }


def format_class_pair_log(report: dict) -> str:
    nc = report.get("model_nc") or 0
    if report.get("warnings"):
        return "[Predictor] 权重与类别映射未成对: " + " ".join(report["warnings"])
    if not nc:
        return "[Predictor] 未加载分类权重，跳过 best.pt / class_names.json 成对检查"
    if report.get("v3_other_index_armed"):
        found = report.get("other_indices") or []
        found_txt = (", ".join(str(i) for i in found)) if found else "标签未写明，仍按下标拒识"
        return (
            "[Predictor] best.pt 与 class_names.json 成对加载: %d 类。"
            "v3 拒识类为 YOLO index %d（other / 「非植物/无关图片」；本权重上的拒识下标: %s）。"
            "只替换其中一个文件会把无关图标成病害名。"
            % (nc, other_class_index(), found_txt)
        )
    return (
        "[Predictor] best.pt 与 class_names.json 成对加载: %d 类。"
        "当前不是 v3 的 %s 类拒识头，不会仅因 YOLO index %d 拒识"
        "（64 类模型的 index 1 是 class_1 / 樱桃白粉病）。"
        % (nc, v3_num_classes() if v3_num_classes() is not None else "禁用", other_class_index())
    )
