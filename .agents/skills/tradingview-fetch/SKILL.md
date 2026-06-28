---
name: tradingview-fetch
description: "Fetches OHLCV + technical indicators from TradingView for a list of tokens or stocks, writes each result to .cache/tradingview/{date}/{SYMBOL}.json. Use this skill to pre-fetch TradingView data so downstream agents (seats, subagents, openclaw plugins) can read it as plain JSON without needing MCP access. Handles the single-chart-slot constraint internally — always sequential per symbol. Triggered by: 'fetch tradingview data for [tokens]', or called as a pre-step by crypto-advisor / stocks-advisor before running seat analysis."
license: MIT
compatibility: opencode
metadata:
  audience: internal-skill
  domain: market-data
  role: data-fetcher
---

# tradingview-fetch

Fetch TradingView technical data for a symbol list and write it to disk.
Once written, any agent reads the output as plain JSON — no MCP, no browser, no session constraint.

> This skill owns the single-chart-slot. It is always sequential. Parallelism lives downstream (in seat analysis), not here.

---

## Input

Symbols passed as a space-separated list, e.g.:

```
BTC ETH SOL HYPE AERO
```

Or with exchange prefix for stocks:

```
NASDAQ:NVDA NYSE:AAPL
```

TradingView symbol mapping defaults:
- Crypto: `BINANCE:{TOKEN}USDT` (fallback: `OKX:{TOKEN}USDT`)
- Stocks: `NASDAQ:{TICKER}` or `NYSE:{TICKER}`

---

## Output

Writes one file per symbol:

```
.cache/tradingview/{YYYY-MM-DD}/{SYMBOL}.json
```

Example: `.cache/tradingview/2026-06-28/BTC.json`

Returns the cache directory path on completion.

---

## Data pulled per symbol

```
D timeframe:
  - OHLCV count=365 summary=true   → 52w high/low, avg volume
  - OHLCV count=210 summary=false  → ≥200 daily closes (for SMA200)
  - study_values                   → RSI(14), BB(20,2), MACD(12,26,9), Volume

W timeframe:
  - OHLCV count=210 summary=false  → weekly closes (for 200wMA)

Computed via indicators.py:
  - EMA20, SMA50, SMA200, 200wMA (or INSUFFICIENT if weekly_closes < 200)
  - death_cross (SMA50 < SMA200)
  - zone (DEEP_VALUE / FAIR_VALUE / ELEVATED / EXTREME / UNKNOWN)
  - pct_below_ath, pct_below_200wma

Screenshot:
  - capture_screenshot → saved to .cache/tradingview/{date}/{SYMBOL}.png
```

---

## Steps

**0. Set up output directory**

```bash
DATE=$(date +%F)
CACHE_DIR=".cache/tradingview/$DATE"
mkdir -p "$CACHE_DIR"
INDICATORS=".agents/skills/crypto-advisor/scripts/indicators.py"
```

**1. For each symbol — sequential (single chart slot)**

```
tradingview-chart_get_state
  → inspect studies list
  → deduplicate: add ONLY if not present: "Relative Strength Index", "Bollinger Bands", "MACD"
  → remove duplicates with chart_manage_indicator action=remove

tradingview-chart_set_symbol   symbol="{TV_SYMBOL}"
tradingview-chart_set_timeframe timeframe="D"
tradingview-data_get_ohlcv     count=365 summary=true    → d_summary (52w hi/lo + avg vol)
tradingview-data_get_ohlcv     count=210 summary=false   → d_closes[]
tradingview-data_get_study_values                        → rsi, bb, macd, volume
tradingview-chart_set_timeframe timeframe="W"
tradingview-data_get_ohlcv     count=210 summary=false   → w_closes[]
tradingview-chart_set_timeframe timeframe="D"             → reset to daily
tradingview-capture_screenshot                           → save to $CACHE_DIR/{SYMBOL}.png
```

**2. Compute MAs**

```bash
INPUT_JSON=$(python3 -c "
import json, sys
print(json.dumps({
  'symbol': '$SYMBOL',
  'price': $PRICE,
  'daily_closes': $D_CLOSES,
  'weekly_closes': $W_CLOSES
}))
")

INDICATORS_OUT=$(/Users/engineer/.venv/bin/python3 "$INDICATORS" <(echo "$INPUT_JSON"))
```

