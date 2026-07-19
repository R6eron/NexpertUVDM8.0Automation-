#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional

RESET = "\u001B[0m"
RED = "\u001B[31m"
GREEN = "\u001B[32m"
YELLOW = "\u001B[33m"
CYAN = "\u001B[36m"
MAGENTA = "\u001B[35m"
WHITE = "\u001B[97m"
BOLD = "\u001B[1m"
GOLD = "\u001B[93m"

APP_NAME = "UVDM MASTER"
APP_VERSION = "4.0-skeleton"
ROOT = Path(os.getenv("UVDM_ROOT", str(Path.home() / "NexpertUVDM-Automation")))
CONFIG_DIR = ROOT / "config"
VOICE_DIR = ROOT / "voice"
LOG_DIR = ROOT / "logs"
OUTPUT_DIR = ROOT / "output"

STATE_PATH = Path(os.getenv("UVDM_STATE_FILE", str(Path.home() / ".xrpeasy_onboarding_state.json")))
LEGACY_IDENTITY_FILE = ROOT / "uvdm_identity.json"
EXECUTION_LOG = ROOT / "execution_log.jsonl"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
VOICE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class UserProfile:
    key: str
    name: str
    confirms: int
    cooldown: int
    max_pct: float


FOUNDER = UserProfile("founder", "XRPeasy Digital Solutions Founder", 2, 5, 0.05)
HEIR = UserProfile("heir", "XRPeasy Digital Solutions Heir", 7, 30, 0.01)


