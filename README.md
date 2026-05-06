# kilerd blog

This repository contains an Astro blog with file-backed content editing through Keystatic.

- `src/content/posts`: Markdown posts and pages managed by Keystatic
- `keystatic.config.ts`: Keystatic schema and local storage configuration
- `data/`: legacy Staple Markdown source retained as a backup and migration source

## Local setup

1. Install dependencies:

   ```bash
   pnpm install
   ```

2. Start the Astro frontend:

   ```bash
   cp .env.example .env
   pnpm dev
   ```

3. Open the Keystatic Admin UI:

   ```text
   http://127.0.0.1:4321/keystatic
   ```

## Content

Keystatic stores posts as Markdown files in `src/content/posts`. Nested paths are supported, so an article with `path: "daily/example"` can live at `src/content/posts/daily/example.md` while keeping the public URL `/daily/example`. The frontend imports these files directly at build/runtime and parses their YAML frontmatter.

The old Staple content under `data/` is no longer the active content source. To re-run the one-time legacy migration into Keystatic Markdown, use:

```bash
pnpm migrate:legacy-content
```

If `src/content/posts` already exists, the migration refuses to overwrite it. Use `pnpm migrate:legacy-content -- --force` only when you intentionally want to replace the Keystatic content from the legacy source.

## Commands

```bash
pnpm dev
pnpm build
pnpm check
```

## Notes

- Legacy URLs stay the same because each post keeps its original `url` value as a `path` frontmatter field.
- Existing images continue to work from `public/statics/`.
- Gitalk configuration is read from `.env` / Cloudflare runtime environment variables.
