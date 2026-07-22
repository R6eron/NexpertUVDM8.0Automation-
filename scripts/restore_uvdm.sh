#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/NexpertUVDM-Automation"
git status --short || true
echo "restoreuvdm ready"
