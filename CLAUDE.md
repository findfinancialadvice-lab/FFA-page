# CLAUDE.md — Find Financial Advice NZ (FFA)
> Everything Claude needs to know about this project.

---

## Project Overview

**Site name:** Find Financial Advice NZ  
**Domain:** https://financialadvice.co.nz  
**Type:** Static HTML site + a couple of Cloudflare Pages Functions — no framework, no build step, no CMS  
**Hosting:** Cloudflare Pages, deployed from the `main` branch of GitHub repo **`findfinancialadvice-lab/FFA-page`** (auto-deploys on every push to `main`).  
**Purpose:** Free daily NZ personal finance news aggregator. An external **n8n workflow** ("FFA Daily Scraper + Publisher V3") pulls NZ finance RSS feeds each morning, categorises/summarises with an LLM, commits new article cards to the pages, emails subscribers via **Brevo**, and posts to social via Buffer.  
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
├── functions/
│   └── api/
│       └── subscribe.js        # Cloudflare Pages Function — POST /api/subscribe → Brevo (see below)
├── serve_ffa.py                # Local dev server (python3 serve_ffa.py)
├── update_returns_data.py      # Updates KiwiSaver fund returns data
└── .claude/
    └── settings.local.json     # Local permissions
```

> **Note:** The site of record is the GitHub repo `findfinancialadvice-lab/FFA-page`. The n8n workflow commits directly to that repo's `main`, and Cloudflare Pages deploys from it. Changes reach production only by merging to `main` (use a branch and pull request for manual edits). A separate private copy, `mrcam1/ffa-website`, exists as a backup of the Mac working folder and is **not** connected to Cloudflare, so merging there changes nothing live.

## Deployment
- **Cloudflare Pages**, connected to GitHub repo `findfinancialadvice-lab/FFA-page`.
- **Auto-deploys on every push/commit to `main`.** No manual deploy step, no FTP.
- **Environment variables** (Cloudflare Pages → Settings → Environment variables): `BREVO_API_KEY` — the Brevo API key used by `functions/api/subscribe.js`. Never hard-code it.

## Newsletter signup (Brevo)
- Homepage `#subscribe-form` POSTs `{email}` to **`/api/subscribe`** (a Pages Function).
- `functions/api/subscribe.js` validates the email and calls `POST https://api.brevo.com/v3/contacts` with `{ email, listIds: [2], updateEnabled: true }` (single opt-in, list ID **2**). Duplicate contacts are treated as success.
- The Brevo key is read only from `env.BREVO_API_KEY` — never in client code.
- **MailerLite has been fully removed** (form embed, scripts, and the old email path). Do not re-add it.

## Email flow (verified 9 Oct 2026 from a raw test email)
Everything sent as `@financialadvice.co.nz` goes out through **Brevo**; Cloudflare handles inbound mail only.
- **Daily digest:** Brevo campaign to list **2**, triggered by the n8n workflow (see below).
- **Mail typed in Gmail as `hello@financialadvice.co.nz`:** Gmail's "Send mail as" uses **Brevo's SMTP relay**, not Gmail's own servers. Headers show `Return-Path` on `sender-sib.com`, `DKIM pass` for `financialadvice.co.nz` (selector `brevo2`), `SPF pass`, `DMARC pass`. Consequences: Brevo adds an open-tracking pixel and `List-Unsubscribe` headers to these one-to-one emails, and they count toward the same Brevo daily sending limit as the digest. The only tracking control found is Brevo > Settings > Transactional email > Tracking > **Anonymous email tracking**, set to **Yes** on 9 Oct 2026: opens and clicks are still recorded but no longer tied to named contacts. That does not remove the pixel, and no off switch was found for relayed mail. Keep the privacy policy accurate about email open tracking. Do not move `hello@` sending off the Brevo relay to Gmail's own servers without adding Google's SPF/DKIM, or DMARC alignment will fail.
- **`info@` auto-reply:** a Cloudflare Email Worker (`ffa-info-autoreply`) replies from `hello@` through the Brevo transactional API. Its source is in `email-worker/` in the Mac working folder only, not in this repo.
- **Inbound:** MX records point at Cloudflare Email Routing, which forwards to the Gmail mailbox. It cannot send.
- **DNS (Cloudflare):** Brevo DKIM CNAMEs (`brevo1._domainkey`, `brevo2._domainkey`), a `brevo-code` TXT, SPF including `spf.brevo.com`, and DMARC `p=none` (monitoring only).
- `/cdn-cgi/l/email-protection` is Cloudflare Email Address Obfuscation rewriting the footer address. Search Console reports it as a 404. It is harmless and can be ignored.

