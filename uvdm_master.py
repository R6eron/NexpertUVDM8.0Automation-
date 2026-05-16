#!/usr/bin/env python3
import json
import os
import time
import subprocess
from datetime import datetime, UTC

RESET = "\u001B[0m"
RED = "\u001B[31m"
GREEN = "\u001B[32m"
YELLOW = "\u001B[33m"
CYAN = "\u001B[36m"
MAGENTA = "\u001B[35m"
BOLD = "\u001B[1m"

IDENTITY_FILE = "uvdm_identity.json"
LOG_FILE = "execution_log.jsonl"


class UserProfile:
    def __init__(self, key, name, confirms, cooldown, max_pct):
        self.key = key
        self.name = name
        self.confirms = confirms
        self.cooldown = cooldown
        self.max_pct = max_pct


FOUNDER = UserProfile("founder", "XRPeasy Digital Solutions Founder", 2, 5, 0.05)
HEIR = UserProfile("heir", "XRPeasy Digital Solutions Heir", 7, 30, 0.01)


def speak(text):
    try:
        subprocess.run(["termux-tts-speak", "-r", "1.0", "-p", "1.0", text], check=False)
    except Exception:
        pass


def utc_now():
    return datetime.now(UTC).isoformat()


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def parse_money(text):
    s = text.strip().lower().replace(",", "").replace("$", "")
    mult = 1.0
    if s.endswith("k"):
        mult = 1000.0
        s = s[:-1]
    elif s.endswith("m"):
        mult = 1000000.0
        s = s[:-1]
    return float(s) * mult


def prompt_nonempty(label):
    while True:
        v = input(label).strip()
        if v:
            return v
        print("This value cannot be empty, sir.")
        speak("This value cannot be empty, sir.")


def prompt_money(label):
    while True:
        raw = input(label).strip()
        try:
            v = parse_money(raw)
            if v <= 0:
                print("Value must be greater than zero, sir.")
                speak("Value must be greater than zero, sir.")
                continue
            return v
        except ValueError:
            print("Invalid amount, sir. Try 500, 5000, 50k, or 1.2m.")
            speak("Invalid amount, sir.")


def prompt_yes_no(question):
    while True:
        ans = input(f"{question} [yes/no]: ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer yes or no, sir.")
        speak("Please answer yes or no, sir.")


def get_symbol():
    while True:
        symbol = input("Symbol (e.g. XLM/USDT): ").strip().upper()
        if not symbol:
            print("Symbol cannot be empty, sir.")
            speak("Symbol cannot be empty, sir.")
            continue
        if "/" not in symbol and len(symbol) >= 6:
            base = symbol[:-4]
            quote = symbol[-4:]
            symbol = f"{base}/{quote}"
            print(f"Normalising symbol to {symbol}, sir.")
            speak(f"Normalising symbol to {symbol}, sir.")
        return symbol


def get_side():
    while True:
        side = input("Side (buy/sell): ").strip().lower()
        if side in ("buy", "sell"):
            return side
        print("Side must be buy or sell, sir.")
        speak("Side must be buy or sell, sir.")


def ensure_identity():
    data = load_json(IDENTITY_FILE, {})
    if "first_user" not in data:
        print(f"{CYAN}First-user identity setup required, sir.{RESET}")
        speak("First user identity setup required, sir.")
        name = prompt_nonempty("Digital Immortal Name: ")
        number = prompt_nonempty("Digital Immortal Number: ")
        data["first_user"] = {
            "digital_immortal_name": name,
            "digital_immortal_number": number,
            "bound_at": utc_now(),
        }
        save_json(IDENTITY_FILE, data)
        print(f"{GREEN}First user identity bound successfully, sir.{RESET}")
        speak("First user identity bound successfully, sir.")
        print()
    return data["first_user"]


