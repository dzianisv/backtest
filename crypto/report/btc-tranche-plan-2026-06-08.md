# BTC Tranche Plan — 2026-06-08 · NOTIFICATION-FIRST order ticket

> **Educational analysis, not financial advice. The agent does NOT execute.** This is an order
> ticket the investor reviews and signs/executes from their own wallet. **Self-custody.**
> Numbers are from the 2026-06-01 book snapshot (`report/portfolio.md`, total **$177,145**) and the
> MODERATE / CONSERVATIVE rebalance docs. **Re-pull every live reading (BTC price, 200-day MA, global
> liquidity trend, Chainflip slip quote, idle balances) before signing each tranche.**

This applies a **5-lens quorum-consensus** decision (Howell/liquidity · Carver/systematic ·
Bernstein/TA · Graham/value · Alden/debasement) to the question *"buy BTC now for the ~$177k
conservative book?"* The quorum was **unanimous AGAINST a lump-sum** ~$21k buy and converged on
**start small, then gate further buys on confirmation.** This doc turns that into a signable ladder.

---

## 1. TL;DR — first order ticket (sign this one only)

| Field | Value |
|---|---|
| **Action** | **BUY ~$6,000 of spot BTC** (first tranche) |
| **Instrument** | Native Bitcoin to **self-custody** (your own BTC address / hardware wallet) |
| **Rail / venue** | **Chainflip** — USDT(Arbitrum)→native BTC, no wrapper, no bridge IOU (per `btc-dex.md`: cleanest native self-custody path at this size; **quote the exact slip in the UI first**). Acceptable transition alternative: **cbBTC spot held self-custody** (NOT lent on Morpho) as a rail, then migrate the structural position to investor-held BTC keys. CEX (Kraken/MEXC) → withdraw native BTC is the cheapest fallback if you tolerate a brief custodial touch. |
| **Funding source** | Draw from **Seamless USDC @ Morpho — $37,770, 0.00% live** (the largest idle, sub-frontier position; the single best dollar to redeploy). Pulling $6k leaves ~$31.8k there for the stable-reactivation legs. |
| **Size rationale** | $6,000 = **3.4% of the $177,145 book.** Inside Graham's "losable" ≤3% cap (rounded, see dissent), inside Carver's starter tranche, inside Alden's first-tranche. Funded from genuinely idle 0% cash, so it costs **zero** current yield. Far below the ≤15% position cap (C2) and the BTC sleeve ceiling. |
| **Pre-trade checks** | (a) confirm Seamless $37,770 balance is live and withdrawable; (b) re-pull BTC spot price; (c) get the Chainflip all-in quote (0.1% + JIT spread + gas + BTC miner fee) and compare vs a CEX before sending; (d) confirm receiving address is **your** BTC key. |

**One sentence:** *Buy ~$6k spot BTC via Chainflip to self-custody, funded by the idle 0% Seamless
USDC; do nothing else until a trigger below fires.*

---

## 2. Staged ladder (dollar math vs the actual $177,145 book)

Two named ceilings from the quorum:
- **MODERATE ceiling: ~$21,000 ≈ 11.9% of book** (the cbBTC target in `rebalance-2026-06-01.md`).
- **Carver vol-target cap: ~$15,000 ≈ 8.5% of book** — the *more conservative* stop. Treat $15k as
  the default ceiling; only extend toward $21k if BOTH structural triggers are firmly positive.

| Tranche | Size | Cumulative | % of $177,145 | Release trigger (checkable, NOT fear-driven) | Funding source |
|---|---|---|---|---|---|
| **T1 — now** | ~$6,000 | $6,000 | **3.4%** | None — this is the starter. Sign today. | Seamless USDC $37,770 (0%) |
| **T2** | ~$5,000 | $11,000 | **6.2%** | **BTC reclaims its 200-day MA** (daily close above) **OR** global liquidity re-crosses its trend (Howell tide turning back in). One of the two. | Seamless remainder / idle 0% USDC |
| **T3** | ~$5,000 | $16,000 | **9.0%** | The **other** of the two T2 triggers also confirms (so both 200d reclaim **AND** liquidity-trend turn are in) — crosses past the $15k Carver cap deliberately, only on dual confirmation. | idle 0% USDC (Extrafi/Universal legs) |
| **T4** | ~$5,000 | **$21,000** | **11.9%** | Both triggers still positive **and** holding (no fresh trend break); tops up to the MODERATE ceiling. Skip if either trigger has reverted. | idle 0% USDC |

**Math check:** $6k + $5k + $5k + $5k = **$21,000** = MODERATE ceiling, **11.9%** of the current book —
under the ≤15% position cap (C2) and consistent with Alden's ~12% debasement allocation. If you stop
at the **Carver $15k** cap (T1+T2+T3 ≈ $16k, trim T3 to $4k for exactly $15k), that is **8.5%** — the
default stop unless dual confirmation is firm.

