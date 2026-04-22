import sys

def asset_status(symbol):
    symbol = symbol.strip().lower()

    if symbol == "xlm":
        return {"symbol": "xlm", "action": "accumulate", "status": "UVDM XLM mode engaged"}
    elif symbol == "xrp":
        return {"symbol": "xrp", "action": "hold", "status": "XRP mode engaged"}
    elif symbol == "flr":
        return {"symbol": "flr", "action": "buy", "status": "FLR mode engaged"}
    elif symbol == "btc":
        return {"symbol": "btc", "action": "sell", "status": "BTC mode engaged"}
    else:
        return {"symbol": symbol, "action": "unknown", "status": "Waiting for valid symbol"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(asset_status(sys.argv[1]))
    else:
        try:
            while True:
                typed = input("> ")
                print(asset_status(typed))
        except (EOFError, KeyboardInterrupt):
            print("Exited cleanly")
