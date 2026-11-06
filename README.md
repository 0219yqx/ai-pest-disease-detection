# 田安智识 · 稼护慧眼 — 农作物病虫害智能诊断与防治系统

农业植保领域的 Web 应用：上传叶片照片，AI（YOLOv8 分类模型）识别病虫害并给出防治建议；内置河南 18 地市病情地图、病虫害知识图谱与 AI 对话问诊。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + vue-router + axios + ECharts + vis-network + 高德地图 JS API |
| 后端 | Python FastAPI + uvicorn + ultralytics(YOLOv8) + PyTorch |
| 模型 | `models/best.pt` — YOLOv8n-cls（64 类，imgsz=224）。仓库里写过的 Top-1 ≈ 86.6% 是在**污染验证标签**上测的，不是实地病名准确率 |
| AI 问诊 | DeepSeek Chat API（未配置 Key 时提示离线，不再返回写死回复） |

## 快速开始

### 1. 后端

```bash
cd backend
pip install -r requirements.txt        # 建议 Python 3.9+（训练/推理需要 torch）
# 复制环境变量模板并按需填写
copy ..\.env.example .env   # Windows
# Linux: cp ../.env.example .env

python main.py   # 启动于 http://localhost:8000 ，接口文档 /docs
```

环境变量（`.env` 或系统环境变量）：

| 变量 | 说明 | 默认 |
|---|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek 对话问诊的 Key（不填则问诊返回提示） | 空 |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 | `https://api.deepseek.com` |
| `AMAP_KEY` / `AMAP_SECRET` | 高德地图 Key（需在控制台配置域名白名单） | 空 |
| `MODEL_PATH` | 模型路径 | `../models/best.pt` |
| `CLASS_NAMES_PATH` | 类别映射（前后端共用） | `../models/class_names.json` |
| `MAX_UPLOAD_MB` | 上传图片大小上限 | 10 |
| `HOST` / `PORT` | 监听地址/端口 | `0.0.0.0` / `8000` |
| `CORS_ORIGINS` | 允许的前端来源，逗号分隔 | `http://localhost:5173,http://127.0.0.1:5173` |

### 2. 前端

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173 （/api 自动代理到后端 8000）
```

> 若后端换端口，用 `VITE_PROXY_TARGET` 覆盖：`VITE_PROXY_TARGET=http://localhost:8080 npm run dev`

生产构建：`npm run build`，产物在 `frontend/dist`。把 `dist` 内全部文件上传到线上 nginx 站点目录（覆盖旧的 `index.html` 与 `assets`）即可更新界面，无需改后端。

