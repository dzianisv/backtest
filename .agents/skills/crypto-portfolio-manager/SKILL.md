---
name: crypto-portfolio-manager
description: "Manages the crypto portfolio — runs analysis on every token in the universe (BTC/ETH/SOL/UNI/HYPE/AAVE/LINK) and outputs a BUY/SELL/HOLD decision per token. Run on demand or via /loop. Educational, not advice."
license: MIT
compatibility: opencode
metadata:
  audience: crypto-allocators
  domain: crypto-portfolio-management
  role: portfolio-manager
---

# Crypto Portfolio Manager

Analyze every token in the universe in parallel → decide BUY/SELL/HOLD per token → print the signal table.

> Educational analysis, not financial advice. No leverage. Ever.

## Token universe

BTC, ETH, SOL, UNI, HYPE, AAVE, LINK — edit this list to add/remove tokens.

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

TradingView symbol mapping: `BINANCE:{TOKEN}USDT` (e.g. `BINANCE:BTCUSDT`).

## Step 2 — Decide per token

| Signal | Condition |
|---|---|
| **BUY** | `quorum_verdict = BULLISH`, seats_bull ≥ 3 |
| **BUY (small)** | `quorum_verdict = SPLIT`, `dominant_zone = DEEP_VALUE` |
| **SELL** | `quorum_verdict = BEARISH`, seats_bear ≥ 4 |
| **HOLD** | everything else |

## Step 3 — Print signal table

```
=== PORTFOLIO RUN — {timestamp} ===

Token | Quorum  | Zone       | Signal
------|---------|------------|-------
BTC   | BEARISH | FAIR_VALUE | HOLD
ETH   | SPLIT   | FAIR_VALUE | HOLD
SOL   | BEARISH | ELEVATED   | SELL
...
```

## Running continuously

```
/loop interval=6h
/stop
```
