@echo off
setlocal EnableExtensions
chcp 65001 >nul
REM ============================================================
REM 一条龙（Windows）：需要时清洗 → 训练 → 复制 best.pt 和 class_names.json
REM 在仓库根目录的上一级没有关系，本脚本会自己 cd 到仓库根目录。
REM
REM 可覆盖的环境变量：
REM   PY            Python（须已安装 torch、ultralytics）
REM   RAW_TRAIN     原始 train 目录。清洗结果已合格时可以没有
REM   RAW_VAL       原始 val 目录
REM   DATA          清洗输出 / 训练数据目录
REM   NAME_MAP      旧类别映射，默认 models\class_names.json
REM   MODEL IMGSZ EPOCHS BATCH PATIENCE DEVICE MIN_PER_CLASS
REM   FORCE_CLEAN=1 即使已有清洗结果也重洗
REM ============================================================

cd /d "%~dp0.."

if not defined PY set "PY=D:\ProgramData\Anaconda3\envs\yolo\python.exe"
if not defined RAW_TRAIN set "RAW_TRAIN=D:\Projects\YOLOv8_PlantDisease\dataset\train"
if not defined RAW_VAL set "RAW_VAL=D:\Projects\YOLOv8_PlantDisease\dataset\val"
if not defined DATA set "DATA=D:\Projects\YOLOv8_PlantDisease\dataset_cleaned"
if not defined NAME_MAP set "NAME_MAP=models\class_names.json"
if not defined MODEL set "MODEL=yolov8s-cls.pt"
if not defined IMGSZ set "IMGSZ=384"
if not defined EPOCHS set "EPOCHS=100"
if not defined BATCH set "BATCH=32"
if not defined PATIENCE set "PATIENCE=30"
if not defined DEVICE set "DEVICE=0"
if not defined MIN_PER_CLASS set "MIN_PER_CLASS=5"

"%PY%" -c "import sys" >nul 2>&1
if errorlevel 1 (
  echo [FAIL] 无法运行 Python: "%PY%"
  echo        请设置 PY 为已安装 torch 和 ultralytics 的解释器，例如：
  echo        set PY=C:\Users\you\anaconda3\envs\yolo\python.exe
  exit /b 1
)
if not exist "%NAME_MAP%" (
  echo [FAIL] 找不到类别映射: "%NAME_MAP%"
  echo        默认应是仓库里的 models\class_names.json。请在仓库根目录运行，或设置 NAME_MAP。
  exit /b 1
)

set "EXTRA="
if /I "%FORCE_CLEAN%"=="1" set "EXTRA=--force-clean"

echo [RUN] %PY% training\pipeline.py
echo       DATA=%DATA%
echo       RAW_TRAIN=%RAW_TRAIN%
echo       RAW_VAL=%RAW_VAL%

"%PY%" training\pipeline.py ^
  --raw-train "%RAW_TRAIN%" ^
  --raw-val "%RAW_VAL%" ^
  --data "%DATA%" ^
  --name-map "%NAME_MAP%" ^
  --min-per-class %MIN_PER_CLASS% ^
  --model %MODEL% ^
  --imgsz %IMGSZ% ^
  --epochs %EPOCHS% ^
  --batch %BATCH% ^
  --patience %PATIENCE% ^
  --device %DEVICE% ^
  --deploy-to models ^
  %EXTRA%
if errorlevel 1 (
  echo [FAIL] 清洗、训练或部署失败。上面的 [FAIL] 会写明缺哪个路径。
  exit /b 1
)

echo.
echo [OK] 已用 %DATA% 更新 models\best.pt 和 models\class_names.json
echo      建议再看一遍验证输出，并运行：
echo      "%PY%" training\validate_cls.py --weights output\plant_disease_v2\weights\best.pt --data "%DATA%" --imgsz %IMGSZ% --device %DEVICE%
exit /b 0
