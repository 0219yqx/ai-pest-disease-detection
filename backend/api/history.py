"""历史病虫害监测数据 API — 来自全国农技中心公开数据"""
import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()

# 爬虫生成的结构化数据
CRAWLER_DATA = Path(__file__).parent.parent / "crawler" / "henan_pest_history.json"


def _load_crawler_data():
    """加载爬虫数据，若文件不存在则返回内嵌精简版"""
    if CRAWLER_DATA.exists():
        with open(CRAWLER_DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    # 内嵌精简版 fallback（与爬虫数据保持同步）
    return {
        "meta": {
            "source": "全国农技中心·病虫害测报处",
            "updated": "2026-06-21",
            "province": "河南省",
        },
        "major_pests": [
            {"name": "小麦条锈病", "crop": "小麦", "annual_area": 3000, "henan_severity": "偏重",
             "henan_risk_zone": "豫南（信阳、南阳、驻马店）", "peak_months": [3,4,5]},
            {"name": "小麦赤霉病", "crop": "小麦", "annual_area": 15000, "henan_severity": "偏重至大流行",
             "henan_risk_zone": "豫南大流行风险高", "peak_months": [4,5]},
            {"name": "玉米螟", "crop": "玉米", "annual_area": 24000, "henan_severity": "中等至偏重",
             "henan_risk_zone": "全省普遍", "peak_months": [6,7,8]},
            {"name": "棉铃虫", "crop": "玉米/棉花", "annual_area": 12000, "henan_severity": "偏重",
             "henan_risk_zone": "黄淮海棉区", "peak_months": [6,7,8,9]},
            {"name": "稻飞虱", "crop": "水稻", "annual_area": 31000, "henan_severity": "中等",
             "henan_risk_zone": "豫南稻区", "peak_months": [7,8,9]},
        ],
        "city_data": {
            "郑州市": {"main_pest": "小麦茎基腐病", "severity": "中"},
            "开封市": {"main_pest": "小麦赤霉病", "severity": "中"},
            "洛阳市": {"main_pest": "小麦条锈病", "severity": "低"},
            "新乡市": {"main_pest": "小麦茎基腐病", "severity": "高"},
            "许昌市": {"main_pest": "玉米螟", "severity": "中"},
            "周口市": {"main_pest": "玉米螟", "severity": "高"},
            "驻马店市": {"main_pest": "小麦条锈病", "severity": "高"},
            "南阳市": {"main_pest": "稻飞虱", "severity": "中"},
            "商丘市": {"main_pest": "玉米大斑病", "severity": "中"},
            "平顶山市": {"main_pest": "玉米螟", "severity": "中"},
            "安阳市": {"main_pest": "小麦白粉病", "severity": "中"},
            "信阳市": {"main_pest": "小麦赤霉病", "severity": "高"},
            "焦作市": {"main_pest": "小麦赤霉病", "severity": "中"},
            "濮阳市": {"main_pest": "玉米锈病", "severity": "中"},
            "漯河市": {"main_pest": "小麦赤霉病", "severity": "中"},
            "三门峡市": {"main_pest": "小麦条锈病", "severity": "低"},
            "鹤壁市": {"main_pest": "玉米灰斑病", "severity": "低"},
            "济源市": {"main_pest": "小麦白粉病", "severity": "低"},
        },
        "monthly_trend": {
            "小麦": [2,3,18,42,65,30,8,2,1,1,1,1],
            "玉米": [1,1,2,5,12,38,72,68,35,8,2,1],
            "水稻": [1,1,2,3,8,22,55,65,42,12,2,1],
        },
        "weekly_trend_2026": {
            "水稻": [10,14,22,35,48,52,44,32,22,15],
            "小麦": [5,12,28,35,22,10,5,3,2,1],
            "玉米": [3,4,6,12,28,40,48,42,25,10],
            "棉花": [2,2,5,8,15,24,30,26,16,6],
        },
        "news_alerts": [
            {"id":1,"level":"high","title":"2026年全国玉米病虫害预计中等至偏重发生",
             "desc":"玉米螟在黄淮海局部偏重，河南冬前百秆活虫量39-40头。","crop":"玉米","drug":"氯虫苯甲酰胺·Bt"},
            {"id":2,"level":"high","title":"河南南部小麦赤霉病大流行风险高",
             "desc":"河南南部（信阳、南阳）赤霉病大流行风险高。","crop":"小麦","drug":"氰烯菌酯·戊唑醇"},
        ],
    }


@router.get("/api/history/pest-data")
async def get_pest_history_data():
    """获取河南省病虫害历史监测数据（来源：全国农技中心公开数据）"""
    data = _load_crawler_data()
    return {"code": 200, "data": data}


@router.get("/api/history/major-pests")
async def get_major_pests():
    """获取重大病虫害列表"""
    data = _load_crawler_data()
    return {"code": 200, "data": data.get("major_pests", [])}


@router.get("/api/history/city-overview")
async def get_city_overview():
    """获取 18 地市病虫害概况"""
    data = _load_crawler_data()
    return {"code": 200, "data": data.get("city_data", {})}


@router.get("/api/history/monthly-trend")
async def get_monthly_trend(crop: str = "小麦"):
    """获取指定作物月度发生趋势"""
    data = _load_crawler_data()
    trends = data.get("monthly_trend", {})
    result = trends.get(crop, [])
    return {"code": 200, "data": {"crop": crop, "months": list(range(1,13)), "values": result}}


@router.get("/api/history/alerts")
async def get_alerts():
    """获取最新预警信息"""
    data = _load_crawler_data()
    return {"code": 200, "data": data.get("news_alerts", [])}
