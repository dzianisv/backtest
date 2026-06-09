#!/usr/bin/env python3
"""
Point-in-time data layer for the agent backtest.

Pulls per-pool daily APY/TVL history from DefiLlama (`/chart/{poolId}`) for a curated universe of
pools that EXISTED in the backtest window, and caches each to crypto/backtest/data/{label}.json.
A pool is only "available" to the agent on a date it already had history — this is what prevents
look-ahead into venues that didn't exist yet.

Run: /Users/engineer/.venv/bin/python3 crypto/backtest/fetch_history.py
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# Curated universe. Each entry resolves to the matching pool with the OLDEST history (the original
# vault, not a newer re-deploy). kind drives the simulator's asset class. stable = a USD pool.
UNIVERSE = [
    # label,                project,        symbol,     chain,      kind
    ("aave_usdc_eth",       "aave-v3",      "USDC",     "Ethereum", "stable"),
    ("aave_usdt_eth",       "aave-v3",      "USDT",     "Ethereum", "stable"),
    ("compound_usdc_eth",   "compound-v3",  "USDC",     "Ethereum", "stable"),
    ("steakusdc_eth",       "morpho-blue",  "STEAKUSDC","Ethereum", "stable"),
    ("steakusdc_base",      "morpho-blue",  "STEAKUSDC","Base",     "stable"),
    ("sdai_eth",            "spark",        "SDAI",     "Ethereum", "stable"),
    ("susds_eth",           "sky-lending",  "SUSDS",    "Ethereum", "stable"),
    ("steth",               "lido",         "STETH",    "Ethereum", "eth"),
    # directional/yield-trap probes (to test that the agent AVOIDS them):
    ("susde",               "ethena-usde",  "SUSDE",    "Ethereum", "synthetic"),
    ("curve_crvusd_usdc",   "curve-dex",    "CRVUSD-USDC","Ethereum","stable_lp"),
]


def _get(url, timeout=40):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode())


def resolve_oldest(pools_by_key, project, symbol, chain):
    """Among pools matching (project,symbol,chain), return the poolId with the earliest history."""
    cands = [p for p in pools_by_key
             if p["project"] == project and p["symbol"] == symbol and p["chain"] == chain]
    best, best_first, best_series = None, None, None
    for p in cands:
        try:
            series = _get(f"https://yields.llama.fi/chart/{p['pool']}").get("data", [])
        except Exception:
            continue
        if not series:
            continue
        first = series[0]["timestamp"][:10]
        if best_first is None or first < best_first:
            best, best_first, best_series = p["pool"], first, series
    return best, best_series


def main():
    os.makedirs(DATA, exist_ok=True)
    print("Fetching pool list…", file=sys.stderr)
    pools = _get("https://yields.llama.fi/pools")["data"]
    print(f"{'label':22} {'pool':10} {'kind':10} {'pts':>5} {'first':12} {'last':12}")
    coverage = []
    for label, project, symbol, chain, kind in UNIVERSE:
        pid, series = resolve_oldest(pools, project, symbol, chain)
        if not series:
            print(f"{label:22} {'—':10} {kind:10} {'0':>5}  NOT FOUND ({project}/{symbol}/{chain})")
            continue
        rows = [{"date": d["timestamp"][:10], "apy": d.get("apy"), "tvl": d.get("tvlUsd")}
                for d in series]
        out = {"label": label, "pool": pid, "kind": kind,
               "project": project, "symbol": symbol, "chain": chain, "series": rows}
        with open(os.path.join(DATA, f"{label}.json"), "w") as f:
            json.dump(out, f)
        first, last = rows[0]["date"], rows[-1]["date"]
        coverage.append((label, first, last))
        print(f"{label:22} {pid[:8]:10} {kind:10} {len(rows):>5} {first:12} {last:12}")

    if coverage:
        common_start = max(c[1] for c in coverage)
        common_end = min(c[2] for c in coverage)
        full_2024 = [c[0] for c in coverage if c[1] <= "2024-07-01"]
        print(f"\nCommon window (all pools overlap): {common_start} → {common_end}")
        print(f"Pools with ≥2024-07 history (usable for a 2-yr backtest): {len(full_2024)} → {full_2024}")
        print(f"\nCached → {DATA}/")


if __name__ == "__main__":
    main()
