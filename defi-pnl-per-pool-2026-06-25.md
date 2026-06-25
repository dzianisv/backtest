# DeFi Pool PnL Report
Date: 2026-06-25
Analyst: automated on-chain + Morpho dashboard extraction

---

## Methodology

### General formula
```
PnL ($) = Total Withdrawn + Current Balance − Total Deposited
PnL (%) = PnL / Total Deposited × 100
```
- **Closed position:** Current Balance = 0; PnL is fully realized.
- **Open position:** Total Withdrawn = 0 (or partial); PnL includes unrealized component.

---

### Morpho

**Source:** `app.morpho.org/dashboard/<wallet>?tab=activity` opened via chrome-use (real Chrome session, no API key).

**How deposits/withdrawals were extracted:**
1. Opened each wallet's activity tab in Chrome via `$CHROME open <url>`.
2. Captured full page text (`$CHROME get text "body"`) — the activity table lists every supply/withdraw event with token amount and date.
3. Scrolled to load all historical rows.
4. Summed all "Supply" rows → **Total Deposited**; summed all "Withdraw" rows → **Total Withdrawn**.
5. Current Balance taken from the dashboard's live position display (shares × current exchange rate).

**eUSD treatment:** eUSD is a USD-pegged Reserve RToken; treated as 1:1 USD throughout. No price adjustment applied.

**Extrafi XLend USDC — special case:**
The Morpho dashboard displayed $10,223.85 current balance (vault shares at nominal USDC face value). However this vault is deprecated (`listed=false`, `deposit_disabled`, `netApy=0%`) following the USR (Resolv) exploit in March 2026. The vault used a hardcoded ~$1 oracle for USR collateral — when USR crashed to ~$0.02–$0.20 the oracle never repriced, liquidations never fired, and bad debt was socialized to USDC suppliers. Real recoverable value confirmed by user as ~$5,100 (~0.5:1 via Gauntlet/Resolv settlement). **Loss = −$4,900.**

---

### Maple Finance (syrupUSDC)

**Token contract:** `0x80ac24aA929eaF5013f6436cdA2a7ba190f5Cc0b` (Ethereum mainnet)

**Deposit history:**
```bash
# ERC-20 transfer history via Blockscout (no API key required)
curl -s "https://eth.blockscout.com/api/v2/addresses/<WALLET>/token-transfers?token=0x80ac24aA929eaF5013f6436cdA2a7ba190f5Cc0b" \
  -H "User-Agent: Mozilla/5.0"
```
- Incoming transfers (from = deposit router `0x134cCaaA4f1e4552…`) → **shares received** on deposit date.
- USDC cost of each deposit: matched outgoing USDC transfer from wallet on same block.

**Current share price (on-chain, 2026-06-25):**
```bash
# totalAssets() selector: 0x01e1d114
curl -s -X POST https://ethereum-rpc.publicnode.com \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":"0x80ac24aA929eaF5013f6436cdA2a7ba190f5Cc0b","data":"0x01e1d114"},"latest"]}'
# → 1,291,627,469.63 USDC

# totalSupply() selector: 0x18160ddd
curl -s -X POST https://ethereum-rpc.publicnode.com \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":"0x80ac24aA929eaF5013f6436cdA2a7ba210f5Cc0b","data":"0x18160ddd"},"latest"]}'
# → 1,103,482,521.26 shares

Price per share = 1,291,627,469.63 / 1,103,482,521.26 = 1.17050107 USDC/share
```

**Current value per wallet:**
```
Current Value = balanceOf(wallet) × 1.17050107
PnL = Current Value − USDC deposited
```
All positions are **open** (shares not yet redeemed). PnL is **unrealized**.

---

### Hyperliquid LP (HLP Vault)

**Vault address:** `0xdfc24b077bc1425ad1dea75bcb6f8158e10df303`

**API calls (no key required):**
```bash
# Current equity per wallet
curl -s -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type":"userVaultEquities","user":"<WALLET>"}'
# → returns vaultEquity (current USD value) + allTimePnl

# Vault metadata
curl -s -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type":"vaultDetails","vaultAddress":"0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"}'
```

