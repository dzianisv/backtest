Two things to untangle here — one is a mix-up, one is the real lesson.

**1. That 13% gold/BTC/ETH vault is NOT Maple.** It's **Steakhouse USDT on Morpho**. Maple is a different product (`Syrup USDT`, ~4.2%, institutional lending — no gold/BTC collateral). The XAUt-gold / WBTC / wstETH book you're remembering is the Morpho Steakhouse vault. Easy to conflate since I showed them together, but they're two separate venues.

**2. You're right that the collateral is safe — but that's not the problem. The 13% itself isn't real.** These are two independent things:

- **Collateral quality** (is the loan backed by good assets?) → ✅ Yes: gold, BTC, stETH. No argument.
- **Yield sustainability** (will you actually *earn* that rate?) → ❌ No. The 13% existed for a moment, not a month.

The 30-day history I just pulled is the proof:

```
Steakhouse USDT, last 7 days:  2.51 → 2.52 → 2.50 → 2.67 → 2.53 → 2.53 → 6.58%
30-day:  min 2.48%   max 6.58%   mean 2.97%
```

It sat at **~2.5% for six straight days**, then twitched up on the last day. The "13.7%" was an *instantaneous* spot reading on the Morpho API at the second I queried — DefiLlama's daily samples never even caught above 6.58%. Either way: **the rate you'd actually live with is ~3%, not 13%.**

**Why it can't hold (the mechanism):** lending APY = borrow rate × utilization. The number spikes to 13% only when borrowers briefly max out the wstETH market. The moment they repay, *or* more lenders deposit, utilization drops and the rate falls back to ~2.5%. And here's the kicker — **when you deposit your $15k, you yourself add supply, pushing utilization (and the rate) down.** You can't lock 13%; you'd be buying into a number that's already gone.

So the comparison that matters:

| | Steakhouse USDT (Morpho) | Maple Syrup USDT |
|---|---|---|
| Collateral | gold/BTC/ETH ✅ | overcollateralized loans ✅ |
| Rate you *saw* | 13% (a spike) | 4.1% |
| Rate you'd *earn* (30d mean) | **~3%** | **~4.4%** |
| Stability | swings 2.5%→6.6% | flat ±0.2% |

**You'd earn *more* in Maple (~4.4%) than in the "13%" Steakhouse vault (~3% lived), with less volatility.** The 13% is a mirage — safe collateral, yes, but a rate that evaporates the moment you (or anyone) deposits into it. That's exactly why Maple is the pick for the $15k.

Want me to chart both APY series side by side so you can see the Maple flat-line vs the Steakhouse spike visually?

