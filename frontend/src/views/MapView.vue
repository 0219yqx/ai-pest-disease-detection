<template>
  <div class="page-wrapper map-page">
    <!-- ============ 顶部标题栏 ============ -->
    <div class="dashboard-header">
      <div class="dh-left">
        <div class="dh-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            <path d="M11 8v3l2 2"/>
          </svg>
        </div>
        <div>
          <h1>河南省农作物病情监测指挥中心</h1>
          <p>数据来源：全国农技中心 · 病虫害测报处 · 18地市实时监测</p>
        </div>
      </div>
      <div class="dh-right">
        <div class="dh-clock">
          <span class="dh-time">{{ currentTime }}</span>
          <span class="dh-date">{{ currentDate }}</span>
        </div>
        <div class="dh-status online">
          <span class="dh-dot-pulse"></span> 系统运行中
        </div>
      </div>
    </div>

    <!-- ============ 核心 KPI 指标卡 ============ -->
    <div class="kpi-row animate-fade-in">
      <div class="kpi-card kpi-red card-ribbon">
        <div class="kpi-icon-wrap"><span class="kpi-icon">&#9888;</span></div>
        <div class="kpi-body">
          <div class="kpi-val">{{ highCount }}</div>
          <div class="kpi-label">高风险区县</div>
        </div>
        <div class="sparkline" aria-hidden="true">
          <span class="sl-bar" v-for="(h,i) in [40,55,48,65,72,60,highCount*12]" :key="i" :class="{peak: h>=70}" :style="{height: h+'%'}"></span>
        </div>
        <div class="kpi-trend up">▲ {{ highPct }}%</div>
      </div>
      <div class="kpi-card kpi-amber card-ribbon" style="animation-delay:60ms">
        <div class="kpi-icon-wrap"><span class="kpi-icon">&#9673;</span></div>
        <div class="kpi-body">
          <div class="kpi-val">{{ midCount }}</div>
          <div class="kpi-label">中风险区县</div>
        </div>
        <div class="sparkline" aria-hidden="true">
          <span class="sl-bar" v-for="(h,i) in [50,45,52,48,40,44,midCount*12]" :key="i" :class="{peak: h>=52}" :style="{height: h+'%'}"></span>
        </div>
        <div class="kpi-trend down">▼ {{ midPct }}%</div>
      </div>
      <div class="kpi-card kpi-green card-ribbon" style="animation-delay:120ms">
        <div class="kpi-icon-wrap"><span class="kpi-icon">&#10003;</span></div>
        <div class="kpi-body">
          <div class="kpi-val">{{ lowCount }}</div>
          <div class="kpi-label">低风险区县</div>
        </div>
        <div class="sparkline" aria-hidden="true">
          <span class="sl-bar" v-for="(h,i) in [30,35,28,32,38,34,lowCount*12]" :key="i" :style="{height: h+'%'}"></span>
        </div>
        <div class="kpi-trend steady">→ 持平</div>
      </div>
      <div class="kpi-card kpi-blue card-ribbon" style="animation-delay:180ms">
        <div class="kpi-icon-wrap"><span class="kpi-icon">&#9733;</span></div>
        <div class="kpi-body">
          <div class="kpi-val">{{ totalArea }}</div>
          <div class="kpi-label">监测面积（万亩）</div>
        </div>
        <div class="sparkline" aria-hidden="true">
          <span class="sl-bar" v-for="(h,i) in [55,60,58,65,70,72,75]" :key="i" :class="{peak: h>=75}" :style="{height: h+'%'}"></span>
        </div>
        <div class="kpi-trend up">▲ +8%</div>
      </div>
      <div class="kpi-card kpi-teal card-ribbon" style="animation-delay:240ms">
        <div class="kpi-icon-wrap"><span class="kpi-icon">&#9883;</span></div>
        <div class="kpi-body">
          <div class="kpi-val">{{ majorPests.length || fallbackMajorPests.length }}</div>
          <div class="kpi-label">重大病虫害</div>
        </div>
        <div class="sparkline" aria-hidden="true">
          <span class="sl-bar" v-for="(h,i) in [20,35,28,40,50,55,48]" :key="i" :class="{peak: h>=55}" :style="{height: h+'%'}"></span>
        </div>
        <div class="kpi-trend">全国农技中心数据</div>
      </div>
    </div>

    <!-- ============ 主内容：地图 + 侧面板 ============ -->
    <div class="main-grid">
      <!-- 左侧：河南地图 -->
      <div class="map-panel card animate-fade-in" style="animation-delay:100ms">
        <div class="panel-header">
          <span class="panel-title">🌍 河南省病情热力地图</span>
          <div class="panel-tools">
            <div class="map-legend-inline">
              <span class="mli-item"><span class="mli-dot" style="background:var(--color-cotton)"></span>高风险</span>
              <span class="mli-item"><span class="mli-dot" style="background:var(--color-wheat)"></span>中风险</span>
              <span class="mli-item"><span class="mli-dot" style="background:var(--color-rice)"></span>低风险</span>
            </div>
          </div>
        </div>
        <div class="map-wrap" :class="{ 'map-loading': mapLoading }">
          <div v-if="mapLoading" class="map-loader">
            <div class="map-loader-spin"></div>
            <span>地图加载中...</span>
          </div>
          <div id="amapContainer" ref="amapContainer" style="height:520px;width:100%"></div>
        </div>
        <!-- 地图下方作物筛选 -->
        <div class="crop-filters">
          <button
            v-for="c in cropFilterList"
            :key="c.key"
            class="cf-btn"
            :class="{ active: activeCrop === c.key }"
            @click="filterCrop(c.key)"
          >
            <span class="cf-dot" :style="{background: c.color}"></span>
            {{ c.label }}
          </button>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="side-panels">
        <!-- 实时预警 -->
        <div class="card sp-card animate-fade-in" style="animation-delay:160ms">
          <div class="panel-header">
            <span class="panel-title">⚠ 实时预警</span>
            <span class="panel-badge badge-red">{{ displayAlerts.length }} 条</span>
          </div>
          <div class="alert-list">
            <div
              v-for="(a, idx) in displayAlerts"
              :key="a.id"
              class="alert-item"
              :class="'alert-' + a.level"
              :style="{ animationDelay: idx * 60 + 'ms' }"
              @click="activeCrop = a.crop"
            >
              <div class="al-icon">
                <svg v-if="a.level==='high'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01"/></svg>
              </div>
              <div class="al-body">
                <div class="al-title">{{ a.title }}</div>
                <div class="al-desc">{{ a.desc }}</div>
                <div class="al-tags">
                  <span class="al-crop-tag" :style="{background: cropColor(a.crop)+'18', color: cropColor(a.crop)}">{{ a.crop }}</span>
                  <span class="al-drug-tag">{{ a.drug }}</span>
                  <span class="al-time-tag">{{ a.time }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 重大病虫害列表 -->
        <div class="card sp-card animate-fade-in" style="animation-delay:220ms">
          <div class="panel-header">
            <span class="panel-title">📊 重大病虫害概览</span>
            <span class="panel-badge">全国农技中心</span>
          </div>
          <div class="pest-mini-list">
            <div v-for="p in displayMajorPests" :key="p.name" class="pml-item">
              <div class="pml-head">
                <span class="pml-dot" :style="{background: cropColor(p.crop)}"></span>
                <span class="pml-name">{{ p.name }}</span>
                <span class="pml-sev" :class="'sev-' + p.severity.charAt(0)">{{ p.severity }}</span>
              </div>
              <div class="pml-meta">{{ p.risk_zone }} · {{ p.crop }}</div>
              <div class="pml-bar-wrap">
                <div class="pml-bar" :style="{width: p.area_ratio + '%', background: severityGrad(p.severity)}"></div>
                <span class="pml-num">{{ p.area_desc }}</span>
              </div>
              <div class="pml-trend">
                <span class="delta" :class="p.trend_dir === 'up' ? 'delta-up' : p.trend_dir === 'down' ? 'delta-down' : 'delta-flat'">
                  {{ p.trend_dir === 'up' ? '↑' : p.trend_dir === 'down' ? '↓' : '→' }} {{ p.trend_text }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ 底部：三列数据面板 ============ -->
    <div class="bottom-grid">
      <!-- 月度趋势 -->
      <div class="card animate-fade-in" style="animation-delay:300ms">
        <div class="panel-header">
          <span class="panel-title">📈 月度发生趋势</span>
          <div class="trend-crop-tabs">
            <button
              v-for="t in trendCrops"
              :key="t"
              class="tct-btn"
              :class="{active: trendCrop === t}"
              @click="trendCrop = t"
            >{{ t }}</button>
          </div>
        </div>
        <v-chart :option="monthlyTrendOpt" style="height:220px;width:100%" autoresize />
        <div class="workflow-strip">
          <div class="wf-step">
            <span class="wf-label">当前判断</span>
            <strong>{{ monthlyWorkflow.level }}</strong>
          </div>
          <div class="wf-step">
            <span class="wf-label">高发窗口</span>
            <strong>{{ monthlyWorkflow.window }}</strong>
          </div>
          <div class="wf-step">
            <span class="wf-label">处置动作</span>
            <strong>{{ monthlyWorkflow.action }}</strong>
          </div>
        </div>
      </div>

      <!-- 周度监测 -->
      <div class="card animate-fade-in" style="animation-delay:360ms">
        <div class="panel-header">
          <span class="panel-title">📉 周度监测趋势（4-8月）</span>
        </div>
        <v-chart :option="weeklyTrendOpt" style="height:220px;width:100%" autoresize />
        <div class="workflow-strip">
          <div class="wf-step">
            <span class="wf-label">升高最快</span>
            <strong>{{ weeklyWorkflow.crop }}</strong>
          </div>
          <div class="wf-step">
            <span class="wf-label">本周风险</span>
            <strong>{{ weeklyWorkflow.level }}</strong>
          </div>
          <div class="wf-step">
            <span class="wf-label">巡检建议</span>
            <strong>{{ weeklyWorkflow.action }}</strong>
          </div>
        </div>
      </div>

      <!-- 病虫害分布饼图 -->
      <div class="card animate-fade-in" style="animation-delay:420ms">
        <div class="panel-header">
          <span class="panel-title">📊 病虫害类型分布</span>
        </div>
        <v-chart :option="pestPieOpt" style="height:220px;width:100%" autoresize />
        <div class="workflow-strip">
          <div class="wf-step">
            <span class="wf-label">主导类型</span>
            <strong>{{ typeWorkflow.primary }}</strong>
          </div>
          <div class="wf-step">
            <span class="wf-label">占比</span>
            <strong>{{ typeWorkflow.share }}%</strong>
          </div>
          <div class="wf-step">
            <span class="wf-label">复核重点</span>
            <strong>{{ typeWorkflow.action }}</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ 底部信息仪表盘 ============ -->
    <div class="info-dashboard animate-fade-in" style="animation-delay:480ms">
      <div class="id-row">
        <div class="id-item">
          <div class="id-icon-wrap id-ic-blue">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <div class="id-body">
            <div class="id-val">{{ lastUpdateTime }}</div>
            <div class="id-lbl">数据更新时间</div>
          </div>
        </div>
        <div class="id-divider"></div>
        <div class="id-item">
          <div class="id-icon-wrap id-ic-green">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <div class="id-body">
            <div class="id-val">全国农技中心 · 病虫害测报处</div>
            <div class="id-lbl">权威数据源</div>
          </div>
        </div>
        <div class="id-divider"></div>
        <div class="id-item">
          <div class="id-icon-wrap id-ic-teal">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
          </div>
          <div class="id-body">
            <div class="id-val">18 个地市全覆盖</div>
            <div class="id-lbl">监测范围</div>
          </div>
        </div>
        <div class="id-divider"></div>
        <div class="id-item">
          <div class="id-icon-wrap id-ic-purple">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
          </div>
          <div class="id-body">
            <div class="id-val">河南省农业农村厅指导</div>
            <div class="id-lbl">数据背书</div>
          </div>
        </div>
        <div class="id-divider"></div>
        <div class="id-item">
          <div class="id-icon-wrap id-ic-amber">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/></svg>
          </div>
          <div class="id-body">
            <div class="id-val">{{ uniqueCrops.length }} 种作物 · {{ pestTotalCount }} 条记录</div>
            <div class="id-lbl">知识库覆盖</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { PEST_KNOWLEDGE, CROP_COLOR_MAP } from '../data/knowledgeData.js'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent, MarkLineComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, BarChart, LineChart, PieChart, TooltipComponent, LegendComponent, GridComponent, MarkLineComponent])

