---
name: feed-wsj
description: Source adapter for The Wall Street Journal (WSJ) Markets — PAYWALLED, RSS descriptions/teasers available as summary. Fetch + normalize the WSJ Markets RSS into the common article record (headline + url + published_at + publisher's RSS teaser). Use when gathering the crypto/macro news feed, when narrative-news needs WSJ markets coverage, or when asked for "WSJ headlines" / "Wall Street Journal markets news". Fetch + normalize ONLY — no dedup/store/judge. NEVER fabricates a body.
license: MIT
compatibility: opencode
metadata:
  audience: crypto-research-pipeline
  domain: news-feed-adapter
  role: source-adapter
  tier: macro-paywalled
---

# feed-wsj (WSJ Markets source adapter — RSS teasers available)

Pure **fetch + normalize** adapter for a **paywalled** outlet. WSJ bodies are behind a paywall, so this
adapter emits **headline + url + published_at + RSS teaser** (the publisher's own `description`) and marks
the body `[UNAVAILABLE - paywall]` only when the RSS teaser is absent. Dedup/store/judge live downstream in
[[crypto-news-store]] + [[narrative-news]].

## Hard rule (paywall)

**NEVER fabricate body text.** Headline-only is acceptable; invented prose is a defect (PRD AC6). On any
failure → `[UNAVAILABLE]`. Return **≥1 headline record or a clean `[UNAVAILABLE]`** (AC5).

## Retrieval recipe

- **Primary endpoint (verified working 2026-06-25):** Dow Jones official public RSS on the **new** host
  `https://feeds.content.dowjones.io/public/rss/<FEED>`. Returns real `www.wsj.com` article URLs **plus a
  1-sentence publisher teaser** (40–100 items/feed). Use these feeds:
  `RSSMarketsMain` (markets) · `RSSWorldNews` (world) · `WSJcomUSBusiness` (US business) · `RSSWSJD` (tech)
  Example: `https://feeds.content.dowjones.io/public/rss/RSSMarketsMain`
- **DEPRECATED (frozen 2025-01-27):** `https://feeds.a.dj.com/rss/*` — the OLD Dow Jones host; still 200s
  but its newest item is dated Jan 27 2025. Dow Jones migrated to `feeds.content.dowjones.io` (above). Do NOT use.
- **Optional topical fallback (opaque URLs):** Google News RSS filtered to WSJ —
  `https://news.google.com/rss/search?q=site%3Awsj.com+<terms>+when%3A7d&hl=en-US&gl=US&ceid=US%3Aen`.
  Use ONLY for targeted topic search; its links are opaque Google redirects, not real wsj.com paths.
- Parse `channel > item`: `title`→title (strip `" - The Wall Street Journal"` suffix), `link`→url (real
  www.wsj.com URL; canonicalize, strip `utm_*` and the `?mod=` tracking param), `pubDate`(RFC-822)→
  `published_at` (ISO-8601 UTC), `description`→`summary` (WSJ's own teaser — keep **verbatim**, never scrape
  the body). If a teaser is absent → `summary = "[UNAVAILABLE - paywall]"`. `category`→`tags`, `lang: en`, `source: wsj`.
- **Pipeline:** the automated ingest is `crypto-news-store/news_fetch.py` (Python, drives narrative-news)
  and `trend-stock-research/scripts/feeds/feed_wsj.ts` (TS) — both already point at these endpoints.

## Reading the BODY (verified method, June 2026)

For the full article body, use the script — **no extension required**:

```bash
bun /Users/engineer/workspace/backtest/.agents/scripts/feeds/read_article.ts "<wsj-url>"
```

**Method order for WSJ:** Wayback Machine (`web.archive.org/web/2/<url>`) → archive.ph via Chrome CDP
→ direct fetch. Wayback works for WSJ — unlike FT, WSJ does not serve a paywall page to the Wayback
crawler. Returns HTTP 404 when no snapshot exists for a URL; script falls through to next method.

Tested 2026-06-20: Wayback returned `OK` for snapshot URLs; specific articles without snapshots return 404.

**Direct fetch**: HTTP 401 from agent IPs. Do NOT use as primary.

**What does NOT work for WSJ:**
- Bing cache (`cc.bingj.com`) — DNS does not resolve
- Google cache — deprecated, returns error page

**Legal/ToS:** web.archive.org is a public archive; for owner's personal research only, never redistribution.

## Politeness (required)

Conditional GET (ETag/If-Modified-Since; `304` → nothing-new). Exponential backoff on `429`/`5xx`, ~2 retries, then `[UNAVAILABLE]`. Sequential fetch.

## Normalized output record

```json
{"source":"wsj","url":"https://www.wsj.com/finance/<slug>","title":"Micron’s Blockbuster Earnings Quiet the AI Doubters","published_at":"2026-06-24T...Z","summary":"A rally in the memory-chip company’s shares drove Nasdaq futures higher.","lang":"en","tags":["markets"]}
```

The `summary` is WSJ's own RSS teaser (1 sentence). Body text is NOT in the feed. If a teaser is missing →
`summary:"[UNAVAILABLE - paywall]"`.

## Failure mode

```json
{"source":"wsj","status":"[UNAVAILABLE]","reason":"paywall / fetch failed"}
```

## Full-body fallback

See [[bypass-paywalls]] skill for CAPTCHA instructions and manual usage. Call `read_article.ts`
directly from agent bash for ad-hoc reads; this skill handles automated daily RSS ingestion only.

> Educational, not advice. Headlines only; never fabricate a paywalled body.
