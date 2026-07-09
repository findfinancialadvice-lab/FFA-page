# CLAUDE.md — Find Financial Advice NZ (FFA)
> Everything Claude needs to know about this project.

---

## Project Overview

**Site name:** Find Financial Advice NZ  
**Domain:** https://financialadvice.co.nz  
**Type:** Static HTML website — no framework, no build step, no CMS  
**Purpose:** Free daily NZ personal finance news aggregator. Scrapes 10 NZ financial sources daily, adds article summaries to topic pages, deploys to SiteGround, and emails subscribers via MailerLite.  
**Owner:** Cameron Steele (Solid Steele Advice Ltd, Christchurch NZ)

---

## Folder Structure

```
/Users/cam/Documents/saved stuff/SSA/FFA/
├── index.html                  # Homepage — hero, featured article, full news grid (all articles)
├── kiwisaver.html              # KiwiSaver topic page
├── property.html               # Property topic page
├── investing.html              # Investing topic page
├── budgeting.html              # Budgeting topic page
├── retirement.html             # Retirement topic page
├── insurance.html              # Insurance topic page
├── advisers.html               # Find a financial adviser page (static content + directory)
├── calculators.html            # Financial calculators page (curated links)
├── sources.html                # About our sources page (static content)
├── kiwisaver-fund-comparison.html  # Standalone KiwiSaver fund comparison tool
├── styles.css                  # Single shared stylesheet — SOURCE file, edit this
├── styles.min.css              # Minified copy — what the HTML actually links to
├── main.js                     # Minimal JS source — makes news cards fully clickable
├── main.min.js                 # Minified copy — what the HTML actually links to
├── site.webmanifest            # PWA manifest (name: Find Financial Advice NZ, short_name: FFA NZ)
├── robots.txt                  # Allows all crawlers; 5s crawl delay; references sitemap
├── sitemap.xml                 # 10 URLs, non-www HTTPS, priorities set
├── .htaccess                   # HTTPS enforce, www→non-www redirect, clean URLs, cache headers
├── og-image.jpg                # 1200×630 OG image (hosted externally at postimages.org — see below)
├── favicon.ico / favicon.svg / favicon-96x96.png / apple-touch-icon.png
├── Find Financial Advice Logo, wide R.png   # Nav logo
├── serve_ffa.py                # Local dev server (python3 serve_ffa.py)
├── update_returns_data.py      # Updates KiwiSaver fund returns data
└── .claude/
    └── settings.local.json     # Permissions for the daily scheduled task
```

**Deploy script** (one level up):
```
/Users/cam/Documents/saved stuff/SSA/deploy-ffa.command
```
Run with: `cd "/Users/cam/Documents/saved stuff/SSA" && python3 deploy-ffa.command`  
Uploads all HTML, CSS, JS, images, xml, txt, webmanifest, and .htaccess via FTP_TLS to SiteGround.  
**Always run this after making any changes.**

**Daily scrape task:**
```
/Users/cam/.claude/scheduled-tasks/ffa-daily-news-scrape/SKILL.md
```
Runs at 6am daily. Scrapes 10 sources, prepends new articles to category pages and index.html, deploys, sends MailerLite email.

---

## Pages & Their Purpose

| Page | URL | Content type |
|------|-----|-------------|
| index.html | / | Hero + featured article + full accumulated news grid |
| kiwisaver.html | /kiwisaver | KiwiSaver articles (accumulated) |
| property.html | /property | Property articles |
| investing.html | /investing | Investing articles |
| budgeting.html | /budgeting | Budgeting articles |
| retirement.html | /retirement | Retirement articles |
| insurance.html | /insurance | Insurance articles |
| advisers.html | /advisers | Static — adviser directory links + FSPR callout |
| calculators.html | /calculators | Static — curated calculator links |
| sources.html | /sources | Static — describes the 10 news sources |

**News grid behaviour:**  
- Category pages: daily scrape **prepends** new articles (accumulate over time)  
- index.html: daily scrape **prepends** new articles, then **caps the grid at 60 cards** (oldest trimmed; full archive lives on topic pages)  
- Article card format: `<div class="news-card" data-category="[category]">` with tag, h3/link, summary, meta (source + date)