## Daily news (n8n)
- Handled by the external **n8n workflow "FFA Daily Scraper + Publisher V3"** (not a local Claude task — the old `~/.claude/scheduled-tasks/ffa-daily-news-scrape/SKILL.md` is retired).
- Cron `0 7 * * *` in `Pacific/Auckland` (7am NZT).
- Fetches the current pages from GitHub, dedupes new articles against existing URLs, categorises + summarises via OpenRouter (`claude-haiku-4.5`), then **splices article cards into the news grid** and commits to `main` via the GitHub Contents API.
- It edits the **live** files (does not use a page template), so anything outside the `.news-grid` — e.g. the newsletter form — is preserved untouched.
- Also sends the daily email via a **Brevo** campaign to list **2**, and posts to LinkedIn/Facebook via **Buffer**.

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
| sources.html | /sources | Static — describes the news sources |
| subscribe.html | /subscribe | Static — standalone Brevo signup landing page (posts to `/api/subscribe`); linked in header nav + footer on every page |

**News grid behaviour** (performed by the n8n workflow's "HTML Surgery" node):  
- Category pages: **prepends** new articles into `<div class="news-grid">` (accumulate over time, no cap)  
- index.html: **prepends** new articles into `<div class="news-grid" id="news-grid">`, then **caps the grid at 60 cards** (oldest trimmed; full archive lives on topic pages)  
- Article card format: `<div class="news-card" data-category="[category]">` with tag, h3/link, summary, meta (source + date). The workflow keys off these exact markers — don't rename the grid `id`/class or the card structure.

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
- Social icons (Facebook, LinkedIn) after nav links, separated by thin divider (Instagram removed — do not re-add)
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
  (Originally externalised because SiteGround blocked Facebook's crawler. Now on Cloudflare Pages that constraint is gone — the OG image could be served from the site directly, but it's left external to avoid re-scraping/cache churn. Not urgent.)
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

## News Sources (n8n RSS feeds)
The workflow's "Set RSS Feed URLs" node currently pulls these 7 RSS feeds:
1. Interest.co.nz — `https://www.interest.co.nz/rss`
2. Good Returns (KiwiSaver) — `https://www.goodreturns.co.nz/rss/kiwisaver.xml`
3. Good Returns (News) — `https://www.goodreturns.co.nz/rss/news.xml`
4. Stuff.co.nz — `https://www.stuff.co.nz/rss`
5. RNZ Business — `https://www.rnz.co.nz/rss/business.xml`
6. NZ Herald Business — `https://www.nzherald.co.nz/arc/outboundfeeds/rss/section/business/?outputType=xml`
7. Solid Steele Advice — `https://www.solidsteeleadvice.co.nz/feed.xml`

- Articles within a ~48h window are considered; **Solid Steele articles are always included regardless of age**.
- **Categories:** kiwisaver, property, investing, budgeting, retirement, insurance (LLM assigns exactly one).
- To change sources, edit the feed array in the n8n workflow — not this repo.

---

## Minification
HTML pages link to `styles.min.css` and `main.min.js` (Semrush flagged unminified assets).
**After editing styles.css or main.js, always regenerate the minified copies before committing to `main`** (the pages load the `.min` files, so unminified edits won't show up live):
```bash
cd "/Users/cam/Documents/saved stuff/SSA/FFA" && python3 -c "
import rcssmin, rjsmin
open('styles.min.css','w').write(rcssmin.cssmin(open('styles.css').read()))
open('main.min.js','w').write(rjsmin.jsmin(open('main.js').read()))"
```

## Owner's Preferences
- **Terse responses** — no trailing summaries or recaps
- **Deploy = push to `main`** — changes go live via Cloudflare when committed to `main` (no `deploy-ffa.command`, no FTP). This local folder has no git remote; changes currently reach `main` via GitHub web upload.
- **Broad permissions** preferred over per-command prompts
- **No diagonal microlines** on intro/header sections (removed, keep them off)
- **Solid Steele Advice** is Cameron's own KiwiSaver advisory business — feature it prominently where relevant (advisers page, FAQ schema, calculators)
- **Do not include** KiwiSaver articles that argue passive investment style is better than active
- **Backlog drip:** max 2–3 Solid Steele blog articles added per daily scrape run

---

## Known Issues / Notes
- **Now on Cloudflare Pages** (migrated off SiteGround). Old SiteGround-specific notes (HTTP 202 bot protection, `facebookexternalhit` blocking, FTP) no longer apply.
- **`.htaccess` is Apache-only** and is inert on Cloudflare Pages. The redirects it used to do (HTTPS enforce, www→non-www, `/index.html`→`/`, clean `.html` URLs) must be reproduced with a Cloudflare `_redirects` file or Cloudflare rules — verify these are in place; don't assume `.htaccess` is doing anything.
- The n8n workflow **prepends** (never replaces) articles and preserves everything outside `.news-grid` — do not change the grid markers it keys off.
- `kiwisaver-fund-comparison.html` is a standalone page not in the main nav or sitemap.
- A `netlify-deploy/` folder may still exist locally — ignore it; the site is on Cloudflare Pages, not Netlify.
- news.html was REMOVED (June 2026) — /news 301-redirects to homepage. Do not recreate it.
