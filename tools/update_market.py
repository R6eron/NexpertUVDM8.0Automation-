#!/usr/bin/env python3
import re
import sys

def update_market(file_path, replacements):
    with open(file_path, 'r') as f:
        content = f.read()

    for old, new in replacements.items():
        content = re.sub(f'^{re.escape(old)}.*$', new, content, flags=re.MULTILINE)

    with open(file_path, 'w') as f:
        f.write(content)

    print(f"✅ Updated {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_market.py <sgb|flr>")
        sys.exit(1)

    asset = sys.argv[1].lower()

    if asset == "sgb":
        file_path = "./output/sgbeasy_market_live.sh"
        replacements = {
            "Bias         :": "Bias         : CONSERVATIVE while 0.00155 holds; governance rail first.",
            "Plan         :": "Plan         : Governance/lottery rail. Target >= 1M; hold, do not add.",
            "Size         :": "Size         : 1093539.65 SGB",
            "Avg Entry    :": "Avg Entry    : 0.00169",
            "Live Price   :": "Live Price   : 0.00185",
            "Side         :": "Side         : spot long",
            "Stop Trigger :": "Stop Trigger : 0.00155",
            "Stop Limit   :": "Stop Limit   : 0.00156",
            "SL / TP Note :": "SL / TP Note : target reached; maintain stack, no new adds.",
            "Mode         :": "Mode         : spot",
            "Leverage     :": "Leverage     : none",
            "Notional USD :": "Notional USD : spot_stack",
            "Asset        :": "Asset        : SGB (spot, target reached)",
            "Setup        :": "Setup        : SPOT_HOLD",
            "Level        :": "Level        : target_met",
            "Voice Cmd    :": "Voice Cmd    : maintain SGB stack; route new spot flow to FLR.",
            "Watcher Note :": "Watcher Note : RISK: target achieved | PROCESS: hold | ACTION: no new adds | EMOTION: calm, detached, process over outcome | redirect accumulation to FLR."
        }
    elif asset == "flr":
        file_path = "./output/flreasy_market_live.sh"
        replacements = {
            "Bias         :": "Bias         : CONSTRUCTIVE while 0.00620 holds; income backbone intact.",
            "Plan         :": "Plan         : Income/protocol backbone. Accumulate spot toward 1M.",
            "Size         :": "Size         : 401378 WFLR",
            "Avg Entry    :": "Avg Entry    : 0.00653",
            "Live Price   :": "Live Price   : 0.00654",
            "Side         :": "Side         : spot long",
            "Stop Trigger :": "Stop Trigger : 0.00620",
            "Stop Limit   :": "Stop Limit   : 0.00621",
            "SL / TP Note :": "SL / TP Note : below 1M target; continue accumulation, no leverage.",
            "Mode         :": "Mode         : spot",
            "Leverage     :": "Leverage     : none",
            "Notional USD :": "Notional USD : spot_stack",
            "Asset        :": "Asset        : FLR (spot)",
            "Setup        :": "Setup        : SPOT_ACCUMULATION",
            "Level        :": "Level        : 1M_target",
            "Voice Cmd    :": "Voice Cmd    : accumulate FLR spot until 1M, no leverage.",
            "Watcher Note :": "Watcher Note : RISK: below 1M target | PROCESS: accumulate | ACTION: direct new spot flow here | EMOTION: calm, detached, process over outcome | SGB already above target."
        }
    else:
        print("Usage: python update_market.py <sgb|flr>")
        sys.exit(1)

    update_market(file_path, replacements)
