<template>
  <div class="page-wrapper">
    <!-- 顶部欢迎横幅 -->
    <div class="welcome-banner">
      <div class="wb-bg">
        <div class="wb-orb wb-orb-1"></div>
        <div class="wb-orb wb-orb-2"></div>
        <div class="wb-orb wb-orb-3"></div>
        <div class="wb-grid"></div>
      </div>
      <div class="wb-content">
        <div class="wb-left">
          <div class="wb-tagline">
            <span class="wb-live-dot"></span>
            智慧植保 · 实时监测
          </div>
          <h1 class="wb-greeting">{{ greeting }}，稼护慧眼 <span class="wb-wave">👋</span></h1>
          <p class="wb-date">{{ today }} · 河南省农作物病虫害智能识别与防控平台</p>
        </div>
        <div class="wb-right">
          <div class="wb-chip"><span class="wb-chip-icon">🌾</span> 河南省 大小麦收割期</div>
          <div class="wb-chip"><span class="wb-chip-icon">☀️</span> 28℃ 适合田间作业</div>
          <div class="wb-chip wb-chip-warn"><span class="wb-chip-icon">🌡️</span> 本周高温预警 注意防暑</div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="metrics-grid">
      <div class="metric-card mc-main card-ribbon animate-fade-in" style="animation-delay: 0ms">
        <div class="mc-icon-wrap mc-icon-green">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
        </div>
        <div class="mc-body">
          <div class="mc-label">监测地市</div>
          <div class="mc-value">18</div>
        </div>
        <div class="mc-progress"><div class="mc-bar mc-bar-green" style="width:78%"></div></div>
        <div class="mc-footer">
          <span>覆盖全省主要农区</span>
          <span class="delta delta-up">↑ 2</span>
        </div>
      </div>
      <div class="metric-card card-ribbon animate-fade-in" style="animation-delay: 80ms">
        <div class="mc-icon-wrap mc-icon-amber">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e8a317" stroke-width="2"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>
        </div>
        <div class="mc-body">
          <div class="mc-label">本周新增虫情</div>
          <div class="mc-value" style="color:var(--color-wheat)">68</div>
        </div>
        <div class="sparkline" aria-hidden="true">
          <span class="sl-bar" v-for="(h,i) in [30,45,38,60,52,75,68]" :key="i" :class="{peak: h===75}" :style="{height: h+'%'}"></span>
        </div>
        <div class="mc-footer">
          <span>同比上周</span>
          <span class="delta delta-up">↑ 8.3%</span>
        </div>
      </div>
      <div class="metric-card card-ribbon animate-fade-in" style="animation-delay: 160ms">
        <div class="mc-icon-wrap mc-icon-blue">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1976d2" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </div>
        <div class="mc-body">
          <div class="mc-label">本月AI识别数</div>
          <div class="mc-value" style="color:var(--color-corn)">1,286</div>
        </div>
        <div class="sparkline" aria-hidden="true">
          <span class="sl-bar" v-for="(h,i) in [40,55,48,62,70,85,92]" :key="i" :class="{peak: h===92}" :style="{height: h+'%'}"></span>
        </div>
        <div class="mc-footer">
          <span>精确率 97.8%</span>
          <span class="delta delta-up">↑ 12%</span>
        </div>
      </div>
      <div class="metric-card card-ribbon animate-fade-in" style="animation-delay: 240ms">
        <div class="mc-icon-wrap mc-icon-red">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#c62828" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01"/></svg>
        </div>
        <div class="mc-body">
          <div class="mc-label">待处理预警</div>
          <div class="mc-value" style="color:var(--color-cotton)">5</div>
        </div>
        <div class="mc-progress"><div class="mc-bar mc-bar-red" style="width:18%"></div></div>
        <div class="mc-footer">
          <span>需立即处理</span>
          <span class="delta delta-down">↓ 2</span>
        </div>
      </div>
      <div class="metric-card card-ribbon animate-fade-in" style="animation-delay: 300ms">
        <div class="mc-icon-wrap mc-icon-purple">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><path d="M20 12a8 8 0 0 0-8-8v8h8z" opacity="0.5"/></svg>
        </div>
        <div class="mc-body">
          <div class="mc-label">知识库覆盖</div>
          <div class="mc-value" style="color:#7c3aed">38</div>
        </div>
        <div class="mc-progress"><div class="mc-bar mc-bar-purple" style="width:100%"></div></div>
        <div class="mc-footer">
          <span>13种作物 · 38条记录</span>
          <span class="delta delta-up">↑ 11</span>
        </div>
      </div>
      <div class="metric-card card-ribbon animate-fade-in" style="animation-delay: 360ms">
        <div class="mc-icon-wrap mc-icon-teal">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0f766e" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="mc-body">
          <div class="mc-label">防治方案</div>
          <div class="mc-value" style="color:#0f766e">114</div>
        </div>
        <div class="mc-progress"><div class="mc-bar mc-bar-teal" style="width:100%"></div></div>
        <div class="mc-footer">
          <span>全覆盖 · 114条方案</span>
          <span class="delta delta-up">↑ 20</span>
        </div>
      </div>
    </div>

    <!-- 中间区域：趋势图 + 作物分布 + 天气 -->
    <div class="row-3col">
      <div class="card chart-box animate-fade-in" style="animation-delay: 400ms; grid-column: span 1;">
        <div class="section-header">
          <span class="section-title">📈 病虫害趋势（近7日）</span>
          <span class="section-badge">单位：个数</span>
        </div>
        <v-chart :option="trendOpt" style="height:280px;width:100%" autoresize />
      </div>
      <div class="card crop-pie-box animate-fade-in" style="animation-delay: 440ms">
        <div class="section-header">
          <span class="section-title">作物病害分布</span>
        </div>
        <v-chart :option="cropPieOpt" style="height:280px;width:100%" autoresize />
      </div>
      <div class="card weather-box animate-fade-in" style="animation-delay: 480ms">
        <div class="section-header">
          <span class="section-title">农事气象</span>
          <span class="section-badge">郑州 · 今日</span>
        </div>
        <div class="weather-content">
          <div class="wc-main">
            <div class="wc-temp">28°</div>
            <div class="wc-desc">
              <div class="wc-condition">☀️ 晴转多云</div>
              <div class="wc-detail">湿度 62% · 东南风 3级</div>
            </div>
          </div>
          <div class="wc-forecast">
            <div class="wf-item" v-for="d in weatherDays" :key="d.day">
              <div class="wf-day">{{ d.day }}</div>
              <div class="wf-icon">{{ d.icon }}</div>
              <div class="wf-temps">
                <span class="wf-high">{{ d.high }}°</span>
                <span class="wf-low">/{{ d.low }}°</span>
              </div>
            </div>
          </div>
          <div class="wc-advice">
            <div class="wa-icon">🌱</div>
            <div class="wa-text">适宜田间施药，风速较低，药液不易飘移。建议上午10点前或下午4点后喷施。</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 下方区域：预警列表 + 农事指南/快捷操作/防治效果 -->
    <div class="row-2col" style="margin-top:14px">
      <div class="left-col">
        <!-- 预警列表 -->
        <div class="card alert-box animate-fade-in" style="animation-delay: 500ms">
          <div class="section-header">
            <span class="section-title">近期预警</span>
            <span class="section-badge alert-badge">{{ alerts.length }} 条 · 实时</span>
          </div>
          <div class="alert-list">
            <div v-for="a in alerts" :key="a.id" class="alert-item" :class="'alert-' + a.level">
              <div class="ai-dot"></div>
              <div class="ai-body">
                <div class="ai-title">{{ a.title }}</div>
                <div class="ai-desc">{{ a.desc }}</div>
              </div>
              <div class="ai-meta">
                <div class="ai-time">{{ a.time }}</div>
                <span class="ai-level-tag" :class="'tag-' + a.level">{{ a.levelText }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 农事指南 -->
        <div class="card guide-box animate-fade-in" style="animation-delay: 540ms; margin-top:14px">
          <div class="section-header">
            <span class="section-title">📋 农事指南</span>
            <span class="section-badge guide-badge">6月重点</span>
          </div>
          <div class="guide-grid">
            <div v-for="g in guideItems" :key="g.id" class="guide-item" :style="{ borderLeftColor: g.color }">
              <div class="gi-head">
                <span class="gi-icon">{{ g.icon }}</span>
                <span class="gi-title">{{ g.title }}</span>
              </div>
              <div class="gi-desc">{{ g.desc }}</div>
              <div class="gi-tags">
                <span class="gi-tag">{{ g.crop }}</span>
                <span class="gi-tag gi-tag-time">{{ g.time }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 防治效果追踪 -->
        <div class="card effect-box animate-fade-in" style="animation-delay: 560ms; margin-top:14px">
          <div class="section-header">
            <span class="section-title">💊 近期防治效果</span>
            <span class="section-badge effect-badge">本月</span>
          </div>
          <div class="effect-grid">
            <div v-for="e in effectItems" :key="e.name" class="effect-item">
              <div class="ei-head">
                <span class="ei-name">{{ e.name }}</span>
                <span class="ei-rate" :style="{ color: e.rateColor }">{{ e.rate }}%</span>
              </div>
              <div class="ei-bar-bg">
                <div class="ei-bar-fill" :style="{ width: e.rate + '%', background: e.barColor }"></div>
              </div>
              <div class="ei-foot">
                <span>处理 {{ e.count }} 次</span>
                <span>{{ e.trend }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="right-stack">
        <!-- 快捷操作 -->
        <div class="card quick-box animate-fade-in" style="animation-delay: 520ms">
          <div class="section-header">
            <span class="section-title">快捷操作</span>
          </div>
          <div class="qa-grid">
            <div class="qa-item2" @click="$router.push('/diagnose')">
              <div class="qa-icon qa-icon-green">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              </div>
              <div class="qa-lbl">AI识别</div>
            </div>
            <div class="qa-item2" @click="$router.push('/consult')">
              <div class="qa-icon qa-icon-amber">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              </div>
              <div class="qa-lbl">对话问诊</div>
            </div>
            <div class="qa-item2" @click="$router.push('/map')">
              <div class="qa-icon qa-icon-blue">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/></svg>
              </div>
              <div class="qa-lbl">病情地图</div>
            </div>
            <div class="qa-item2" @click="$router.push('/knowledge')">
              <div class="qa-icon qa-icon-purple">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/></svg>
              </div>
              <div class="qa-lbl">知识图谱</div>
            </div>
          </div>
        </div>

        <!-- 农资价格参考 -->
        <div class="card price-box animate-fade-in" style="animation-delay: 560ms">
          <div class="section-header">
            <span class="section-title">🛒 农资行情参考</span>
            <span class="section-badge price-badge">河南</span>
          </div>
          <div class="price-list">
            <div v-for="p in priceItems" :key="p.name" class="price-item">
              <div class="pi-left">
                <span class="pi-name">{{ p.name }}</span>
                <span class="pi-spec">{{ p.spec }}</span>
              </div>
              <div class="pi-right">
                <span class="pi-price" :class="p.change > 0 ? 'pi-up' : p.change < 0 ? 'pi-down' : ''">¥{{ p.price }}</span>
                <span class="pi-change" :class="p.change > 0 ? 'pi-up' : p.change < 0 ? 'pi-down' : ''">{{ p.change > 0 ? '+' : '' }}{{ p.change }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 系统动态 -->
        <div class="card news-box animate-fade-in" style="animation-delay: 600ms">
          <div class="section-header">
            <span class="section-title">系统动态</span>
          </div>
          <div class="news-list">
            <div v-for="n in newsItems" :key="n.id" class="news-item">
              <div class="ni-dot" :class="'ni-' + n.type"></div>
              <div class="ni-body">
                <div class="ni-title">{{ n.title }}</div>
                <div class="ni-time">{{ n.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部技术架构栏 -->
    <div class="tech-bar card animate-fade-in" style="animation-delay: 640ms">
      <div class="tb-label">
        <span class="tb-label-dot"></span>
        <span>系统架构</span>
      </div>
      <div class="tb-items">
        <div class="tb-item">
          <span class="status-dot sd-green"></span>
          <div class="tb-icon tb-icon-green">YOLOv8</div>
          <div class="tb-text"><div class="tb-v">检测引擎</div><div class="tb-l">实时推理 · 30ms</div></div>
        </div>
        <div class="tb-divider"></div>
        <div class="tb-item">
          <span class="status-dot sd-green"></span>
          <div class="tb-icon tb-icon-amber">38</div>
          <div class="tb-text"><div class="tb-v">识别病种</div><div class="tb-l">13种作物</div></div>
        </div>
        <div class="tb-divider"></div>
        <div class="tb-item">
          <span class="status-dot sd-green"></span>
          <div class="tb-icon tb-icon-blue">DeepSeek</div>
          <div class="tb-text"><div class="tb-v">AI问诊</div><div class="tb-l">智能对话</div></div>
        </div>
        <div class="tb-divider"></div>
        <div class="tb-item">
          <span class="status-dot sd-green"></span>
          <div class="tb-icon tb-icon-purple">AMap</div>
          <div class="tb-text"><div class="tb-v">高德地图</div><div class="tb-l">空间分析</div></div>
        </div>
        <div class="tb-divider"></div>
        <div class="tb-item">
          <span class="status-dot sd-amber"></span>
          <div class="tb-icon tb-icon-teal">FastAPI</div>
          <div class="tb-text"><div class="tb-v">后端服务</div><div class="tb-l">高并发</div></div>
        </div>
        <div class="tb-divider"></div>
        <div class="tb-item">
          <span class="status-dot sd-green"></span>
          <div class="tb-icon tb-icon-cyan">5级</div>
          <div class="tb-text"><div class="tb-v">级联Fallback</div><div class="tb-l">高可用</div></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent, MarkLineComponent, MarkPointComponent } from 'echarts/components'
import VChart from 'vue-echarts'
use([CanvasRenderer, LineChart, PieChart, TooltipComponent, LegendComponent, GridComponent, MarkLineComponent, MarkPointComponent])

const days = ['06/11','06/12','06/13','06/14','06/15','06/16','06/17']
const now = new Date()
const today = now.getFullYear() + '年' + (now.getMonth()+1) + '月' + now.getDate() + '日'
const hour = now.getHours()
const greeting = hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好'

const weatherDays = [
  { day: '明天', icon: '⛅', high: 30, low: 21 },
  { day: '周四', icon: '🌤', high: 32, low: 22 },
  { day: '周五', icon: '🌧', high: 26, low: 19 },
  { day: '周六', icon: '☀️', high: 29, low: 20 },
]

const alerts = [
  { id:1, title:'信阳稻瘟病高风险预警', desc:'信阳地区稻瘟病发病率上升至42%，建议立即喷施三环唑。', level:'high', levelText:'紧急', time:'10分钟前' },
  { id:2, title:'周口小麦赤霉病监测', desc:'周口麦区赤霉病零星发生，建议喷施戊唑醇预防。', level:'high', levelText:'紧急', time:'1小时前' },
  { id:3, title:'南阳棉铃虫中度发生', desc:'南阳棉区二代棉铃虫发生面积扩大，需关注。', level:'mid', levelText:'警告', time:'3小时前' },
  { id:4, title:'许昌小麦条锈病监测', desc:'许昌小麦条锈病零星发生，持续监测中。', level:'low', levelText:'关注', time:'6小时前' },
  { id:5, title:'平顶山玉米灰斑病提示', desc:'近期降雨偏多，玉米灰斑病有流行趋势。', level:'mid', levelText:'警告', time:'昨天' },
]

const guideItems = [
  { id:1, icon:'🌾', title:'水稻破口期防治', desc:'6月中旬水稻进入破口抽穗期，重点防治稻瘟病、稻曲病和褐斑病，推荐三环唑+吡蚜酮组合施药。', crop:'水稻', time:'6月中旬', color:'#2e7d32' },
  { id:2, icon:'🌾', title:'小麦收割后管理', desc:'小麦收割后及时灭茬整地，清除田间病残体，减少下季条锈病、赤霉病初侵染源。', crop:'小麦', time:'6月上旬', color:'#e8a317' },
  { id:3, icon:'🌽', title:'玉米叶斑病防控', desc:'玉米抽雄前后注意叶斑病、灰斑病和锈病，可用苯醚甲环唑或戊唑醇预防。', crop:'玉米', time:'6-7月', color:'#1976d2' },
  { id:4, icon:'🍅', title:'番茄晚疫病预警', desc:'雨季来临前重点防控番茄晚疫病、早疫病和白粉病，注意通风降湿，及时清除病叶。', crop:'番茄', time:'6月全月', color:'#dc2626' },
]

// 防治效果数据
const effectItems = [
  { name: '稻瘟病', rate: 92, count: 48, trend: '↑ 较上月提升', rateColor: '#15803d', barColor: 'linear-gradient(90deg, #4caf50, #2e7d32)' },
  { name: '小麦条锈病', rate: 95, count: 56, trend: '↑ 显著提升', rateColor: '#15803d', barColor: 'linear-gradient(90deg, #22c55e, #16a34a)' },
  { name: '玉米叶斑病', rate: 81, count: 29, trend: '↑ 提升6%', rateColor: '#1976d2', barColor: 'linear-gradient(90deg, #60a5fa, #1976d2)' },
  { name: '棉铃虫', rate: 87, count: 35, trend: '→ 保持稳定', rateColor: '#e8a317', barColor: 'linear-gradient(90deg, #fbbf24, #e8a317)' },
  { name: '番茄晚疫病', rate: 78, count: 42, trend: '↓ 略降3%', rateColor: '#dc2626', barColor: 'linear-gradient(90deg, #f87171, #dc2626)' },
]

// 农资价格数据（模拟河南市场均价）
const priceItems = [
  { name: '吡蚜酮', spec: '50% WP', price: '85', change: 2.3 },
  { name: '三环唑', spec: '75% WP', price: '45', change: 0 },
  { name: '氯虫苯甲酰胺', spec: '20% SC', price: '120', change: -1.5 },
  { name: '甲维盐', spec: '2.2% EC', price: '38', change: 5.2 },
  { name: '戊唑醇', spec: '430g/L SC', price: '55', change: 1.8 },
  { name: '噻呋酰胺', spec: '240g/L SC', price: '95', change: -0.8 },
  { name: '烯酰吗啉', spec: '50% WP', price: '72', change: 3.1 },
]

const newsItems = [
  { id:1, title:'知识库扩充至38条病虫害数据(13种作物)', time:'今天 09:30', type:'update' },
  { id:2, title:'YOLOv8 模型新增水稻/番茄/葡萄等病害识别', time:'昨天 16:20', type:'model' },
  { id:3, title:'系统已完成月度安全巡检', time:'06/15', type:'system' },
  { id:4, title:'新增驻马店、信阳监测点接入', time:'06/14', type:'update' },
  { id:5, title:'病情地图筛选联动功能上线', time:'06/13', type:'update' },
  { id:6, title:'高德地图API升级至v2.0', time:'06/12', type:'system' },
]

// ===== 趋势图配置（美化版：更多系列、渐变填充、标记点） =====
const trendOpt = {
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255,255,255,0.97)',
    borderColor: '#e5e7eb', borderWidth: 1,
    borderRadius: 10,
    textStyle: { color: '#111827', fontSize: 12, fontWeight: 500 },
    padding: [12, 16],
    extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.08);',
    axisPointer: { type: 'cross', crossStyle: { color: '#aaa' } },
  },
  legend: {
    data: ['稻瘟病', '褐斑病', '玉米叶斑病', '棉铃虫', '大豆蚜虫'],
    bottom: 0,
    icon: 'roundRect',
    itemWidth: 12, itemHeight: 6,
    itemGap: 16,
    textStyle: { color: '#6b7280', fontSize: 11 },
    selectedMode: true,
  },
  grid: { left: 44, right: 12, top: 20, bottom: 38 },
  xAxis: {
    type: 'category', data: days,
    axisLine: { show: false }, axisTick: { show: false },
    axisLabel: { color: '#9ca3b4', fontSize: 11, fontWeight: 500 },
    boundaryGap: false,
  },
  yAxis: {
    type: 'value',
    name: '个数',
    nameTextStyle: { color: '#9ca3b4', fontSize: 11, padding: [0, 36, 0, 0] },
    splitLine: { lineStyle: { color: '#f1f3f7', type: 'dashed', width: 1 } },
    axisLabel: { color: '#9ca3b4', fontSize: 11 },
    minInterval: 5,
  },
  series: [
    {
      name: '稻瘟病', type: 'line', smooth: true, data: [12,18,15,22,28,24,19],
      symbol: 'circle', symbolSize: 6,
      lineStyle: { color: '#2e7d32', width: 2.5, cap: 'round' },
      itemStyle: { color: '#2e7d32', borderWidth: 2, borderColor: '#fff' },
      emphasis: { focus: 'series', itemStyle: { shadowBlur: 8, shadowColor: 'rgba(46,125,50,0.3)', symbolSize: 8 } },
      areaStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(46,125,50,0.25)' },
            { offset: 0.5, color: 'rgba(46,125,50,0.08)' },
            { offset: 1, color: 'rgba(46,125,50,0.01)' }
          ]
        }
      },
      markPoint: {
        data: [{ type: 'max', name: '最高值' }],
        symbolSize: [30, 18],
        itemStyle: { color: '#2e7d32', borderColor: '#fff', borderWidth: 1 },
        label: { fontSize: 10, color: '#fff', fontWeight: 600 },
      },
    },
    {
      name: '褐斑病', type: 'line', smooth: true, data: [8,10,13,9,14,17,12],
      symbol: 'circle', symbolSize: 5,
      lineStyle: { color: '#e8a317', width: 2, cap: 'round' },
      itemStyle: { color: '#e8a317', borderWidth: 2, borderColor: '#fff' },
      areaStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(232,163,23,0.18)' },
            { offset: 0.6, color: 'rgba(232,163,23,0.05)' },
            { offset: 1, color: 'rgba(232,163,23,0.01)' }
          ]
        }
      },
    },
    {
      name: '玉米叶斑病', type: 'line', smooth: true, data: [5,7,6,9,11,8,10],
      symbol: 'circle', symbolSize: 5,
      lineStyle: { color: '#1976d2', width: 2, cap: 'round' },
      itemStyle: { color: '#1976d2', borderWidth: 2, borderColor: '#fff' },
      areaStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(25,118,210,0.16)' },
            { offset: 0.6, color: 'rgba(25,118,210,0.04)' },
            { offset: 1, color: 'rgba(25,118,210,0.01)' }
          ]
        }
      },
    },
    {
      name: '棉铃虫', type: 'line', smooth: true, data: [20,25,18,30,35,28,32],
      symbol: 'circle', symbolSize: 5,
      lineStyle: { color: '#ec4899', width: 2, cap: 'round' },
      itemStyle: { color: '#ec4899', borderWidth: 2, borderColor: '#fff' },
      areaStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(236,72,153,0.14)' },
            { offset: 0.7, color: 'rgba(236,72,153,0.03)' },
            { offset: 1, color: 'rgba(236,72,153,0.01)' }
          ]
        }
      },
    },
    {
      name: '大豆蚜虫', type: 'line', smooth: true, data: [3,5,4,7,9,6,8],
      symbol: 'circle', symbolSize: 5,
      lineStyle: { color: '#c62828', width: 2, cap: 'round' },
      itemStyle: { color: '#c62828', borderWidth: 2, borderColor: '#fff' },
      areaStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(198,40,40,0.12)' },
            { offset: 0.7, color: 'rgba(198,40,40,0.03)' },
            { offset: 1, color: 'rgba(198,40,40,0.01)' }
          ]
        }
      },
    },
  ],
}

