---
name: dip-tranches-strategy
description: Tiered framework for deploying cash into S&P 500 ETFs (VOO, IVV, SPLG, SPY) during drawdowns. Use this whenever the user mentions buying the dip, deploying cash into the S&P 500, sitting on cash waiting for a correction, asks how much to invest during a market drop, mentions a drawdown of -5%/-7%/-10%/-20% from highs, asks about dollar-cost averaging vs lump sum, has a windfall (inheritance, bonus, sale proceeds) to deploy, or wants to know what percentage of a portfolio to commit at each level of decline. Trigger even if the user only describes the situation ("market is down 12%, should I add?") without using the term "tranche". Always remind the user this is an analytical framework, not personalized financial advice.
license: MIT
compatibility: opencode
metadata:
  audience: retail-investors
  domain: personal-finance
---

# Dip Tranches Strategy

A disciplined framework for deploying a cash reserve into broad-market US equity index ETFs (VOO, IVV, SPLG/SPYM, SPY) during market drawdowns. The goal is to avoid the two failure modes most retail investors fall into: (1) firing all dip-buying cash at the first -5% pullback and having nothing left when -25% arrives, and (2) sitting in cash forever waiting for a crash that doesn't come.

## ⛔ CRYPTO ASSETS — different process, mandatory data step

This skill's % drawdown tiers are calibrated for S&P 500 ETFs (typical drawdown: -5% to -35%). **Do NOT apply them directly to crypto**, where -50% to -80% drawdowns are routine and support zones are structural, not purely % based.

**For any crypto "when/where to buy" question, the mandatory sequence is:**

1. **Pull OHLCV first.** Before naming any dollar level, call `data_get_ohlcv` for 210 weekly bars. No exceptions.
2. **Count price concentration.** Bucket weekly closes into $5k-$10k ranges. A level with ≥8 weekly closes is structural support; <4 closes is just a visit.
3. **Cross-check on-chain.** The 200wMA (already computed by crypto-advisor) is the long-term cost-basis floor. The realized price (~MVRV=1) is where average holder bought. Levels near those matter; arbitrary round numbers do not.
4. **Name only data-backed levels.** Every price level set in a `mkt` alert `--reason` must cite the specific evidence: "14 weekly closes in $60k–$65k range" or "200wMA $62,640". Never "strong support zone" without data.

**⛔ Hard rule:** If you cannot identify a level from steps 1–3, do NOT set a `mkt` alert with a price. Set an alert on a data-verified level or do not set one at all. Fabricated support levels in alerts are worse than no alert — they create false confidence.

## Mandatory framing

Before applying this framework, always remind the user:

- This is an **analytical framework**, not personalized financial advice. The user should consult a fee-only fiduciary CFP before deploying significant capital.
- This framework assumes a **long-horizon investor** (10+ years) treating the cash as growth capital, not their entire net worth.
- Before any equity deployment, the user should have: an adequate emergency fund (3-6 months expenses), high-interest debt paid down, and clarity on time horizon.
- Past drawdown patterns don't guarantee future ones. The framework can fail in a structural bear market that doesn't recover for years.

## The portfolio split

For a given investable cash amount, split it into three buckets:

| Bucket | % of cash | Purpose | Deployment |
|---|---|---|---|
| Foundation | 50% | Time-in-market | Lump sum now (or spread over 4-8 weeks) |
| Systematic DCA | 30% | Smooth cost basis | Equal monthly buys over 12-18 months |
| Dip Reserve | 20% | Buy the dip | Tiered deployment on drawdowns (see below) |

Park the Dip Reserve in a money market fund, T-bills, or HYSA earning 4-5% while it waits.

**If the user is more risk-averse or anxious about all-time highs:** shift to 30% / 40% / 30% (less foundation, more reserve).
**If the user is more aggressive or strongly bullish:** shift to 70% / 20% / 10% (more foundation, less reserve).

The dip strategy is on the **Dip Reserve bucket only**. Foundation + DCA buckets run on schedule regardless of market level.

## Tier structure for the Dip Reserve

The Dip Reserve splits into three tiers, triggered by drawdown from the trailing 52-week high:

| Tier | Trigger | % of Dip Reserve |
|---|---|---|
| Tier 1 | -7% from 52-week high | 20% |
| Tier 2 | -12% from 52-week high | 30% |
| Tier 3 | -20% from 52-week high | 50% |

**Worked example for $200K Dip Reserve:** Tier 1 = $40K, Tier 2 = $60K, Tier 3 = $100K.

The 20/30/50 weighting is intentional: shallow dips happen 1-2x/year, moderate corrections every 18-24 months, deep drawdowns every 3-5 years. Weight the rare, painful events most heavily because that's where the highest-conviction entries historically lived (2020, 2022, early 2025).

## Within each tier: sub-tranches

The critical insight: **a dip is not a single moment, it's a process**. Splitting each tier into sub-tranches prevents whipsaw losses and prevents exhausting ammo too early.

### Tier 1 ($40K example, fires at -7%)
| Sub | Trigger | Amount |
|---|---|---|
| 1a | -7% from 52w high (weekly close) | $10K |
| 1b | -8.5% | $10K |
| 1c | -10% | $10K |
| 1d | Time trigger: weekly close still below -7% after 2 weeks | $10K |

### Tier 2 ($60K example, fires at -12%)
| Sub | Trigger | Amount |
|---|---|---|
| 2a | -12% from 52w high | $15K |
| 2b | -14% | $15K |
| 2c | -16% | $15K |
| 2d | Time trigger: weekly close still below -12% after 3 weeks | $15K |

### Tier 3 ($100K example, fires at -20%)
| Sub | Trigger | Amount |
|---|---|---|
| 3a | -20% from 52w high | $25K |
| 3b | -25% | $25K |
| 3c | -30% | $25K |
| 3d | Time trigger: weekly close still below -20% after 4 weeks | $25K |

Total Dip Reserve: deployed across up to 12 buy events.

## Execution rules

These rules exist to protect the user from impulsive behavior in either direction (panic buying or paralysis).

1. **Use weekly closes, not intraday prints.** Most triggers should fire on Friday close prices. Intraday wicks reverse too often to be reliable signals.

2. **Don't skip tiers.** If the market gaps down -15% overnight, deploy Tier 1 fully first, then Tier 2 on the normal schedule. Resist "backing up the truck" on day one.

3. **Cooldown between sub-tranches.** Minimum 3 trading days between fills, even if conditions are met. Forces the user to actually watch the dip develop.

4. **Re-arm rule.** If the market recovers above -5% from a new 52-week high, reset tier counters. The next decline is a fresh dip. But cap re-arms at 2x per year to prevent chasing noise.

5. **Update the 52-week high regularly.** As the index grinds higher, trigger prices recompute. Refresh at minimum monthly, ideally weekly.

6. **Stop deploying if fundamentals crack badly.** If Tier 3 fires alongside VIX > 40, recession underway, unemployment rising sharply, credit spreads blowing out (a 2008-style scenario), the user should pause the last sub-tranches and reassess. This is judgment, not a mechanical rule.

7. **Unused reserve gets recycled.** If no qualifying dip materializes within 18-24 months, fold the unused Dip Reserve back into the DCA bucket. Cash waiting forever is a drag on returns.

## Order execution mechanics

**Manual approach:** Set GTC (good-till-cancelled) limit orders at each sub-tranche price level. Most major brokers (Schwab, Fidelity, Vanguard, IBKR, Robinhood) support these. Adjust limit prices when the 52-week high updates.

**Computing trigger prices:** For each sub-tranche, the limit price is `52_week_high * (1 - drawdown_pct)`. Example: 52-week high = $700, Tier 1a trigger at -7% means a limit buy at $651.

**Automated approach:** A daily script that pulls the previous close, computes drawdown from rolling 52-week high, checks which sub-tranches should fire, and either places orders via broker API (Alpaca, IBKR) or sends an alert. **Strongly recommend notification-only mode** for the first 6+ months before any auto-trading.

## Live data and automation

This skill bundles three resources for getting real prices, detecting triggers, and backtesting:

- **`scripts/check_drawdown.py`** — a ready-to-run Python script. Pulls the last 400 trading days for a given ticker via yfinance, computes drawdown from 52-week high, and prints (or emits JSON for) all currently-triggered sub-tranches and the next pending price levels. Run with `python scripts/check_drawdown.py --ticker VOO --reserve 200000`. Read it before suggesting custom code — the user may already have it set up.

