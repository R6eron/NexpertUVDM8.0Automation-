#!/data/data/com.termux/files/usr/bin/sh
# Spot-mode wrapper for uvdm_live_onboard.py
# Forces venue=spot and leverage=1x via environment hints if supported,
# otherwise relies on manual spot choices in the script.

cd "$HOME/NexpertUVDM-Automation" || exit 1
exec python3 "uvdm_live_onboard.py"
