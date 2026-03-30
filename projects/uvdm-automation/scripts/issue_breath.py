#!/usr/bin/env python3
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import (
    AccountSet, TrustSet
)
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops
from xrpl.models.amounts import IssuedCurrencyAmount

client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
wallet = Wallet.from_seed("sEd7rNkEqVMtW2gLj3ZeKhnNRnUbACT")

# Enable DefaultRipple (required for token issuer)
print("🚀 Configuring BREATH issuer...")
tx1 = AccountSet(
    account=wallet.classic_address,
    set_flag=8  # asfDefaultRipple
)
resp1 = submit_and_wait(tx1, client, wallet)
print(f"✅ Issuer configured: {resp1.result['hash']}")

# Self-trustline for BREATH (issuer must trust own token)
print("✅ Creating BREATH trustline...")
breath = IssuedCurrencyAmount(
    currency="BREATH",
    issuer=wallet.classic_address,
    value="10000000"  # 10M total supply
)
tx2 = TrustSet(
    account=wallet.classic_address,
    limit=breath
)
resp2 = submit_and_wait(tx2, client, wallet)
print(f"✅ BREATH issued: {resp2.result['hash']}")
