<template>
  <div class="page-wrapper">
    <div class="page-header">
      <div class="ph-left">
        <h1>AI病虫害识别</h1>
        <p>支持水稻 · 小麦 · 玉米 · 棉花等 13 类作物 38 种病虫害智能识别</p>
      </div>
      <div class="ph-badge">
        <span class="tag tag-green">YOLOv8</span>
        <span class="tag tag-blue">真实模型优先</span>
      </div>
    </div>

    <!-- 步骤指示器 -->
    <div class="step-bar animate-fade-in">
      <div class="step" :class="{ active: !selectedFile, done: !!selectedFile }">
        <span class="step-num">{{ selectedFile ? '✓' : '1' }}</span><span class="step-txt">上传图片</span>
      </div>
      <div class="step-line" :class="{ filled: !!selectedFile }"></div>
      <div class="step" :class="{ active: !!selectedFile && !result && !diagnoseError, done: !!result || !!diagnoseError }">
        <span class="step-num">{{ result || diagnoseError ? '✓' : '2' }}</span><span class="step-txt">AI 分析</span>
      </div>
      <div class="step-line" :class="{ filled: !!result || !!diagnoseError }"></div>
      <div class="step" :class="{ active: !!result || !!diagnoseError }">
        <span class="step-num">3</span><span class="step-txt">{{ diagnoseError ? '处理异常' : '查看结果' }}</span>
      </div>
    </div>

    <div class="diag-layout">
      <!-- 左：上传区 -->
      <div class="card upload-card animate-fade-in">
        <div class="drop-zone" :class="{ dragging: isDragging, 'has-file': previewUrl, scanning: loading }"
             @dragover.prevent="isDragging=true" @dragleave="isDragging=false"
             @drop.prevent="handleDrop" @click="triggerUpload">
          <div class="scan-line" v-if="loading"></div>
          <div v-if="!previewUrl" class="drop-placeholder">
            <div class="drop-icon-wrap">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
            <p class="drop-text">拖拽图片到此处，或 <span class="drop-link">点击上传</span></p>
            <p class="drop-hint">建议 640×640，支持 JPG / PNG</p>
          </div>
          <img v-else :src="previewUrl" class="preview-img" :class="{ dim: loading }" />
          <div v-if="loading" class="scan-overlay">
            <div class="so-text">AI 正在分析...</div>
          </div>
          <input ref="fileInput" type="file" accept="image/jpeg,image/png" style="display:none" @change="handleFileChange" />
        </div>
        <div class="upload-actions">
          <button class="btn btn-primary" :disabled="!selectedFile||loading" @click="submitDiagnose">
            <svg v-if="loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M21 12a9 9 0 1 1-6.22-8.56"/></svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            {{ loading ? '分析中...' : '开始识别' }}
          </button>
          <button class="btn btn-ghost" :disabled="!previewUrl" @click="resetUpload">重新选择</button>
        </div>
      </div>

      <!-- 右：结果区 -->
      <div class="card result-card animate-fade-in" style="animation-delay:100ms">
        <div class="section-header">
          <span class="section-title">识别结果</span>
          <span v-if="result" class="section-badge result-time-badge">⏱ {{ resultLatency }}ms</span>
        </div>
        <div v-if="diagnoseError && !loading" class="result-error animate-scale-in">
          <div class="error-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <div>
            <div class="error-title">识别未完成</div>
            <div class="error-desc">{{ diagnoseError }}</div>
          </div>
          <button class="btn btn-outline" :disabled="!selectedFile" @click="submitDiagnose">重新分析</button>
        </div>

        <div v-if="!result && !loading && !diagnoseError" class="result-empty">
          <div class="empty-illustration animate-float">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--gray-300)" stroke-width="1">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <p class="empty-text">上传图片后点击开始识别</p>
          <p class="empty-sub">AI 将自动分析病虫害类型并给出防治建议</p>
        </div>

        <!-- 骨架屏（加载中） -->
        <div v-if="loading" class="result-skeleton">
          <div class="skeleton skel-banner"></div>
          <div class="skeleton skel-line" style="width:80%"></div>
          <div class="skeleton skel-line" style="width:60%"></div>
          <div class="skeleton skel-line" style="width:90%"></div>
          <div class="skeleton skel-line" style="width:70%"></div>
        </div>

        <div v-if="result && !loading" class="result-content animate-scale-in">
          <!-- 主结果 Banner -->
          <div class="result-banner" :style="{'--accent': accentColor}">
            <div class="rb-top">
              <div class="rb-tags">
                <span class="tag" :class="cropTagClass">{{ result.crop || '--' }}</span>
                <span v-if="result.type" class="rb-type-tag" :class="result.type === '害虫' ? 'rtt-pest' : 'rtt-disease'">{{ result.type }}</span>
                <span v-if="confidenceLevel" class="rb-conf-badge" :class="'rb-conf-' + confidenceLevel">{{ confidenceLabel }}</span>
              </div>
              <span class="rb-source">{{ sourceLabel }}</span>
            </div>
            <div class="rb-name">{{ result.disease || result.pest_name }}</div>
            <div v-if="result.sci" class="rb-sci">{{ result.sci }}</div>
            <div class="rb-conf-wrap">
              <div class="rb-conf-bar">
                <div class="rb-conf-fill" :style="{width: ((result.confidence||0)*100).toFixed(0)+'%'}"></div>
              </div>
              <span class="rb-conf-val">置信度 {{ ((result.confidence||0)*100).toFixed(1) }}%</span>
            </div>
          </div>

          <div class="trust-panel">
            <div class="trust-item">
              <div class="trust-label">可信度判断</div>
              <div class="trust-value" :class="'trust-' + confidenceLevel">{{ confidenceAdvice.title }}</div>
            </div>
            <div class="trust-item">
              <div class="trust-label">下一步动作</div>
              <div class="trust-value">{{ confidenceAdvice.action }}</div>
            </div>
            <div class="trust-item">
              <div class="trust-label">数据来源</div>
              <div class="trust-value">{{ sourceLabel }}</div>
            </div>
          </div>

          <!-- Top3 候选病害 -->
          <div v-if="candidates.length > 1" class="candidates-box">
            <div class="cb-title">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/></svg>
              其他候选病害（Top 3）
            </div>
            <div class="cb-list">
              <div v-for="(c, idx) in candidates" :key="idx"
                   class="cb-item" :class="{ 'cb-item-top': idx === 0 }"
                   @click="applyCandidate(c)">
                <span class="cb-rank">{{ idx + 1 }}</span>
                <div class="cb-info">
                  <div class="cb-name">{{ c.name }}</div>
                  <div class="cb-crop">{{ c.crop }}</div>
                </div>
                <div class="cb-bar-wrap">
                  <div class="cb-bar" :style="{ width: (c.confidence*100).toFixed(0) + '%', background: getCropColor(c.crop) }"></div>
                </div>
                <span class="cb-pct">{{ (c.confidence*100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <!-- 元数据网格 -->
          <div class="meta-grid">
            <div class="meta-item">
              <div class="meta-label">发生时期</div>
              <div class="meta-value">{{ result.season || '6-9月' }}</div>
            </div>
            <div class="meta-item">
              <div class="meta-label">传播途径</div>
              <div class="meta-value">{{ result.spread || '气流 / 雨水传播' }}</div>
            </div>
            <div class="meta-item">
              <div class="meta-label">影响产量</div>
              <div class="meta-value" :style="{color: confidenceLevel === 'high' ? '#dc2626' : confidenceLevel === 'mid' ? '#e8a317' : '#15803d'}">
                {{ result.impact || (confidenceLevel === 'high' ? '减产 20-50%' : confidenceLevel === 'mid' ? '减产 10-20%' : '减产 <10%') }}
              </div>
            </div>
          </div>

          <div class="result-fields">
            <div class="rf-item">
              <div class="rf-label">症状描述</div>
              <div class="rf-value">{{ result.symptoms || result.description || '暂无描述' }}</div>
            </div>
            <div class="rf-item rf-highlight">
              <div class="rf-label">防治建议</div>
              <div class="rf-value">{{ result.treatment || result.advice || '暂无建议' }}</div>
            </div>
          </div>

          <!-- 防治时间轴 -->
          <div class="treat-timeline">
            <div class="tt-title">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              最佳防治时间窗
            </div>
            <div class="timeline">
              <div class="tl-item">
                <div class="tl-dot tl-done"></div>
                <div class="tl-content">
                  <div class="tl-head"><span class="tl-stage">预防期</span><span class="tl-time">发病前 7 天</span></div>
                  <div class="tl-desc">选用抗病品种，合理密植，增施磷钾肥增强抗性。</div>
                </div>
              </div>
              <div class="tl-item">
                <div class="tl-dot tl-active"></div>
                <div class="tl-content">
                  <div class="tl-head"><span class="tl-stage tl-stage-now">关键防治期</span><span class="tl-time tl-time-now">当前 · 立即施药</span></div>
                  <div class="tl-desc">发病初期及时喷施对症药剂，连喷 2-3 次，间隔 7-10 天。</div>
                </div>
              </div>
              <div class="tl-item">
                <div class="tl-dot"></div>
                <div class="tl-content">
                  <div class="tl-head"><span class="tl-stage">巩固期</span><span class="tl-time">施药后 14 天</span></div>
                  <div class="tl-desc">复查防治效果，必要时补施，清除病残体减少再侵染。</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作 -->
          <div class="result-actions">
            <button class="btn btn-outline" @click="goConsult">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              咨询 AI 专家
            </button>
            <button class="btn btn-ghost" @click="resetUpload">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
              重新识别
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { PEST_KNOWLEDGE, CROP_COLOR_MAP, MODEL_CLASSES } from '../data/knowledgeData.js'

const router = useRouter()

const colors = CROP_COLOR_MAP
const tagMap = {
  '水稻':'tag-green','小麦':'tag-orange','玉米':'tag-blue','棉花':'tag-red',
  '大豆':'tag-green','番茄':'tag-red','苹果':'tag-red','葡萄':'tag-red',
  '柑橘':'tag-orange','草莓':'tag-red','黄瓜':'tag-green','樱桃':'tag-red',
  '马铃薯':'tag-orange',
}

// class_id 或 class_N → 中文名称
function resolveClassName(result) {
  // 如果 disease 已经是中文（非 class_ 开头），直接用
  const name = result.disease || result.pest_name || ''
  if (!name.startsWith('class_')) return name
  // 尝试从 class_id 解析
  const cid = result.class_id
  if (cid !== undefined && cid !== null && cid >= 0) {
    return MODEL_CLASSES[cid] || name
  }
  // 尝试从 class_N 字符串解析
  try {
    const n = parseInt(name.replace('class_', ''))
    return MODEL_CLASSES[n] || name
  } catch { return name }
}

// 从 YOLO 类名中提取 severity 后缀（如 "_轻"、"_重"、"_严重"、"_中"、"_轻微"、"_早期"、"_严重"、"_中期"、"_后期"）
function extractSeveritySuffix(name) {
  const m = name.match(/_(轻|重|严重|中|轻微|早期|后期|中期|rice|_2|_3|_4|_5)$/)
  return m ? m[1] : ''
}

// 去掉 severity / 重复后缀，得到基础病害名（用于匹配知识库）
function getBaseDiseaseName(name) {
  return name
    .replace(/_(轻|重|严重|中|轻微|早期|后期|中期|rice|2|3|4|5)$/g, '')
    .replace(/_健康$/, '')
}

// 通过基础病害名 + 作物名匹配知识库
function matchKnowledge(baseName, crop) {
  // 精确匹配
  let found = PEST_KNOWLEDGE.find(p => p.name === baseName)
  if (found) return found
  // 模糊匹配：包含关系
  found = PEST_KNOWLEDGE.find(p => baseName.includes(p.name) || p.name.includes(baseName))
  if (found) return found
  // 通过作物名匹配
  if (crop) {
    found = PEST_KNOWLEDGE.find(p => p.crop === crop && baseName.includes(p.name.replace(/^.*?([\u4e00-\u9fa5]+病|.*虫)$/, '$1')))
  }
  return found || null
}

const fileInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)
const loading = ref(false)
const isDragging = ref(false)
const result = ref(null)
const candidates = ref([])
const resultLatency = ref(0)
const diagnoseError = ref('')

const accentColor = computed(() => colors[result.value?.crop] || '#888')
const cropTagClass = computed(() => tagMap[result.value?.crop] || 'tag-gray')
const sourceLabel = computed(() => {
  if (!result.value) return ''
  if (result.value.source === 'yolov8') return 'YOLOv8 实测'
  if (result.value.source === 'rejected') return '系统拒识'
  if (result.value.source === 'error') return '模型异常'
  return '后端返回'
})

// 置信度等级（仅表示模型对该结果的把握程度，非病害严重程度）
const confidenceLevel = computed(() => {
  if (!result.value) return null
  const conf = result.value.confidence || 0
  if (conf >= 0.92) return 'high'
  if (conf >= 0.8) return 'mid'
  return 'low'
})
const confidenceLabel = computed(() => {
  const m = { high: '置信度高', mid: '置信度中', low: '置信度低' }
  return m[confidenceLevel.value] || ''
})
const confidenceAdvice = computed(() => {
  if (!result.value) return { title: '--', action: '--' }
  if (result.value.source === 'rejected') {
    return { title: '非识别范围', action: '请重新上传清晰的作物叶片、果实或茎秆照片' }
  }
  if (confidenceLevel.value === 'high') {
    return { title: '模型可信度高', action: '建议结合田间症状和发生时期确认后用药' }
  }
  if (confidenceLevel.value === 'mid') {
    return { title: '模型可信度中等', action: '建议查看候选病害并补拍病斑正反面照片' }
  }
  return { title: '模型可信度低', action: '请更换角度或光照重新拍摄后再识别' }
})

function getCropColor(crop) { return colors[crop] || '#888' }

function triggerUpload() { fileInput.value?.click() }
function handleFileChange(e) { const f = e.target.files?.[0]; if (f) setFile(f) }
function handleDrop(e) { isDragging.value = false; const f = e.dataTransfer.files?.[0]; if (f) setFile(f) }
function setFile(f) {
  if (!['image/jpeg','image/png'].includes(f.type)) { alert('仅支持 JPG / PNG'); return }
  selectedFile.value = f; previewUrl.value = URL.createObjectURL(f); result.value = null; candidates.value = []; diagnoseError.value = ''
}

// 从后端返回的真实 candidates 中提取 Top3 展示，前端不再伪造候选数据
function loadCandidatesFromBackend(data, crop, primaryName) {
  if (data.candidates && data.candidates.length > 1) {
    // 取前3个（过滤掉健康类）
    const filtered = data.candidates
      .filter(c => !c.name.includes('健康') && (c.crop || crop))
      .slice(0, 3)
    return filtered.map(c => {
      const kn = matchKnowledge(getBaseDiseaseName(c.name), crop)
      return { ...c, crop: crop, ...(kn ? { type: kn.type, sci: kn.sci } : {}) }
    })
  }
  return []
}

async function submitDiagnose() {
  if (!selectedFile.value) return
  loading.value = true; result.value = null; candidates.value = []; diagnoseError.value = ''
  const fd = new FormData(); fd.append('file', selectedFile.value)
  const t0 = performance.now()
  try {
    const r = await axios.post('/api/diagnose', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    const data = r.data.data || r.data
    // 将 class_N 映射为中文名
    const cnName = resolveClassName(data)
    const sev = extractSeveritySuffix(cnName)
    const baseName = getBaseDiseaseName(cnName)
    // 如果后端没有返回 crop，从中文名推断
    let crop = data.crop || ''
    if (!crop) {
      const cropKeywords = {'水稻':'水稻','小麦':'小麦','玉米':'玉米','棉花':'棉花','大豆':'大豆','番茄':'番茄','苹果':'苹果','葡萄':'葡萄','柑橘':'柑橘','草莓':'草莓','黄瓜':'黄瓜','樱桃':'樱桃','马铃薯':'马铃薯'}
      for (const [k, v] of Object.entries(cropKeywords)) {
        if (cnName.includes(k)) { crop = v; break }
      }
    }
    // 匹配知识库补充详细信息
    const kn = matchKnowledge(baseName, crop)
    result.value = {
      disease: cnName,
      crop: crop || (kn ? kn.crop : ''),
      type: kn ? kn.type : '',
      sci: kn ? kn.sci : '',
      season: kn ? kn.season : '',
      spread: kn ? kn.spread : '',
      impact: kn ? kn.impact : '',
      confidence: data.confidence || 0,
      symptoms: kn ? kn.symptoms : (data.symptoms || ''),
      treatment: kn ? kn.treatment_chemical : (data.treatment || ''),
      source: data.source || 'yolov8',
      class_id: data.class_id,
    }
    resultLatency.value = Math.round(performance.now() - t0)
    candidates.value = loadCandidatesFromBackend(data, crop || (kn ? kn.crop : ''), cnName)
  } catch (e) {
    const status = e.response?.status
    const detail = e.response?.data?.detail || e.response?.data?.message
    diagnoseError.value = detail || (status ? `后端服务返回 ${status}，请稍后重试。` : '后端识别服务暂时不可用，请检查服务状态后重试。')
    resultLatency.value = Math.round(performance.now() - t0)
  } finally { loading.value = false }
}

function applyCandidate(c) {
  // 候选点击：直接作为新的诊断结果（置信度来自后端模型实际概率）
  const kn = matchKnowledge(getBaseDiseaseName(c.name), c.crop)
  result.value = {
    disease: c.name, crop: c.crop, type: kn?.type || '', sci: kn?.sci || '',
    season: kn?.season || '', spread: kn?.spread || '', impact: kn?.impact || '',
    confidence: c.confidence || 0,
    symptoms: kn?.symptoms || '', treatment: kn?.treatment_chemical || '',
    source: result.value?.source || 'yolov8'
  }
  // 候选列表：从结果中移除选中的项，保持简洁
  candidates.value = candidates.value.filter(cd => cd.name !== c.name)
}

function goConsult() {
  if (result.value) {
    router.push({ path: '/consult', query: { disease: result.value.disease || result.value.pest_name } })
  }
}

function resetUpload() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  selectedFile.value = null; previewUrl.value = null; result.value = null; candidates.value = []; diagnoseError.value = ''
}
</script>
<style scoped>
.page-wrapper { width: 100%; padding: 0 28px; }

.page-header {
  display: flex; justify-content: space-between; align-items: flex-end;
  margin-bottom: 20px;
}
.ph-left h1 { font-size: 22px; font-weight: 800; color: var(--text-primary); margin: 0; }
.ph-left p  { font-size: 12px; color: var(--text-tertiary); margin-top: 4px; }
.ph-badge { display: flex; gap: 6px; }

/* ---- 步骤指示器 ---- */
.step-bar {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 20px; padding: 14px 24px;
  background: var(--bg-card); border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
}
.step { display: flex; align-items: center; gap: 8px; }
.step-num {
  width: 24px; height: 24px; border-radius: 50%; display: flex;
  align-items: center; justify-content: center; font-size: 12px; font-weight: 700;
  background: var(--gray-100); color: var(--text-tertiary);
  transition: all var(--duration-normal) var(--ease-spring);
}
.step-txt { font-size: 13px; color: var(--text-tertiary); font-weight: 500; transition: color var(--duration-fast); }
.step.active .step-num { background: var(--grad-brand); color: #fff; box-shadow: 0 0 0 4px rgba(76,175,80,0.15); }
.step.active .step-txt { color: var(--text-primary); font-weight: 600; }
.step.done .step-num { background: var(--brand-600); color: #fff; }
.step-line { flex: 1; height: 2px; background: var(--gray-200); border-radius: 2px; position: relative; overflow: hidden; }
.step-line.filled::after {
  content: ''; position: absolute; inset: 0; background: var(--grad-brand);
  animation: barGrow 500ms var(--ease-out);
}

.diag-layout {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
}

/* ---- 上传区 ---- */
.upload-card { padding: 24px; }
.drop-zone {
  border: 2px dashed var(--gray-300);
  padding: 48px 24px; text-align: center; cursor: pointer;
  min-height: 300px; display: flex; align-items: center; justify-content: center;
  margin-bottom: 16px; background: var(--gray-50);
  border-radius: var(--radius-md); transition: all var(--duration-normal) var(--ease-out);
  position: relative; overflow: hidden;
}
.drop-zone.dragging {
  border-color: var(--brand-500); background: rgba(46,125,50,0.04);
  box-shadow: 0 0 0 4px rgba(46,125,50,0.08);
  transform: scale(1.01);
}
.drop-zone.has-file { border-style: solid; border-color: var(--gray-200); background: #fff; }
.drop-zone:hover:not(.has-file) { border-color: var(--brand-400); }
.drop-zone.scanning { border-color: var(--brand-500); }

.scan-line {
  position: absolute; left: 0; right: 0; height: 3px; z-index: 3;
  background: linear-gradient(90deg, transparent, var(--brand-400), var(--brand-600), var(--brand-400), transparent);
  box-shadow: 0 0 12px rgba(76,175,80,0.6);
  animation: scanMove 1.6s ease-in-out infinite;
}
@keyframes scanMove {
  0%, 100% { top: 5%; }
  50% { top: 95%; }
}
.scan-overlay {
  position: absolute; inset: 0; z-index: 2; display: flex; align-items: flex-end; justify-content: center;
  background: linear-gradient(180deg, transparent 60%, rgba(15,43,26,0.55));
  padding-bottom: 16px;
}
.so-text { color: #fff; font-size: 13px; font-weight: 600; letter-spacing: 1px; }
.preview-img { max-width: 100%; max-height: 320px; object-fit: contain; border-radius: 8px; transition: filter var(--duration-normal); }
.preview-img.dim { filter: brightness(0.85); }

.drop-icon-wrap {
  width: 64px; height: 64px; border-radius: 16px; background: var(--brand-50);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px; color: var(--brand-700);
  transition: transform var(--duration-normal) var(--ease-spring);
}
.drop-zone:hover:not(.has-file) .drop-icon-wrap { transform: translateY(-4px); }
.drop-text { font-size: 14px; color: var(--text-secondary); }
.drop-link { color: var(--brand-700); font-weight: 600; }
.drop-hint { font-size: 11px; color: var(--text-tertiary); margin-top: 6px; }

.upload-actions { display: flex; gap: 10px; }

/* ---- 结果区 ---- */
.result-card { padding: 24px; display: flex; flex-direction: column; }
.result-empty {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 40px 20px; text-align: center;
}
.result-error {
  display: grid; grid-template-columns: 44px 1fr auto; align-items: center; gap: 12px;
  padding: 18px; border: 1px solid #fecaca; background: #fef2f2;
  border-radius: var(--radius-md); color: #991b1b;
}
.error-icon {
  width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
  background: #fee2e2; color: #dc2626;
}
.error-title { font-size: 15px; font-weight: 800; color: #991b1b; margin-bottom: 4px; }
.error-desc { font-size: 12px; line-height: 1.6; color: #b91c1c; }
.empty-illustration { opacity: 0.5; margin-bottom: 16px; }
.empty-text { font-size: 14px; color: var(--text-secondary); font-weight: 500; }
.empty-sub  { font-size: 12px; color: var(--text-tertiary); margin-top: 6px; }

.result-content { display: flex; flex-direction: column; gap: 16px; }

/* ---- 结果 Banner ---- */
.result-banner {
  padding: 18px; border-radius: var(--radius-md);
  background: linear-gradient(135deg, rgba(46,125,50,0.06), rgba(29,78,216,0.04));
  border: 1px solid rgba(46,125,50,0.1);
  position: relative; overflow: hidden;
}
.result-banner::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
  background: var(--accent, var(--brand-600));
}
.rb-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.rb-tags { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.rb-type-tag {
  font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 6px;
}
.rtt-disease { background: #fff3e0; color: #e65100; }
.rtt-pest { background: #ffebee; color: #c62828; }
.rb-sev {
  font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 999px;
}
.rb-sev-high { background: #fee2e2; color: #b91c1c; }
.rb-sev-mid  { background: #fef3c7; color: #b45309; }
.rb-sev-low  { background: #dcfce7; color: #15803d; }
.rb-source { font-size: 10px; color: var(--text-tertiary); background: var(--gray-100); padding: 2px 8px; border-radius: 999px; }
.rb-name { font-size: 22px; font-weight: 800; color: var(--text-primary); margin-bottom: 4px; letter-spacing: -0.3px; }
.rb-sci { font-size: 11px; color: var(--text-tertiary); font-style: italic; margin-bottom: 12px; }
.rb-conf-wrap { display: flex; align-items: center; gap: 10px; }
.rb-conf-bar {
  flex: 1; height: 8px; background: var(--gray-100); border-radius: 4px; overflow: hidden;
}
.rb-conf-fill {
  height: 100%; border-radius: 4px;
  background: linear-gradient(90deg, var(--brand-500), var(--brand-700));
  transition: width 0.8s var(--ease-out);
  box-shadow: 0 0 8px rgba(76,175,80,0.4);
}
.rb-conf-val { font-size: 12px; color: var(--text-secondary); font-weight: 600; white-space: nowrap; }

.trust-panel {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
}
.trust-item {
  padding: 10px 12px; background: #fff; border: 1px solid var(--gray-200);
  border-radius: var(--radius-sm);
}
.trust-label {
  font-size: 10px; font-weight: 700; color: var(--text-tertiary); margin-bottom: 4px;
}
.trust-value {
  font-size: 12px; font-weight: 700; color: var(--text-primary); line-height: 1.5;
}
.trust-high { color: var(--brand-700); }
.trust-mid { color: var(--color-wheat); }
.trust-low { color: var(--color-cotton); }

/* ---- Top3 候选病害 ---- */
.candidates-box {
  padding: 14px; background: var(--gray-50); border-radius: var(--radius-md);
  border: 1px solid var(--gray-200);
}
.cb-title {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 700; color: var(--text-secondary); margin-bottom: 10px;
}
.cb-list { display: flex; flex-direction: column; gap: 6px; }
.cb-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px; background: #fff; border-radius: 8px;
  border: 1px solid var(--gray-100); cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}
.cb-item:hover { border-color: var(--brand-200); transform: translateX(2px); box-shadow: var(--shadow-sm); }
.cb-item-top { background: linear-gradient(135deg, #f0fdf4, #ecfdf5); border-color: var(--brand-200); }
.cb-rank {
  width: 20px; height: 20px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: var(--text-tertiary);
  background: var(--gray-100); flex-shrink: 0;
}
.cb-item-top .cb-rank { background: var(--brand-600); color: #fff; }
.cb-info { flex-shrink: 0; min-width: 90px; }
.cb-name { font-size: 12px; font-weight: 600; color: var(--text-primary); }
.cb-crop { font-size: 10px; color: var(--text-tertiary); }
.cb-bar-wrap { flex: 1; height: 5px; background: var(--gray-100); border-radius: 3px; overflow: hidden; }
.cb-bar { height: 100%; border-radius: 3px; transition: width 0.6s var(--ease-out); }
.cb-pct { font-size: 11px; font-weight: 700; color: var(--text-secondary); width: 44px; text-align: right; font-variant-numeric: tabular-nums; }

/* ---- 元数据网格 ---- */
.meta-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
}
.meta-item {
  padding: 10px 12px; background: var(--gray-50);
  border-radius: var(--radius-sm); border: 1px solid var(--gray-200);
}
.meta-label { font-size: 10px; font-weight: 600; color: var(--text-tertiary); margin-bottom: 4px; letter-spacing: 0.3px; }
.meta-value { font-size: 12px; font-weight: 600; color: var(--text-primary); }

/* ---- 防治时间轴 ---- */
.treat-timeline {
  padding: 14px; background: linear-gradient(135deg, #f0fdf4, #f8fffc);
  border-radius: var(--radius-md); border: 1px solid var(--brand-200);
}
.tt-title {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 700; color: var(--brand-700); margin-bottom: 12px;
}
.tl-content { padding-left: 4px; }
.tl-head { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap; }
.tl-stage { font-size: 12px; font-weight: 700; color: var(--text-primary); }
.tl-stage-now { color: var(--brand-700); }
.tl-time { font-size: 10px; color: var(--text-tertiary); padding: 1px 7px; background: var(--gray-100); border-radius: 999px; }
.tl-time-now { background: var(--brand-100); color: var(--brand-800); font-weight: 600; }
.tl-desc { font-size: 11px; color: var(--text-secondary); line-height: 1.6; }

/* ---- 操作按钮 ---- */
.result-actions { display: flex; gap: 8px; margin-top: 4px; }

/* ---- 骨架屏 ---- */
.result-skeleton { display: flex; flex-direction: column; gap: 12px; padding: 4px 0; }
.skel-banner { height: 110px; border-radius: var(--radius-md); }
.skel-line { height: 14px; border-radius: 4px; }

.result-time-badge { background: #dcfce7; color: #15803d; }

/* ---- 结果字段 ---- */
.result-fields { display: flex; flex-direction: column; gap: 10px; }
.rf-item {
  padding: 14px; background: var(--gray-50); border-radius: var(--radius-sm);
  border: 1px solid var(--gray-200);
}
.rf-highlight {
  background: #fffbeb; border-color: #fde68a; border-left: 3px solid var(--color-wheat);
}
.rf-label {
  font-size: 10px; font-weight: 700; color: var(--text-tertiary);
  text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px;
}
.rf-value { font-size: 13px; color: var(--text-primary); line-height: 1.7; }

/* ---- 旋转动画 ---- */
.spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

@media (max-width: 800px) {
  .diag-layout, .trust-panel { grid-template-columns: 1fr; }
  .result-error { grid-template-columns: 1fr; }
}
</style>
