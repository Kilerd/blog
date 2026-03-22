import rss from '@astrojs/rss'

import { getArticlePosts, getDescription, getPostHref } from '../lib/content'
import { renderMarkdownToHtml } from '../lib/markdown'
import { siteConfig } from '../lib/site'
import { getPublishedPosts } from '../lib/sonic'

export async function GET() {
  const posts = getArticlePosts(await getPublishedPosts())

  return rss({
    title: siteConfig.title,
    description: siteConfig.description,
    site: siteConfig.siteUrl,
    items: posts.map((post) => ({
      title: post.title,
      description: getDescription(post),
      pubDate: new Date(post.data.publishedAt),
      link: getPostHref(post),
      content: renderMarkdownToHtml(post.data.content)
    }))
  })
}
