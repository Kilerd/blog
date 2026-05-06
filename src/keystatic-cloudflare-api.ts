// @ts-expect-error Cloudflare provides this virtual module at Worker runtime.
import { env } from 'cloudflare:workers'
import { makeHandler } from '@keystatic/astro/api'
import type { APIContext } from 'astro'
import keystaticConfig from '../keystatic.config'

export const prerender = false

const handler = makeHandler({
  config: keystaticConfig
})

export const ALL = (context: APIContext) => {
  const compatContext = {
    ...context,
    locals: {
      runtime: {
        env
      }
    }
  } as unknown as APIContext

  return handler(compatContext)
}

export const all = ALL
