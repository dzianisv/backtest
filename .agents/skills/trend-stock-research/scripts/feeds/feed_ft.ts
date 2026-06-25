/**
 * Feed: Financial Times (FT)
 * PAYWALLED — native section RSS gives headline + REAL ft.com/content URL + a 1-sentence teaser
 * (CDATA <description>); bodies stay paywalled. Endpoints: `ft.com/<section>?format=rss` (verified
 * 2026-06-25). The old ft.com/rss/home is dead (301 → stale stub). When a teaser is absent the summary
 * falls back to [UNAVAILABLE - paywall] (never fabricated).
 * Optional Wayback enrichment for body (usually blocked by FT's subscribe-wall — best-effort only).
 * Usage: bun .agents/scripts/feeds/feed_ft.ts [--db path] [--days n] [--no-enrich]
 */

import { Database } from "bun:sqlite";
import type { Article, FeedResult } from "./types";
import {
  parseRSS,
  stripHtml,
  toISO,
  isWithinDays,
  parseArgs,
  sleep,
  fetchWaybackBody,
  normalizeUrl,
} from "./types";
import { openDb, upsertArticle, hasArticle } from "./news_db";

// FT native section RSS — real ft.com/content/<uuid> URLs + a 1-sentence publisher teaser.
const FEED_URLS = [
  "https://www.ft.com/markets?format=rss",
  "https://www.ft.com/companies?format=rss",
  "https://www.ft.com/global-economy?format=rss",
  "https://www.ft.com/world?format=rss",
];

export async function fetchFT(
  db: Database,
  days: number,
  noEnrich = false,
): Promise<FeedResult> {
  const result: FeedResult = { source: "ft", fetched: 0, inserted: 0, enriched: 0, withinWindow: 0, errors: [] };

  for (const feedUrl of FEED_URLS) {
    try {
      const resp = await fetch(feedUrl, {
        headers: { "User-Agent": "FeedBot/1.0 (news aggregator)" },
      });
      if (!resp.ok) {
        result.errors.push(`HTTP ${resp.status} from ${feedUrl}`);
        continue;
      }

      const xml = await resp.text();
      const items = parseRSS(xml);
      result.fetched += items.length;

      for (const item of items) {
        if (!item.link) continue;
        const publishedAt = toISO(item.pubDate);
        if (!isWithinDays(publishedAt, days)) continue;
        result.withinWindow++;

        // Real ft.com/content URL; normalize to dedup across sections (drops tracking params).
        const url = normalizeUrl(item.link);
        // Skip enrichment + insert for articles already in DB
        if (hasArticle(db, url)) continue;

        let body: string | null = null;
        if (!noEnrich) {
          body = await fetchWaybackBody(url);
          await sleep(1000); // polite delay between Wayback requests
        }

        // FT ships a CDATA teaser; fall back to paywall marker only if it's ever absent.
        const teaser = stripHtml(item.description);
        const article: Article = {
          source: "ft",
          url,
          title: item.title,
          summary: teaser || "[UNAVAILABLE - paywall]",
          body,
          published_at: publishedAt,
          lang: "en",
          tags: item.categories,
        };

        if (upsertArticle(db, article)) {
          result.inserted++;
          if (body) result.enriched++;
        }
      }
    } catch (e: unknown) {
      result.errors.push(e instanceof Error ? e.message : String(e));
    }
  }

  return result;
}

// ── Standalone entry point ──────────────────────────────────────────────────

if (import.meta.main) {
  const { dbPath, days, noEnrich } = parseArgs();
  const db = openDb(dbPath);
  const r = await fetchFT(db, days, noEnrich);
  db.close();
  console.log(`ft: fetched=${r.fetched} inserted=${r.inserted} enriched=${r.enriched} errors=${r.errors.length}`);
  if (r.fetched > 0 && r.withinWindow === 0) {
    console.warn("⚠ STALE: RSS returned articles but none within date window.");
  }
  if (r.errors.length) console.error("Errors:", r.errors);
  process.exit(r.errors.length ? 1 : 0);
}
