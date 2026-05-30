# blog/

Substack-ready posts derived from the research in [`../research/`](../research/).

| Post | Topic |
|------|-------|
| [2026-05-where-to-park-usdt-usdc.md](2026-05-where-to-park-usdt-usdc.md) | Where a conservative investor should deposit USDT/USDC this month (Maple ~4.7%; why every 5%+ option fails the collateral test) |

## Graphics

Charts live in [`img/`](img/) and are regenerated from live API data:

```bash
/Users/engineer/.venv/bin/python3 blog/make_charts.py
```

- `01_yield_ladder.png` — the clean-vs-risky yield ladder
- `02_mirage.png` — steakUSDT's "13%" spike vs Maple's flat line (90d)
- `03_candidates.png` — every 5%+ candidate vs Maple (90d)

The `img/series_*.json` files are the raw DefiLlama chart series the script plots; re-pull them to refresh (poolIds are in the script's git history / the research doc).

## Publishing to Substack

Substack's editor doesn't import Markdown image syntax — it renders text but **not** `![](img/...)` links. To publish:

1. Paste the Markdown body into the Substack editor (it converts headers, tables→ it flattens tables, bold, blockquotes, and code blocks).
2. **Tables** become plain text on paste — either rebuild them with Substack's table block or screenshot them. Keep tables short.
3. **Insert each image manually** at its `![...]` marker using the image button, uploading the PNG from `img/`. Order: ladder → mirage → candidates.
4. Use the first `> TL;DR` block as the post's subtitle/preview text.
5. Set a featured image (the yield ladder works well as the social card).

Source data and methodology are in the research note this post is built on:
[`../research/10-crypto-lp-yield-state.md`](../research/10-crypto-lp-yield-state.md).
