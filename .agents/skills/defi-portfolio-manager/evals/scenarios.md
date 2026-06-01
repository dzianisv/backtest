# Eval scenarios (fixed across skill iterations)

Each is a user request handed to a PM agent operating under the skill. The agent has tools (curl,
WebSearch) but the relevant world-state is given inline so scoring is reproducible — what's tested is
the *reasoning and process*, not whether a live fetch happened to succeed.

## S1 — deploy idle cash
> I have 40,000 USDC sitting in my wallet earning nothing. Put it to work. I'm conservative — I will not risk losing the principal.

## S2 — yield-trap temptation
> A friend showed me a "stablecoin" vault paying 18% APY on USDT. I'm thinking of moving most of my stablecoins into it. Good idea? It's called bbqUSDT on Morpho.

## S3 — live incident (Scan must catch it)
> My book: 30% in LayerBank, 25% in Aave USDC, 45% idle USDC.
> [NEWS, today: "LayerBank reports a smart-contract exploit; roughly $27M drained; deposits paused."]
> What should I do with my portfolio right now?

## S4 — messy portfolio review
> Review my book and tell me what to fix:
> - $38,000 USDC in "Seamless USDC Vault @ Morpho" (shows 0% APY)
> - $9,000 USDT-SLPT @ Storm (a perp-DEX LP, 6.7%)
> - $16,000 USDC @ save.finance (Solana, 2.2%)
> - $5,000 ASTER token
> - $4,000 USDC idle on an exchange
> Total ~$72,000.

## S5 — concentration / "is X safe"
> I want to put 60% of my book into sUSDe to capture the Ethena yield. Walk me through whether that's smart.

## S6 — weekly review (the default job, full book, moderate)
> Run my weekly review. Book (~$200k): $90k idle USDC across two wallets, $30k stETH, $20k jitoSOL, $25k Maple Syrup USDC, $15k in a Morpho USDC vault showing 0%, $12k HYPE token, $8k in a Storm perp-LP. Risk profile moderate. Tell me what to do this week.
