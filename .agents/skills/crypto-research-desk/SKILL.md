---
name: crypto-research-desk
description: Consolidate raw gather-seat data into ONE clean, sourced crypto market brief (the evidence file a panel reasons over). Use in the Consolidate phase of the crypto research workflow. Triggers — "consolidate the brief", "merge the data seats", crypto-panel Consolidate phase. Produces evidence only, no recommendations.
license: MIT
compatibility: opencode
metadata:
  role: synthesis
  domain: crypto-research
---

# Crypto research desk — consolidate the brief

Merge the raw data seats into ONE dense, factual brief on the asset/portfolio in question, as of the given date. **No recommendations** — this is the evidence the panel debates.

## Sections (in order)
1. **QUESTION & PORTFOLIO** — restate the user's question + current holdings/exposure verbatim so every downstream seat sees it.
2. **PRICE & TREND** · 3. **ON-CHAIN VALUATION** · 4. **DERIVATIVES / POSITIONING** · 5. **MACRO (CPI/FOMC/rates)** · 6. **LIQUIDITY FLOWS** (MUST include a **Spot-BTC-ETF net-flow** line — write `[UNAVAILABLE]` + §11 entry if the onchain seat couldn't fetch it; never omit) · 7. **SENTIMENT / REGIME** · 8. **NEWS / NARRATIVE** (events + source-count + priced-in tag; `[UNAVAILABLE]` if no news seat ran) · 9. **PREDICTION-MARKET ODDS** · 10. **CROSS-SOURCE CONFLICTS** · 11. **DATA GAPS**.

## Rules
- Every number keeps its `as-of` + `source`. Quote, don't paraphrase, priced probabilities.
- **Completeness contract:** if a required category is `[UNAVAILABLE]`, write `[UNAVAILABLE — <category> seat failed to return]` in its section AND list it in §11 DATA GAPS at the top. Never paper over a gap.
- Surface conflicts (e.g. liquidity expanding vs contracting) in §10; do not average them away.
- **Canonical-number rule (one metric → one value).** When two seats report the SAME metric with different numbers (e.g. HYPE annualized revenue $880M vs $792M, SOL realized price, MVRV, 200-week MA, BTC realized price), §10 MUST resolve each into a single **canonical value** the rest of the brief uses everywhere: pick the most-authoritative/most-recent source (or, for an irreducible spread, an explicit point estimate like the midpoint) and write `→ DESK CANONICAL: <value> (chose <source>; range <a>–<b>)`. Every other section, and especially any threshold a verdict/invalidation could hang on, must then quote that ONE canonical number — never a second value. A metric appearing with two different numbers in two sections is a defect, not honesty.
- Be dense and neutral. No verdicts, no sizing, no "should."

## Done when
All 11 sections present; every figure sourced + dated; gaps and conflicts explicit.
