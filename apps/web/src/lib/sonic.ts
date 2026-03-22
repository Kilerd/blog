const apiBase = (import.meta.env.SONICJS_API_URL ?? 'http://127.0.0.1:8787').replace(/\/$/, '')

export interface PostData {
  title: string
  slug: string
  path: string
  section: string
  excerpt?: string
  content: string
  tags?: string
  publishedAt: string
  isPage?: boolean
  pageIndex?: number
  cover?: string
  headerBgColor?: string
  headerColor?: string
  sourceFile?: string
}

export interface PostRecord {
  id: string
  title: string
  slug: string
  status: string
  data: PostData
  created_at: number
  updated_at: number
}

interface SonicResponse<T> {
  data: T
  meta: {
    count: number
    timestamp: string
  }
}

export function normalizeContentPath(pathname: string) {
  return pathname.replace(/^\/+|\/+$/g, '')
}

async function fetchSonic<T>(pathname: string) {
  const response = await fetch(`${apiBase}${pathname}`, {
    headers: {
      Accept: 'application/json'
    }
  })

  if (!response.ok) {
    throw new Error(`SonicJS request failed: ${response.status} ${response.statusText}`)
  }

  return response.json() as Promise<SonicResponse<T>>
}

export async function getPublishedPosts() {
  const response = await fetchSonic<PostRecord[]>(
    '/api/collections/posts/content?limit=100&filter[status][equals]=published'
  )

  return response.data
}
