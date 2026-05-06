import { parse as parseYaml } from 'yaml'

export interface PostData {
  title: string
  slug: string
  path: string
  section: string
  excerpt?: string
  content: string
  tags: string[]
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
  status: 'published'
  data: PostData
  created_at: number
  updated_at: number
}

interface PostFrontmatter {
  title?: unknown
  path?: unknown
  section?: unknown
  excerpt?: unknown
  tags?: unknown
  publishedAt?: unknown
  isPage?: unknown
  pageIndex?: unknown
  cover?: unknown
  headerBgColor?: unknown
  headerColor?: unknown
  sourceFile?: unknown
}

const postModules = import.meta.glob<string>('../content/posts/**/*.md', {
  eager: true,
  import: 'default',
  query: '?raw'
})

export function normalizeContentPath(pathname: string) {
  return pathname.replace(/^\/+|\/+$/g, '')
}

export async function getPublishedPosts(): Promise<PostRecord[]> {
  return Object.entries(postModules).map(([filePath, raw]) => {
    const { data, body } = parseMarkdownFile(filePath, raw)
    const path = normalizeContentPath(readString(data.path, inferPathFromFile(filePath)))
    const slug = path.split('/').pop() ?? path

    return {
      id: inferPathFromFile(filePath),
      title: readString(data.title, slug),
      slug,
      status: 'published',
      data: {
        title: readString(data.title, slug),
        slug,
        path,
        section: readString(data.section, 'uncategorized'),
        content: body,
        excerpt: readString(data.excerpt) || undefined,
        tags: readStringArray(data.tags),
        publishedAt: readString(data.publishedAt, new Date(0).toISOString()),
        isPage: readBoolean(data.isPage),
        pageIndex: readNumber(data.pageIndex, 999),
        cover: readString(data.cover) || undefined,
        headerBgColor: readString(data.headerBgColor) || undefined,
        headerColor: readString(data.headerColor) || undefined,
        sourceFile: readString(data.sourceFile) || undefined
      },
      created_at: 0,
      updated_at: 0
    }
  })
}

function parseMarkdownFile(filePath: string, raw: string) {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/)

  if (!match) {
    throw new Error(`Missing frontmatter in ${filePath}`)
  }

  return {
    data: parseYaml(match[1]) as PostFrontmatter,
    body: match[2].trim()
  }
}

function inferPathFromFile(filePath: string) {
  return filePath
    .replace(/^..\/content\/posts\//, '')
    .replace(/\.md$/, '')
}

function readString(value: unknown, fallback = '') {
  return typeof value === 'string' ? value : fallback
}

function readStringArray(value: unknown) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).filter(Boolean)
  }

  if (typeof value === 'string') {
    return value
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean)
  }

  return []
}

function readBoolean(value: unknown) {
  return value === true
}

function readNumber(value: unknown, fallback: number) {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}
