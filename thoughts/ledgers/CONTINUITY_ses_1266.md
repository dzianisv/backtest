---
session: ses_1266
updated: 2026-06-18T07:30:14.731Z
---

# Session Summary

## Goal
Scan SEC EDGAR for 13D/13G filings from 2026-06-11 to 2026-06-18, score/tier them, and produce a final markdown report saved to `research/13d-watch-2026-06-18.md`.

## Constraints & Preferences
- Never fabricate data — if EDGAR returns nothing, say so
- Mark unavailable fields as `[UNAVAILABLE]`
- Recommend-only — never suggest executing trades
- Skip SPACs, blank-check companies, and obvious low-signal filings
- Roster activists (Icahn, Ackman, Loeb, Singer, Peltz, Starboard, JANA, ValueAct, Buffett, Burry) get immediate attention
- Use `search-index` endpoint with `q=%2213D%22` (NOT `forms=` parameter which returns 0 hits); filter client-side by `root_forms` containing "SCHEDULE 13D"
- Workspace root: `/Users/engineer/workspace/backtest`

## Progress
### Done
- [x] Read SKILL.md and all scripts (watch.ts, score.ts, tier.ts)
- [x] Ran `watch.ts roster` — 10 activists tracked (Icahn, Ackman, Loeb, Singer, Peltz, Starboard/Jeff Smith, JANA/Rosenstein, ValueAct/Ubben, Buffett, Burry)
- [x] Ran `watch.ts list` — 16 existing ledger entries already recorded on 2026-06-18 (JACK, LAB, CVEO, DBI, FAC, GOSS, CMTL, NEXT, LFTO, and others)
- [x] Fetched EDGAR search-index: 910 total hits, 100 returned; parsed into 23 new initial 13D filings and amendments
- [x] Filtered results: identified notable new filings vs SPACs/low-signal
- [x] Dedup check all candidates: LAB, DBI, TBBB, FAC, GRTX, LFTO = SEEN (exit 0); STWI, HWKE, VRXA, NCI, BRUN = NEW (exit 1)
- [x] Checked for roster activist amendments — **none found** this week
- [x] Notable non-roster amendments found: Mill Road/LCUT, Juniper/LINC, Cochlear/NYXH, Redmile/STTK, TCV/PAYO, Engine Capital/CVEO
- [x] Fetched VRXA filing XML: European Molecular Biology Laboratory filing; pharmaceutical sector, Zurich-based biotech
- [x] Fetched STWI filing XML: Artikkhodjaev from Tashkent/Uzbekistan filing on StageWise Strategies Corp (Nevada, tiny company) — low signal
- [x] Fetched NCI filing XML: Eva Yuk Yin Siu / Asset Empire International filing on Neo-Concept International Group Holdings (Hong Kong garment company) — insider/founder filing
- [x] Checked BRUN (Boost Run Inc.): B. Luke Weil filer, Bogota/Northbrook, DE incorporated — appears to be a micro-cap shell

### In Progress
- [ ] Evaluate quality of 5 NEW filings (STWI, HWKE, VRXA, NCI, BRUN) — preliminary assessment shows all are low-signal micro/nano-cap filings
- [ ] Need to score any worthy new candidates via `score.ts`
- [ ] Need to tier all candidates via `tier.ts`
- [ ] Need to produce and save final markdown report

### Blocked
- (none)

## Key Decisions
- **Skip STWI, HWKE, NCI, BRUN as low-signal**: All are nano/micro-cap shells or insider filings with no activist catalyst; no institutional filer of note
- **VRXA multiple filers noted but likely post-SPAC/de-SPAC restructuring**: 4 separate filings from different entities (EMBL, Xlife Sciences, Schoeni, Deck) all on same company, appears to be initial ownership disclosures post-transaction
- **Already-recorded filings are the high-quality ones this week**: JACK (Engine Capital), LAB (Viking Global), CVEO (Engine Capital), DBI (Stone House), FAC (Mercedes-Benz/Stellantis convergence), LFTO (General Atlantic), GOSS (D.E. Shaw), CMTL (Outerbridge), NEXT (GAP Holdings)
- **No roster activists filed this week**: Zero 13D or 13D/A from any of the 10 tracked activists

## Next Steps
1. Confirm no new scoreable candidates from the 5 NEW tickers (all low-signal) — or score VRXA if worth including as a pharma play
2. Use existing 16 ledger entries as the candidate pool for the report
3. Run `tier.ts` with `--portfolio-value 1000000` on the existing scored candidates (pipe JSON array)
4. Produce final markdown report with: scan summary (910 hits, 23 new 13D, 5 unseen but low-quality), candidate details from ledger, tiering results, convergence signals (FAC has 3 filers), and next steps
5. Save report to `research/13d-watch-2026-06-18.md`

## Critical Context
- EDGAR raw output saved at: `/Users/engineer/.local/share/opencode/tool-output/tool_ed99e54a9001PCHITlZsCGj1R6` (JSON, 72K+ bytes)
- The `search-index` endpoint with `startdt`/`enddt` works (returns 200) but `dateRange=custom` param is required; plain `startdt/enddt` without `dateRange` returns 500
- Existing ledger top scores: JACK=73, LAB=72, CVEO=71, LFTO=73, FAC=73 (all T2)
- Convergence signal: FAC (Factorial Energy) has 3 separate 13D filers (Mercedes-Benz, Stellantis, Huang Siyu) — strong convergence
- Engine Capital filed on both JACK and CVEO — same activist, two positions = pattern signal
- All 16 existing ledger entries were recorded on 2026-06-18 (today's prior run)

## File Operations
### Read
- `/Users/engineer/workspace/backtest/.agents/skills/13d-watch/SKILL.md`
- `/Users/engineer/workspace/backtest/.agents/skills/13d-watch/watch.ts`
- `/Users/engineer/workspace/backtest/.agents/skills/13d-watch/score.ts`
- `/Users/engineer/workspace/backtest/.agents/skills/13d-watch/tier.ts`
- `/Users/engineer/.local/share/opencode/tool-output/tool_ed99e54a9001PCHITlZsCGj1R6` (EDGAR JSON response)
- Multiple EDGAR filing XMLs fetched via webfetch (VRXA, STWI, NCI, BRUN index pages)

### Modified
- (none yet — report not yet written)
