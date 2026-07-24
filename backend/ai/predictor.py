import os, sys, numpy as np
from pathlib import Path
from config import settings

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
            name = results[0].names[top1_idx] if results[0].names else ("class_" + str(top1_idx))

            # 中文类别名映射（class_N → 中文名）
            MODEL_CLASSES = {
                0: '樱桃健康', 1: '樱桃白粉病', 2: '樱桃白粉病_严重',
                3: '玉米健康', 4: '玉米叶斑病_轻', 5: '玉米叶斑病_重', 6: '玉米灰斑病', 7: '玉米锈病_轻', 8: '玉米锈病_重',
                9: '玉米健康_2',
                10: '水稻褐斑病_轻', 11: '水稻褐斑病_重', 12: '水稻锈病_轻', 13: '水稻锈病_重', 14: '水稻叶枯病_轻', 15: '水稻叶枯病_重',
                16: '苹果健康', 17: '苹果赤霉病',
                18: '葡萄健康', 19: '葡萄黑痘病_轻', 20: '葡萄黑痘病_中', 21: '葡萄黑痘病_重', 22: '葡萄霜霉病_轻', 23: '葡萄霜霉病_重', 24: '葡萄健康_2',
                25: '柑橘黄龙病_早期', 26: '柑橘黄龙病_严重', 27: '柑橘疮痂病_轻', 28: '柑橘疮痂病_中', 29: '柑橘疮痂病_重',
                30: '玉米健康_3', 31: '玉米灰斑病_严重', 32: '玉米灰斑病_轻微',
                33: '草莓健康', 34: '草莓早疫病_轻', 35: '草莓早疫病_重', 36: '草莓晚疫病_轻', 37: '草莓晚疫病_重',
                38: '番茄健康', 39: '番茄晚疫病_轻', 40: '番茄晚疫病_重', 41: '番茄健康_2', 42: '番茄白粉病_轻', 43: '番茄白粉病_重',
                44: '番茄细菌病', 45: '番茄健康_3', 46: '番茄早疫病_轻', 47: '番茄早疫病_重',
                48: '番茄黄化曲叶病毒_早期', 49: '番茄黄化曲叶病毒_严重',
                50: '黄瓜健康', 51: '黄瓜白粉病', 52: '黄瓜细菌性叶斑病',
                53: '黄瓜健康_2', 54: '玉米健康_4', 55: '玉米健康_5', 56: '番茄健康_4', 57: '番茄健康_5',
                58: '番茄黄化曲叶病毒_中期', 59: '番茄黄化曲叶病毒_后期', 60: '未知类别',
                61: '小麦健康', 62: '小麦条锈病', 63: '小麦叶锈病', 64: '小麦白粉病', 65: '小麦赤霉病', 66: '小麦根腐病', 67: '小麦纹枯病',
                68: '棉花棉铃虫', 69: '棉花枯萎病', 70: '棉花黄萎病',
                71: '大豆健康', 72: '大豆根腐病', 73: '大豆蚜虫', 74: '大豆紫斑病',
                75: '马铃薯早疫病', 76: '马铃薯晚疫病', 77: '马铃薯健康',
                78: '水稻干尖线虫病', 79: '水稻稻瘟病', 80: '水稻褐斑病_rice', 81: '水稻恶苗病',
            }
            # 如果 name 是 class_N 格式，替换为中文名
            if name.startswith("class_"):
                try:
                    cid = int(name.replace("class_", ""))
                    name = MODEL_CLASSES.get(cid, name)
                except ValueError:
                    pass
            
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
            }
                
        except Exception as e:
            print(f"[Predictor] 推理失败: {e}")
            return {"disease":"识别出错","confidence":0,"crop":"","symptoms":"系统内部错误：" + str(e),"treatment":"请重试或联系管理员","source":"error"}
