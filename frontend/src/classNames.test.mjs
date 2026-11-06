import assert from 'node:assert/strict'
import test from 'node:test'
import { readFileSync } from 'node:fs'
import { isDenseIndexMap, resolveModelLabel } from './classNames.js'

const shipped = JSON.parse(readFileSync(new URL('../../models/class_names.json', import.meta.url), 'utf8'))

test('legacy class_10 is not looked up by the model index', () => {
  assert.equal(isDenseIndexMap(shipped), false)
  assert.equal(resolveModelLabel(2, 'class_10', shipped), '水稻褐斑病_轻')
  assert.notEqual(resolveModelLabel(2, 'class_10', shipped), shipped[2])
  assert.equal(resolveModelLabel(2, '水稻褐斑病_轻', shipped), '水稻褐斑病_轻')
  assert.equal(resolveModelLabel(59, 'class_75', shipped), '马铃薯早疫病')
})

test('dense map follows the model index', () => {
  const mapping = { 0: '苹果黑星病', 1: '玉米锈病', 2: '葡萄黑腐病' }
  assert.equal(isDenseIndexMap(mapping), true)
  assert.equal(resolveModelLabel(2, 'class_10', mapping), '葡萄黑腐病')
  assert.equal(resolveModelLabel(-1, '非农作物', mapping), '非农作物')
})
