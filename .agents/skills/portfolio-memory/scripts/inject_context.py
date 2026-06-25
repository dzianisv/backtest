#!/usr/bin/env python3
"""
inject_context.py — pull prior memory for a list of tickers and print a
formatted <prior_context> block ready to paste into a seat prompt.

Usage (from repo root):
  python3 .agents/skills/portfolio-memory/scripts/inject_context.py \
    --db .db/portfolio_memory.db --desk stocks --tickers COIN PYPL AVGO MRVL

Output: a plain-text <prior_context>…</prior_context> block printed to stdout.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from memory import connect, format_context, load_preferences, recall


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=".db/portfolio_memory.db")
    p.add_argument("--desk", default=None)
    p.add_argument("--tickers", nargs="+", required=True)
    p.add_argument("--k-per-ticker", type=int, default=3)
    p.add_argument("--half-life", type=float, default=45.0)
    args = p.parse_args()

    con = connect(args.db)
    prefs = load_preferences(con, desk=args.desk)

    all_memories: list[dict] = []
    seen_ids: set[int] = set()
    for ticker in args.tickers:
        rows = recall(con, ticker, desk=args.desk, k=args.k_per_ticker,
                      half_life_days=args.half_life)
        for row in rows:
            if row["id"] not in seen_ids:
                seen_ids.add(row["id"])
                all_memories.append(row)

    block = format_context(prefs, all_memories)
    print("<prior_context>")
    print(block)
    print("</prior_context>")


if __name__ == "__main__":
    main()
