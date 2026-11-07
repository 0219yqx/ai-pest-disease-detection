# -*- coding: utf-8 -*-
"""Wheat v4 label map, crop boxes, image-level splits, and class-index math.

Category ids come from the Zenodo release cited by
https://huggingface.co/datasets/Project-AgML/wheat_disease_detection
(CC-BY-4.0). The Hugging Face README only stores class_label names
``'0'`` .. ``'6'``. The disease names are in ``xiaomai/xiaomai.yaml``
inside https://doi.org/10.5281/zenodo.15621359 (file ``xiaomai.zip``).
Label files in that zip use the same ids (Powdery → 0, Scab → 1,
LeafRust → 2, StripeRust → 3, Glume → 4, WheatEar → 5, WheatLeaf → 6).

The snapshot below is that yaml ``names:`` block, copied verbatim on
2026-11-07. ``CATEGORIES`` is parsed from it. Do not hand-edit the dict.
"""

from __future__ import annotations

import math
import re
from collections import Counter

# Verbatim `names:` block from xiaomai/xiaomai.yaml (Zenodo 15621359).
ZENODO_YAML_NAMES = """
  0: Powdery Mildew  # 白粉病
  1: Scab            # 赤霉病
  2: Leaf Rust       # 叶锈病
  3: Stripe Rust     # 条锈病
  4: Glume Blotch    # 颖枯病
  5: Wheat Ear       # 正常麦穗
  6: Wheat Leaf      # 正常麦叶
"""

# Image counts from the zip central directory on 2026-11-07 (4156 images).
# Stripe rust is 434 `StripeRust*` files plus `train/stripe_rust.*` (class id 3).
ZENODO_IMAGE_COUNTS = {
    0: 400,
    1: 1276,
    2: 632,
    3: 435,
    4: 468,
    5: 501,
    6: 444,
}

# v3 trains with a folder literally named `other`. Alphabetical order puts
# it at YOLO index 1 (67 classes). The display name is not the folder name.
OTHER_FOLDER = "other"
OTHER_DISPLAY = "非植物/无关图片"
V3_OTHER_INDEX = 1

# Crops below this count are dropped. They are not merged into a neighbor.
DEFAULT_MIN_CROPS = 150

_NAME_LINE = re.compile(
    r"^\s*(\d+)\s*:\s*([^#]+?)\s*(?:#\s*(.*?))?\s*$"
)


def parse_zenodo_names(text: str = ZENODO_YAML_NAMES) -> dict[int, dict[str, str]]:
    """Parse the yaml names block into id → English name, Chinese comment, folder.

    Folder and display names prefix the yaml Chinese comment with ``小麦``.
    The comment itself is the dataset's wording (``白粉病``, ``正常麦穗``, …).
    The prefix matches the rest of this classifier (``番茄白粉病``, ``玉米锈病``)
    and is not a different disease name.
    """
    found = {}
    for line in text.splitlines():
        match = _NAME_LINE.match(line)
        if not match:
            continue
        cid = int(match.group(1))
        english = re.sub(r"\s+", " ", match.group(2)).strip()
        comment = (match.group(3) or "").strip()
        if not english or not comment:
            raise ValueError(f"yaml 类别行缺少英文名或中文注释: {line!r}")
        folder = "小麦" + comment
        found[cid] = {
            "id": cid,
            "en": english,
            "zh_comment": comment,
            "folder": folder,
            "display": folder,
        }
    if sorted(found) != list(range(len(found))):
        raise ValueError(f"类别 id 不连续: {sorted(found)}")
    return found


CATEGORIES = parse_zenodo_names()
ENGLISH_TO_ID = {spec["en"].casefold(): cid for cid, spec in CATEGORIES.items()}
FOLDER_TO_ID = {spec["folder"]: cid for cid, spec in CATEGORIES.items()}


def names_as_list(feature_names) -> list[str] | None:
    """Normalize a Hugging Face ClassLabel ``.names`` list or id→name dict."""
    if feature_names is None:
        return None
    if isinstance(feature_names, dict):
        keys = []
        for key in feature_names:
            try:
                keys.append(int(key))
            except (TypeError, ValueError):
                raise ValueError(f"ClassLabel 名字不是整数下标: {key!r}") from None
        if sorted(keys) != list(range(len(keys))):
            raise ValueError(f"ClassLabel 下标不连续: {sorted(keys)}")
        return [str(feature_names[key] if key in feature_names else feature_names[str(key)]) for key in keys]
    return [str(name) for name in feature_names]


