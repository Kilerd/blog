import { markdownToPlainText, renderMarkdownToHtml } from './markdown'
import type { PostRecord } from './sonic'

export function sortPosts(posts: PostRecord[]) {
  return [...posts].sort((left, right) => {
    return new Date(right.data.publishedAt).getTime() - new Date(left.data.publishedAt).getTime()
  })
}

export function getNavigationPages(posts: PostRecord[]) {
  return posts
    .filter((post) => post.data.isPage)
    .sort((left, right) => (left.data.pageIndex ?? 999) - (right.data.pageIndex ?? 999))
}

export function getArticlePosts(posts: PostRecord[]) {
  return sortPosts(posts.filter((post) => !post.data.isPage))
}

export function getPostHref(post: PostRecord) {
  return `/${post.data.path}`.replace(/\/{2,}/g, '/')
}

export function findPostByPath(posts: PostRecord[], pathname: string) {
  const normalized = pathname.replace(/^\/+|\/+$/g, '')
  return posts.find((post) => post.data.path === normalized) ?? null
}

export function getExcerptHtml(post: PostRecord) {
  return post.data.excerpt ? renderMarkdownToHtml(post.data.excerpt) : ''
}

export function getDescription(post: PostRecord) {
  const source = post.data.excerpt || post.data.content
  return markdownToPlainText(source).slice(0, 160)
}

export function getTagList(post: PostRecord) {
  return (post.data.tags ?? '')
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}
