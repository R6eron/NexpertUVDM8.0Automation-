import json
import hashlib
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

CYAN = "\u001B[96m"
WHITE = "\u001B[97m"
GOLD = "\u001B[93m"
GREEN = "\u001B[92m"
RED = "\u001B[91m"
MAGENTA = "\u001B[95m"
RESET = "\u001B[0m"
BOLD = "\u001B[1m"
HEX_RE = re.compile(r"^0x[0-9a-fA-F]+$")
STATE_PATH = Path.home() / ".xrpeasy_onboarding_state.json"

def term_width(default=80):
    try:
        return shutil.get_terminal_size((default, 24)).columns
    except Exception:
        return default

def center(text, width):
    return text.center(width)

def line(char="═", width=80):
    return char * width

def render_header(identity="UVDM Pending Identity", customer="Customer / Mentee Pending"):
    width = term_width()
    print(CYAN + line("═", width) + RESET)
    print(CYAN + BOLD + center("UVDM Wingman TM 2025", width) + RESET)
    print(WHITE + center(identity, width) + RESET)
    print(WHITE + center(customer, width) + RESET)
    print(CYAN + line("═", width) + RESET)
    print()
    print(GOLD + center("Process over outcome..", width) + RESET)
    print(GOLD + center("No fear or Greed if you hope to succeed..", width) + RESET)
    print(GREEN + center("Tape is the only source of Truth", width) + RESET)
    print()

def validate_hex(hex_value: str):
    return bool(HEX_RE.match(hex_value)) and len(hex_value) >= 10

def normalize_dob_uk(dob_raw: str):
    dob_raw = dob_raw.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(dob_raw, fmt)
            return dt.strftime("%d/%m/%Y"), dt.strftime("%Y-%m-%d"), dt.strftime("%d%m%Y")
        except ValueError:
            pass
    return None, None, None

def ask(prompt, allow_blank=False):
    while True:
        value = input(prompt).strip()
        if value or allow_blank:
            return value
        print(RED + "Blank response not accepted." + RESET)

def yes_like(v: str):
    return v.strip().lower() in {"y", "yes"}

def build_identity(last_name: str, initials: str, dob_compact_uk: str, mentee_no: str):
    return f"{last_name.upper()} {initials.upper()} {dob_compact_uk}{mentee_no}"

def derive_immortal_id(hex_value: str, last_name: str, initials: str, dob_iso: str, gender: str, device_label: str):
    payload = "|".join([
        hex_value.strip(),
        last_name.strip().upper(),
        initials.strip().upper(),
        dob_iso.strip(),
        gender.strip().upper(),
        device_label.strip().upper(),
    ])
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"uvdm-{digest[:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}"

def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            return None
    return None

def save_state(state: dict):
    STATE_PATH.write_text(json.dumps(state, indent=2))

def main(argv):
    hex_value = argv[1].strip() if len(argv) > 1 else ask("Book hex? ")
    if not validate_hex(hex_value):
        print(RED + "Invalid hex. Must be full 0x-prefixed hexadecimal." + RESET)
        return 2

    existing = load_state()
    if existing and existing.get("identity_bound"):
        bound_hex = existing.get("first_user_hex")
        if bound_hex == hex_value:
            render_header(
                identity=existing.get("display_identity", "UVDM Bound Identity"),
                customer=existing.get("customer_line", "Customer / Mentee Bound"),
            )
            print(GREEN + "Identity already bound on this device. Preserving existing identity." + RESET)
            print(WHITE + f"immortal_id = {existing.get('immortal_id')}" + RESET)
            print(WHITE + f"first_user_hex = {existing.get('first_user_hex')}" + RESET)
            print(WHITE + f"bound_device_label = {existing.get('device_label')}" + RESET)
            print(WHITE + f"state_file = {STATE_PATH}" + RESET)
            return 0
        print(RED + "Binding blocked. This device is already bound to a different first_user_hex." + RESET)
        print(WHITE + f"existing_hex = {bound_hex}" + RESET)
        print(WHITE + f"state_file = {STATE_PATH}" + RESET)
        return 3

    last_name = ask("Last name? ")
    initials = ask("Initials? ")
    dob_input = ask("DOB (DD/MM/YYYY)? ")
    dob_uk, dob_iso, dob_compact = normalize_dob_uk(dob_input)
    if not dob_uk:
        print(RED + "Invalid DOB format. Use DD/MM/YYYY, e.g. 15/08/1968." + RESET)
        return 4
    gender = ask("Gender (M/F/U)? ").upper()
    device_label = ask("Device label? ")
    mentee_no = ask("Mentee number suffix (e.g. 001)? ")

    display_identity = build_identity(last_name, initials, dob_compact, mentee_no)
    customer_line = f"Customer / Mentee {initials.upper()}{mentee_no}"
    immortal_id = derive_immortal_id(hex_value, last_name, initials, dob_iso, gender, device_label)

    render_header(identity=display_identity, customer=customer_line)
    print(MAGENTA + "Review identity data:" + RESET)
    print(WHITE + f"display_identity = {display_identity}" + RESET)
    print(WHITE + f"immortal_id = {immortal_id}" + RESET)
    print(WHITE + f"device_label = {device_label}" + RESET)
    print(WHITE + f"dob_uk = {dob_uk}" + RESET)
    print(WHITE + f"dob_iso = {dob_iso}" + RESET)
    print(WHITE + f"hex = {hex_value}" + RESET)

    confirm1 = ask("Confirm details? (y/n) ")
    if not yes_like(confirm1):
        print(RED + "Binding cancelled." + RESET)
        return 5

    confirm2 = ask("Type EXECUTE to bind identity: ")
    if confirm2.strip().lower() != "execute":
        print(RED + "Binding not executed." + RESET)
        return 6

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state = {
        "immortal_id": immortal_id,
        "display_identity": display_identity,
        "customer_line": customer_line,
        "first_user_hex": hex_value,
        "identity_bound": True,
        "device_label": device_label,
        "gender": gender,
        "dob_uk": dob_uk,
        "dob_iso": dob_iso,
        "last_name": last_name.upper(),
        "initials": initials.upper(),
        "current_stage": "bifrost_create",
        "next_stage": "buy_flr_demo",
        "flow_ready": True,
        "created_at": now,
        "updated_at": now,
    }
    save_state(state)

    print(GREEN + "Identity bound and persisted." + RESET)
    print(WHITE + f"state_file = {STATE_PATH}" + RESET)
    print(WHITE + f"immortal_id = {immortal_id}" + RESET)
    print(WHITE + f"display_identity = {display_identity}" + RESET)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