class IdentityManager:
    def __init__(self, state_path: Path = STATE_PATH, legacy_path: Path = LEGACY_IDENTITY_FILE):
        self.state_path = state_path
        self.legacy_path = legacy_path

    def load_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return default
        return default

    def save_json(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_identity(self) -> Dict[str, Any]:
        state = self.load_json(self.state_path, {})
        if state.get("identity_bound"):
            return {
                "source": "state",
                "digital_immortal_name": state.get("display_identity", "UVDM Bound Identity"),
                "digital_immortal_number": state.get("immortal_id", "uvdm-unset"),
                "first_user_hex": state.get("first_user_hex"),
                "device_label": state.get("device_label"),
                "state": state,
            }

        legacy = self.load_json(self.legacy_path, {})
        first_user = legacy.get("first_user")
        if first_user:
            return {
                "source": "legacy",
                "digital_immortal_name": first_user.get("digital_immortal_name", "UVDM Legacy User"),
                "digital_immortal_number": first_user.get("digital_immortal_number", "legacy-unset"),
                "first_user_hex": None,
                "device_label": None,
                "state": legacy,
            }

        return self.bootstrap_legacy_identity()

    def bootstrap_legacy_identity(self) -> Dict[str, Any]:
        print(f"{CYAN}First-user identity setup required, sir.{RESET}")
        name = prompt_nonempty("Digital Immortal Name: ")
        number = prompt_nonempty("Digital Immortal Number: ")
        data = {
            "first_user": {
                "digital_immortal_name": name,
                "digital_immortal_number": number,
                "bound_at": utc_now(),
            }
        }
        self.save_json(self.legacy_path, data)
        return {
            "source": "legacy",
            "digital_immortal_name": name,
            "digital_immortal_number": number,
            "first_user_hex": None,
            "device_label": None,
            "state": data,
        }


class AuditLogger:
    def __init__(self, log_path: Path = EXECUTION_LOG):
        self.log_path = log_path

    def log_event(
        self,
        user: Optional[UserProfile],
        identity: Optional[Dict[str, Any]],
        portfolio: float,
        symbol: str,
        side: str,
        notional: float,
        status: str,
        reason: str,
        limit_value: float,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
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
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


class TTS:
    @staticmethod
    def speak(text: str) -> None:
        try:
            if shutil.which("termux-tts-speak"):
                subprocess.run(["termux-tts-speak", "-r", "1.0", "-p", "1.0", text], check=False)
        except Exception:
            pass


class MasterConsole:
    def __init__(self, identity_manager: IdentityManager, audit: AuditLogger):
        self.identity_manager = identity_manager
        self.audit = audit
        self.identity = self.identity_manager.get_identity()

    def show_banner(self) -> None:
        print(f"{BOLD}{CYAN}UVDM Wingman TM 2025{RESET}")
        print(f"{WHITE}{self.identity['digital_immortal_name']}{RESET}")
        print(f"{WHITE}{self.identity['digital_immortal_number']}{RESET}")
        print(f"{GOLD}Process over outcome..{RESET}")
        print(f"{GOLD}No fear or Greed if you hope to succeed..{RESET}")
        print(f"{GREEN}Tape is the only source of Truth{RESET}")
        print(f"{MAGENTA}{APP_NAME} v{APP_VERSION}{RESET}")
        print("")
        TTS.speak("U V D M master online, sir.")

    def select_venue(self) -> str:
        print("Select venue:")
        print("1) Spot / CEX / DEX")
        print("2) XRPL AMM (paper mode)")
        print("3) Live execution router")
        ans = input("> ").strip()
        if ans == "2":
            return "xrpl_amm"
        if ans == "3":
            return "live_router"
        return "spot"

    def select_profile(self) -> UserProfile:
        print("Select profile:")
        print("1) Founder")
        print("2) XRPeasy Digital Solutions Heir")
        ans = input("> ").strip()
        if ans == "2":
            return HEIR
        return FOUNDER

    def check_limit(self, user: UserProfile, portfolio: float, notional: float) -> float:
        limit_value = portfolio * user.max_pct
        if notional > limit_value:
            raise ValueError(
                f"Requested ${notional:,.2f} exceeds {user.max_pct * 100:.2f}% of portfolio "
                f"(${limit_value:,.2f}) for {user.name}."
            )
        return limit_value

    def confirm_and_build_instruction(self, user: UserProfile) -> Optional[Dict[str, Any]]:
        print("")
        portfolio = prompt_money("Current total portfolio value in USD: ")
        symbol = get_symbol()
        side = get_side()

        while True:
            raw = input("Notional in USD (or 'profile' / 'quit'): ").strip().lower()
            if raw in ("quit", "q", "exit"):
                self.audit.log_event(user, self.identity, portfolio, symbol, side, 0.0, "aborted", "Operator quit at notional prompt", portfolio * user.max_pct)
                return None
            if raw in ("profile", "p"):
                self.audit.log_event(user, self.identity, portfolio, symbol, side, 0.0, "aborted", "Operator requested profile change", portfolio * user.max_pct)
                return {"action": "profile_change"}
            try:
                notional = parse_money(raw)
                if notional <= 0:
                    print("Notional must be greater than zero, sir.")
                    continue
            except ValueError:
                print("Invalid notional, sir. Try 500, 5000, 50k, or 1.2m.")
                continue

            try:
                limit_value = self.check_limit(user, portfolio, notional)
                break
            except ValueError as e:
                limit_value = portfolio * user.max_pct
                print(f"{RED}Oversized instruction, sir.{RESET}")
                print(str(e))
                self.audit.log_event(user, self.identity, portfolio, symbol, side, notional, "rejected_oversized", str(e), limit_value)

        print("")
        print(f"{user.name}, bound to {self.identity['digital_immortal_name']} #{self.identity['digital_immortal_number']}.")
        print(f"Portfolio: ${portfolio:,.2f} | Policy: {user.max_pct * 100:.2f}% per instruction (max ${limit_value:,.2f}).")
        print(f"You are about to {side} {symbol} for approximately ${notional:,.2f}.")
        TTS.speak(f"Confirmation required. {side} {symbol} for approximately {notional:,.2f} dollars.")

        for i in range(1, user.confirms + 1):
            q = f"Confirmation {i} of {user.confirms}: execute, sir?" if i < user.confirms else f"Confirmation {i} of {user.confirms}: final answer - execute now, sir?"
            if not prompt_yes_no(q):
                self.audit.log_event(user, self.identity, portfolio, symbol, side, notional, "cancelled", f"User declined at confirmation {i}", limit_value)
                return None
            if i < user.confirms and user.cooldown > 0:
                time.sleep(user.cooldown)

        instruction = {
            "status": "confirmed",
            "venue": "spot",
            "user_key": user.key,
            "user_name": user.name,
            "identity_name": self.identity["digital_immortal_name"],
            "identity_number": self.identity["digital_immortal_number"],
            "portfolio_usd": portfolio,
            "max_pct": user.max_pct,
            "limit_value_usd": limit_value,
            "symbol": symbol,
            "side": side,
            "notional_usd": notional,
            "ts": utc_now(),
        }
        self.audit.log_event(user, self.identity, portfolio, symbol, side, notional, "confirmed", "Instruction confirmed by operator", limit_value, extra=instruction)
        return instruction

    def xrpl_amm_paper_flow(self) -> None:
        print("")
        print(f"{CYAN}XRPL AMM PAPER MODE (no live submission), sir.{RESET}")
        xrpl_address = prompt_nonempty("XRPL account address (r...): ")
        print("Select XRPL AMM action:")
        print("1) AMM Deposit")
        print("2) AMM Withdraw")
        print("3) Swap via AMM/DEX")
        action_choice = input("> ").strip()
        action_map = {"1": "amm_deposit", "2": "amm_withdraw", "3": "swap"}
        action = action_map.get(action_choice)
        if not action:
            print("Unknown action, sir. Returning to shell.")
            return
        amm_pair = prompt_nonempty("AMM pair (e.g. XLM/XRP): ").upper()
        base_asset, quote_asset = (amm_pair.split("/", 1) + ["XRP"])[:2] if "/" in amm_pair else (amm_pair, "XRP")
        amount_base = prompt_money(f"Amount in {base_asset}: ")
        print(f"{MAGENTA}XRPL AMM PAPER PREVIEW{RESET}")
        print(f"Account: {xrpl_address}")
        print(f"Action:  {action}")
        print(f"Pool:    {base_asset}/{quote_asset}")
        print(f"Amount:  {amount_base:,.6f} {base_asset}")
        if not prompt_yes_no("Does this preview match your intended XRPL AMM instruction, sir?"):
            self.audit.log_event(None, self.identity, 0.0, f"{base_asset}/{quote_asset}", action, 0.0, "cancelled_preview", "Operator cancelled XRPL AMM paper preview", 0.0, extra={"venue": "xrpl_amm", "xrpl_address": xrpl_address, "mode": "paper"})
            return
        self.audit.log_event(None, self.identity, 0.0, f"{base_asset}/{quote_asset}", action, amount_base, "executed_paper", "XRPL AMM paper flow completed", 0.0, extra={"venue": "xrpl_amm", "xrpl_address": xrpl_address, "mode": "paper"})
        print("XRPL AMM PAPER execution recorded (no on-ledger submission).")


class Router:
    def __init__(self, root: Path = ROOT):
        self.root = root

    def route_live_execution(self) -> None:
        print(f"{CYAN}Live execution router placeholder{RESET}")
        print("Hook this to uvdm_live.py, det_trigger.py, wyckoff_trend_wrapper_v2.py, or guard modules.")

    def route_confirmed_instruction(self, instruction: Dict[str, Any]) -> None:
        print(f"{GREEN}Instruction confirmed and ready for downstream routing.{RESET}")
        print(json.dumps(instruction, indent=2))
        print("Next hook: map symbol/venue/mode into live deploy adapters.")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def parse_money(text: str) -> float:
    s = text.strip().lower().replace(",", "").replace("$", "")
    mult = 1.0
    if s.endswith("k"):
        mult = 1000.0
        s = s[:-1]
    elif s.endswith("m"):
        mult = 1000000.0
        s = s[:-1]
    return float(s) * mult


def prompt_nonempty(label: str) -> str:
    while True:
        v = input(label).strip()
        if v:
            return v
        print("This value cannot be empty, sir.")
        TTS.speak("This value cannot be empty, sir.")


def prompt_money(label: str) -> float:
    while True:
        raw = input(label).strip()
        try:
            v = parse_money(raw)
            if v <= 0:
                print("Value must be greater than zero, sir.")
                continue
            return v
        except ValueError:
            print("Invalid amount, sir. Try 500, 5000, 50k, or 1.2m.")


def prompt_yes_no(question: str) -> bool:
    while True:
        ans = input(f"{question} [yes/no]: ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer yes or no, sir.")


def get_symbol() -> str:
    while True:
        symbol = input("Symbol (e.g. XLM/USDT): ").strip().upper()
        if not symbol:
            print("Symbol cannot be empty, sir.")
            continue
        if "/" not in symbol and len(symbol) >= 6:
            base = symbol[:-4]
            quote = symbol[-4:]
            symbol = f"{base}/{quote}"
            print(f"Normalising symbol to {symbol}, sir.")
        return symbol


def get_side() -> str:
    while True:
        side = input("Side (buy/sell): ").strip().lower()
        if side in ("buy", "sell"):
            return side
        print("Side must be buy or sell, sir.")


def main() -> int:
    identity_manager = IdentityManager()
    audit = AuditLogger()
    console = MasterConsole(identity_manager, audit)
    router = Router()

    console.show_banner()
    venue = console.select_venue()

    if venue == "xrpl_amm":
        console.xrpl_amm_paper_flow()
        return 0

    if venue == "live_router":
        router.route_live_execution()
        return 0

    user = console.select_profile()
    instruction = console.confirm_and_build_instruction(user)
    if not instruction:
        return 0
    if instruction.get("action") == "profile_change":
        user = console.select_profile()
        instruction = console.confirm_and_build_instruction(user)
        if not instruction or instruction.get("action") == "profile_change":
            return 0

    router.route_confirmed_instruction(instruction)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())