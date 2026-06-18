---
session: ses_1269
updated: 2026-06-18T08:04:41.866Z
---

# Session Summary

## Goal
Rewrite both `13f-watch/SKILL.md` and `13d-watch/SKILL.md` to share a unified structure (same scoring model, tiering, output contract, convergence protocol, exit rules, anti-signals) using the `write-skill` methodology.

## Constraints & Preferences
- Use `/write-skill` skill principles (outcome-defined, XML-structured where beneficial, imperative, lean, self-verifying)
- Both skills must share: same report sections, same tiering (T1/T2/T3/SKIP), same output contract format (`research/{skill-name}-{YYYY-MM-DD}.md`), cross-skill convergence protocol
- Skills are recommend-only — never trade, route to quorum
- 13F tooling is Python (`watch.py`); 13D tooling is TypeScript (`watch.ts`, `score.ts`, `tier.ts`) — both use JSONL ledgers
- Ledger dedup scope: ticker + quarter (13F) or ticker + filing-date (13D)

## Progress
### Done
- [x] Ran first 13f-watch scan (Q1 2026) — report at `research/13f-watch-2026-06-18.md`
- [x] Cross-evaluated 13D vs 13F results (complementary, zero overlap)
- [x] Identified all improvements needed for both skills (6 for 13F, 5 for 13D, 3 shared)
- [x] Read current `13f-watch/SKILL.md` (full content loaded — 263 lines, lacks scoring/tiering/output-contract/exit-rules/anti-signals/convergence)
- [x] Read both skill directories via subagent — confirmed tooling files exist
- [x] Loaded `write-skill` skill for methodology

### In Progress
- [ ] Rewriting `13f-watch/SKILL.md` — unified structure, scoring, tiering, output contract, convergence
- [ ] Rewriting `13d-watch/SKILL.md` — align to same unified structure, fix script-reality gap

### Blocked
- (none)

## Key Decisions
- **Unified scoring model**: 13F gets its own composite score (cross-fund count, % of AUM, new-vs-add, sector momentum, beaten-down discount) mirroring 13D's 0-100 approach (conviction 35%, catalyst 25%, timing 20%, technical 10%, risk 10%)
- **Tiering**: T1 = cross-fund cluster (≥2 managers) or score ≥75; T2 = large single-manager new initiation or score 50-74; T3 = meaningful adds or score 25-49; SKIP = below threshold
- **Convergence protocol**: Each skill checks the other's ledger; shared `convergence.jsonl` records cross-hits
- **Anti-signals section**: Explicitly surface bearish signals (>50% trims, full exits) in both reports
- **Exit rules for 13F**: Manager trims >50% next quarter → exit signal; all managers exit → hard exit
- **13D scripts marked as working**: They exist and run with `node --experimental-strip-types`; SKILL.md should reflect reality

## Next Steps
1. Write the new `13f-watch/SKILL.md` with unified structure (scoring, tiering, output contract, convergence, anti-signals, exit monitoring)
2. Write the new `13d-watch/SKILL.md` aligned to same structure (fix EDGAR URL fragility note, add staleness handling, make heavy sub-skill deps optional)
3. Verify both pass write-skill self-audit checklist (no orphan refs, verbs over nouns, exit criteria clear, etc.)
4. Optionally define shared convergence schema (`convergence.jsonl` format)

## Critical Context
- **13F roster** (5 managers): Burry (CIK 0001649339), Buffett (0001067983), Ackman (0001336528), Klarman (0001061768), Li Lu (0001709323)
- **13F watch.py commands**: `roster`, `seen <TICKER> --quarter`, `record --ticker --manager --quarter --action`, `list [--since]`
- **13D watch.ts commands**: `roster`, `seen <TICKER>`, `record --ticker --filer --filed --action --schedule --score --tier`, `list [--since]`
- **13D scoring weights (current)**: Conviction 35%, Catalyst 25%, Timing 20%, Technical 10%, Risk 10%
- **13F SKILL.md is 263 lines** — has detailed EDGAR pull workflow, puts caveat, manager roster section, but NO scoring/tiering/output-contract/exit/anti-signal/convergence sections
- **13D SKILL.md** already has scoring, tiering, exit rules, output contract — needs alignment to shared format plus staleness/fragility fixes
- **Live results from first 13F run**: MU (Klarman+Li Lu), AMZN (Ackman+Klarman+Buffett), VRT (Klarman new), QRVO (Klarman new), BAC anti-signal (Li Lu -75%)

## File Operations
### Read
- `/Users/engineer/workspace/backtest/.agents/skills/13f-watch/SKILL.md` (full content, 263 lines)
- `/Users/engineer/workspace/backtest/.agents/skills/13f-watch/watch.py` (via subagent)
- `/Users/engineer/workspace/backtest/.agents/skills/13d-watch/SKILL.md` (via subagent)
- `/Users/engineer/workspace/backtest/.agents/skills/13d-watch/watch.ts` (via subagent)
- `/Users/engineer/workspace/backtest/.agents/skills/13d-watch/score.ts` (via subagent)
- `/Users/engineer/workspace/backtest/.agents/skills/13d-watch/tier.ts` (via subagent)

### Modified
- (none yet in this phase — rewrites are next)
