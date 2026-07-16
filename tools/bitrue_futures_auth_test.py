#!/usr/bin/env python3
import json, time, hmac, hashlib, urllib.request, urllib.error, os, sys
from dotenv import load_dotenv

load_dotenv(".env", override=True)
API_KEY = os.getenv("BITRUE_API_KEY", "")
API_SECRET = os.getenv("BITRUE_API_SECRET", "")
BASE_URL = "https://fapi.bitrue.com"

def sign_headers(method: str, path: str, body: str = ""):
    ts = str(int(time.time() * 1000))
    payload = f"{ts}{method.upper()}{path}{body}"
    sig = hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-CH-APIKEY": API_KEY,
        "X-CH-TS": ts,
        "X-CH-SIGN": sig,
    }

def request(method: str, path: str, body_obj=None):
    body = json.dumps(body_obj, separators=(",", ":")) if body_obj is not None else ""
    data = body.encode() if method.upper() == "POST" else None
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers=sign_headers(method, path, body),
        method=method.upper(),
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode()
            return r.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, raw
    except Exception as e:
        return None, json.dumps({"error": str(e)})

def main():
    if not API_KEY or not API_SECRET:
        print(json.dumps({"ok": False, "error": "Missing BITRUE_API_KEY or BITRUE_API_SECRET in .env"}))
        sys.exit(1)

    tests = [
        ("GET", "/fapi/v1/ping", None),
        ("GET", "/fapi/v1/time", None),
        ("GET", "/fapi/v2/account", None),
    ]

    results = []
    for method, path, body in tests:
        status, raw = request(method, path, body)
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw
        results.append({
            "method": method,
            "path": path,
            "status": status,
            "response": parsed
        })

    print(json.dumps({
        "ok": True,
        "base_url": BASE_URL,
        "results": results
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
