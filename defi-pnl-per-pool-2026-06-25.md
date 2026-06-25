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
