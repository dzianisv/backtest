# Portfolio Synthesis — Fidelity Multi-Account Review

**Date:** 2026-07-01 · **Seat:** Portfolio-synthesis (cross-position) · **Book:** $444,748 across 5 accounts
**Scope:** Reason across positions/accounts. Per-stock verdicts are inputs, not re-litigated here.

---

## 1. FACTOR CORRELATION MAP

Every holding — invested sleeve *and* cash-like — grouped by primary risk factor, weighted to the $444,748 book.

| Factor | Holdings | $ | % of book | Tail scenario |
|---|---|---:|---:|---|
| **Rates / Fed (short duration)** | T-bill ladder $314,620 + SGOV $13,764 | **$328,384** | **73.8%** 🚩 | Fed cuts / curve rallies → rollover yield collapses (reinvestment risk); the "safe" 4% evaporates and the book is left underexposed to whatever rallied. In a hawkish hold it "works," but only by standing still. |
| **Cash (zero duration)** | Brokerage $30,880 + Cash-Mgmt $11,513 + IRA cash $3,017 | **$45,410** | **10.2%** | Pure opportunity cost + inflation erosion; earns near-nothing vs bills. This is deployable dry powder, not a position. |
| **US equity — dividend / value / income** | SCHD $27,475 (×3 accts) + JEPI $16,749 + SPYI $10,058 | **$54,282** | **12.2%** (🚩 **64% of invested sleeve**) | Single-factor cluster: rate-sensitive high-dividend + two covered-call overlays. In a growth/AI melt-up the overlays cap upside and the value tilt lags; all three draw down together in a value/rate shock. Not 3 bets — 1 bet, 3 wrappers. |
| **International equity** | VXUS $10,442 | **$10,442** | **2.3%** | USD strength / EM-DM underperformance. Genuine diversifier but sub-scale. |
| **Special-situation (event-driven)** | UNH $4,354 + SITC $1,876 | **$6,230** | **1.4%** | Idiosyncratic/binary: UNH (DOJ + MCR + smart-money distributing) and SITC (delisting/special-div stub). Uncorrelated to each other, but both headline-driven and both flagged for exit-review. |
| **AI / growth** | *(none held — GOOG is a recurring buy, not a holding)* | **$0** | **0%** | The entire AI-bubble exposure lives in the IBKR book, not here. Fidelity carries zero bubble beta — coherent with its "reserve/DCA half" role. |

**Concentration flags (>25%):**
- **Rates/Fed 73.8% — the dominant risk of the entire book.** Aggregated with pure cash, **84.0% ($373,794) sits in cash-equivalents.** As the brief notes, cash *is* a factor here, not the absence of one: the active bet is *reinvestment / opportunity risk* under a hawkish-opaque Warsh Fed. This position wins only in a near-term drawdown; it loses slowly in a melt-up and loses in real terms in a sticky-inflation sideways tape.
- **Income cluster is a hidden sub-concentration:** 12.2% of the book but **64% of everything actually invested**, and internally correlated. Flagged in §2.

No equity factor exceeds 25% of the book — because the book is barely invested. The concentration risk is *cash*, not any stock.

---

## 2. OVER-DIVERSIFICATION CRITIQUE

**Position count:** 8 distinct securities (T-bill ladder, SGOV, SCHD, JEPI, SPYI, VXUS, SITC, UNH) held across 10 account-line-items + 5 cash balances. For a $445k book that's *thin*, not over-diversified in count — the problem is **redundancy inside the tiny invested sleeve**, not sprawl.

**The income overlap — accidental, not intentional tilt.** SCHD (×3 accounts) + JEPI + SPYI = **$54,282 = 64% of the invested sleeve**, all three chasing the same US-large-cap income factor:
- **SCHD** — dividend-growth quality-value index, 0.06% ER. The clean, cheap core. Keep.
- **JEPI** — active covered-call on low-vol equities, ~0.35% ER. Caps upside, income via ELN premium.
- **SPYI** — S&P covered-call ELN income, ~0.68% ER. Near-duplicate of JEPI's payoff, **10× SCHD's fee**.

Verdict: this reads as **accidental overlap dressed as diversification**. Three vehicles, one factor, high mutual correlation, and two of them (JEPI/SPYI) impose the *same* structural drag — capped upside in exactly the melt-up scenario the 84% cash pile is already exposed to. Holding **both** JEPI and SPYI is the redundancy. Rationalize to SCHD (core) + **one** overlay if income is genuinely wanted; drop SPYI first (highest fee, most redundant). The income-in-tax-shelter logic is sound; running two option-overlay funds side by side is not.

