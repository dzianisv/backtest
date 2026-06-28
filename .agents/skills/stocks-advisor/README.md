# stocks-advisor

Analyzes individual stocks one at a time — runs a **5-seat analyst panel** (fundamental / technical / narrative / sentiment / smart-money) per stock and outputs a concrete **entry plan** (price zone + bar-close trigger + market-based stop) with a **BUY / WATCH / SKIP** decision.

For portfolio reviews: outputs HOLD / ADD / TRIM / EXIT per position with a tax-harvest table, cash deployment plan, and a cross-portfolio synthesis seat.

Input: user-supplied ticker list, a Google Sheet of holdings, or stocks discovered live from a named market theme.

> Educational analysis, not financial advice. Single stocks are satellites; the index is the bar.

## Architecture

```mermaid
flowchart TD
    USER(["User prompt"])

    MEM["Step -1 · Load prior memory
bun portfolio-memory/recall.ts"]
    SHEET["Step 0 · Load Google Sheet (optional)
gws sheets +read
ticker, qty, cost_basis, pnl_pct"]
    SEED["Step 1 · Seed todo list
INSERT INTO todos per ticker"]

    MACRO["Step 0.9 · Macro-regime synthesis — run ONCE
WSJ feeds/wsj.ts --feed markets,economy
FT feeds/ft.ts --section markets,global-economy
Yahoo Finance breadth
→ 5-sentence paragraph:
  Fed/rates · Growth · Inflation · Geopolitics · Liquidity
Anti-hallucination: every sentence = named dateable fact
Save to RUN_DIR/macro_regime.txt
Inject into ALL seat data packages as macro_regime"]

    subgraph SEQ ["Sequential per-stock loop — ONE ticker at a time (shared TradingView slot)"]
        direction TB

        subgraph TVPULL ["Orchestrator data pull — subagents cannot call MCP or yfinance"]
            direction LR
            TV1["TradingView MCP
chart_set_symbol NASDAQ: NYSE:
D OHLCV 365d summary + 250 bars
study values: RSI, BB, MACD, Volume
W OHLCV 210 bars
capture_screenshot"]
            FYFI["fundamentals.py (yfinance)
price, ma50, ma200, vs200d
fwdPE, PEG, rev growth
FCF yield, ROE
short pct, inst pct, rec_mean"]
        end

        PKG["Assemble data package
TradingView + yfinance merged
+ macro_regime injected
+ prior_context injected"]

        subgraph SEATS ["5 seats — PARALLEL subagents"]
            direction TB

            subgraph NOSEEK ["Seats 1, 2, 4 — injected data ONLY (no external calls)"]
                direction LR
                SF["Seat 1 · Fundamental
FCF yield, PE, PEG
rev growth, moat
STRONG / GOOD / FAIR / POOR"]
                ST["Seat 2 · Technical Bernstein
Setup, Trigger, Follow-Through
RSI, BB, MACD, MAs
SETUP_NAMED / NO_SETUP / BROKEN"]
                SS["Seat 4 · Sentiment
short pct, inst pct, rec_mean
contrarian read
QUIET_ACCUM / NEUTRAL / CROWDED / EXTREME"]
            end

            subgraph NARR ["Seat 3 · Narrative — reads live news"]
                direction TB
                SN_DATA["Receives injected data + macro_regime"]
                NEWS["read_news.ts --source ft,wsj (discovery)
feeds/wsj.ts + feeds/ft.ts (citation)
web_fetch Bloomberg/Reuters (breadth)
Verbatim quotes required
No URL = not a source"]
                SN_OUT["EARLY / MID / LATE / FADING
theme durability verdict"]
                SN_DATA --> NEWS --> SN_OUT
            end

            subgraph SM ["Seat 5 · Smart-Money — disclosed flows"]
                direction TB
                SM_IN["Receives injected data + macro_regime"]
                SM_FETCH["web_fetch per-ticker:
openinsider.com Form 4 (code P)
13f.info stock page (net adds/trims)
EDGAR SC 13D/13G search
capitoltrades.com PTR buys
No URL = not a source"]
                SM5["ACCUMULATING / DISTRIBUTING / NEUTRAL
CONVICTION: HIGH / MED / LOW"]
                SM_IN --> SM_FETCH --> SM5
            end
        end

        VDT["Verdict decision table
BUY:   Fund GTE GOOD + SETUP_NAMED + MID or EARLY + not EXTREME
WATCH: Fund GTE GOOD but NO_SETUP (wait for trigger)
SKIP:  Fund POOR or LATE or FADING or BROKEN
SKIP dominates · Conviction 1-5"]

        PERSIST["UPDATE stock_analysis
bun portfolio-memory/remember.ts"]

        TV1 --> PKG
        FYFI --> PKG
        PKG --> SEATS
        SF & ST & SN_OUT & SS & SM5 --> VDT
        VDT --> PERSIST
    end

    SYNTH["Step 4 · Portfolio-synthesis seat — run ONCE after per-stock loop
/model opus /effort xhigh — single subagent, cross-position reasoning

Input: all per-stock verdicts + holdings + macro_regime + theme map

Output (5 sections):
1. FACTOR CORRELATION MAP — group by Fed/USD/oil/AI-capex/China;
   flag any factor > 25% book weight as CONCENTRATION RISK
2. OVER-DIVERSIFICATION CRITIQUE — if > 40 names, list index-like
   positions replaceable by VOO (Carver: marginal benefit falls past ~20)
3. CROSS-POSITION CONFLICTS — ADD + TRIM pairs sharing same factor
4. PORTFOLIO STRUCTURE VERDICT — biggest structural risk + single action
5. CASH DEPLOYMENT PRIORITY — top 3 ADD candidates ranked by portfolio fit"]

    SIGNAL["Signal table
Ticker, Decision, Conv, Entry zone, Trigger, Theme"]
    CHAIR[["stock-chair
portfolio synthesis, sizing, concentration"]]

    USER --> MEM --> SHEET --> MACRO --> SEED --> SEQ
    PERSIST --> SYNTH --> SIGNAL --> CHAIR
```

