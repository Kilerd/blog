import { defineConfig } from 'astro/config'
import cloudflare from '@astrojs/cloudflare'
import markdoc from '@astrojs/markdoc'
import react from '@astrojs/react'
import keystatic from '@keystatic/astro'
import tailwindcss from '@tailwindcss/vite'

const isKeystaticDev = process.env.KEYSTATIC_DEV === 'true'

export default defineConfig({
  output: 'server',
  adapter: isKeystaticDev ? undefined : cloudflare(),
  integrations: [react(), markdoc(), keystatic()],
  devToolbar: {
    enabled: false
  },
  vite: {
    plugins: [tailwindcss()]
  },
  server: {
    host: true,
    port: 4321
  }
})
