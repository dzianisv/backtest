#!/usr/bin/env python3
"""
Fetch live APYs for DeFi protocols in the crypto portfolio.
No API key required. Sources:
  - Morpho Blue: blue-api.morpho.org/graphql      (Base + ETH vaults)
  - DeFiLlama:  yields.llama.fi/pools             (Maple Syrup, LIDO, ExtraFi XLend, Avantis)
  - Ethena:     ethena.fi/api/yields/...           (sUSDe staking yield)
  - Hyperliquid: api.hyperliquid.xyz/info          (HLP vault APR via userVaultEquities)
"""

import json
import urllib.request

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

    # ExtraFi XLend is NOT a MetaMorpho vault — sourced from DeFiLlama instead.
    # Only pure MetaMorpho vaults go here.
    name_map = {
        "seamless usdc vault": "morpho_seamless_usdc_base",
        "universal usdc": "morpho_universal_usdc_base",
        "morpho eusd": "morpho_eusd_base",
        "gauntlet eusd core": "morpho_eusd_eth",
    }
    out = {}
    for v in result["data"]["vaults"]["items"]:
        name_lower = v["name"].lower().strip()
        state = v.get("state") or {}
        raw_apy = state.get("netApy")  # None = missing data; 0.0 = genuinely idle
        for pattern, key in name_map.items():
            if pattern in name_lower:
                out[key] = None if raw_apy is None else round(raw_apy * 100, 2)
                break
    return out

def defi_llama_apys():
    """Single DeFiLlama fetch for Maple Syrup, LIDO, ExtraFi XLend, Avantis."""
    result = fetch("https://yields.llama.fi/pools")
    if "error" in result or "data" not in result:
        return {"error": result.get("error", "fetch failed")}
    out = {}
    for p in result["data"]:
        proj = (p.get("project") or "").lower()
        sym = (p.get("symbol") or "").lower()
        chain = (p.get("chain") or "").lower()
        meta = (p.get("poolMeta") or "").lower()
        apy = round(p.get("apy") or 0, 2)
        # Maple Syrup USDC / USDT
        if "maple" in proj and "usdc" in sym and "syrup" in meta:
            out["maple_syrup_usdc"] = apy
        elif "maple" in proj and "usdt" in sym and "syrup" in meta:
            out["maple_syrup_usdt"] = apy
        # LIDO stETH on Ethereum
        elif "lido" in proj and "steth" in sym and chain == "ethereum":
            out["lido_steth"] = apy
        # ExtraFi XLend USDC on Base (lending supply side, not leverage-farming)
        elif proj == "extra-finance-xlend" and "usdc" in sym and chain == "base":
            out["extrafi_xlend_usdc_base"] = apy
        # Avantis USDC vault on Base
        elif "avantis" in proj and "usdc" in sym and chain == "base":
            out["avantis_junior_usdc"] = apy
    return out

def ethena_apy():
    """Fetch Ethena sUSDe staking yield."""
    result = fetch("https://ethena.fi/api/yields/protocol-and-staking-yield")
    if "error" in result or "stakingYield" not in result:
        return {"error": result.get("error", "fetch failed")}
    return {"ethena_susde": round(result["stakingYield"]["value"], 2)}

def hyperliquid_vault_apr(user_addr, vault_addr=None):
    """Fetch Hyperliquid HLP vault APR for a given user address."""
    equities = fetch(
        "https://api.hyperliquid.xyz/info",
        method="POST",
        data={"type": "userVaultEquities", "user": user_addr},
        headers={"Content-Type": "application/json"}
    )
    if "error" in equities or not isinstance(equities, list) or not equities:
        return {"error": f"no vault equities for {user_addr}"}

    target = vault_addr or equities[0].get("vaultAddress")
    if not target:
        return {"error": "no vaultAddress in equities"}

    details = fetch(
        "https://api.hyperliquid.xyz/info",
        method="POST",
        data={"type": "vaultDetails", "vaultAddress": target},
        headers={"Content-Type": "application/json"}
    )
    if "error" in details or "apr" not in details:
        return {"error": f"no APR for vault {target}"}

    apr_pct = round((details["apr"] or 0) * 100, 2)
    return {"hyperliquid_hlp_vault": apr_pct, "_vault_name": details.get("name", target)}

def main():
    results = {"sources": {}}

    print("Fetching Morpho Blue vaults...", flush=True)
    morpho = morpho_apys()
    if "error" in morpho:
        results["sources"]["morpho"] = f"[UNAVAILABLE: {morpho['error']}]"
    else:
        results.update(morpho)
        results["sources"]["morpho"] = "blue-api.morpho.org/graphql"

    print("Fetching DeFiLlama (Maple/LIDO/ExtraFi/Avantis)...", flush=True)
    llama = defi_llama_apys()
    if "error" in llama:
        results["sources"]["defi_llama"] = f"[UNAVAILABLE: {llama['error']}]"
    else:
        results.update(llama)
        results["sources"]["defi_llama"] = "yields.llama.fi/pools"

    print("Fetching Ethena sUSDe...", flush=True)
    ethena = ethena_apy()
    if "error" in ethena:
        results["sources"]["ethena"] = f"[UNAVAILABLE: {ethena['error']}]"
    else:
        results.update(ethena)
        results["sources"]["ethena"] = "ethena.fi/api/yields"

    print("Fetching Hyperliquid HLP vault (L3)...", flush=True)
    hlp = hyperliquid_vault_apr("0x5d039ece117073323ade5057a516864f4c40e653")
    if "error" in hlp:
        results["hyperliquid_hlp_vault"] = f"[UNAVAILABLE: {hlp['error']}]"
        results["sources"]["hyperliquid"] = "[UNAVAILABLE]"
    else:
        results["hyperliquid_hlp_vault"] = hlp["hyperliquid_hlp_vault"]
        results["_hyperliquid_vault_name"] = hlp.get("_vault_name", "")
        results["sources"]["hyperliquid"] = f"api.hyperliquid.xyz ({hlp.get('_vault_name','')})"

    print("\n--- LIVE APYs ---")
    for k, v in results.items():
        if k == "sources" or k.startswith("_"):
            continue
        label = k.replace("_", " ").title()
        if v is None:
            print(f"  {label}: [UNAVAILABLE — API returned no data]")
        elif isinstance(v, str):
            print(f"  {label}: {v}")
        elif v == 0.0 and "morpho" in k:
            print(f"  {label}: 0% ⚠️ IDLE — verify on morpho.org")
        else:
            print(f"  {label}: {v}%")

    print("\n--- SOURCES ---")
    for k, v in results["sources"].items():
        print(f"  {k}: {v}")

    print("\nJSON:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
