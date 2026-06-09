# 10 — State of Crypto LP / Stablecoin Yield (live snapshot)

*Where to earn yield on stablecoins right now **without shady collateral**. Educational
analysis, not advice. All numbers pulled live from the DefiLlama free yields API
(`https://yields.llama.fi/pools`) and the Morpho GraphQL API (`https://api.morpho.org/graphql`)
on **2026-05-30**. Re-run the queries at the bottom to refresh — DeFi rates move hourly.*

## TL;DR

- **The honest base rate for stablecoins is ~3–5%.** It tracks US T-bills (the risk-free rate),
  because the safest large pools are now backed by tokenized treasuries or overcollateralized
  blue-chip lending. Anything materially above ~6% sustained is paying you for *extra risk*
  (curator risk, exotic collateral, depeg risk) or is a temporary spike / token emission.
- **"No shady collateral" has a precise meaning here:** the pool lends only against
  cash-equivalents (T-bills), BTC, or ETH — not long-tail tokens, leveraged PT positions, or
  reflexive synthetic dollars.
- **Best risk-adjusted picks right now:** Maple `Syrup USDT/USDC` (~4.1–4.7%, overcollateralized
  institutional lending) and Morpho `steakUSDC` (~3.8%, lends only vs WBTC/cbBTC/ETH).

## The landscape — largest stablecoin pools, all chains (TVL > $200M)

| Protocol | Chain | TVL | APY | What backs it | Collateral grade |
|----------|-------|-----|-----|---------------|------------------|
| Sky `sUSDS` | Ethereum | $6.2B | 3.6% | Maker/Sky reserves | Cash-equiv ✅ |
| Maple `Syrup USDC` | Ethereum | $3.3B | 4.67% | Overcollateralized institutional loans | Blue-chip ✅ |
| Circle `USYC` | BSC | $2.8B | 3.0% | Tokenized T-bills (Hashnote) | Cash-equiv ✅ |
| Ethena `sUSDe` | Ethereum | $1.8B | 3.8% | Delta-neutral perp basis | ⚠️ Synthetic |
| Spark Savings `USDT` | Ethereum | $1.3B | 2.5% | Sky reserves | Cash-equiv ✅ |
| Ondo `USDY` | Ethereum | $1.1B | 3.55% | Tokenized T-bills + bank deposits | Cash-equiv ✅ |
| Maple `Syrup USDT` | Ethereum | $986M | 4.13% | Overcollateralized institutional loans | Blue-chip ✅ |
| BlackRock `BUIDL` | Ethereum | $838M | 3.55% | Tokenized T-bills (BlackRock/Securitize) | Cash-equiv ✅ |
| Superstate `USTB` | Ethereum | $759M | 3.3% | Tokenized T-bills | Cash-equiv ✅ |
| Aave v3 `USDT` | Ethereum | $555M | 2.37% | Overcollateralized crypto lending | Blue-chip ✅ |

**Read:** the entire top of the market has converged on **T-bill yield (~3.5%)** plus a small
spread for overcollateralized lending (Maple/Aave at 4–4.7%). That *is* the no-shady-collateral
yield right now. There is no safe 10%.

## Protocol-by-protocol

### Morpho — the one to understand
Morpho is **not one pool**. It's a permissionless vault layer: independent *curators*
(Steakhouse, Gauntlet, MEV Capital…) each run a vault, pick the collateral, the loan-to-value
(LLTV), and the oracle. So a "Morpho APY" is meaningless without naming the **vault and its
collateral**. The headline 8–13%+ numbers you see are almost always: (a) token emissions, (b) a
transient utilization spike, (c) exotic collateral risk premium, or (d) a near-zero-TVL vault
where one borrow distorts the instantaneous rate.

Verified collateral books (Morpho API, 2026-05-30):

| Vault | TVL | APY | Collateral (actual) | Verdict |
|-------|-----|-----|---------------------|---------|
| **`steakUSDC`** | $109M | **3.73%** | 65% WBTC, 20% cbBTC, 10% ETH/stETH | ✅ **Blue-chip only** |
| `steakUSDT` | $92M | 13.71%* | 73% wstETH, 23% BTC, 3% gold | ✅ collateral, ⚠️ *yield is a utilization spike, 30d mean ~3%* |
| `steakUSDTBethena` | $120M | 1.5% | 100% sUSDe (Ethena) | ⚠️ Synthetic-dollar collateral — avoid for low-risk |