**Do NOT accelerate on extreme Fear & Greed alone.** Fear is not a release trigger; the gates are the
200-day MA reclaim and/or the liquidity-trend turn. (Howell is near-term cautious — tide going out,
BTC could see ~$30k — but structurally constructive into the ~2027 liquidity trough; the ladder buys
*confirmation*, and a falling price simply means later tranches buy cheaper, not faster.)

---

## 3. Why staged, not lump (the quorum)

All five lenses rejected a lump-sum ~$21k buy. The **overlap** of their individual sizing —
Carver's systematic starter tranche, Graham's "only what you can lose" cap, and Alden's first
debasement tranche — lands at **~$5–7k**, which is why T1 is $6k. Carver and Bernstein both want
*confirmation of trend* before committing more, so tranches 2–4 are gated on the **200-day MA reclaim**
(Bernstein/TA) **and/or the global-liquidity trend turn** (Howell). Graham caps the whole speculative
line low and insists it be losable; Alden argues that *zero* BTC under fiscal dominance is itself a
risk and supports building toward ~12%. The ladder honors both: it starts inside Graham's losable cap
and only reaches Alden's ~12% if the market confirms — buying on **evidence, not fear**.

---

## 4. Drawdown / constraint check

- **First tranche ($6k, 3.4%).** A −60% BTC move on $6k = **−$3,600 ≈ −2.0% of book.** Funded from
  0%-yield idle cash, so no yield given up. Trivially inside both the **−30% MODERATE budget** and the
  stricter **−20% STRATEGY policy** drawdown.
- **Full ladder ($21k, 11.9%).** A −60% BTC move on $21k = **−$12,600 ≈ −7.1% of book** *from the BTC
  line alone.* The MODERATE plan already crash-tests the whole directional book at **≈ −21%** in a
  −60% crypto move — inside the −30% moderate budget. This BTC ladder is the cbBTC slice of that same
  plan, so the full ladder stays within the already-validated envelope.
- **Position cap C2 (≤15%):** 11.9% at the ceiling ✓. Carver-cap stop = 8.5% ✓.
- **Protocol cap C3 (≤25%):** BTC is held **SPOT / self-custody, NOT lent on Morpho**, so it adds
  **nothing** to Morpho's protocol concentration (this was red-team fix M4 in the MODERATE plan). ✓
- **Chain cap C4 / off-main:** native BTC on its own chain; does not touch the Solana ≤13% budget. ✓
- **Instant-liquidity reserve (≥$25k):** untouched — funding comes from idle 0% USDC, not the reserve. ✓
- **No idle cash (C9):** the ladder *reduces* idle cash (it spends the 0% Seamless position), which
  the strategy wants deployed within 3 days anyway. ✓

Conclusion: **first tranche and the full ladder both stay inside every position/protocol cap and
inside the drawdown budget.**

---

## 5. Preserved dissents + the conservative alternative

This is a genuine disagreement; it is recorded, not averaged away.

- **Graham (value) — dissent AGAINST.** BTC is speculation, not investment; it has no cash flow to
  value. If bought at all, the line must be **losable and capped ≤3%** of the book. Under Graham, T1
  is the *whole* position and tranches 2–4 are optional at best.
- **Alden (debasement) — dissent FOR more.** Under fiscal dominance and structural fiat debasement,
  holding **zero** BTC is itself a risk; **~12%** (the full $21k ceiling) is an appropriate strategic
  weight. Under Alden, the ladder should complete on confirmation rather than stall at the starter.
- **Howell (liquidity) — near-term cautious, structurally constructive.** The liquidity tide is going
  out now (BTC could revisit ~$30k), so *don't rush*; but into the ~2027 liquidity trough/turn the
  setup is constructive — which is exactly why later tranches gate on the liquidity-trend re-cross.

- **The conservative zero-BTC alternative remains fully legitimate.** Per
  `rebalance-2026-06-01-conservative.md` and the repo backtest: an **all-clean-stable book returned
  ~5.0% with ~0 drawdown** over 2024–26, while the moderate directional sleeve returned 2.44% with
  −18.5% drawdown. If you do **not** hold a bullish crypto view, **buying no BTC at all** and routing
  this $21k into the stable menu (Aave/sUSDS/Ondo/Morpho) is the better-evidenced risk-adjusted
  choice in the current risk-off regime. The ladder above is the *moderate* path; this is the
  standing alternative.

---

## 6. Disclaimer

- **Educational analysis only — not financial advice.**
- **The agent does not execute any transaction.** It produces this ticket; **the investor signs and
  executes every transaction** from their own wallet.
- **Self-custody:** the structural BTC position must end up on **investor-held keys**. cbBTC is
  acceptable only as a transition rail, not the final home.
- **Re-check live readings before each tranche:** BTC spot price, the 200-day MA, the global-liquidity
  trend, the Chainflip all-in slip quote (vs a CEX), and your actual idle balances. Quote the exact
  amount in the venue UI before sending. Verify the receiving address is your own BTC key.
- Balances cited are the 2026-06-01 snapshot; confirm live balances first.
