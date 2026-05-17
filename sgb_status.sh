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
printf "SGB STATUS  %b
" "${BIAS_DEFENSIVE}"
printf "
"

printf "Doctrine validation before deployment:
"
printf "  If ANY rail / liquidity / structure answer = NO   -> %b
" "${ACTION_OBSERVE}"
printf "  If ALL rails clean and signals aligned            -> %b
" "${ACTION_AGGRESSIVE}"
printf "
"

printf "UVDM SIGNALS (SGB rail)
"
printf "  sg    -> Songbird structure holding above key demand
"
printf "  liq   -> Liquidity conditions acceptable for rotation
"
printf "  voice -> Machine gate aligned with SGB thesis
"
printf "
"

printf "Waiting Game:
"
printf "  If no pre-planned SGB level is in play, DO NOTHING.
"
printf "
"

printf "Pullback Levels (example for 3000 USDT scale-in):
"
printf "  • %b -> 1000 USDT (starter fill)
" "${GREEN}LEVEL_1${RESET}"
printf "  • %b -> 1000 USDT (core fill)
"    "${GREEN}LEVEL_2${RESET}"
printf "  • %b -> 1000 USDT (final fill)
"   "${GREEN}LEVEL_3${RESET}"
printf "
"

printf "Take-Profit Ladder (example SGB stack):
"
printf "  • %b -> first trim into resistance
"        "${YELLOW}TP_1${RESET}"
printf "  • %b -> second trim, de-risk rail
"         "${YELLOW}TP_2${RESET}"
printf "  • %b -> final trim before extension tests
" "${YELLOW}TP_3${RESET}"
printf "  • Runner -> remaining SGB for protocol upside flywheel
"
printf "
"

printf "Risk Guardrails
"
printf "  • Alert  : watch closely if we break below %b
" "${YELLOW}ALERT_LEVEL${RESET}"
printf "  • Cut    : close / hedge if %b fails with volume
" "${RED}INVALIDATION${RESET}"
printf "  • Bias   : CONSTRUCTIVE while core SGB demand zone holds
"
printf "
"

printf "Doctrine:
"
printf "  %b
" "${YELLOW}I do not front-run thin books; I wait for clean fills.${RESET}"
printf "  %b
" "${YELLOW}I do not confuse volatility with edge.${RESET}"
printf "  %b
" "${YELLOW}I do not force deployment; I obey structure first.${RESET}"
printf "
"
printf "  %b
" "${GREEN}Tape truth (SGB rail): obey. Do not argue.${RESET}"
printf "
"