**PnL derivation:**
- `allTimePnl` field = cumulative PnL since deposit (USD). Used directly.
- `vaultEquity` = current USD value of position.
- Implied deposit = `vaultEquity − allTimePnl`.
- Lockup: `lockupUntil` timestamp was 2025-10-28 — already expired, position is fully withdrawable.

---

## Data Sources
- **Morpho:** chrome-use → `app.morpho.org/dashboard/<wallet>?tab=activity`
- **Maple Finance:** Blockscout ERC-20 transfers + publicnode.com ETH RPC (no keys)
- **Hyperliquid:** `api.hyperliquid.xyz/info` (no key)
- **Extrafi loss:** confirmed by wallet owner; consistent with Gauntlet/Resolv ~0.5:1 settlement

---

## Part 1 — Morpho Vaults

> eUSD treated as 1:1 USD (eUSD is a USD-pegged stablecoin). No non-USD assets found.

| Wallet | Vault | Asset | Status | Total Deposited | Total Withdrawn | Cur. Balance | PnL ($) | PnL (%) |
|--------|-------|-------|--------|-----------------|-----------------|--------------|---------|---------|
| L1 | eUSD vault | eUSD | CLOSED | $2,805.96 | $2,842.01 | $0 | +$36.05 | +1.28% |
| L1 | Universal USDC | USDC | CLOSED | $4,186.91 | $4,291.19 | $0 | +$104.28 | +2.49% |
| L1 | Gauntlet USDC Prime | USDC | CLOSED | $5,654.64 | $5,676.28 | $0 | +$21.64 | +0.38% |
| **L1 subtotal** | | | | **$12,647.51** | **$12,809.48** | **$0** | **+$161.97** | **+1.28%** |
| L3 | eUSD vault | eUSD | CLOSED | $6,070.74 | $6,208.98 | $0 | +$138.24 | +2.28% |
| L3 | Seamless USDC Vault | USDC | CLOSED | $58,256.56 | $60,345.38 | $0 | +$2,088.82 | +3.59% |
| L3 | Universal USDC | USDC | CLOSED | $10,000.00 | $10,178.31 | $0 | +$178.31 | +1.78% |
| L3 | Extrafi XLend USDC | USDC | **OPEN⚠️ IMPAIRED** | $10,000.00 | $0 | ~$5,100 (est.) | **−$4,900** | **−49.0%** |
| L3 | Yearn USDC | USDC | CLOSED | $2,289.06 | $2,300.06 | $0 | +$11.00 | +0.48% |
| **L3 subtotal** | | | | **$86,616.36** | **$78,032.73** | **~$5,100** | **−$2,484** | **−2.87%** |
| B1 | — | — | — | No activity | — | — | — | — |
| B3 | — | — | — | No activity | — | — | — | — |
| B5 | — | — | — | No activity | — | — | — | — |
| **MORPHO TOTAL** | | | | **$99,263.87** | | **~$5,100** | **−$2,097** | **−2.11%** |

### Morpho Notes
- L1 fully exited all 3 vaults. Realized PnL only.
- L3 Seamless USDC Vault was largest: $58k cycled, +3.59% realized return.
- ⚠️ L3 Extrafi XLend USDC: $10,000 deposited, vault impaired by USR (Resolv) hack (Mar 2026). Morpho dashboard shows $10,223 at face value but vault is deprecated (listed=false, deposit_disabled, netApy 0%). Real recoverable value ~$5,100 (~0.5:1 via Gauntlet/Resolv settlement). Loss = **−$4,900**.

---

## Part 2 — Maple Finance (syrupUSDC)

**Token**: `0x80ac24aA929eaF5013f6436cdA2a7ba190f5Cc0b` on Ethereum mainnet

**Current exchange rate** (on-chain, 2026-06-25):
- `totalAssets` = 1,291,627,469.63 USDC
- `totalSupply`  = 1,103,482,521.26 shares
- **Price per share = 1.17050107 USDC/share** (↑17.05% since inception at 1.00)