const router = useRouter()

// ==================== 从知识库派生的全局数据 ====================
const uniqueCrops = computed(() => [...new Set(PEST_KNOWLEDGE.map(p => p.crop))])
const pestTotalCount = computed(() => PEST_KNOWLEDGE.length)

// ==================== 响应式状态 ====================
const activeCrop = ref('all')
const trendCrop = ref('小麦')
const mapLoading = ref(false)
const amapContainer = ref(null)

const alerts = ref([])
const majorPests = ref([])
const monthTrend = ref({})
const weekTrend = ref({})

const currentTime = ref('')
const currentDate = ref('')
const lastUpdateTime = ref('')

const updateClock = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
  currentDate.value = now.toLocaleDateString('zh-CN', { year:'numeric', month:'long', day:'numeric', weekday:'long' })
  lastUpdateTime.value = now.toLocaleString('zh-CN', { month:'numeric', day:'numeric', hour:'2-digit', minute:'2-digit' })
}
updateClock()
let clockTimer = setInterval(updateClock, 1000)

onBeforeUnmount(() => {
  clearInterval(clockTimer)
})

// ==================== 城市坐标和本地监测数据 ====================
const cityPositions = {
  '郑州市': [113.62, 34.75], '开封市': [114.31, 34.80], '洛阳市': [112.45, 34.62],
  '新乡市': [113.85, 35.30], '许昌市': [113.83, 34.02], '周口市': [114.65, 33.62],
  '驻马店市': [114.02, 32.98], '南阳市': [112.53, 33.00], '商丘市': [115.66, 34.41],
  '平顶山市': [113.29, 33.75], '安阳市': [114.39, 36.10], '信阳市': [114.08, 32.13],
  '焦作市': [113.24, 35.22], '濮阳市': [114.99, 35.76], '漯河市': [113.98, 33.58],
  '三门峡市': [111.20, 34.77], '鹤壁市': [114.30, 35.90], '济源市': [112.58, 35.07],
}