// 作物分布饼图 — 雅致版：统一绿色调渐变 + 内外双环
const cropPieOpt = {
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(255,255,255,0.97)',
    borderColor: '#e5e7eb', borderWidth: 1,
    borderRadius: 10,
    textStyle: { color: '#374151', fontSize: 12 },
    formatter: (p) => `<b>${p.name}</b>　${p.value} 种<br><span style="color:#6b7280;font-size:11px">占比 ${p.percent}%</span>`,
  },
  legend: {
    type: 'scroll',
    bottom: 0,
    icon: 'circle', itemWidth: 7, itemHeight: 7,
    textStyle: { color: '#9ca3af', fontSize: 10 },
    itemGap: 8,
    pageIconColor: '#16a34a',
    pageIconInactiveColor: '#d1d5db',
    pageTextStyle: { color: '#6b7280', fontSize: 10 },
    pageIconSize: 9,
    formatter: (name) => {
      const item = [
        { name:'水稻', value:6 }, { name:'小麦', value:6 }, { name:'番茄', value:5 },
        { name:'玉米', value:3 }, { name:'棉花', value:3 }, { name:'大豆', value:3 },
        { name:'柑橘', value:3 }, { name:'葡萄', value:2 }, { name:'草莓', value:2 },
        { name:'黄瓜', value:2 }, { name:'马铃薯', value:2 }, { name:'樱桃', value:1 },
        { name:'苹果', value:1 },
      ].find(d => d.name === name)
      return item ? `${name}  ${item.value}种` : name
    },
  },
  series: [{
    type: 'pie',
    radius: ['28%', '66%'],
    center: ['50%', '43%'],
    roseType: 'area',
    avoidLabelOverlap: true,
    itemStyle: {
      borderRadius: 5,
      borderColor: '#ffffff',
      borderWidth: 2,
    },
    label: {
      show: true,
      fontSize: 10,
      color: '#6b7280',
      formatter: (p) => p.percent >= 7 ? `{name|${p.name}}\n{val|${p.value}种}` : '',
      rich: {
        name: { fontSize: 10, color: '#374151', fontWeight: 600, lineHeight: 14 },
        val: { fontSize: 9, color: '#9ca3af', lineHeight: 13 },
      },
    },
    labelLine: {
      length: 6,
      length2: 5,
      smooth: true,
      lineStyle: { width: 1, color: '#d1d5db' },
    },
    labelLayout: { hideOverlap: true },
    emphasis: {
      label: { show: true, fontSize: 11, fontWeight: 'bold', formatter: '{b}\n{c}种' },
      itemStyle: { shadowBlur: 12, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.10)' },
      scale: true, scaleSize: 5,
    },
    data: [
      { value:6,  name:'水稻',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#16a34a'},{offset:1,color:'#4ade80'}] } } },
      { value:6,  name:'小麦',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#d97706'},{offset:1,color:'#fbbf24'}] } } },
      { value:5,  name:'番茄',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#dc2626'},{offset:1,color:'#f87171'}] } } },
      { value:3,  name:'玉米',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#2563eb'},{offset:1,color:'#60a5fa'}] } } },
      { value:3,  name:'棉花',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#be123c'},{offset:1,color:'#fb7185'}] } } },
      { value:3,  name:'大豆',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#ca8a04'},{offset:1,color:'#fde047'}] } } },
      { value:3,  name:'柑橘',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#ea580c'},{offset:1,color:'#fb923c'}] } } },
      { value:2,  name:'葡萄',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#7c3aed'},{offset:1,color:'#a78bfa'}] } } },
      { value:2,  name:'草莓',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#db2777'},{offset:1,color:'#f472b6'}] } } },
      { value:2,  name:'黄瓜',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#059669'},{offset:1,color:'#34d399'}] } } },
      { value:2,  name:'马铃薯', itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#92400e'},{offset:1,color:'#d97706'}] } } },
      { value:1,  name:'樱桃',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#9f1239'},{offset:1,color:'#e11d48'}] } } },
      { value:1,  name:'苹果',   itemStyle:{ color:{ type:'linear',x:0,y:0,x2:1,y2:1, colorStops:[{offset:0,color:'#b91c1c'},{offset:1,color:'#f87171'}] } } },
    ].sort((a, b) => b.value - a.value),
  }],
}
</script>
<style scoped>
.page-wrapper { width: 100%; padding: 0 28px 20px; }

/* ---- 欢迎横幅 ---- */
.welcome-banner {
  position: relative; padding: 28px 32px; border-radius: var(--radius-xl);
  margin-bottom: 20px; overflow: hidden;
  background: linear-gradient(135deg, #0f2b1a 0%, #1a4030 40%, #1b3a2a 100%);
  color: #fff;
  box-shadow: 0 12px 32px -8px rgba(15,43,26,0.35);
}
.wb-bg { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
.wb-orb { position: absolute; border-radius: 50%; filter: blur(40px); opacity: 0.35; }
.wb-orb-1 { width: 200px; height: 200px; background: #2e7d32; top: -60px; right: 10%; animation: float 6s ease-in-out infinite; }
.wb-orb-2 { width: 120px; height: 120px; background: #1d4ed8; bottom: -40px; left: 20%; animation: float 7s ease-in-out infinite reverse; }
.wb-orb-3 { width: 80px; height: 80px; background: #e8a317; top: 10px; right: 40%; animation: float 5s ease-in-out infinite; }
.wb-grid {
  position: absolute; inset: 0; opacity: 0.08;
  background-image:
    linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(ellipse at 80% 20%, #000 0%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse at 80% 20%, #000 0%, transparent 70%);
}
.wb-content { position: relative; display: flex; justify-content: space-between; align-items: flex-end; gap: 20px; }
.wb-tagline {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 600; letter-spacing: 1.5px;
  color: rgba(255,255,255,0.7);
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1);
  padding: 3px 10px; border-radius: 999px; margin-bottom: 12px;
}
.wb-live-dot {
  width: 6px; height: 6px; border-radius: 50%; background: #5cda7c;
  box-shadow: 0 0 6px #5cda7c; animation: pulse-dot 1.6s infinite;
}
.wb-greeting { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; margin: 0; }
.wb-wave { display: inline-block; animation: wave 2.5s ease-in-out infinite; transform-origin: 70% 70%; }
@keyframes wave { 0%,60%,100%{transform:rotate(0)} 15%{transform:rotate(14deg)} 30%{transform:rotate(-8deg)} 45%{transform:rotate(14deg)} }
.wb-date { font-size: 12px; opacity: 0.55; margin-top: 6px; }
.wb-right { display: flex; gap: 10px; flex-shrink: 0; }
.wb-chip {
  display: flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.1); backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.12);
  padding: 6px 14px; border-radius: 999px; font-size: 12px; opacity: 0.85;
  transition: all var(--duration-fast) var(--ease-out);
}
.wb-chip:hover { background: rgba(255,255,255,0.18); transform: translateY(-1px); }
.wb-chip-warn { background: rgba(245,158,11,0.18); border-color: rgba(245,158,11,0.3); }
.wb-chip-icon { font-size: 14px; }

/* ---- 统计卡片 ---- */
.metrics-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; margin-bottom: 20px; }
.metric-card {
  background: var(--bg-card); border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg); padding: 18px 20px;
  transition: all var(--duration-normal) var(--ease-out);
  backdrop-filter: var(--glass-blur);
  position: relative; overflow: hidden;
}
.metric-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--grad-brand); opacity: 0; transition: opacity var(--duration-normal);
}
.metric-card:hover::before { opacity: 1; }
.metric-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-3px); border-color: var(--brand-200); }
.mc-main { border-left: 3px solid var(--brand-600); }
.mc-icon-wrap { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; transition: transform var(--duration-normal) var(--ease-spring); }
.metric-card:hover .mc-icon-wrap { transform: scale(1.08) rotate(-4deg); }
.mc-icon-green  { background: #dcfce7; }
.mc-icon-amber  { background: #fef3c7; }
.mc-icon-blue   { background: #dbeafe; }
.mc-icon-red    { background: #fee2e2; }
.mc-icon-purple { background: #ede9fe; }
.mc-icon-teal   { background: #ccfbf1; }
.mc-body { margin-bottom: 10px; }
.mc-label { font-size: 12px; color: var(--text-tertiary); font-weight: 500; }
.mc-value { font-size: 28px; font-weight: 800; color: var(--text-primary); margin-top: 2px; font-variant-numeric: tabular-nums; letter-spacing: -0.5px; }
.mc-progress { height: 3px; background: var(--gray-100); border-radius: 2px; overflow: hidden; margin-bottom: 6px; }
.mc-bar { height: 100%; border-radius: 2px; animation: barGrow 900ms var(--ease-out); }
.mc-bar-green  { background: linear-gradient(90deg, #4caf50, #2e7d32); }
.mc-bar-amber  { background: linear-gradient(90deg, #fbbf24, #e8a317); }
.mc-bar-blue   { background: linear-gradient(90deg, #60a5fa, #1976d2); }
.mc-bar-red    { background: linear-gradient(90deg, #f87171, #c62828); }
.mc-bar-purple { background: linear-gradient(90deg, #a78bfa, #7c3aed); }
.mc-bar-teal   { background: linear-gradient(90deg, #5eead4, #0f766e); }
.mc-footer {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 11px; color: var(--text-tertiary); gap: 6px;
}
.metric-card .sparkline { width: 100%; height: 24px; margin-bottom: 6px; }

/* ---- 3列布局 ---- */
.row-3col { display: grid; grid-template-columns: 1.6fr 280px 260px; gap: 14px; margin-bottom: 14px; }
.chart-box { padding: 20px; }
.crop-pie-box { padding: 20px; }
.weather-box { padding: 20px; }

/* ---- 天气卡片 ---- */
.weather-content { display: flex; flex-direction: column; gap: 14px; }
.wc-main { display: flex; align-items: center; gap: 14px; }
.wc-temp { font-size: 42px; font-weight: 800; color: var(--text-primary); line-height: 1; }
.wc-condition { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.wc-detail { font-size: 11px; color: var(--text-tertiary); margin-top: 2px; }
.wc-forecast { display: flex; gap: 0; }
.wf-item { flex: 1; text-align: center; padding: 8px 4px; border-right: 1px solid var(--gray-100); }
.wf-item:last-child { border-right: none; }
.wf-day { font-size: 11px; color: var(--text-tertiary); margin-bottom: 4px; }
.wf-icon { font-size: 18px; margin-bottom: 4px; }
.wf-high { font-size: 13px; font-weight: 700; color: var(--text-primary); }
.wf-low { font-size: 11px; color: var(--text-tertiary); }
.wc-advice {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; background: #f0fdf4; border: 1px solid #bbf7d0;
  border-radius: var(--radius-sm);
}
.wa-icon { font-size: 20px; }
.wa-text { font-size: 12px; color: #15803d; line-height: 1.6; }

/* ---- 2列布局 ---- */
.row-2col { display: grid; grid-template-columns: 1fr 320px; gap: 14px; }
.left-col { display: flex; flex-direction: column; }
.right-stack { display: flex; flex-direction: column; gap: 14px; }

/* ---- 预警列表 ---- */
.alert-box { padding: 20px; }
.alert-list { display: flex; flex-direction: column; gap: 6px; }
.alert-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  border: 1px solid var(--gray-100);
  transition: all var(--duration-fast) var(--ease-out);
  position: relative; overflow: hidden;
}
.alert-item:hover { background: var(--gray-50); transform: translateX(2px); }
.alert-high { border-left: 3px solid #dc2626; }
.alert-mid  { border-left: 3px solid #e8a317; }
.alert-low  { border-left: 3px solid #2e7d32; }
.ai-dot {
  width: 8px; height: 8px; border-radius: 50%; margin-top: 5px; flex-shrink: 0;
}
.alert-high .ai-dot { background: #dc2626; box-shadow: 0 0 0 0 rgba(220,38,38,0.5); animation: alertPulse 1.8s infinite; }
.alert-mid .ai-dot { background: #e8a317; }
.alert-low .ai-dot { background: #2e7d32; }
@keyframes alertPulse {
  0%   { box-shadow: 0 0 0 0 rgba(220,38,38,0.5); }
  70%  { box-shadow: 0 0 0 8px rgba(220,38,38,0); }
  100% { box-shadow: 0 0 0 0 rgba(220,38,38,0); }
}
.ai-body { flex: 1; }
.ai-title { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.ai-desc { font-size: 11px; color: var(--text-tertiary); margin-top: 2px; line-height: 1.5; }
.ai-meta { text-align: right; flex-shrink: 0; }
.ai-time { font-size: 10px; color: var(--text-tertiary); margin-bottom: 4px; }
.ai-level-tag {
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  font-size: 10px; font-weight: 600;
}
.tag-high { background: #fee2e2; color: #b91c1c; }
.tag-mid { background: #fef3c7; color: #92400e; }
.tag-low { background: #dcfce7; color: #15803d; }
.alert-badge { background: #fee2e2; color: #b91c1c; }

/* ---- 农事指南 ---- */
.guide-box { padding: 20px; }
.guide-badge { background: #dcfce7; color: #15803d; }
.guide-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.guide-item {
  padding: 14px; border-radius: 10px;
  border: 1px solid var(--gray-100); border-left: 3px solid var(--brand-600);
  transition: all var(--duration-fast);
}
.guide-item:hover { background: var(--gray-50); transform: translateY(-1px); }
.gi-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.gi-icon { font-size: 18px; }
.gi-title { font-size: 13px; font-weight: 700; color: var(--text-primary); }
.gi-desc { font-size: 11px; color: var(--text-tertiary); line-height: 1.6; margin-bottom: 8px; }
.gi-tags { display: flex; gap: 6px; }
.gi-tag {
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  font-size: 10px; font-weight: 600; background: var(--gray-100); color: var(--text-secondary);
}
.gi-tag-time { background: #ede9fe; color: #6d28d9; }

/* ---- 防治效果 ---- */
.effect-box { padding: 20px; }
.effect-badge { background: #dbeafe; color: #1d4ed8; }
.effect-grid { display: flex; flex-direction: column; gap: 10px; }
.effect-item {
  padding: 12px 14px; border-radius: 10px;
  border: 1px solid var(--gray-100); transition: all var(--duration-fast);
}
.effect-item:hover { background: var(--gray-50); }
.ei-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.ei-name { font-size: 13px; font-weight: 700; color: var(--text-primary); }
.ei-rate { font-size: 18px; font-weight: 800; }
.ei-bar-bg { height: 6px; background: var(--gray-100); border-radius: 3px; overflow: hidden; margin-bottom: 6px; }
.ei-bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease; }
.ei-foot { display: flex; justify-content: space-between; font-size: 10px; color: var(--text-tertiary); }

/* ---- 快捷操作 (2x2网格) ---- */
.quick-box { padding: 20px; }
.qa-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.qa-item2 {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 14px 10px; border-radius: 10px; cursor: pointer;
  border: 1px solid var(--gray-100);
  transition: all var(--duration-fast) var(--ease-out);
}
.qa-item2:hover { background: var(--gray-50); border-color: var(--brand-200); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.qa-item2:active { transform: translateY(0) scale(0.97); }
.qa-icon {
  width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;
  border-radius: 12px; transition: transform var(--duration-normal) var(--ease-spring);
}
.qa-item2:hover .qa-icon { transform: scale(1.1) rotate(-5deg); }
.qa-icon-green  { background: #dcfce7; color: #15803d; }
.qa-icon-amber  { background: #fef3c7; color: #b45309; }
.qa-icon-blue   { background: #dbeafe; color: #1d4ed8; }
.qa-icon-purple { background: #ede9fe; color: #6d28d9; }
.qa-lbl { font-size: 12px; font-weight: 600; color: var(--text-primary); }

/* ---- 农资价格 ---- */
.price-box { padding: 20px; }
.price-badge { background: #fef3c7; color: #92400e; }
.price-list { display: flex; flex-direction: column; gap: 6px; }
.price-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 10px; border-radius: 8px;
  border: 1px solid var(--gray-100); transition: all var(--duration-fast);
}
.price-item:hover { background: var(--gray-50); }
.pi-left { display: flex; align-items: baseline; gap: 8px; }
.pi-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.pi-spec { font-size: 10px; color: var(--text-tertiary); }
.pi-right { display: flex; align-items: baseline; gap: 8px; }
.pi-price { font-size: 14px; font-weight: 700; color: var(--text-primary); }
.pi-change { font-size: 11px; font-weight: 600; }
.pi-up { color: #dc2626; }
.pi-down { color: #15803d; }

/* ---- 系统动态 ---- */
.news-box { padding: 20px; }
.news-list { display: flex; flex-direction: column; gap: 6px; }
.news-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 8px 0; border-bottom: 1px solid var(--gray-50);
}
.news-item:last-child { border-bottom: none; }
.ni-dot { width: 6px; height: 6px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.ni-update { background: #2e7d32; }
.ni-model { background: #1976d2; }
.ni-system { background: #6b7280; }
.ni-body { flex: 1; }
.ni-title { font-size: 12px; color: var(--text-primary); font-weight: 500; }
.ni-time { font-size: 10px; color: var(--text-tertiary); margin-top: 2px; }

/* ---- 底部技术栏 ---- */
.tech-bar {
  display: flex; align-items: center; padding: 14px 20px; gap: 16px;
  background: var(--bg-card); border-radius: var(--radius-lg);
  margin-top: 14px; border: 1px solid var(--gray-200);
}
.tb-label {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; color: var(--text-tertiary);
  letter-spacing: 1px; text-transform: uppercase;
  padding-right: 14px; border-right: 1px solid var(--gray-200);
  white-space: nowrap;
}
.tb-label-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--brand-500);
  box-shadow: 0 0 6px rgba(76,175,80,0.5);
  animation: pulse-dot 2s infinite;
}
.tb-items { flex: 1; display: flex; align-items: center; gap: 6px; }
.tb-item { flex: 1; display: flex; align-items: center; gap: 8px; transition: transform var(--duration-fast); }
.tb-item:hover { transform: translateY(-1px); }
.tb-icon { font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 6px; white-space: nowrap; }
.tb-icon-green  { background: #dcfce7; color: #15803d; }
.tb-icon-amber  { background: #fef3c7; color: #b45309; }
.tb-icon-blue   { background: #dbeafe; color: #1d4ed8; }
.tb-icon-purple { background: #ede9fe; color: #6d28d9; }
.tb-icon-teal   { background: #ccfbf1; color: #0f766e; }
.tb-icon-cyan   { background: #cffafe; color: #0e7490; }
.tb-v { font-size: 12px; font-weight: 600; color: var(--text-primary); white-space: nowrap; }
.tb-l { font-size: 10px; color: var(--text-tertiary); white-space: nowrap; }
.tb-divider { width: 1px; height: 28px; background: var(--gray-200); }

@media (max-width: 1100px) {
  .metrics-grid { grid-template-columns: repeat(3, 1fr); }
  .row-3col { grid-template-columns: 1fr; }
}
@media (max-width: 800px) {
  .row-2col { grid-template-columns: 1fr; }
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .guide-grid { grid-template-columns: 1fr; }
}
</style>