def yaml_id_for_category(category: int, hf_names: list[str] | None) -> int:
    """Map one HF category value to the Zenodo yaml id.

    The published HF class_label names are the strings ``'0'`` .. ``'6'``.
    Those digits are the yaml ids. If a later upload replaces them with the
    English yaml names, match on the name instead of assuming the position.
    Anything else is refused. This function does not invent a disease name.
    """
    try:
        cat = int(category)
    except (TypeError, ValueError):
        raise KeyError(f"无法解析的类别值: {category!r}") from None
    if hf_names is None:
        if cat not in CATEGORIES:
            raise KeyError(f"类别 id {cat} 不在 Zenodo yaml 的 0..{len(CATEGORIES) - 1}")
        return cat
    if cat < 0 or cat >= len(hf_names):
        raise KeyError(f"类别值 {cat} 超出 HF ClassLabel 长度 {len(hf_names)}")
    label = hf_names[cat].strip()
    if label.isdigit():
        yaml_id = int(label)
        if yaml_id not in CATEGORIES:
            raise KeyError(f"HF 名字 {label!r} 不是 yaml 里的类别 id")
        return yaml_id
    yaml_id = ENGLISH_TO_ID.get(re.sub(r"\s+", " ", label).casefold())
    if yaml_id is None:
        known = ", ".join(spec["en"] for spec in CATEGORIES.values())
        raise KeyError(
            f"HF 类别名 {label!r} 对不上 Zenodo yaml。"
            f"只接受 id 字符串 '0'..'6' 或这些英文名: {known}"
        )
    return yaml_id


def resolve_split(source_split: str, keep_test: bool = False) -> str:
    """Map the dataset's split column onto an Ultralytics classify split.

    Default folds ``test`` into ``val`` so the tree is train/val only.
    The whole image moves together; crops from one photo do not split.
    """
    key = str(source_split).strip().lower()
    if key in {"train", "training"}:
        return "train"
    if key in {"val", "valid", "validation"}:
        return "val"
    if key == "test":
        return "test" if keep_test else "val"
    raise ValueError(f"未知的 split 列取值: {source_split!r}")


def _split_rank(split: str) -> int:
    return {"train": 0, "val": 1, "test": 2}[split]


def assign_image_splits(rows: list[dict], keep_test: bool = False) -> list[dict]:
    """Give every crop from one ``image_id`` the same split.

    If the same photo was listed under more than one source split, keep the
    earliest of train < val < test and rewrite every crop. That is the
    no-leak rule: one photo, one split.
    """
    by_image: dict[str, set[str]] = {}
    resolved_rows = []
    for row in rows:
        image_id = str(row["image_id"])
        split = resolve_split(row["source_split"], keep_test=keep_test)
        by_image.setdefault(image_id, set()).add(split)
        copied = dict(row)
        copied["split"] = split
        resolved_rows.append(copied)
    chosen = {}
    for image_id, splits in by_image.items():
        chosen[image_id] = min(splits, key=_split_rank)
    out = []
    for row in resolved_rows:
        row["split"] = chosen[row["image_id"]]
        row["split_conflict"] = len(by_image[row["image_id"]]) > 1
        out.append(row)
    return out


