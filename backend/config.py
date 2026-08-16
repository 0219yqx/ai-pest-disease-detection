import os

from typing import List

class Settings:
    DEEPSEEK_API_KEY: str = os.environ.get("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.environ.get(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com"
    )
    AMAP_KEY: str = os.environ.get("AMAP_KEY", "")
    AMAP_SECRET: str = os.environ.get("AMAP_SECRET", "")
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.environ.get(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]
    MODEL_PATH: str = os.environ.get(
        "MODEL_PATH",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "best.pt")
    )
    # 前后端共用的类别映射（单一来源，勿再在业务代码里硬编码）
    CLASS_NAMES_PATH: str = os.environ.get(
        "CLASS_NAMES_PATH",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "class_names.json")
    )
    # 上传图片大小上限（MB）
    MAX_UPLOAD_MB: int = int(os.environ.get("MAX_UPLOAD_MB", "10"))
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8000"))


settings = Settings()