**ROBO (recurring buy, $250/wk, not yet held).** 0.95% ER thematic robotics/automation — **~16× SCHD's fee** and maps to **no v3 sleeve**. v3's "extra" equity factors are AVUV (small-cap value, 0.25%) and USMV (min-vol, 0.15%), both cheap and diversifying; ROBO is an expensive single-theme concentration bet inside a mandate that is explicitly *all-weather*. Unless there's standing robotics conviction, **fold it** (see §5) — it's factor-incoherent and fee-heavy.

**Index-like names replaceable by core ETFs.** JEPI and SPYI are both S&P-proxies with an option collar bolted on; if the goal is US-equity exposure rather than a specific income stream, both are replaceable by **RSP** (equal-weight, dilutes Mag-7 concentration) or the SCHD core. In the Trad IRA the covered-call tax-inefficiency is moot, but the *upside-cap* cost is not.

---

## 3. CROSS-POSITION CONFLICTS

**a) GOOG weekly drip vs IBKR desk staging a GOOG trim — RESOLVED, and coherent.** Buying GOOG $500/wk in Fidelity while the IBKR desk plans to *trim* GOOG at 380–400 is two accounts trading the same name in opposite directions: net exposure churns, spread is paid both ways, and any loss-leg trim within 30 days of a drip buy creates **wash-sale** entanglement across accounts. The `REDIRECT_DRIP` verdict (GOOG→RSP before the Jul 7 first run) is the coherent fix: it stops accumulating the exact single-name AI/growth concentration the desk is reducing, routes the dollars into equal-weight RSP (which *dilutes* Mag-7), and removes the cross-account wash-sale surface entirely. **Confirmed coherent** — execute the redirect before Jul 7.

**b) SGOV in the Trad IRA while GLD is absent — tax-location is backwards.** SGOV (T-bill yield, taxed as ordinary income) currently occupies **$13,764 of prime tax-advantaged space** in the Trad IRA — but bill interest is also **state-tax-exempt in a taxable account**, so sheltering it buys relatively little. Meanwhile **GLD is entirely missing** despite a $22.1k v3 target, and gold in a *taxable* account is taxed as a **collectible at 28%** (vs 20% LTCG for equities). The asset that most *needs* the shelter is the one that isn't there. **Swap: sell SGOV in the Trad IRA → buy GLD in the Trad IRA.** The bill reserve stays where it belongs — the brokerage ladder. This shields the 8-point collectibles premium, adds the missing all-weather diversifier, and trims the rates/cash over-concentration. Clean, high-value, executable now with no new capital. (DBMF, which also throws ordinary income, is a secondary IRA candidate.)

**c) UNH single-name in the small Roth vs Roth-as-max-growth-space.** The Roth is the most valuable tax real estate on the board (tax-free growth forever, no RMD) — it should hold the **highest-expected-return** assets. It currently holds **UNH (HOLD 1/5, distributing-high, a legal/turnaround name) + SITC (a stub being liquidated within weeks) + $947 SCHD.** That is close to the *inverse* of the principle: premium tax-free space rented to a 1/5-conviction single name and a soon-to-be-sold spinoff. One nuance is correct — harvesting SITC's ~$421 special dividend **tax-free in the Roth** is the right venue, so keep SITC through the Jul 17 record date, then exit per verdict. But **do not add to UNH**; on the Jul 16 re-eval EXIT trigger (MCR ≥85.5% / DOJ escalation / 3 closes <395), redeploy the freed Roth space into the highest-growth v3 sleeve (AVUV or a quality-growth tilt), not back into another defensive name.

---

## 4. PORTFOLIO STRUCTURE VERDICT

The single biggest structural risk *right now* is not any holding — it is that **84% of the book ($373,794) sits in cash and short bills earning ~4% while an approved v3 all-weather structure sits undeployed.** This is a large, unhedged *bet on cash*: it pays off only in a near-term drawdown that lets the dip-tiers fire, and it quietly loses in a continued melt-up and loses in real terms in a sticky-inflation sideways tape — the two outcomes a hawkish-opaque Fed and record late-cycle risk appetite make entirely plausible. **But** the highest-leverage action is *not* a trade — it is resolving the open gate: **confirm whether the $314.6k T-bill ladder is risk capital or the $1.5M untouchable house reserve.** That one answer swings everything downstream: if it's risk capital, the book is ~71% under-deployed vs mandate and staged Foundation deployment should begin on the Jul 7/14 maturities; if it's house reserve, the book is roughly *correctly* positioned (reserve in bills, small risk sleeve invested) and the plan must shrink to deploy only the ~$45k free cash and re-scale every v3 ticket to the true risk-capital base. Deploying before that answer risks putting the house down-payment into equities at a late-cycle top; sitting idle if it *is* risk capital burns the mandate. **Resolve the classification first — it is the single action that most reduces structural risk, because it converts an ambiguous 71%-of-book from "unknown" to "sized."**

