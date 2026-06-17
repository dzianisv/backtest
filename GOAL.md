# GOAL — Proactive Investment Advisor

AI skills + workflows that turn any AI agent (Claude Code, OpenClaw, Hermes) into a **proactive,
notification-first investment advisor** behind a hard backtest-before-trade gate.

> Educational analysis only — not financial advice. Human approves every action.

## Mission

The owner manages a $1M tradfi book + a ~$177k crypto book and has no time to research. Reach a state
where the owner never again misses a time-sensitive setup like:
- **Google (GOOGL), Spring 2025** — quality stock −30% from 52w high.
- **SanDisk (WDC), Sept 2025** — AI-supply-chain narrative built over weeks in FT/WSJ.
- **BTC, April 2025** — $61k, −43% from ATH, Fear&Greed sub-20, funding negative.

Each was obvious in hindsight, time-boxed (days), and missed because nobody was watching.
The advisor surfaces them **same-day, with a defended verdict**, before the window closes.

## What it does

- Watches markets daily — dips, regime shifts, Fed moves, congressional trades, 13F filings, news narratives.
- Sends a DM the same day a real setup appears (silent otherwise — no noise).
- Runs a weekly investment brief: signals → quorum verdict → risk veto → ranked buy/sell ideas.
- **Recommend-only.** No trades placed without your sign-off. Hard caps live in deterministic code.

## Two books (separate ledgers — never conflate)

| Book | Size | Strategy | Goal |
|------|------|----------|------|
| **Tradfi** | ~$1M | Bubble-Aware All-Weather (v3): RSP 70% / GLD 15% / IEF 15% | S&P-like return, less AI-bubble concentration. Backtested: −42% max DD vs S&P −55%. |
| **Crypto** | ~$177k | Yield-first conservative: maximize sustainable net yield on stable sleeve | Capital preservation first; no idle cash sits at 0%. See `crypto/GOAL.md`. |

## Installed (~60 skills + 1 workflow)

**Signals** — regime-detection, fomc-monitor, dip-screener, crypto-dip-scanner, trend-stock-research, signal-convergence-alert, 13f-watch, congressman-stock-watch, feed-{bloomberg,ft,wsj,coindesk,…}

**Analysis** — macro-panel (7 thinker lenses), multi-lens-quorum (buy/sell/hold verdict), superforecasting, fundamental-analysis, analyst-{technical,systematic,crypto,derivatives}

**Portfolio** — portfolio-monitor, risk-management, hedge-fund-manager, tradfi-portfolio-manager, defi-portfolio-manager, forecast-ledger

**Workflow** — `hedge-fund-committee` (weekly parallel fan-out: news → price-ground → quorum → CIO brief → staged buy plan)

## Three backends, same portable skills

Design rule: **lean on each platform's native primitives — don't reinvent scheduling or state.**

| Backend | Install | Scheduling | State | Notification |
|---------|---------|-----------|-------|--------------|
| **Claude Code** | `npx -y skills add dzianisv/financial-advisor-agents` | cron → `claude -p` + dynamic workflows | auto-memory + dedup ledgers | terminal / push |
| **OpenClaw** | `npx --yes skills add dzianisv/financial-advisor-agents --agent openclaw --yes --copy --dangerously-accept-openclaw-risks` | agent-native CRON (heartbeat = backup) | memory + workspace files | Telegram DM |
| **Hermes** | `npx -y skills add dzianisv/financial-advisor-agents --agent hermes-agent` | hermes scheduler | preloaded skill sessions | configured channel |

Setup prompts: `docs/InstallPrompt.md`. Per-backend wiring: `docs/setup-{openclaw,claudecode,hermes}.md`.

## Hard rules (invariants — an action breaking one is rejected)

1. **Backtest before trade.** `strategy-discovery-backtest` runs first; only PASS + human approval trades.
2. **Human in the loop.** Agent proposes; human approves. Notification-first until paper-validated.
3. **No fabricated data.** Source down → `[UNAVAILABLE]`, never an invented price.
4. **Risk management has veto.** RISK_OFF regime → no new buy alerts (logged to watchlist only).
5. **Two books are separate.** Never conflate tradfi and crypto accounting.
6. **Hard caps in code, outside the LLM.** Size, drawdown, per-trade/day loss, leverage.

## Scope

**IN:** daily dip scans (stock + crypto), regime/Fed monitoring, journalism narrative accumulation,
signal convergence, weekly brief, proactive scheduling on 3 backends, recommend-only DMs.

**OUT:** auto-trading (recommend-only; execution tracks D/E in AGENTS.md), paid data feeds,
intraday day-trading (gated by backtest skill, separate workstream).

## Done (advisor sub-project — all [x] or deferred)

- [x] dip-screener, crypto-dip-scanner, signal-convergence-alert — built + evaluated on live data.
- [x] 3-backend proactive setup documented (heartbeat / cron / hermes scheduler).
- [x] Skills deployed + validated on LIVE openclaw (2026-06-14): python3.12+yfinance in agent bash; live DM fired.
- [x] Agent-native CRON owns the schedule (3 dip jobs + regime 08:00, journalism 08:15, weekly brief Mon).
- [x] forecast-ledger wired: each DM'd call logged; 30/60/90d hit-rate scored in weekly brief.
- [x] claude-code backend validated: skills load as `/commands`, run clean on live data.
- [~] hermes backend: DEFERRED — no instance available. Setup documented; same skills apply when ready.