→ **`steakUSDC` pool:** https://defillama.com/yields/pool/b55f43a8-f444-4cd8-a3a4-0a4e786ba566
→ **`steakUSDC` vault (deposit here):** https://app.morpho.org/ethereum/vault/0xBEEF01735c132Ada46AA9aA4c54623cAA92A64CB
*(\* `steakUSDT` netAPY swings — it showed 6.2% base on DefiLlama, 13.7% live on Morpho, 30-day
mean ~3%, trend "Down". Same good collateral as steakUSDC but a rate you can't count on.)*

### Maple Finance — best blue-chip lending spread
`Syrup USDT/USDC`. Overcollateralized lending to vetted institutional borrowers. Single-asset
(no IL), `apyReward: 0` (real yield, not emissions), ~$1B (USDT) / $3.3B (USDC) TVL. **~4.1–4.7%.**
The protocol you already trust; it earns its spread above T-bills by taking *overcollateralized*
counterparty risk, not by holding junk. Withdrawals route through a cycle/notice window (not
always instant) — check the current cooldown before depositing.

### Beefy — autocompounder, *inherits* its collateral risk
Beefy doesn't originate yield; it auto-compounds someone else's LP. Its risk = the underlying
pool's risk plus a smart-contract layer. Current Ethereum stablecoin Beefy vaults are small
($3–9M) and mostly Curve stable-LP wrappers (e.g. `RLUSD-USDC` ~7%, `USDS-stUSDS` ~4.5%). Fine as
an autocompounding convenience on an L2 with cheap gas, **not** where you want size on mainnet.

### Aave v3 — the liquidity benchmark
`USDT` 2.37% base (6.5% on the incentivized market with rewards). The most battle-tested,
most liquid, instant-withdraw option. Lowest yield, lowest risk. The thing everything else is
measured against.

### Curve / Convex — yield is mostly emissions now
Large stable LPs (`USDC-RLUSD` 7.6%, `PYUSD-USDC` 5.3%) but the APY is **mostly `apyReward`**
(CRV/CVX token emissions), not trading fees. When emissions taper the rate collapses, and you
take pair/depeg exposure (RLUSD, PYUSD are newer than USDC). Not "no-shady" for size.

### RWA / tokenized T-bills — the genuinely safest tier
BlackRock `BUIDL`, Superstate `USTB`, Ondo `USDY/OUSG`, Circle `USYC`. These hold **actual US
Treasuries**. ~3.3–3.6%. The collateral literally cannot be shady — it's T-bills. Catch: most
require KYC / accredited-investor onboarding and have minimums, so they're not click-to-deposit
for a retail wallet.

## The shady-collateral checklist (how to screen any pool)

Reject a pool if any are true:
1. **APY is mostly `apyReward`** → token emissions, not real yield; collapses when they end.
2. **TVL < ~$20M** → instantaneous APY is noise; one borrow distorts it.
3. **Collateral is long-tail / PT / looped / a reflexive synthetic** → you eat the bad debt.
4. **Sustained APY >> ~6% on a "stablecoin"** → you're being paid for risk you haven't priced.
5. **`outlook: Down` + APY far above 30-day mean** → you're buying a transient spike.

Keep it if: single-asset (`ilRisk: no`), `apyReward ≈ 0`, TVL > $100M, collateral ∈
{T-bills, BTC, ETH}, reputable curator/protocol.

## How to refresh this (free, no API key, no wallet)

```bash
# Top no-shady stablecoin pools on Ethereum, real yield only:
curl -s https://yields.llama.fi/pools | jq -r '
  [.data[] | select(.chain=="Ethereum" and .stablecoin==true)
   | select(.tvlUsd>100e6) | select((.apyReward//0) < 0.5) | select(.apy<6)]
  | sort_by(-.apy) | .[]
  | "\(.project) [\(.symbol)] $\(.tvlUsd/1e6|floor)M  \(.apy)%"'

# Verify a Morpho vault's actual collateral before depositing:
curl -s https://api.morpho.org/graphql -X POST -H 'Content-Type: application/json' \
  -d '{"query":"{ vaults(first:300,where:{chainId_in:[1]}){items{symbol state{netApy allocation{supplyAssetsUsd market{collateralAsset{symbol} lltv}}}}}}"}'
```

Or just ask the installed **`risk-assessment`** skill ("is Maple safe?") — it walks hack history
→ oracle → treasury → yield sustainability before you commit.

## Sources
- DefiLlama Yields API — https://yields.llama.fi/pools (free, public)
- Morpho GraphQL API — https://api.morpho.org/graphql
- DefiLlama yields UI — https://defillama.com/yields
- Morpho app (collateral per vault) — https://app.morpho.org
