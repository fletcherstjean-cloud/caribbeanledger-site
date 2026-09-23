# The Caribbean Ledger — site

Content lives in `content/articles.json`. The build reads it and generates the full
static site into `dist/`: the homepage, a standalone page per story with full search
tags (title, description, canonical, Open Graph, Twitter card, NewsArticle structured
data), an all-stories archive, a sitemap, and robots.

## Publishing
Add or edit a story in `content/articles.json` and commit. Cloudflare Pages rebuilds
and deploys automatically. No manual upload.

## Cloudflare Pages settings (set once)
- Framework preset: None
- Build command: `python3 build.py`
- Build output directory: `dist`
- Root directory: `/`
- No dependencies (Python standard library only)

## Local build (optional)
`python3 build.py`  →  writes everything to `dist/`
