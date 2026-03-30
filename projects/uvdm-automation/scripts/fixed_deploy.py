#!/usr/bin/env python3
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import AMMCreate
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.account import does_account_exist

client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
wallet = Wallet.from_seed("sEd7rNkEqVMtW2gLj3ZeKhnNRnUbACT")

print(f"🚀 Checking {wallet.classic_address}...")
if does_account_exist(wallet.classic_address, client):
    print("✅ Account funded - deploying AMM")
    breath_amount = IssuedCurrencyAmount(
        currency="BREATH",
        issuer=wallet.classic_address,
        value="2160000"
    )
    tx = AMMCreate(
        account=wallet.classic_address,
        amount=xrp_to_drops(20),
        amount2=breath_amount,
        trading_fee=300
    )
    response = submit_and_wait(tx, client, wallet)
    print(f"✅ AMM DEPLOYED: {response.result['hash']}")
    print(f"https://testnet.xrpl.org/transactions/{response.result['hash']}")
else:
    print("⏳ Account not ready - wait 30s")
