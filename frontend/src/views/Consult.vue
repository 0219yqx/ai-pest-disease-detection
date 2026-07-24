<template>
  <div class="page-wrapper">
    <!-- 顶栏 -->
    <div class="consult-top">
      <div class="ct-header">
        <h1>对话问诊</h1>
        <div class="ct-status" :class="{ online: backendOk }">
          <span class="cs-dot"></span>
          {{ backendOk ? 'AI 在线' : '离线模式' }}
        </div>
        <div class="ct-stats">
          <div class="cts-item">
            <span class="cts-val">{{ msgCount }}</span>
            <span class="cts-lbl">消息</span>
          </div>
          <div class="cts-divider"></div>
          <div class="cts-item">
            <span class="cts-val">{{ aiReplyCount }}</span>
            <span class="cts-lbl">AI回复</span>
          </div>
          <div class="cts-divider"></div>
          <div class="cts-item">
            <span class="cts-val">{{ totalWords }}</span>
            <span class="cts-lbl">总字数</span>
          </div>
        </div>
      </div>
      <div class="ct-tags">
        <span v-for="t in quickTags" :key="t" class="ct-tag" @click="sendQuick(t)">{{ t }}</span>
      </div>
    </div>

    <!-- 聊天区 -->
    <div class="chat-area card" ref="chatRef">
      <div class="chat-bg"></div>
      <transition-group name="msg" tag="div" class="chat-flow">
        <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
          <div v-if="msg.role==='ai'" class="msg-avatar avatar-ai">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
          </div>
          <div class="msg-stack">
            <div class="msg-bubble" :class="msg.role" @mouseenter="msg.hover=true" @mouseleave="msg.hover=false">
              <div class="msg-text" v-html="formatMsg(msg.text)"></div>
              <div class="msg-time">{{ msg.time }}</div>
            </div>
            <div v-if="msg.role==='ai'" class="msg-tools" :class="{visible: msg.hover}">
              <button class="mt-btn" @click="copyMsg(msg)" :title="'复制'">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                <span>{{ msg.copied ? '已复制' : '复制' }}</span>
              </button>
            </div>
          </div>
          <div v-if="msg.role==='user'" class="msg-avatar avatar-user">您</div>
        </div>
        <div v-if="loading" key="typing" class="msg-row ai">
          <div class="msg-avatar avatar-ai">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
          </div>
          <div class="msg-bubble ai typing">
            <div class="typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <div class="input-wrap">
        <input v-model="inputText" class="chat-input" placeholder="请问您想咨询什么病虫害问题...（回车发送）" @keyup.enter="sendMsg" :disabled="loading" />
        <span class="char-count" :class="{warn: inputText.length > 200}">{{ inputText.length }}</span>
        <button class="send-btn" @click="sendMsg" :disabled="!inputText.trim()||loading">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
      <div class="input-hint">
        <span>💡 提示：输入病虫害名称，例如"稻瘟病防治"、"葡萄霜霉病用药"</span>
        <span class="kbd">Enter</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const inputText = ref(''); const loading = ref(false); const backendOk = ref(false)
const chatRef = ref(null); const messages = ref([])
const quickTags = ['稻瘟病防治','水稻褐斑病','小麦赤霉病','玉米叶斑病','棉铃虫防治','番茄晚疫病','葡萄霜霉病','柑橘黄龙病','大豆蚜虫','马铃薯晚疫病']

// 会话统计
const msgCount = computed(() => messages.value.length)
const aiReplyCount = computed(() => messages.value.filter(m => m.role === 'ai').length)
const totalWords = computed(() => messages.value.reduce((s, m) => s + (m.text || '').length, 0))

function formatMsg(text) {
  return text.replace(/\n/g, '<br>')
}

function addMsg(role, text) {
  const now = new Date()
  const time = String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0')
  messages.value.push({ role, text, time, hover: false, copied: false })
}
function scrollBottom() { nextTick(() => { const el = chatRef.value; if (el) el.scrollTop = el.scrollHeight }) }

