#!/usr/bin/env python3
"""
portfolio-memory — BM25 × recency-decay cross-run memory for portfolio manager agents.

SQLite FTS5 stdlib only. No embeddings, no numpy, no external APIs.
Architecture mirrors crypto-news-store/news_store.py.

CLI:
  python3 memory.py recall   --q "COIN" [--desk stocks] [--k 8] [--db path]
  python3 memory.py remember --desk stocks --ticker COIN --verdict HOLD --body "..." [--meta '{}'] [--run-id 2026-06-24]
  python3 memory.py pref-add --text "crypto bullish" [--desk crypto] [--scope "COIN,HOOD"]
  python3 memory.py pref-list [--desk crypto]
  python3 memory.py stats

All output is JSON.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
_SCHEMA = """
CREATE TABLE IF NOT EXISTS memory (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  kind        TEXT NOT NULL DEFAULT 'verdict',
  desk        TEXT NOT NULL,
  ticker      TEXT,
  verdict     TEXT,
  body        TEXT NOT NULL,
  meta        TEXT,
  run_id      TEXT,
  created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mem_ticker ON memory(ticker);
CREATE INDEX IF NOT EXISTS idx_mem_desk   ON memory(desk);
CREATE INDEX IF NOT EXISTS idx_mem_run    ON memory(run_id);

CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts
  USING fts5(ticker, body, content='memory', content_rowid='id',
             tokenize='porter unicode61');

CREATE TRIGGER IF NOT EXISTS mem_ai AFTER INSERT ON memory BEGIN
  INSERT INTO memory_fts(rowid, ticker, body)
  VALUES (new.id, COALESCE(new.ticker,''), new.body);
END;

CREATE TABLE IF NOT EXISTS preferences (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  desk        TEXT,
  scope       TEXT,
  text        TEXT NOT NULL UNIQUE,
  created_at  TEXT NOT NULL
);
"""

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def connect(db_path: str = ".db/portfolio_memory.db") -> sqlite3.Connection:
    if db_path != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.executescript(_SCHEMA)
    return con

# ---------------------------------------------------------------------------
# Recency decay — registered as a SQLite function
# ---------------------------------------------------------------------------

def _register_decay(con: sqlite3.Connection, half_life_days: float = 45.0) -> None:
    now = datetime.now(timezone.utc).timestamp()

    def decay(iso: str | None) -> float:
        if not iso:
            return 0.5
        try:
            t = datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0.5
        age_days = max(0.0, (now - t) / 86400.0)
        return 0.5 ** (age_days / half_life_days)

    con.create_function("decay", 1, decay)

# ---------------------------------------------------------------------------
# FTS query sanitiser — mirrors news_store.normalize_text
# ---------------------------------------------------------------------------

def _fts_query(q: str) -> str:
    """Sanitise a free-text query into a safe FTS5 MATCH expression."""
    tokens = re.findall(r"[a-z0-9$]+", q.lower())
    if not tokens:
        return '""'
    # Wrap each token in double-quotes so FTS5 treats them as phrases, not operators.
    return " OR ".join(f'"{t}"' for t in tokens)

# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def remember_verdict(
    con: sqlite3.Connection,
    desk: str,
    ticker: str,
    verdict: str,
    body: str,
    meta: dict | None = None,
    run_id: str | None = None,
) -> int:
    """Append one ticker verdict to the memory store. Returns the new row id."""
    now = datetime.now(timezone.utc).isoformat()
    cur = con.execute(
        "INSERT INTO memory(kind, desk, ticker, verdict, body, meta, run_id, created_at)"
        " VALUES('verdict', ?, ?, ?, ?, ?, ?, ?)",
        (
            desk,
            ticker.upper().strip(),
            verdict.upper().strip(),
            body,
            json.dumps(meta or {}),
            run_id or datetime.now(timezone.utc).date().isoformat(),
            now,
        ),
    )
    con.commit()
    return cur.lastrowid


def remember_preference(
    con: sqlite3.Connection,
    text: str,
    desk: str | None = None,
    scope: str | None = None,
) -> None:
    """Upsert a durable user preference (always injected, never BM25-gated)."""
    now = datetime.now(timezone.utc).isoformat()
    con.execute(
        "INSERT INTO preferences(desk, scope, text, created_at) VALUES(?,?,?,?)"
        " ON CONFLICT(text) DO UPDATE SET desk=excluded.desk, scope=excluded.scope, created_at=excluded.created_at",
        (desk, scope, text.strip(), now),
    )
    con.commit()

# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def recall(
    con: sqlite3.Connection,
    query: str,
    desk: str | None = None,
    k: int = 8,
    half_life_days: float = 45.0,
) -> list[dict]:
    """Return up to k prior verdicts ranked by BM25 × recency decay.

    FTS5 bm25() returns negative scores (more negative = more relevant).
    We flip the sign (-bm25) and multiply by decay so the combined score is
    positive and higher-is-better.
    Ticker column is weighted 10× body so ticker symbol queries dominate.
    """
    _register_decay(con, half_life_days)
    fts = _fts_query(query)
    desk_clause = " AND m.desk = ?" if desk else ""
    sql = (
        "SELECT m.id, m.kind, m.desk, m.ticker, m.verdict, m.body, m.meta,"
        "       m.run_id, m.created_at,"
        "       -bm25(memory_fts, 10.0, 1.0)                       AS relevance,"
        "       -bm25(memory_fts, 10.0, 1.0) * decay(m.created_at) AS final"
        " FROM memory_fts f"
        " JOIN memory m ON m.id = f.rowid"
        " WHERE memory_fts MATCH ?" + desk_clause +
        " ORDER BY final DESC"
        " LIMIT ?"
    )
    args: list = [fts] + ([desk] if desk else []) + [k]
    try:
        rows = con.execute(sql, args).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.OperationalError:
        # Malformed MATCH — degrade gracefully (empty recall)
        return []


def load_preferences(
    con: sqlite3.Connection, desk: str | None = None
) -> list[dict]:
    """Load all durable preferences. Always inject these — never BM25-gate them."""
    rows = con.execute(
        "SELECT text, scope, desk, created_at FROM preferences"
        " WHERE desk IS NULL OR desk = ?"
        " ORDER BY created_at DESC",
        (desk,),
    ).fetchall()
    return [dict(r) for r in rows]

# ---------------------------------------------------------------------------
# Format for prompt injection
# ---------------------------------------------------------------------------

def format_context(
    prefs: list[dict],
    memories: list[dict],
    max_body_chars: int = 200,
) -> str:
    """Format recalled memories + preferences into a compact context block."""
    lines: list[str] = []

    if prefs:
        lines.append("DURABLE PREFERENCES (always apply):")
        for p in prefs:
            scope = f" (applies to: {p['scope']})" if p.get("scope") else ""
            lines.append(f"  - {p['text']}{scope}")
        lines.append("")

    if memories:
        lines.append("PRIOR VERDICTS (BM25-recalled, recency-weighted):")
        for m in memories:
            run = m.get("run_id") or m.get("created_at", "")[:10]
            ticker = m.get("ticker") or "—"
            verdict = m.get("verdict") or "?"
            body = (m.get("body") or "")[:max_body_chars]
            if len(m.get("body", "")) > max_body_chars:
                body += "…"
            lines.append(f"  [{run}] {ticker} {verdict} — {body}")
    else:
        lines.append("PRIOR VERDICTS: none found for this query.")

    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Last-run report — the primary memory anchor
# ---------------------------------------------------------------------------

def last_run(
    con: sqlite3.Connection,
    desk: str | None = None,
) -> tuple[str | None, list[dict]]:
    """Return (run_id, verdicts) for the most recent completed run.

    This is the primary memory surface for portfolio agents: show yesterday's
    full signal table at the start of every new run so the agent knows where
    things stood — without selective filtering or BM25 framing.
    """
    row = con.execute(
        "SELECT run_id FROM memory"
        + (" WHERE desk = ?" if desk else "")
        + " ORDER BY created_at DESC LIMIT 1",
        ((desk,) if desk else ()),
    ).fetchone()
    if not row:
        return None, []
    run_id = row["run_id"]
    verdicts = [
        dict(r)
        for r in con.execute(
            "SELECT ticker, verdict, meta, body, created_at FROM memory"
            " WHERE run_id = ?" + (" AND desk = ?" if desk else "") +
            " ORDER BY ticker",
            ((run_id, desk) if desk else (run_id,)),
        ).fetchall()
    ]
    return run_id, verdicts


def format_last_run(
    run_id: str | None,
    verdicts: list[dict],
    prefs: list[dict],
) -> str:
    """Format the previous run into a compact signal-table block for the agent."""
    if not run_id:
        return "PREVIOUS RUN: none — first run."

    lines = [f"PREVIOUS RUN: {run_id}"]
    lines.append("═" * 60)

    if verdicts:
        lines.append(f"{'TICKER':<8} {'VERDICT':<7} {'CONV':<5}  NOTES")
        lines.append("─" * 60)
        for v in verdicts:
            ticker  = (v.get("ticker") or "—")[:8]
            verdict = (v.get("verdict") or "?")[:7]
            try:
                meta = json.loads(v.get("meta") or "{}")
            except Exception:
                meta = {}
            conv  = f"{meta.get('conviction', '?')}/5"
            theme = meta.get("theme", "")
            # Pull first 60 chars of body as the note
            note  = (v.get("body") or "")[:60].split("—", 1)[-1].strip()
            lines.append(f"{ticker:<8} {verdict:<7} {conv:<5}  {note}  [{theme}]")
    else:
        lines.append("  (no verdicts recorded for this run)")

    lines.append("═" * 60)

    if prefs:
        pref_texts = " | ".join(p["text"][:50] for p in prefs)
        lines.append(f"Prefs: {pref_texts}")

    lines.append(
        "\nUse this as a baseline — do fresh analysis, note what changed vs prior run."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def stats(con: sqlite3.Connection) -> dict:
    rows = con.execute(
        "SELECT desk, kind, COUNT(*) AS n FROM memory GROUP BY desk, kind ORDER BY desk, kind"
    ).fetchall()
    pref_count = con.execute("SELECT COUNT(*) FROM preferences").fetchone()[0]
    return {
        "verdicts": [dict(r) for r in rows],
        "preferences": pref_count,
    }

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    parser = argparse.ArgumentParser(prog="memory.py")
    parser.add_argument("--db", default=".db/portfolio_memory.db")
    sub = parser.add_subparsers(dest="cmd")

    r = sub.add_parser("recall")
    r.add_argument("--q", required=True)
    r.add_argument("--desk")
    r.add_argument("--k", type=int, default=8)
    r.add_argument("--half-life", type=float, default=45.0)

    w = sub.add_parser("remember")
    w.add_argument("--desk", required=True)
    w.add_argument("--ticker", required=True)
    w.add_argument("--verdict", required=True)
    w.add_argument("--body", required=True)
    w.add_argument("--meta", default="{}")
    w.add_argument("--run-id")

    pa = sub.add_parser("pref-add")
    pa.add_argument("--text", required=True)
    pa.add_argument("--desk")
    pa.add_argument("--scope")

    pl = sub.add_parser("pref-list")
    pl.add_argument("--desk")

    lr = sub.add_parser("last-run")
    lr.add_argument("--desk")

    sub.add_parser("stats")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    con = connect(args.db)

    if args.cmd == "recall":
        rows = recall(con, args.q, desk=args.desk, k=args.k, half_life_days=args.half_life)
        prefs = load_preferences(con, desk=args.desk)
        print(format_context(prefs, rows))

    elif args.cmd == "remember":
        row_id = remember_verdict(
            con, args.desk, args.ticker, args.verdict, args.body,
            meta=json.loads(args.meta), run_id=args.run_id,
        )
        print(json.dumps({"ok": True, "id": row_id}))

    elif args.cmd == "pref-add":
        remember_preference(con, args.text, desk=args.desk, scope=args.scope)
        print(json.dumps({"ok": True}))

    elif args.cmd == "pref-list":
        print(json.dumps(load_preferences(con, desk=args.desk), indent=2))

    elif args.cmd == "last-run":
        run_id, verdicts = last_run(con, desk=args.desk)
        prefs = load_preferences(con, desk=args.desk)
        print(format_last_run(run_id, verdicts, prefs))

    elif args.cmd == "stats":
        print(json.dumps(stats(con), indent=2))


if __name__ == "__main__":
    _cli()