// 18 地市真实监测数据（基于知识库的 13 种作物）
const cityData = reactive([
  { name:'信阳市',   pest:'水稻稻瘟病',   severity:'高', crop:'水稻', area:3.8, freq:24 },
  { name:'新乡市',   pest:'小麦条锈病',   severity:'高', crop:'小麦', area:3.5, freq:22 },
  { name:'周口市',   pest:'玉米叶斑病',   severity:'高', crop:'玉米', area:4.2, freq:28 },
  { name:'驻马店市', pest:'小麦条锈病',   severity:'高', crop:'小麦', area:3.0, freq:18 },
  { name:'南阳市',   pest:'水稻褐斑病',   severity:'中', crop:'水稻', area:2.1, freq:15 },
  { name:'平顶山市', pest:'番茄晚疫病',   severity:'中', crop:'番茄', area:1.5, freq:12 },
  { name:'许昌市',   pest:'玉米灰斑病',   severity:'中', crop:'玉米', area:1.4, freq:11 },
  { name:'漯河市',   pest:'小麦赤霉病',   severity:'中', crop:'小麦', area:1.8, freq:11 },
  { name:'焦作市',   pest:'小麦赤霉病',   severity:'中', crop:'小麦', area:1.1, freq:9  },
  { name:'开封市',   pest:'大豆蚜虫',     severity:'中', crop:'大豆', area:1.6, freq:10 },
  { name:'安阳市',   pest:'小麦白粉病',   severity:'中', crop:'小麦', area:0.9, freq:7  },
  { name:'商丘市',   pest:'玉米锈病',     severity:'中', crop:'玉米', area:1.2, freq:8  },
  { name:'濮阳市',   pest:'棉铃虫',       severity:'中', crop:'棉花', area:1.3, freq:8  },
  { name:'洛阳市',   pest:'葡萄霜霉病',   severity:'低', crop:'葡萄', area:0.5, freq:4  },
  { name:'郑州市',   pest:'草莓早疫病',   severity:'低', crop:'草莓', area:0.4, freq:4  },
  { name:'三门峡市', pest:'苹果赤霉病',   severity:'低', crop:'苹果', area:0.3, freq:3  },
  { name:'鹤壁市',   pest:'黄瓜白粉病',   severity:'低', crop:'黄瓜', area:0.3, freq:3  },
  { name:'济源市',   pest:'柑橘疮痂病',   severity:'低', crop:'柑橘', area:0.2, freq:2  },
])

// ==================== 颜色映射（统一用 CROP_COLOR_MAP） ====================
const cropColor = (c) => CROP_COLOR_MAP[c] || '#6b7280'

// ECharts 用 Canvas 渲染，无法识别 CSS 变量，这里集中维护 hex 色板
const HEX = {
  rice:   '#2e7d32', wheat: '#e8a317', corn: '#1976d2', cotton: '#c62828',
  brand:  '#4caf50', brand700: '#388e3c', brand200: '#a5d6a7',
  text3:  '#9ca3b4', gray100: '#f1f3f7', gray200: '#e5e8ef',
  danger: '#ef4444', warn: '#f59e0b', success: '#22c55e',
}
// hex + alpha → rgba 字符串（用于渐变填充）
const rgba = (hex, a) => {
  const h = hex.replace('#','')
  const r = parseInt(h.slice(0,2),16), g = parseInt(h.slice(2,4),16), b = parseInt(h.slice(4,6),16)
  return `rgba(${r},${g},${b},${a})`
}

const severityGrad = (s) => {
  if (s.startsWith('重')) return 'linear-gradient(90deg, var(--color-cotton), #ef4444)'
  if (s.startsWith('中')) return 'linear-gradient(90deg, var(--color-wheat), #f59e0b)'
  return 'linear-gradient(90deg, var(--color-rice), #22c55e)'
}

// ==================== 作物筛选按钮 ====================
const cropFilterList = computed(() => {
  const crops = [...new Set(PEST_KNOWLEDGE.map(p => p.crop))].sort()
  return [
    { key: 'all', label: '全部作物', color: '#6b7280' },
    ...crops.map(c => ({ key: c, label: c, color: CROP_COLOR_MAP[c] || '#888' })),
  ]
})

const filterCrop = (key) => { activeCrop.value = key }

const filteredCities = computed(() => {
  if (activeCrop.value === 'all') return cityData
  return cityData.filter(c => c.crop === activeCrop.value)
})

const highCount = computed(() => filteredCities.value.filter(c => c.severity === '高').length)
const midCount = computed(() => filteredCities.value.filter(c => c.severity === '中').length)
const lowCount = computed(() => filteredCities.value.filter(c => c.severity === '低').length)
const highPct = computed(() => Math.round(highCount.value / 18 * 100))
const midPct = computed(() => Math.round(midCount.value / 18 * 100))
const totalArea = computed(() => filteredCities.value.reduce((s, c) => s + c.area, 0).toFixed(1))

// ==================== Fallback 数据 ====================
const fallbackAlerts = [
  { id:1, title:'信阳稻瘟病高风险预警', desc:'信阳地区稻瘟病发病率上升至42%，建议立即喷施三环唑。', level:'high', crop:'水稻', drug:'三环唑', time:'10分钟前' },
  { id:2, title:'新乡小麦条锈病紧急预警', desc:'新乡麦区条锈病大面积扩散，百株发病率达35%。', level:'high', crop:'小麦', drug:'三唑酮', time:'30分钟前' },
  { id:3, title:'周口玉米叶斑病扩散', desc:'周口玉米叶斑病发生面积达4.2万亩，高温高湿条件利于流行。', level:'high', crop:'玉米', drug:'苯醚甲环唑', time:'1小时前' },
  { id:4, title:'驻马店小麦赤霉病监测', desc:'驻马店小麦赤霉病零星发生，需持续关注天气变化。', level:'mid', crop:'小麦', drug:'戊唑醇', time:'2小时前' },
  { id:5, title:'南阳水稻褐斑病提示', desc:'南阳稻区褐斑病发生面积扩大，建议加强田间管理。', level:'mid', crop:'水稻', drug:'噻呋酰胺', time:'3小时前' },
  { id:6, title:'平顶山番茄晚疫病预警', desc:'近期降雨偏多，番茄晚疫病有流行风险，注意通风降湿。', level:'mid', crop:'番茄', drug:'烯酰吗啉', time:'4小时前' },
  { id:7, title:'许昌玉米灰斑病提示', desc:'灰斑病在许昌部分区域发生，建议适时防治。', level:'mid', crop:'玉米', drug:'戊唑醇', time:'5小时前' },
  { id:8, title:'安阳小麦白粉病关注', desc:'安阳麦区白粉病处于低发状态，持续监测中。', level:'low', crop:'小麦', drug:'烯唑醇', time:'6小时前' },
  { id:9, title:'濮阳棉铃虫发生动态', desc:'二代棉铃虫已进入卵孵高峰期，注意防治适期。', level:'mid', crop:'棉花', drug:'氯虫苯甲酰胺', time:'昨天' },
  { id:10, title:'开封大豆蚜虫提示', desc:'大豆田蚜虫密度上升，百株蚜量达200头。', level:'low', crop:'大豆', drug:'吡虫啉', time:'昨天' },
]

