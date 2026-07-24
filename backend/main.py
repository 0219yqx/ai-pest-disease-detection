import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api.diagnose import router as dr
from api.diagnose_ai import router as dar
from api.map_api import router as mr
from api.knowledge import router as kr
from api.history import router as hr

app = FastAPI(
    title="\u7530\u5b89\u667a\u8bc6\u00b7\u7a3c\u62a4\u667a\u773c",
    description="\u519c\u4f5c\u7269\u75c5\u866b\u5bb3\u667a\u80fd\u8bca\u65ad\u4e0e\u9632\u6cbb\u7cfb\u7edf API",
    version="2.0.0",
    docs_url="/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(dr)
app.include_router(dar)
app.include_router(mr)
app.include_router(kr)
app.include_router(hr)

@app.get("/api/health")
async def health():
    from knowledge_graph.pest_data import PEST_DATABASE
    return {
        "status": "ok",
        "service": "\u7530\u5b89\u667a\u8bc6\u00b7\u7a3c\u62a4\u667a\u773c",
        "version": "2.0.0",
        "pest_count": len(PEST_DATABASE),
        "crops": ["水稻", "小麦", "玉米", "棉花", "大豆", "花生", "油菜", "甘薯", "马铃薯"],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
