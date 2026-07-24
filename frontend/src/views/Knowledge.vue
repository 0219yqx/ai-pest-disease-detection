<template>
  <div class="page-wrapper">
    <!-- 顶部 -->
    <div class="kg-top">
      <div class="kg-header">
        <div class="kh-left">
          <h1>知识图谱</h1>
          <p class="kh-sub">病虫害知识库 · 结构化数据检索 · 点击行查看详情</p>
        </div>
        <div class="kg-stats">
          <div class="ks-card"><div class="ks-val">{{ allPests.length }}</div><div class="ks-lbl">当前记录</div></div>
          <div class="ks-card"><div class="ks-val">{{ allPests.length }}</div><div class="ks-lbl">总病虫害</div></div>
          <div class="ks-card"><div class="ks-val">{{ cropList.length }}</div><div class="ks-lbl">作物类别</div></div>
        </div>
      </div>
      <div class="kg-toolbar card">
        <div class="kt-tabs">
          <span v-for="tab in tabs" :key="tab.key" class="kt-tab" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key; currentPage=1">
            <span class="kt-dot" :style="{ background: tab.color }"></span>
            {{ tab.label }}
            <span class="kt-count" v-if="tab.key !== 'all'">{{ tab.count }}</span>
          </span>
        </div>
        <div class="kt-actions">
          <div class="kt-search">
            <input v-model="searchText" placeholder="搜索病虫害名称..." class="kt-input" />
          </div>
          <button class="kt-view-btn" :class="{ active: viewType==='table' }" @click="viewType='table'">表格</button>
          <button class="kt-view-btn" :class="{ active: viewType==='card' }" @click="viewType='card'">卡片</button>
        </div>
      </div>
    </div>

    <!-- ===== 表格视图 ===== -->
    <div v-if="viewType==='table'" class="kg-table-wrap card">
      <table class="kg-table">
        <thead><tr>
          <th class="th-name">名称</th>
          <th>类型</th>
          <th>作物</th>
          <th class="th-sci">学名</th>
          <th>严重度</th>
          <th>发生期</th>
          <th>操作</th>
        </tr></thead>
        <tbody>
          <template v-for="item in pagedItems" :key="item.name">
            <tr class="kg-row" :class="{ expanded: expandedRow === item.name }" @click="openDetail(item)">
              <td class="td-name"><span class="name-dot" :style="{ background: getCropColor(item.crop) }"></span><span class="name-text">{{ item.name }}</span></td>
              <td><span class="type-tag" :class="item.type==='病害'?'tag-disease':'tag-pest'">{{ item.type }}</span></td>
              <td><span class="crop-tag">{{ item.crop }}</span></td>
              <td class="td-sci">{{ item.sci }}</td>
              <td><div class="severity-bar"><div class="sb-fill" :style="{ width: (item.severity||3)*20+'%', background: getSevColor(item.severity) }"></div></div><span class="sb-num">{{ item.severity }}/5</span></td>
              <td class="td-season">{{ item.season }}</td>
              <td><button class="action-btn" @click.stop="openDetail(item)">详情</button></td>
            </tr>
            <tr v-if="expandedRow === item.name" class="kg-expand-row">
              <td colspan="7">
                <div class="expand-content">
                  <div class="ec-field ec-symptom-field">
                    <div class="ef-label">症状简述</div>
                    <div class="ef-value ef-symptom">{{ (item.symptoms||"").slice(0,100) }}{{ (item.symptoms||"").length > 100 ? "..." : "" }}</div>
                  </div>
                  <div class="ec-field ec-cause-field">
                    <div class="ef-label">发病诱因</div>
                    <div class="ef-value ef-cause">{{ (item.cause||"").slice(0,80) }}{{ (item.cause||"").length > 80 ? "..." : "" }}</div>
                  </div>
                  <div class="ec-field ec-spread-field">
                    <div class="ef-label">传播途径</div>
                    <div class="ef-value ef-spread">{{ item.spread || '-' }}</div>
                  </div>
                  <div class="ec-field ec-impact-field">
                    <div class="ef-label">影响产量</div>
                    <div class="ef-value ef-impact">{{ item.impact || '-' }}</div>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <div class="kg-pagination" v-if="totalPages > 1">
        <span>共 {{ filteredPests.length }} 条 · 第 {{ currentPage }}/{{ totalPages }} 页</span>
        <div class="pg-btns">
          <button :disabled="currentPage <= 1" @click="currentPage--">上一页</button>
          <button v-for="p in displayPages" :key="p" :class="{ active: p === currentPage }" @click="currentPage = p">{{ p }}</button>
          <button :disabled="currentPage >= totalPages" @click="currentPage++">下一页</button>
        </div>
      </div>
    </div>

    <!-- ===== 卡片视图 ===== -->
    <div v-if="viewType==='card'" class="kg-card-grid">
      <div v-for="item in pagedItems" :key="item.name" class="pest-card" @click="openDetail(item)">
        <div class="pc-header" :style="{ borderLeftColor: getCropColor(item.crop) }">
          <div class="pc-top"><span class="pc-name">{{ item.name }}</span><span class="type-tag" :class="item.type==='病害'?'tag-disease':'tag-pest'">{{ item.type }}</span></div>
          <div class="pc-sci">{{ item.sci }}</div>
          <div class="pc-tags"><span class="crop-tag">{{ item.crop }}</span><span class="season-tag">{{ item.season }}</span></div>
        </div>
        <div class="pc-body">
          <div class="severity-bar sb-lg"><div class="sb-fill" :style="{ width: (item.severity||3)*20+'%', background: getSevColor(item.severity) }"></div></div>
          <div class="pc-symptoms">{{ (item.symptoms||"").slice(0,60) }}{{ (item.symptoms||"").length > 60 ? "..." : "" }}</div>
        </div>
      </div>
    </div>

    <!-- ===== 居中详情弹窗 ===== -->
    <transition name="modal-fade">
      <div v-if="detailItem" class="modal-overlay" @click.self="detailItem=null">
        <div class="modal-panel">
          <!-- 头部 -->
          <div class="mp-header" :style="{ '--accent': getCropColor(detailItem.crop) }">
            <div class="mp-meta">
              <span class="mp-type" :class="detailItem.type==='病害'?'mp-disease':'mp-pest'">{{ detailItem.type }}</span>
              <span class="mp-crop">{{ detailItem.crop }}</span>
              <span class="mp-season">{{ detailItem.season }}</span>
            </div>
            <h2 class="mp-title">{{ detailItem.name }}</h2>
            <p class="mp-sci">{{ detailItem.sci }}</p>
            <button class="mp-close" @click="detailItem=null">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <!-- 主体 -->
          <div class="mp-body">
            <!-- 严重度 -->
            <div class="mp-severity">
              <span class="ms-label">严重程度</span>
              <span v-for="i in 5" :key="i" class="ms-star" :class="{ filled: i <= (detailItem.severity||3) }">★</span>
              <span class="ms-text">{{ severityText(detailItem.severity) }}</span>
            </div>

            <!-- 症状描述 -->
            <div class="mp-section" v-if="detailItem.symptoms_paragraph || detailItem.symptoms">
              <div class="ms-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                症状描述
              </div>
              <p class="ms-paragraph">{{ detailItem.symptoms_paragraph || detailItem.symptoms || '暂无数据' }}</p>
            </div>

            <!-- 发病原因 -->
            <div class="mp-section" v-if="detailItem.cause_paragraph || detailItem.cause">
              <div class="ms-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                发病原因
              </div>
              <p class="ms-paragraph">{{ detailItem.cause_paragraph || detailItem.cause || '暂无数据' }}</p>
            </div>

            <!-- 防治方法（可折叠） -->
            <div class="mp-section mp-collapsible" v-if="detailItem.treatment_chemical || detailItem.treatment_mechanical || detailItem.treatment_biological">
              <div class="ms-title ms-clickable" @click="treatExpanded = !treatExpanded">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                防治方法
                <span class="ms-toggle" :class="{ collapsed: !treatExpanded }">▼</span>
              </div>
              <transition name="slide-down">
                <div v-if="treatExpanded" class="treat-blocks">
                  <div class="tb-item tb-mechanical" v-if="detailItem.treatment_mechanical">
                    <div class="tb-header">
                      <span class="tb-icon">🔧</span>
                      <span class="tb-label">机械防治</span>
                    </div>
                    <p class="tb-text">{{ detailItem.treatment_mechanical }}</p>
                  </div>
                  <div class="tb-item tb-biological" v-if="detailItem.treatment_biological">
                    <div class="tb-header">
                      <span class="tb-icon">🌱</span>
                      <span class="tb-label">生物防治</span>
                    </div>
                    <p class="tb-text">{{ detailItem.treatment_biological }}</p>
                  </div>
                  <div class="tb-item tb-chemical" v-if="detailItem.treatment_chemical">
                    <div class="tb-header">
                      <span class="tb-icon">💊</span>
                      <span class="tb-label">化学防治</span>
                    </div>
                    <p class="tb-text">{{ detailItem.treatment_chemical }}</p>
                  </div>
                </div>
              </transition>
            </div>

            <!-- 因果链（可折叠） -->
            <div class="mp-section mp-collapsible" v-if="detailItem.cause || detailItem.symptoms || detailItem.treatment_chemical">
              <div class="ms-title ms-clickable" @click="causalExpanded = !causalExpanded">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                发病因果链
                <span class="ms-toggle" :class="{ collapsed: !causalExpanded }">▼</span>
              </div>
              <transition name="slide-down">
                <div v-if="causalExpanded" class="causal-chain">
                  <div class="cc-node cc-env">
                    <div class="cc-icon">☀</div>
                    <div class="cc-label">诱发环境</div>
                    <div class="cc-text">{{ (detailItem.cause||'').slice(0, 30) }}{{ (detailItem.cause||'').length > 30 ? '…' : '' }}</div>
                  </div>
                  <div class="cc-arrow">→</div>
                  <div class="cc-node cc-infect">
                    <div class="cc-icon">🦠</div>
                    <div class="cc-label">发病症状</div>
                    <div class="cc-text">{{ (detailItem.symptoms||'').slice(0, 30) }}{{ (detailItem.symptoms||'').length > 30 ? '…' : '' }}</div>
                  </div>
                  <div class="cc-arrow">→</div>
                  <div class="cc-node cc-harm" :class="'cc-sev-' + (detailItem.severity||3)">
                    <div class="cc-icon">⚠</div>
                    <div class="cc-label">危害等级</div>
                    <div class="cc-stars"><span v-for="i in 5" :key="i" class="cc-star" :class="{filled: i <= (detailItem.severity||3)}">★</span></div>
                  </div>
                  <div class="cc-arrow">→</div>
                  <div class="cc-node cc-treat">
                    <div class="cc-icon">💊</div>
                    <div class="cc-label">推荐防治</div>
                    <div class="cc-text">{{ (detailItem.treatment_chemical||'').slice(0, 25) }}{{ (detailItem.treatment_chemical||'').length > 25 ? '…' : '' }}</div>
                  </div>
                </div>
              </transition>
            </div>

            <!-- 去问诊 -->
            <div class="mp-consult-bar" v-if="detailItem.name">
              <div class="mcb-tip">💡 想了解更详细的防治方案？AI 植保专家在线解答</div>
              <button class="mcb-btn" @click="goConsult(detailItem.name)">去问诊 · 咨询 {{ detailItem.name }}</button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { PEST_KNOWLEDGE, CROP_COLOR_MAP } from '../data/knowledgeData.js'

