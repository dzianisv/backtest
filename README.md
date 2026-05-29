# Dip-Tranche Strategy — Backtest

Tiered dip-buying strategy backtested against lump-sum and DCA across **VOO**, **QQQ**, and **VXUS** (2020–2026).

## Research Paper

📄 [Dip-Tranche Strategy: S&P 500, Nasdaq-100, International — Backtest 2020–2026](https://telegra.ph/Dip-Tranche-Strategy-SP-500-Nasdaq-100-International--Backtest-20202026-05-28)

Full write-up with charts, strategy mechanics, and per-symbol results.

## Strategy Summary

A $1,000,000 portfolio is split into three buckets:

| Bucket | Allocation | Deployment |
|--------|-----------|------------|
| Foundation | 50% ($500K) | Lump-sum on day 1 |
| DCA | 30% ($300K) | Equal weekly instalments over 18 months |
| Dip Reserve | 20% ($200K) | Tiered tranches triggered by drawdown from 52-week high |

**Dip Reserve tiers (VOO/VXUS baseline, QQQ ×1.4):**

| Tier | Reserve Share | Triggers | Sub-tranches |
|------|:---:|---|:---:|
| Tier 1 | 20% | −7%, −8.5%, −10%, time | 4 × $10K |
| Tier 2 | 30% | −12%, −14%, −16%, time | 4 × $15K |
| Tier 3 | 50% | −20%, −25%, −30%, time | 4 × $25K |

## Backtest Results (2020-01-01 → 2026-05-27)

| Symbol | Strategy CAGR | Lump Sum CAGR | DCA CAGR | Strategy Max DD |
|--------|:---:|:---:|:---:|:---:|
| VOO | 15.1% | 15.8% | 14.6% | −22.5% |
| QQQ | 19.6% | 21.7% | 17.6% | −31.2% |
| VXUS | **10.6%** | 10.2% | 10.3% | −26.6% |

> VXUS is the only symbol where the strategy beat both benchmarks — slower international recoveries reward tiered entry.

## Files

| File | Description |
|------|-------------|
| `backtest.py` | Full backtest engine — fetches data, runs all three strategies, prints report, saves PNG charts |
| `publish_report.py` | Builds and publishes the Telegraph report (uploads charts to Imgur, creates Telegraph page) |
| `VOO_backtest.png` | VOO results chart |
| `QQQ_backtest.png` | QQQ results chart |
| `VXUS_backtest.png` | VXUS results chart |

## How to Run

```bash
pip install yfinance matplotlib pandas numpy requests
python3 backtest.py          # generates charts + prints report
python3 publish_report.py    # publishes to telegra.ph
```

## Disclaimer

This repository is for educational and analytical purposes only. Nothing here constitutes financial advice. Past backtest performance does not guarantee future results. Consult a licensed fiduciary advisor before making any investment decisions.