---

## Design System

### Typography
- **Headings / display text:** `DM Serif Display` (Google Fonts) — weight 400, italic variant available
- **Body / UI:** `Inter` (Google Fonts) — weights 400, 500, 600, 700
- CSS variables: `--serif` and `--sans`

### Colour Palette (NZ Fern Green theme)
```css
--green:        #0d4a35   /* Deep fern — primary brand, navbar text, buttons */
--green-mid:    #1a6b4e   /* Mid green */
--green-bright: #17b97a   /* Bright accent — hover states, tags, featured bars */
--green-pale:   #e8f5ef   /* Light green tint — tag backgrounds, featured cards */
--cream:        #F5F1EB   /* Page background */
--cream-dark:   #EAE5DC   /* Darker cream */
--ink:          #161616   /* Near-black body text */
--charcoal:     #363636   /* Secondary text */
--mid:          #5e5e5e   /* Muted text */
--light:        #909090   /* Light/label text */
--border:       #D4CFC6   /* Borders */
--border-light: #E4DFD7   /* Light borders, grid gaps */
--white:        #ffffff
```

**Legacy aliases** (kept for backward compatibility with inline styles):  
`--navy = --green`, `--blue = --green-bright`, `--light-grey = --cream`, `--text = --charcoal`, etc.

