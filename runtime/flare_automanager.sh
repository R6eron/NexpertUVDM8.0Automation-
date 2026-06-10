#!/data/data/com.termux/files/usr/bin/bash

cd "$HOME/NexpertUVDM-Automation" || exit 1

export AUTO_WRAP_ENABLED="${AUTO_WRAP_ENABLED:-1}"
export AUTO_DELEGATE_ENABLED="${AUTO_DELEGATE_ENABLED:-1}"
export FLARE_RPC_URL="${FLARE_RPC_URL:-https://flare-api.flare.network/ext/C/rpc}"
export FLARE_AGENT_ADDRESS="${FLARE_AGENT_ADDRESS:-0x1234567890123456789012345678901234567890}"
export FLR_GAS_RESERVE="${FLR_GAS_RESERVE:-5}"
export FTSO_DELEGATE_SPLIT="${FTSO_DELEGATE_SPLIT:-50/50}"
export FTSO_PROVIDER_1="${FTSO_PROVIDER_1:-0xProviderAddress1}"
export FTSO_PROVIDER_2="${FTSO_PROVIDER_2:-0xProviderAddress2}"

echo "[LIVERMORE CAPITAL] FLARE AUTOWRAP/DELEGATE | $(date -u +'%H:%M GMT')"

python3 - <<'PYCODE'
import os
from datetime import datetime, timezone
from web3 import Web3

FLARE_RPC_URL = os.getenv("FLARE_RPC_URL", "https://flare-api.flare.network/ext/C/rpc")
AGENT_ADDRESS = Web3.to_checksum_address(os.getenv("FLARE_AGENT_ADDRESS"))
GAS_RESERVE_FLR = float(os.getenv("FLR_GAS_RESERVE", "5"))
AUTO_WRAP_ENABLED = os.getenv("AUTO_WRAP_ENABLED", "1") == "1"
AUTO_DELEGATE_ENABLED = os.getenv("AUTO_DELEGATE_ENABLED", "1") == "1"
FTSO_PROVIDER_1 = os.getenv("FTSO_PROVIDER_1")
FTSO_PROVIDER_2 = os.getenv("FTSO_PROVIDER_2")

w3 = Web3(Web3.HTTPProvider(FLARE_RPC_URL))

def get_native_balance():
    return w3.eth.get_balance(AGENT_ADDRESS) / 10**18

balance = get_native_balance()
excess = balance - GAS_RESERVE_FLR
now = datetime.now(timezone.utc).isoformat()

print(f"[{now}] rpc={FLARE_RPC_URL}")
print(f"[{now}] address={AGENT_ADDRESS}")
print(f"[{now}] native_flr={balance:.6f}")
print(f"[{now}] gas_reserve_flr={GAS_RESERVE_FLR:.6f}")

if AUTO_WRAP_ENABLED:
    if excess > 0:
        print(f"[{now}] wrap_candidate_flr={excess:.6f}")
    else:
        print(f"[{now}] no_wrap_excess")
else:
    print(f"[{now}] auto_wrap_disabled")

if AUTO_DELEGATE_ENABLED:
    print(f"[{now}] delegate_targets={[FTSO_PROVIDER_1, FTSO_PROVIDER_2]}")
else:
    print(f"[{now}] auto_delegate_disabled")
PYCODE
