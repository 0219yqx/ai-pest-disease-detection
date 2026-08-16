@echo off
REM ============================================================
REM 重训练脚本（Windows）— 田安智识
REM 前置：先用 fix_dataset_labels.py 生成清洗数据集，例如：
REM   D:\ProgramData\Anaconda3\envs\yolo\python.exe training\fix_dataset_labels.py ^
REM       --train D:\Projects\YOLOv8_PlantDisease\dataset\train ^
REM       --val   D:\Projects\YOLOv8_PlantDisease\dataset\val ^
REM       --out   D:\Projects\YOLOv8_PlantDisease\dataset_cleaned ^
REM       --name-map models\class_names.json --min-per-class 5 --apply
REM ============================================================
setlocal

REM ---- 0. 仓库根目录（本文件位于 training\ 下）----
cd /d "%~dp0.."

REM ---- 1. Python 环境（yolo 环境已装 ultralytics+torch；按需修改）----
set "PY=D:\ProgramData\Anaconda3\envs\yolo\python.exe"

REM ---- 2. 训练参数（RTX 4070 8GB 可 batch 32；显存小改 16；想快改 yolov8n-cls 或 imgsz 320）----
set DATA=D:\Projects\YOLOv8_PlantDisease\dataset_cleaned\dataset.yaml
set MODEL=yolov8s-cls.pt
set IMGSZ=384
set EPOCHS=100
set BATCH=32

%PY% training\train_yolov8.py --data %DATA% --model %MODEL% --imgsz %IMGSZ% --epochs %EPOCHS% --batch %BATCH% --device 0 --name plant_disease_v2
if errorlevel 1 goto :fail

REM ---- 3. 部署回仓库（模型 + 类别映射，保持前后端一致）----
copy /Y output\plant_disease_v2\weights\best.pt models\best.pt
copy /Y "D:\Projects\YOLOv8_PlantDisease\dataset_cleaned\class_names.json" models\class_names.json
echo.
echo ============================================================
echo  训练完成！已更新 models\best.pt 与 models\class_names.json
echo  记得: git add models/ && git commit -m "feat: retrain model"
echo ============================================================
exit /b 0

:fail
echo 训练失败，请检查上方日志。
exit /b 1
