#!/usr/bin/env python3
"""Install the native messaging host manifest for the bridge.

Writes ~/.mozilla/native-messaging-hosts/computer_use_bridge.json with
the absolute path of host/cu_bridge_host.py and makes the host
executable. Zen reads the same ~/.mozilla registration as Firefox, so
no separate ~/.zen copy is written (a ~/.zen copy was tried by other
projects and did not work; the Mozilla location is the working one).

Run on the laptop, from this folder:
  python3 install.py

This script only writes files under the user's home directory. It does
not start a browser and does not touch any browser profile.
"""

import json
import os
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOST = HERE / "cu_bridge_host.py"
HOST_NAME = "computer_use_bridge"


def main():
    home = Path.home()
    if str(home) in ("", "/"):
        print("cannot determine home directory", file=sys.stderr)
        return 1
    target_dir = home / ".mozilla" / "native-messaging-hosts"
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "name": HOST_NAME,
        "description": "Native messaging host for the computer-use WebExtension bridge",
        "path": str(HOST),
        "type": "stdio",
        "allowed_extensions": ["cu-bridge@example.local"],
    }
    target = target_dir / f"{HOST_NAME}.json"
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    mode = HOST.stat().st_mode
    HOST.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"wrote {target}")
    print(f"host path: {HOST}")
    print("next: load the extension in Zen (about:debugging, Load Temporary Add-on, pick extension/manifest.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
