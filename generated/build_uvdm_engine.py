#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path.home() / "NexpertUVDM-Automation"
CONFIG = ROOT / "config" / "assets.json"
TEMPLATE = ROOT / "templates" / "uv_asset_wrapper.py"
BIN = ROOT / "bin"
GENERATED = ROOT / "generated"

data = json.loads(CONFIG.read_text())
defaults = data["defaults"]
template = TEMPLATE.read_text()

for asset in data["assets"]:
    text = template
    text = text.replace("__ASSET_NAME__", asset["name"])
    text = text.replace("__ASSET_SYMBOL__", asset["symbol"])
    text = text.replace("__ASSET_ALIAS__", asset["alias"])
    text = text.replace("__ASSET_TYPE__", asset["type"])
    text = text.replace("__ASSET_MAX_LIVE_LEVERAGE__", str(asset["max_live_leverage"]))
    text = text.replace("__ASSET_ML_PROFILE__", asset["ml_profile"])

    py_path = GENERATED / (asset["alias"] + ".py")
    sh_path = BIN / asset["alias"]
    env_path = GENERATED / (asset["name"] + ".env.json")

    py_path.write_text(text)
    py_path.chmod(0o755)

    shell_script = "#!/data/data/com.termux/files/usr/bin/bash
"
    shell_script += "exec python3 "$HOME/NexpertUVDM-Automation/generated/" + asset["alias"] + ".py" "$@"
"
    sh_path.write_text(shell_script)
    sh_path.chmod(0o755)

    env_payload = {
        "name": asset["name"],
        "symbol": asset["symbol"],
        "alias": asset["alias"],
        "type": asset["type"],
        "exchange": defaults["exchange"],
        "mode_default": defaults["mode_default"],
        "spot_default_leverage": defaults["spot_default_leverage"],
        "futures_default_leverage": defaults["futures_default_leverage"],
        "max_live_leverage": asset["max_live_leverage"],
        "ml_enabled": defaults["ml_enabled"],
        "det_enabled": defaults["det_enabled"],
        "wyckoff_required": defaults["wyckoff_required"],
        "ml_profile": asset["ml_profile"],
        "ml": asset.get("ml", {}),
        "execution": asset.get("execution", {})
    }
    env_path.write_text(json.dumps(env_payload, indent=2) + "
")

print("UVDM engine build complete.")
