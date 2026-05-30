# Crypto Portfolio — GOAL

> **Educational analysis only — not financial advice.** APYs/balances pulled live from DefiLlama and
> protocol APIs (last: **2026-05-30**) and move hourly. Verify against your own wallet before acting.
> Read-only research mandate: **never** custody keys or sign transactions — the investor executes.

## The mission

Find and continuously maintain the **optimal allocation** of a live **~$177k multi-chain crypto book**
for a conservative, bubble-defensive investor — then prove it is optimal, and keep it there as rates move.

"Optimal" is not "I moved the idle cash somewhere better." It is a **specific, defended target weight for
every dollar**, derived from the full eligible opportunity set under explicit constraints, such that you
**cannot raise expected risk-adjusted return without breaking a constraint or lowering collateral quality.**

## The optimization problem (well-defined)

**Decision variables.** A weight `wᵢ ≥ 0` for each eligible venue/asset `i`, with `Σ wᵢ = 1` (of investable capital).

**Two layers** (solve top-down):

1. **Strategic sleeves** — the split across `{clean-stable-yield, ETH, SOL, BTC, gold, satellite}`. Driven by
   the **bubble-defense mandate and the investor's risk tolerance/horizon/liquidity needs**, not by yield.
   This layer is a *policy choice*, not a free optimization — it needs the investor inputs below.
2. **Within the stable sleeve** — a true constrained yield-maximization (a linear program):
   **maximize** `Σ wᵢ · r_netᵢ` **subject to** the constraints below, where `r_netᵢ` = live APY net of expected
   loss, gas, and protocol fees.

**Objective.** Maximize expected **net** blended yield on the cash sleeve and risk-adjusted total return overall,
where the directional sleeve is sized for *survival in a crash*, not for yield.

**Hard constraints (a position is ineligible or capped if it violates any):**

| # | Constraint | Current setting (tunable) |
|---|---|---|
| C1 | **Collateral whitelist.** Every yield position backed only by T-bills, BTC, ETH, SOL-staking, or overcollateralized loans against those. No reflexive/synthetic dollars (sUSDe, stcUSD, reUSD…), no PT/looped/long-tail, no perp-LP in the core. | per [`10-crypto-lp-yield-state.md`](../research/10-crypto-lp-yield-state.md) checklist |
| C2 | **Position concentration** ≤ X% of book in any one vault/pool | 15% |
| C3 | **Protocol concentration** ≤ Y% across all pools of one protocol | 25% |
| C4 | **Chain concentration** ≤ Z% per chain outside Ethereum/Base | 10% |
| C5 | **Capacity** — deposit ≤ 10% of a pool's TVL (avoid rate impact) | 10% of TVL |
| C6 | **Liquidity** — ≥ L% of the book redeemable within D days (respect Maple/notice windows) | *needs investor input* |
| C7 | **Satellite cap** — high-risk/perp-LP/points positions ≤ S% total, sized so a total loss is survivable | 5% |
| C8 | **Sleeve bands** — stable / ETH / SOL / BTC / gold / satellite within target ranges | *needs investor input* |

**Definition of optimal (the stop condition).** The allocation is optimal when it sits **on the efficient
frontier for this mandate**: no feasible reallocation raises expected net yield (stable sleeve) or improves the
risk/return of the whole book without violating C1–C8. Equivalently — every stable dollar earns ≥ the clean
frontier (~4.5–4.7%) or has a documented reason it can't, and no constraint is breached.

## Required investor inputs (without these, "optimal" is undefined)

These are policy choices only the investor can make — they set C6, C8, and the satellite appetite:

- [ ] **Risk tolerance** — max tolerable drawdown on the *whole* book in a crypto/AI crash (e.g. −15%? −30%?).
- [ ] **Time horizon** — when, if ever, is this capital needed?
- [ ] **Liquidity need** — how much must be withdrawable within 1 / 7 / 30 days?
- [ ] **Stable vs directional split** — target % in yield-bearing stables vs blue-chip crypto upside.
- [ ] **KYC willingness** — open to RWA tokenized-T-bill products (BUIDL/USTB/USDY) that require onboarding? They're the genuinely-safest ~3.5% tier but gated.
- [ ] **Per-protocol trust caps** — any protocol you want hard-limited or excluded regardless of yield.
- [ ] **Self-custody preference** — willing to move blue-chip spot (SOL/ETH) off exchanges/perp venues to cold storage?

