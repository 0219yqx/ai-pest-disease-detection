import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fastapi import APIRouter
from config import settings
from knowledge_graph.pest_data import HENAN_HOTSPOTS as HOTSPOTS
router = APIRouter()
@router.get("/api/map/key")
async def get_map_key(): return {"code":200,"data":{"key":settings.AMAP_KEY,"secret":settings.AMAP_SECRET}}
@router.post("/api/map/hotspots")
async def get_hotspots(): return {"code":200,"data":HOTSPOTS}
