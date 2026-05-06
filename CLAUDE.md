# CLAUDE.md

This repository hosts the Cloudflare-native version of the blog.

## Stack

- Root app: Astro SSR frontend running on Cloudflare Workers
- `src/content/posts/`: active Markdown posts/pages managed by Keystatic
- `keystatic.config.ts`: Keystatic schema and local storage configuration
- `data/`: legacy Markdown source retained for backup and one-time migration

## Main Commands

```bash
pnpm install

# Web
pnpm dev
pnpm build
pnpm check

# One-time legacy migration
pnpm migrate:legacy-content
```

## Content Flow

1. Keystatic edits Markdown files under `src/content/posts/`
2. `src/lib/posts.ts` imports Markdown files directly and parses YAML frontmatter
3. That module normalizes content entries into the blog's existing post shape
4. `data/` remains a legacy backup and can be migrated with `pnpm migrate:legacy-content`

## URL Rules

- Migrated records keep the old `url` value as `path`
- Frontend routes remain on `/{path}`
- Existing page slugs such as `/about`, `/blogroll`, and `/portfolios` stay unchanged

## Important Files

- `keystatic.config.ts`: CMS schema for file-backed editing
- `src/lib/posts.ts`: Markdown reader and normalizer
- `src/pages/index.astro`: homepage and pagination
- `src/pages/[...slug].astro`: article and page route
- `src/components/Comments.astro`: Gitalk integration
- `public/statics/style.css`: site styling
- `scripts/lib/legacy-content.ts`: parser for the old Markdown front matter format
- `scripts/migrate-keystatic-content.ts`: one-time migration from `data/` to Keystatic Markdown

## Notes

- `data/` is a backup/migration source, so it should not be deleted casually.
- `src/content/posts/` is now the active content source.
- The old Staple templates, config, and deployment files have been removed from this repo.
- Gitalk keeps compatibility with old issue IDs by using the legacy path format.
