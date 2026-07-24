import os, uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from ai.predictor import Predictor
from config import settings
router = APIRouter()
_predictor = None
def get_predictor():
    global _predictor
    if _predictor is None: _predictor = Predictor(settings.MODEL_PATH)
    return _predictor
UPLOAD_DIR = os.path.join(os.path.dirname(__file__),"..","uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED = {".jpg",".jpeg",".png",".bmp",".webp"}
@router.post("/api/diagnose")
async def diagnose(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED: raise HTTPException(400, "不支持的文件格式")
    save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    try:
        content = await file.read()
        with open(save_path, "wb") as f: f.write(content)
        predictor = get_predictor()
        result = predictor.predict(save_path)
        return {"code":200,"message":"诊断成功","data":result}
    except Exception as e: raise HTTPException(500, f"预测失败: {str(e)}")
    finally:
        try:
            if os.path.isfile(save_path): os.remove(save_path)
        except: pass
