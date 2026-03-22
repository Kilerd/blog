import type { CollectionConfig } from '@sonicjs-cms/core'

export default {
  name: 'posts',
  displayName: 'Posts',
  description: 'Migrated posts and pages from the legacy Staple blog',
  icon: '🪨',
  managed: true,
  isActive: true,

  schema: {
    type: 'object',
    properties: {
      title: {
        type: 'string',
        title: 'Title',
        required: true,
        maxLength: 200
      },
      slug: {
        type: 'slug',
        title: 'Slug',
        required: true,
        maxLength: 200
      },
      path: {
        type: 'string',
        title: 'Original Path',
        required: true,
        maxLength: 255,
        helpText: 'Original URI path without the leading slash. This is what Astro routes on.'
      },
      section: {
        type: 'string',
        title: 'Section',
        required: true,
        maxLength: 80
      },
      excerpt: {
        type: 'markdown',
        title: 'Excerpt'
      },
      content: {
        type: 'markdown',
        title: 'Content',
        required: true
      },
      tags: {
        type: 'string',
        title: 'Tags',
        helpText: 'Comma-separated tags from the legacy blog.'
      },
      publishedAt: {
        type: 'datetime',
        title: 'Published At',
        required: true
      },
      isPage: {
        type: 'boolean',
        title: 'Static Page',
        default: false
      },
      pageIndex: {
        type: 'number',
        title: 'Page Index'
      },
      cover: {
        type: 'string',
        title: 'Cover URL'
      },
      headerBgColor: {
        type: 'string',
        title: 'Header Background Color'
      },
      headerColor: {
        type: 'string',
        title: 'Header Text Color'
      },
      sourceFile: {
        type: 'string',
        title: 'Source File',
        helpText: 'Original Markdown file path in this repository.'
      }
    },
    required: ['title', 'slug', 'path', 'section', 'content', 'publishedAt']
  },

  listFields: ['title', 'path', 'section', 'publishedAt', 'status'],
  searchFields: ['title', 'path', 'excerpt', 'content', 'tags'],
  defaultSort: 'publishedAt',
  defaultSortOrder: 'desc'
} satisfies CollectionConfig
