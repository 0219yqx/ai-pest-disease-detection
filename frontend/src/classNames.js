/**
 * 与 backend/ai/class_names.py 的 resolve_label 保持一致。
 *
 * models/class_names.json 是唯一的类别名来源。
 * - 有空缺的遗留表：权重里的名字是 class_N，用 N 查表，不能用模型下标。
 *   （class_10 的模型下标是 2，下标 2 在表里是另一种病。）
 * - 清洗重训后的表：键是 0..N-1，与 sorted(train 文件夹) 一致，用模型下标查表。
 */

const CLASS_N = /^class_(\d+)$/

export function isDenseIndexMap(mapping) {
  if (!mapping || typeof mapping !== 'object') return false
  const keys = Object.keys(mapping)
  if (!keys.length) return false
  const nums = keys.map((key) => Number(key))
  if (nums.some((key) => !Number.isInteger(key))) return false
  nums.sort((a, b) => a - b)
  return nums.every((key, index) => key === index)
}

export function resolveModelLabel(index, rawName, mapping) {
  const table = mapping || {}
  const raw = rawName == null ? '' : String(rawName).trim()
  const match = CLASS_N.exec(raw)
  const folderId = match ? Number(match[1]) : null
  const dense = isDenseIndexMap(table)
  const indexOk = Number.isInteger(index) && index >= 0 && Object.prototype.hasOwnProperty.call(table, String(index))

  if (dense && indexOk) return table[index]
  if (folderId !== null && !dense && Object.prototype.hasOwnProperty.call(table, String(folderId))) {
    return table[folderId]
  }
  if (raw) return raw
  if (index !== undefined && index !== null && index !== '') return `class_${index}`
  return ''
}
