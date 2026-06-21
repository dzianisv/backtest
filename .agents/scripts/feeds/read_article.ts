#!/usr/bin/env bun
// read_article.ts — fetch full body of a (possibly paywalled) article URL.
// Usage: bun read_article.ts <url> [--no-cache]
// Ladder: cache → Wayback → direct fetch
//
// HARD PAYWALLS (no headless bypass exists as of 2026-06):
//   FT:        Wayback serves their paywall page; archive.ph requires CAPTCHA every session
//   WSJ:       Wayback works for OLDER archived articles; recent ones return 404
//   Bloomberg: Wayback works sometimes
// For hard-paywalled outlets: returns [UNAVAILABLE]; use RSS teaser only.

import { $ } from "bun";

const FETCH_PY = "/Users/engineer/workspace/backtest/.agents/scripts/feeds/fetch_article.py";

const UA =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";

const argv = process.argv.slice(2);
const url = argv.find((a) => !a.startsWith("--"));
const noCache = argv.includes("--no-cache");

if (!url) {
  console.error("Usage: bun read_article.ts <url> [--no-cache]");
  process.exit(1);
}

// Hard-paywall domains — skip all fetch attempts, return immediately
const HARD_PAYWALL_RE = /\b(ft\.com|wsj\.com|bloomberg\.com)\b/i;

function stripHtml(html: string): string {
  return html
    .replace(/<(script|style|nav|header|footer|noscript)[^>]*>[\s\S]*?<\/\1>/gi, "")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const PAYWALL_RE = /subscribe to read|sign in to read|subscription required|to continue reading/i;
const CAPTCHA_RE = /security check|captcha|cloudflare|ddos-guard|verify you are human/i;

function isValidContent(text: string): boolean {
  if (text.length < 500) return false;
  if (PAYWALL_RE.test(text)) return false;
  if (CAPTCHA_RE.test(text)) return false;
  const meaningful = text.split("\n").filter((l) => l.trim().length > 40).join(" ");
  return meaningful.length > 300;
}

async function ingest(targetUrl: string, title: string, body: string, source: string) {
  await $`python3 ${FETCH_PY} --ingest --url ${targetUrl} --title ${title} --body ${body} --source ${source}`
    .quiet()
    .nothrow();
}

// 1. Cache check
if (!noCache) {
  try {
    const cached = await $`python3 ${FETCH_PY} --by-url ${url}`.json();
    if (cached?.body && !cached.body.startsWith("[UNAVAILABLE")) {
      process.stdout.write(cached.body);
      process.exit(0);
    }
  } catch {
    // cache miss — continue
  }
}

// Hard paywall: no method works headlessly — skip all fetches
if (HARD_PAYWALL_RE.test(url)) {
  const outlet = url.match(HARD_PAYWALL_RE)?.[1] ?? "outlet";
  process.stderr.write(`[UNAVAILABLE - ${outlet} hard paywall: no headless bypass available. Use RSS teaser only.]\n`);
  process.exit(1);
}

// 2. Wayback Machine — works for older WSJ/Bloomberg/open-web articles
async function tryWayback(targetUrl: string): Promise<string> {
  const resp = await fetch(`https://web.archive.org/web/2/${targetUrl}`, {
    headers: { "User-Agent": UA },
  });
  if (!resp.ok) throw new Error(`Wayback HTTP ${resp.status}`);

  // Guard: ensure Wayback didn't redirect to a different domain
  const finalUrl = resp.url;
  const targetDomain = new URL(targetUrl).hostname.replace(/^www\./, "");
  if (!finalUrl.includes(targetDomain)) {
    throw new Error(`Wayback: redirected away from ${targetDomain} → ${finalUrl}`);
  }

  const html = await resp.text();
  const text = stripHtml(html).substring(0, 8000);
  if (!isValidContent(text)) throw new Error("Wayback: paywall or invalid content");
  const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  const title = titleMatch ? titleMatch[1].trim() : "";
  await ingest(targetUrl, title, text, "wayback");
  return text;
}

// 3. Direct fetch — for open/soft-paywall sites (Reuters, CNBC, Coindesk, etc.)
async function tryDirect(targetUrl: string): Promise<string> {
  const resp = await fetch(targetUrl, { headers: { "User-Agent": UA } });
  if (!resp.ok) throw new Error(`Direct HTTP ${resp.status}`);
  const html = await resp.text();
  const text = stripHtml(html).substring(0, 8000);
  if (!isValidContent(text)) throw new Error("Direct: paywall or invalid content");
  const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  const title = titleMatch ? titleMatch[1].trim() : "";
  await ingest(targetUrl, title, text, "direct");
  return text;
}

const methods = [tryWayback, tryDirect];
const errors: string[] = [];
for (const method of methods) {
  try {
    process.stdout.write(await method(url));
    process.exit(0);
  } catch (e) {
    errors.push(String(e));
  }
}

process.stderr.write(`[UNAVAILABLE - all methods failed for ${url}]\n`);
for (const e of errors) process.stderr.write(`  ${e}\n`);
process.exit(1);