async function copyMsg(msg) {
  try {
    await navigator.clipboard.writeText(msg.text)
    msg.copied = true
    setTimeout(() => { msg.copied = false }, 1500)
  } catch (e) {
    // 兜底
    const ta = document.createElement('textarea')
    ta.value = msg.text; document.body.appendChild(ta); ta.select()
    try { document.execCommand('copy'); msg.copied = true; setTimeout(() => { msg.copied = false }, 1500) } catch (er) {}
    document.body.removeChild(ta)
  }
}

async function sendMsg() {
  const text = inputText.value.trim(); if (!text || loading.value) return
  inputText.value = ''; addMsg('user', text); loading.value = true; scrollBottom()
  try {
    const r = await axios.post('/api/diagnose/ai', { disease: text }, { timeout: 30000 })
    const reply = r.data?.data?.reply || '暂无回复'
    addMsg('ai', reply); backendOk.value = true
  } catch (e) {
    // 面向基层农户的通俗化回答（每条约280-320字）
    const farmAnswers = [
      // ===== 通用模板（匹配到任何关键词时兜底） =====
      {
        keywords: ['防治', '方法', '怎么办', '如何治'],
        answer: `老乡您好！关于您问的这个问题，我用大白话给您讲清楚：

【第一步：先确认是不是】您得仔细看看叶片上有没有斑点、霉层，或者翻翻叶子背面有没有虫子。有照片最好，拍清楚了发给我看一眼最准。

【第二步：对症下药】
· 如果是真菌性病害（叶片有斑点、霉层）：用三环唑、多菌灵或甲基硫菌灵，一喷雾器水（15公斤）加药30-40克，均匀喷到叶面叶背。
· 如果是虫害（看到虫子或被咬的孔洞）：用吡虫啉或氯虫苯甲酰胺，用量按说明书来，一般一亩地用10-15毫升。
· 细菌性病害（软腐、溃疡）：用噻菌铜或中生菌素。

【第三步：注意事项】
① 选晴天上午或下午4点后喷药，别在大中午晒着喷；
② 喷匀了，叶背面也要喷到；
③ 连续用同一种药别超过2次，换着用效果更好；
④ 打完药6小时内下雨就得补喷。

【预防为主】平时多通风透光，别施太多氮肥，发现病叶赶紧摘掉带出田外。早发现早治，省药省钱省心！`
      },
      {
        keywords: ['稻瘟病', '稻飞虱', '纹枯病', '水稻', '褐斑病', '叶枯病', '锈病', '稻曲病', '干尖线虫', '恶苗病'],
        answer: `老乡您好！水稻的问题我给您详细说说：

【稻瘟病】这是水稻最常见的病了。叶片上会长梭形的斑，中间灰白色、边缘褐色。严重了穗子会变白（叫"白穗"），基本绝收。
→ 治法：用三环唑或稻瘟灵，破口期和齐穗期各喷一次。一亩地用20-25克兑水45斤喷。

【水稻褐斑病】叶片出现椭圆形褐色小斑，后期连成大斑。多发生在分蘖期至抽穗期。
→ 治法：用噻菌铜或中生菌素，发病初期连喷2次，间隔7-10天。注意控氮增钾。

【水稻叶枯病（白叶枯）】叶尖或叶缘出现黄褐色条斑，沿叶脉蔓延，湿度大时有菌脓。
→ 治法：用叶枯唑或噻菌铜。重点是田边杂草清除、不串灌水。

【稻曲病】穗子上长黄绿色球状物（稻曲球），灌浆期发生。开花期遇雨易发。
→ 治法：破口前5-7天用戊唑醇或苯醚甲环唑预防一次。

【通用提醒】水稻破口抽穗期是防病的关键时候，千万别大意！提前预防比发病后再治强多了。`
      },
      {
        keywords: ['玉米螟', '玉米', '叶斑病', '灰斑病', '锈病'],
        answer: `老乡您好！玉米的事儿给您说道说道：

【玉米叶斑病（小斑病）】叶片上长椭圆形黄褐色病斑，有同心轮纹，严重时叶片枯死。
→ 治法：用苯醚甲环唑或戊唑醇，发病初期连喷2次，间隔7-10天。

【玉米灰斑病】叶片上出现灰色到褐色的长条斑，顺着叶脉延伸，像被"鞭子抽过"。
→ 治法：用代森锰锌或吡唑醚菌酯。注意田间通风，雨后及时排水。

【玉米锈病】叶片上出现铁锈色粉状夏孢子堆，主要在抽雄后发生。
→ 治法：用三唑酮或丙环唑。发病初期是关键防治期。

【玉米螟】幼虫钻进茎秆里面吃，外面看不到，等发现了玉米秆都断了。
→ 防法：心叶末期（就是玉米快抽雄的时候）是最佳打药时间！用氯虫苯甲酰胺或甲维盐喷心叶。也可以放赤眼蜂卡。

【实用建议】
① 玉米秸秆别留在地里过冬，那是病菌和玉米螟越冬的老窝；
② 种抗病品种能少操很多心；
③ 合理密植，别种太密了通风不好容易发病。`
      },
      {
        keywords: ['小麦', '条锈病', '叶锈病', '白粉病', '赤霉病', '根腐病', '纹枯病', '蚜虫'],
        answer: `老乡您好！小麦病虫害给您掰扯明白：

【条锈病】叶片上排成一排一排的小黄点（夏孢子堆），像铁锈一样。流行起来特别快。
→ 治法：三唑酮或戊唑醇，见病就打！

【叶锈病】叶片上散生圆形橙褐色夏孢子堆，不规则分布。
→ 治法：同条锈病，三唑类杀菌剂都有效。

【白粉病】叶片表面一层白色的粉状物，像撒了面粉似的。
→ 治法：烯唑醇或腈菌唑，早期防治效果好。

【赤霉病】最要命！穗子上长红色霉，麦粒秕瘦，毒素对人畜有害。
→ 治法：扬花初期（10%麦穗开花时）必须打氰烯菌酯或咪鲜胺！

【根腐病】根部变褐腐烂，植株矮小发黄，成片枯死。
→ 治法：用咯菌腈或苯醚甲环醇拌种预防；发病后用恶霉灵灌根。

【纹枯病】茎基部叶鞘出现云纹状病斑，引起烂茎倒伏。
→ 治法：用井冈霉素或噻呋酰胺喷茎基部。返青拔节期是关键。

【提醒】小麦"一喷三防"很重要——把杀虫剂、杀菌剂、叶面肥混在一起喷，一次搞定。`
      },
      {
        keywords: ['棉铃虫', '棉花', '枯萎病', '黄萎病'],
        answer: `老乡您好！棉花种植的难点我来帮您理清：

【棉铃虫】这是棉花最大的敌人！幼虫啃花蕾啃棉桃，一个棉铃虫能毁好几个蕾铃。
→ 治法：氯虫苯甲酰胺或氟铃脲。二代三代棉铃虫是重点防治时期。另外可以用性诱剂诱捕雄虫，减少交配产卵，物理办法也管用。

【枯萎/黄萎病】都是土传病害，得了以后叶子变黄、萎蔫，最后整株死掉。最难治的就是这个，因为病菌在土里。
→ 目前没有特效药能治愈！只能：
  · 拔掉病株带出田外烧毁，千万别留；
  · 轮作倒茬，跟禾本科作物轮作3年以上；
  · 选用抗病品种（中棉所的抗病棉不错）；
  · 用无病土育苗。

【种植要点】
① 合理化控（用缩节胺/DPC），防止棉花疯长；
② 现蕾后及时整枝打杈，保证通风透光；
③ 重施花铃肥，这个时候棉花需肥量最大；
④ 别连作，连作地病害越来越重。`
      },
      {
        keywords: ['番茄', '黄瓜', '白菜', '蔬菜', '晚疫病', '早疫病', '白粉病', '细菌', '黄化曲叶', '霜霉病', '软腐病'],
        answer: `老乡您好！蔬菜（番茄/黄瓜）的病虫害给您一条条说：

【番茄晚疫病】叶片上有水渍状的暗斑，湿度大时叶背面长白霉。烂果硬邦邦的。传播极快，两三天就能毁半棚。
→ 治法：甲霜灵·锰锌或烯酰吗啉。发现中心病株马上打，摘掉病叶带出棚外！

【番茄早疫病】叶片上出现同心轮纹的褐色病斑，像"靶子"一样。从下部老叶开始向上蔓延。
→ 治法：用代森锰锌或苯醚甲环唑，发病初期连喷2-3次。

【番茄白粉病】叶面覆盖白色粉状霉层，严重时叶片卷曲干枯。
→ 治法：用醚菌酯或乙嘧酚磺酸酯，发病初期防治效果好。

【番茄黄化曲叶病毒】顶部叶片发黄、卷曲、皱缩，植株矮化。由烟粉虱传播病毒引起。
→ 治法：无特效药！重点是防烟粉虱——用吡虫啉或噻虫嗪，挂黄板诱杀。

【番茄细菌性病害（疮痂/溃疡）】叶片出现不规则水渍斑，果实上有"鸟眼状"斑点。
→ 治法：用噻菌铜或春雷霉素。注意减少伤口和雨水飞溅。

【黄瓜白粉病】叶面长白粉，后期叶片黄化干枯。
→ 治法：用醚菌酯或氟菌唑，发病前预防效果最好。

【通用经验】
· 蔬菜棚里湿度控制最重要！发病多半是湿大了；
· 别偏施氮肥，磷钾肥跟上植株才壮实抗病；
· 发现病叶立刻摘掉，轮作换茬减少病原积累。`
      },
      {
        keywords: ['葡萄', '黑痘病', '霜霉病', '柑橘', '黄龙病', '疮痂病', '苹果', '赤霉病', '樱桃', '果树', '草莓'],
        answer: `老乡您好！果树病虫害给您详细讲讲：

【葡萄霜霉病】叶片正面出现黄色油渍状斑，背面长白色霜霉层。危害叶片和果穗。
→ 治法：用波尔多液预防，发病后用甲霜·锰锌或烯酰吗啉。

【葡萄黑痘病】嫩叶、嫩梢、幼果上出现黑色凹陷病斑，像"鸟眼"。
→ 治法：用苯醚甲环唑或嘧菌酯，开花前/后是关键防治期。

【柑橘黄龙病】最严重的柑橘病害！叶片斑驳黄化（不对称黄），果实小、歪斜、味苦。木虱传播。
→ 治法：无药可治！发现病树立即砍除烧毁，并彻底防除柑橘木虱。

【柑橘疮痂病】果实和叶片上出现疣状突起，果实变形。
→ 治法：用苯醚甲环唑或多·锰锌，春梢和幼果期各喷一次。

【苹果赤霉病/轮纹病】果实出现红褐色轮纹病斑，引起果腐。
→ 治法：套袋前用甲基托布津或多菌灵，采后用咪鲜胺处理。

【樱桃白粉病】叶片正面覆盖白色粉状霉层，后期卷曲脱落。
→ 治法：用三唑酮或氟硅唑，花后7-10天防治关键期。

【草莓早疫病/晚疫病】叶片出现暗褐色病斑，果实软腐。
→ 治法：用嘧菌酯或烯酰吗啉，控湿是关键。

【通用经验】
· 果树冬剪清园最关键——剪掉病枝、刮除老皮、清园喷石硫合剂；
· 套袋防病效果好，幼果期就要套；
· 加强肥水管理，强壮树势抗病力强。`
      },
      {
        keywords: ['大豆', '根腐病', '蚜虫', '紫斑病', '马铃薯', '晚疫病', '早疫病', '块茎'],
        answer: `老乡您好！大豆和马铃薯的病虫害给您说说：

【大豆根腐病】主根和侧根变褐腐烂，植株矮小黄化，严重时成片枯死。
→ 治法：用咯菌腈或精甲霜灵拌种预防；轮作3年以上；及时排水。

【大豆蚜虫】嫩叶背面密集蚜虫吸汁，叶片卷曲，并传播病毒病。
→ 治法：用吡虫啉或噻虫嗪。苗期发现就要打。

【大豆紫斑病】叶片和豆荚上出现紫红色病斑，影响籽粒品质。
→ 治法：用苯醚甲环唑或多菌灵，结荚初期喷施。

【马铃薯晚疫病】叶片出现暗绿色水渍斑，湿度大时背面长白霉。块茎染病变褐腐烂。流行起来特别快。
→ 治法：用甲霜灵·锰锌或霜脲·锰锌，发现中心病株立即拔除并全田喷药！

【马铃薯早疫病】叶片上出现同心轮纹的褐色病斑，从下部老叶开始。
→ 治法：用代森锰锌或苯醚甲环唑，发病初期连喷2-3次。

【通用经验】
· 选脱毒种薯是无病高产的第一步；
· 高垄栽培+及时排水能减少块茎腐烂；
· 大豆马铃薯轮作3-4年，病害明显减轻。`
      },
    ]

    // 匹配最佳回答
    function matchAnswer(text) {
      const lower = text.toLowerCase()
      let bestMatch = null
      let bestScore = 0
      for (const fa of farmAnswers) {
        const score = fa.keywords.filter(k => text.includes(k)).length
        if (score > bestScore) { bestScore = score; bestMatch = fa }
      }
      return bestMatch?.answer || farmAnswers[0].answer
    }

    addMsg('ai', matchAnswer(text))
  } finally { loading.value = false; scrollBottom() }
}
function sendQuick(t) { inputText.value = t; sendMsg() }

