# kilerd blog

This repository contains an Astro blog with GitHub-backed content editing through Keystatic.

- `src/content/posts`: Markdown posts and pages managed by Keystatic
- `keystatic.config.ts`: Keystatic schema and GitHub storage configuration
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

   The admin UI uses Keystatic GitHub mode against `Kilerd/blog`. On first setup, create or connect a GitHub App and copy the generated Keystatic variables into `.env`.

4. Required Keystatic variables:

   ```bash
   KEYSTATIC_GITHUB_CLIENT_ID=
   KEYSTATIC_GITHUB_CLIENT_SECRET=
   KEYSTATIC_SECRET=
   PUBLIC_KEYSTATIC_GITHUB_APP_SLUG=
   ```

   `KEYSTATIC_SECRET` must be at least 32 characters. For Cloudflare Workers, set these in the deployed Worker environment as well; `PUBLIC_KEYSTATIC_GITHUB_APP_SLUG` must also be available during the Cloudflare build so it can be bundled into the admin UI.

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
pnpm deploy
```

## Notes

- Legacy URLs stay the same because each post keeps its original `url` value as a `path` frontmatter field.
- Existing images continue to work from `public/statics/`.
- Gitalk configuration is read from `.env` / Cloudflare runtime environment variables.
