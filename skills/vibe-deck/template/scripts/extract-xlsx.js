#!/usr/bin/env node
/**
 * Excel → JS data extraction scaffold.
 *
 * Usage:
 *   node scripts/extract-xlsx.js <input.xlsx> [--sheet "Sheet1"] [--output src/data/mydata.js]
 *
 * Without --sheet: prints structure summary of all sheets
 * With --sheet: prints first 5 rows as JSON for inspection
 * With --output: writes full sheet data to JS file
 */

import { readFileSync, writeFileSync } from 'fs'
import { read, utils } from 'xlsx'

const args = process.argv.slice(2)
const filePath = args[0]

if (!filePath) {
  console.log('Usage: node scripts/extract-xlsx.js <input.xlsx> [--sheet "name"] [--output path]')
  console.log('')
  console.log('Without --sheet: prints structure summary of all sheets')
  console.log('With --sheet: prints first 5 rows as JSON for inspection')
  process.exit(0)
}

const sheetFlag = args.indexOf('--sheet')
const targetSheet = sheetFlag >= 0 ? args[sheetFlag + 1] : null

const outputFlag = args.indexOf('--output')
const outputPath = outputFlag >= 0 ? args[outputFlag + 1] : null

const buf = readFileSync(filePath)
const wb = read(buf, { type: 'buffer' })

if (!targetSheet) {
  console.log(`\nFile: ${filePath}`)
  console.log(`   Sheets: ${wb.SheetNames.length}\n`)

  for (const name of wb.SheetNames) {
    const ws = wb.Sheets[name]
    const data = utils.sheet_to_json(ws, { header: 1 })
    const headers = data[0] || []
    console.log(`  Sheet: "${name}"`)
    console.log(`    Rows: ${data.length - 1} (excluding header)`)
    console.log(`    Columns: ${headers.join(' | ')}`)
    console.log('')
  }
  console.log('Next step: run with --sheet "SheetName" to inspect data')
} else {
  const ws = wb.Sheets[targetSheet]
  if (!ws) {
    console.error(`Sheet "${targetSheet}" not found. Available: ${wb.SheetNames.join(', ')}`)
    process.exit(1)
  }
  const data = utils.sheet_to_json(ws)
  console.log(`\nSheet "${targetSheet}" — ${data.length} rows\n`)
  console.log('First 5 rows:')
  console.log(JSON.stringify(data.slice(0, 5), null, 2))

  if (outputPath) {
    const content = `// Auto-extracted from ${filePath} → "${targetSheet}"\n// ${new Date().toISOString()}\n\nexport default ${JSON.stringify(data, null, 2)}\n`
    writeFileSync(outputPath, content)
    console.log(`\nWritten to ${outputPath}`)
  }
}
