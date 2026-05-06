import { defineConfig } from 'astro/config'
import cloudflare from '@astrojs/cloudflare'
import markdoc from '@astrojs/markdoc'
import react from '@astrojs/react'
import keystatic from '@keystatic/astro'

const isKeystaticDev = process.env.KEYSTATIC_DEV === 'true'
const skipKeystatic = process.env.SKIP_KEYSTATIC === 'true'
const keystaticIntegrations = skipKeystatic ? [] : [react(), markdoc(), keystatic()]

export default defineConfig({
  output: 'server',
  adapter: isKeystaticDev ? undefined : cloudflare(),
  integrations: keystaticIntegrations,
  server: {
    host: true,
    port: 4321
  }
})
