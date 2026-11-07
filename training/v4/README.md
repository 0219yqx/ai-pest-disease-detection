# 小麦病害 v4 训练（在 Windows 本机跑）

这些脚本只在 `D:\Projects\YOLOv8_PlantDisease` 上准备数据和微调。不要在服务器上跑，也不要部署。

v3 是现成的 67 类分类模型，文件夹 `other` 的展示名是「非植物/无关图片」。v4 在不复制 v3 图片的前提下，加上河南原阳田间小麦病害的裁剪图，从 `models/v3/best.pt` 接着训大约 30 个 epoch。

## 类别从哪来

主数据是 [Project-AgML/wheat_disease_detection](https://huggingface.co/datasets/Project-AgML/wheat_disease_detection)（CC-BY-4.0，4156 张，约 1.11 GB，3 个 parquet）。图是 2023 年河南原阳的手机 / 单反田间照片，任务是检测框，不是分类文件夹。

Hugging Face 的 README 里 `class_label` 名字只是字符串 `'0'` … `'6'`，没有病名。病名以 Zenodo [10.5281/zenodo.15621359](https://doi.org/10.5281/zenodo.15621359) 压缩包里的 `xiaomai/xiaomai.yaml` 为准，并用同包里的标注文件核对过（`Powdery` 的框是 0，`Scab` 是 1，`LeafRust` 是 2，`StripeRust` 是 3，`Glume` 是 4，`WheatEar` 是 5，`WheatLeaf` 是 6）：

| yaml id | 英文名 | yaml 里的中文注释 | v4 文件夹 / 展示名 | zip 里的原图张数 |
| --- | --- | --- | --- | --- |
| 0 | Powdery Mildew | 白粉病 | 小麦白粉病 | 400 |
| 1 | Scab | 赤霉病 | 小麦赤霉病 | 1276 |
| 2 | Leaf Rust | 叶锈病 | 小麦叶锈病 | 632 |
| 3 | Stripe Rust | 条锈病 | 小麦条锈病 | 435 |
| 4 | Glume Blotch | 颖枯病 | 小麦颖枯病 | 468 |
| 5 | Wheat Ear | 正常麦穗 | 小麦正常麦穗 | 501 |
| 6 | Wheat Leaf | 正常麦叶 | 小麦正常麦叶 | 444 |

文件夹名在中文注释前加了「小麦」，和现有类（番茄白粉病、玉米锈病）同一套叫法。病名本身没有另起一个。`正常麦穗` 和 `正常麦叶` 在 yaml 里是两类，脚本不把它们并成一个「健康」。

2026-11-07 数过 zip 中央目录：上表 7 类合计 4156 张，每一类都超过 400 张原图，框只会更多。默认阈值是 150 张裁剪。按这个数量，7 类都会留下。真的低于阈值时，脚本丢掉该类并写进 `prepare_report.json`，不并进别的病。

不用 `ashu010/agridrone-data`。那张数据集卡片写的是打包代码为 MIT，原图许可并不跟着 MIT 走。白粉、两种锈病和健康麦穗 / 麦叶在 AgML 里已经够用。也不用 wfd.sysbio.ru（要填表，而且是多标签）。

## other 下标：v3 的 1 在 v4 仍是 index 1

v3 按文件夹名字母序训练，`other` 在 **YOLO index 1**，`class_names.json` 里写成「非植物/无关图片」。

v4 新文件夹都叫「小麦…」。按 Unicode 码点，这些中文名排在 ASCII 的 `other` **后面**，不会插到它前面。所以只要 v3 仍然是「恰好有一个文件夹排在 `other` 前面」，**`other` / 「非植物/无关图片」在 v4 仍是 index 1**。

会后移的是排在新小麦文件夹之后的原有中文类：每插入一个新文件夹，它后面的下标都加 1。类别总数从 67 变成 67 + 实际留下的小麦类数（7 类都留下时是 74）。不要把 v3 分类头的前 67 维抄到新模型上，下标已经对不上，而且头的宽度也变了。Ultralytics 会按新类别数重建最后一层，骨干权重从 `models/v3/best.pt` 接着训。

`prepare_dataset_v4.py` 用本机 `dataset_v3/train` 的真实目录重算，写入 `dataset_v4/class_names.json`，并打印 `OTHER_CLASS_INDEX=<n>`。若打印值不是 1，以这个文件为准，不要继续沿用 v3 的 `OTHER_CLASS_INDEX=1`。

## 怎么跑

环境沿用原来的 yolo 环境（需要 `ultralytics`、`torch`、`Pillow`、`datasets`）。依赖列表在 `training/v4/requirements.txt`。下载默认走国内镜像，已经在脚本里把未设置的 `HF_ENDPOINT` 设为 `https://hf-mirror.com`。要用官方站就加上 `--hf-endpoint https://huggingface.co`。

```bat
set HF_ENDPOINT=https://hf-mirror.com
set PLANT_DISEASE_ROOT=D:\Projects\YOLOv8_PlantDisease
D:\ProgramData\Anaconda3\envs\yolo\python.exe training\v4\prepare_dataset_v4.py
D:\ProgramData\Anaconda3\envs\yolo\python.exe training\v4\train_v4.py
```

也可以直接跑 `training\v4\run_v4.bat`（先准备，再训练）。只想核对映射、不下载：

```bat
python training\v4\prepare_dataset_v4.py --dry-run
```

默认路径（可用同名参数或环境变量改掉）：

| 用途 | 环境变量 | 默认 |
| --- | --- | --- |
| 工程根 | `PLANT_DISEASE_ROOT` | `D:\Projects\YOLOv8_PlantDisease` |
| 现有数据 | `DATASET_V3` | `<root>\dataset_v3` |
| 新数据 | `DATASET_V4` | `<root>\dataset_v4` |
| v3 权重 | `V3_WEIGHTS` | `<root>\models\v3\best.pt` |
| v4 输出权重 | `V4_MODEL_DIR` | `<root>\models\v4` |
| 训练目录 | `V4_PROJECT` / 运行名 | `<root>\output` / `plant_disease_v4` |
| 日志 | `V4_LOG` | `<root>\retrain_run\train_v4.log` |
| HF 缓存 | `HF_DATASETS_CACHE` | `<root>\retrain_run\hf_cache` |

准备阶段做的事：

1. 读 parquet。框是 COCO 的 `[x, y, w, h]`。整张图的坐标都 ≤ 1.5 时按归一化处理，否则按像素。四周留白默认是框宽高的 6%（`--pad`）。
2. 按**原图**划分，不按裁剪划分。同一张照片的哈希相同，它的所有框进同一个 split。数据集里原 `test` 整图并入 `val`（只要 train/val）。想单独留出 test 目录就加 `--keep-test`。
3. 同一类里像素完全相同的裁剪只留一份，优先留在 train，避免验证集看到同一块图。
4. Windows 上用目录联接（`mklink /J`）把 `dataset_v3` 的 train/val 类文件夹接到 `dataset_v4`，包含 `other`。其他系统用符号链接。小麦类是新建的真实文件夹。联接不会把文件写回 v3。
5. 写出 `dataset_v4/class_names.json`（字母序下标 → 中文展示名）和 `prepare_report.json`。

重做数据集加 `--force`。这只会拆掉 `dataset_v4` 里的联接和小麦文件夹，不会删除 `dataset_v3`。

训练阶段（`train_v4.py`）：YOLOv8-cls，`imgsz` 384，`batch` 32，`workers` 4，`epochs` 30，`patience` 10，AMP 开，从 v3 的 `best.pt` 微调。叶面增强和 `training/train_yolov8.py` 相同。日志追加到 `retrain_run/train_v4.log`。结束后把 `best.pt` 和 `class_names.json` 复制到 `models/v4/`，成功时打印一行 `COPIED`。

## 磁盘

- parquet 约 1.2 GB，缓存在 `retrain_run\hf_cache`。
- 裁剪大约再占 1–4 GB（五千多个框，视裁出来的大小而定）。
- `dataset_v3` 是联接，不占第二份。
- `output\plant_disease_v4` 再留大约 3 GB。
- D 盘建议至少空出 **10 GB**。缓存和数据都在工程根目录下，避免占满 C 盘。

## 权重不要提交

`models/v3/`、`models/v4/`、`dataset_v3/`、`dataset_v4/`、`retrain_run/`、`output/` 已在 `.gitignore` 里。`models/v4/best.pt` 只留在本机。不要提交这些权重或图片。仓库里原有的 `models/best.pt` 是另一份旧的 64 类权重，这次训练不会覆盖它。
