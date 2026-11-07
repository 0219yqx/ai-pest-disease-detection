@echo off
REM 在 D:\Projects\YOLOv8_PlantDisease 上准备小麦 v4 并微调。不要在服务器上跑。
setlocal
cd /d "%~dp0..\.."

set "PY=D:\ProgramData\Anaconda3\envs\yolo\python.exe"
set "HF_ENDPOINT=https://hf-mirror.com"
set "PLANT_DISEASE_ROOT=D:\Projects\YOLOv8_PlantDisease"

"%PY%" training\v4\prepare_dataset_v4.py
if errorlevel 1 goto :fail

"%PY%" training\v4\train_v4.py
if errorlevel 1 goto :fail

echo.
echo 完成。权重在 models\v4\ ，不要 git add。
exit /b 0

:fail
echo 失败。准备阶段看屏幕输出，训练阶段再看 retrain_run\train_v4.log
exit /b 1
