# XRPeasy Termux Bootstrap README

This README preserves the current Jesse/Ron mobile voice architecture for rebuilding the stack on a new Android device.

## Core idea

The stack uses Termux on Android as a lightweight voice command surface. Speech is captured, normalized to lowercase, filtered for recognizer noise, and routed through a Bash case tree into Jesse, Ron, and asset-specific command handlers.

## Voice roles

- Jesse: behavioural coach, doctrine, patience, confirmation.
- Ron: systems operator, command acknowledgements, engine-room state.
- Butt Reynolds: Jesse's spiritual coach in the narrative layer.

## Working checkpoint

- Jesse and Ron wake by name.
- XLM routing works with fuzzy phrase variants.
- BTC routing works through `btc`, `b t c`, and `bitcoin`.
- `error_no_match` is known recognizer noise and should be filtered from logs.
- FLR / SGB is the next planned rail.

## Core loop pattern

```bash
while true; do
  CMD="$(termux-speech-to-text 2>/dev/null | tr '[:upper:]' '[:lower:]')"

  [ "$CMD" != "error: error_no_match" ] && \
  [ "$CMD" != "error: error_network" ] && \
  echo "HEARD: $CMD"

  [ -z "$CMD" ] && continue

  case "$CMD" in
    *wake*up*jesse*|*jesse*|*jessie*)
      jesse_say "Jesse online. Stay sharp and wait for confirmation."
      ;;

    *ron*wake*up*|*wake*up*ron*|*ron*)
      ron_say "Ron online. Systems are up."
      ;;

    *price*xlm*|*xlm*price*|*ixlm*|*xlm*phil*price*|*lm*fill*price*)
      ron_say "X L M price request logged. Pulling your X L M report now."
      xlm
      ;;

    *btc*|*b t c*|*bitcoin*)
      ron_say "B T C is the macro driver. Any new deployment gets checked against its structure first."
      btc
      ;;
  esac
done
