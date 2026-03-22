const siteUrl = (import.meta.env.SITE_URL ?? 'https://www.kilerd.me').replace(/\/$/, '')

export const siteConfig = {
  title: '你好，耳先生',
  description: '先生贵姓？耳东陈。好的，这边请，耳先生。',
  siteUrl,
  keywords: [] as string[],
  adsenseAccount: 'ca-pub-9147137464451642',
  monetag: 'd95128f77d10e0303c6e756503a7a959',
  umamiSrc: 'https://umami.xinsoftware.top/script.js',
  umamiWebsiteId: '3741d60f-07c2-48b2-b085-9cb584b38fb5',
  gitalk: {
    clientId: import.meta.env.GITALK_CLIENT_ID ?? '',
    clientSecret: import.meta.env.GITALK_CLIENT_SECRET ?? '',
    repo: import.meta.env.GITALK_REPO ?? 'blog',
    owner: import.meta.env.GITALK_OWNER ?? 'Kilerd',
    admin: (import.meta.env.GITALK_ADMIN ?? 'Kilerd')
      .split(',')
      .map((value: string) => value.trim())
      .filter(Boolean)
  }
}

export function absoluteUrl(pathname: string) {
  const normalized = pathname.startsWith('/') ? pathname : `/${pathname}`
  return `${siteConfig.siteUrl}${normalized}`
}
