/** 纯数字入场。尊重 prefers-reduced-motion，只改文本节点。 */
export const vCount = {
  mounted(el) {
    const original = (el.textContent || '').trim()
    const comma = original.includes(',')
    const numeric = original.replace(/,/g, '')
    if (!/^-?\d+(\.\d+)?$/.test(numeric)) return
    const target = Number(numeric)
    const decimals = numeric.includes('.') ? numeric.split('.')[1].length : 0
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const paint = (value) => {
      const fixed = decimals ? value.toFixed(decimals) : String(Math.round(value))
      el.textContent = comma || target >= 1000
        ? Number(fixed).toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
          })
        : fixed
    }
    if (reduce || target === 0) {
      paint(target)
      return
    }
    const start = performance.now()
    const duration = 900
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      paint(target * eased)
      if (t < 1) requestAnimationFrame(tick)
      else paint(target)
    }
    paint(0)
    requestAnimationFrame(tick)
  },
}
