#!/usr/bin/env python3

import json
import urllib.request
from xlm_mode_note import (
    xlm_risk_light,
    btc_risk_light,
    xrp_risk_light,
    log_risk_sample,
)

BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

def fetch_price(symbol: str) -> float:
    url = BINANCE_TICKER_URL.format(symbol=symbol)
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return float(data["price"])

def main() -> None:
    xlm_price = fetch_price("XLMUSDT")
    btc_price = fetch_price("BTCUSDT")
    xrp_price = fetch_price("XRPUSDT")

    color, msg = xlm_risk_light(xlm_price)
    log_risk_sample("XLMUSDT", "leader", xlm_price, color, msg, leverage=7.0, position_size=9084)

    color, msg = btc_risk_light(btc_price)
    log_risk_sample("BTCUSDT", "leader", btc_price, color, msg, leverage=5.0, position_size=0.01)

    color, msg = xrp_risk_light(xrp_price)
    log_risk_sample("XRPUSDT", "laggard", xrp_price, color, msg, leverage=5.0, position_size=1000)

if __name__ == "__main__":
    main()
