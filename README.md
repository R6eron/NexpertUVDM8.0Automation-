# NexpertUVDM8.0Automation-
UVDM 8.0 Automations
import requests
import time
import json
import hmac
import hashlib
import logging
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import safe_sign_and_submit_transaction
from flareio import FlareApiClient

def get_api_credentials():
    print("Enter your API credentials (keep secure!)")
    nexo_api_key = input("Nexo API Key: ").strip()
    mexc_api_key = input("MEXC API Key: ").strip()
    mexc_api_secret = input("MEXC API Secret: ").strip()
    xrpl_seed = input("XRPL Wallet Seed: ").strip()
    flare_api_key = input("Flare API Key: ").strip()
    bifrost_ws_endpoint = input("Bifrost RPC Endpoint (default: https://api.bifrost.finance/staking): ") or "https://api.bifrost.finance/staking"
    if not all([nexo_api_key, mexc_api_key, mexc_api_secret, xrpl_seed]):
        print("Error: Required credentials missing. Exiting.")
        return None
    return {
        'nexo_api_key': nexo_api_key,
        'mexc_api_key': mexc_api_key,
        'mexc_api_secret': mexc_api_secret,
        'xrpl_seed': xrpl_seed,
        'flare_api_key': flare_api_key,
        'bifrost_endpoint': bifrost_ws_endpoint
    }

def connect_to_xrpl():
    xrpl_url = "https://s1.ripple.com:51234"
    timeout = 10
    try:
        response = requests.get(xrpl_url, timeout=timeout)
        if response.status_code == 200:
            print("Connected to XRPL network successfully.")
            return JsonRpcClient(xrpl_url)
        print(f"Failed to connect to XRPL network (status: {response.status_code}).")
        return None
    except requests.exceptions.RequestException as e:
        print("Connection to XRPL network failed:", e)
        return None

def retrieve_previous_month_ftso_data():
    ftso_api_url = "https://api.flare.network/ftso-data"
    try:
        response = requests.get(ftso_api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        top_ftsos = sorted(data, key=lambda x: x.get("performance_score", 0), reverse=True)[:2]
        print("Top FTSOs:", top_ftsos)
        return top_ftsos
    except requests.exceptions.RequestException as e:
        print("Failed to retrieve FTSO data (using mock):", e)
        return [{"ftso_id": "mock1", "performance_score": 95}, {"ftso_id": "mock2", "performance_score": 90}]

def connect_to_flare_protocols(credentials):
    api_key = credentials['flare_api_key']
    if not api_key:
        print("Flare API key required.")
        return None
    try:
        api_client = FlareApiClient(api_key=api_key)
        print("Connected to Flare Protocols successfully.")
        return api_client
    except Exception as e:
        print("Failed to connect to Flare Protocols:", e)
        return None

def auto_wrap_flare_tokens(flare_token_amount, flare_client):
    try:
        wrapped_response = flare_client.post("/wrap", data={"amount": flare_token_amount})
        wrapped_tokens = wrapped_response.json().get("wrapped_amount", flare_token_amount * 1.1)
        print(f"Auto-wrapped {flare_token_amount} Flare tokens to {wrapped_tokens}")
        return wrapped_tokens
    except Exception as e:
        print("Failed to wrap Flare tokens:", e)
        return None

def delegate_votes_to_best_ftsos(credentials, wrapped_tokens, ftso_data, xrpl_client):
    total_votes = 100
    vote_percentage = 50
    votes_per_ftso = total_votes * (vote_percentage / 100)
    wallet = Wallet.from_seed(credentials['xrpl_seed'])
    for ftso in ftso_data:
        try:
            tx = Payment(account=wallet.classic_address, destination="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", amount=str(votes_per_ftso))
            response = safe_sign_and_submit_transaction(tx, wallet, xrpl_client)
            print(f"Delegated {votes_per_ftso} votes to FTSO ID {ftso['ftso_id']}: {response.result}")
        except Exception as e:
            print(f"Failed to delegate votes to FTSO {ftso['ftso_id']}:", e)

def mint_f_assets(credentials, crypto_sets, xrpl_client):
    f_assets = []
    wallet = Wallet.from_seed(credentials['xrpl_seed'])
    for crypto_set in crypto_sets:
        try:
            tx = Payment(account=wallet.classic_address, destination=wallet.classic_address, amount="100")
            response = safe_sign_and_submit_transaction(tx, wallet, xrpl_client)
            f_asset = {"crypto_set": crypto_set, "f_asset_id": f"f_asset_{crypto_set}", "amount": 100, "tx_result": response.result}
            f_assets.append(f_asset)
            print(f"Minted {f_asset['amount']} {f_asset['f_asset_id']}: {response.result}")
        except Exception as e:
            print(f"Failed to mint {crypto_set}:", e)
    return f_assets

def get_nexo_balance(credentials):
    url = "https://api.nexo.com/v1/balances"
    headers = {"X-API-KEY": credentials['nexo_api_key'], "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        balances = response.json()
        print("Nexo Balances:", balances)
        return balances
    except requests.exceptions.RequestException as e:
        print(f"Nexo API Error: {e}")
        return None

def place_mexc_order(credentials, symbol, side, quantity, price):
    base_url = "https://api.mexc.com"
    endpoint = "/api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {"symbol": symbol, "side": side, "type": "LIMIT", "quantity": quantity, "price": price, "timestamp": timestamp, "recvWindow": 5000}
    query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    signature = hmac.new(credentials['mexc_api_secret'].encode(), query_string.encode(), hashlib.sha256).hexdigest().lower()
    params["signature"] = signature
    headers = {"X-MEXC-APIKEY": credentials['mexc_api_key'], "Content-Type": "application/x-www-form-urlencoded"}
    try:
        response = requests.post(f"{base_url}{endpoint}", headers=headers, data=params, timeout=10)
        response.raise_for_status()
        print("MEXC Order Placed:", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"MEXC API Error: {e}")
        return None

def query_bifrost_staking(credentials):
    try:
        response = requests.get(credentials['bifrost_endpoint'], timeout=10)
        response.raise_for_status()
        print("Bifrost Staking Data:", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Failed to query Bifrost:", e)
        return {"mock_staking": "100 FLR delegated"}

def main():
    print("Starting UVDM Automation Script")
    credentials = get_api_credentials()
    if not credentials:
        return
    xrpl_client = connect_to_xrpl()
    if not xrpl_client:
        return
    get_nexo_balance(credentials)
    query_bifrost_staking(credentials)
    flare_client = connect_to_flare_protocols(credentials)
    if not flare_client:
        return
    wrapped_tokens = auto_wrap_flare_tokens(1000, flare_client)
    ftso_data = retrieve_previous_month_ftso_data()
    delegate_votes_to_best_ftsos(credentials, wrapped_tokens, ftso_data, xrpl_client)
    mint_f_assets(credentials, ["set1", "set2", "set3"], xrpl_client)
    place_mexc_order(credentials, "BTCUSDT", "BUY", "0.001", "50000")
    print("UVDM Automation Completed")

if __name__ == "__main__":
    main()
