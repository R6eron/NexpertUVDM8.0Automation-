#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

if [ -t 1 ]; then
  R=$'\u001B[0m'; RED=$'\u001B[1;31m'; G=$'\u001B[1;32m'; Y=$'\u001B[1;33m'; B=$'\u001B[1;34m'; M=$'\u001B[1;35m'; C=$'\u001B[1;36m'; W=$'\u001B[1;37m'
else
  R=''; RED=''; G=''; Y=''; B=''; M=''; C=''; W=''
fi

say(){ printf '%b
' "$*"; }
speak(){
  if command -v termux-tts-speak >/dev/null 2>&1; then
    termux-tts-speak "$*" >/dev/null 2>&1 || true
  fi
}

asset="${1:-XLM}"
lev="${2:-10x}"
budget="${3:-600}"

asset_up="${asset^^}"
symbol="${asset_up}USDT Perpetual"

if [ "$asset_up" = "XLM" ]; then
  l1_price="0.18520000"; l1_usdt="120.00"
  l2_price="0.18450000"; l2_usdt="210.00"
  l3_price="0.18390000"; l3_usdt="270.00"
  invalidation="0.1838"
  bias="constructive while 0.1838 holds"
  plan="hybrid probe / core / value"
else
  say "${RED}Only XLM is preconfigured right now.${R}"
  exit 1
fi

l1_qty="$(awk -v u="$l1_usdt" -v p="$l1_price" 'BEGIN{printf "%.2f", u/p}')"
l2_qty="$(awk -v u="$l2_usdt" -v p="$l2_price" 'BEGIN{printf "%.2f", u/p}')"
l3_qty="$(awk -v u="$l3_usdt" -v p="$l3_price" 'BEGIN{printf "%.2f", u/p}')"
total_qty="$(awk -v a="$l1_qty" -v b="$l2_qty" -v c="$l3_qty" 'BEGIN{printf "%.2f", a+b+c}')"
notional="$(awk -v b="$budget" -v l="${lev%x}" 'BEGIN{printf "%.2f", b*l}')"

say "${C}#UVDM Wingman TM${R}"
say "${W}Digital Immortal number 001${R}"
say "${C}━━━━━━━━━━━━━━━━━━━━━━━━${R}"
say
say "${W}Symbol${R}   : ${C}${symbol}${R}"
say "${W}Lev${R}      : ${Y}${lev}${R}"
say "${W}Bias${R}     : ${G}${bias}${R}"
say "${W}Plan${R}     : ${Y}${plan}${R}"
say
say "${C}LADDER${R}"
say "  ${W}L1${R}  ${Y}${l1_usdt} USDT${R}  ${C}@ ${l1_price}${R}  ${G}${l1_qty} ${asset_up}${R}  ${W}(probe)${R}"
say "  ${W}L2${R}  ${Y}${l2_usdt} USDT${R}  ${C}@ ${l2_price}${R}  ${G}${l2_qty} ${asset_up}${R}  ${W}(core)${R}"
say "  ${W}L3${R}  ${Y}${l3_usdt} USDT${R}  ${C}@ ${l3_price}${R}  ${G}${l3_qty} ${asset_up}${R}  ${W}(value)${R}"
say
say "${C}TOTALS${R}"
say "${W}Size${R}     : ${G}${total_qty} ${asset_up}${R}"
say "${W}Budget${R}   : ${Y}${budget}.00 USDT${R}"
say "${W}Ntnl${R}     : ${Y}${notional} USDT${R}"
say "${W}Inval${R}    : ${RED}acceptance below ${invalidation}${R}"
say
say "${C}DOCTRINE${R}"
say "${W}  Start small.${R}"
say "${W}  Core at reaction.${R}"
say "${W}  Value at structural low.${R}"
say "${W}  Exit clean if demand fails.${R}"
say "${W}  Process over outcome.${R}"
say
say "${C}BITRUE MANUAL ENTRY${R}"
say "${W}  Set leverage once:${R} ${Y}${lev}${R}"
say "${W}  Enter margin amounts:${R} ${Y}${l1_usdt}${R}, ${Y}${l2_usdt}${R}, ${Y}${l3_usdt}${R} USDT"
say "${W}  Enter limit prices :${R} ${C}${l1_price}${R}, ${C}${l2_price}${R}, ${C}${l3_price}${R}"
say
speak "Jesse here. Bitrue ladder ready. Set leverage to ${lev}. Level one ${l1_usdt} at ${l1_price}. Level two ${l2_usdt} at ${l2_price}. Level three ${l3_usdt} at ${l3_price}. Start small. Add at reaction. Exit clean if demand fails."