onMounted(async () => {
  addMsg('ai', '老乡您好！👋 我是田安智识·稼护慧眼的植保助手。覆盖 13 种作物 38 种病虫害知识库，您可以直接输入病虫害名称（比如"稻瘟病怎么治"、"葡萄霜霉病用药"），或者从上方标签选择常见问题。我用大白话给您讲清楚，有啥不懂尽管问！')
  await scrollBottom()
  try { await axios.get('/api/health', { timeout: 3000 }); backendOk.value = true } catch (e) { backendOk.value = false }
  // 接收来自知识图谱的跳转参数，自动发送问诊
  const disease = route.query.disease
  if (disease) {
    await nextTick()
    setTimeout(() => {
      inputText.value = `请详细介绍${disease}的防治方法`
      sendMsg()
    }, 600)
  }
})
</script>
<style scoped>
.page-wrapper {
  width: 100%; padding: 0 28px;
  display: flex; flex-direction: column; height: calc(100vh - 32px);
}

.consult-top { margin-bottom: 14px; }
.ct-header { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.ct-header h1 { font-size: 22px; font-weight: 800; color: var(--text-primary); margin: 0; }
.ct-status {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; color: var(--text-tertiary);
  background: var(--gray-100); padding: 4px 10px; border-radius: 999px;
}
.ct-status.online { color: var(--brand-700); background: #dcfce7; }
.cs-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--text-tertiary);
}
.ct-status.online .cs-dot {
  background: var(--brand-600);
  animation: pulse-dot 2s infinite;
}