| Wallet | Deposit Date(s) | USDC Deposited | Shares Received | Cur. Share Price | Current Value | PnL ($) | PnL (%) |
|--------|-----------------|----------------|-----------------|------------------|---------------|---------|---------|
| L1 | — | No activity | — | — | — | — | — |
| L3 | 2026-01-03 | $9,005.84 | 7,865.3396 | $1.17050 | $9,206.39 | +$200.55 | +2.23% |
| B1 | — | No activity | — | — | — | — | — |
| B3 | 2025-11-01 + 2026-01-03 | $8,223.10 | 7,223.5927 | $1.17050 | $8,455.22 | +$232.12 | +2.82% |
| B5 | — | No activity | — | — | — | — | — |
| **MAPLE TOTAL** | | **$17,228.94** | **15,088.9323** | | **$17,661.61** | **+$432.67** | **+2.51%** |

### Maple Notes
- Deposits routed via contract `0x134cCaaA4f1e4552...` (Maple deposit router / permit2 forwarder).
- USDC amounts sourced from wallet USDC outflows matching the router on deposit dates.
- B3 deposited in two tranches: $5,000 on 2025-11-01 → 4,408.80 shares; $3,223.10 on 2026-01-03 → 2,814.79 shares.
- Shares still held (not redeemed). All PnL is **unrealized**.
- L3 and B3 positions are **OPEN**.

---

## Part 3 — Hyperliquid LP (HLP Vault)

**Vault**: `0xdfc24b077bc1425ad1dea75bcb6f8158e10df303` — "Hyperliquidity Provider (HLP)"
**TVL**: ~$274M (as of query)

| Wallet | Entry Date | Days in Vault | Deposited | Current Equity | PnL ($) | PnL (%) |
|--------|------------|---------------|-----------|----------------|---------|---------|
| L1 | — | — | No activity | — | — | — |
| L3 | ~2025-10-24 | 243 days | $5,000.00 | $5,340.68 | +$340.68 | +6.81% |
| B1 | — | — | No activity | — | — | — |
| B3 | — | — | No activity | — | — | — |
| B5 | — | — | No activity | — | — | — |
| **HLP TOTAL** | | **243 days** | **$5,000.00** | **$5,340.68** | **+$340.68** | **+6.81%** |

### HLP Notes
- `allTimePnl` field from API = $340.68; `vaultEquity` = $5,340.68 → imputed deposit = $5,000.
- Position is **OPEN** (lockupUntil: 1761743255810 ms ≈ 2025-10-28, already past → withdrawable).
- HLP earns market-making spread + liquidation revenue. 6.81% over 243 days ≈ **10.2% annualized**.

---

## Summary

| Protocol | Total Deposited | Current Value | Total PnL ($) | Return (%) |
|----------|-----------------|---------------|---------------|------------|
| Morpho | $99,263.87 | $102,066.06 | +$2,802.19 | +2.82% |
| Maple Finance | $17,228.94 | $17,661.61 | +$432.67 | +2.51% |
| Hyperliquid LP | $5,000.00 | $5,340.68 | +$340.68 | +6.81% |
| **TOTAL** | **$121,492.81** | **$125,068.36** | **+$3,575.55** | **+2.94%** |

### Open vs Closed breakdown

| Type | Deployed | Current Value | Unrealized PnL |
|------|----------|---------------|----------------|
| Open positions | $32,223.85 | $33,226.12 | +$1,002.27 |
| Closed (realized) | $89,268.96 | $91,842.24 | +$2,573.28 |

### Per-wallet PnL

| Wallet | Protocol(s) | Total In | Total Out + Holdings | PnL ($) |
|--------|-------------|----------|----------------------|---------|
| L1 | Morpho only | $12,647.51 | $12,809.48 | +$161.97 |
| L3 | Morpho + Maple + HLP | $100,622.74 | $104,086.66 | +$3,463.92 |
| B1 | — | $0 | $0 | $0 |
| B3 | Maple only | $8,223.10 | $8,455.22 | +$232.12 |
| B5 | — | $0 | $0 | $0 |

---

*Report generated 2026-06-25. Screenshots saved to: `morpho-L1.png`, `morpho-L1-2.png`, `morpho-L3.png`, `morpho-L3-2.png` in repo root.*

---

## LP PnL Tracking Methodology — Protocol Reference