### Layout
- **Container max-width:** standard CSS container class
- **Navbar height:** `--nav-h: 62px`
- **Border radius:** `--radius: 3px` (near-sharp corners — intentional premium feel)
- **News grid:** 3 columns, `gap: 1px`, `background: var(--border-light)` — gap-as-divider technique (no card borders, gaps create the grid lines)
- **Section background:** `--cream` (#F5F1EB) so white news cards contrast against it

### Navbar
- White background with 3px `--green-bright` top border
- Underline hover animation (`::after` pseudo-element, scales from 0 to 1)
- Social icons (Facebook, LinkedIn, Instagram) after nav links, separated by thin divider
- Mobile: hamburger toggle

### Cards
- News cards: white background, no border, no border-radius
- `::before` pseudo-element — 2px top accent bar, transparent by default, `--green-bright` on hover
- Hover: background shifts to `--cream`
- Entire card is clickable (via `main.js`)

### Intro/Header sections
- `background-image: none` — diagonal microlines were **removed** from all intro sections
- Affected: `.category-intro`, `.sources-intro`, `.section:has(.advisers-intro-body)`, `.section:has(.category-intro-body)`, `#news`

---

## SEO & Meta Configuration

### Per-page head tags (all 11 pages)
- `<html lang="en-NZ">`
- `<link rel="canonical">` — non-www HTTPS, clean URL (no .html extension)
- `<meta name="description">` — unique per page
- `<meta name="application-name" content="Find Financial Advice NZ">`
- `<meta name="apple-mobile-web-app-title" content="Find Financial Advice NZ">`
- `og:site_name` = `Find Financial Advice NZ`
- `og:url`, `og:title`, `og:description`, `og:image`, `og:image:type`, `og:image:width/height`
- `twitter:card` = `summary_large_image`
- `og:locale` = `en_NZ`
- `geo.region` = `NZ`
- `language` = `en-NZ`
- `robots` = `index, follow`
- `theme-color` = `#0d4a35`

### OG Image
- **File:** og-image.jpg (1200×630, baseline JPEG)
- **Hosted externally:** `https://i.postimg.cc/XvXzCPs9/FFA-og-image.jpg`  
  (SiteGround blocks Facebook's crawler at server level — externally hosted bypasses this)
- Design: deep green background, "FinancialAdvice.co.nz" white + green accent, subheadline, category footer strip

### Schema (JSON-LD)
Every page has a single `@graph` block containing:
- `WebSite` (on index only) with `@id: /#website`, `name: Find Financial Advice NZ`
- `Organization` (on index only) with logo, email, areaServed: New Zealand
- `WebPage` — page-specific name, description, isPartOf → #website
- `FAQPage` — NZ-specific Q&As relevant to each topic
- Additional types where relevant (e.g. `ItemList` on calculators, `NewsMediaOrganization` on sources)

### Analytics & Tracking
- **GTM:** `GTM-PXX6WRRG` (on all pages, in `<head>`)
- **GA4:** `G-EKNTL9Q19B` (on all pages via gtag.js)
- **Meta Pixel:** `1661535551726233` (on all pages, before `</head>`)

### Redirects (.htaccess)
- HTTP → HTTPS (301)
- www → non-www (301)
- `/index.html` → `/` (301)
- `/page.html` → `/page` (301 — clean URLs)
- Internally serves `.html` files for clean URL requests

---

## Social Media
- **Facebook:** https://www.facebook.com/FindFinancialAdviceNZ
- **LinkedIn:** https://www.linkedin.com/company/find-financial-advice-nz/
- Icons appear in navbar on all pages (inline SVG, no icon library dependency)
- Instagram link was removed (June 2026) — do not re-add

---

## News Scrape Sources (Daily Task)
1. Interest.co.nz — https://www.interest.co.nz/news
2. Good Returns — https://www.goodreturns.co.nz
3. Sorted NZ — https://sorted.org.nz/blog
4. Stuff.co.nz — RSS feed (JS-rendered page, use RSS instead)
5. NZ Herald — https://www.nzherald.co.nz/business/personal-finance
6. RNZ Business — https://www.rnz.co.nz/news/business
7. 1News — https://www.1news.co.nz/tags/business/
8. Irvine Wenborn — https://www.irvinewenborn.co.nz/financialeducation
9. Opes Partners — https://www.opespartners.co.nz/mortgage
10. Solid Steele Advice — https://www.solidsteeleadvice.co.nz/learn-and-blog

**Categories:** kiwisaver, property, investing, budgeting, retirement, insurance  
**Article card format:** see SKILL.md for exact HTML template

---

## Minification
HTML pages link to `styles.min.css` and `main.min.js` (Semrush flagged unminified assets).
**After editing styles.css or main.js, always regenerate the minified copies before deploying:**
```bash
cd "/Users/cam/Documents/saved stuff/SSA/FFA" && python3 -c "
import rcssmin, rjsmin
open('styles.min.css','w').write(rcssmin.cssmin(open('styles.css').read()))
open('main.min.js','w').write(rjsmin.jsmin(open('main.js').read()))"
```

## Owner's Preferences
- **Terse responses** — no trailing summaries or recaps
- **Auto-deploy** — always run `deploy-ffa.command` at the end of any change
- **Broad permissions** preferred over per-command prompts
- **No diagonal microlines** on intro/header sections (removed, keep them off)
- **Solid Steele Advice** is Cameron's own KiwiSaver advisory business — feature it prominently where relevant (advisers page, FAQ schema, calculators)
- **Do not include** KiwiSaver articles that argue passive investment style is better than active
- **Backlog drip:** max 2–3 Solid Steele blog articles added per daily scrape run

---

## Known Issues / Notes
- SiteGround's server-level bot protection blocks third-party scanners (RankPrompt, etc.) with HTTP 202. This does **not** affect Google/Bing — ignore audit tool errors about robots.txt/sitemap being "missing"
- Facebook's crawler (facebookexternalhit) is also blocked by SiteGround — that's why OG image is hosted on postimages.org
- The daily scrape SKILL.md has been updated to **prepend** (not replace) articles on index.html — do not change this back to replace behaviour
- `kiwisaver-fund-comparison.html` is a standalone page not in the main nav or sitemap
- `netlify-deploy/` folder exists but site is deployed to SiteGround via FTP, not Netlify

---

## FTP / Deploy Credentials
Credentials stored in `~/.netrc` (not in any project file).  
- Host: `ftp.financialadvice.co.nz`  
- User: `host@financialadvice.co.nz`  
- Remote path: `financialadvice.co.nz/public_html`

- news.html was REMOVED (June 2026) — /news 301-redirects to homepage. Do not recreate it.
