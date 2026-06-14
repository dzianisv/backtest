#!/usr/bin/env python3
"""
crypto_dip_scanner.py — Daily crypto dip scanner.
Checks major crypto for % below 52-week INTRADAY high, Fear & Greed, BTC funding rate.
Educational only — not investment advice.

Usage:
    python3 crypto_dip_scanner.py
    python3 crypto_dip_scanner.py --threshold 25
    python3 crypto_dip_scanner.py --json

Data sources (all free, no API key):
  - Prices:      yfinance  (BTC-USD, ETH-USD, etc.) — High/Close, auto_adjust=False
  - Fear & Greed: api.alternative.me/fng/
  - Funding rate: fapi.binance.com (Binance perp futures; geo-blocked in US/some pods → null)

Honesty notes:
  - "52w high" = max trailing-1y INTRADAY HIGH, not a closing max, not all-time.
  - sma200 is null when <200 days of history exist.
"""
from __future__ import annotations
import argparse, json, sys
from urllib.request import Request, urlopen

try:
    import yfinance as yf
except ImportError:
    sys.exit("pip install yfinance")

CRYPTO = {
    "BTC":  "BTC-USD",
    "ETH":  "ETH-USD",
    "SOL":  "SOL-USD",
    "BNB":  "BNB-USD",
    "AVAX": "AVAX-USD",
    "LINK": "LINK-USD",
}


def _get(url: str) -> dict | list | None:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception:
        return None


def fear_greed() -> dict | None:
    d = _get("https://api.alternative.me/fng/?limit=1")
    try:
        if d and d.get("data"):
            v = d["data"][0]
            return {"value": int(v["value"]), "label": v["value_classification"]}
    except (KeyError, ValueError, TypeError):
        return None
    return None


def btc_funding_rate() -> float | None:
    d = _get("https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1")
    try:
        if isinstance(d, list) and d:
            return round(float(d[0]["fundingRate"]) * 100, 5)
    except (KeyError, ValueError, TypeError):
        return None
    return None


def scan(threshold_pct: float = 20.0) -> tuple[list[dict], dict | None, float | None]:
    tickers = list(CRYPTO.values())
    try:
        raw = yf.download(tickers, period="1y", auto_adjust=False, progress=False, group_by="column")
        close = raw["Close"]
        high = raw["High"]
    except Exception as e:
        print(f"[crypto-dip] fetch failed: {e}", file=sys.stderr)
        return [], fear_greed(), btc_funding_rate()

    hits = []
    for name, yf_sym in CRYPTO.items():
        try:
            if yf_sym not in close.columns:
                print(f"[crypto-dip] no data for {name} (skipped)", file=sys.stderr)
                continue
            cs = close[yf_sym].dropna()
            hs = high[yf_sym].dropna()
            if len(cs) < 20 or len(hs) < 20:
                continue
            current = float(cs.iloc[-1])
            high_52w = float(hs.max())
            pct_from_high = (current - high_52w) / high_52w * 100
            if len(cs) >= 200:
                sma200 = float(cs.rolling(200).mean().iloc[-1])
                pct_vs_200d = round((current - sma200) / sma200 * 100, 1)
            else:
                sma200 = None
                pct_vs_200d = None
            if pct_from_high <= -threshold_pct:
                hits.append({
                    "ticker": name,
                    "current_usd": round(current, 2),
                    "high_52w_usd": round(high_52w, 2),
                    "pct_from_high": round(pct_from_high, 1),
                    "sma200_usd": round(sma200, 2) if sma200 is not None else None,
                    "pct_vs_200d": pct_vs_200d,
                    "conviction": (
                        "HIGH" if pct_from_high <= -40
                        else "MEDIUM" if pct_from_high <= -30
                        else "WATCH"
                    ),
                })
        except Exception as e:
            print(f"[crypto-dip] {name} parse error: {e}", file=sys.stderr)
            continue

    hits.sort(key=lambda x: x["pct_from_high"])
    return hits, fear_greed(), btc_funding_rate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=20.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    hits, fg, fr = scan(a.threshold)

    if a.json:
        print(json.dumps({"dips": hits, "fear_greed": fg, "btc_funding_rate_pct": fr}, indent=2))
        return

    print("\n=== CRYPTO DIP SCANNER ===\n")
    if fg:
        zone = "BUY ZONE" if fg["value"] <= 25 else "GREED ZONE" if fg["value"] >= 75 else "NEUTRAL"
        print(f"  Fear & Greed: {fg['value']}/100 ({fg['label']})  [{zone}]")
    else:
        print("  Fear & Greed: [UNAVAILABLE]")
    if fr is not None:
        fr_note = "shorts dominant" if fr < -0.01 else "overleveraged longs" if fr > 0.05 else "neutral"
        print(f"  BTC Funding:  {fr:+.4f}%  [{fr_note}]")
    else:
        print("  BTC Funding:  [UNAVAILABLE — Binance geo-blocked]")
    print()

    if not hits:
        print(f"  No crypto >= {a.threshold:.0f}% below 52w high today.")
    else:
        for r in hits:
            label = {"HIGH": "[HIGH]", "MEDIUM": "[MED]", "WATCH": "[WATCH]"}[r["conviction"]]
            if r["sma200_usd"] is not None:
                trend = "above" if r["pct_vs_200d"] >= 0 else "below"
                ma = f"200dMA ${r['sma200_usd']:,.0f} ({r['pct_vs_200d']:+.1f}% {trend})"
            else:
                ma = "200dMA n/a (<200d history)"
            print(
                f"  {label} {r['ticker']:5s}  {r['pct_from_high']:+.1f}% from 52w high (${r['high_52w_usd']:,.0f})  "
                f"now ${r['current_usd']:,.2f}  {ma}"
            )
    print("\n  Educational only — not advice.\n")


if __name__ == "__main__":
    main()
