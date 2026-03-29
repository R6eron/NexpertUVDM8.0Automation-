#!/usr/bin/env python3
import json, os
from pathlib import Path

artifacts = Path("article_json_legacy_vault").glob("*.json")
tokens = []

for artifact in artifacts:
    data = json.loads(artifact.read_text())
    token_name = f"XRPEASY_{data['filename'].split('.')[0][:8].upper()}"
    tokens.append({"name": token_name, "wisdom": data['filename'], "family": data['family']})

print(f"🎯 UDVM TOKENS GENERATED: {len(tokens)}")
for t in tokens[:5]:  # Show first 5
    print(f"  {t['name']} → {t['wisdom']}")
