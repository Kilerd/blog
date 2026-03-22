import { readFile } from 'node:fs/promises'
import path from 'node:path'

import { collectLegacyPosts, writeLegacyPosts } from './lib/legacy-content.js'

interface AuthResponse {
  token: string
}

interface CollectionResponse {
  data: Array<{
    id: string
    name: string
  }>
}

interface ContentResponse {
  data: Array<{
    id: string
    data?: {
      path?: string
    }
  }>
}

const apiBase = (process.env.SONICJS_API_URL ?? 'http://127.0.0.1:8787').replace(/\/$/, '')
const email = process.env.SONICJS_EMAIL ?? 'admin@sonicjs.com'
const password = process.env.SONICJS_PASSWORD ?? 'sonicjs!'

async function main() {
  const projectRoot = process.cwd()
  const posts = await collectLegacyPosts(projectRoot)
  const outputFile = await writeLegacyPosts(projectRoot, posts)

  console.log(`Prepared ${posts.length} legacy posts in ${path.relative(projectRoot, outputFile)}`)

  const token = await loginOrRegister()
  const collectionId = await getCollectionId(token, 'posts')
  const existingContent = await getExistingContent(token)
  const existingByPath = new Map(
    existingContent
      .filter((item) => item.data?.path)
      .map((item) => [item.data?.path as string, item.id])
  )

  let created = 0
  let updated = 0

  for (const post of posts) {
    const payload = {
      title: post.title,
      slug: post.slug,
      status: 'published',
      data: {
        title: post.title,
        slug: post.slug,
        path: post.path,
        section: post.section,
        excerpt: post.excerpt ?? '',
        content: post.content,
        tags: post.tags.join(', '),
        publishedAt: post.publishedAt,
        isPage: post.isPage,
        pageIndex: post.pageIndex ?? 0,
        cover: post.cover ?? '',
        headerBgColor: post.headerBgColor ?? '',
        headerColor: post.headerColor ?? '',
        sourceFile: post.sourceFile
      }
    }

    const existingId = existingByPath.get(post.path)

    if (existingId) {
      await request(`/api/content/${existingId}`, {
        method: 'PUT',
        token,
        body: payload
      })
      updated += 1
      continue
    }

    await request('/api/content', {
      method: 'POST',
      token,
      body: {
        collectionId,
        ...payload
      }
    })
    created += 1
  }

  console.log(`SonicJS import complete: created=${created}, updated=${updated}`)
}

async function loginOrRegister() {
  try {
    const response = await request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: { email, password }
    })

    return response.token
  } catch (error) {
    await request('/auth/register', {
      method: 'POST',
      body: {
        email,
        password,
        username: email.split('@')[0],
        firstName: 'Chen',
        lastName: 'Xin'
      }
    })

    const response = await request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: { email, password }
    })

    return response.token
  }
}

async function getCollectionId(token: string, collectionName: string) {
  const response = await request<CollectionResponse>('/api/collections', {
    method: 'GET',
    token
  })

  const collection = response.data.find((item) => item.name === collectionName)
  if (!collection) {
    throw new Error(
      `Could not find the "${collectionName}" collection. Start the CMS once so SonicJS can auto-sync it.`
    )
  }

  return collection.id
}

async function getExistingContent(token: string) {
  const response = await request<ContentResponse>(
    '/api/collections/posts/content?limit=100&filter[status][equals]=published',
    {
      method: 'GET',
      token
    }
  )

  return response.data
}

async function request<T = unknown>(
  pathname: string,
  options: {
    method: 'GET' | 'POST' | 'PUT'
    token?: string
    body?: unknown
  }
) {
  const response = await fetch(`${apiBase}${pathname}`, {
    method: options.method,
    headers: {
      'Content-Type': 'application/json',
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {})
    },
    body: options.body ? JSON.stringify(options.body) : undefined
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`${options.method} ${pathname} failed: ${response.status} ${text}`)
  }

  if (response.status === 204) {
    return {} as T
  }

  return (await response.json()) as T
}

main().catch(async (error) => {
  console.error(error)

  const generatedFile = path.join(process.cwd(), 'generated', 'content', 'posts.json')
  try {
    const exists = await readFile(generatedFile, 'utf8')
    if (exists) {
      console.error(`Legacy JSON is still available at ${path.relative(process.cwd(), generatedFile)}`)
    }
  } catch {
    // Ignore missing generated file.
  }

  process.exit(1)
})
