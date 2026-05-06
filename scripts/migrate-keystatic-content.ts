import { access, mkdir, rm, writeFile } from 'node:fs/promises'
import path from 'node:path'

import { collectLegacyPosts } from './lib/legacy-content.js'

async function main() {
  const projectRoot = process.cwd()
  const outputRoot = path.join(projectRoot, 'src', 'content', 'posts')
  const posts = await collectLegacyPosts(projectRoot)
  const force = process.argv.includes('--force')

  if (await exists(outputRoot)) {
    if (!force) {
      throw new Error(
        `${path.relative(projectRoot, outputRoot)} already exists. Pass --force to replace migrated content.`
      )
    }

    await rm(outputRoot, { force: true, recursive: true })
  }

  for (const post of posts) {
    const outputFile = path.join(outputRoot, `${post.path}.md`)
    await mkdir(path.dirname(outputFile), { recursive: true })
    await writeFile(outputFile, formatPost(post), 'utf8')
  }

  console.log(`Wrote ${posts.length} Keystatic posts to ${path.relative(projectRoot, outputRoot)}`)
}

async function exists(filePath: string) {
  try {
    await access(filePath)
    return true
  } catch {
    return false
  }
}

type LegacyPost = Awaited<ReturnType<typeof collectLegacyPosts>>[number]

function formatPost(post: LegacyPost) {
  const frontmatter = toYaml({
    title: post.title,
    path: post.path,
    section: post.section,
    excerpt: post.excerpt ?? '',
    tags: post.tags,
    publishedAt: post.publishedAt,
    isPage: post.isPage,
    pageIndex: post.pageIndex ?? 999,
    cover: post.cover ?? '',
    headerBgColor: post.headerBgColor ?? '',
    headerColor: post.headerColor ?? '',
    sourceFile: post.sourceFile
  })

  return `---\n${frontmatter}---\n\n${post.content.trim()}\n`
}

function toYaml(values: Record<string, string | number | boolean | string[]>) {
  return Object.entries(values)
    .map(([key, value]) => {
      if (Array.isArray(value)) {
        if (value.length === 0) {
          return `${key}: []\n`
        }

        return `${key}:\n${value.map((item) => `  - ${quoteString(item)}`).join('\n')}\n`
      }

      if (typeof value === 'string') {
        return `${key}: ${formatString(value)}\n`
      }

      return `${key}: ${value}\n`
    })
    .join('')
}

function formatString(value: string) {
  if (value.includes('\n')) {
    return `|-\n${value
      .split('\n')
      .map((line) => `  ${line}`)
      .join('\n')}`
  }

  return quoteString(value)
}

function quoteString(value: string) {
  return JSON.stringify(value)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