const router = useRouter()

const activeTab = ref('all')
const searchText = ref('')
const viewType = ref('table')
const currentPage = ref(1)
const pageSize = 15
const expandedRow = ref(null)
const detailItem = ref(null)
const allPests = ref([])
const causalExpanded = ref(true)
const treatExpanded = ref(true)

const tabs = ref([])
const cropList = computed(() => [...new Set(allPests.value.map(p => p.crop).filter(Boolean))])

const filteredPests = computed(() => {
  let list = allPests.value
  if (activeTab.value !== 'all') list = list.filter(p => p.crop === activeTab.value)
  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    list = list.filter(p => (p.name||'').includes(q) || (p.sci||'').toLowerCase().includes(q))
  }
  return list
})
const totalPages = computed(() => Math.ceil(filteredPests.value.length / pageSize))
const pagedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredPests.value.slice(start, start + pageSize)
})
const displayPages = computed(() => {
  const tp = totalPages.value
  if (tp <= 7) return Array.from({length: tp}, (_,i) => i + 1)
  const cp = currentPage.value
  if (cp <= 3) return [1,2,3,4,'...',tp]
  if (cp >= tp - 2) return [1,'...',tp-3,tp-2,tp-1,tp]
  return [1,'...',cp-1,cp,cp+1,'...',tp]
})