def log_event(user, identity, portfolio, symbol, side, notional, status, reason, limit_value, extra=None):
    record = {
        "ts": utc_now(),
        "user_key": user.key if user else None,
        "user_name": user.name if user else None,
        "digital_immortal_name": identity.get("digital_immortal_name") if identity else None,
        "digital_immortal_number": identity.get("digital_immortal_number") if identity else None,
        "portfolio_value_usd": portfolio,
        "max_trade_pct_of_portfolio": getattr(user, "max_pct", None) if user else None,
        "derived_max_notional_usd": limit_value,
        "symbol": symbol,
        "side": side,
        "requested_notional_usd": notional,
        "status": status,
        "reason": reason,
        "extra": extra or {},
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        print(json.dumps(record), file=f)


def check_limit(user, portfolio, notional):
    limit_value = portfolio * user.max_pct
    if notional > limit_value:
        raise ValueError(
            f"Requested ${notional:,.2f} exceeds "
            f"{user.max_pct * 100:.2f}% of portfolio "
            f"(${limit_value:,.2f}) for {user.name}."
        )
    return limit_value


def xrpl_amm_paper_flow(identity):
    print()
    print(f"{CYAN}XRPL AMM PAPER MODE (no live submission), sir.{RESET}")
    speak("XRPL A M M paper mode, no live submission, sir.")
    xrpl_address = prompt_nonempty("XRPL account address (r...): ")

    print("Select XRPL AMM action:")
    print("1) AMM Deposit (add liquidity)")
    print("2) AMM Withdraw (remove liquidity)")
    print("3) Swap via AMM/DEX")
    speak("Select X R P L A M M action.")
    action_choice = input("> ").strip()

    if action_choice == "1":
        action = "amm_deposit"
    elif action_choice == "2":
        action = "amm_withdraw"
    elif action_choice == "3":
        action = "swap"
    else:
        print("Unknown action, sir. Returning to shell.")
        speak("Unknown action, sir. Returning to shell.")
        return

    amm_pair = prompt_nonempty("AMM pair (e.g. XLM/XRP): ").upper()
    if "/" in amm_pair:
        base_asset, quote_asset = (a.strip() for a in amm_pair.split("/", 1))
    else:
        base_asset, quote_asset = amm_pair, "XRP"

    amount_base = prompt_money(f"Amount in {base_asset}: ")

    print()
    print(f"{MAGENTA}XRPL AMM PAPER PREVIEW{RESET}")
    print(f"Account: {xrpl_address}")
    print(f"Action:  {action}")
    print(f"Pool:    {base_asset}/{quote_asset}")
    print(f"Amount:  {amount_base:,.6f} {base_asset}")
    print()
    speak(f"Preview ready. Action {action}. Pool {base_asset} {quote_asset}. Amount {amount_base:,.2f} {base_asset}.")

    if not prompt_yes_no("Does this preview match your intended XRPL AMM instruction, sir?"):
        print("Understood, sir. XRPL AMM paper instruction cancelled.")
        speak("Understood, sir. X R P L A M M paper instruction cancelled.")
        log_event(
            user=None,
            identity=identity,
            portfolio=0.0,
            symbol=f"{base_asset}/{quote_asset}",
            side=action,
            notional=0.0,
            status="cancelled_preview",
            reason="Operator cancelled XRPL AMM paper preview",
            limit_value=0.0,
            extra={
                "venue": "xrpl_amm",
                "xrpl_address": xrpl_address,
                "amm_action": action,
                "amm_pair": f"{base_asset}/{quote_asset}",
                "amount_base": amount_base,
                "mode": "paper",
            },
        )
        return

    print()
    print("Executing XRPL AMM PAPER instruction now, sir...")
    speak("Executing X R P L A M M paper instruction now, sir.")
    time.sleep(1)
    print("XRPL AMM PAPER execution recorded (no on-ledger submission).")
    speak("X R P L A M M paper execution recorded. No on ledger submission.")

    log_event(
        user=None,
        identity=identity,
        portfolio=0.0,
        symbol=f"{base_asset}/{quote_asset}",
        side=action,
        notional=amount_base,
        status="executed_paper",
        reason="XRPL AMM paper flow completed",
        limit_value=0.0,
        extra={
            "venue": "xrpl_amm",
            "xrpl_address": xrpl_address,
            "amm_action": action,
            "amm_pair": f"{base_asset}/{quote_asset}",
            "amount_base": amount_base,
            "mode": "paper",
        },
    )


def confirm_and_execute(user, identity):
    print()
    portfolio = prompt_money("Current total portfolio value in USD: ")
    symbol = get_symbol()
    side = get_side()

    while True:
        raw = input("Notional in USD (or 'profile' / 'quit'): ").strip().lower()

        if raw in ("quit", "q", "exit"):
            print("Exiting by operator request, sir.")
            speak("Exiting by operator request, sir.")
            log_event(
                user,
                identity,
                portfolio,
                symbol,
                side,
                0.0,
                "aborted",
                "Operator quit at notional prompt",
                portfolio * user.max_pct,
            )
            return

        if raw in ("profile", "p"):
            print("Profile change requested, sir. Restart UVDM MASTER to select a different profile.")
            speak("Profile change requested, sir.")
            log_event(
                user,
                identity,
                portfolio,
                symbol,
                side,
                0.0,
                "aborted",
                "Operator requested profile change",
                portfolio * user.max_pct,
            )
            return

        try:
            notional = parse_money(raw)
            if notional <= 0:
                print("Notional must be greater than zero, sir.")
                speak("Notional must be greater than zero, sir.")
                continue
        except ValueError:
            print("Invalid notional, sir. Try 500, 5000, 50k, or 1.2m.")
            speak("Invalid notional, sir.")
            continue

        try:
            limit_value = check_limit(user, portfolio, notional)
            break
        except ValueError as e:
            limit_value = portfolio * user.max_pct
            print()
            print(f"{RED}Oversized instruction, sir.{RESET}")
            print(str(e))
            print(
                f"Portfolio value: ${portfolio:,.2f} | Policy cap: {user.max_pct * 100:.2f}% "
                f"→ maximum allowed notional: ${limit_value:,.2f}."
            )
            print("Enter a lower notional, type 'profile' to change profile, or 'quit' to exit.")
            speak("Oversized instruction, sir.")
            log_event(
                user,
                identity,
                portfolio,
                symbol,
                side,
                notional,
                "rejected_oversized",
                str(e),
                limit_value,
            )
            continue

    print()
    print(f"{user.name}, bound to {identity['digital_immortal_name']} #{identity['digital_immortal_number']}.")
    print(
        f"Portfolio: ${portfolio:,.2f} | Policy: {user.max_pct * 100:.2f}% "
        f"per instruction (max ${limit_value:,.2f})."
    )
    print(f"You are about to {side} {symbol} for approximately ${notional:,.2f}.")
    speak(f"Confirmation required. {side} {symbol} for approximately {notional:,.2f} dollars.")

    for i in range(1, user.confirms + 1):
        if i < user.confirms:
            q = f"Confirmation {i} of {user.confirms}: are you sure, sir?"
        else:
            q = f"Confirmation {i} of {user.confirms}: this will be your final answer - shall I execute now, sir?"
        if not prompt_yes_no(q):
            print()
            print("Understood, sir. I will NOT execute this instruction.")
            speak("Understood, sir. I will not execute this instruction.")
            log_event(
                user,
                identity,
                portfolio,
                symbol,
                side,
                notional,
                "cancelled",
                f"User declined at confirmation {i}",
                limit_value,
            )
            return
        if i < user.confirms and user.cooldown > 0:
            time.sleep(user.cooldown)

    print()
    print("Executing now, sir...")
    print("Execution complete (stub).")
    speak("Executing now, sir. Execution complete.")
    log_event(
        user,
        identity,
        portfolio,
        symbol,
        side,
        notional,
        "executed_stub",
        "Execution stub completed",
        limit_value,
    )


def main():
    print(f"{BOLD}{CYAN}🎮 UVDM MASTER v3.1 | XRPeasy Digital Solutions (Ltd){RESET}")
    print(f"{MAGENTA}🌾 Flare → XRP → XRPL AMM Flywheel{RESET}")
    print(f"{YELLOW}🔄 24mo → XLS30D | ML Stoploss 8.2% (display only){RESET}")
    print(f"{GREEN}💰 XLM 61K LIVE | Pivot $0.1468{RESET}")
    print(f"{CYAN}📞 Support: XRPeasy Digital Solutions (Ltd) | ronlewis1968@gmail.com{RESET}")
    print("#WhenRonWon")
    print()
    speak("U V D M master online, sir.")

    identity = ensure_identity()

    print("Select venue:")
    print("1) Spot / CEX / DEX (not XRPL AMM-specific)")
    print("2) XRPL AMM (paper mode)")
    speak("Select venue. One for spot. Two for X R P L A M M paper mode.")
    venue_choice = input("> ").strip()

    if venue_choice == "2":
        xrpl_amm_paper_flow(identity)
        return

    print("Select profile:")
    print("1) Founder")
    print("2) XRPeasy Digital Solutions Heir")
    speak("Select profile. One for founder. Two for heir.")
    choice = input("> ").strip()

    if choice == "1":
        user = FOUNDER
    elif choice == "2":
        user = HEIR
    else:
        print("Unknown choice, defaulting to Founder, sir.")
        speak("Unknown choice. Defaulting to founder, sir.")
        user = FOUNDER

    confirm_and_execute(user, identity)


if __name__ == "__main__":
    main()
