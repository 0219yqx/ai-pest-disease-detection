/** 把 /api/history/major-pests 的爬虫字段收成病情地图卡片用的视图字段。 */

function formatWanMu(area) {
  const n = Number(area)
  if (!Number.isFinite(n)) return ''
  const text = Number.isInteger(n) ? String(n) : String(Math.round(n * 10) / 10)
  return `全国年发生面积${text}万亩`
}

function inferTrendDir(text) {
  const s = String(text || '')
  if (/下降|减少|回落|减轻/.test(s)) return 'down'
  if (/增加|上升|加重/.test(s)) return 'up'
  return 'steady'
}

export function normalizeMajorPests(list) {
  const rows = Array.isArray(list) ? list.filter(item => item && typeof item === 'object') : []
  const areas = rows.map(p => Number(p.annual_area)).filter(n => Number.isFinite(n) && n > 0)
  const maxArea = areas.length ? Math.max(...areas) : 0
  return rows.map((raw) => {
    const severity = String(raw.severity ?? raw.henan_severity ?? '').trim()
    const riskZone = String(raw.risk_zone ?? raw.henan_risk_zone ?? '').trim()
    const annual = Number(raw.annual_area)
    const givenRatio = Number(raw.area_ratio)
    const areaRatio = Number.isFinite(givenRatio)
      ? givenRatio
      : (Number.isFinite(annual) && maxArea > 0 ? Math.max(8, Math.round((annual / maxArea) * 100)) : 0)
    const trendText = String(raw.trend_text ?? raw.trend_2026 ?? raw.trend_2025 ?? '').trim()
    const trendDir = raw.trend_dir === 'up' || raw.trend_dir === 'down' || raw.trend_dir === 'steady'
      ? raw.trend_dir
      : inferTrendDir(trendText)
    return {
      ...raw,
      name: raw.name || '未命名',
      crop: raw.crop || '',
      severity,
      risk_zone: riskZone,
      area_ratio: areaRatio,
      area_desc: raw.area_desc || formatWanMu(annual),
      trend_dir: trendDir,
      trend_text: trendText,
    }
  })
}

/** 预警列表：线上字段是 date，卡片读的是 time。 */
export function normalizeAlerts(list) {
  if (!Array.isArray(list)) return []
  return list.filter(item => item && typeof item === 'object').map((a) => ({
    ...a,
    level: a.level || 'mid',
    crop: a.crop || '',
    drug: a.drug || '',
    time: a.time || a.date || '',
  }))
}

export function severityInitial(severity) {
  const text = typeof severity === 'string' ? severity : ''
  return text.charAt(0) || ''
}
