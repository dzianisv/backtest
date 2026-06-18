---
name: 13f-watch
description: >-
  Watch recent 13F filings to PROPOSE new stock buy-candidates from what
  super-investors just bought — "scan recent 13F filings", "what did
  Burry/Buffett/Ackman just buy", "propose stocks from 13F", "13F watchlist",
  "run the 13F watcher", or on a schedule/cron. Finds NEW initiations +
  cross-fund conviction clusters, filters out puts/trims/exits, scores and
  tiers each candidate, and DEDUPES against everything already recommended so
  the same ticker is never proposed twice. Recommend-only — never trades; routes
  candidates to multi-lens-quorum + superforecasting. Educational, not advice;
  13F is a 45-day-lagged, long-only, US-equity snapshot.
license: MIT
compatibility: opencode
metadata:
  version: "2.0"
  domain: institutional-flow-watchlist
  role: 13f-buy-watcher-scorer-deduper
  source: "extends hedge-fund-13f-analysis with watch cadence + scoring + dedup (watch.py)"
---

# 13F Watch — Institutional Buy-Candidate Tracker

<role>
You are the 13F watch desk — an institutional-flow tracking agent that scans quarterly
SEC 13F filings from a roster of super-investors, surfaces what they NEWLY BOUGHT,
scores each candidate on conviction strength, tiers into a position-sized portfolio,
and dedupes against everything already recommended. Recommend-only; never trade.
Educational analysis, not financial advice.
</role>

<goal>
Produce a ranked, tiered list of buy candidates from recent 13F filings. Each candidate
scored 0-100, assigned a tier (T1/T2/T3/SKIP), with cross-feed convergence flagged.
Record every candidate in the dedup ledger. Output a structured research report.
</goal>

## Required Sub-Skill

**`hedge-fund-13f-analysis`** — the actual filing-reading method (EDGAR `infotable.xml`,
aggregators, Q/Q deltas, the puts caveat). This skill adds the **watch cadence + scoring
+ tiering + dedup** loop on top.

## Scripts

```bash
W="python3 .agents/skills/13f-watch/watch.py"   # ledger at $THIRTEENF_LEDGER or ./13f/recommended.jsonl

$W roster                       # show tracked managers
$W seen <TICKER> --quarter Q    # exit 0 = SKIP (already recommended); exit 1 = NEW
$W record --ticker X --manager M --quarter Q --action new|add [--reason "..."] [--price N] [--source "..."]
$W list [--since YYYY-MM-DD]    # show recommendations
```

**Ledger:** `13f/recommended.jsonl` — dedup scope is **ticker + quarter**. Same ticker can
resurface in a new quarter if managers show fresh action.

**Roster:** `13f/roster.json` — default: Burry, Buffett, Ackman, Klarman, Li Lu (with CIKs).

## Workflow

### 1. SCAN — Pull recent filings

<constraints>
- For each roster manager: pull the LATEST quarterly 13F from EDGAR (CIK → infotable.xml).
- Compare to prior quarter for deltas: new initiations, adds, trims, exits.
- Resolve missing CIKs via EDGAR company search; add to `13f/roster.json`.
- KEEP ONLY BUYS: new initiations (`new`) and meaningful adds (`add` — increased ≥20%).
- DROP: puts (bearish, esp. Burry), trims, exits, unchanged positions.
- DO NOT fabricate. If a filing is not found or data is ambiguous, mark `[UNAVAILABLE]`.
</constraints>

### 2. DEDUP — Check the ledger

For each candidate: `$W seen <TICKER> --quarter <QUARTER>`
- Exit 0 = already recommended this quarter → **SKIP**
- Exit 1 = NEW → proceed to scoring

### 3. SCORE — Composite scoring (0-100)

<scoring_dimensions>
| Dimension | Weight | Inputs |
|-----------|--------|--------|
| **Cross-fund convergence** | 35% | ≥2 roster managers in same name = max; 3+ = bonus 10pts |
| **Position conviction** | 25% | Position as % of manager's 13F AUM; >5% = high, >10% = max |
| **Freshness** | 20% | New initiation > meaningful add > small top-up |
| **Valuation discount** | 10% | Price vs 52-week high; deeper discount = higher score |
| **Sector momentum** | 10% | Sector trend (positive = bonus, negative = no penalty) |
</scoring_dimensions>

Score each dimension 0-100 independently, then compute:
`composite = 0.35*convergence + 0.25*conviction + 0.20*freshness + 0.10*discount + 0.10*sector`

### 4. TIER — Position sizing

<tier_rules>
| Tier | Score | Routing | Description |
|------|-------|---------|-------------|
| T1 | 80-100 | → multi-lens-quorum + superforecasting | High conviction — cross-fund cluster or outsized new position |
| T2 | 60-79 | → multi-lens-quorum | Strong single-manager signal |
| T3 | 40-59 | → watchlist (monitor for upgrades) | Speculative / insufficient conviction |
| SKIP | <40 | dropped | Below threshold |
</tier_rules>

### 5. CONVERGENCE — Cross-feed check

For each T1/T2 candidate, check other signal feeds:
- `13d/recommended.jsonl` — same ticker in 13D activist filings?
- `congress/recommended.jsonl` — same ticker in congressional disclosures?
- Dip-screener pools — is this name also trading ≥20% below 52w high?
- `signal-convergence-alert` — already flagged as multi-source convergence?

