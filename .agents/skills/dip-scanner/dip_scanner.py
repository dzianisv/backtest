#!/usr/bin/env python3
"""
dip_scanner.py — Unified daily dip scanner for equities AND crypto.
Screens S&P 100 and/or major crypto for assets >= threshold% below their 52-week
INTRADAY high. Equity is gated on regime (RISK_ON). Crypto is gated on Fear & Greed < 25.
Educational only — not investment advice.

Usage:
    python3 dip_scanner.py --universe all
    python3 dip_scanner.py --universe equity --threshold 25
    python3 dip_scanner.py --universe crypto --json
    python3 dip_scanner.py --universe all --emit-pool
    python3 dip_scanner.py --tickers LEU,BTC-USD,MSFT

Data sources (all free, no API key):
  - Prices:       yfinance (equities + crypto via -USD suffix), auto_adjust=False
  - Fear & Greed: api.alternative.me/fng/ (crypto gate)
  - Funding rate: OKX primary -> dYdX fallback (bonus for crypto)
  - Regime x-ref: SPY vs 200d-MA (lightweight, self-contained)

Honesty notes:
  - "52w high" = max trailing-1y INTRADAY HIGH, not closing max, not all-time.
  - sma200 is null when <200 trading days of history exist.
  - Funding: OKX=8h rate; dYdX=1h normalized x8. Binance (451) / Bybit (403) skipped.
"""
from __future__ import annotations
import argparse, json, os, sys, time
from datetime import datetime, timezone
from urllib.request import Request, urlopen

try:
    import yfinance as yf
except ImportError:
    sys.exit("pip install yfinance")

# === CONSTANTS ===

_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_SKILL_DIR, "..", "..", ".."))
DEFAULT_POOL = os.environ.get(
    "DIP_POOL", os.path.join(_REPO_ROOT, ".cache", "dip-scanner", "dip_candidates.jsonl"))

SP100 = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "BRK-B", "LLY", "JPM", "V",
    "UNH", "TSLA", "XOM", "MA", "JNJ", "PG", "AVGO", "HD", "COST", "ABBV",
    "MRK", "CVX", "KO", "PEP", "ADBE", "WMT", "BAC", "CRM", "ACN", "TMO",
    "MCD", "CSCO", "ABT", "DHR", "NFLX", "ORCL", "AMD", "QCOM", "TXN", "PM",
    "NEE", "AMGN", "IBM", "INTC", "HON", "CAT", "GE", "SPGI", "MS", "GS",
    "RTX", "BLK", "T", "UNP", "AXP", "ELV", "MDT", "PFE", "BMY", "GILD",
    "USB", "C", "LOW", "DE", "SBUX", "SCHW", "MO", "BA", "MMC", "CVS",
    "SO", "DUK", "CL", "ZTS", "CB", "NOW", "ISRG", "ADI", "REGN", "SYK",
    "PLD", "AMT", "EQIX", "VRTX", "PANW", "ANET", "MU", "KLAC", "LRCX", "SNPS",
    "AON", "TGT", "FDX", "ETN", "ADP", "ITW", "NSC", "WM", "APH", "CARR",
]

CRYPTO = {
    "BTC":  "BTC-USD",
    "ETH":  "ETH-USD",
    "SOL":  "SOL-USD",
    "BNB":  "BNB-USD",
    "AVAX": "AVAX-USD",
    "LINK": "LINK-USD",
}

# === HELPERS ===


def _http_get(url: str) -> dict | list | None:
    """Simple HTTP GET returning parsed JSON or None."""
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception:
        return None


def _ms_to_iso(ms) -> str | None:
    try:
        return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError, OSError):
        return None


