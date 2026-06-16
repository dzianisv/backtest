# Financial Advisor Agent — Agentic Hedge-Fund + Crypto Workflows

> ⚠️ **Educational analysis only — not financial advice.** Past backtest performance does not guarantee future results. Validate with a fee-only fiduciary before deploying real capital.

A portable skill+workflow layer that turns **Claude Code, openclaw, or hermes** into a proactive financial advisor — watching markets daily and surfacing time-sensitive setups before they're missed.

The agent proposes; the human approves every order. Recommend-only, always.

---

## Installation

### Prerequisites

- **Python 3** with `yfinance` — used by the data-pulling `.py` scripts bundled in `.agents/skills/` (e.g. `dip_screener.py`, `crypto_dip_scanner.py`, `ledger.py`). Install once: `pip install yfinance`.
- **Claude Code ≥ v2.1.154** with Dynamic Workflows enabled (`/config`) — required to run `/hedge-fund-committee`, `/research-market`, and the other slash-command workflows.

### Skills

Skills live in `.agents/skills/`. A `.claude/skills` symlink already points there, making every skill in that directory available to Claude Code when you open the repo:

```
.claude/skills -> ../.agents/skills   # already present in the repo
```

To install skills onto another runtime (openclaw, hermes, Cursor):

| Runtime | Command |
|---|---|
| **Claude Code** | `npx skills add dzianisv/financial-advisor-agents` (auto-detected) |
| **openclaw** | `npx skills add dzianisv/financial-advisor-agents --agent openclaw --copy` |
| **hermes** | `npx skills add dzianisv/financial-advisor-agents --agent hermes-agent --copy` |

`--copy` ships the bundled Python scripts alongside each `SKILL.md` (needed for data-pulling skills). Without `--copy`, skills install but the `.py` helpers that pull live prices are absent.

### Workflows (Claude Code only)

Workflow scripts live in `.agents/workflows/` and `crypto/workflows/`. Symlinks in `.claude/workflows/` register them as slash commands — present in this repo:

```
.claude/workflows/hedge-fund-committee.js   -> ../../.agents/workflows/hedge-fund-committee.workflow.js
.claude/workflows/research-market.js        -> ../../crypto/workflows/research-market.js
.claude/workflows/pairwise-eval.js          -> ../../crypto/workflows/pairwise-eval.js
.claude/workflows/multi-lens-quorum.js      # direct workflow (not a symlink)
.claude/workflows/trend-stock-research.js   # direct workflow (not a symlink)
```

To use them from another project, copy to `~/.claude/workflows/`:

```bash
cp financial-advisor-agents/.claude/workflows/*.js ~/.claude/workflows/
```

> On macOS/Linux the symlinks resolve automatically. On Windows, copy the real files from `.agents/workflows/` and `crypto/workflows/` instead.

---

## Quick Start

### Plain-language (always works)

```
"research whether I should buy ETH, I hold 20% SOL"
"should I trim NVDA — I'm 40% in it"
```

Claude routes to the right workflow and passes your portfolio as args.

### Slash commands

With the repo open in Claude Code, the workflows are available as:

```
/hedge-fund-committee    ← weekly equity committee → staged buy brief
/research-market         ← ad-hoc crypto or equity research question
/pairwise-eval           ← blind A/B comparison of two research reports
/multi-lens-quorum       ← convene N independent analyst lenses on a judgment call
/trend-stock-research    ← research-first trend-stock screen → nominees for quorum
```

### Explicit Workflow tool form

Use this when you want to pass specific args (ticker, date, portfolio):

**Ad-hoc research — crypto** (`research-market`):

```js
Workflow({
  scriptPath: "/path/to/financial-advisor-agents/crypto/workflows/research-market.js",
  args: {
    question:  "BTC reached 65k from the drop to 61k. I hold 30% in COIN. Should I buy BTC today?",
    portfolio: "~30% of book in COIN (levered crypto-beta proxy); no direct BTC.",
    date:      "2026-06-16",   // required — Date.now() is unavailable in the workflow runtime
    anchor:    ""              // optional seed price; leave "" to let Gather fetch live
  }
})
```

**Ad-hoc research — equity / mixed** (`research-market`):

```js
Workflow({
  scriptPath: "/path/to/financial-advisor-agents/crypto/workflows/research-market.js",
  args: {
    question:  "NVDA pulled back 15% from ATH. I'm 40% concentrated in it. Should I trim?",
    portfolio: "40% NVDA, remainder unspecified. $1M tradfi book, no leverage.",
    date:      "2026-06-16"
    // assets + tickers are extracted from `question` by the manager LLM — no separate ticker arg needed
  }
})
```

**Weekly equity committee** (`hedge-fund-committee`):

```js
Workflow({
  scriptPath: "/path/to/financial-advisor-agents/.agents/workflows/hedge-fund-committee.workflow.js",
  args: { date: "2026-06-16" }  // no ticker needed — open-universe discovery
})
// Output: reports/hedge-fund-brief-<date>.md (30-sec read) + reports/hedge-fund-committee-<date>.md (full memo)
```

**Blind A/B comparison of two research reports** (`pairwise-eval`):

```js
Workflow({
  scriptPath: "/path/to/financial-advisor-agents/crypto/workflows/pairwise-eval.js",
  args: {
    a:        "/path/to/iter1.report.md",   // hypothesis: worse (baseline)
    b:        "/path/to/iter2.report.md",   // hypothesis: better (candidate)
    question: "BTC reached 65k from 61k. I hold 30% in COIN. Should I buy today?",
    judges:   5                             // number of blind judges; default 5
  }
})
```

### Output

Each research workflow writes:

- `research/research.crypto.<date>.md` or `research/research.stock.<date>.md` — the full report.
- A dated row in the `forecast-ledger` (`ledger.py`) — tracked for Brier-score grading.

### Deeper docs

| Doc | Purpose |
|---|---|
| `crypto/crypto.goal.md` | Crypto book mission + constraints |
| `crypto/crypto.prd.md` | Feature spec for the crypto workflow |
| `crypto/crypto.tdd.md` | Architecture + wiring diagrams |
| `crypto/eval/IMPROVE-LOOP.md` | How to improve a workflow with pairwise-eval |

---

## Install once, then just chat

One command installs every skill onto your agent. It auto-detects the host (Claude Code, openclaw, hermes, Cursor, +others), pulls all skills, and wires them in:

```bash
npx skills add dzianisv/financial-advisor-agents
```

That's the whole setup. **You don't run a workflow or type a slash command** — the skills route themselves from what you say. After install, just ask:

```
"Should I buy the dip on BTC today?"          → crypto-dip-scanner / analyst-crypto
"What did Buffett just buy?"                   → 13f-watch
"Run the weekly committee."                    → agentic-fund-orchestration
"What's the market regime right now?"          → regime-detection
"What would Lyn Alden think of this?"          → analytics-lyn-alden
"Is there a multi-source convergence signal?"  → signal-convergence-alert
```

Each skill's description is written as a routing trigger, so the right desk answers the right question with no ceremony.

### Per-runtime install

| Runtime | Command |
|---|---|
| **Claude Code** | `npx skills add dzianisv/financial-advisor-agents` (auto-detected) |
| **openclaw** | `npx skills add dzianisv/financial-advisor-agents --agent openclaw --copy` |
| **hermes** | `npx skills add dzianisv/financial-advisor-agents --agent hermes-agent --copy` |

`--copy` ships the Python helper scripts alongside each `SKILL.md` (needed for the data-pulling skills). For scheduled/proactive operation (daily scans + weekly committee), see [`docs/`](docs/) — `setup-claudecode.md`, `setup-openclaw.md`, `setup-hermes.md`.

### The multi-agent workflows (Claude Code only)

`npx skills add` installs **skills**, not the dynamic [Workflow](https://code.claude.com/docs/en/workflows) scripts (the committee / panel orchestrators). Those are a Claude-Code-native feature — they live in `.claude/workflows/` and Claude Code exposes any `.js` there as a `/<name>` command. Two ways to get them:

```bash
# Option A — clone the repo, open Claude Code in it; the workflows are project /commands
git clone https://github.com/dzianisv/financial-advisor-agents && cd financial-advisor-agents
#   → /hedge-fund-committee   /research-market   /pairwise-eval   /multi-lens-quorum   /trend-stock-research

# Option B — make them global (available in every project)
cp financial-advisor-agents/.claude/workflows/*.js ~/.claude/workflows/
```

Then run e.g. `/hedge-fund-committee` or `/research-market`. (Needs Claude Code ≥ v2.1.154 with Dynamic workflows enabled in `/config`. Workflows are a Claude Code feature — openclaw/hermes use the skills, which orchestrate via their own primitives.)

> Note: some `.claude/workflows/*.js` entries are symlinks to `.agents/workflows/` and `crypto/workflows/` (they resolve on macOS/Linux; on Windows copy the real files). `multi-lens-quorum.js` and `trend-stock-research.js` are standalone files in `.claude/workflows/` directly.

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

Core skills: `regime-detection` · `trend-stock-research` · `dip-screener` · `dip-tranches-strategy` · `fomc-monitor` · `prediction-market-odds` · `forecast-ledger` · `hedge-fund-manager` · `tradfi-portfolio-manager` · `superforecasting` · `macro-panel` · `multi-lens-quorum` · `portfolio-monitor` · `portfolio-construction` · `rebalancing` · `risk-management` · `fundamental-analysis` · `stock-chair` · `stock-research-desk` · `13f-watch` · `hedge-fund-13f-analysis` · `congressman-stock-watch` · `signal-convergence-alert` · `agentic-fund-orchestration`

Analyst lenses: `analyst-crypto` · `analyst-derivatives-positioning` · `analyst-systematic-trading` · `analyst-technical-analysis`

Macro-economist panel: `analytics-lyn-alden` · `analytics-ray-dalio` · `analytics-stanley-druckenmiller` · `analytics-lacy-hunt` · `analytics-michael-pettis` · `analytics-russell-napier` · `analytics-warren-buffett` · `analytics-benjamin-graham` · `analytics-morgan-housel`

News feeds: `feed-bloomberg` · `feed-wsj` · `feed-ft` · `feed-bitcoinmagazine` · `feed-coindesk` · `feed-cointelegraph` · `feed-decrypt` · `feed-theblock` · `narrative-news`

**Status:** fast-tier daily scanners live on openclaw (cron + liveness); weekly committee workflow validated (3 iterations); congress stock-watch wired (`congress/`).

---

### 2. Crypto portfolio workflow

Manages a **~$177k crypto book** with a BTC-as-hurdle filter — only deploy into tokens that pass the 6-point infrastructure value-accrual test (HYPE the current benchmark).

Full spec: [`crypto/`](crypto/) — `crypto.goal.md` · `crypto.prd.md` · `crypto.tdd.md` · `crypto.loop.md`

Core skills: `crypto-chair` · `crypto-research-desk` · `crypto-dip-scanner` · `crypto-liquidity-data` · `crypto-onchain-data` · `crypto-news-store` · `crypto-workflow-eval` · `analyst-crypto` · `research-manager` · `defi-portfolio-manager` · `tax-loss-harvesting` · `trend-following`

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

Tracking issue: https://github.com/dzianisv/financial-advisor-agents/issues/1
