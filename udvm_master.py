#!/usr/bin/env python3
import time

# ANSI colour codes
RESET = "\u001B[0m"
RED = "\u001B[31m"
GREEN = "\u001B[32m"
YELLOW = "\u001B[33m"
CYAN = "\u001B[36m"
MAGENTA = "\u001B[35m"
BOLD = "\u001B[1m"

# Banner
print(f"{BOLD}{CYAN}🎮 UVDM MASTER v1.0 | XRPeasy Digital Solutions (Ltd){RESET}")
print(f"{MAGENTA}🌾 Flare → XRP → XRPL AMM Flywheel{RESET}")
print(f"{YELLOW}🔄 24mo → XLS30D | ML Stoploss 8.2% (display only){RESET}")
print(f"{GREEN}💰 XLM 61K LIVE | Pivot $0.1468{RESET}")
print(f"{CYAN}📞 Support: XRPeasy Digital Solutions (Ltd) | ronlewis1968@gmail.com{RESET}")
print("#WhenRonWon")
print()


class UserProfile:
    def __init__(
        self,
        name,
        confirmations_required,
        cooldown_seconds_between_confirms,
        max_notional_per_trade_usd,
    ):
        self.name = name
        self.confirmations_required = confirmations_required
        self.cooldown_seconds_between_confirms = cooldown_seconds_between_confirms
        self.max_notional_per_trade_usd = max_notional_per_trade_usd


FOUNDER = UserProfile(
    name="XRPeasy Digital Solutions Founder",
    confirmations_required=2,
    cooldown_seconds_between_confirms=5,
    max_notional_per_trade_usd=5000.0,
)

HEIR = UserProfile(
    name="XRPeasy Digital Solutions Heir",
    confirmations_required=7,
    cooldown_seconds_between_confirms=30,
    max_notional_per_trade_usd=500.0,
)


def prompt_yes_no(question):
    while True:
        ans = input(f"{question} [yes/no]: ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer yes or no, sir.")


def check_size_limit(user, notional_usd):
    if notional_usd > user.max_notional_per_trade_usd:
        raise ValueError(
            f"Requested ${notional_usd:.2f} exceeds limit "
            f"${user.max_notional_per_trade_usd:.2f} for {user.name}."
        )


def confirm_and_execute_shell(user):
    symbol = input("Symbol (e.g. XLM/USDT): ").strip().upper()
    side = input("Side (buy/sell): ").strip().lower()
    notional = float(input("Notional in USD: ").strip())

    check_size_limit(user, notional)

    print()
    print(
        f"{user.name}, you are about to {side} {symbol} "
        f"for approximately ${notional:,.2f}."
    )

    if user.confirmations_required <= 0:
        print("Policy is infinite confirmations; I will never execute, sir.")
        return

    for i in range(1, user.confirmations_required + 1):
        if i < user.confirmations_required:
            question = (
                f"Confirmation {i} of {user.confirmations_required}: "
                f"are you sure, sir?"
            )
        else:
            question = (
                f"Confirmation {i} of {user.confirmations_required}: "
                f"this will be your final answer - shall I execute now, sir?"
            )

        if not prompt_yes_no(question):
            print()
            print("Understood, sir. I will NOT execute this instruction.")
            return

        if (
            i < user.confirmations_required
            and user.cooldown_seconds_between_confirms > 0
        ):
            time.sleep(user.cooldown_seconds_between_confirms)

    print()
    print("Executing now, sir...")
    # TODO: plug real XRPL / CEX / AMM call here
    print("Execution complete (stub).")


def main():
    print("Select profile:")
    print("1) Founder")
    print("2) XRPeasy Digital Solutions Heir")
    choice = input("> ").strip()

    if choice == "1":
        user = FOUNDER
    elif choice == "2":
        user = HEIR
    else:
        print("Unknown choice, defaulting to Founder, sir.")
        user = FOUNDER

    confirm_and_execute_shell(user)


if __name__ == "__main__":
    main()