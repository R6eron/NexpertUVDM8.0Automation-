#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="$HOME/NexpertUVDM-Automation"
BACKUP="$ROOT/tools/uvdm_backup_runtime.sh"
if [ "$#" -eq 0 ]; then
    echo "usage: uvwrap <command> [args...]"
    exit 2
fi
if [ ! -x "$BACKUP" ]; then
    echo "missing_backup_script=$BACKUP"
    exit 1
fi
"$BACKUP"
status=0
"$@" || status=$?
"$BACKUP"
exit "$status"