const fallbackMajorPests = [
  { name:'小麦条锈病', crop:'小麦', severity:'偏重', risk_zone:'豫南·信阳驻马店', area_ratio:85, area_desc:'年发生面积2.1亿亩', trend_dir:'up', trend_text:'较上年增加12%' },
  { name:'小麦赤霉病', crop:'小麦', severity:'偏重', risk_zone:'豫中·周口漯河', area_ratio:78, area_desc:'年发生面积1.8亿亩', trend_dir:'up', trend_text:'较上年增加8%' },
  { name:'稻瘟病', crop:'水稻', severity:'中等偏重', risk_zone:'豫南·信阳南阳', area_ratio:72, area_desc:'年发生面积0.9亿亩', trend_dir:'steady', trend_text:'与上年持平' },
  { name:'玉米叶斑病', crop:'玉米', severity:'中等', risk_zone:'豫东·周口商丘', area_ratio:60, area_desc:'年发生面积1.2亿亩', trend_dir:'down', trend_text:'较上年下降5%' },
  { name:'棉铃虫', crop:'棉花', severity:'中等', risk_zone:'豫北·濮阳安阳', area_ratio:55, area_desc:'年发生面积0.5亿亩', trend_dir:'steady', trend_text:'与上年持平' },
  { name:'番茄晚疫病', crop:'番茄', severity:'中等', risk_zone:'全省设施大棚', area_ratio:42, area_desc:'年发生面积0.15亿亩', trend_dir:'up', trend_text:'较上年增加15%' },
  { name:'小麦白粉病', crop:'小麦', severity:'中等', risk_zone:'豫北·新乡安阳', area_ratio:50, area_desc:'年发生面积1.0亿亩', trend_dir:'down', trend_text:'较上年下降3%' },
  { name:'大豆蚜虫', crop:'大豆', severity:'中等', risk_zone:'豫东·开封商丘', area_ratio:35, area_desc:'年发生面积0.3亿亩', trend_dir:'steady', trend_text:'与上年持平' },
]

const fallbackMonthTrend = {
  '小麦': [1,2,8,35,62,28,5,2,1,1,1,1],
  '玉米': [1,1,2,5,12,45,58,52,20,5,2,1],
  '水稻': [1,1,2,4,8,18,42,55,38,12,3,1],
  '番茄': [2,3,5,12,25,35,42,38,28,15,5,2],
  '棉花': [1,1,1,3,8,20,38,45,30,12,4,1],
}

const fallbackWeekTrend = {
  '水稻': [2,5,8,12,18,25,32,38,35,28],
  '小麦': [15,22,30,42,55,48,35,20,12,8],
  '玉米': [3,5,8,12,18,25,30,35,32,28],
  '棉花': [1,2,4,6,10,14,18,22,20,16],
}

const displayAlerts = computed(() => alerts.value.length > 0 ? alerts.value : fallbackAlerts)
const displayMajorPests = computed(() => majorPests.value.length > 0 ? majorPests.value : fallbackMajorPests)

// ==================== ECharts 图表配置 ====================
const trendCrops = ['小麦', '玉米', '水稻', '番茄', '棉花']

const monthNames = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
const monthlyWorkflow = computed(() => {
  const vals = monthTrend.value.values?.length
    ? monthTrend.value.values
    : (fallbackMonthTrend[trendCrop.value] || fallbackMonthTrend['小麦'])
  const maxVal = Math.max(...vals)
  const peakIndex = vals.indexOf(maxVal)
  const currentVal = vals[new Date().getMonth()] || vals[peakIndex] || 0
  const level = currentVal >= 50 ? '高发期' : currentVal >= 20 ? '上升期' : '平稳期'
  const action = currentVal >= 50 ? '立即复核告警' : currentVal >= 20 ? '加密巡检' : '保持监测'
  return {
    level,
    window: `${monthNames[Math.max(0, peakIndex - 1)]}-${monthNames[Math.min(11, peakIndex + 1)]}`,
    action,
  }
})

const weeklyWorkflow = computed(() => {
  const crops = ['水稻', '小麦', '玉米', '棉花']
  const rows = crops.map((crop) => {
    const data = weekTrend.value[crop] || fallbackWeekTrend[crop] || []
    const last = data[data.length - 1] || 0
    const previous = data[data.length - 2] || 0
    return { crop, last, delta: last - previous }
  }).sort((a, b) => b.delta - a.delta)
  const top = rows[0] || { crop: '--', last: 0, delta: 0 }
  return {
    crop: `${top.crop} ${top.delta >= 0 ? '+' : ''}${top.delta}`,
    level: top.last >= 35 ? '偏高' : top.last >= 18 ? '中等' : '平稳',
    action: top.last >= 35 ? '48小时内巡检' : top.last >= 18 ? '本周抽检' : '常规巡查',
  }
})

const monthlyTrendOpt = computed(() => {
  const vals = monthTrend.value.values?.length
    ? monthTrend.value.values
    : (fallbackMonthTrend[trendCrop.value] || fallbackMonthTrend['小麦'])
  const maxVal = Math.max(...vals, 10)
  const curMonth = new Date().getMonth() // 0-indexed
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.97)',
      borderColor: HEX.gray200, borderWidth: 1,
      borderRadius: 10,
      textStyle: { color:'#111827', fontSize:12 },
      padding: [10, 14],
      extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.08);',
      formatter: (params) => {
        const v = params[0].value
        const lvl = v >= 50 ? '🔴 高发期' : v >= 20 ? '🟡 中发期' : '🟢 低发期'
        return `<b>${params[0].axisValue}</b><br/>发生率：${v}%  ${lvl}`
      },
    },
    grid: { left:36, right:14, top:20, bottom:26 },
    xAxis: {
      type:'category',
      data: ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'],
      axisLine:{show:false}, axisTick:{show:false},
      axisLabel:{color: HEX.text3, fontSize:10},
    },
    yAxis: {
      type:'value', max: Math.ceil(maxVal/10)*10 + 10,
      splitLine:{lineStyle:{color:'#f3f4f6', type:'dashed'}},
      axisLabel:{color: HEX.text3, fontSize:10},
    },
    series: [{
      type:'bar',
      barMaxWidth: 18,
      borderRadius:[4,4,0,0],
      data: vals.map((v) => {
        const level = v >= 50 ? 0 : v >= 20 ? 1 : 2
        const cs = [[HEX.cotton, HEX.danger], [HEX.wheat, HEX.warn], [HEX.rice, HEX.success]]
        return { value: v, itemStyle: { color: { type:'linear',x:0,y:0,x2:0,y2:1, colorStops:[{offset:0,color:cs[level][0]},{offset:1,color:cs[level][1]}] }} }
      }),
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: HEX.brand, type: 'dashed', width: 1.5 },
        data: [{ xAxis: curMonth }],
        label: { show: true, formatter: '当月', color: HEX.brand700, fontSize: 10, position: 'start' },
      },
    }],
  }
})

