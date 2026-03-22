import path from 'node:path'

import { collectLegacyPosts, writeLegacyPosts } from './lib/legacy-content.js'

async function main() {
  const projectRoot = process.cwd()
  const posts = await collectLegacyPosts(projectRoot)
  const outputFile = await writeLegacyPosts(projectRoot, posts)

  console.log(`Wrote ${posts.length} posts to ${path.relative(projectRoot, outputFile)}`)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
