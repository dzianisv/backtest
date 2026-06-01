# Real-book rebalance — 2026-06-01 (MODERATE)

Produced by the `defi-portfolio-manager` hedge-fund team on the investor's actual ~$177,145 book.
**Read-only: the investor executes every transaction.** Balances are from the session snapshot —
**confirm current balances and re-pull every APY + verify every on-chain address before signing.**

## Verdict
A 1.68%-yield book where **$103.9k (59%) sits idle <3%**, the largest position ($37.8k Seamless USDC)
earns **0.00% live on a likely-deprecated clone** (and breaches the 20% position cap at 21.3%), and
~$48k is in synthetics + perp-LP "you're-the-house" junk. The fix is mostly **free idle-reactivation**
(+~$4.5–5k/yr carry, zero new risk), then **exit the synthetic/perp-LP positions**, then **build the
directional sleeve to the moderate band** with staked BTC/ETH/SOL. Target blended yield → ~5.5%.

## Moderate target (compliant by construction)
- **Stable core 54%** (~$96k): Morpho gtUSDCp/steakUSDC (Base, ~4.61%), Maple syrupUSDC (~4.62%),
  Fluid USDC (~5% base), Sky sUSDS (3.60%), Ondo USDY (3.55% T-bill), save.finance (Solana), reserve.
- **Directional 29%** (~$51k): jitoSOL (5.60%), wstETH/stETH, cbBTC (new), HYPE, SOL.
- **Satellite ≤9%**, **Gold (PAXG) 2.5%**. Synthetic/perp-LP = **0**.
- Caps: ≤20% position, ≤30% protocol (Morpho 19%), off-main ≤13% (trim save.finance to ~$6k), reserve held.

## Crash test
−60% crypto ≈ **−22.6%** book — inside the moderate −30% budget. Residual tails named: Morpho curator
risk (risk-off regime post Resolv/USR 2026-03-22), Solana smart-contract (Drift precedent), Maple credit.

## Tickets (sequence A→B→C; verify address + re-pull APY before signing)

**A — Free idle-reactivation (do first, zero new risk):**
1. $19,000 Seamless USDC (Base, verify `0x616a4E1db48e22028f6bbf20444Cd3b8e3273738`) → Morpho gtUSDCp (Base)
2. $15,000 Seamless USDC → Morpho steakUSDC (Base)
3. $3,770 Seamless USDC → instant reserve (clears the 21.3% cap breach)
4. $10,000 Extrafi XLend (Base, 0%) → Fluid USDC (Eth, ~5% base)
5. $10,000 Universal USDC L3 (Base, 0%) → Sky sUSDS (Eth)
6. $10,000 Universal $4,094 + Hyperliquid idle $5,676 → Ondo USDY (Eth)
7. $4,000 + $1,000 + $964 idle (Solana/DeFi.app/Asterdex) → save.finance (top to ~$6k) / gtUSDCp
8. $2,054 Woo.Fi vault (Avax) → Morpho gtUSDCp (Base)

**B — De-risk / exit (reject-list):**
9. EXIT $6,149 R7 USDe @ Morpho → steakUSDC (synthetic veto)
10. EXIT $2,887 sUSDe @ Ethena → Maple syrupUSDC (synthetic veto)
11. EXIT $2,806 Re7 eUSD @ Morpho → Fluid USDC (USR-exposed curator + synthetic)
12. EXIT $5,000 HLP @ Hyperliquid → gtUSDCp (perp-LP, repeated drains)
13. EXIT $1,000 Avantis LP → reserve (perp-LP)
14. EXIT $8,877 + $8,520 Storm USDT-SLPT + TON-SLP → bridge → sUSDS/USDY (perp-LP + TON exit)
15. EXIT $6,383 DeDust TON-USDT LP → bridge → stable core (AMM-LP/IL + off-main)
16. EXIT $609 lighter.xyz SOL farm → jitoSOL (emissions)

**C — Directional build (to band, last):**
17. CONVERT $3,935 fragSOL + ~$1,490 SOL → jitoSOL (~$16k staked, 5.60%)
18. CONSOLIDATE $233 cbETH + $3,141 stETH → wstETH (kill 0% cbETH)
19. BUY ~$11,000 → cbBTC (Base) — add the missing true major
20. TRIM ASTER $3,547 → ~$2,000; let TRUMP/micro-dust bleed into stable core

## Caveats
- Balances are the session snapshot; **confirm live balances first** (some may have moved).
- Stable-core APYs/addresses are live-pulled but **re-pull + verify on-chain** before each deposit
  (deprecated Morpho clones earn ~0%); use Circle CCTP (not third-party bridges) for USDC bridging.
- This is MODERATE (29% directional = crypto-direction bet). The repo backtest (`crypto/backtest/RESULTS.md`)
  shows directional beta *lost* to all-stable in the 2024–26 bear window — if you'd rather not bet on
  crypto direction, say so and I'll re-cut at a conservative (all-stable ~5%, near-zero-drawdown) target.