const weeklyTrendOpt = computed(() => {
  const hasData = weekTrend.value && Object.keys(weekTrend.value).length > 0
  const crops = ['水稻', '小麦', '玉米', '棉花']
  const palette = {
    '水稻': HEX.rice, '小麦': HEX.wheat,
    '玉米': HEX.corn, '棉花': HEX.cotton,
  }
  const doSeries = (name) => {
    const data = hasData && weekTrend.value[name] ? weekTrend.value[name] : (fallbackWeekTrend[name] || [0,0,0,0,0,0,0,0,0,0])
    const c = palette[name]
    return {
      name, type:'line', smooth:true, symbol:'circle', symbolSize:5, data,
      lineStyle:{width:2.5, color:c},
      itemStyle:{color:c, borderWidth:2, borderColor:'#fff'},
      areaStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,
        colorStops:[{offset:0,color: rgba(c,0.22)}, {offset:1,color:'rgba(0,0,0,0)'}]}},
    }
  }
  return {
    tooltip: {
      trigger:'axis',
      backgroundColor:'rgba(255,255,255,0.97)',
      borderColor: HEX.gray200, borderWidth:1, borderRadius:10,
      textStyle:{color:'#111827', fontSize:12},
      padding:[10,14],
      extraCssText:'box-shadow: 0 4px 12px rgba(0,0,0,0.08);',
    },
    legend: {
      data: crops, bottom:0, icon:'roundRect', itemWidth:14, itemHeight:6,
      textStyle:{color: HEX.text3, fontSize:10},
      itemGap:16,
    },
    grid: { left:36, right:14, top:16, bottom:34 },
    xAxis: {
      type:'category',
      data: ['第16周','第18周','第20周','第22周','第24周','第26周','第28周','第30周','第32周','第34周'],
      axisLine:{show:false}, axisTick:{show:false},
      axisLabel:{color: HEX.text3, fontSize:9.5},
      boundaryGap: false,
    },
    yAxis: {
      type:'value', name:'起',
      nameTextStyle:{color: HEX.text3, fontSize:10},
      splitLine:{lineStyle:{color:'#f3f4f6', type:'dashed'}},
      axisLabel:{color: HEX.text3, fontSize:10},
    },
    series: crops.map(doSeries),
  }
})

const pestPieData = [
  {value:42, name:'真菌性病害', itemStyle:{color: HEX.cotton}},
  {value:22, name:'鳞翅目害虫', itemStyle:{color: HEX.wheat}},
  {value:15, name:'刺吸式害虫', itemStyle:{color: HEX.corn}},
  {value:12, name:'细菌性病害', itemStyle:{color: HEX.rice}},
  {value:6,  name:'病毒性病害', itemStyle:{color:'#7c3aed'}},
  {value:3,  name:'线虫病害',   itemStyle:{color:'#0f766e'}},
].sort((a,b) => b.value - a.value)

const typeWorkflow = computed(() => {
  const primary = pestPieData[0] || { name: '--', value: 0 }
  const actionMap = {
    '真菌性病害': '叶片病斑样本',
    '鳞翅目害虫': '幼虫与取食痕迹',
    '刺吸式害虫': '叶背虫口密度',
    '细菌性病害': '水渍状病斑',
    '病毒性病害': '黄化皱缩症状',
    '线虫病害': '根部样本',
  }
  return {
    primary: primary.name,
    share: primary.value,
    action: actionMap[primary.name] || '异常样本',
  }
})

const pestPieOpt = {
  tooltip: {
    trigger:'item',
    backgroundColor:'rgba(255,255,255,0.97)',
    borderColor: HEX.gray200, borderWidth:1, borderRadius:10,
    textStyle:{color:'#111827', fontSize:12},
    formatter: (p) => `${p.marker} ${p.name}：${p.value}%`,
  },
  legend: {
    type: 'scroll',
    orient: 'vertical',
    right: 6, top: 'center',
    itemWidth: 10, itemHeight: 10, itemGap: 8,
    textStyle: { color: HEX.text3, fontSize: 10 },
    formatter: (name) => {
      const item = pestPieData.find(d => d.name === name)
      return `${name}  ${item ? item.value : 0}%`
    },
  },
  series: [{
    type:'pie',
    radius:['42%','70%'],
    center:['32%','50%'],
    itemStyle:{borderRadius:6, borderColor:'#fff', borderWidth:2},
    label: { show: false },
    labelLine: { show: false },
    emphasis: {
      scaleSize: 8,
      itemStyle:{shadowBlur:14, shadowColor:'rgba(0,0,0,0.16)'},
    },
    data: pestPieData,
  }],
}

// ==================== 地图初始化 ====================

