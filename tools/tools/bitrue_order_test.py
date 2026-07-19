#!/usr/bin/env python3
import json, time, hmac, hashlib, urllib.request, urllib.error, os, sys
from dotenv import load_dotenv

load_dotenv(".env", override=True)
API_KEY = os.getenv("BITRUE_API_KEY", "")
API_SECRET = os.getenv("BITRUE_API_SECRET", "")
BASE_URL = "https://fapi.bitrue.com"

def sign_headers(method: str, path: str, body_str: str = ""):
    ts = str(int(time.time() * 1000))
    payload = f"{ts}{method.upper()}{path}{body_str}"
    sig = hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-CH-APIKEY": API_KEY,
        "X-CH-TS": ts,
        "X-CH-SIGN": sig,
    }

def request(method: str, path: str, body_obj=None):
    body_str = json.dumps(body_obj, separators=(",", ":")) if body_obj else ""
    data = body_str.encode("utf-8") if method.upper() == "POST" else None
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers=sign_headers(method, path, body_str),
        method=method.upper(),
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)

def main():
    body = {
        "contractName": "E-XLM-USDT",
        "side": "BUY",
        "type": "LIMIT",
        "positionType": 1,
        "open": "OPEN",
        "volume": 10,
        "amount": 1.8,
        "price": 0.18,
        "leverage": 1
    }
    
    print("Testing POST /fapi/v2/order with minimal valid payload...")
    status, raw = request("POST", "/fapi/v2/order", body)
    print(f"Status: {status}")
    print(f"Response: {raw}")

if __name__ == "__main__":
    main()
