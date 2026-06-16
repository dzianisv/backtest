---
name: feed-ft
description: Source adapter for the Financial Times (FT) — PAYWALLED, so HEADLINES ONLY. Fetch + normalize the FT RSS into the common article record (headline + url + published_at) with body marked [UNAVAILABLE - paywall]. Use when gathering the crypto/macro news feed, when narrative-news needs FT macro coverage, or when asked for "FT headlines" / "Financial Times news". Fetch + normalize ONLY — no dedup/store/judge. NEVER fabricates a body.
license: MIT
compatibility: opencode
metadata:
  audience: crypto-research-pipeline
  domain: news-feed-adapter
  role: source-adapter
  tier: macro-paywalled
---

# feed-ft (Financial Times source adapter — headlines only)

Pure **fetch + normalize** adapter for a **paywalled** outlet. FT bodies are behind a hard paywall, so this
adapter emits **headline + url + published_at only** and marks the body `[UNAVAILABLE - paywall]`. Dedup/
store/judge live downstream in [[crypto-news-store]] + [[narrative-news]].

## Hard rule (paywall)

**NEVER fabricate body text.** Headline-only is acceptable; invented prose is a defect (PRD AC6). On any
failure → `[UNAVAILABLE]`. Return **≥1 headline record or a clean `[UNAVAILABLE]`** (AC5).

## Retrieval recipe

- **Endpoint:** `https://www.ft.com/rss/home` (FT home RSS — headlines + links + pubDate; bodies paywalled).
  Also useful: `https://www.ft.com/rss/markets`.
- **Note (verify at runtime):** FT aggressively bot-blocks; the RSS may return `403`/be unfetchable from
  some hosts/agents (e.g. `web_fetch` returned "unable to fetch" at build time). That is the paywall path,
  not a bug — **degrade to `[UNAVAILABLE]`, never fabricate**. If the RSS resolves, parse `channel > item`.
- Parse: `title`→title, `link`→url (canonicalize, strip `utm_*`), `pubDate`(RFC-822)→`published_at` (ISO-8601 UTC). **`summary` = `"[UNAVAILABLE - paywall]"`** (do NOT scrape or guess the body). `lang: en`, `source: ft`.
- The RSS `description`, if present, is FT's own short teaser — you MAY keep it verbatim as `summary` (it is
  publisher-provided, not fabricated). If empty/absent → `[UNAVAILABLE - paywall]`.

## Reading the BODY (verified method, June 2026)

This adapter emits headlines only, but downstream readers (`narrative-news`, `trend-stock-research`)
sometimes need the article body. **Empirically tested from this agent environment** against live FT/WSJ
URLs — use this exact ladder, do NOT theorize:

1. **chrome-use** (user's real Chrome with the `bypass-paywalls-clean` extension): the ONLY method that
   reliably returns the FT body. Works because BPC spoofs a Googlebot UA, clears the metered-paywall cookie,
   and disables the paywall JS — all of which need a real configured browser. **Only available on the user's
   own machine**, not in headless/CI/MCP runs.
2. **web.archive.org** (`curl -L "http://web.archive.org/web/2/<url>"`, or check
   `https://archive.org/wayback/available?url=<url>` first): reachable headlessly via plain `curl` from the
   agent's bash. ⚠️ **FT-specific limitation:** FT serves the Wayback crawler its `"Subscribe to read"` wall,
   so most FT `/content/` snapshots are the PAYWALL page, not the body — Wayback is unreliable for FT bodies
   (it works well for WSJ). Always verify the snapshot isn't just `"Subscribe to read"` before using it.
3. **archive.today** (`archive.ph/newest/<url>`): captures FT bodies better than Wayback, BUT from this
   environment's datacenter IP it returns a **Cloudflare CAPTCHA (HTTP 429)** to `curl`/`web_fetch` — only
   usable from a real JS browser (i.e. chrome-use on the user's machine).
4. **Direct fetch / Googlebot-UA spoof / `?format=amp`**: all return **403** from this IP (FT bot-blocks the
   datacenter range; the Googlebot spoof needs verified Googlebot reverse-DNS we don't have). Do NOT rely on these.

**Headless verdict:** there is NO reliable way to read the full FT body from a headless/MCP run today.
Degrade to headline + `[UNAVAILABLE - paywall]`. Full-body FT reads require the user's real Chrome (chrome-use).
This matches the ladder in [[trend-stock-research]] §"How to read articles".

**Legal/ToS:** paywall bypass is ToS-gray. web.archive.org / archive.today are public archives; this is for
the owner's personal research reading only, never redistribution. Honor robots/bot-blocks; do not hammer.

## Politeness (required)

Conditional GET (ETag/If-Modified-Since; `304` → nothing-new). Exponential backoff on `429`/`5xx`, ~2 retries, then `[UNAVAILABLE]`. Sequential fetch. Respect the bot-block — do not retry aggressively.

## Normalized output record

```json
{"source":"ft","url":"https://www.ft.com/content/<id>","title":"...","published_at":"2026-06-15T...Z","summary":"[UNAVAILABLE - paywall]","lang":"en","tags":["macro"]}
```

## Failure mode

```json
{"source":"ft","status":"[UNAVAILABLE]","reason":"paywall / 403 bot-block / fetch failed"}
```

> Educational, not advice. Headlines only; never fabricate a paywalled body.
