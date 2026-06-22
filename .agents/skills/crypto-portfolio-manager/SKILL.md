---
name: crypto-portfolio-manager
description: "Manages the crypto portfolio — reads current positions, runs analysis on every token in the universe (BTC/ETH/SOL/UNI/HYPE/AAVE/LINK), and outputs a BUY/SELL/HOLD decision per token with sizing. Run on demand or via /loop. Educational, not advice."
license: MIT
compatibility: opencode
metadata:
  audience: crypto-allocators
  domain: crypto-portfolio-management
  role: portfolio-manager
---

# Crypto Portfolio Manager

Read positions → analyze every token in parallel → decide BUY/SELL/HOLD per token → print the signal table.

> Educational analysis, not financial advice. No leverage. Ever.

## Portfolio state

Positions live in `crypto/POSITIONS.json`. Create it if missing:

```json
{
  "updated_at": "2026-06-22T00:00:00Z",
  "portfolio_usd": 100000,
  "dry_powder_pct": 30,
  "positions": [
    {"symbol": "BTC",  "size_usd": 0, "entry_price": 0, "target_pct": 25},
    {"symbol": "ETH",  "size_usd": 0, "entry_price": 0, "target_pct": 10},
    {"symbol": "SOL",  "size_usd": 0, "entry_price": 0, "target_pct": 5},
    {"symbol": "UNI",  "size_usd": 0, "entry_price": 0, "target_pct": 3},
    {"symbol": "HYPE", "size_usd": 0, "entry_price": 0, "target_pct": 3},
    {"symbol": "AAVE", "size_usd": 0, "entry_price": 0, "target_pct": 3},
    {"symbol": "LINK", "size_usd": 0, "entry_price": 0, "target_pct": 3}
  ]
}
```

If `portfolio_usd = 0`, stop and ask the user to fill in their actual positions.

## Step 1 — Run analysis for every token in parallel

Spawn one `analysis-comprehensive-crypto` subagent per token **simultaneously**.
Each returns a compact verdict:

```json
{
  "symbol": "BTC",
  "quorum_verdict": "BULLISH | SPLIT | BEARISH | UNCERTAIN",
  "dominant_zone":  "DEEP_VALUE | FAIR_VALUE | ELEVATED | EXTREME | UNKNOWN",
  "seats_bull": 3,
  "seats_bear": 2,
  "key_support": 60000,
  "key_resistance": 66000,
  "confidence": "HIGH | MED | LOW"
}
```

TradingView symbol mapping: append `USDT` on `BINANCE:` prefix (e.g. `BINANCE:BTCUSDT`).

## Step 2 — Decide per token

| Signal | Condition |
|---|---|
| **BUY** | `quorum_verdict = BULLISH`, seats_bull ≥ 3, position below target |
| **BUY (small)** | `quorum_verdict = SPLIT`, `dominant_zone = DEEP_VALUE`, dry powder > 20% |
| **SELL** | `quorum_verdict = BEARISH`, seats_bear ≥ 4, have a position |
| **HOLD** | everything else |

Size caps: BTC/ETH max 40%, SOL max 10%, each alt max 5%. Never deploy >25% of dry powder in one run.

## Step 3 — Print signal table

```
=== PORTFOLIO RUN — {timestamp} ===

Token | Quorum  | Zone       | Signal | Size
------|---------|------------|--------|----------
BTC   | BEARISH | FAIR_VALUE | HOLD   | —
ETH   | SPLIT   | FAIR_VALUE | HOLD   | —
SOL   | BEARISH | ELEVATED   | SELL   | $3,200
...

Dry powder deployed: $X / $Y budget
```

Write signals to `crypto/signals/SIGNALS-{YYYY-MM-DD}.jsonl` (one line per token, append-only).
Update `crypto/POSITIONS.json` `updated_at`.

## Running continuously

Use `/loop` inside an agent session:
```
/loop interval=6h
/stop
```
