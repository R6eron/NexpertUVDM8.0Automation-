import time
from bitrue_client import BitrueClient
from position_manager import PositionManager
from risk_engine import RiskEngine

API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"
SYMBOL = "BTCUSDT"
POLL_SECONDS = 2

def close_position(client, symbol, position_amt):
    if position_amt > 0:
        side = "SELL"
    elif position_amt < 0:
        side = "BUY"
    else:
        return None

    payload = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": str(abs(position_amt)),
        "reduceOnly": "true"
    }
    return client.request("POST", "/fapi/v1/order", payload=payload)

def main():
    client = BitrueClient(API_KEY, API_SECRET)
    pm = PositionManager(client, SYMBOL)
    re = RiskEngine(tp_pct=0.02, sl_pct=0.01)

    state = pm.current_state()
    print("STATE:", state)

    if state["side"] == "FLAT":
        print("No open position.")
        return

    th = re.thresholds(state["side"], state["entryPrice"])
    print("THRESHOLDS:", th)

    while True:
        state = pm.current_state()
        if state["side"] == "FLAT":
            print("Position closed.")
            break

        hit = re.hit(state["side"], state["markPrice"], th["tp"], th["sl"])
        print("LIVE:", state["markPrice"], "HIT:", hit)

        if hit:
            resp = close_position(client, SYMBOL, state["positionAmt"])
            print("CLOSE RESP:", resp)
            time.sleep(2)
            verify = pm.current_state()
            print("VERIFY:", verify)
            break

        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()
