/** ECharts 色板，与 style.css 的麦田纸面令牌一致。 */
export const ink = '#2A2118'
export const muted = '#6E6256'
export const dim = '#5E5348'
export const line = '#E4D8C8'
export const paper = '#F7F3EB'
export const leaf = '#1F4A34'
export const leaf2 = '#3E6B52'
export const straw = '#A67C3D'
export const straw2 = '#C4A574'
export const clay = '#8C4E32'
export const soil = '#3E2E22'

export const series = [leaf, straw, leaf2, straw2, clay, soil]

export const reducedMotion =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

export const chartMotion = reducedMotion
  ? { animation: false, backgroundColor: 'transparent' }
  : {
      animation: true,
      animationDuration: 700,
      animationEasing: 'cubicOut',
      backgroundColor: 'transparent',
    }

export const tooltip = {
  backgroundColor: paper,
  borderColor: line,
  borderWidth: 1,
  borderRadius: 2,
  textStyle: { color: ink, fontSize: 14 },
  padding: [10, 12],
  extraCssText: 'box-shadow: none;',
}

export function rgba(hex, a) {
  const h = hex.replace('#', '')
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  return `rgba(${r},${g},${b},${a})`
}
