#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

USERS_FILE = Path("wingman_users.json")


def load_users():
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_users(data):
    USERS_FILE.write_text(json.dumps(data, indent=2, sort_keys=True))


def ask(prompt, default=""):
    raw = input(f"{prompt}" + (f" [{default}]" if default else "") + ": ").strip()
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
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
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
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
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

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