// 高德地图标记加载（单独提取为函数，方便降级复用）
function loadMapMarkers(map) {
  const sevConf = { '高': { bg:'#dc2626', size:38, pulse:true }, '中': { bg:'#e8a317', size:30, pulse:false }, '低': { bg:'#16a34a', size:24, pulse:false } }
  const markers = []
  cityData.forEach(c => {
    const pos = cityPositions[c.name]
    if (!pos) return
    const conf = sevConf[c.severity] || sevConf['低']
    const pulseHtml = conf.pulse ? `<div style="position:absolute;width:${conf.size+12}px;height:${conf.size+12}px;border-radius:50%;background:${conf.bg}22;animation:amPulse 2s infinite;top:${-(conf.size+12)/2+conf.size/2}px;left:${-(conf.size+12)/2+conf.size/2}px;"></div>` : ''
    const content = `<div style="position:relative;display:flex;align-items:center;justify-content:center;">
      ${pulseHtml}
      <div style="width:${conf.size}px;height:${conf.size}px;background:${conf.bg};border:3px solid #fff;border-radius:50%;box-shadow:0 2px 12px ${conf.bg}55;cursor:pointer;display:flex;align-items:center;justify-content:center;color:#fff;font-size:${conf.size >= 34 ? 13 : 11}px;font-weight:bold;transition:transform .2s;">${c.freq}</div>
    </div>`
    try {
      const marker = new AMap.Marker({
        position: pos,
        content: content,
        offset: new AMap.Pixel(-conf.size/2, -conf.size/2),
        title: c.name,
      })
      marker.on('click', () => {
        const sevColor = conf.bg
        try {
          const info = new AMap.InfoWindow({
            content: '<div style="padding:14px 16px;min-width:220px;border-radius:12px;font-family:system-ui;">' +
              '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">' +
              '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:' + sevColor + ';box-shadow:0 0 6px ' + sevColor + '55;"></span>' +
              '<span style="font-size:15px;font-weight:700;color:#111827;">' + c.name + '</span>' +
              '<span style="font-size:11px;padding:2px 8px;border-radius:999px;background:' + sevColor + '18;color:' + sevColor + ';font-weight:600;">' + c.severity + '风险</span>' +
              '</div>' +
              '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px;">' +
              '<div style="padding:8px 10px;background:#f8f9fb;border-radius:8px;"><div style="font-size:10px;color:#9ca3af;margin-bottom:2px;">主要病虫害</div><div style="font-size:12px;font-weight:600;color:#111827;">' + c.pest + '</div></div>' +
              '<div style="padding:8px 10px;background:#f8f9fb;border-radius:8px;"><div style="font-size:10px;color:#9ca3af;margin-bottom:2px;">发生面积</div><div style="font-size:12px;font-weight:600;color:#111827;">' + c.area + ' 万亩</div></div>' +
              '<div style="padding:8px 10px;background:#f8f9fb;border-radius:8px;"><div style="font-size:10px;color:#9ca3af;margin-bottom:2px;">所属作物</div><div style="font-size:12px;font-weight:600;color:#111827;">' + c.crop + '</div></div>' +
              '<div style="padding:8px 10px;background:#f8f9fb;border-radius:8px;"><div style="font-size:10px;color:#9ca3af;margin-bottom:2px;">监测频次</div><div style="font-size:12px;font-weight:600;color:#111827;">' + c.freq + ' 次/周</div></div>' +
              '</div></div>',
            offset: new AMap.Pixel(0, -10),
          })
          info.open(map, pos)
        } catch(e) { console.warn('InfoWindow error:', e) }
      })
      markers.push(marker)
      map.add(marker)
    } catch(e) { console.warn('Marker error for', c.name, e) }
  })
  if (markers.length) map.setFitView(markers, false, [60, 60, 60, 60])
  window.hermesMap = map
}

const onMapClick = (params) => {
  if (params.name && cityData.find(c => c.name === params.name)) {
    const city = cityData.find(c => c.name === params.name)
    if (city) activeCrop.value = city.crop
  }
}

// 后端数据加载（与地图并行，失败用 fallback）
const loadBackendData = async () => {
  try {
    const [alertRes, pestRes, trendRes, weekRes] = await Promise.all([
      fetch('/api/history/alerts').then(r => r.json()).catch(() => ({ data: [] })),
      fetch('/api/history/major-pests').then(r => r.json()).catch(() => ({ data: [] })),
      fetch('/api/history/monthly-trend?crop=小麦').then(r => r.json()).catch(() => ({ data: { values: [] } })),
      fetch('/api/history/pest-data').then(r => r.json()).catch(() => ({ data: {} })),
    ])
    if (alertRes.data?.length) alerts.value = alertRes.data
    if (pestRes.data?.length) majorPests.value = pestRes.data
    if (trendRes.data?.values?.length) monthTrend.value = trendRes.data
    const full = weekRes.data || {}
    if (full.weekly_trend_2026) weekTrend.value = full.weekly_trend_2026
  } catch (e) {
    console.warn('后端数据加载失败，使用本地数据', e)
  }
}

// 等待 AMap SDK 加载，带 8 秒超时
const waitAMap = (timeout = 1000) => new Promise((resolve, reject) => {
  if (window.AMap && typeof window.AMap.Map === 'function') return resolve(window.AMap)
  const start = Date.now()
  const check = setInterval(() => {
    if (window.AMap && typeof window.AMap.Map === 'function') {
      clearInterval(check); resolve(window.AMap)
    } else if (Date.now() - start > timeout) {
      clearInterval(check); reject(new Error('AMap SDK 加载超时'))
    }
  }, 100)
})

// 在没有 AMap SDK 时，使用 SVG 渲染简易地图作为兜底
const renderFallbackMap = () => {
  if (!amapContainer.value) return
  // 简易示意图：河南省轮廓 + 城市点（按坐标缩放到容器）
  const minLng = 110.3, maxLng = 116.7, minLat = 31.4, maxLat = 36.6
  const W = 800, H = 520
  const project = (lng, lat) => [
    ((lng - minLng) / (maxLng - minLng)) * (W - 60) + 30,
    H - 30 - ((lat - minLat) / (maxLat - minLat)) * (H - 60),
  ]
  const sevConf = { '高': '#dc2626', '中': '#e8a317', '低': '#16a34a' }
  const sizeConf = { '高': 22, '中': 17, '低': 13 }
  let dots = ''
  cityData.forEach(c => {
    const pos = cityPositions[c.name]
    if (!pos) return
    const [x, y] = project(pos[0], pos[1])
    const color = sevConf[c.severity] || sevConf['低']
    const r = sizeConf[c.severity] || 13
    const pulse = c.severity === '高' ? `<circle cx="${x}" cy="${y}" r="${r+6}" fill="${color}" opacity="0.18"><animate attributeName="r" values="${r+4};${r+12};${r+4}" dur="2.2s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.32;0;0.32" dur="2.2s" repeatCount="indefinite"/></circle>` : ''
    dots += `${pulse}
      <g class="fb-dot" data-city="${c.name}" style="cursor:pointer">
        <circle cx="${x}" cy="${y}" r="${r}" fill="${color}" stroke="#fff" stroke-width="2.5" filter="drop-shadow(0 2px 4px ${color}88)"/>
        <text x="${x}" y="${y+4}" text-anchor="middle" fill="#fff" font-size="${r>=20?11:9}" font-weight="700">${c.freq}</text>
        <text x="${x}" y="${y-r-5}" text-anchor="middle" fill="#374151" font-size="10" font-weight="600">${c.name.replace('市','')}</text>
      </g>`
  })
  amapContainer.value.innerHTML = `
    <div style="position:relative;width:100%;height:520px;background:linear-gradient(135deg,#e8f1e0 0%,#dceadf 50%,#e8e9d8 100%);border-radius:12px;overflow:hidden;">
      <div style="position:absolute;top:12px;left:14px;font-size:11px;color:#6b7280;background:rgba(255,255,255,0.75);padding:4px 10px;border-radius:6px;z-index:2;">📍 河南省病情分布示意图（离线模式）</div>
      <svg viewBox="0 0 ${W} ${H}" style="width:100%;height:100%;" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="prov" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#cfe3c4"/><stop offset="100%" stop-color="#bcd5b0"/>
          </linearGradient>
        </defs>
        <path d="M170,80 L260,55 L380,62 L470,90 L560,85 L640,130 L700,200 L680,290 L720,360 L660,430 L540,470 L420,455 L300,475 L210,420 L130,350 L120,260 L90,170 Z"
          fill="url(#prov)" stroke="#7ba66c" stroke-width="2" stroke-linejoin="round" opacity="0.9"/>
        ${dots}
      </svg>
      <div style="position:absolute;bottom:12px;right:14px;display:flex;gap:12px;font-size:11px;color:#6b7280;background:rgba(255,255,255,0.75);padding:6px 12px;border-radius:6px;">
        <span style="display:flex;align-items:center;gap:4px;"><span style="width:9px;height:9px;border-radius:50%;background:#dc2626;"></span>高</span>
        <span style="display:flex;align-items:center;gap:4px;"><span style="width:9px;height:9px;border-radius:50%;background:#e8a317;"></span>中</span>
        <span style="display:flex;align-items:center;gap:4px;"><span style="width:9px;height:9px;border-radius:50%;background:#16a34a;"></span>低</span>
      </div>
    </div>`
  // 简易点击交互
  amapContainer.value.querySelectorAll('.fb-dot').forEach(g => {
    g.addEventListener('click', () => {
      const name = g.getAttribute('data-city')
      const city = cityData.find(c => c.name === name)
      if (city) activeCrop.value = city.crop
    })
  })
}

