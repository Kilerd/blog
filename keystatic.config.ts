import { collection, config, fields } from '@keystatic/core'

export default config({
  storage: {
    kind: 'local'
  },
  ui: {
    brand: {
      name: 'kilerd blog'
    }
  },
  collections: {
    posts: collection({
      label: 'Posts',
      slugField: 'title',
      path: 'src/content/posts/**',
      columns: ['title', 'section', 'publishedAt'],
      format: {
        contentField: 'content'
      },
      schema: {
        title: fields.slug({
          name: {
            label: 'Title'
          }
        }),
        path: fields.text({
          label: 'Route path',
          description: 'URL path without the leading slash.'
        }),
        section: fields.text({
          label: 'Section'
        }),
        excerpt: fields.text({
          label: 'Excerpt',
          multiline: true
        }),
        tags: fields.array(fields.text({ label: 'Tag' }), {
          label: 'Tags',
          itemLabel: (props) => props.value || 'Tag'
        }),
        publishedAt: fields.text({
          label: 'Published at',
          description: 'ISO 8601 date/time string. Existing offsets are preserved.'
        }),
        isPage: fields.checkbox({
          label: 'Static page',
          defaultValue: false
        }),
        pageIndex: fields.integer({
          label: 'Page index',
          defaultValue: 999
        }),
        cover: fields.text({
          label: 'Cover URL'
        }),
        headerBgColor: fields.text({
          label: 'Header background color'
        }),
        headerColor: fields.text({
          label: 'Header text color'
        }),
        sourceFile: fields.text({
          label: 'Original source file'
        }),
        content: fields.markdoc({
          label: 'Content',
          extension: 'md'
        })
      }
    })
  }
})
