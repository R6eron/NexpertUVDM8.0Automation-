#!/usr/bin/env python3
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.requests import AccountLines

client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
wallet = Wallet.from_seed("YOUR_SEED_FROM_DEPLOY")  # From amm_breath_deploy.py

lines = client.request(AccountLines(account=wallet.classic_address)).result
lp_tokens = [line for line in lines["lines"] if line["currency"] == "03" + "..."*37]

print("🎟️ YOUR LP TOKENS:")
for lp in lp_tokens:
    print(f"  AMM: {lp['currency']} | Balance: {lp['balance']}")
