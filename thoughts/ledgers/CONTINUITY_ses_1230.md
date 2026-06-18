---
session: ses_1230
updated: 2026-06-18T23:08:58.100Z
---

# Session Summary

## Goal
Merge two separate skills (`dip-screener` for S&P 100 equities and `crypto-dip-scanner` for crypto) into a single unified `.agents/skills/dip-scanner/` skill with combined SKILL.md and dip_scanner.py.

## Constraints & Preferences
- Unified script must accept `--universe equity|crypto|all` argument
- Equity gate: regime-detection (RISK_ON required for alerts)
- Crypto gate: Fear & Greed < 25 (extreme fear)
- Keep threshold tiers: -20%/-25%/-30% for equity; -20%/-30%/-40% for crypto
- Both universes emit to convergence pool (`~/.openclaw/workspace/investor/pools/dip_candidates.jsonl`)
- Uses yfinance for both universes (auto_adjust=False, intraday highs)
- Old directories must be deleted after merge

## Progress
### Done
- [x] Read both source SKILL.md files (`.agents/skills/dip-screener/SKILL.md` and `.agents/skills/crypto-dip-scanner/SKILL.md`)
- [x] Read both source .py files (`dip_screener.py` and `crypto_dip_scanner.py`)
- [x] Created `.agents/skills/dip-scanner/` directory
- [x] Wrote unified `SKILL.md` with `name: dip-scanner` frontmatter, both universes documented, combined trigger phrases, both gates described, convergence pool references
- [x] Wrote unified `dip_scanner.py` (~300 lines) with `--universe`, `--threshold`, `--tickers`, `--json`, `--emit-pool` arguments
- [x] Deleted `.agents/skills/dip-screener/` and `.agents/skills/crypto-dip-scanner/`
- [x] Verified new directory exists with both files (SKILL.md: 8425 bytes, dip_scanner.py: 17992 bytes)
- [x] Python syntax validation passed (`ast.parse` OK)

### In Progress
- (none — task complete)

### Blocked
- (none)

## Key Decisions
- **Crypto conviction tiers shifted up vs equity**: Crypto uses -40%/-30%/-20% (vs equity -30%/-25%/-20%) because crypto volatility is higher — mirrors the original crypto-dip-scanner thresholds
- **SPY regime check self-contained in crypto path**: Rather than requiring the separate regime-detection skill, the crypto scan includes a lightweight SPY vs 200d-MA check inline for cross-reference
- **Funding rate is BONUS only**: Never suppresses a valid dip+fear alert; OKX primary, dYdX fallback (Binance 451, Bybit 403 known broken)
- **Price-ground mode (`--tickers`)**: Kept from equity original — allows arbitrary ticker grounding without universe scan or threshold filter
- **Batch downloading**: Equity uses 10-ticker batches via yfinance with fallback to single-fetch on miss; crypto fetches all 6 in one batch

## Next Steps
1. Task is complete — no further steps required
2. (Optional) Run `python3 .agents/skills/dip-scanner/dip_scanner.py --universe all --json` to validate live execution with network access
3. (Optional) Update any cron/scheduling references that pointed to old skill paths

## Critical Context
- The convergence pool path is `~/.openclaw/workspace/investor/pools/dip_candidates.jsonl` (durable, NOT /tmp — needed for cross-session cron reads)
- Schedule: equity at 07:45 UTC Mon-Fri, crypto at 07:50 UTC daily (or combined `--universe all` at 07:45)
- Data source: api.alternative.me/fng/ for Fear & Greed; OKX `/api/v5/public/funding-rate?instId=BTC-USD-SWAP` for funding; dYdX `indexer.dydx.trade/v4/perpetualMarkets?ticker=BTC-USD` as fallback
- The script outputs to `signal-convergence-alert` downstream (reads the JSONL pool at 08:30 UTC)

## File Operations
### Read
- `/Users/engineer/workspace/backtest/.agents/skills/dip-screener/SKILL.md`
- `/Users/engineer/workspace/backtest/.agents/skills/dip-screener/dip_screener.py`
- `/Users/engineer/workspace/backtest/.agents/skills/crypto-dip-scanner/SKILL.md`
- `/Users/engineer/workspace/backtest/.agents/skills/crypto-dip-scanner/crypto_dip_scanner.py`

### Created
- `/Users/engineer/workspace/backtest/.agents/skills/dip-scanner/SKILL.md` (8425 bytes)
- `/Users/engineer/workspace/backtest/.agents/skills/dip-scanner/dip_scanner.py` (17992 bytes)

### Deleted
- `/Users/engineer/workspace/backtest/.agents/skills/dip-screener/` (entire directory)
- `/Users/engineer/workspace/backtest/.agents/skills/crypto-dip-scanner/` (entire directory)
