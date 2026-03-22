# kilerd blog migration

This repository now contains a Cloudflare-native blog stack:

- `apps/cms`: SonicJS on Cloudflare Workers + D1 + R2
- `apps/web`: Astro SSR on Cloudflare
- `data/`: legacy Staple Markdown source kept intact for migration and backup

## Local setup

1. Install dependencies:

   ```bash
   pnpm install
   ```

2. Create your CMS database and media bucket:

   ```bash
   cd apps/cms
   pnpm wrangler d1 create kilerd-blog-cms
   pnpm wrangler r2 bucket create kilerd-blog-media
   ```

3. Put the returned `database_id` into [apps/cms/wrangler.toml](/Users/chenxin/Projects/blog/apps/cms/wrangler.toml).

4. Run local migrations:

   ```bash
   pnpm cms:db:migrate:local
   ```

5. Start the CMS once so SonicJS can auto-sync the `posts` collection:

   ```bash
   pnpm dev:cms
   ```

6. In another shell, import the legacy content:

   ```bash
   pnpm import:content
   ```

7. Start the Astro frontend:

   ```bash
   cp apps/web/.env.example apps/web/.env
   pnpm dev:web
   ```

## What was preserved

- Legacy URIs stay the same because each post stores its original `url` front matter as a `path` field.
- Existing images continue to work from `apps/web/public/statics/`.
- Old Markdown source remains under `data/` and is also exported to `generated/content/posts.json` during migration.

## Notes

- Gitalk is now opt-in via `apps/web/.env` instead of being hard-coded into the page.
- The frontend expects the CMS API at `SONICJS_API_URL`; the default local value is `http://127.0.0.1:8787`.