- **`assets/dip_tranches_strategy.pine`** — a Pine Script v6 strategy for TradingView. Implements the full 3-tier × 4-sub-tranche framework directly on the user's chart, including the re-arm rule. Plots tier trigger lines, shades tier zones, shows a live dashboard, runs as a backtestable strategy in TradingView's Strategy Tester, and fires alerts on every sub-tranche trigger. Recommend this whenever the user wants to (a) visualize the strategy on a chart, (b) backtest it against historical data interactively, or (c) get push/email/webhook alerts when triggers fire. See "Using the TradingView strategy" below for setup details.

- **`references/data-sources.md`** — a detailed comparison of data sources (yfinance, xfinance, Alpha Vantage, Twelve Data, Finnhub, Polygon.io, broker APIs) with code examples, free-tier limits, reliability caveats, and recommended setups by user scale. Load this when the user asks anything about data retrieval, API choice, scheduling, rate limits, or production reliability.

**Quick guidance for picking a source:**
- Hobby / personal use, ≤1 ticker daily: `yfinance` is fine if cached.
- Reliability matters (you'd be upset if it broke for a week): `xfinance` (yfinance-compatible with auto-failover) or Twelve Data free tier (800 calls/day).
- Production agent placing real trades: Polygon.io paid plan or the user's broker API (Alpaca/IBKR/Schwab).
- Just want to see it on a chart and get alerts: the bundled Pine Script — TradingView handles data, charting, and notifications for free.

**Common reliability pitfall:** yfinance scrapes Yahoo Finance and is fragile — Yahoo can rate-limit or block IPs without notice, especially from cloud providers. Always cache data locally and never put yfinance in the hot path of automated trading without a backup source.

**For automation orchestration:** a daily cron at 5pm ET (after US market close) is the right cadence. Free options include GitHub Actions scheduled workflows, AWS Lambda + EventBridge, or a $5/month VPS with crontab. Notifications via Telegram bot, email (SMTP), or Slack webhook are all trivial to wire up.

## Using the TradingView strategy

The bundled `assets/dip_tranches_strategy.pine` is a Pine Script v6 strategy. Setup:

1. Open TradingView, load a chart of VOO (or IVV / SPLG / SPY).
2. Switch the chart to the **Weekly** timeframe — the strategy's tier triggers fire on weekly closes, matching the framework's "use weekly closes, not intraday wicks" rule.
3. Open the **Pine Editor** (bottom panel), paste the contents of `dip_tranches_strategy.pine`, and click **Add to chart**.
4. Open the strategy's **Settings → Inputs** to configure: Dip Reserve size (default $200K), tier triggers (default -7% / -12% / -20%), tier allocation (default 20% / 30% / 50%), and re-arm rules.
5. **For backtesting**, open the **Strategy Tester** panel at the bottom. TradingView simulates the deployment across the chart's full history and reports net profit, drawdown, win rate, etc. To check the 2022 scenario discussed in the worked example, scroll the chart back to 2022 and inspect the "List of Trades" tab.
6. **For live alerts**, right-click any tier trigger line on the chart or click the alarm icon → **Create Alert** → set Condition to "Dip Tranches Deploy" → Any alert() function call. TradingView pushes notifications to phone, email, or a webhook URL.

**Important caveats for the Pine Script:**
- **The strategy uses the chart's price history** — TradingView's free tier limits how far back this goes (typically 5-10 years for most ETFs). For longer backtests, the user needs a paid TradingView plan.
- **Backtest results are simulations**, not promises. Slippage, dividend reinvestment, and broker commissions are simplified. Don't size positions purely on the green PnL number.
- **The script is a tool, not a robot.** TradingView can't actually buy VOO for the user — it only generates alerts. Real execution still requires the user (or a broker-API bridge) to place orders.
- **The re-arm rule is capped at 2 resets per 52 bars** by default to prevent the strategy from chasing every minor pullback in a strong uptrend. Tune via the input panel.

## How to apply this skill

When a user asks for a dip-buying plan, walk through these steps:

1. **Ask for context** (only if not already provided): total cash to deploy, whether it's in a taxable or tax-advantaged account, time horizon, and risk tolerance. If they push back on questions, give the default 50/30/20 plan with a note about adjusting.

2. **Compute the three buckets** based on the cash amount.

3. **Compute the three tiers** for the Dip Reserve (20% / 30% / 50% split of the reserve).

4. **Compute sub-tranches** for each tier (4 sub-tranches per tier, equal-weighted).

5. **Compute concrete trigger prices** using the current 52-week high of the chosen ETF. If the user hasn't given the high, either ask, or note the formula and let them fill in.

6. **Summarize execution rules** the user needs to follow.

7. **Optionally apply to a historical drawdown** as a worked example (e.g., 2022 or 2020) to make the strategy concrete.

8. **Remind the user about the framing** — analytical framework, not advice; consult a CFP.

## Worked example: $1M cash, VOO at 52-week high of $700

Bucket split:
- Foundation: $500K → lump sum into VOO over 4-8 weeks
- DCA: $300K → ~$20K/month for 15 months
- Dip Reserve: $200K → tiered deployment

Tier sizes:
- Tier 1: $40K (trigger -7%)
- Tier 2: $60K (trigger -12%)
- Tier 3: $100K (trigger -20%)

Tier 1 sub-tranches and trigger prices:
- 1a: $10K limit buy at $651.00 (-7%)
- 1b: $10K limit buy at $640.50 (-8.5%)
- 1c: $10K limit buy at $630.00 (-10%)
- 1d: $10K manual buy if weekly close still below $651 two weeks after 1a fires

Tier 2 sub-tranches and trigger prices:
- 2a: $15K at $616.00 (-12%)
- 2b: $15K at $602.00 (-14%)
- 2c: $15K at $588.00 (-16%)
- 2d: $15K manual if still below $616 three weeks after 2a fires

Tier 3 sub-tranches and trigger prices:
- 3a: $25K at $560.00 (-20%)
- 3b: $25K at $525.00 (-25%)
- 3c: $25K at $490.00 (-30%)
- 3d: $25K manual if still below $560 four weeks after 3a fires

## Historical sanity check (2022 drawdown on VOO)

VOO peaked ~$435 in early 2022, bottomed ~$326 in October 2022 (-25%). Under this framework with a $200K reserve:
- Feb 2022: -7% triggers → Tier 1a, 1b deployed (~$20K at ~$405)
- Mar 2022: -10% → Tier 1c deployed ($10K at ~$390)
- Apr-May 2022: -12% to -16% → Tier 2a, 2b, 2c deployed ($45K)
- Jun 2022: -20% → Tier 3a deployed ($25K at ~$348)
- Sep-Oct 2022: -25% → Tier 3b deployed ($25K at ~$326)
- Total deployed near bottom: ~$125K of $200K reserve
- Average cost basis on deployed dip capital: ~$370-385
- VOO recovered to old highs by mid-2023 and is well above today

The framework would have left ~$75K of reserve unused at the bottom — that's a feature, not a bug. It preserves dry powder for the rare deep crisis.

## Common user questions and how to answer

**"Why not just lump sum everything?"** — Vanguard research shows lump sum beats DCA ~2/3 of the time on average, but the framework is designed around regret risk and behavioral fit, not just expected value. A 50% foundation lump sum captures most of the time-in-market advantage while the 20% reserve protects against the buy-at-the-top scenario.

**"What if the dip never comes?"** — The 18-24 month timeout rule folds unused reserve back into DCA. Worst case: slightly suboptimal entry, still fully invested within ~2 years.

**"Why these specific percentages (7/12/20)?"** — They roughly correspond to: 1-standard-deviation pullback, technical correction territory, bear-market territory. Could be tuned slightly (e.g., -10/-15/-25 for a more patient deployment). The exact numbers matter less than having a rules-based approach.

**"Should I use options/leverage at the bottom?"** — Out of scope. Adds complexity and tail risk most retail investors mismanage. If the user pushes, point them to a CFP.

**"Which ETF should I buy?"** — VOO, IVV, and SPLG/SPYM all track the S&P 500 with expense ratios of 0.02-0.03%. They're interchangeable for this strategy. SPY has higher fees but tighter spreads; better for active trading than long-term holds.
