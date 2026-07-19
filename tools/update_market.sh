#!/usr/bin/env bash
# Automated sed updates for market live files

ASSET=$1
FILE="./output/${ASSET}easy_market_live.sh"

if [ ! -f "$FILE" ]; then
  echo "File not found: $FILE"
  exit 1
fi

case $ASSET in
  sgb)
    sed -i \
      -e 's|^Bias         : .*|Bias         : CONSERVATIVE while 0.00155 holds; governance rail first.|' \
      -e 's|^Plan         : .*|Plan         : Governance/lottery rail. Target >= 1M; hold, do not add.|' \
      -e 's|^Size         : .*|Size         : 1093539.65 SGB|' \
      -e 's|^Avg Entry    : .*|Avg Entry    : 0.00169|' \
      -e 's|^Live Price   : .*|Live Price   : 0.00185|' \
      -e 's|^Side         : .*|Side         : spot long|' \
      -e 's|^Stop Trigger : .*|Stop Trigger : 0.00155|' \
      -e 's|^Stop Limit   : .*|Stop Limit   : 0.00156|' \
      -e 's|^SL / TP Note : .*|SL / TP Note : target reached; maintain stack, no new adds.|' \
      -e 's|^Mode         : .*|Mode         : spot|' \
      -e 's|^Leverage     : .*|Leverage     : none|' \
      -e 's|^Notional USD : .*|Notional USD : spot_stack|' \
      -e 's|^Asset        : .*|Asset        : SGB (spot, target reached)|' \
      -e 's|^Setup        : .*|Setup        : SPOT_HOLD|' \
      -e 's|^Level        : .*|Level        : target_met|' \
      -e 's|^Voice Cmd    : .*|Voice Cmd    : maintain SGB stack; route new spot flow to FLR.|' \
      -e 's|^Watcher Note : .*|Watcher Note : RISK: target achieved | PROCESS: hold | ACTION: no new adds | EMOTION: calm, detached, process over outcome | redirect accumulation to FLR.|' \
      "$FILE"
    ;;
  flr)
    sed -i \
      -e 's|^Bias         : .*|Bias         : CONSTRUCTIVE while 0.00620 holds; income backbone intact.|' \
      -e 's|^Plan         : .*|Plan         : Income/protocol backbone. Accumulate spot toward 1M.|' \
      -e 's|^Size         : .*|Size         : 401378 WFLR|' \
      -e 's|^Avg Entry    : .*|Avg Entry    : 0.00653|' \
      -e 's|^Live Price   : .*|Live Price   : 0.00654|' \
      -e 's|^Side         : .*|Side         : spot long|' \
      -e 's|^Stop Trigger : .*|Stop Trigger : 0.00620|' \
      -e 's|^Stop Limit   : .*|Stop Limit   : 0.00621|' \
      -e 's|^SL / TP Note : .*|SL / TP Note : below 1M target; continue accumulation, no leverage.|' \
      -e 's|^Mode         : .*|Mode         : spot|' \
      -e 's|^Leverage     : .*|Leverage     : none|' \
      -e 's|^Notional USD : .*|Notional USD : spot_stack|' \
      -e 's|^Asset        : .*|Asset        : FLR (spot)|' \
      -e 's|^Setup        : .*|Setup        : SPOT_ACCUMULATION|' \
      -e 's|^Level        : .*|Level        : 1M_target|' \
      -e 's|^Voice Cmd    : .*|Voice Cmd    : accumulate FLR spot until 1M, no leverage.|' \
      -e 's|^Watcher Note : .*|Watcher Note : RISK: below 1M target | PROCESS: accumulate | ACTION: direct new spot flow here | EMOTION: calm, detached, process over outcome | SGB already above target.|' \
      "$FILE"
    ;;
  *)
    echo "Usage: update_market.sh <sgb|flr>"
    exit 1
    ;;
esac

echo "✅ $ASSET market file updated."
chmod +x "$FILE"
