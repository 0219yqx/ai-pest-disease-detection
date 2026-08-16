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

生产构建：`npm run build`，产物在 `frontend/dist`。

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
│   ├── best.pt                  # 训练好的 YOLOv8n-cls 模型
│   └── class_names.json         # ⭐ 类别映射（前后端单一来源，改类别名只改这里）
└── training/                    # 数据重标注 + 重训练脚本（见下文）
```

## 模型与类别映射

- 当前模型为 **YOLOv8n-cls 分类模型**，共 **64 个真实类别**（`class_0`~`class_60`、`class_75`、`class_76`、`class_77`）。
- 中文名映射统一维护在 **`models/class_names.json`**：后端 `predictor.py` 与前端 `knowledgeData.js` 都从这一份读取，**不要**在别处再硬编码类别名。
- `predictor.py` 返回 `top5_list`（真实 Top5 类别名+置信度），前端"其他候选病害"展示的就是模型真实输出，而非伪造数据。

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
# 1) 按文件名规则把图片重新归位到正确类别（自动清洗 + 生成新 dataset.yaml）
#    --name-map 会用仓库现有的 models/class_names.json 为未确证类补中文名
python training/fix_dataset_labels.py --train D:/你的数据集目录/train --val D:/你的数据集目录/val \
    --out D:/你的数据集目录/cleaned --name-map models/class_names.json --min-per-class 5 --apply

# 2) 训练（建议 GPU；参数可调）
python training/train_yolov8.py --data D:/你的数据集目录/cleaned/dataset.yaml \
    --model yolov8s-cls.pt --imgsz 384 --epochs 100 --batch 32 --device 0

# 3) 训练完成后把 best.pt 复制到仓库 models/，并核对 models/class_names.json 与 dataset.yaml 一致
#    Windows 一条龙：直接运行 training/train.bat（含激活环境、训练、部署回仓库）
```

训练建议（针对标签问题）：

1. **先重标注再训练**：用 `fix_dataset_labels.py` 清洗；删除只有 1 张图的类别（如 class_44/45）；
2. **合并重复"健康"类**：`玉米健康_2~_5`、`番茄健康_2~_5` 等应合并为同一类；
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
