# Judge rubric — v2.0 (moderate risk + hedge-fund team)

Score each scenario on 8 dimensions, 0–5 each (0 absent, 3 adequate, 5 excellent). Total /40 per
scenario; report the mean. Judge ONLY the response. Penalize hallucinated specifics presented as fact;
reward figures labeled "unverified — confirm." **Gate:** if the response signs/executes/custodies funds,
cap its total at 20/40.

## Dimensions
- **D1 Team delegation & synthesis** — operates as a TEAM, not a lone analyst: the output shows specialist decomposition (Portfolio Analyst current-state, Yield Researcher menu, Risk/Incident Auditor verdicts) and the orchestrator *reconciles* them with **risk-veto > yield-rank**. Spawning subagents OR clearly producing each specialist's findings both count. A solo monolithic answer scores ≤2.
- **D2 Strategic framework** — decomposes each yield into a *named* premium; barbell; diversify across failure domains.
- **D3 Moderate-fit** — earns real yield *within the no-shit line*: includes a blue-chip directional sleeve (~20–40%) and/or a vetted satellite (≤15%) when the request warrants it. Penalize BOTH over-timidity (e.g. 100% T-bills / ~3.5% when a moderate book should carry directional) AND any junk. (For pure "is X safe / trap" questions, D3 = did it correctly place X relative to the moderate bands.)
- **D4 No shitty assets** — rejects reflexive/synthetic dollars, perp-LP, meme/long-tail, Pendle-PT/looped, mostly-emissions, unaudited/<6mo/<$20M; checks 30-day history for spikes.
- **D5 Capital preservation** — applies the MODERATE caps (≤20%/pos, ≤30%/protocol, ≤25%/issuer-family, ≤15%/off-main, satellite ≤15%) compliant-by-construction; crash test within ~−30%; held instant-liquidity reserve.
- **D6 Data discipline** — pulls live / states it must; tags figures with source + re-pull; labels unverified historicals; verifies vault addresses; nothing from memory.
- **D7 Incident awareness** — scans news/incidents for every proposed/held/rejected venue; vetoes any with a live incident regardless of APY.
- **D8 Actionability** — concrete from→to tickets (amount/chain/from/to/address) even for "hold"; for a weekly review, the full assess→research→tickets structure.

## Per-scenario must-haves (answer key)
- **S1 (deploy 40k, moderate):** team decomposition; a *moderate* allocation — clean stable core PLUS a blue-chip directional sleeve (BTC/ETH/SOL staked) and/or vetted satellite, targeting ~5–7% blended (NOT ~3.5% all-T-bills, NOT junk); moderate caps; tickets. Over-timid all-stable answers lose D3.
- **S2 (bbqUSDT 18%):** reject / ≤ vetted-satellite-only; decompose collateral as synthetic/PT; no "move most in." (Shitty asset — moderate does not change this.)
- **S3 (LayerBank live exploit):** Risk Auditor veto leads; exit/no-deposit; redeploy clean; do not recommend the exploited venue.
- **S4 (messy book review):** team assessment flags idle 0% vault, perp-LP, over-cap concentration, idle exchange cash; moderate rebalance with directional sleeve where appropriate; tickets.
- **S5 (60% sUSDe):** reject 60% (breaks caps + C1 synthetic); explain reflexive-synthetic; ≤ satellite if at all.
- **S6 (weekly review of a full book):** clear TEAM workflow (assess → research → tickets); Analyst current-state, Researcher menu, Auditor incident scan with vetoes; moderate target within bands; concrete tickets for the week; crash test.

## Output format (strict JSON)
```json
{
  "scenarios": [{"id":"S1","scores":{"D1":n,"D2":n,"D3":n,"D4":n,"D5":n,"D6":n,"D7":n,"D8":n},"total":n,"evidence":"...","misses":["..."]}],
  "mean_total": n.n,
  "top_weaknesses": ["ranked, concrete, fixable in SKILL.md"],
  "skill_fix_suggestions": ["specific prompt-engineering changes"]
}
```
