import { defineConfig } from 'vite'
import { readFileSync, existsSync } from 'fs'
import { resolve, extname } from 'path'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

const MIME = {
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp',
}

/**
 * Replaces string literals like "/logo.svg" in JS source with inline data URIs
 * so that public/ assets are embedded in the single-file build.
 */
function inlinePublicAssets() {
  let publicDir
  return {
    name: 'inline-public-assets',
    enforce: 'pre',
    configResolved(config) {
      // When publicDir is false, resolve manually to ./public
      publicDir = config.publicDir || resolve(config.root, 'public')
    },
    transform(code, id) {
      if (!publicDir || !id.match(/\.(jsx?|tsx?)$/)) return null
      // Match string literals referencing public assets: "/something.ext"
      const replaced = code.replace(/(['"`])(\/[\w./-]+\.(svg|png|jpe?g|gif|webp))\1/g, (match, quote, path) => {
        const ext = extname(path).toLowerCase()
        const mime = MIME[ext]
        if (!mime) return match
        const file = resolve(publicDir, path.slice(1))
        if (!existsSync(file)) return match
        const data = readFileSync(file)
        const b64 = data.toString('base64')
        return `${quote}data:${mime};base64,${b64}${quote}`
      })
      if (replaced !== code) return { code: replaced, map: null }
      return null
    },
  }
}

export default defineConfig({
  plugins: [react(), tailwindcss(), inlinePublicAssets(), viteSingleFile()],
  publicDir: false,
  build: {
    outDir: 'dist-single',
    assetsInlineLimit: Infinity,
  },
})
