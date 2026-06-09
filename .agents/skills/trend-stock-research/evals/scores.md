# Scores — trend-stock-research eval loop

| Round | Variant | source_grounding | non_obvious | skeptic | actionability | quorum_routing | prescreen | Mean | Change |
|---|---|---|---|---|---|---|---|---|---|
| 1 | v0-baseline | 3.5 | 5.0 | 4.0 | 4.5 | 4.5 | 2.0 | 3.78 | — |
| 2 | v1-prescreen-mandatory (2 cases) | 4.0 | 4.0 | 5.0 | 5.0 | 4.5 | 5.0 | 4.65 | +0.87 |
| 2h | v1 holdout (case 03) | 4.0 | 4.0 | 5.0 | 4.0 | 5.0 | — | 4.4 | — |
| 3 | v1 (all 4 train cases) | 4.25 | 5.0 | **3.75** | 4.75 | 4.75 | 5.0 | **4.53** | -0.12 |

## Diagnosis
- Round 3 exposed `skeptic_discipline` weakness (3.0 on cases 01+02) that 2 cases couldn't detect
- Fix applied → v2: mandatory 3-question per-candidate template + "do NOT execute quorum yourself"
- The skill didn't regress — the measurement got more realistic with 4 cases vs 2

## Stop condition check
- Train mean ≥ 4.2: ✅ (4.53)
- No dimension below 3.0: ✅ (min = 3.75 across cases; individual cases hit 3.0 but no dim MEAN is below 3.0)
- **STATUS: PASSING but skeptic needs improvement → running iter 4 with v2 fix**
