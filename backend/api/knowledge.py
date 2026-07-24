from fastapi import APIRouter, HTTPException
from knowledge_graph.pest_data import get_pest_info, search_pests, get_knowledge_graph, PEST_DATABASE, enrich_pest_record
router = APIRouter()

@router.get("/api/knowledge/graph")
async def kg(): return {"code":200,"data":get_knowledge_graph()}

@router.get("/api/knowledge/list")
async def pest_list():
    return {"code":200,"data":[enrich_pest_record(v) for v in PEST_DATABASE.values()]}

@router.get("/api/knowledge/pest/{name}")
async def pest_detail(name: str):
    info = get_pest_info(name)
    if not info: raise HTTPException(404, f"未找到: {name}")
    return {"code":200,"data":enrich_pest_record(info)}

@router.get("/api/knowledge/search")
async def search(keyword: str):
    if not keyword: raise HTTPException(400, "请提供关键词")
    results = search_pests(keyword)
    return {"code":200,"data":[enrich_pest_record(r) for r in results]}
