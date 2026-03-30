#!/usr/bin/env python3
import os, glob, hashlib, json, datetime
from pathlib import Path

class LegacyVault:
    def __init__(self):
        self.vault = Path.home() / "projects" / "uvdm-automation" / "vault" / "voice_breaths_2026"
        print(f"🔍 Scanning: {self.vault.absolute()}")  # DEBUG
        self.breaths = list(self.vault.glob("*.m4a"))
        print(f"📂 Found files: {len(self.breaths)}")     # DEBUG
        
    def hash_breath(self, file):
        sha256 = hashlib.sha256()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def scan_vault(self):
        self.manifest = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_breaths": len(self.breaths),
            "total_size_mb": sum(f.stat().st_size for f in self.breaths) / 1e6,
            "files": [f.name for f in self.breaths],
            "breath_hashes": {f.name: self.hash_breath(f) for f in self.breaths}
        }
        return self.manifest
    
    def run(self):
        print("🗝️  LEGACY VAULT ENGINE ACTIVE")
        if not self.vault.exists():
            print("❌ VAULT DIRECTORY MISSING - CREATE IT:")
            print("mkdir -p ~/projects/uvdm-automation/vault/voice_breaths_2026")
            return
        manifest = self.scan_vault()
        print(f"📊 {manifest['total_breaths']} breaths | {manifest['total_size_mb']:.1f}MB")
        print(f"🔗 BREATH supply: {int(manifest['total_size_mb']*1e6):,} tokens")
        print("🚀 UVDM flywheel → XRPL AMM → XLS30D → ∞")
        return manifest

if __name__ == "__main__":
    vault = LegacyVault()
    vault.run()