界面是半透明米白纸面叠在整页麦田影像上。背景视频来自 [Pexels · Aerial Drone Footage Of A Wheat Field（Egor Kunovsky）](https://www.pexels.com/video/aerial-drone-footage-of-a-wheat-field-3851640/)，取其中约 8 秒远景麦浪。[Pexels License](https://www.pexels.com/license/) 允许商用和剪辑，不要求署名，也不能把未改动的视频单独转售。文件在 `frontend/public/field/`（`wheat.webm`、`wheat.mp4`、`poster.jpg`）。省流和 `prefers-reduced-motion` 只显示静帧。标题字体为自托管的 Noto Serif SC / Noto Sans SC 子集（`frontend/public/fonts/`）。

## 项目结构

```
├── backend/
│   ├── ai/predictor.py          # YOLOv8 推理 + 四层非农作物拒识 + 真实 Top5 候选
│   ├── api/                     # diagnose / diagnose_ai / history / knowledge / map_api
│   ├── knowledge_graph/         # 病虫害知识库（防治方案）
│   └── crawler/                 # 河南历史虫情数据
├── frontend/
│   └── src/
│       ├── views/               # Home / Diagnose / Consult / MapView / Knowledge
│       └── data/knowledgeData.js
├── models/
│   ├── best.pt                  # 现役 YOLOv8n-cls。换模型时必须连 class_names.json 一起换
│   └── class_names.json         # ⭐ 类别映射（前后端只读这一份）
└── training/                    # 审计、清洗、训练、验证、一条龙脚本（见下文）
```

## 模型与类别映射

- 现役权重是 **YOLOv8n-cls**，类别名是文件夹名 `class_0`–`class_60`、`class_75`、`class_76`、`class_77`（64 类）。编号 **61–74 是空的**。
- 中文名只放在 **`models/class_names.json`**。后端 `backend/ai/predictor.py` 和前端 `frontend/src/data/knowledgeData.js` 都读它，诊断页用 `frontend/src/classNames.js` 查表（规则与 `backend/ai/class_names.py` 相同）。不要在页面或接口里再写一份 id → 病名。
- 这份现役 JSON **故意保留空缺和重复健康类**（`玉米健康_2` 这类）。权重里的名字是 `class_N`，查表用的是 N，不是模型内部下标。Ultralytics 按文件夹名字母序编号，`class_10` 的下标是 2；若按下标去查，会显示成另一种病。
- 清洗并重训之后，JSON 变成 **0..N-1 连续编号**，顺序等于 `sorted(train 文件夹名)`，也就是新模型的下标。部署时要连 `best.pt` 一起换。只改 JSON、不重训，病名会对错位。
- `predictor.py` 返回的 `top5_list` 是模型真实的前 5 名。前端「其他候选病害」用的就是这份结果。

## ⚠️ 已知问题：训练标签需要校正（重要）

通过解码训练图片文件名发现，**部分类别的图片内容与中文标签不符**（合并 PlantVillage / AI Challenger / 自采数据时未按内容重新标注），例如：

- `class_4/5`（玉米叶斑病）内实际是玉米锈病图片；
- `class_7/8`（玉米锈病）内实际是白粉病图片；
- `class_10/11`（水稻褐斑病）内混入玉米灰斑病；
- `class_18`（葡萄健康）内实际是葡萄黑腐病；
- `class_39/40`（番茄晚疫病）内混入草莓叶焦病；
- `class_45`（番茄健康_3）仅 1 张图且实际是细菌性斑点病；
- `class_48/49`（番茄黄化曲叶病毒）内混入柑橘黄龙病图片；
- `class_50/51`（黄瓜健康/白粉病）内混入番茄叶霉病；
- `class_54/55`（玉米健康_4/5）内混入番茄斑枯病。

**因此当前约 86.6% 的 Top-1 是在被污染的验证标签上测得的。** 模型和验证集用的是同一套错误文件夹名，高分只说明「和错误标签一致」，不能当成实地看到的中文病名准确率。上线前用下面的脚本清洗并重训。不要把数据集提交进仓库。

## 训练（清洗 → 训练 → 部署）

数据集放在仓库外面，目录是 YOLOv8 分类的样子：`train/<类别文件夹>/*.jpg` 和 `val/<类别文件夹>/*.jpg`。类别文件夹可以是现在的 `class_N`，也可以已经是中文名。

下面命令都在**仓库根目录**执行。把路径换成你本机的目录。没有 GPU 时把 `--device 0` 改成 `--device cpu`，并把 `--batch` 降到 8 或 16。

```bash
# 0) 不改图片，只出审计报告。先看这份报告再决定要不要清洗。
python training/fix_dataset_labels.py \
    --train D:/你的数据集目录/train \
    --val   D:/你的数据集目录/val \
    --name-map models/class_names.json \
    --report audit_report.md

# 1) 复制到一个新目录（不移动、不删除原始图片）。
#    同作物的「玉米健康_2」会并进「玉米健康」。
#    训练+验证合计少于 5 张，或训练集里一张都没有的类，不会进入结果。
#    输出是 train/<中文类别名>/、val/<中文类别名>/，以及与文件夹排序一致的 class_names.json。
python training/fix_dataset_labels.py \
    --train D:/你的数据集目录/train \
    --val   D:/你的数据集目录/val \
    --out   D:/你的数据集目录/cleaned \
    --name-map models/class_names.json \
    --min-per-class 5 \
    --apply
# 输出目录已经有 train/ 时，加重跑要加 --force。--out 不能和原始 train/val 重叠。

# 2) 训练。默认 yolov8s-cls、imgsz 384、100 轮、patience 30。
#    --data 传目录，不要传 yaml。
python training/train_yolov8.py \
    --data D:/你的数据集目录/cleaned \
    --model yolov8s-cls.pt \
    --imgsz 384 \
    --epochs 100 \
    --patience 30 \
    --batch 32 \
    --device 0

# 3) 看验证集一致率。脚本打印 top1、top5，以及 ultralytics 若返回混淆矩阵时的逐类召回和最常见错分。
python training/validate_cls.py \
    --weights output/plant_disease_v2/weights/best.pt \
    --data D:/你的数据集目录/cleaned \
    --imgsz 384 \
    --device 0

# 4) 接受结果之后，再把权重和类别文件一起换进仓库。只换 best.pt 会让病名对错位。
python training/pipeline.py --deploy-only \
    --weights output/plant_disease_v2/weights/best.pt \
    --data D:/你的数据集目录/cleaned \
    --deploy-to models

# 核对：清洗结果必须是 0..N-1 连续、且与 train 文件夹顺序一致，否则退出码为 1。
python training/check_class_names.py \
    --class-names D:/你的数据集目录/cleaned/class_names.json \
    --data D:/你的数据集目录/cleaned \
    --strict
```

Windows 一条龙（清洗结果不合格或不存在时才清洗，然后训练，再复制到 `models\`）：

```bat
set PY=D:\ProgramData\Anaconda3\envs\yolo\python.exe
set RAW_TRAIN=D:\你的数据集目录\train
set RAW_VAL=D:\你的数据集目录\val
set DATA=D:\你的数据集目录\cleaned
training\train.bat
```

`PY` 必须是已经装了 `torch` 和 `ultralytics` 的解释器。`DATA` 还不能直接训练，而 `RAW_TRAIN`、`RAW_VAL` 或 `NAME_MAP` 缺了任何一个时，脚本会失败并写明缺的是哪一个，不会用空目录继续训。已经有合格的 `DATA`（含 `train/`、`val/` 和与文件夹一致的 `class_names.json`）时，会跳过清洗。强制重洗：`set FORCE_CLEAN=1`。

Linux / macOS 用同样的环境变量跑 `./training/train.sh`。`DATA` 在 shell 脚本里没有默认值，必须自己设。

不跑训练、只检查脚本本身（仓库里没有数据集，也不会下载）：

```bash
python -m unittest training.tests.test_label_pipeline
node --test frontend/src/classNames.test.mjs
```

### 污染标签上的分数，和清洗之后的分数

| | 污染验证集上的分数 | 清洗之后的分数 |
|---|---|---|
| 测的是什么 | 预测文件夹和**原来的错误文件夹**是否一致 | 预测文件夹和**清洗后的文件夹**是否一致 |
| 高分说明什么 | 模型记住了错误标签。约 86.6% 的 Top-1 属于这种 | 只说明和清洗标签一致。文件名对得上的类比较可信 |
| 不能说明什么 | 实地照片上的中文病名是对的 | md5（AI Challenger）和自采、对不上码的图片仍可能标错 |
| 能否和 86.6% 比 | — | 不能。类别集合变了，标签含义也变了，高一点或低一点都不代表模型变好或变坏 |

审计报告里的「确证错标」只统计**文件名解码出的病害和文件夹规划标签不一致**的图片。能解码但已经在正确文件夹里的，不算错标。

以前在 `D:\Projects\YOLOv8_PlantDisease` 上留过一次本地记录（数据集不在本仓库，这里没有重跑，也不要把它当成这次改动的成绩）：当时的计数是 9017 张（28%）文件名可解码；去掉样本过少的类、合并重复健康类之后是 66 类（train 32051 / val 4644）。yolov8s-cls、imgsz 384 只训了 1 轮做冒烟，top1 53.6% / top5 90.3%。那个 28% 用的是旧计数（凡是能解码都算进去）。请以你本机新生成的 `audit_report.md` 和 `validate_cls.py` 的输出为准。

清洗脚本会合并 `玉米健康_2` 这类重复健康类，并丢掉样本过少的类。训练脚本默认 `yolov8s-cls`、`imgsz 384`，并打开旋转、剪切和 mixup。类别仍然可能不平衡。文件名对不上的类要人工看报告里的「码未知 / 自采 / 健康文件名出现在非健康类」。

## 高德地图 Key 安全

`frontend/index.html` 中的 Key 与 `securityJsCode` 已在公开仓库中，**请到高德开放平台控制台**：
1. 为 Key 配置 **域名白名单**（如 `localhost` 与你的部署域名）；
2. 若担心配额被盗用，可重新生成 Key 并仅用于本系统。

## 说明

- 比赛材料（PPTX/DOCX/XLSX）已从仓库移除（保留在本地），避免仓库体积过大。
- 首页统计卡片的数字为演示数据，接入真实业务前请注意标注。