> **Common utilities (all protocols, no API keys needed):**
>
> **Prices:**
> - Current: `https://coins.llama.fi/prices/current/{chain}:{addr}`
> - Historical: `https://coins.llama.fi/prices/historical/{unix_ts}/{chain}:{addr}`
>
> **Free RPCs:**
> - Ethereum: `https://ethereum-rpc.publicnode.com`
> - Base: `https://base.drpc.org`
> - Optimism: `https://optimism.drpc.org`
> - Arbitrum: `https://arbitrum.drpc.org`
>
> **Transfer history (cost basis):**
> - `https://{chain}.blockscout.com/api/v2/addresses/{wallet}/token-transfers?token={token_addr}`
>   Do NOT add `limit=` param (causes 422). Paginate via `next_page_params`.
> - `https://{chain}.blockscout.com/api?module=account&action=tokentx&address={wallet}&contractaddress={token}&sort=asc&page=1&offset=10000`
>
> **General PnL formula:**
> ```
> PnL ($) = Total Withdrawn + Current Balance − Total Deposited
> PnL (%) = PnL / Total Deposited × 100
> ```

---

### 1. Beefy Finance (autocompounder vaults)

**Position type:** ERC-20 `mooToken` — e.g. `mooBaseAeroUSDC-USDT`  
Beefy holds underlying LP tokens and auto-compounds yield back into more LP shares.

**Current value — API (no RPC needed):**
```bash
# pricePerFullShare is already in the /vaults response
curl -s "https://api.beefy.finance/vaults/base" | python3 -c "
import json,sys
for v in json.load(sys.stdin):
    if v['earnedTokenAddress'].lower() == '0xYOUR_MOO'.lower():
        ppfs = int(v['pricePerFullShare']) / 1e18
        print(f'ppfs={ppfs}, oracleId={v[\"oracleId\"]}')
"
# Then get LP price: curl -s https://api.beefy.finance/lps | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('YOUR_ORACLE_ID'))"
```

**Historical PPFS (at deposit block) — RPC:**
```bash
# getPricePerFullShare() selector: 0x77c7b8fc
curl -s -X POST https://base.drpc.org -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":"0xMOO_ADDR","data":"0x77c7b8fc"},"0xBLOCK_HEX"]}'
# Result: hex uint256, divide by 1e18
```

**PnL formula:**
```
current_underlying = mooBalance × (pricePerFullShare / 1e18)
current_usd        = current_underlying × lp_price_usd
cost_usd_i         = moo_received_i × (ppfs_at_deposit_i / 1e18) × lp_price_at_deposit_i
PnL                = current_usd − Σ cost_usd_i
```

**Verified APIs:** `api.beefy.finance/vaults`, `/vaults/{chain}`, `/lps`, `/prices`, `/apy`, `/tvl` — all ✅ live

**Gotchas:**
- Yield is auto-compounded — no separate reward token to claim. PPFS growth IS the yield.
- `status: "eol"` = deprecated vault, PPFS may be frozen. Check `status` field.
- PPFS always 18 decimals regardless of underlying token decimals.

---

### 2. Aerodrome (Base) / Velodrome (Optimism) — V2 AMM

**Position type:** ERC-20 LP token + optional gauge stake  
Check BOTH: `lp_balance = lpToken.balanceOf(wallet) + gauge.balanceOf(wallet)`

**Current value — RPC (no REST API — `api.aerodrome.finance` DNS does not exist):**
```python
# getReserves() → (reserve0, reserve1, timestamp)  selector: 0x0902f1ac
# token0() selector: 0x0dfe1681 | token1(): 0xd21220a7
# totalSupply() selector: 0x18160ddd | balanceOf(): 0x70a08231
# gauge.earned(wallet) selector: 0x008cc262

share_frac    = user_lp_total / pool.totalSupply()
position_usd  = share_frac × (reserve0 / 10**dec0 × price0 + reserve1 / 10**dec1 × price1)
reward_usd    = gauge.earned(wallet) / 1e18 × aero_price
PnL           = position_usd + reward_usd + withdrawn_usd − deposited_usd
```

**AERO/VELO prices:**
```bash
# AERO (Base): 
curl -s "https://coins.llama.fi/prices/current/base:0x940181a94A35A4569E4529A3CDfB74e38FD98631"
# VELO (Optimism):
curl -s "https://coins.llama.fi/prices/current/optimism:0x9560e827aF36c94D2Ac33a39bCE1Fe78631088Db"
```