/* ---- 会话统计 ---- */
.ct-stats {
  margin-left: auto; display: flex; align-items: center; gap: 0;
  padding: 4px 12px; background: var(--bg-card); border: 1px solid var(--gray-200);
  border-radius: 999px;
}
.cts-item { display: flex; flex-direction: column; align-items: center; padding: 0 12px; }
.cts-val { font-size: 14px; font-weight: 800; color: var(--text-primary); font-variant-numeric: tabular-nums; line-height: 1; }
.cts-lbl { font-size: 9px; color: var(--text-tertiary); margin-top: 2px; }
.cts-divider { width: 1px; height: 18px; background: var(--gray-200); }

.ct-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.ct-tag {
  display: inline-flex; align-items: center; padding: 5px 14px; font-size: 12px; font-weight: 500;
  background: var(--brand-50); color: var(--brand-800);
  border: 1px solid var(--brand-100); border-radius: 999px;
  cursor: pointer; transition: all var(--duration-fast) var(--ease-out);
}
.ct-tag:hover {
  background: var(--brand-700); color: #fff; border-color: var(--brand-700);
  transform: translateY(-2px); box-shadow: 0 4px 12px rgba(46,125,50,0.25);
}
.ct-tag:active { transform: translateY(0) scale(0.96); }

/* ---- 聊天区 ---- */
.chat-area {
  flex: 1; overflow-y: auto; padding: 20px;
  border-radius: var(--radius-lg); margin-bottom: 14px;
  display: flex; flex-direction: column; gap: 14px; min-height: 300px;
  background: var(--bg-card); position: relative;
}
.chat-bg {
  position: absolute; inset: 0; pointer-events: none; opacity: 0.4;
  background-image: radial-gradient(circle at 15% 20%, rgba(76,175,80,0.04) 0%, transparent 35%),
                    radial-gradient(circle at 85% 80%, rgba(29,78,216,0.03) 0%, transparent 35%);
}
.chat-flow { display: flex; flex-direction: column; gap: 14px; position: relative; }