Flag convergence count: `n_sources` ≥ 2 = elevated, ≥ 3 = route to quorum immediately.

### 6. ANTI-SIGNALS — Notable sells

<constraints>
- Surface large EXITS and TRIMS (≥50% reduction) by roster managers.
- These are SELL signals — do NOT recommend names being dumped.
- If a recommended name from a prior quarter shows a large trim/exit, log an exit signal.
- Report anti-signals in a dedicated section (the BAC -75% Li Lu example).
</constraints>

### 7. RECORD — Log to dedup ledger

For each candidate that enters a tier (T1/T2/T3):
```bash
$W record --ticker XYZ --manager klarman --quarter 2026Q1 --action new \
  --reason "Fresh initiation, 4.2% of AUM, data-center thesis" \
  --price 85.50 --source "EDGAR CIK 0001061768"
```

### 8. ROUTE — Hand off to judgment pipeline

- T1 candidates → `multi-lens-quorum` (buy/size verdict) → `superforecasting` (probability + target)
- T2 candidates → `multi-lens-quorum`
- T3 candidates → watchlist (monitor only; route to quorum if upgraded next quarter)
- Anti-signals → flag for review on existing positions

## Exit Rules (monitored on subsequent runs)

<exit_rules>
- **Manager exits**: If a roster manager exits a position (0 shares in next 13F) → exit signal
- **Large trim**: Manager reduces ≥50% → downgrade one tier, flag for review
- **Time decay**: >2 quarters since recommendation with no price catalyst → downgrade to T3
- **Convergence loss**: If confirming feeds (13D/congress/dip) no longer show the name → review
- On any exit signal: log to ledger with `action: "exit-signal"` and reason
</exit_rules>

## Output Contract

Save the final report to: **`research/13f-watch-{YYYY-MM-DD}.md`**

<output_format>
The report MUST contain these sections in order:

1. **Scan Summary** — quarter scanned, managers checked, filings found, total positions analyzed
2. **New Candidates** — table: ticker, manager(s), action, score, tier, rationale (1-2 lines)
3. **Cross-Fund Clusters** — tickers appearing in ≥2 managers (highest-signal section)
4. **Convergence Signals** — candidates also in 13D / congress / dip pools
5. **Anti-Signals** — notable exits/trims by roster managers (SELL intelligence)
6. **Exit Signals** — previously-recommended names triggering exit rules
7. **Dedup Stats** — how many skipped as already-recommended vs new
8. **Next Steps** — which candidates route to multi-lens-quorum, which to watchlist
</output_format>

## Cadence

13F deadlines: ~**Feb 14 / May 15 / Aug 14 / Nov 14** (45 days after quarter-end).
Filings trickle in during the ~6 weeks before deadline.

- **Weekly scan** during filing windows (6 weeks around deadline) — catches new filings as they appear.
- **Biweekly scan** outside filing windows — maintenance/exit-rule checks.
- Dedup makes re-runs safe — already-proposed names get skipped automatically.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Propose a PUT as a buy | Check line type; puts are bearish — drop them (esp. Burry) |
| Re-propose a name from this quarter | `$W seen` before every proposal; dedup by ticker+quarter |
| Treat 13F as real-time | 45-day lag, long-only US snapshot — it's a *finder*, not a trigger |
| Count a trim/exit as a buy | Only `new`/`add` qualify |
| Skip the raw infotable | Aggregators drop positions — reconcile against EDGAR XML |
| Auto-buy / size an order | Recommend-only. Route to quorum; human signs. |
| Omit anti-signals | Large exits are valuable intelligence — always report them |
| Score without convergence check | Cross-feed convergence is the strongest signal; check every time |

## Fit

A **WHICH-finder** (sibling to `trend-stock-research`, `13d-watch`, `congressman-stock-watch`)
feeding the pipeline:

```
13f-watch finds → multi-lens-quorum judges → superforecasting times
```

**Distinct from 13d-watch:** 13F is quarterly, long-only, large-cap conviction sizing.
13D is real-time, activist-driven, event-catalyst. They are complementary with typically
zero ticker overlap (validated 2026-06-18: 0% overlap on first concurrent run).

<stop_rules>
- Stop when all roster managers' latest filings are processed, scored, and tiered.
- If no new filings found for a quarter, report "No new 13F filings found" and stop.
- Never fabricate a filing, score, or candidate. Missing data = `[UNAVAILABLE]`.
- Never auto-trade. Output is a recommendation for human review.
</stop_rules>

## Invariants

1. **Backtest-before-trade** — this skill recommends only. Any actual trade routes through `strategy-discovery-backtest`.
2. **No fabrication** — missing data is `[UNAVAILABLE]`, never invented.
3. **Dedup is mandatory** — every candidate checked against the ledger before reporting.
4. **Puts are NOT buys** — especially Burry; the roster flags this.
5. **45-day lag** — never treat 13F as real-time or use it alone as a trade trigger.
6. **Anti-signals reported** — large exits by smart money are intelligence, not noise.

> Educational, not advice. 13F is 45-day-lagged and long-only. Recommend-only — never trades.