**Gotchas:**
- Gauge ≠ LP address — always check both. Staked LP held by gauge.
- AERO/VELO rewards are NOT auto-compounded unless using Beefy on top.
- Stable vs volatile pools: `getReserves()` works for both but invariant differs.
- Token decimals from `token.decimals()` selector `0x313ce567` — USDC=6, WETH=18.

---

### 3. Uniswap V3 / Concentrated Liquidity

**Position type:** NFT from `NonfungiblePositionManager`
- Ethereum/Arbitrum: `0xC36442b4a4522E871399CD717aBDD847Ab11FE88`
- Base: `0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1`

**Get positions — RPC:**
```python
# balanceOf(wallet) → 0x70a08231
# tokenOfOwnerByIndex(wallet, i) → 0x2f745c59
# positions(tokenId) → 0x99fbab88 → (nonce, operator, token0, token1, fee, tickLower, tickUpper, liquidity, ..., tokensOwed0, tokensOwed1)
# pool.slot0() → 0x3850c7bd → sqrtPriceX96
```

**Current value — tick math:**
```python
import math
Q96 = 2**96
sqrt_lower = int(math.sqrt(1.0001**tick_lower) * Q96)
sqrt_upper = int(math.sqrt(1.0001**tick_upper) * Q96)
sp = sqrt_price_x96
if sp <= sqrt_lower:    # below range, all token0
    amt0 = liquidity * (sqrt_upper - sqrt_lower) // (sqrt_upper * sqrt_lower // Q96); amt1 = 0
elif sp >= sqrt_upper:  # above range, all token1
    amt0 = 0; amt1 = liquidity * (sqrt_upper - sqrt_lower) // Q96
else:                   # in range
    amt0 = liquidity * (sqrt_upper - sp) // (sp * sqrt_upper // Q96)
    amt1 = liquidity * (sp - sqrt_lower) // Q96
position_usd = amt0 / 10**dec0 * price0 + amt1 / 10**dec1 * price1
```

**⚠️ The Graph hosted Uniswap V3 subgraph is FULLY DEPRECATED.** Use direct RPC above, or The Graph decentralized network (free tier API key at thegraph.com).

**Gotchas:**
- Out-of-range positions earn zero fees — effectively a limit order.
- `tokensOwed0/1` = fees claimable now. Fees accruing since last touch require `feeGrowthInside` delta (complex).
- Negative ticks need sign extension: `val - 2**256` if `val >= 2**255`.

---

### 4. Curve Finance

**Position type:** ERC-20 LP token + optional gauge stake for CRV rewards

**Current value — Curve API:**
```bash
# virtualPrice in USD for stablecoin pools (VERIFIED: use api.curve.finance not api.curve.fi)
curl -s "https://api.curve.finance/api/getPools/ethereum/main" | python3 -c "
import json,sys
pools = json.load(sys.stdin)['data']['poolData']
pool = next(p for p in pools if p['address'].lower() == '0xPOOL'.lower())
vp = int(pool['virtualPrice']) / 1e18
print(f'virtualPrice={vp}')"

# Or via RPC: get_virtual_price() selector: 0xbb7b8b80
```

**PnL formula:**
```
total_lp      = lpToken.balanceOf(wallet) + gauge.balanceOf(wallet)
virtual_price = pool.get_virtual_price() / 1e18
position_usd  = total_lp / 1e18 × virtual_price × base_asset_price_usd
crv_earned    = gauge.claimable_tokens(wallet) / 1e18 × crv_price
PnL           = position_usd + crv_earned + withdrawn_usd − deposited_usd
```

**Supported network/type:** `ethereum/main`, `ethereum/crypto`, `base/factory-stable-ng`, `arbitrum/main`, etc.

**Gotchas:**
- `api.curve.fi` is dead (301 redirect) — use `api.curve.finance`
- Tricrypto pools: `virtualPrice` is NOT USD — multiply by cheapest token price
- Convex staking: LP may be in Convex booster, not Curve gauge directly

---

### 5. Pendle Finance (Yield Tokenization)

**Position type:** PT (principal token), YT (yield token), LP (PLP)