function getCropColor(crop) {
  return CROP_COLOR_MAP[crop] || '#888'
}
function getSevColor(s) {
  s = s || 3
  if (s >= 5) return '#d32f2f'
  if (s >= 4) return '#f57c00'
  if (s >= 3) return '#fbc02d'
  return '#388e3c'
}
function severityText(s) {
  s = s || 3
  if (s >= 5) return '极重度，需立即防治'
  if (s >= 4) return '重度，尽快防治'
  if (s >= 3) return '中度，密切监控'
  return '轻度，预防为主'
}
function openDetail(item) {
  detailItem.value = { ...item }
  // 确保弹窗的 body 有内容渲染
  if (!detailItem.value.symptoms && !detailItem.value.symptoms_paragraph) {
    detailItem.value.symptoms = '暂无症状描述数据'
    detailItem.value.symptoms_paragraph = '暂无症状描述数据'
  }
  if (!detailItem.value.cause && !detailItem.value.cause_paragraph) {
    detailItem.value.cause = '暂无病因数据'
    detailItem.value.cause_paragraph = '暂无病因数据'
  }
  if (!detailItem.value.treatment_chemical && !detailItem.value.treatment_mechanical && !detailItem.value.treatment_biological) {
    detailItem.value.treatment_chemical = '暂无化学防治方案'
  }
  causalExpanded.value = true
  treatExpanded.value = true
}
function goConsult(name) {
  detailItem.value = null
  router.push({ path: '/consult', query: { disease: name } })
}

