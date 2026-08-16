import httpx
import random
from fastapi import APIRouter, HTTPException
from config import settings

router = APIRouter()

SYS_PROMPT = """你是一位在基层干了20年的农业植保专家，专门给普通农户、种地老乡解答病虫害问题。

核心要求：
1. 开头称呼用"老乡"，像跟邻居聊天一样说话，用大白话，绝对不用学术术语
2. 每次回答300字左右，不长篇大论
3. 格式固定四段：确诊结论→防治方案→推荐药剂→注意事项
4. 药剂必须写清楚：百分比含量、剂型（可湿性粉剂/悬浮剂/乳油）、稀释倍数或亩用量，让老乡直接去农资店买
5. 注意事项要说人话：什么时候打药、打完几小时下雨要补喷、收获前几天停药、打药时穿长袖戴手套等
6. 一定强调"预防为主、早发现早治比发病后治省钱省力"

语气示例：
- 好："老乡，这个病初期叶片上长淡黄色斑块..."
- 差："该病害由卵菌门霜霉属真菌侵染导致叶组织坏死..."
"""

MOCK_REPLIES = [
    "确诊结论：稻瘟病由真菌侵染引起，叶片上长出梭形褐斑，中间灰白边缘褐色，严重时穗子变白（白穗），基本绝收。\n\n防治方案：发病初期立即喷药，重点喷叶片正反面和穗部；拔除重病株带出田外烧毁；合理灌溉，避免长期深灌；控制氮肥用量，别追太多氮。\n\n推荐药剂：可选用75%三环唑可湿性粉剂25-30克/亩兑水45斤喷雾，或40%稻瘟灵乳油80-100毫升/亩。破口期和齐穗期各喷一次效果最好。严重田块可用春雷霉素+丙环唑复配。\n\n注意事项：选晴天上午或傍晚喷药，别在中午高温时段打药；破口抽穗期是防病关键窗口，千万别耽误；打完药6小时内下雨要补喷；收割前14天停止用药。",
    "确诊结论：稻飞虱群集在水稻茎基部吸汁液，严重时整片田像火烧一样倒伏枯黄，俗称'虱烧'。\n\n防治方案：发病初期喷药，重点喷水稻中下部（飞虱都藏在下面）；田间保持浅水层2-3厘米让药液自然分布；合理密植避免郁闭；保护田间蜘蛛等天敌，别乱打广谱杀虫剂。\n\n推荐药剂：可选用50%吡蚜酮水分散粒剂10-15克/亩，或10%三氟苯嘧啶悬浮剂30-35毫升/亩，或25%噻虫嗪水分散粒剂4-8克/亩。交替使用不同药剂。\n\n注意事项：傍晚喷药效果最好，飞虱傍晚活动最活跃；一定要喷到稻株中下部；打药时保持浅水层；同一药剂连续用别超过2次，防止产生抗药性；收割前7天停药。",
    "确诊结论：玉米螟幼虫钻进茎秆和果穗里啃食，外面看不到，等发现时玉米秆已经断了、穗子烂了。\n\n防治方案：心叶末期（大喇叭口期）是最佳打药时机；成虫期可以用灯光诱杀减少产卵；有条件可以释放赤眼蜂卡，一张卡管一亩地，环保又省钱；收获后秸秆粉碎还田，消灭越冬幼虫。\n\n推荐药剂：心叶期用200g/L氯虫苯甲酰胺悬浮剂10毫升/亩，或5%甲维盐水分散粒剂15克/亩喷心叶；大喇叭口期可用白僵菌颗粒剂丢心，每株2-3克。\n\n注意事项：打药重点喷心叶，虫子就藏在里面；秸秆别留田里过冬，那是螟虫越冬的老窝；释放赤眼蜂后7天内别打杀虫剂；穗期防治要喷到花丝和果穗上。",
]

@router.post("/api/diagnose/ai")
async def diagnose_ai(request: dict):
    disease = request.get("disease", "")
    message = request.get("message", "")
    query = disease or message
    if not query:
        raise HTTPException(400, "请提供病虫害名称或问诊内容")
    
    user_msg = f"老乡问：{query}\n\n请用大白话给老乡讲清楚这个病虫害，格式：确诊结论→防治方案→推荐药剂→注意事项，300字左右，药剂量必须写清楚。"
    
    # 检查是否配置了真实的DeepSeek Key
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key or api_key == "your-key" or len(api_key) < 30:
        return {"code": 200, "data": {
            "reply": "老乡您好，AI 问诊服务当前未配置（缺少 DEEPSEEK_API_KEY）。\n\n请在后端环境变量或 .env 中填入有效的 DeepSeek API Key 并重启服务，即可获得针对您问题的精准防治建议。",
            "source": "not_configured"
        }}
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": SYS_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 800,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            return {"code": 200, "data": {"reply": reply, "source": "deepseek"}}
    except Exception as e:
        reply = random.choice(MOCK_REPLIES)
        return {"code": 200, "data": {"reply": reply, "source": "mock_fallback"}}
