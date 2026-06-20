#!/usr/bin/env python3
"""
Fetch live APYs for DeFi protocols in the crypto portfolio.
No API key required. Sources:
  - Morpho Blue: blue-api.morpho.org/graphql  (Base + ETH vaults)
  - Maple Syrup: yields.llama.fi/pools         (USDC / USDT)
  - Ethena sUSDe: ethena.fi/api/yields/...
  - LIDO stETH: eth-api.lido.fi/v1/...
  - Hyperliquid vaults: [UNAVAILABLE — no public API]
  - Avantis: [UNAVAILABLE — no public API]
"""

import json
import urllib.request
import urllib.error

def fetch(url, method="GET", data=None, headers=None):
    req = urllib.request.Request(url, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if data:
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def morpho_apys():
    """Query Morpho Blue GraphQL for vault APYs (Base + ETH mainnet)."""
    query = {
        "query": "{ vaults(first:500, where:{chainId_in:[1,8453]}) { items { name chain { id } address state { netApy } } } }"
    }
    result = fetch(
        "https://blue-api.morpho.org/graphql",
        method="POST",
        data=query,
        headers={"Content-Type": "application/json"}
    )
    if "error" in result or "data" not in result:
        return {"error": result.get("error", "unknown")}

    # Known vault name → canonical key mapping
    name_map = {
        "seamless usdc vault": "morpho_seamless_usdc_base",
        "universal usdc": "morpho_universal_usdc_base",
        "extrafi xlend usdc": "morpho_extrafi_usdc_base",
        "morpho eusd": "morpho_eusd_base",
        "gauntlet eusd core": "morpho_eusd_eth",
    }
    out = {}
    for v in result["data"]["vaults"]["items"]:
        name_lower = v["name"].lower().strip()
        state = v.get("state") or {}
        apy = state.get("netApy") or 0
        for pattern, key in name_map.items():
            if pattern in name_lower:
                out[key] = round(apy * 100, 2)
                break
    return out

def maple_apys():
    """Fetch Maple Syrup pool APYs from DeFiLlama yields."""
    result = fetch("https://yields.llama.fi/pools")
    if "error" in result or "data" not in result:
        return {"error": result.get("error", "unknown")}
    out = {}
    for p in result["data"]:
        proj = p.get("project", "").lower()
        sym = p.get("symbol", "").lower()
        meta = (p.get("poolMeta") or "").lower()
        if "maple" not in proj:
            continue
        if "usdc" in sym and "syrup" in meta:
            out["maple_syrup_usdc"] = round(p.get("apy", 0), 2)
        elif "usdt" in sym and "syrup" in meta:
            out["maple_syrup_usdt"] = round(p.get("apy", 0), 2)
    return out

def ethena_apy():
    """Fetch Ethena sUSDe staking yield."""
    result = fetch("https://ethena.fi/api/yields/protocol-and-staking-yield")
    if "error" in result or "stakingYield" not in result:
        return {"error": result.get("error", "fetch failed")}
    return {
        "ethena_susde": round(result["stakingYield"]["value"], 2)
    }

def lido_apy():
    """Fetch LIDO stETH APR via DeFiLlama (eth-api.lido.fi returns 403 in sandbox)."""
    result = fetch("https://yields.llama.fi/pools")
    if "error" in result or "data" not in result:
        return {"error": result.get("error", "fetch failed")}
    for p in result["data"]:
        proj = (p.get("project") or "").lower()
        sym = (p.get("symbol") or "").lower()
        chain = (p.get("chain") or "").lower()
        if "lido" in proj and "steth" in sym and chain == "ethereum":
            return {"lido_steth": round(p.get("apy", 0), 2)}
    return {"error": "LIDO stETH pool not found in DeFiLlama"}

def main():
    results = {"sources": {}}

    print("Fetching Morpho Blue vaults...", flush=True)
    morpho = morpho_apys()
    if "error" in morpho:
        results["sources"]["morpho"] = f"[UNAVAILABLE: {morpho['error']}]"
    else:
        results.update(morpho)
        results["sources"]["morpho"] = "blue-api.morpho.org/graphql"

    print("Fetching Maple Syrup (DeFiLlama)...", flush=True)
    maple = maple_apys()
    if "error" in maple:
        results["sources"]["maple"] = f"[UNAVAILABLE: {maple['error']}]"
    else:
        results.update(maple)
        results["sources"]["maple"] = "yields.llama.fi/pools"

    print("Fetching Ethena sUSDe...", flush=True)
    ethena = ethena_apy()
    if "error" in ethena:
        results["sources"]["ethena"] = f"[UNAVAILABLE: {ethena['error']}]"
    else:
        results.update(ethena)
        results["sources"]["ethena"] = "ethena.fi/api/yields"

    print("Fetching LIDO stETH...", flush=True)
    lido = lido_apy()
    if "error" in lido:
        results["sources"]["lido"] = f"[UNAVAILABLE: {lido['error']}]"
    else:
        results.update(lido)
        results["sources"]["lido"] = "yields.llama.fi/pools (lido)"

    # Flag vaults returning 0% from Morpho API — may be winding down or API gap
    for key in ["morpho_universal_usdc_base", "morpho_extrafi_usdc_base"]:
        if results.get(key) == 0:
            results[key] = "[UNAVAILABLE — Morpho API returned 0%; verify on morpho.org]"

    # Unavailable (no public API)
    results["hyperliquid_vaults"] = "[UNAVAILABLE — check app.hyperliquid.xyz/vaults live]"
    results["avantis_junior_usdc"] = "[UNAVAILABLE — check avantis.trade live]"

    print("\n--- LIVE APYs ---")
    for k, v in results.items():
        if k == "sources":
            continue
        label = k.replace("_", " ").title()
        print(f"  {label}: {v}%")

    print("\n--- SOURCES ---")
    for k, v in results["sources"].items():
        print(f"  {k}: {v}")

    print("\nJSON:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
