# 田安智识 · 稼护慧眼 — 农作物病虫害智能诊断与防治系统

农业植保领域的 Web 应用：上传叶片照片，AI（YOLOv8 分类模型）识别病虫害并给出防治建议；内置河南 18 地市病情地图、病虫害知识图谱与 AI 对话问诊。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + vue-router + axios + ECharts + vis-network + 高德地图 JS API |
| 后端 | Python FastAPI + uvicorn + ultralytics(YOLOv8) + PyTorch |
| 模型 | `models/best.pt` — YOLOv8n-cls 分类模型（64 类，imgsz=224，Top-1 ≈ 86.6%） |
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
| `MODEL_PATH` | 模型路径。必须与下面的类别映射是同一次训练的产物 | `../models/best.pt` |
| `CLASS_NAMES_PATH` | 类别映射（前后端共用）。必须与 `best.pt` 成对部署 | `../models/class_names.json` |
| `OTHER_CLASS_INDEX` | v3 拒识类的 YOLO 下标 | `1` |
| `OTHER_CLASS_MODEL_NC` | 达到该类别数时，上一项下标即使标签没更新也拒识。`0` 关闭这条捷径 | `67` |
| `OTHER_CLASS_FORCE_INDEX` | 设为 `1` 时，无论类别数，该下标的 top-1 都拒识 | `0` |
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
│   ├── ai/predictor.py          # YOLOv8 推理 + MobileNet 植物门控 + other 类拒识 + 低置信度启发式 + 真实 Top5 候选
│   ├── ai/other_class.py        # v3「other / 非植物/无关图片」拒识与权重-类别映射成对检查
│   ├── api/                     # diagnose / diagnose_ai / history / knowledge / map_api
│   ├── knowledge_graph/         # 病虫害知识库（防治方案）
│   └── crawler/                 # 河南历史虫情数据
├── frontend/
│   └── src/
│       ├── views/               # Home / Diagnose / Consult / MapView / Knowledge
│       └── data/knowledgeData.js
├── models/
│   ├── best.pt                  # 训练好的 YOLOv8n-cls 模型
│   └── class_names.json         # ⭐ 类别映射（前后端单一来源，改类别名只改这里）
└── training/                    # 数据重标注 + 重训练脚本（见下文）
```

## 模型与类别映射

- 当前仓库里的 **YOLOv8n-cls** 是 **64 类**（`class_0`~`class_60`、`class_75`、`class_76`、`class_77`）。YOLO 下标 1 对应 `class_1` / **樱桃白粉病**，不是拒识类。
- 中文名映射统一维护在 **`models/class_names.json`**：后端 `predictor.py` 与前端 `knowledgeData.js` 都从这一份读取，**不要**在别处再硬编码类别名。
- `best.pt` 和 `class_names.json` 必须成对加载。服务启动时会核对类别数：`class_N` 按文件名编号对齐，v3 的文件夹名按下标对齐。只换其中一个，病名会错位。
- `predictor.py` 返回 `top5_list`（真实 Top5 类别名+置信度），前端"其他候选病害"展示的就是模型真实输出，而非伪造数据。

### v3 部署（67 类，index 1 是拒识类）

本地 v3 权重不进 git。上线时同时替换这两份文件：

1. `models/best.pt` — YOLOv8-cls，**67 类**
2. `models/class_names.json` — 与该次训练文件夹顺序一致的 67 条映射

按文件夹名字母序，`other` 在 **YOLO index 1**，展示名是 **「非植物/无关图片」**。诊断接口在 MobileNet 植物门控之后、把结果当成病害返回之前，遇到下列 top-1 会返回与 `not_plant` / `low_confidence` 相同的拒识结构（`source=rejected`，`reason=other_class`，并带 `message`，前端拒识提示会显示「未识别到作物」）：

- 类别名是 `other`、`非植物/无关图片`，或「其他 / 非植物 / 无关图片 / non-plant」等写法
- 或者当前权重是 67 类且 top-1 就是 index 1（即使 json 还是旧病名）

MobileNet 植物门控和低置信度 / 分差 / 熵启发式都保留。不要在这台 1.6GB 机器上加载 CLIP。

注意：部分普通花园照片会被 v3 误判成 `other` 而拒识，这是模型行为，不是门控被关掉。64 类旧权重不会仅因为 index 1 被拒识。

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

**因此当前 86.6% 的 Top-1 准确率是在被污染标签上测得的，真实场景下显示的中文病名可能不正确。** 上线前请按 `training/` 中的脚本重新标注并重训模型。

## 训练（重新训练模型）

```bash
# 1) 按文件名规则把图片重新归位到正确类别（生成 66 类清洗数据集）
#    --name-map 会用仓库现有的 models/class_names.json 为未确证类补中文名；
#    同作物重复"健康"类自动合并（如 玉米健康_2~_5 -> 玉米健康）
python training/fix_dataset_labels.py --train D:/你的数据集目录/train --val D:/你的数据集目录/val \
    --out D:/你的数据集目录/cleaned --name-map models/class_names.json --min-per-class 5 --apply

# 2) 训练（建议 GPU；注意分类任务 --data 传【目录】而非 yaml）
python training/train_yolov8.py --data D:/你的数据集目录/cleaned \
    --model yolov8s-cls.pt --imgsz 384 --epochs 100 --batch 32 --device 0

# 3) 把同一次训练的 best.pt 与 class_names.json 成对复制到仓库 models/
#    v3 若含 other 类：字母序 index 1，展示名写成「非植物/无关图片」
#    Windows 一条龙：直接运行 training/train.bat（含激活环境、训练、部署回仓库）
```

已按上述流程对 `D:\Projects\YOLOv8_PlantDisease` 执行过一次清洗：
- 确认 **9017 张（28%）** 错标图片按文件名规则归位到正确类别；
- 剔除 3 个样本 <5 的垃圾类；同作物重复健康类合并；
- 最终数据集 **66 类**（train 32051 张 / val 4644 张），输出在 `dataset_cleaned/`；
- 冒烟验证：yolov8s-cls @384 第 1 轮即 top1 53.6% / top5 90.3%（原模型 64 类训 37 轮仅 86.6%）。

训练建议（针对标签问题）：

1. **先重标注再训练**：用 `fix_dataset_labels.py` 清洗；删除只有 1 张图的类别；
2. **合并重复"健康"类**：工具已自动合并 `玉米健康_2~_5`、`番茄健康_2~_5` 等；
3. **类别不平衡**：对小样本类使用类别加权或重采样；
4. **增强**：开启 `degrees`/`shear`/`mixup`（作物叶面旋转很常见）；
5. **分辨率**：`imgsz` 提到 384 或 448；
6. **模型**：`yolov8s-cls` / `yolov8m-cls` 通常比 nano 高 2~4 个点。

## 高德地图 Key 安全

`frontend/index.html` 中的 Key 与 `securityJsCode` 已在公开仓库中，**请到高德开放平台控制台**：
1. 为 Key 配置 **域名白名单**（如 `localhost` 与你的部署域名）；
2. 若担心配额被盗用，可重新生成 Key 并仅用于本系统。

## 说明

- 比赛材料（PPTX/DOCX/XLSX）已从仓库移除（保留在本地），避免仓库体积过大。
- 首页统计卡片的数字为演示数据，接入真实业务前请注意标注。