**200wMA sufficiency rule:**
- `weekly_closes < 200` → set `wma200 = null`, `wma200_label = "INSUFFICIENT (Nwk)"`, compute proxy MA from available weeks, label as `~{N}wk MA proxy`
- `weekly_closes >= 200` → compute 200wMA normally

**3. Compute zone**

```
pct_below_ath   = (ath - price) / ath * 100
pct_below_200wma = (wma200 - price) / wma200 * 100   (null if wma200 null)

zone =
  UNKNOWN     if wma200 is null AND pct_below_ath < 20
  DEEP_VALUE  if pct_below_ath >= 50 AND pct_below_200wma >= 30
  FAIR_VALUE  if pct_below_ath >= 20
  ELEVATED    if 0 <= pct_below_ath < 20
  EXTREME     if pct_below_ath < 0  (price above ATH)
```

**4. Write JSON**

```bash
python3 -c "
import json

result = {
  'symbol': '$SYMBOL',
  'fetched_at': '$DATE',
  'price_usd': $PRICE,
  'weekly_closes': $WEEKLY_COUNT,
  'ema20': ...,
  'sma50': ...,
  'sma200': ...,
  'wma200': ...,            # null if insufficient
  'wma200_label': '...',    # '200wMA' or 'INSUFFICIENT (Nwk)' or '~Nwk MA proxy'
  'death_cross': bool,
  'rsi_14': ...,
  'macd_line': ...,
  'macd_signal': ...,
  'macd_hist': ...,
  'bb_upper': ...,
  'bb_mid': ...,
  'bb_lower': ...,
  'bb_position': '...',     # ABOVE_UPPER / ABOVE_MID / BELOW_MID / BELOW_LOWER
  'vol_vs_30d_avg': ...,    # ratio: 1.0 = in line with avg
  'high_52w': ...,
  'low_52w': ...,
  'pct_from_52wh': ...,
  'pct_below_ath': ...,
  'pct_below_200wma': ...,  # null if wma200 null
  'zone': '...',
  'screenshot': '$CACHE_DIR/$SYMBOL.png'
}

open('$CACHE_DIR/$SYMBOL.json', 'w').write(json.dumps(result, indent=2))
print(f'Written: $CACHE_DIR/$SYMBOL.json')
"
```

**5. Print summary and return cache path**

```
=== tradingview-fetch COMPLETE ===
Date:    {DATE}
Symbols: {N} fetched
Cache:   .cache/tradingview/{DATE}/

Files written:
  BTC.json  BTC.png
  ETH.json  ETH.png
  ...

Any agent can read these files directly — no MCP required.
```

---

## How downstream skills use the output

**Trend seat (investor-stanley-druckenmiller):**
```bash
cat .cache/tradingview/{DATE}/{TOKEN}.json
# receives the full technical package — MAs, RSI, death cross, zone
```

**Other seats (value / quality / cycle / onchain):**
```bash
# read only what they need:
python3 -c "
import json
d = json.load(open('.cache/tradingview/{DATE}/{TOKEN}.json'))
print(d['price_usd'], d['zone'], d['pct_below_ath'])
"
# then fetch their own data from DeFiLlama / F&G / news
```

**crypto-advisor / stocks-advisor orchestrator:**
```bash
# Before running quorum — call tradingview-fetch first:
# "Run tradingview-fetch for: BTC ETH SOL TON HYPE AAVE JUP UNI AERO PUMP LINK"
# Then read .cache/tradingview/{today}/*.json for each token
# No MCP calls in the orchestrator's quorum phase
```

---

## Error handling

| Error | Action |
|---|---|
| Symbol not found on Binance | Try `OKX:{TOKEN}USDT`; if still fails, write `"error": "symbol_not_found"` in JSON |
| Study already present | Skip `add` — use existing; do NOT add duplicate |
| `weekly_closes < 200` | Set `wma200: null`, compute proxy, label INSUFFICIENT — not an error |
| Screenshot fails | Write `"screenshot": null` — not a blocking error |
| indicators.py fails | Write `"error": "indicators_failed"`, log stdout/stderr |
