import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'

export interface LegacyPostRecord {
  title: string
  slug: string
  path: string
  section: string
  tags: string[]
  publishedAt: string
  template: string
  isPage: boolean
  pageIndex: number | null
  excerpt: string | null
  content: string
  cover: string | null
  headerBgColor: string | null
  headerColor: string | null
  sourceFile: string
}

export async function collectLegacyPosts(projectRoot: string) {
  const dataRoot = path.join(projectRoot, 'data')
  const filePaths = await walkMarkdownFiles(dataRoot)
  const posts = await Promise.all(filePaths.map((filePath) => parseLegacyFile(projectRoot, filePath)))

  return posts.sort((left, right) => {
    return new Date(right.publishedAt).getTime() - new Date(left.publishedAt).getTime()
  })
}

async function walkMarkdownFiles(directory: string): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true })
  const files = await Promise.all(
    entries.map(async (entry) => {
      const entryPath = path.join(directory, entry.name)

      if (entry.isDirectory()) {
        return walkMarkdownFiles(entryPath)
      }

      return entry.isFile() && entry.name.endsWith('.md') ? [entryPath] : []
    })
  )

  return files.flat()
}

async function parseLegacyFile(projectRoot: string, filePath: string): Promise<LegacyPostRecord> {
  const raw = await readFile(filePath, 'utf8')
  const lines = raw.split(/\r?\n/)
  const frontMatter = new Map<string, string>()

  let cursor = 0
  while (cursor < lines.length) {
    const line = lines[cursor]
    if (!/^\s*-\s/.test(line)) {
      break
    }

    const assignment = line.replace(/^\s*-\s/, '')
    const separatorIndex = assignment.indexOf('=')
    if (separatorIndex === -1) {
      break
    }

    const key = assignment.slice(0, separatorIndex).trim()
    const value = assignment.slice(separatorIndex + 1).trim()
    frontMatter.set(key, value)
    cursor += 1
  }

  while (cursor < lines.length && lines[cursor].trim() === '') {
    cursor += 1
  }

  const body = lines.slice(cursor).join('\n').trim()
  const [excerptPart] = body.split('<!--more-->')
  const excerpt = body.includes('<!--more-->') ? excerptPart.trim() : null
  const content = body.replace(/\n?<!--more-->\n?/g, '\n\n').trim()
  const contentPath = normalizePath(frontMatter.get('url') ?? '')
  const slug = contentPath.split('/').pop() ?? contentPath
  const tags = (frontMatter.get('tags') ?? '')
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)

  if (!frontMatter.get('title') || !contentPath || !frontMatter.get('datetime')) {
    throw new Error(`Missing required legacy front matter in ${filePath}`)
  }

  return {
    title: frontMatter.get('title') ?? '',
    slug,
    path: contentPath,
    section: path.basename(path.dirname(filePath)),
    tags,
    publishedAt: frontMatter.get('datetime') ?? '',
    template: frontMatter.get('template') ?? 'article.html',
    isPage: parseBoolean(frontMatter.get('page')),
    pageIndex: frontMatter.has('page_index') ? Number(frontMatter.get('page_index')) : null,
    excerpt,
    content,
    cover: nullableString(frontMatter.get('cover')),
    headerBgColor: nullableString(frontMatter.get('header_bg_color')),
    headerColor: nullableString(frontMatter.get('header_color')),
    sourceFile: path.relative(projectRoot, filePath)
  }
}

function normalizePath(value: string) {
  return value.replace(/^\/+|\/+$/g, '')
}

function parseBoolean(value: string | undefined) {
  return value === 'true'
}

function nullableString(value: string | undefined) {
  if (!value) {
    return null
  }

  return value.trim() || null
}

export async function writeLegacyPosts(projectRoot: string, posts: LegacyPostRecord[]) {
  const outputDir = path.join(projectRoot, 'generated', 'content')
  const outputFile = path.join(outputDir, 'posts.json')
  await mkdir(outputDir, { recursive: true })
  await writeFile(outputFile, `${JSON.stringify(posts, null, 2)}\n`, 'utf8')
  return outputFile
}