## Success criteria (how we know the goal is reached)

- [ ] **Opportunity set enumerated** — the full menu of C1-passing venues across all held chains *and* the obvious unheld ones (Aave, Spark/sUSDS, clean Morpho vaults per chain, Maple, RWA T-bills, ETH LSTs, SOL LSTs, BTC-collateralized lending), each with live APY, TVL/capacity, and liquidity terms.
- [ ] **Investor inputs captured** (the checklist above) so C6/C8 are numbers, not blanks.
- [ ] **Target weights computed** by the two-layer optimization, with each weight traceable to a constraint or a yield rank.
- [ ] **Crash-validated** — the target survives a scenario test (BTC/ETH −60%, a stablecoin depeg, a venue freeze) within the C-row drawdown/liquidity limits.
- [ ] **Transition plan** — exact from→to tickets with gas/fee/tax cost, and net uplift > transition cost.
- [ ] **Instrumented** — [`portfolio.py`](portfolio.py) reports current weights vs target and the drift, monthly.

## Current status — ⚠️ GOAL NOT YET REACHED

Done so far (necessary, not sufficient):
- ✅ **Audited** the live book (2 research subagents vs DefiLlama/Morpho). Findings below.
- ✅ **Built the tracker** ([`portfolio.py`](portfolio.py)) — live value, blended yield, idle capital, concentration.
- ✅ **Interim "stop-the-bleeding" target** — reactivate idle cash to the clean frontier (the model below).

Still missing to actually *reach* an optimum:
- ❌ The **full eligible opportunity set** (I only graded venues already held + the 5%+ synthetics I rejected).
- ❌ The **investor inputs** above (risk tolerance, liquidity, sleeve split) — so the strategic layer is unsolved.
- ❌ The **constrained optimization** producing target weights, and the **crash validation**.

**This interim model is a lower bound, not the optimum.** It only says "stop earning 0% on cash"; it does not
prove the *best* mix across the full menu under your risk policy.

### Audited state (2026-05-30)

| Metric | Value |
|---|---|
| Total | ~$177,145 |
| Stablecoins | $122k (69%) |
| **Blended yield (live)** | **~1.7% (~$2,989/yr)** |
| Stables earning <3% | **~$104k** |
| Biggest position | Seamless USDC @ Morpho — **$37,770 (21%)**, **0.00% live** |

Key findings: ~$62k of "0%" Morpho USDC is **genuinely idle** (deposits no one borrows; some in **deprecated
vault versions — verify addresses**); ~$17k in Storm perp-LP makes you counterparty to leveraged traders; TON
ecosystem is 14% (bridge closing 2026); two tracking errors hid real ~5% yields (jup.ag, fragSOL).

### Interim model (the floor, not the goal)

Reallocate ~$113k of idle/sub-frontier/exit-able stables → ~4.5% clean frontier (Maple Syrup USDC, Morpho
steakUSDC/gtUSDCp). No new risk — *less* risk (exits the perp-LP).

| | Income/yr | Yield |
|---|---|---|
| Now | $2,989 | 1.69% |
| Interim target | **$7,058** | **3.98%** |
| Uplift | **+$4,069** | +2.3 pts |

## Roadmap to the optimum

1. **Capture investor inputs** — the policy checklist above (one short session).
2. **Enumerate the opportunity set** — research agents sweep every chain for C1-passing venues; build a graded, live menu with capacity + liquidity terms.
3. **Solve** — run the two-layer optimization (strategic sleeves from policy, stable sleeve as a constrained LP) → target weights.
4. **Validate** — crash-scenario test against C6/C-drawdown limits.
5. **Transition** — cost/tax-aware from→to tickets; execute (investor signs).
6. **Maintain** — monthly drift check via `portfolio.py`; re-screen; rebalance to bands.

## References

- Tooling: [`portfolio.py`](portfolio.py) · report in [`report/`](report/) · run guide in [`README.md`](README.md)
- Screening & yield landscape: [`../research/10-crypto-lp-yield-state.md`](../research/10-crypto-lp-yield-state.md)
- Conservative-deposit thesis: [`../blog/2026-05-where-to-park-usdt-usdc.md`](../blog/2026-05-where-to-park-usdt-usdc.md)
- Parent (equity) mandate: [`../GOAL.md`](../GOAL.md)