onMounted(async () => {
  try {
    const r = await axios.get('/api/knowledge/list', { timeout: 5000 })
    const data = r.data?.data || []
    allPests.value = data
  } catch(e) { /* fallback */ }

  if (allPests.value.length === 0) {
    allPests.value = PEST_KNOWLEDGE
  }

  // Build tabs
  const cropSet = [...new Set(allPests.value.map(p => p.crop))]
  tabs.value = [{ key:'all', label:'全部', color:'#666', count: allPests.value.length }]
  cropSet.forEach(c => {
    tabs.value.push({ key:c, label:c, color:getCropColor(c), count: allPests.value.filter(p=>p.crop===c).length })
  })
})
</script>

<style scoped>
/* ---- 顶部 ---- */
.page-wrapper { width: 100%; padding: 0 24px; }
.kg-top { margin-bottom: 14px; }
.kg-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.kg-header h1 { font-size: 22px; font-weight: 800; color: var(--text-primary); margin: 0; }
.kh-sub { font-size: 12px; color: var(--text-tertiary); margin-top: 2px; }
.kg-stats { display: flex; gap: 10px; }
.ks-card {
  background: var(--bg-card); border: 1px solid var(--gray-200); border-radius: 10px;
  padding: 8px 14px; text-align: center; min-width: 70px;
  transition: all var(--duration-fast) var(--ease-out);
}
.ks-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: var(--brand-200); }
.ks-val { font-size: 20px; font-weight: 800; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.ks-lbl { font-size: 10px; color: var(--text-tertiary); margin-top: 1px; }

/* ---- 工具栏 ---- */
.kg-toolbar { display: flex; align-items: center; gap: 10px; padding: 8px 14px; border-radius: 10px; margin-bottom: 14px; }
.kt-tabs { display: flex; gap: 4px; flex-wrap: wrap; flex: 1; }
.kt-tab {
  display: flex; align-items: center; gap: 4px; padding: 5px 10px;
  font-size: 12px; color: var(--text-secondary); cursor: pointer;
  border-radius: 6px; white-space: nowrap; transition: all var(--duration-fast) var(--ease-out);
}
.kt-tab:hover { background: var(--gray-50); }
.kt-tab.active { background: #e8f5e9; color: #2e7d32; font-weight: 600; box-shadow: 0 2px 6px rgba(46,125,50,0.12); }
.kt-dot { width: 8px; height: 8px; border-radius: 50%; }
.kt-count { font-size: 10px; color: var(--text-tertiary); background: var(--gray-100); padding: 0 5px; border-radius: 999px; }
.kt-actions { display: flex; gap: 6px; align-items: center; }
.kt-input {
  padding: 5px 10px; border: 1.5px solid var(--gray-200); border-radius: 8px;
  font-size: 12px; width: 160px; outline: none;
  transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
}
.kt-input:focus { border-color: var(--brand-400); box-shadow: 0 0 0 3px rgba(76,175,80,0.1); }
.kt-view-btn {
  padding: 4px 10px; font-size: 11px; border: 1.5px solid var(--gray-200); border-radius: 8px;
  background: #fff; color: var(--text-secondary); cursor: pointer;
  transition: all var(--duration-fast);
}
.kt-view-btn:hover { border-color: var(--brand-300); color: var(--brand-700); }
.kt-view-btn.active { background: var(--grad-brand); color: #fff; border-color: transparent; box-shadow: 0 2px 8px rgba(46,125,50,0.2); }

/* ---- 表格视图 ---- */
.kg-table-wrap { border-radius: 10px; overflow: hidden; padding: 0; }
.kg-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.kg-table th {
  padding: 10px 12px; text-align: left; font-size: 11px; color: var(--text-tertiary); font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.5px; background: var(--gray-50);
  border-bottom: 1px solid var(--gray-200);
}
.kg-table td { padding: 10px 12px; border-bottom: 1px solid var(--gray-100); }
.kg-row { cursor: pointer; transition: background var(--duration-fast); }
.kg-row:hover { background: var(--gray-50); }
.kg-row.expanded { background: #f0fdf4; }
.name-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }
.name-text { font-weight: 600; color: var(--text-primary); font-size: 14px; transition: color var(--duration-fast); }
.kg-row:hover .name-text { color: var(--brand-700); }
.type-tag { display: inline-block; padding: 1px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-disease { background: #fff3e0; color: #e65100; }
.tag-pest { background: #ffebee; color: #c62828; }
.crop-tag { display: inline-block; padding: 1px 8px; border-radius: 4px; font-size: 11px; background: var(--gray-100); color: var(--text-secondary); }
.severity-bar { display: inline-block; width: 60px; height: 5px; background: var(--gray-100); border-radius: 3px; overflow: hidden; vertical-align: middle; margin-right: 6px; }
.sb-fill { height: 100%; border-radius: 3px; transition: width 0.6s var(--ease-out); }
.sb-num { font-size: 11px; color: var(--text-tertiary); font-variant-numeric: tabular-nums; }
.sb-lg { width: 80px; height: 6px; }
.sb-lg .sb-fill { height: 6px; }
.td-sci { font-size: 12px; color: var(--text-tertiary); max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-style: italic; }
.td-season { font-size: 12px; color: var(--text-secondary); }
.action-btn {
  padding: 3px 10px; font-size: 11px; border: 1px solid var(--brand-200); border-radius: 6px;
  background: var(--brand-50); color: var(--brand-700); cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}
.action-btn:hover { background: var(--grad-brand); color: #fff; border-color: transparent; box-shadow: 0 2px 8px rgba(46,125,50,0.2); transform: translateY(-1px); }

/* ---- 展开行 ---- */
.kg-expand-row td { padding: 0 !important; border-bottom: 2px solid var(--brand-200) !important; }
.expand-content { padding: 14px 18px; background: linear-gradient(135deg, #f8fdf9, #fefce8); }
.ec-field { margin-bottom: 10px; }
.ef-label { font-size: 12px; font-weight: 700; color: var(--brand-700); margin-bottom: 4px; display: flex; align-items: center; gap: 4px; }
.ef-value { font-size: 14px; color: var(--text-primary); line-height: 1.7; }
.ef-symptom { color: #c62828; font-weight: 600; }
.ef-cause { color: #e65100; font-weight: 600; }
.ec-symptom-field { border-left: 3px solid #c62828; padding-left: 10px; }
.ec-cause-field { border-left: 3px solid #e65100; padding-left: 10px; }
.ec-spread-field { border-left: 3px solid #1976d2; padding-left: 10px; }
.ec-impact-field { border-left: 3px solid #7c3aed; padding-left: 10px; }
.ef-spread { color: #1565c0; font-weight: 600; }
.ef-impact { color: #6a1b9a; font-weight: 600; }

/* ---- 分页 ---- */
.kg-pagination { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; font-size: 12px; color: var(--text-tertiary); }
.pg-btns { display: flex; gap: 4px; }
.pg-btns button {
  padding: 4px 10px; border: 1.5px solid var(--gray-200); border-radius: 6px;
  background: #fff; color: var(--text-secondary); cursor: pointer; font-size: 12px;
  transition: all var(--duration-fast);
}
.pg-btns button:hover { border-color: var(--brand-300); color: var(--brand-700); }
.pg-btns button.active { background: var(--grad-brand); color: #fff; border-color: transparent; box-shadow: 0 2px 6px rgba(46,125,50,0.2); }
.pg-btns button:disabled { opacity: 0.4; cursor: default; }

/* ---- 卡片视图 ---- */
.kg-card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.pest-card {
  background: #fff; border: 1px solid var(--gray-200); border-radius: 10px; overflow: hidden;
  cursor: pointer; transition: all var(--duration-normal) var(--ease-out);
  position: relative;
}
.pest-card::after {
  content: ''; position: absolute; top: 0; left: -120%;
  width: 60%; height: 100%;
  background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%);
  transform: skewX(-20deg); pointer-events: none;
  transition: left 700ms var(--ease-out); z-index: 1;
}
.pest-card:hover { border-color: var(--brand-300); box-shadow: var(--shadow-md); transform: translateY(-3px); }
.pest-card:hover::after { left: 130%; }
.pc-header { padding: 14px; border-left: 4px solid var(--brand-600); position: relative; z-index: 2; }
.pc-top { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.pc-name { font-size: 15px; font-weight: 700; color: var(--text-primary); }
.pc-sci { font-size: 12px; color: var(--text-tertiary); margin-bottom: 6px; font-style: italic; }
.pc-tags { display: flex; gap: 6px; }
.season-tag { display: inline-block; padding: 1px 8px; font-size: 11px; background: var(--gray-100); color: var(--text-secondary); border-radius: 4px; }
.pc-body { padding: 0 14px 14px; position: relative; z-index: 2; }
.pc-symptoms { font-size: 13px; color: var(--text-secondary); margin-top: 8px; line-height: 1.6; }

/* ===== 居中模态框 ===== */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000;
  display: flex; align-items: center; justify-content: center; padding: 20px;
  backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
}
.modal-panel {
  width: 680px; max-width: 100%; max-height: 85vh; background: #fff;
  border-radius: 16px; overflow: hidden; display: flex; flex-direction: column;
  box-shadow: 0 24px 70px rgba(0,0,0,0.25), 0 0 0 1px rgba(255,255,255,0.5);
}
.modal-fade-enter-active { animation: modalIn 300ms var(--ease-out); }
.modal-fade-leave-active { animation: modalIn 200ms var(--ease-out) reverse; }
@keyframes modalIn { from { opacity: 0; } to { opacity: 1; } }
.modal-fade-enter-active .modal-panel { animation: panelIn 350ms var(--ease-spring); }
.modal-fade-leave-active .modal-panel { animation: panelIn 200ms var(--ease-out) reverse; }
@keyframes panelIn { from { opacity: 0; transform: scale(0.92) translateY(20px); } to { opacity: 1; transform: scale(1) translateY(0); } }

.mp-header {
  padding: 22px 24px 16px; border-bottom: 1px solid var(--gray-100); position: relative;
  background: linear-gradient(135deg, var(--gray-50), #f0fdf4);
  overflow: hidden;
}
.mp-header::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: var(--accent, var(--grad-brand));
}
.mp-meta { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
.mp-type { padding: 2px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
.mp-disease { background: #fff3e0; color: #e65100; }
.mp-pest { background: #ffebee; color: #c62828; }
.mp-crop { font-size: 12px; color: var(--text-secondary); background: var(--gray-100); padding: 2px 8px; border-radius: 6px; }
.mp-season { font-size: 12px; color: var(--text-secondary); background: var(--gray-100); padding: 2px 8px; border-radius: 6px; }
.mp-title { font-size: 22px; font-weight: 800; color: var(--text-primary); margin: 0; }
.mp-sci { font-size: 12px; color: var(--text-tertiary); margin-top: 2px; font-style: italic; }
.mp-close {
  position: absolute; top: 16px; right: 16px; width: 32px; height: 32px;
  border: none; background: var(--gray-100); border-radius: 8px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: var(--text-tertiary); transition: all var(--duration-fast);
}
.mp-close:hover { background: var(--gray-200); color: var(--text-primary); transform: rotate(90deg); }

.mp-body { padding: 20px 24px; overflow-y: auto; flex: 1; }

/* 严重度 */
.mp-severity {
  display: flex; align-items: center; gap: 6px; margin-bottom: 18px;
  padding: 10px 14px; background: var(--gray-50); border-radius: 8px; border: 1px solid var(--gray-200);
}
.ms-label { font-size: 12px; font-weight: 700; color: var(--text-secondary); }
.ms-star { font-size: 16px; color: var(--gray-200); transition: color var(--duration-fast); }
.ms-star.filled { color: #f57c00; }
.ms-text { font-size: 12px; color: var(--text-secondary); margin-left: 8px; }

/* 各区块 */
.mp-section { margin-bottom: 16px; }
.ms-title { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; }
.ms-paragraph {
  font-size: 13px; color: var(--text-secondary); line-height: 1.9; margin: 0;
  padding: 12px 14px; background: var(--gray-50); border: 1px solid var(--gray-200);
  border-radius: 8px; text-indent: 2em;
}

/* 防治方法三类 */
.treat-blocks { display: flex; flex-direction: column; gap: 10px; }
.tb-item { padding: 14px 16px; border-radius: 10px; border: 1px solid; transition: transform var(--duration-fast); }
.tb-item:hover { transform: translateX(3px); }
.tb-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.tb-icon { font-size: 18px; }
.tb-label { font-size: 13px; font-weight: 700; }
.tb-text { font-size: 13px; color: var(--text-secondary); line-height: 1.8; margin: 0; }
.tb-mechanical { background: #f0f9ff; border-color: #bfdbfe; }
.tb-mechanical .tb-label { color: #1d4ed8; }
.tb-biological { background: #f0fdf4; border-color: #bbf7d0; }
.tb-biological .tb-label { color: #15803d; }
.tb-chemical { background: #fffbeb; border-color: #fde68a; }
.tb-chemical .tb-label { color: #b45309; }

/* 可折叠 */
.mp-collapsible .ms-clickable { cursor: pointer; user-select: none; transition: color var(--duration-fast); }
.mp-collapsible .ms-clickable:hover { color: var(--brand-700); }
.ms-toggle { margin-left: auto; font-size: 10px; color: var(--text-tertiary); transition: transform 250ms var(--ease-out); }
.ms-toggle.collapsed { transform: rotate(-90deg); }
.slide-down-enter-active { animation: slideDown 250ms var(--ease-out); }
.slide-down-leave-active { animation: slideDown 150ms var(--ease-out) reverse; }
@keyframes slideDown { from { max-height: 0; opacity: 0; overflow: hidden; } to { max-height: 500px; opacity: 1; } }

/* 因果链 */
.causal-chain {
  display: flex; align-items: center; gap: 6px; padding: 14px;
  background: linear-gradient(135deg, var(--gray-50), #f0fdf4);
  border: 1px solid var(--brand-200); border-radius: 10px; overflow-x: auto;
}
.cc-node {
  flex: 1; min-width: 100px; text-align: center; padding: 12px 8px;
  border-radius: 10px; background: #fff; border: 1px solid var(--gray-200);
  transition: all var(--duration-fast);
}
.cc-node:hover { box-shadow: var(--shadow-sm); transform: translateY(-2px); }
.cc-icon { font-size: 22px; margin-bottom: 4px; }
.cc-label { font-size: 11px; font-weight: 700; color: var(--text-secondary); margin-bottom: 4px; }
.cc-text { font-size: 11px; color: var(--text-primary); line-height: 1.5; }
.cc-arrow { font-size: 20px; color: var(--text-tertiary); font-weight: 700; flex-shrink: 0; }
.cc-env { border-color: #fde68a; background: #fffbeb; }
.cc-infect { border-color: #fecaca; background: #fef2f2; }
.cc-harm { border-color: var(--gray-200); }
.cc-sev-5 { border-color: #fca5a5; background: #fef2f2; }
.cc-sev-4 { border-color: #fdba74; background: #fff7ed; }
.cc-sev-3 { border-color: #fde68a; background: #fffbeb; }
.cc-treat { border-color: #bbf7d0; background: #f0fdf4; }
.cc-stars { display: flex; justify-content: center; gap: 1px; }
.cc-star { font-size: 12px; color: var(--gray-200); }
.cc-star.filled { color: #f57c00; }

/* 去问诊 */
.mp-consult-bar {
  margin-top: 18px; padding: 14px;
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
  border: 1px solid var(--brand-200); border-radius: 10px; text-align: center;
}
.mcb-tip { font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; }
.mcb-btn {
  padding: 8px 24px; border: none; border-radius: 8px;
  background: var(--grad-brand); color: #fff; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: all var(--duration-fast) var(--ease-out);
}
.mcb-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(46,125,50,0.3); }
.mcb-btn:active { transform: translateY(0) scale(0.97); }
</style>