def _fetch_single(ticker: str):
    """Fetch one ticker's unadjusted 1y OHLC. Returns (close_series, high_series) or (None, None)."""
    raw = yf.download(ticker, period="1y", auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        return None, None
    close = raw["Close"]
    high = raw["High"]
    if hasattr(close, "columns"):
        close = close[ticker] if ticker in close.columns else close.iloc[:, 0]
        high = high[ticker] if ticker in high.columns else high.iloc[:, 0]
    return close.dropna(), high.dropna()


# === CRYPTO-SPECIFIC DATA SOURCES ===


def fear_greed() -> dict | None:
    """Fetch crypto Fear & Greed index (0-100). < 25 = extreme fear."""
    d = _http_get("https://api.alternative.me/fng/?limit=1")
    try:
        if d and d.get("data"):
            v = d["data"][0]
            return {"value": int(v["value"]), "label": v["value_classification"]}
    except (KeyError, ValueError, TypeError):
        pass
    return None


def btc_funding_rate() -> dict | None:
    """Live BTC perp funding rate. OKX primary, dYdX fallback. Returns dict or None."""
    # OKX — 8h funding rate
    d = _http_get("https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USD-SWAP")
    try:
        if isinstance(d, dict) and d.get("code") == "0" and d.get("data"):
            row = d["data"][0]
            return {
                "rate_pct": round(float(row["fundingRate"]) * 100, 5),
                "venue": "OKX",
                "timestamp": _ms_to_iso(row.get("fundingTime")),
                "interval_h": 8,
            }
    except (KeyError, ValueError, TypeError, IndexError):
        pass
    # dYdX — 1h rate normalized to 8h
    d = _http_get("https://indexer.dydx.trade/v4/perpetualMarkets?ticker=BTC-USD")
    try:
        if isinstance(d, dict) and d.get("markets", {}).get("BTC-USD"):
            m = d["markets"]["BTC-USD"]
            rate_1h = float(m["nextFundingRate"])
            return {
                "rate_pct": round(rate_1h * 8 * 100, 5),
                "venue": "dYdX (1h x8)",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "interval_h": 8,
            }
    except (KeyError, ValueError, TypeError):
        pass
    return None


def spy_regime() -> dict | None:
    """Lightweight TradFi regime: SPY vs 200d-MA. RISK_OFF if below."""
    try:
        raw = yf.download("SPY", period="1y", auto_adjust=False, progress=False, group_by="column")
        cs = raw["Close"]
        if hasattr(cs, "columns"):
            cs = cs["SPY"]
        cs = cs.dropna()
        if len(cs) < 200:
            return None
        price = float(cs.iloc[-1])
        sma200 = float(cs.rolling(200).mean().iloc[-1])
        pct = (price - sma200) / sma200 * 100
        return {
            "ticker": "SPY",
            "price": round(price, 2),
            "sma200": round(sma200, 2),
            "pct_vs_200d": round(pct, 1),
            "regime": "RISK_OFF" if price < sma200 else "RISK_ON",
        }
    except Exception:
        return None


# === EVALUATION ===


def _evaluate_equity(ticker: str, cs, hs, threshold_pct: float, ground: bool = False):
    """Compute dip metrics for one equity ticker."""
    if cs is None or hs is None or len(cs) < 20 or len(hs) < 20:
        return None
    current = float(cs.iloc[-1])
    high_52w = float(hs.max())
    pct_from_high = (current - high_52w) / high_52w * 100
    as_of = cs.index[-1].date().isoformat()
    if len(cs) >= 200:
        sma200 = float(cs.rolling(200).mean().iloc[-1])
        pct_vs_200d = round((current - sma200) / sma200 * 100, 1)
    else:
        sma200 = None
        pct_vs_200d = None
    if not ground and pct_from_high > -threshold_pct:
        return None
    return {
        "ticker": ticker,
        "current": round(current, 2),
        "high_52w": round(high_52w, 2),
        "pct_from_high": round(pct_from_high, 1),
        "sma200": round(sma200, 2) if sma200 is not None else None,
        "pct_vs_200d": pct_vs_200d,
        "as_of": as_of,
        "conviction": (
            "HIGH" if pct_from_high <= -30
            else "MEDIUM" if pct_from_high <= -25
            else "WATCH"
        ),
    }


# === EQUITY SCANNING ===


def scan_equity(threshold_pct: float = 20.0) -> tuple[list[dict], list[str]]:
    """Scan S&P 100 for equity dips. Returns (hits, fetch_misses)."""
    results = []
    fetch_misses = []
    batch_size = 10
    for i in range(0, len(SP100), batch_size):
        batch = SP100[i:i + batch_size]
        close = high = None
        try:
            raw = yf.download(batch, period="1y", auto_adjust=False, progress=False, group_by="column")
            close = raw["Close"]
            high = raw["High"]
        except Exception as e:
            print(f"[dip-scanner/equity] batch fetch failed {batch}: {e}", file=sys.stderr)
        for ticker in batch:
            cs = hs = None
            try:
                if close is not None and ticker in getattr(close, "columns", []):
                    cs = close[ticker].dropna()
                    hs = high[ticker].dropna()
                if cs is None or hs is None or cs.empty or hs.empty:
                    print(f"[dip-scanner/equity] {ticker}: empty in batch, retrying...", file=sys.stderr)
                    time.sleep(1)
                    cs, hs = _fetch_single(ticker)
                if cs is None or hs is None or cs.empty or hs.empty:
                    print(f"[dip-scanner/equity] FETCH-MISS {ticker}", file=sys.stderr)
                    fetch_misses.append(ticker)
                    continue
                hit = _evaluate_equity(ticker, cs, hs, threshold_pct)
                if hit is not None:
                    results.append(hit)
            except Exception as e:
                print(f"[dip-scanner/equity] {ticker} error: {e}", file=sys.stderr)
                fetch_misses.append(ticker)
        time.sleep(1)
    results.sort(key=lambda x: x["pct_from_high"])
    return results, fetch_misses


# === CRYPTO SCANNING ===


def scan_crypto(threshold_pct: float = 20.0) -> tuple[list[dict], dict | None, dict | None]:
    """Scan crypto universe for dips. Returns (hits, fear_greed_data, funding_data)."""
    tickers = list(CRYPTO.values())
    try:
        raw = yf.download(tickers, period="1y", auto_adjust=False, progress=False, group_by="column")
        close = raw["Close"]
        high = raw["High"]
    except Exception as e:
        print(f"[dip-scanner/crypto] fetch failed: {e}", file=sys.stderr)
        return [], fear_greed(), btc_funding_rate()

    hits = []
    for name, yf_sym in CRYPTO.items():
        try:
            if yf_sym not in close.columns:
                print(f"[dip-scanner/crypto] no data for {name}", file=sys.stderr)
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
            print(f"[dip-scanner/crypto] {name} error: {e}", file=sys.stderr)
    hits.sort(key=lambda x: x["pct_from_high"])
    return hits, fear_greed(), btc_funding_rate()


# === PRICE-GROUND MODE ===


def ground_tickers(tickers: list[str]) -> tuple[list[dict], list[str]]:
    """Price-ground arbitrary tickers (no dip threshold, no universe scan)."""
    grounded, misses = [], []
    for t in tickers:
        t = t.strip().upper()
        if not t:
            continue
        cs, hs = _fetch_single(t)
        row = _evaluate_equity(t, cs, hs, 0.0, ground=True)
        if row is None:
            misses.append(t)
        else:
            grounded.append(row)
    return grounded, misses


# === POOL EMITTER ===


def emit_pool(equity_hits: list[dict], crypto_hits: list[dict], path: str) -> int:
    """Append HIGH+MEDIUM dips (both universes) to the durable convergence pool."""
    today = datetime.now(timezone.utc).date().isoformat()
    rows = []
    for h in equity_hits:
        if h["conviction"] in ("HIGH", "MEDIUM"):
            rows.append({"ticker": h["ticker"],
                         "reason": f"equity dip {h['pct_from_high']}% below 52w high ({h['conviction']})",
                         "date": today, "universe": "equity"})
    for h in crypto_hits:
        if h["conviction"] in ("HIGH", "MEDIUM"):
            rows.append({"ticker": h["ticker"],
                         "reason": f"crypto dip {h['pct_from_high']}% below 52w high ({h['conviction']})",
                         "date": today, "universe": "crypto"})
    if not rows:
        return 0
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return len(rows)


# === DISPLAY ===


def print_equity(hits: list[dict], fetch_misses: list[str], threshold: float):
    """Print equity scan results in human-readable format."""
    print(f"\n=== EQUITY DIP SCANNER — S&P 100 >= {threshold:.0f}% below 52w high ===\n")
    if fetch_misses:
        print(f"  [FETCH-MISS] {len(fetch_misses)} ticker(s): {', '.join(fetch_misses)}")
    if not hits:
        print(f"  No S&P 100 stocks >= {threshold:.0f}% below 52w high today.")
        return
    for r in hits:
        label = {"HIGH": "[HIGH]", "MEDIUM": "[MED]", "WATCH": "[WATCH]"}[r["conviction"]]
        if r["sma200"] is not None:
            trend = "above" if r["pct_vs_200d"] >= 0 else "below"
            ma = f"200dMA ${r['sma200']:.2f} ({r['pct_vs_200d']:+.1f}% {trend})"
        else:
            ma = "200dMA n/a"
        print(f"  {label} {r['ticker']:6s}  {r['pct_from_high']:+.1f}% from 52w high "
              f"(${r['high_52w']:.2f})  now ${r['current']:.2f}  {ma}  as-of {r['as_of']}")
    print(f"\n  {len(hits)} candidate(s).")


def print_crypto(hits: list[dict], fg, fr, regime, threshold: float):
    """Print crypto scan results in human-readable format."""
    print(f"\n=== CRYPTO DIP SCANNER — >= {threshold:.0f}% below 52w high ===\n")
    if fg:
        zone = "BUY ZONE" if fg["value"] <= 25 else "GREED ZONE" if fg["value"] >= 75 else "NEUTRAL"
        print(f"  Fear & Greed: {fg['value']}/100 ({fg['label']})  [{zone}]")
    else:
        print("  Fear & Greed: [UNAVAILABLE]")
    if fr is not None:
        rate = fr["rate_pct"]
        note = "shorts dominant" if rate < -0.01 else "overleveraged longs" if rate > 0.05 else "neutral"
        print(f"  BTC Funding:  {rate:+.4f}%  [{note}]  ({fr['venue']}, {fr['interval_h']}h)")
    else:
        print("  BTC Funding:  [UNAVAILABLE]")
    if regime is not None:
        tag = "RISK_OFF — confirms stress" if regime["regime"] == "RISK_OFF" else "RISK_ON"
        print(f"  TradFi (SPY): {regime['pct_vs_200d']:+.1f}% vs 200d-MA  [{tag}]")
    else:
        print("  TradFi (SPY): [UNAVAILABLE]")
    print()
    if not hits:
        print(f"  No crypto >= {threshold:.0f}% below 52w high today.")
        return
    for r in hits:
        label = {"HIGH": "[HIGH]", "MEDIUM": "[MED]", "WATCH": "[WATCH]"}[r["conviction"]]
        if r["sma200_usd"] is not None:
            trend = "above" if r["pct_vs_200d"] >= 0 else "below"
            ma = f"200dMA ${r['sma200_usd']:,.0f} ({r['pct_vs_200d']:+.1f}% {trend})"
        else:
            ma = "200dMA n/a"
        print(f"  {label} {r['ticker']:5s}  {r['pct_from_high']:+.1f}% from 52w high "
              f"(${r['high_52w_usd']:,.0f})  now ${r['current_usd']:,.2f}  {ma}")
    print(f"\n  {len(hits)} candidate(s).")


# === MAIN ===


def main():
    ap = argparse.ArgumentParser(description="Unified dip scanner (equity + crypto)")
    ap.add_argument("--universe", choices=["equity", "crypto", "all"], default="all",
                    help="Which universe to scan (default: all)")
    ap.add_argument("--threshold", type=float, default=20.0,
                    help="Minimum %% below 52w high to report (default: 20)")
    ap.add_argument("--tickers", type=str, default=None,
                    help="Comma-separated tickers to PRICE-GROUND (no threshold, no universe scan)")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    ap.add_argument("--emit-pool", nargs="?", const=DEFAULT_POOL, default=None,
                    help="Append HIGH+MEDIUM to convergence pool")
    a = ap.parse_args()

    # Price-ground mode (bypasses universe scan)
    if a.tickers:
        grounded, misses = ground_tickers(a.tickers.split(","))
        print(json.dumps({"grounded": grounded, "fetch_misses": misses}, indent=2))
        return

    equity_hits, equity_misses = [], []
    crypto_hits, fg, fr, regime = [], None, None, None

    if a.universe in ("equity", "all"):
        equity_hits, equity_misses = scan_equity(a.threshold)

    if a.universe in ("crypto", "all"):
        crypto_hits, fg, fr = scan_crypto(a.threshold)
        regime = spy_regime()

    # Emit to convergence pool
    if a.emit_pool:
        n = emit_pool(equity_hits, crypto_hits, a.emit_pool)
        print(f"[dip-scanner] wrote {n} candidate(s) to pool {a.emit_pool}", file=sys.stderr)

    # Output
    if a.json:
        out = {}
        if a.universe in ("equity", "all"):
            out["equity"] = {"hits": equity_hits, "fetch_misses": equity_misses}
        if a.universe in ("crypto", "all"):
            out["crypto"] = {
                "dips": crypto_hits,
                "fear_greed": fg,
                "btc_funding": fr,
                "btc_funding_rate_pct": fr["rate_pct"] if fr else None,
                "tradfi_regime": regime,
            }
        print(json.dumps(out, indent=2))
        return

    # Human-readable output
    if a.universe in ("equity", "all"):
        print_equity(equity_hits, equity_misses, a.threshold)
    if a.universe in ("crypto", "all"):
        print_crypto(crypto_hits, fg, fr, regime, a.threshold)

    print("\n  Educational only — not advice.\n")


if __name__ == "__main__":
    main()
