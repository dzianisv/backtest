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

- **Primary endpoint (verified working 2026-06-16):** Google News RSS filtered to WSJ:
  `https://news.google.com/rss/search?q=site%3Awsj.com+when%3A7d&hl=en-US&gl=US&ceid=US%3Aen`
  Returns ~100 articles/7 days. URLs are opaque Google News redirects (work in browsers, not directly resolvable).
- **DEPRECATED (dead since Jan 2025):** `https://feeds.a.dj.com/rss/RSSMarketsMain.xml` and other DJ feeds — frozen, return stale data.
- Parse `channel > item`: `title`→title (strip `" - The Wall Street Journal"` suffix), `link`→url (Google News redirect), `pubDate`(RFC-822)→`published_at` (ISO-8601 UTC). The RSS `description` is Google News's snippet — keep verbatim as `summary` if present, else `"[UNAVAILABLE - paywall]"`. **Do NOT scrape the full body.** `category`→`tags`, `lang: en`, `source: wsj`.

## Reading the BODY (verified method, June 2026)

This adapter emits headlines only, but downstream readers (`narrative-news`, `trend-stock-research`)
sometimes need the article body. **Empirically tested from this agent environment** against live WSJ URLs —
use this exact ladder, do NOT theorize:

1. **web.archive.org** — the WORKHORSE for WSJ in headless runs. `curl -L "http://web.archive.org/web/2/<url>"`
   (or check `https://archive.org/wayback/available?url=<url>` first) returns the **full WSJ article body**
   (verified: a CPI story snapshot carried the real "Consumer prices were up 4.2%…" paragraphs). Reachable via
   plain `curl` from the agent's bash with no extension. WSJ snapshots are far more complete than FT's
   (unlike FT, WSJ does not serve the Wayback crawler a bare paywall wall).
2. **chrome-use** (user's real Chrome + `bypass-paywalls-clean`): also returns the body (BPC clears the metered
   cookie / disables paywall JS). **Only on the user's own machine**, not headless/CI/MCP.
3. **archive.today** (`archive.ph/newest/<url>`): an alternative, BUT from this environment's datacenter IP it
   returns a **Cloudflare CAPTCHA (HTTP 429)** to `curl`/`web_fetch` — only usable from a real JS browser.
4. **Direct fetch / Googlebot-UA spoof**: return **HTTP 401** from this IP. Do NOT rely on these.

**Headless verdict:** prefer **web.archive.org** for WSJ bodies — it actually works here. If the URL has no
snapshot yet, degrade to headline + `[UNAVAILABLE - paywall]`; do not fabricate. This matches the ladder in
[[trend-stock-research]] §"How to read articles".

**Legal/ToS:** paywall bypass is ToS-gray. web.archive.org / archive.today are public archives; this is for
the owner's personal research reading only, never redistribution. Honor robots/bot-blocks; do not hammer.

## Politeness (required)

Conditional GET (ETag/If-Modified-Since; `304` → nothing-new). Exponential backoff on `429`/`5xx`, ~2 retries, then `[UNAVAILABLE]`. Sequential fetch.

## Normalized output record

```json
{"source":"wsj","url":"https://www.wsj.com/articles/<slug>","title":"...","published_at":"2026-06-15T...Z","summary":"<publisher teaser or [UNAVAILABLE - paywall]>","lang":"en","tags":["markets"]}
```

## Failure mode

```json
{"source":"wsj","status":"[UNAVAILABLE]","reason":"paywall / fetch failed"}
```

## Interactive fallback — full article body

When the RSS teaser and Wayback snapshot are not enough and you need the full WSJ article, use the
**bypass-paywalls** skill (`.agents/skills/bypass-paywalls/SKILL.md`) which navigates the user's
Chrome (with bypass-paywalls-clean extension) to extract the full body interactively.

The automated path (this skill) handles daily RSS ingestion + Wayback bodies; the interactive path
handles ad-hoc reads when no Wayback snapshot exists or the snapshot is stale. This is the same
chrome-use + BPC method documented in §"Reading the BODY" above, packaged as a reusable skill.

> Educational, not advice. Headlines only; never fabricate a paywalled body.