/* 消息入场过渡 */
.msg-enter-active { transition: all 350ms var(--ease-spring); }
.msg-leave-active { transition: all 200ms var(--ease-out); }
.msg-enter-from { opacity: 0; transform: translateY(12px) scale(0.96); }
.msg-leave-to   { opacity: 0; transform: translateX(20px); }

.msg-row { display: flex; align-items: flex-start; gap: 10px; max-width: 78%; }
.msg-row.user { margin-left: auto; flex-direction: row-reverse; }

.msg-avatar {
  width: 34px; height: 34px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 11px; font-weight: 700;
}
.avatar-ai  { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #15803d; }
.avatar-user { background: var(--gray-100); color: var(--gray-500); }

.msg-bubble {
  padding: 12px 16px; border-radius: 14px; font-size: 13px; line-height: 1.7;
  white-space: pre-wrap; word-break: break-word;
  position: relative;
}
.msg-bubble.user {
  background: linear-gradient(135deg, var(--brand-700), var(--brand-600));
  color: #fff; border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(46,125,50,0.2);
}
.msg-bubble.ai {
  background: #fff; color: var(--text-primary);
  border: 1px solid var(--gray-200); border-bottom-left-radius: 4px;
}
.msg-time { font-size: 10px; color: var(--text-tertiary); margin-top: 4px; text-align: right; }
.msg-bubble.ai .msg-time { text-align: left; }

/* ---- 消息工具栏（复制） ---- */
.msg-stack { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.msg-tools {
  display: flex; gap: 4px; opacity: 0; transition: opacity var(--duration-fast);
}
.msg-tools.visible { opacity: 1; }
.mt-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 8px; font-size: 10px; font-weight: 500;
  background: var(--gray-50); color: var(--text-tertiary);
  border: 1px solid var(--gray-200); border-radius: 6px;
  cursor: pointer; transition: all var(--duration-fast);
}
.mt-btn:hover { background: var(--brand-50); color: var(--brand-700); border-color: var(--brand-200); }

/* ---- Typing 动画 ---- */
.typing { padding: 16px 20px; }
.typing-dots { display: flex; gap: 5px; align-items: center; }
.typing-dots span {
  width: 7px; height: 7px; border-radius: 50%; background: var(--brand-400);
  animation: typingBounce 1.3s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.15s; }
.typing-dots span:nth-child(3) { animation-delay: 0.3s; }
@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-5px); opacity: 1; }
}

