import { readFileSync } from 'node:fs'
import { defineConfig } from 'astro/config'
import cloudflare from '@astrojs/cloudflare'
import markdoc from '@astrojs/markdoc'
import react from '@astrojs/react'
import keystatic from '@keystatic/astro'
import tailwindcss from '@tailwindcss/vite'

const isKeystaticDev = process.env.KEYSTATIC_DEV === 'true'
const publicKeystaticGithubAppSlug =
  process.env.PUBLIC_KEYSTATIC_GITHUB_APP_SLUG ?? readWranglerVar('PUBLIC_KEYSTATIC_GITHUB_APP_SLUG')
const viteEnvDefine = publicKeystaticGithubAppSlug
  ? {
      'import.meta.env.PUBLIC_KEYSTATIC_GITHUB_APP_SLUG': JSON.stringify(publicKeystaticGithubAppSlug)
    }
  : {}

function readWranglerVar(name) {
  try {
    const wranglerToml = readFileSync(new URL('./wrangler.toml', import.meta.url), 'utf8')
    return wranglerToml.match(new RegExp(`^${name}\\s*=\\s*"([^"]+)"`, 'm'))?.[1]
  } catch {
    return undefined
  }
}

export default defineConfig({
  output: 'server',
  adapter: isKeystaticDev ? undefined : cloudflare(),
  integrations: [react(), markdoc(), keystatic()],
  devToolbar: {
    enabled: false
  },
  vite: {
    define: viteEnvDefine,
    plugins: [tailwindcss()]
  },
  server: {
    host: true,
    port: 4321
  }
})
