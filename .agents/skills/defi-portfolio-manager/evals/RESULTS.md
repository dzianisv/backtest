# Eval results — defi-portfolio-manager

Method: 5 fixed scenarios ([scenarios.md](scenarios.md)) run by independent PM agents operating under the
skill, scored by an independent judge agent against a fixed 8-dimension rubric ([rubric.md](rubric.md),
40 pts/scenario). Only the SKILL.md changes between iterations; scenarios, rubric, and judge are held
constant. Prompting changes grounded in Anthropic's prompt-engineering best-practices guide.

## Score trajectory (mean of 5 scenarios, /40)

| Version | S1 | S2 | S3 | S4 | S5 | **Mean** | % |
|---|----|----|----|----|----|------|---|
| v1.0 (baseline) | 33 | 34 | 33 | 34 | 32 | **33.2** | 83% |
| v1.1 | 39 | 40 | 39 | 40 | 40 | **39.6** | 99% |
| v1.2 | 40 | 40 | 39 | 40 | 40 | **39.8** | 99.5% |
| v1.3 | — | — | — | — | — | (chain-cap clarification; not re-scored) | — |

## What each iteration changed (weakness → fix)

**v1.0 → v1.1** (judge weaknesses: uneven actionability; live data read as fact; incident scan only when an
exploit is named; caps implied not shown):
- Added a **strategic "How to think" frame** (survival-first; decompose every yield into a *named* risk premium; barbell; diversify across failure domains; size for the worst case) — the strategic-reasoning layer.
- Mandated a **deliverable format** that always ends in concrete from→to tickets, even for a "reject."
- Made the **incident scan run for every venue** proposed/held/rejected, dated.
- Required every figure **tagged with source + verify/re-pull caveat**.
- Made caps an **explicit checklist** with a held instant-liquidity reserve line.
- Added a worked **`<example>`** (multishot) anchoring format + reasoning.

**v1.1 → v1.2** (judge weakness: a recommended table breached the ≤25%/issuer cap, self-flagged but not fixed):
- Added a **cap-validator: DETECT → AUTO-CORRECT → recheck before emitting** — never ship a cap-breaching table.
- Added a **≤25% per issuer/sponsor family** cap and a **coupled-exposure rule** (PSM pairs like USDS↔USDC, same stablecoin family, same curator/oracle count as ONE bet).
- **Uniform decomposition** — same base/reward/collateral rigor for chosen venues as for rejected ones.
- **Provenance labels** — any figure not freshly pulled marked "unverified — confirm before sizing."

**v1.2 → v1.3** (judge nit: one scenario soft-noted a chain limit instead of hard-correcting; partly a judge
misread since Base is a main chain):
- Clarified the auto-correct loop applies uniformly to all cap classes, and that the ≤10% chain cap excludes Ethereum/Base.

## v2.x — moderate-risk hedge-fund TEAM (new rubric)

The skill was rebuilt as a team (orchestrator + specialist subagents) at MODERATE risk, so the rubric
was retuned (added **D1 team-delegation** and **D3 moderate-fit**; gate on signing). Scores are on this
NEW rubric — not comparable to the v1.x conservative numbers above.

| Version | scenarios | Mean /40 | Note |
|---|---|---|---|
| v2.0 | S1, S5, S6 | **39.0** (S1 38, S5 39, S6 40) | Team delegation scored 5/5 on all three out of the gate |
| v2.1 | S1 re-run | **37** | Fixed the targeted over-timid regression (directional 15%→28%, now in-band) but surfaced new dings: messy breach-then-correct cap table, blended ~4.4% under the 5–7% target, no per-yield premium tags |
| v2.2 | (pending re-score next tick) | — | Applied the three v2.1 fixes: caps compliant in first pass (no breach-then-correct), blended-yield gate (5–7%), named-premium tag per position |

**Honest read:** near the ceiling the loop is non-monotonic and judge-noise-dominated (37–40). Each fix
exposes the next layer — exactly what a real self-improvement loop looks like. v2.2 is applied but not
yet re-scored; the next autonomous tick verifies it and continues toward plateau.

## Reproduce

Run each scenario in [scenarios.md](scenarios.md) via a fresh agent told to operate under
`../SKILL.md`, then score the outputs against [rubric.md](rubric.md) with a judge agent. The skill file
is the only variable.
