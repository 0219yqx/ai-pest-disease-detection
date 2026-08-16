import os, uuid, io
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
MAX_BYTES = settings.MAX_UPLOAD_MB * 1024 * 1024

@router.post("/api/diagnose")
async def diagnose(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED: raise HTTPException(400, "不支持的文件格式")
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(400, "上传的文件为空")
    if len(content) > MAX_BYTES:
        raise HTTPException(413, f"图片过大，请上传 {settings.MAX_UPLOAD_MB}MB 以内的图片")
    # 校验确实是可解码的图片（防止伪造扩展名 / 损坏文件）
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(content))
        img.verify()
    except Exception:
        raise HTTPException(400, "文件不是有效的图片，请重新上传")
    save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    try:
        with open(save_path, "wb") as f: f.write(content)
        predictor = get_predictor()
        result = predictor.predict(save_path)
        return {"code":200,"message":"诊断成功","data":result}
    except Exception as e: raise HTTPException(500, f"预测失败: {str(e)}")
    finally:
        try:
            if os.path.isfile(save_path): os.remove(save_path)
        except: pass
