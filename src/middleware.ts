import { defineMiddleware } from 'astro:middleware'

export const onRequest = defineMiddleware(async (context, next) => {
  const { pathname } = new URL(context.request.url)

  if (!import.meta.env.DEV && pathname.startsWith('/api/keystatic')) {
    const { ALL } = await import('./keystatic-cloudflare-api')
    return ALL(context)
  }

  return next()
})