---

## 5. CASH DEPLOYMENT PRIORITY

Ranked actions for the **$360,030 cash-like** (brokerage $345.5k = cash $30.9k + bills $314.6k · cash-mgmt $11.5k · IRA cash $3.0k). Staged, not lump (late-cycle). Weekly recurring total held at **$1,750/wk**.

### Priority 1 — Reconfigure the recurring buys BEFORE the Jul 7 first run *(zero-cost, no capital-gate needed, funded from brokerage cash)*
Rewire the $1,750/wk to be 100% v3-aligned, same total:
- **GOOG $500 → RSP** (RSP now **$1,000/wk**) — kills the cross-account GOOG conflict (§3a), buys equal-weight instead of feeding Mag-7.
- **ROBO $250 → AVUV** *(my keep-or-fold call: **FOLD**)* — drops the 0.95%-ER factor-orphan (§2), buys the small-cap-value v3 sleeve at 0.25%.
- **VXUS $500 → keep.**
- **New weekly = RSP $1,000 + VXUS $500 + AVUV $250 = $1,750/wk** (~$7.6k/mo, aligned with the v3 ~$6.4k/mo DCA cadence).
- **Fixes:** single-name accumulation conflict, thematic fee drag, and starts factor-correct DCA on day one. **Do by Jul 6 (before Jul 7 first run).**

### Priority 2 — Trad IRA tax-location swap: SGOV $13,764 → GLD *(executable now, no new capital, no gate)*
- Sell SGOV in the Trad IRA, buy **GLD (~$13.8k of the $22.1k v3 target)**; hold the remaining ~$8.3k of GLD for the next tranche.
- **Fixes:** the 28%-collectibles tax-location error (§3b), adds the missing all-weather gold sleeve, and shaves the rates/cash over-concentration. Bill reserve stays in the brokerage ladder where its state-tax exemption is used.
- **Companion (flag, not a "now" trade):** on the SITC August exit and any UNH Jul-16 EXIT, redeploy the freed Roth space into a growth sleeve (§3c).

### Priority 3 — Staged Foundation deployment — **GATED on house-reserve confirmation**, tied to bill maturities
**Do nothing here until the ladder is confirmed risk capital (§4).**
- **If CONFIRMED risk capital** — deploy the *diversifiers first* (equities are already DCA'ing via P1; late-cycle, put the hedges on before adding beta):
  - **Jul 7 maturity ($25k):** seed **GLD + DBMF** (~$12.5k each) — the two all-weather legs currently at $0.
  - **Jul 14 maturity ($88k):** **stage, do not lump** — ~$30k into remaining diversifiers (**TLT, SCHP, BTAL**, finish GLD/DBMF); **roll ~$58k back into SGOV** as the DCA-in-waiting + dip reserve.
  - **Aug maturities ($25k Aug4 / $25k Aug11 / $20k Aug13 / $50k Aug27):** feed equity Foundation sleeves (RSP/AVUV/USMV top-ups) on the ~$6,449/mo cadence.
  - **Keep $76k permanent in SGOV/bills as the armed dip reserve** for the **-7% / -12% / -20% S&P tiers** — do not pre-spend it.
  - **Fixes:** the 84%-cash mandate gap, while respecting late-cycle staging and preserving dip-buy discipline.
- **If NOT confirmed (house reserve):** deploy **only free cash** — brokerage $30,880 + cash-mgmt $11,513 + IRA cash $3,017 ≈ **$45.4k** into a re-scaled v3 sleeve; leave the ladder rolling untouched and re-size every v3 ticket to that $45k base.

**Net:** P1 + P2 are zero-gate and should execute this week (~$28k repositioned/redirected + the recurring rewire). P3 — the other ~$332k — waits on the one confirmation that defines whether this is a $445k risk book or a $130k risk book with a $315k house reserve attached.