def dedup_crops(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Drop crops whose ``digest`` was already kept.

    Train is processed before val and test, so a duplicated crop stays in
    train and cannot reappear in val. Order inside a split follows the input.
    """
    ordered = sorted(enumerate(rows), key=lambda pair: (_split_rank(pair[1]["split"]), pair[0]))
    seen = set()
    kept = []
    dropped = []
    for _, row in ordered:
        digest = row["digest"]
        if digest in seen:
            dropped.append(row)
            continue
        seen.add(digest)
        kept.append(row)
    return kept, dropped


def decide_classes(rows: list[dict], min_crops: int = DEFAULT_MIN_CROPS) -> tuple[dict[int, int], dict[int, int]]:
    """Keep yaml ids with at least ``min_crops`` crops. No silent merges."""
    counts = Counter(int(row["yaml_id"]) for row in rows)
    kept = {}
    dropped = {}
    for cid in sorted(CATEGORIES):
        n = int(counts.get(cid, 0))
        if n >= min_crops:
            kept[cid] = n
        elif n:
            dropped[cid] = n
    return kept, dropped


def filter_kept(rows: list[dict], kept_ids: dict[int, int]) -> list[dict]:
    return [row for row in rows if int(row["yaml_id"]) in kept_ids]


def boxes_look_normalized(boxes) -> bool:
    """True when every coordinate is in a 0–1.5 range (COCO xywh fractions).

    AgML's HF export uses absolute pixels. The Zenodo txt labels are YOLO
    fractions, but those are not what the prepare script reads. The check is
    per image: a real phone box is hundreds of pixels, so max<=1.5 means
    normalized.
    """
    saw = False
    for box in boxes:
        for value in list(box)[:4]:
            saw = True
            if float(value) > 1.5:
                return False
    return saw


def padded_rect(box, img_w: int, img_h: int, pad_ratio: float, normalized: bool):
    """Expand a COCO ``[x, y, w, h]`` box by ``pad_ratio`` and clip to the image.

    Returns integer ``(x0, y0, x1, y1)`` suitable for ``PIL.Image.crop``,
    or None when the box is empty.
    """
    x, y, w, h = (float(v) for v in list(box)[:4])
    if normalized:
        x, y, w, h = x * img_w, y * img_h, w * img_w, h * img_h
    if w <= 0 or h <= 0:
        return None
    pad_x = w * pad_ratio
    pad_y = h * pad_ratio
    x0 = max(0.0, x - pad_x)
    y0 = max(0.0, y - pad_y)
    x1 = min(float(img_w), x + w + pad_x)
    y1 = min(float(img_h), y + h + pad_y)
    ix0 = max(0, math.floor(x0))
    iy0 = max(0, math.floor(y0))
    ix1 = min(int(img_w), math.ceil(x1))
    iy1 = min(int(img_h), math.ceil(y1))
    if ix1 <= ix0 or iy1 <= iy0:
        return None
    return ix0, iy0, ix1, iy1


def is_other_folder(name: str) -> bool:
    return str(name).strip().casefold() == OTHER_FOLDER


def sorted_class_names(names) -> list[str]:
    """Ultralytics ImageFolder order: Unicode code point, not pinyin."""
    return sorted(set(names), key=lambda name: str(name))


def other_index(names) -> int | None:
    ordered = sorted_class_names(names)
    for index, name in enumerate(ordered):
        if is_other_folder(name):
            return index
    return None


def display_name(folder: str, v3_display: dict[str, str] | None = None) -> str:
    if is_other_folder(folder):
        return OTHER_DISPLAY
    if v3_display and folder in v3_display and not is_other_folder(folder):
        shown = v3_display[folder].strip()
        if shown:
            return shown
    return folder


def v3_display_by_folder(v3_folders: list[str], class_names_json: dict | None) -> dict[str, str]:
    """Zip a v3 ``class_names.json`` onto folders only when the lengths match.

    v3 json keys are YOLO indices, not folder names. Alignment is the
    alphabetical folder order. A length mismatch is ignored so a stale file
    cannot rename classes.
    """
    folders = sorted_class_names(v3_folders)
    if not class_names_json:
        return {}
    try:
        pairs = sorted((int(key), str(value)) for key, value in class_names_json.items())
    except (TypeError, ValueError):
        return {}
    if [index for index, _ in pairs] != list(range(len(pairs))):
        return {}
    if len(pairs) != len(folders):
        return {}
    return {folder: name for folder, (_, name) in zip(folders, pairs)}


def build_class_names(folders, v3_display: dict[str, str] | None = None) -> dict[str, str]:
    """Ultralytics alphabetical index → Chinese display name. Keys are strings."""
    ordered = sorted_class_names(folders)
    return {str(index): display_name(name, v3_display) for index, name in enumerate(ordered)}


def wheat_folders(kept_ids) -> list[str]:
    return [CATEGORIES[cid]["folder"] for cid in sorted(kept_ids)]
