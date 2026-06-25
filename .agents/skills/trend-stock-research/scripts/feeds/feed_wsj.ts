/**
 * Feed: Wall Street Journal (WSJ)
 * PAYWALLED — RSS gives headline + url + publisher teaser only (no body).
 * Source: Dow Jones official PUBLIC RSS on feeds.content.dowjones.io.
 *   Dow Jones migrated off feeds.a.dj.com (frozen Jan 27 2025) to this host; the new feeds carry
 *   fresh items with REAL www.wsj.com article URLs + 1-sentence teasers (verified 2026-06-25).
 *   This replaces the old Google News fallback, whose URLs were opaque redirects with no body.
 * Usage: bun .agents/scripts/feeds/feed_wsj.ts [--db path] [--days n] [--no-enrich]
 */

import { Database } from "bun:sqlite";
import type { Article, FeedResult } from "./types";
import {
  parseRSS,
  stripHtml,
  toISO,
  isWithinDays,
  parseArgs,
  normalizeUrl,
} from "./types";
import { openDb, upsertArticle, hasArticle } from "./news_db";

// Dow Jones official public RSS (new host). Markets + world + US business + tech/WSJD.
// Each returns 40-100 items with real www.wsj.com URLs and publisher teasers.
const FEED_URLS = [
  "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain",
  "https://feeds.content.dowjones.io/public/rss/RSSWorldNews",
  "https://feeds.content.dowjones.io/public/rss/WSJcomUSBusiness",
  "https://feeds.content.dowjones.io/public/rss/RSSWSJD",
];

/** Strip common suffixes WSJ/aggregators append to titles */
function cleanTitle(raw: string): string {
  return raw.replace(/\s*[-–—]\s*(The Wall Street Journal|WSJ)\s*$/i, "").trim();
}

export async function fetchWSJ(
  db: Database,
  days: number,
  _noEnrich = false,
): Promise<FeedResult> {
  const result: FeedResult = { source: "wsj", fetched: 0, inserted: 0, enriched: 0, withinWindow: 0, errors: [] };

  for (const feedUrl of FEED_URLS) {
    try {
      const resp = await fetch(feedUrl, {
        headers: { "User-Agent": "Mozilla/5.0 (compatible; FeedBot/1.0; +https://example.invalid)" },
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

        // Real www.wsj.com URL; normalize to dedup across the 4 feeds (drops ?mod= tracking).
        const url = normalizeUrl(item.link);
        if (hasArticle(db, url)) continue;

        // Body stays null — WSJ articles are paywalled. summary = publisher's own RSS teaser.
        const teaser = stripHtml(item.description);
        const article: Article = {
          source: "wsj",
          url,
          title: cleanTitle(item.title),
          summary: teaser || "[UNAVAILABLE - paywall]",
          body: null,
          published_at: publishedAt,
          lang: "en",
          tags: item.categories,
        };

        if (upsertArticle(db, article)) result.inserted++;
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
  const r = await fetchWSJ(db, days, noEnrich);
  db.close();
  console.log(`wsj: fetched=${r.fetched} window=${r.withinWindow} inserted=${r.inserted} enriched=${r.enriched} errors=${r.errors.length}`);
  if (r.fetched > 0 && r.withinWindow === 0) {
    console.warn("⚠ STALE: Dow Jones RSS returned articles but none within date window.");
  }
  if (r.errors.length) console.error("Errors:", r.errors);
  process.exit(r.errors.length ? 1 : 0);
}