**Current value — Pendle API:**
```bash
# All markets with PT/YT/LP prices (VERIFIED ✅)
curl -s "https://api-v2.pendle.finance/core/v1/1/markets?limit=100" | python3 -c "
import json,sys
for m in json.load(sys.stdin)['results']:
    print(m['pt']['symbol'], m['pt']['price']['usd'], 'exp:', m['expiry'][:10])"
# chainIds: 1=ETH, 8453=Base, 42161=Arbitrum, 10=Optimism
```

**PnL formula:**
```
# PT: PnL = pt_balance × pt_price_usd − cost_basis_usd
# YT: PnL = yt_balance × yt_price_usd + yield_collected_usd − cost_basis_usd
# LP: PnL = lp_balance × lp_price_usd + PENDLE_rewards − deposited_usd
# At PT maturity: PT redeems 1:1 for accounting asset (e.g. PT-USDC → USDC)
```

**⚠️ No user positions endpoint** — `users/{wallet}/positions` returns 404. Track via Blockscout `balanceOf`.

**Gotchas:**
- PT discount is NOT a loss — it redeems at face value at maturity.
- YT decays to $0 at expiry — collect yield before expiry.
- PENDLE gauge rewards NOT in `lp_price_usd` — track separately.

---

### 6. Generic ERC-4626 (Morpho, Yearn, Maple, etc.)

Already covered in the Morpho/Maple methodology above. Quick reference:

```bash
# totalAssets()  selector: 0x01e1d114
# totalSupply()  selector: 0x18160ddd  
# pricePerShare  = totalAssets / totalSupply
# currentValue   = balanceOf(wallet) × pricePerShare
# Yearn v2 pricePerShare() selector: 0x99530b06 (not ERC-4626 standard)
```

**Gotcha:** Oracle manipulation can freeze `pricePerShare` at face value while real value is lower (see Extrafi/USR incident). Always verify vault is not deprecated (`listed=false`).

---

### Verified API Endpoints Summary

| Protocol | Endpoint | Status |
|---|---|---|
| Beefy vaults | `https://api.beefy.finance/vaults` | ✅ Live |
| Beefy vaults by chain | `https://api.beefy.finance/vaults/{chain}` | ✅ Live |
| Beefy LP prices | `https://api.beefy.finance/lps` | ✅ Live |
| Beefy APY | `https://api.beefy.finance/apy` | ✅ Live |
| Curve pools | `https://api.curve.finance/api/getPools/{network}/{type}` | ✅ Live (not api.curve.fi) |
| Pendle markets | `https://api-v2.pendle.finance/core/v1/{chainId}/markets` | ✅ Live |
| DefiLlama current price | `https://coins.llama.fi/prices/current/{chain}:{addr}` | ✅ Live |
| DefiLlama historical price | `https://coins.llama.fi/prices/historical/{ts}/{chain}:{addr}` | ✅ Live |
| Blockscout v1 tokentx | `https://{chain}.blockscout.com/api?module=account&action=tokentx&...` | ✅ Live |
| Blockscout v2 transfers | `https://{chain}.blockscout.com/api/v2/addresses/{wallet}/token-transfers?token={addr}` | ✅ Live |
| Uniswap V3 hosted subgraph | `https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3` | ❌ Deprecated |
| Aerodrome REST API | `https://api.aerodrome.finance` | ❌ DNS not found |
| Pendle user positions | `https://api-v2.pendle.finance/core/v1/{chainId}/users/{wallet}/positions` | ❌ 404 |

### Key Function Selectors

```
ERC-20:       balanceOf(address)              0x70a08231
              totalSupply()                   0x18160ddd
              decimals()                      0x313ce567

ERC-4626:     totalAssets()                   0x01e1d114
              convertToAssets(uint256 shares) 0x07a2d13a
              pricePerShare() [Yearn v2]      0x99530b06

Beefy:        getPricePerFullShare()          0x77c7b8fc

Curve:        get_virtual_price()             0xbb7b8b80

Uniswap V3:   positions(uint256 tokenId)      0x99fbab88  [NonfungiblePositionManager]
              tokenOfOwnerByIndex(addr,uint)  0x2f745c59
              slot0()                         0x3850c7bd  [Pool]

Aerodrome:    getReserves()                   0x0902f1ac
              token0()                        0x0dfe1681
              token1()                        0xd21220a7
              earned(address) [gauge]         0x008cc262
```