## Two input modes

| Mode | Input | Verdicts |
|---|---|---|
| **Watchlist / Theme discovery** | Explicit tickers or live theme discovery | BUY / WATCH / SKIP |
| **Portfolio review** | Google Sheet URL (holdings + cost basis) | HOLD / ADD / TRIM / EXIT + tax-harvest table + portfolio synthesis |

## The 5 seats

| Seat | Lens | Data source | Output |
|---|---|---|---|
| **Fundamental** | FCF yield, PE, PEG, margins, moat — margin of safety at current price? | Injected (yfinance) | STRONG / GOOD / FAIR / POOR |
| **Technical** (Bernstein STF) | Set-Up → Trigger → Follow-Through. Named setup + bar-close trigger + market-based stop. No trigger = no trade. | Injected (TradingView) | SETUP_NAMED / NO_SETUP / BROKEN |
| **Narrative / Macro** | Theme phase + macro-regime context. `read_news.ts` for discovery; feed scripts for verbatim citation. No fabrication. | Injected + live news | EARLY / MID / LATE / FADING |
| **Sentiment** | Contrarian read: short%, institutional%, analyst consensus, RSI extension | Injected (yfinance) | QUIET_ACCUM / NEUTRAL / CROWDED / EXTREME |
| **Smart-Money** | Disclosed flows: Form 4 (openinsider), 13F (13f.info), 13D (EDGAR), PTR (capitoltrades). ≥2 classes agreeing → verdict. | Live web_fetch | ACCUMULATING / DISTRIBUTING / NEUTRAL |

## Step 0.9 — Macro-regime synthesis

Runs **once** before the per-stock loop. Produces a shared 5-sentence paragraph injected into every seat's data package:

| Dimension | Content |
|---|---|
| Fed/rates | Fed stance + next meeting expectation + one named CME/FOMC data point |
| Growth/earnings | Current earnings season signal or GDP read, specific number |
| Inflation | Latest CPI/PCE print with date |
| Geopolitics | Single most market-relevant geopolitical fact this week |
| Liquidity/risk appetite | Equity trend + vol signal (VIX level, index weekly move) |

Anti-hallucination rule: every sentence names a source and a specific, dateable fact. No training-memory claims.

## Step 4 — Portfolio-synthesis seat

Runs **once** after the per-stock loop completes. A single `/model opus /effort xhigh` subagent that reasons across all positions simultaneously — the cross-portfolio view the per-stock loop structurally cannot produce:

1. **Factor correlation map** — groups holdings by shared risk factor; flags >25% concentration
2. **Over-diversification critique** — if >40 names, identifies index-like positions (Carver: marginal diversification benefit falls past ~20 uncorrelated instruments)
3. **Cross-position conflicts** — ADD/TRIM pairs sharing the same factor exposure
4. **Portfolio structure verdict** — biggest structural risk + single highest-impact action
5. **Cash deployment priority** — top 3 ADD candidates ranked by portfolio-level fit

## Verdict rules

```
BUY   = Fundamental ≥ GOOD  AND  SETUP_NAMED  AND  phase ∈ {EARLY,MID}  AND  Sentiment ≠ EXTREME
WATCH = Fundamental ≥ GOOD  BUT  NO_SETUP (wait for trigger)
SKIP  = Fundamental = POOR  OR   phase ∈ {LATE,FADING}  OR  Technical = BROKEN
SKIP dominates all other signals.
Conviction 1–5: start at 3, ±1 per alignment signal.
Smart-money is a conviction modifier (not a primary driver):
  +1 if ACCUMULATING with ≥2 other seats aligned
  −1 if DISTRIBUTING (also caps BUY conviction at 3/5)
```

## Hard constraints

- **TradingView MCP lives only in the orchestrator** — subagents receive injected data, cannot call MCP.
- **One chart slot** — data pull is strictly sequential, one ticker at a time.
- **ETF / sleeve allocation** → `tradfi-portfolio-manager`. This skill is individual stocks only.
- **Portfolio synthesis** → `stock-chair`. This skill provides the synthesis input; `stock-chair` owns sizing decisions.

## Layout

| Path | What |
|---|---|
| `SKILL.md` | Full operating instructions with source citations |
| `scripts/fundamentals.py` | yfinance data helper — writes `{TICKER}.json.out.json` |
| `references/seat-prompts.md` | Per-seat subagent prompt templates |
