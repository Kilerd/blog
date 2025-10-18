# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal blog built with [Staple](https://github.com/Kilerd/staple) - a static site generator written in Rust. The blog is primarily written in Chinese and covers topics including Rust, Python, general tech, daily life, annual summaries, and travel.

## Build and Deployment

### Building the Site

```bash
# Download and install Staple (version 0.3.2)
# Linux: https://github.com/Kilerd/staple/releases/download/0.3.2/staple-ubuntu.tar.gz
# macOS: You may need to build from source or use the Linux version

# Build the site (generates output to ./public)
staple build
```

The build process:
- Reads configuration from `Staple.toml`
- Processes markdown files from `data/` directory
- Applies templates from `templates/rubble/`
- Outputs static HTML to `public/` directory

### Development

Staple likely supports a development server with live reload:
```bash
staple serve
# or
staple dev
```

### Docker Build

```bash
# Build Docker image (multi-stage build with busybox httpd server)
docker build -t blog .

# Run locally on port 3000
docker run -p 3000:3000 blog
```

## Content Structure

### Markdown Files

All content lives in `data/` organized by category:
- `data/rust/` - Rust programming articles
- `data/python/` - Python programming articles
- `data/general-tech/` - General technology articles
- `data/daily/` - Daily life posts
- `data/annual-summaries/` - Annual summary posts
- `data/accidents/` - Incident reports/stories
- `data/trip/` - Travel logs
- `data/page/` - Static pages (About, Portfolios, Blogroll)

### Markdown Front Matter Format

Every markdown file uses a custom front matter format with ` - key = value` syntax:

```markdown
 - title = Post Title Here
 - url = post-url-slug
 - tags = tag1, tag2
 - datetime = 2020-06-11T18:43:26.000000+08:00
 - template = article.html
 - page = true          # Optional: marks as a static page
 - page_index = 3       # Optional: ordering for pages in navigation
 - cover = /path.jpg    # Optional: cover image
 - header_bg_color = black   # Optional: header background color
 - header_color = white      # Optional: header text color

Content starts here after a blank line.

<!--more--> can be used to mark description cutoff.
```

**Important**: The front matter uses space-dash-space (` - `) prefix, NOT standard YAML `---` delimiters.

### Static Pages

Pages marked with `page = true` appear in the site navigation. The `page_index` controls their order.

## Templates

### Theme: Rubble

Located in `templates/rubble/`:
- `article.html` - Article/post template
- `index.html` - Homepage listing
- `rss.xml` - RSS feed template
- `statics/` - CSS, JavaScript, images

### Template Variables

Templates use Tera templating engine with these key variables:
- `{{ config.site.* }}` - Site configuration from Staple.toml
- `{{ page.* }}` - Current page data (title, url, content, datetime, etc.)
- `{{ pages }}` - Collection of all pages
- `{{ config.extra.* }}` - Custom configuration values

### Filters and Functions

- `{{ page.datetime | date(format="%B %d, %Y") }}` - Date formatting
- `{{ page.content.html | safe }}` - Rendered HTML content
- `{{ pages | filter(attribute="data.page", value=true) }}` - Filter pages
- `{{ pages | not_field(attribute="data.page") }}` - Exclude pages
- `{{ pages | sort(attribute="data.page_index") }}` - Sort pages

## Configuration

### Staple.toml

Key settings:
- `[site]` - Basic site metadata (title, description, domain, theme)
- `[[statics]]` - Files to copy to output (CNAME, ads.txt)
- `[extra]` - Custom values (Google Analytics script)
- `utc_offset = 800` - Timezone offset (UTC+8)

### Third-party Services

The site integrates:
- Google AdSense (ca-pub-9147137464451642)
- Gitalk comments (GitHub issue-based)
- Umami analytics (umami.xinsoftware.top)
- Prism.js for syntax highlighting

## CI/CD

### GitHub Pages Deployment

Workflow: `.github/workflows/blog.yml`
- Triggers on every push
- Downloads latest Staple binary
- Builds site with `staple build`
- Deploys `public/` to GitHub Pages

### Docker Image Deployment

Workflow: `.github/workflows/docker-image.yml`
- Triggers on push to main/master branches
- Builds Docker image with multi-stage build
- Pushes to:
  - Docker Hub: `kilerd/application:blog-latest`
  - GitHub Container Registry: `ghcr.io/kilerd/blog`

## Site Architecture

### Static Site Generation Flow

1. **Input**: Markdown files in `data/` with custom front matter
2. **Processing**: Staple reads Staple.toml config and parses markdown
3. **Templating**: Tera templates in `templates/rubble/` render HTML
4. **Output**: Static files written to `public/` directory

### URL Structure

- Articles: `/{url-slug}` (e.g., `/rust-proc-macro-101`)
- Static pages: `/{url-slug}` (e.g., `/about`, `/blogroll`)
- RSS feed: `/rss.xml`
- Static assets: `/statics/*`

### Content Discovery

The homepage (`index.html`) lists all content except pages marked with `page = true`. Pages with `page = true` appear in the site navigation instead.

## Making Changes

### Adding a New Post

1. Create markdown file in appropriate `data/` subdirectory
2. Add front matter with title, url, datetime, tags
3. Write content below front matter
4. Run `staple build` to regenerate site
5. Commit and push - CI will deploy automatically

### Modifying Templates

1. Edit files in `templates/rubble/`
2. Test with `staple build` or `staple serve`
3. Changes to templates require rebuilding all pages

### Updating Configuration

1. Edit `Staple.toml` for site-wide settings
2. Changes require full rebuild with `staple build`
