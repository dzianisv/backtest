# Financial Advisor Agent — Agentic Hedge-Fund + Crypto Workflows

> ⚠️ **Educational analysis only — not financial advice.** Past backtest performance does not guarantee future results. Validate with a fee-only fiduciary before deploying real capital.

A portable skill+workflow layer that turns **Claude Code, openclaw, or hermes** into a proactive financial advisor — watching markets daily and surfacing time-sensitive setups before they're missed.

The agent proposes; the human approves every order. Recommend-only, always.

---

## Install once, then just chat

One command installs every skill onto your agent. It auto-detects the host (Claude Code, openclaw, hermes, Cursor, +others), pulls all skills, and wires them in:

```bash
npx skills add dzianisv/backtest
```

That's the whole setup. **You don't run a workflow or type a slash command** — the skills route themselves from what you say. After install, just ask:

```
"Should I buy the dip on BTC today?"          → crypto-advisor
"Is HYPE a real infra token or just hype?"    → crypto-token-screener
"What did Buffett just buy?"                   → 13f-watch
"Run the weekly committee."                    → agentic-fund-orchestration
"What's the market regime right now?"          → regime-detection
```

Each skill's description is written as a routing trigger, so the right desk answers the right question with no ceremony.

### Per-runtime install

| Runtime | Command |
|---|---|
| **Claude Code** | `npx skills add dzianisv/backtest` (auto-detected) |
| **openclaw** | `npx skills add dzianisv/backtest --agent openclaw --copy` |
| **hermes** | `npx skills add dzianisv/backtest --agent hermes-agent --copy` |

`--copy` ships the Python helper scripts alongside each `SKILL.md` (needed for the data-pulling skills). For scheduled/proactive operation (daily scans + weekly committee), see [`docs/`](docs/) — `setup-claudecode.md`, `setup-openclaw.md`, `setup-hermes.md`.

> **Workflows** (the multi-agent committee in `.agents/workflows/`) don't travel through the skill installer — they're a clone-the-repo power-user artifact. The everyday committee question is answered by the `agentic-fund-orchestration` skill, which installs normally.

---

## Two active workstreams

### 1. Stocks / TradFi portfolio workflow

Manages a **~$1M tradfi book** (RSP 70 / GLD 15 / IEF 15 baseline) through an AI-bubble environment. Runs the loop: **regime-detect → scan → committee → human-approve → execute → report**.

Key artifacts:

| Artifact | Purpose |
|---|---|
| [`GOAL.md`](GOAL.md) | Mission + bubble evidence + done/not-done checklist |
| [`strategy/v3`](strategy/v3-bubble-aware-all-weather.md) | Bubble-Aware All-Weather strategy (the recommended allocation) |
| [`docs/prd.md`](docs/prd.md) | Features, cadence, personas |
| [`docs/tdd.md`](docs/tdd.md) | Architecture, wiring diagrams, data contracts |
| [`.agents/workflows/hedge-fund-committee.workflow.js`](.agents/workflows/) | Weekly committee → ranked next-buy memo |

Core skills: `regime-detection` · `trend-stock-research` · `dip-screener` · `fomc-monitor` · `prediction-market-odds` · `forecast-ledger` · `hedge-fund-manager` · `superforecasting` · `macro-panel` · `multi-lens-quorum`

**Status:** fast-tier daily scanners live on openclaw (cron + liveness); weekly committee workflow validated (3 iterations); congress stock-watch wired (`congress/`).

---

### 2. Crypto portfolio workflow

Manages a **~$177k crypto book** with a BTC-as-hurdle filter — only deploy into tokens that pass the 6-point infrastructure value-accrual test (HYPE the current benchmark).

Full spec: [`crypto/`](crypto/) — `crypto.goal.md` · `crypto.prd.md` · `crypto.tdd.md` · `crypto.loop.md`

Core skills: `crypto-chair` · `crypto-research-desk` · `crypto-dip-scanner` · `crypto-liquidity-data` · `crypto-onchain-data` · `crypto-workflow-eval` · `analyst-crypto`

**Status:** skill tree designed + specced; G-Eval harness baselined (85/100); crypto.loop.md orchestrates daily dip-scan + weekly research desk cycle.

---

## Deployment targets

Same skills install onto any of:

| Runtime | Scheduling primitive | Notification |
|---|---|---|
| **Claude Code** | `/loop` + Routines + dynamic workflows | terminal / push |
| **openclaw** | `heartbeat` + `HEARTBEAT.md` | Telegram DM |
| **hermes-ai** | hermes scheduler | configured channel |

---

## Repository layout

```
GOAL.md                    # tradfi mission north-star
crypto/                    # crypto workflow spec (goal / prd / tdd / loop)
strategy/                  # v1→v3 strategy evolution; v3 = current recommended allocation
research/                  # cited research notes (AI bubble, crypto, macro, frameworks)
backtests/                 # runnable backtest scripts + cached results
docs/                      # prd / tdd / setup guides (openclaw / claude-code / hermes)
.agents/skills/            # all skill modules (SKILL.md + implementation)
.agents/workflows/         # multi-agent workflow scripts
congress/                  # congressional stock-watch feed
report/                    # generated charts + published write-ups
```

---

## Backtest summary (tradfi v3)

1. **Don't bet the whole $1M on cap-weight S&P/QQQ at CAPE ~41.** 2000-2026 backtest: S&P −55%, QQQ −83%; 2000-2009 was a lost decade.
2. **Selection isn't the edge.** Bottom-up stock-picking doesn't reliably beat a cheap index (backtests + SPIVA).
3. **The edge is structural.** De-concentrated diversification + trend/regime overlay (crisis alpha) + dip-reserve = caps left tail without a market call. → [`strategy/v3`](strategy/v3-bubble-aware-all-weather.md)

Tracking issue: https://github.com/dvashchuk/backtest/issues/1