onMounted(async () => {
  mapLoading.value = true
  loadBackendData()
  await nextTick()

  // 优先尝试高德地图 API，失败则降级到离线 SVG
  try {
    if (window.AMap && typeof window.AMap.Map === 'function') {
      const map = new AMap.Map(amapContainer.value, {
        zoom: 7.5,
        center: [113.5, 33.8],
        
      })
      // 添加城市标记
      loadMapMarkers(map)
      mapLoading.value = false
      return
    }
  } catch (e) {
    console.warn('高德地图初始化失败，切换到离线SVG:', e)
  }
  // 降级：离线 SVG 示意图
  renderFallbackMap()
  mapLoading.value = false
})
</script>

<style scoped>
/* ============ 页面容器 ============ */
.map-page { gap: 12px; padding-bottom: 24px; }

/* ============ 顶部仪表盘头部 ============ */
.dashboard-header {
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(135deg, #1b3a1b 0%, #2d5a2d 40%, #365314 100%);
  border-radius: var(--radius-xl); padding: 18px 24px; color: #fff;
  box-shadow: 0 4px 20px rgba(22,101,52,0.15);
}
.dh-left { display:flex; align-items:center; gap:14px; }
.dh-icon {
  width:44px; height:44px; border-radius:12px;
  background: rgba(255,255,255,0.15); backdrop-filter:blur(8px);
  display:flex; align-items:center; justify-content:center; color: #86efac;
}
.dh-left h1 { font-size:18px; font-weight:700; margin:0; letter-spacing:1px; }
.dh-left p { font-size:12px; color:rgba(255,255,255,0.7); margin:2px 0 0; }
.dh-right { display:flex; align-items:center; gap:20px; }
.dh-clock { text-align:right; }
.dh-time { font-size:24px; font-weight:700; font-variant-numeric:tabular-nums; display:block; }
.dh-date { font-size:11px; color:rgba(255,255,255,0.65); }
.dh-status {
  display:flex; align-items:center; gap:6px;
  font-size:11px; padding:5px 12px; border-radius:999px;
  background:rgba(255,255,255,0.1);
}
.dh-status.online { color:#86efac; }
.dh-dot-pulse { width:7px; height:7px; border-radius:50%; background:#22c55e; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.3)} }

/* ============ KPI 指标卡 ============ */
.kpi-row { display:grid; grid-template-columns:repeat(5,1fr); gap:12px; }
.kpi-card {
  background: var(--bg-card); border-radius: var(--radius-lg);
  padding: 16px 18px; display:flex; align-items:center; gap:12px;
  border: 1px solid var(--gray-200);
  backdrop-filter: var(--glass-blur);
  transition: all var(--duration-normal) var(--ease-out);
  position: relative; overflow: hidden;
}
.kpi-card:hover { transform:translateY(-3px); box-shadow:var(--shadow-lg); border-color:var(--brand-200); }
.kpi-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:var(--grad-brand); opacity:0; transition:opacity var(--duration-normal);
}
.kpi-card:hover::before { opacity:1; }
.kpi-icon-wrap {
  width:44px; height:44px; border-radius:12px; display:flex;
  align-items:center; justify-content:center; flex-shrink:0;
  transition:transform var(--duration-normal) var(--ease-spring);
}
.kpi-card:hover .kpi-icon-wrap { transform:scale(1.08) rotate(-4deg); }
.kpi-red .kpi-icon-wrap { background:#fee2e2; color:var(--color-cotton); }
.kpi-amber .kpi-icon-wrap { background:#fef3c7; color:var(--color-wheat); }
.kpi-green .kpi-icon-wrap { background:#dcfce7; color:var(--color-rice); }
.kpi-blue .kpi-icon-wrap { background:#dbeafe; color:var(--color-corn); }
.kpi-teal .kpi-icon-wrap { background:#ccfbf1; color:#0f766e; }
.kpi-icon { font-size:20px; }
.kpi-body { flex:1; min-width:0; }
.kpi-val { font-size:26px; font-weight:800; color:var(--text-primary); line-height:1.1; font-variant-numeric:tabular-nums; }
.kpi-label { font-size:11px; color:var(--text-tertiary); margin-top:2px; }
.kpi-trend { font-size:10px; font-weight:600; flex-shrink:0; white-space:nowrap; }
.kpi-trend.up { color:var(--color-cotton); }
.kpi-trend.down { color:var(--color-rice); }
.kpi-trend.steady { color:var(--text-tertiary); }
.kpi-trend:not(.up):not(.down):not(.steady) { color:var(--text-tertiary); font-size:9px; }
.kpi-card .sparkline { width:100%; height:20px; margin-bottom:4px; }

/* ============ 主网格 ============ */
.main-grid { display:grid; grid-template-columns:1fr 360px; gap:12px; }

/* ============ 地图面板 ============ */
.map-panel { padding:16px 16px 8px; }
.panel-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.panel-title { font-size:14px; font-weight:700; color:var(--text-primary); }
.panel-badge { font-size:10px; padding:3px 10px; border-radius:999px; background:var(--gray-100); color:var(--text-tertiary); }
.panel-badge.badge-red { background:#fee2e2; color:var(--color-cotton); }
.panel-tools { display:flex; align-items:center; gap:12px; }
.map-legend-inline { display:flex; gap:14px; }
.mli-item { font-size:11px; color:var(--text-tertiary); display:flex; align-items:center; gap:5px; }
.mli-dot { width:8px; height:8px; border-radius:50%; }

.map-wrap { position:relative; border-radius:var(--radius-md); overflow:hidden; }
.map-loading .map-wrap { opacity:0.6; }
.map-loader {
  position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center;
  background:rgba(255,255,255,0.85); border-radius:var(--radius-md); z-index:10; gap:12px; color:var(--text-tertiary); font-size:13px;
}
.map-loader-spin { width:32px; height:32px; border:3px solid var(--gray-200); border-top-color:var(--brand-500); border-radius:50%; animation:spin .8s linear infinite; }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes amPulse { 0%,100%{transform:scale(1);opacity:0.6} 50%{transform:scale(1.5);opacity:0} }

.crop-filters { display:flex; gap:6px; padding:10px 0 4px; flex-wrap:wrap; }
.cf-btn {
  display:flex; align-items:center; gap:5px;
  padding:5px 12px; border-radius:999px; border:1.5px solid var(--gray-200);
  background:#fff; color:var(--text-tertiary); font-size:11px; cursor:pointer;
  transition: all var(--duration-fast);
}
.cf-btn:hover { border-color:var(--brand-300); color:var(--brand-700); }
.cf-btn.active { background:var(--brand-50); border-color:var(--brand-400); color:var(--brand-700); font-weight:600; box-shadow:0 2px 6px rgba(46,125,50,0.12); }
.cf-dot { width:8px; height:8px; border-radius:50%; display:inline-block; }

/* ============ 右侧面板 ============ */
.side-panels { display:flex; flex-direction:column; gap:10px; }
.sp-card { padding:14px 16px; }

/* 预警列表 */
.alert-list { display:flex; flex-direction:column; gap:8px; max-height:380px; overflow-y:auto; }
.alert-list::-webkit-scrollbar { width:4px; }
.alert-list::-webkit-scrollbar-thumb { background:var(--gray-200); border-radius:2px; }
.alert-item {
  display:flex; gap:10px; padding:10px; border-radius:10px;
  cursor:pointer; transition:all var(--duration-fast);
  border:1px solid transparent;
  opacity:0; animation:slideInRight .4s var(--ease-out) forwards;
}
@keyframes slideInRight { from{opacity:0;transform:translateX(12px)} to{opacity:1;transform:translateX(0)} }
.alert-item:hover { transform:translateX(3px); }
.alert-high { background:#fef2f2; border-color:#fecaca; }
.alert-mid { background:#fefce8; border-color:#fde68a; }
.alert-low { background:#f0fdf4; border-color:#bbf7d0; }
.al-icon { flex-shrink:0; margin-top:2px; }
.alert-high .al-icon { color:var(--color-cotton); }
.alert-mid .al-icon { color:var(--color-wheat); }
.alert-low .al-icon { color:var(--color-rice); }
.al-body { flex:1; min-width:0; }
.al-title { font-size:12px; font-weight:600; color:var(--text-primary); }
.al-desc { font-size:11px; color:var(--text-tertiary); margin-top:2px; line-height:1.4; }
.al-tags { display:flex; gap:5px; margin-top:5px; flex-wrap:wrap; }
.al-crop-tag { font-size:10px; padding:1px 8px; border-radius:999px; font-weight:600; }
.al-drug-tag { font-size:10px; color:var(--text-tertiary); padding:1px 6px; border-radius:4px; background:var(--gray-100); }
.al-time-tag { font-size:10px; color:var(--text-tertiary); padding:1px 6px; border-radius:4px; background:var(--gray-50); }

/* 重大病虫害 */
.pest-mini-list { display:flex; flex-direction:column; gap:10px; max-height:360px; overflow-y:auto; }
.pest-mini-list::-webkit-scrollbar { width:4px; }
.pest-mini-list::-webkit-scrollbar-thumb { background:var(--gray-200); border-radius:2px; }
.pml-item { padding:8px 0; border-bottom:1px solid var(--gray-100); }
.pml-item:last-child { border-bottom:none; }
.pml-head { display:flex; align-items:center; gap:6px; }
.pml-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.pml-name { font-size:12px; font-weight:600; color:var(--text-primary); flex:1; }
.pml-sev { font-size:10px; padding:2px 7px; border-radius:999px; font-weight:600; }
.sev-偏 { background:#fee2e2; color:var(--color-cotton); }
.sev-中 { background:#fefce8; color:var(--color-wheat); }
.pml-meta { font-size:10px; color:var(--text-tertiary); margin-top:3px; }
.pml-bar-wrap { display:flex; align-items:center; gap:6px; margin-top:5px; }
.pml-bar { height:5px; border-radius:999px; min-width:4px; transition:width .6s var(--ease-out); }
.pml-num { font-size:9px; color:var(--text-tertiary); white-space:nowrap; }
.pml-trend { margin-top:4px; }

/* ============ 底部三列 ============ */
.bottom-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
.workflow-strip {
  display:grid; grid-template-columns:repeat(3,1fr); gap:8px;
  padding-top:10px; border-top:1px solid var(--gray-100);
}
.wf-step {
  min-width:0; padding:8px 10px; border-radius:8px;
  background:var(--gray-50); border:1px solid var(--gray-100);
}
.wf-label {
  display:block; font-size:10px; color:var(--text-tertiary); margin-bottom:3px;
}
.wf-step strong {
  display:block; font-size:12px; color:var(--text-primary);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.trend-crop-tabs { display:flex; gap:4px; flex-wrap:wrap; }
.tct-btn {
  padding:3px 10px; border-radius:6px; border:1.5px solid var(--gray-200);
  background:#fff; color:var(--text-tertiary); font-size:10px; cursor:pointer; transition:all var(--duration-fast);
}
.tct-btn.active { background:var(--brand-50); border-color:var(--brand-400); color:var(--brand-700); font-weight:600; }
.tct-btn:hover { border-color:var(--brand-300); color:var(--brand-700); }

/* ============ 底部信息仪表盘 ============ */
.info-dashboard {
  background:var(--bg-card); border-radius:var(--radius-xl); padding:16px 24px;
  border:1px solid var(--gray-200);
  box-shadow:var(--shadow-sm);
}
.id-row { display:flex; align-items:center; }
.id-item { display:flex; align-items:center; gap:12px; flex:1; padding:0 16px; min-width:0; }
.id-item:first-child { padding-left:0; }
.id-item:last-child { padding-right:0; }
.id-divider { width:1px; height:36px; background:var(--gray-100); flex-shrink:0; }
.id-icon-wrap { width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.id-ic-blue { background:#dbeafe; color:var(--color-corn); }
.id-ic-green { background:#dcfce7; color:var(--color-rice); }
.id-ic-teal { background:#ccfbf1; color:#0f766e; }
.id-ic-purple { background:#ede9fe; color:#7c3aed; }
.id-ic-amber { background:#fef3c7; color:var(--color-wheat); }
.id-body { min-width:0; }
.id-val { font-size:12px; font-weight:600; color:var(--text-primary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.id-lbl { font-size:10px; color:var(--text-tertiary); margin-top:1px; }

/* ============ Card 统一样式 ============ */
.card {
  background:var(--bg-card); border-radius:var(--radius-lg);
  box-shadow:var(--shadow-sm); border:1px solid var(--gray-200);
}

/* 动画 */
.animate-fade-in { opacity:0; animation:fadeInUp .5s var(--ease-out) forwards; }
@keyframes fadeInUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }

@media (max-width:1100px) {
  .main-grid { grid-template-columns:1fr; }
  .kpi-row { grid-template-columns:repeat(3,1fr); }
  .bottom-grid { grid-template-columns:1fr; }
}
@media (max-width:800px) {
  .kpi-row { grid-template-columns:repeat(2,1fr); }
  .workflow-strip { grid-template-columns:1fr; }
  .id-row { flex-wrap:wrap; }
  .id-divider { display:none; }
}
</style>
