import os, sys, json, numpy as np
from pathlib import Path
from config import settings

def _load_class_names():
    """从 models/class_names.json 加载类别映射（前后端单一来源）。
    若文件缺失则退回空映射，推理时以模型原始名（class_N）兜底。"""
    try:
        p = Path(settings.CLASS_NAMES_PATH)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {int(k): v for k, v in data.items()}
    except Exception as e:
        print(f"[Predictor] 类别映射加载失败: {e}")
    return {}

# 类别映射（单一来源 models/class_names.json，勿在此硬编码）
MODEL_CLASSES = _load_class_names()

class Predictor:
    def __init__(self, model_path=None):
        self.model_path = model_path or settings.MODEL_PATH
        self._model = None
        mf = Path(self.model_path)
        if mf.exists():
            try:
                from ultralytics import YOLO
                self._model = YOLO(str(mf))
                print(f"[Predictor] YOLO分类模型加载成功: {mf.name}")
            except Exception as e:
                print(f"[Predictor] YOLO加载失败: {e}")
        else:
            print(f"[Predictor] 模型不存在: {mf}")

    def _resolve_name(self, idx):
        """模型索引 -> 中文名（class_N -> 中文映射）"""
        model_names = getattr(self._model, "names", None) or {}
        raw = model_names.get(idx, f"class_{idx}") if isinstance(model_names, dict) else str(idx)
        if isinstance(raw, str) and raw.startswith("class_"):
            try:
                cid = int(raw.replace("class_", ""))
                return MODEL_CLASSES.get(cid, raw)
            except ValueError:
                return raw
        return raw if isinstance(raw, str) else str(raw)

    def predict(self, image_path):
        if self._model is None:
            return {"disease":"模型未加载","confidence":0,"crop":"","symptoms":"","treatment":"请先训练模型","source":"error"}
        
        try:
            results = self._model(image_path)
            if not results or len(results) == 0:
                return {"disease":"识别失败","confidence":0,"crop":"","symptoms":"","treatment":"请重试","source":"error"}
            
            # 分类模型使用 probs 而不是 boxes
            probs = results[0].probs
            if probs is None:
                return {"disease":"识别失败","confidence":0,"crop":"","symptoms":"","treatment":"请重试","source":"error"}
            
            top1_idx = probs.top1
            top1_conf = float(probs.top1conf)
            name = self._resolve_name(top1_idx)

            # ===== 非农作物图片过滤（四层检测）=====
            # 获取所有类的概率值
            all_probs = probs.data.cpu().numpy() if hasattr(probs.data, 'cpu') else np.array(probs.data)
            top5conf_list = probs.top5conf
            
            # 条件值
            top2_conf = float(top5conf_list[1]) if top5conf_list is not None and len(top5conf_list) > 1 else 0.0
            conf_gap = top1_conf - top2_conf
            epsilon = 1e-10
            entropy = -np.sum(all_probs * np.log(all_probs + epsilon))
            max_entropy = np.log(len(all_probs))
            norm_entropy = entropy / max_entropy
            
            # 1. 绝对置信度过低：任何低于 0.35 的预测都不可信
            #    真实农作物即使患病也通常在 0.5 以上
            if top1_conf < 0.35:
                return {"disease":"非农作物","confidence":round(top1_conf,4),"crop":"","symptoms":"上传的图片不是农作物或不在识别范围内","treatment":"请上传农作物叶片、果实或茎干的清晰照片","source":"rejected","class_id":-1,"reason":"low_confidence"}
            
            # 2. 置信度差距检测：top1 和 top2 差异太小说明模型在犹豫
            #    阈值放宽到 0.35 配合 top1<0.6，能覆盖纯色图等低信息图片
            if conf_gap < 0.35 and top1_conf < 0.6:
                return {"disease":"非农作物","confidence":round(top1_conf,4),"crop":"","symptoms":"图片特征模糊，模型无法确定是否是农作物病虫害","treatment":"请上传清晰的农作物叶片、果实或茎干照片，确保主体突出","source":"rejected","class_id":-1,"conf_gap":round(conf_gap,4),"reason":"small_gap"}
            
            # 3. 信息熵检测：概率分布平坦说明模型不认识这个物体
            if norm_entropy > 0.80 and top1_conf < 0.5:
                return {"disease":"非农作物","confidence":round(top1_conf,4),"crop":"","symptoms":"上传的图片不在训练数据范围内，无法识别","treatment":"请上传训练数据中包含的农作物照片（水稻、小麦、玉米、番茄等）","source":"rejected","class_id":-1,"entropy":round(norm_entropy,4),"reason":"high_entropy"}
            
            # 4. top1 与 top3 平均差距检测：如果 top1 仅略高于后续几个，也是不确定信号
            top3_avg_conf = float(sum(top5conf_list[i] for i in range(min(3, len(top5conf_list)))) / min(3, len(top5conf_list)))
            if top1_conf - top3_avg_conf < 0.2 and top1_conf < 0.5:
                return {"disease":"非农作物","confidence":round(top1_conf,4),"crop":"","symptoms":"图片特征不明确，无法确认是否为农作物病虫害","treatment":"请拍摄农作物患病部位特写，确保光线充足、主体清晰","source":"rejected","class_id":-1,"reason":"flat_distribution"}
            
            top5_idx = [int(probs.top5[i]) for i in range(min(5, len(probs.top5)))]
            top5_conf = [float(top5conf_list[i]) for i in range(min(5, len(top5conf_list)))]
            # 真实 top5 候选（类别名 + 置信度），供前端展示真实候选病害
            top5_list = [
                {"id": idx, "name": self._resolve_name(idx), "conf": round(conf, 4)}
                for idx, conf in zip(top5_idx, top5_conf)
            ]
            # 兼容字段：candidates（class_id/name/confidence）
            candidates = [
                {"class_id": cid, "name": self._resolve_name(cid), "confidence": round(conf, 4)}
                for cid, conf in zip(top5_idx, top5_conf)
            ]
            
            # 判断作物类型（从类别名中提取）
            crop = ""
            if "水稻" in name or "rice" in name.lower():
                crop = "水稻"
            elif "小麦" in name or "wheat" in name.lower():
                crop = "小麦"
            elif "玉米" in name or "corn" in name.lower() or "maize" in name.lower():
                crop = "玉米"
            elif "番茄" in name or "tomato" in name.lower():
                crop = "番茄"
            elif "葡萄" in name or "grape" in name.lower():
                crop = "葡萄"
            elif "柑橘" in name or "citrus" in name.lower():
                crop = "柑橘"
            elif "草莓" in name or "strawberry" in name.lower():
                crop = "草莓"
            elif "苹果" in name or "apple" in name.lower():
                crop = "苹果"
            elif "黄瓜" in name or "cucumber" in name.lower():
                crop = "黄瓜"
            elif "樱桃" in name or "cherry" in name.lower():
                crop = "樱桃"
            elif "马铃薯" in name or "potato" in name.lower():
                crop = "马铃薯"
            elif "棉花" in name or "cotton" in name.lower():
                crop = "棉花"
            elif "大豆" in name or "soybean" in name.lower():
                crop = "大豆"
            
            return {
                "disease": name,
                "confidence": round(top1_conf, 4),
                "crop": crop,
                "symptoms": "",
                "treatment": "",
                "source": "yolov8",
                "class_id": int(top1_idx),
                "top5": top5_conf,
                "top5_list": top5_list,
                "candidates": candidates,
            }
                
        except Exception as e:
            print(f"[Predictor] 推理失败: {e}")
            return {"disease":"识别出错","confidence":0,"crop":"","symptoms":"系统内部错误：" + str(e),"treatment":"请重试或联系管理员","source":"error"}
