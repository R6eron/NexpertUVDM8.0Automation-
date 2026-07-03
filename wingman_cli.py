#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

USERS_FILE = Path("wingman_users.json")
PORTFOLIO_FILE = Path("portfolio_context.json")
PREFS_FILE = Path("wingman_prefs.json")


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json_file(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return default
    return default


def save_json_file(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def load_users():
    return load_json_file(USERS_FILE, {})


def save_users(data):
    save_json_file(USERS_FILE, data)


def load_prefs():
    return load_json_file(
        PREFS_FILE,
        {
            "voice_enabled": True,
            "voice_rate": "0.92",
            "voice_pitch": "1.0",
            "voice_engine": "",
            "voice_stream": "",
        },
    )


def save_prefs(data):
    save_json_file(PREFS_FILE, data)


def detect_tts_engine():
    prefs = load_prefs()
    if prefs.get("voice_engine"):
        return prefs["voice_engine"]
    try:
        out = subprocess.check_output(["termux-tts-engines"], text=True)
        if "com.google.android.tts" in out:
            return "com.google.android.tts"
    except Exception:
        pass
    return None


def speak(text):
    prefs = load_prefs()
    if not prefs.get("voice_enabled", True):
        return
    try:
        cmd = [
            "termux-tts-speak",
            "-r", str(prefs.get("voice_rate", "0.92")),
            "-p", str(prefs.get("voice_pitch", "1.0")),
        ]
        engine = detect_tts_engine()
        if engine:
            cmd += ["-e", engine]
        stream = str(prefs.get("voice_stream", "")).strip()
        if stream:
            cmd += ["-s", stream]
        cmd.append(text)
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception:
        pass


def ask(prompt, default="", why=""):
    audible = prompt
    if why:
        audible += f". {why}"
    if default:
        audible += f". Default is {default}."
    print(f"[voice] {audible}")
    speak(audible)
    try:
        raw = input(f"{prompt}" + (f" [{default}]" if default else "") + ": ").strip()
    except KeyboardInterrupt:
        print("\
cancelled")
        raise SystemExit(130)
    return raw if raw else default


def user_add_cli(args):
    data = load_users()
    alias = args.alias or ask("Alias / handle")
    if not alias:
        print("alias required")
        return 1
    prev = data.get(alias, {})
    data[alias] = {
        "alias": alias,
        "updated_at": utc_now(),
        "notes": args.notes or prev.get("notes", ""),
    }
    save_users(data)
    print(f"saved user -> {USERS_FILE}")
    return 0


def user_show_cli(args):
    data = load_users()
    if args.alias:
        item = data.get(args.alias)
        if not item:
            print("user not found")
            return 1
        print(json.dumps(item, indent=2, sort_keys=True))
        return 0
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def exchange_add_cli(args):
    print("exchange add placeholder")
    return 0


def exchange_list_cli(args):
    print("exchange list placeholder")
    return 0


def trading_brief_cli(args):
    data = load_users()
    alias = ask("Alias / handle")
    if not alias:
        print("alias required")
        return 1

    prev = data.get(alias, {})
    identity = prev.get("identity", {})
    capital_risk = prev.get("capital_risk", {})
    style_assets = prev.get("style_assets", {})
    psychology = prev.get("psychology", {})
    goals = prev.get("goals_3_6_months", {})

    brief = {
        "updated_at": utc_now(),
        "identity": {
            "alias": alias,
            "time_zone": ask("Time zone", identity.get("time_zone", "")),
            "platforms": ask("Platforms", identity.get("platforms", "")),
            "devices": ask("Devices", identity.get("devices", "")),
        },
        "capital_risk": {
            "total_trading_capital_usdt": ask("Total trading capital (USDT)", capital_risk.get("total_trading_capital_usdt", "")),
            "typical_deploy_per_campaign_pct": ask("Typical deploy per campaign (%)", capital_risk.get("typical_deploy_per_campaign_pct", "")),
            "max_leverage": ask("Max leverage (futures)", capital_risk.get("max_leverage", "")),
            "hard_daily_loss_limit": ask("Hard daily loss limit", capital_risk.get("hard_daily_loss_limit", "")),
            "comfortable_max_drawdown_pct": ask("Comfortable max drawdown (%)", capital_risk.get("comfortable_max_drawdown_pct", "")),
        },
        "style_assets": {
            "main_instruments": ask("Main instruments", style_assets.get("main_instruments", "")),
            "timeframes": ask("Timeframes", style_assets.get("timeframes", "")),
            "preferred_patterns": ask("Preferred patterns", style_assets.get("preferred_patterns", "")),
        },
        "psychology": {
            "biggest_recurring_issue": ask("Biggest recurring issue", psychology.get("biggest_recurring_issue", "")),
            "recent_painful_trade": ask("Recent painful trade", psychology.get("recent_painful_trade", "")),
            "recent_by_the_book_trade": ask("Recent by-the-book trade", psychology.get("recent_by_the_book_trade", "")),
            "current_journaling_habit": ask("Current journaling habit", psychology.get("current_journaling_habit", "")),
        },
        "goals_3_6_months": {
            "outcome_goal": ask("Outcome goal", goals.get("outcome_goal", "")),
            "process_goal": ask("Process goal", goals.get("process_goal", "")),
            "education_goal": ask("Education goal", goals.get("education_goal", "")),
        },
    }

    data[alias] = brief
    save_users(data)
    print(f"saved brief -> {USERS_FILE}")
    return 0


def portfolio_cli(args):
    if not PORTFOLIO_FILE.exists():
        print(f"portfolio file not found -> {PORTFOLIO_FILE}")
        return 1
    try:
        data = json.loads(PORTFOLIO_FILE.read_text())
    except Exception as e:
        print(f"failed to read {PORTFOLIO_FILE}: {e}")
        return 1
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def voice_cli(args):
    prefs = load_prefs()
    if args.enable:
        prefs["voice_enabled"] = True
    if args.disable:
        prefs["voice_enabled"] = False
    if args.rate:
        prefs["voice_rate"] = str(args.rate)
    if args.pitch:
        prefs["voice_pitch"] = str(args.pitch)
    if args.engine is not None:
        prefs["voice_engine"] = args.engine
    if args.stream is not None:
        prefs["voice_stream"] = args.stream
    save_prefs(prefs)
    if args.test:
        speak(args.test)
        print("voice test sent")
    print(json.dumps(prefs, indent=2, sort_keys=True))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="./wingman_cli.py")
    sub = parser.add_subparsers(dest="topic", required=True)

    user = sub.add_parser("user")
    user_sub = user.add_subparsers(dest="user_cmd", required=True)

    ua = user_sub.add_parser("add")
    ua.add_argument("--alias")
    ua.add_argument("--notes")
    ua.set_defaults(func=user_add_cli)

    us = user_sub.add_parser("show")
    us.add_argument("--alias")
    us.set_defaults(func=user_show_cli)

    exchange = sub.add_parser("exchange")
    exchange_sub = exchange.add_subparsers(dest="exchange_cmd", required=True)

    ea = exchange_sub.add_parser("add")
    ea.set_defaults(func=exchange_add_cli)

    el = exchange_sub.add_parser("list")
    el.set_defaults(func=exchange_list_cli)

    brief = sub.add_parser("brief")
    brief.set_defaults(func=trading_brief_cli)

    portfolio = sub.add_parser("portfolio")
    portfolio.set_defaults(func=portfolio_cli)

    voice = sub.add_parser("voice")
    voice.add_argument("--enable", action="store_true")
    voice.add_argument("--disable", action="store_true")
    voice.add_argument("--rate")
    voice.add_argument("--pitch")
    voice.add_argument("--engine", nargs="?", const="")
    voice.add_argument("--stream", nargs="?", const="")
    voice.add_argument("--test")
    voice.set_defaults(func=voice_cli)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
