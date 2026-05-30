#!/usr/bin/env python3
"""Generate charts for the Substack post on conservative USDT/USDC yield (May 2026).

Data: DefiLlama free yields API chart endpoint, pulled live 2026-05-30 to blog/img/series_*.json.
Run: /Users/engineer/.venv/bin/python3 blog/make_charts.py
"""
import json
import os
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

IMG = os.path.join(os.path.dirname(__file__), "img")

# ---- house style -----------------------------------------------------------
plt.rcParams.update({
    "figure.dpi": 130,
    "font.size": 11,
    "font.family": "sans-serif",
    "axes.edgecolor": "#cccccc",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.color": "#eaeaea",
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
})
INK = "#1a1a1a"
CLEAN = "#1f8a4c"     # green = blue-chip / clean
MAPLE = "#0f6fd1"     # blue = Maple (the recommendation)
RISK = "#d4341f"      # red = risky strategy layer
AMBER = "#e8a020"     # amber = collateral ok / yield not


def load(name):
    with open(os.path.join(IMG, f"series_{name}.json")) as f:
        d = json.load(f)
    xs = [datetime.fromisoformat(p["t"].replace("Z", "+00:00")) for p in d["series"]]
    ys = [p["apy"] for p in d["series"]]
    return xs, ys


def pct(y, _):
    return f"{y:.0f}%"


# ===========================================================================
# Chart 1 — The yield ladder: clean frontier vs the risk you pay for >5%
# ===========================================================================
def chart_ladder():
    rows = [
        ("Aave / RWA T-bills",        3.4, CLEAN, "T-bills"),
        ("Morpho steakUSDC (Base)",   4.59, CLEAN, "WBTC / cbBTC / ETH"),
        ("Maple Syrup USDT",          4.13, MAPLE, "Overcollateralized loans"),
        ("Maple Syrup USDC",          4.67, MAPLE, "Overcollateralized loans"),
        ("— clean frontier ends —",   None, None, None),
        ("avant savUSD (Avax)",       7.9, RISK, "Delta-neutral perp basis"),
        ("usd-ai sUSDai",             7.2, RISK, "GPU / hardware loans"),
        ("unitas sUSDu (BSC)",        9.9, RISK, "Jupiter perp-LP basis"),
        ("apyx apxUSD",              10.7, RISK, "MSTR/Strive preferred stock"),
        ("mainstreet msUSD",         12.0, RISK, "Options vol arbitrage"),
    ]
    labels = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(9.2, 6.2))
    ypos = list(range(len(rows)))[::-1]
    for y, (label, val, color, backing) in zip(ypos, rows):
        if val is None:
            ax.axhline(y, color="#bbbbbb", ls=(0, (4, 3)), lw=1)
            continue
        ax.barh(y, val, color=color, height=0.62, zorder=3)
        ax.text(val + 0.15, y, f"{val:.1f}%", va="center", ha="left",
                fontsize=10.5, fontweight="bold", color=color)
        ax.text(0.12, y - 0.34, backing, va="center", ha="left",
                fontsize=8.2, color="#666666", style="italic")
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlim(0, 13.6)
    ax.xaxis.set_major_formatter(FuncFormatter(pct))
    ax.set_xlabel("Net APY (live, 2026-05-30)")
    ax.set_title("Stablecoin yield ladder — and where 'safe' ends",
                 fontsize=14, fontweight="bold", color=INK, loc="left", pad=12)
    ax.text(0, 1.015, "Green = T-bill/BTC/ETH backing.  Blue = Maple (overcollateralized).  "
            "Red = a risky strategy bolted under a synthetic dollar.",
            transform=ax.transAxes, fontsize=8.6, color="#666666")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "01_yield_ladder.png"), bbox_inches="tight")
    plt.close(fig)
    print("wrote 01_yield_ladder.png")


# ===========================================================================
# Chart 2 — The "13% mirage": steakUSDT spike vs Maple's flat line (90d)
# ===========================================================================
def chart_mirage():
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    for name, color, label, lw in [
        ("steakUSDT", AMBER, "Morpho steakUSDT  (gold/BTC/ETH collateral)", 1.8),
        ("maple_usdt", MAPLE, "Maple Syrup USDT", 2.4),
        ("maple_usdc", CLEAN, "Maple Syrup USDC", 2.4),
    ]:
        xs, ys = load(name)
        ax.plot(xs, ys, color=color, lw=lw, label=label, zorder=3)
    # annotate the spike
    xs, ys = load("steakUSDT")
    mx = max(range(len(ys)), key=lambda i: ys[i])
    ax.annotate(f"momentary spike\n{ys[mx]:.1f}% (1 day)",
                xy=(xs[mx], ys[mx]), xytext=(xs[mx], ys[mx] + 1.4),
                fontsize=8.5, color=AMBER, ha="center", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.2))
    ax.text(xs[len(xs)//6], 2.0, "steakUSDT sits ~2.5–3% most days\n(30-day mean 2.97%)",
            fontsize=8.5, color="#8a6a10", style="italic")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.set_ylim(0, 8)
    ax.set_title("The '13%' is a mirage — what you'd actually earn",
                 fontsize=14, fontweight="bold", color=INK, loc="left", pad=10)
    ax.text(0, 1.015, "Same good collateral (gold/BTC/ETH) — but the headline rate is a 1-day "
            "utilization spike. Maple's line is the one you can live on.",
            transform=ax.transAxes, fontsize=8.6, color="#666666")
    ax.legend(loc="upper left", frameon=False, fontsize=9.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "02_mirage.png"), bbox_inches="tight")
    plt.close(fig)
    print("wrote 02_mirage.png")


# ===========================================================================
# Chart 3 — Higher APY = a different risk, not a better deal (90d, all candidates)
# ===========================================================================
def chart_candidates():
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    series = [
        ("mainstreet", RISK, "mainstreet msUSD — options arb"),
        ("apyx", "#b5651d", "apyx apxUSD — MSTR/Strive prefs"),
        ("avant", "#c77d0a", "avant savUSD — perp basis"),
        ("usd_ai", "#9b3010", "usd-ai sUSDai — GPU loans"),
        ("maple_usdc", MAPLE, "Maple Syrup USDC — the clean pick"),
    ]
    for name, color, label in series:
        xs, ys = load(name)
        ax.plot(xs, ys, color=color, lw=2.0 if name == "maple_usdc" else 1.5,
                label=label, zorder=4 if name == "maple_usdc" else 3,
                alpha=1.0 if name == "maple_usdc" else 0.85)
    ax.axhspan(0, 5, color="#1f8a4c", alpha=0.06, zorder=0)
    ax.text(load("maple_usdc")[0][2], 4.6, "  'clean' zone (≤5%, blue-chip backing)",
            fontsize=8.3, color="#1f8a4c", va="top")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.set_ylim(0, 14)
    ax.set_title("Everything above Maple is a different risk, not a better Maple",
                 fontsize=13.5, fontweight="bold", color=INK, loc="left", pad=10)
    ax.text(0, 1.015, "90-day net APY. The high flat lines are administered rates on synthetic "
            "dollars — you're an unsecured lender to a trading desk.",
            transform=ax.transAxes, fontsize=8.6, color="#666666")
    ax.legend(loc="center left", frameon=False, fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "03_candidates.png"), bbox_inches="tight")
    plt.close(fig)
    print("wrote 03_candidates.png")


if __name__ == "__main__":
    chart_ladder()
    chart_mirage()
    chart_candidates()
    print("done ->", IMG)
