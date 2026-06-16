# Self-improvement loop — final architecture (researched + proven)

The fully self-contained "one workflow runs the target N times and edits itself" does **not** work in this
runtime, and shouldn't anyway. Two walls, both real:

1. **Runtime:** a workflow cannot nest a heavy target — `workflow(name)`→null, `workflow({scriptPath})`→throws.
   So the loop cannot self-run the target.
2. **Methodological:** a self-graded, pointwise LLM-judge is unreliable AND it's the reward-hack the user caught
   (inflated 76→94). Pointwise absolute scores cluster/fluctuate — they gave iter1=88/iter4=89, then 63.5/64,
   never separating a news-FAILED report from a complete one.

## The architecture that works (orchestrated, not self-contained)

```
SUPERVISOR (main agent) drives the loop:
  1. run target           -> Workflow tool (research-crypto-market / research-stock-market)   [WORKS]
  2. REFLEXION (diagnose)  -> judges critique baseline report -> name single weakest skill
  3. DSPy (propose)        -> K instruction rewrites of that ONE skill (separate proposer agent)
  4. apply candidate       -> write skill, re-run target via Workflow tool -> candidate report
  5. SELECT (pairwise)     -> pairwise-eval.js: N blind judges pick candidate vs baseline,
                              position-randomized, majority vote                                [PROVEN]
  6. accept iff candidate wins the majority -> commit (HUMAN GATE before merge)
  7. ground truth          -> forecast-ledger Brier score over weeks/months (the real arbiter)
```

Roles stay separated (judge ≠ proposer ≠ executor) — no self-grading.

## Why pairwise (the key fix)

Research (Zheng 2023 / MT-Bench / AlpacaEval; see survey): LLM judges are far more stable comparing two
outputs than assigning an absolute score — relative comparison needs no calibrated scale and tracks human
preference better. So **selection** (accept/reject) uses pairwise, not a 0-100 number.

**Proof (this session):** `pairwise-eval.js` on iter1 (news seat failed) vs iter4 (complete), 5 judges,
order swapped by index → **iter4 won 5–0**, every judge citing the failed news seat. Pointwise on the same
pair gave 88 vs 89 and 63.5 vs 64 — no separation. Pairwise is the reliable selection signal.

## Components (all committed, on branch crypto-workflow-research)

| File | Role | Status |
|---|---|---|
| `crypto/workflows/research-crypto-market.js` | crypto research target | proven (ran 4×) |
| `crypto/workflows/research-stock-market.js` | equity research target | proven (NVDA run, report+ledger verified) |
| `crypto/workflows/pairwise-eval.js` | blind A/B selection | **proven 5–0** |
| `crypto/workflows/blind-eval.js` | pointwise scoring | kept as a coarse signal only — do NOT use for selection |
| `crypto/workflows/improve-workflow.js` | self-contained loop | BLOCKED by nesting; superseded by this orchestrated procedure |

## What's NOT done (honest)

The end-to-end auto cycle (propose → edit → re-run → pairwise → auto-commit) is not wired as a single button —
it's the supervisor procedure above, because target runs must be external. The hard, uncertain part (a
trustworthy blind selection that discriminates) is built and proven; the rest is Workflow-tool orchestration.
