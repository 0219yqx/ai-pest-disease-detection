#!/usr/bin/env bash
# 一条龙（Linux / macOS）：需要时清洗 → 训练 → 复制 best.pt 和 class_names.json
# 环境变量与 training/train.bat 相同：PY RAW_TRAIN RAW_VAL DATA NAME_MAP
# MODEL IMGSZ EPOCHS BATCH PATIENCE DEVICE MIN_PER_CLASS FORCE_CLEAN=1
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PY:-python3}"
RAW_TRAIN="${RAW_TRAIN:-}"
RAW_VAL="${RAW_VAL:-}"
DATA="${DATA:-}"
NAME_MAP="${NAME_MAP:-models/class_names.json}"
MODEL="${MODEL:-yolov8s-cls.pt}"
IMGSZ="${IMGSZ:-384}"
EPOCHS="${EPOCHS:-100}"
BATCH="${BATCH:-32}"
PATIENCE="${PATIENCE:-30}"
DEVICE="${DEVICE:-0}"
MIN_PER_CLASS="${MIN_PER_CLASS:-5}"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "[FAIL] 找不到 Python: $PY"
  echo "       请设置 PY 为已安装 torch 和 ultralytics 的解释器。"
  exit 1
fi
if [[ ! -f "$NAME_MAP" ]]; then
  echo "[FAIL] 找不到类别映射: $NAME_MAP"
  exit 1
fi
if [[ -z "$DATA" ]]; then
  echo "[FAIL] 请设置 DATA 为清洗输出目录，例如："
  echo "       DATA=/path/to/dataset_cleaned RAW_TRAIN=/path/to/train RAW_VAL=/path/to/val ./training/train.sh"
  exit 1
fi

extra=()
if [[ "${FORCE_CLEAN:-}" == "1" ]]; then
  extra+=(--force-clean)
fi

"$PY" training/pipeline.py \
  --raw-train "$RAW_TRAIN" \
  --raw-val "$RAW_VAL" \
  --data "$DATA" \
  --name-map "$NAME_MAP" \
  --min-per-class "$MIN_PER_CLASS" \
  --model "$MODEL" \
  --imgsz "$IMGSZ" \
  --epochs "$EPOCHS" \
  --batch "$BATCH" \
  --patience "$PATIENCE" \
  --device "$DEVICE" \
  --deploy-to models \
  "${extra[@]}"

echo "[OK] 已用 $DATA 更新 models/best.pt 和 models/class_names.json"