/* ---- 输入区 ---- */
.input-area { padding-bottom: 16px; }
.input-wrap {
  display: flex; gap: 0; background: #fff;
  border: 1.5px solid var(--gray-200); border-radius: 14px;
  overflow: hidden; transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
  box-shadow: var(--shadow-sm);
}
.input-wrap:focus-within {
  border-color: var(--brand-400);
  box-shadow: 0 0 0 4px rgba(76,175,80,0.1), var(--shadow-sm);
}
.chat-input {
  flex: 1; padding: 12px 16px; border: none; outline: none;
  font-size: 13px; background: transparent;
}
.chat-input::placeholder { color: var(--gray-400); }

/* ---- 字数计数 ---- */
.char-count {
  font-size: 11px; color: var(--text-tertiary); padding: 0 10px;
  font-variant-numeric: tabular-nums; align-self: center;
  transition: color var(--duration-fast);
}
.char-count.warn { color: var(--warning); font-weight: 600; }

.send-btn {
  width: 44px; display: flex; align-items: center; justify-content: center;
  background: transparent; border: none; cursor: pointer;
  color: var(--gray-400); transition: all var(--duration-fast) var(--ease-spring);
  padding-right: 6px;
}
.send-btn:hover:not(:disabled) {
  color: var(--brand-700); transform: scale(1.15) rotate(-8deg);
}
.send-btn:active:not(:disabled) { transform: scale(0.92); }
.send-btn:disabled { opacity: 0.3; cursor: not-allowed; }

/* ---- 输入提示 ---- */
.input-hint {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 6px; padding: 0 4px;
  font-size: 11px; color: var(--text-tertiary);
}
</style>
