import MarkdownIt from 'markdown-it'

const markdown = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: false
})

export function stripMoreMarker(value: string) {
  return value.replace(/\n?<!--more-->\n?/g, '\n\n').trim()
}

export function renderMarkdownToHtml(value: string) {
  return markdown.render(stripMoreMarker(value))
}

export function markdownToPlainText(value: string) {
  return renderMarkdownToHtml(value)
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}
