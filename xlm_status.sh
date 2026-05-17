#!/data/data/com.termux/files/usr/bin/bash

RED=$'\u001B[0;31m'
GREEN=$'\u001B[0;32m'
YELLOW=$'\u001B[1;33m'
RESET=$'\u001B[0m'

BIAS_DEFENSIVE="${RED}[DEFENSIVE]${RESET}"
ACTION_OBSERVE="${YELLOW}OBSERVE ONLY${RESET}"
ACTION_AGGRESSIVE="${GREEN}CONTROLLED AGGRESSION${RESET}"

printf "
"
printf "XLM STATUS  %b
" "${BIAS_DEFENSIVE}"
printf "
"

printf "Doctrine validation before entry:
"
printf "  If ANY answer = NO   -> %b
" "${ACTION_OBSERVE}"
printf "  If ALL answers = YES -> %b
" "${ACTION_AGGRESSIVE}"
printf "
"

printf "UVDM SIGNALS
"
printf "  wy    -> Wyckoff Re-accumulation (higher lows holding)
"
printf "  wj    -> Volume thrust still favours demand on green legs
"
printf "  voice -> Sharpe Gate 2.1+ active
"
printf "
"

printf "Waiting Game:
"
printf "  If no pre-planned level is in play, DO NOTHING.
"
printf "
"

printf "Pullback Levels (for 3000 USDT scale-in):
"
printf "  • %b -> 1000 USDT (~5952 XLM)
" "${GREEN}0.1680${RESET}"
printf "  • %b -> 1000 USDT (~6098 XLM)
" "${GREEN}0.1640${RESET}"
printf "  • %b -> 1000 USDT (~6250 XLM)
" "${GREEN}0.1600${RESET}"
printf "
"

printf "Take-Profit Ladder (example current long: ~149,715 XLM)
"
printf "  • %b -> 45,000 XLM (first trim into resistance)
" "${YELLOW}0.1740${RESET}"
printf "  • %b -> 45,000 XLM (second trim, de-risk further)
" "${YELLOW}0.1765${RESET}"
printf "  • %b -> 30,000 XLM (final trim before 0.18+ tests)
" "${YELLOW}0.1790${RESET}"
printf "  • Runner -> ~29,715 XLM for potential 0.18-0.20 campaign
"
printf "
"

printf "Risk Guardrails
"
printf "  • Alert  : watch closely if we break below %b
" "${YELLOW}0.1660${RESET}"
printf "  • Cut    : close / hedge if %b fails with volume
" "${RED}0.1500${RESET}"
printf "  • Bias   : CONSTRUCTIVE while 0.16-0.15 holds
"
printf "
"

printf "Doctrine:
"
printf "  I do not predict; I wait for proof.
"
printf "  I do not chase; I position at levels.
"
printf "  I do not hope; I define invalidation first.
"
printf "
"
printf "%b
" "${GREEN}Tape truth: obey. Do not argue.${RESET}"
printf "
"
