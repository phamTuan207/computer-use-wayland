#!/usr/bin/env python3
"""Install, check, or uninstall the native messaging host for the bridge.

Default action installs the host manifest:
  python3 install.py
This writes ~/.mozilla/native-messaging-hosts/computer_use_bridge.json
with the absolute path of host/cu_bridge_host.py and makes the host
executable. Zen reads the same ~/.mozilla registration as Firefox, so
no separate ~/.zen copy is written (a ~/.zen copy was tried by other
projects and did not work; the Mozilla location is the working one).
Flatpak Zen is the exception: the manifest and the host must also be
visible inside the sandbox, see docs/webext-bridge-install.md.

Other actions:
  python3 install.py --check
      Verify the manifest exists, parses, points at an existing
      executable host, and allows the bridge extension id.
  python3 install.py --uninstall
      Remove only the manifest file. The host script stays on disk.
  python3 install.py --sign
      Build a signed-ready extension zip with web-ext, if web-ext is
      installed. Signing itself needs AMO API keys, which are never
      stored here; the command prints the exact sign step to run.
  python3 install.py --policies <browser-dir> --xpi <signed.xpi>
      Write <browser-dir>/distribution/policies.json that force-installs
      the signed extension. Use the directory that holds the browser
      binary, for example the Zen install directory on the laptop.

This script only writes files under the user's home directory, plus
the policies directory when --policies is given. It does not start a
browser and does not touch any browser profile. All steps print what
they did and exit non-zero on failure.
"""

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOST = HERE / "host" / "cu_bridge_host.py"
EXTENSION_DIR = HERE / "extension"
HOST_NAME = "computer_use_bridge"
EXTENSION_ID = "cu-bridge@example.local"


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def manifest_path(home):
    return home / ".mozilla" / "native-messaging-hosts" / f"{HOST_NAME}.json"


def build_manifest():
    return {
        "name": HOST_NAME,
        "description": "Native messaging host for the computer-use WebExtension bridge",
        "path": str(HOST),
        "type": "stdio",
        "allowed_extensions": [EXTENSION_ID],
    }


def do_install(home):
    if not HOST.exists():
        print(f"[{stamp()}] host script missing: {HOST}", file=sys.stderr)
        return 1
    target = manifest_path(home)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_manifest(), indent=2) + "\n", encoding="utf-8")
    mode = HOST.stat().st_mode
    HOST.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"[{stamp()}] wrote {target}")
    print(f"[{stamp()}] host path: {HOST}")
    return do_check(home)


def do_check(home):
    target = manifest_path(home)
    problems = []
    if not target.exists():
        problems.append(f"manifest missing: {target}")
    else:
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            problems.append(f"manifest unreadable: {error}")
            data = None
        if data is not None:
            if data.get("name") != HOST_NAME:
                problems.append(f"manifest name is {data.get('name')!r}, want {HOST_NAME!r}")
            if data.get("type") != "stdio":
                problems.append(f"manifest type is {data.get('type')!r}, want 'stdio'")
            if EXTENSION_ID not in data.get("allowed_extensions", []):
                problems.append(f"manifest does not allow {EXTENSION_ID}")
            host_path = Path(str(data.get("path", "")))
            if not host_path.exists():
                problems.append(f"host path missing: {host_path}")
            elif not os.access(host_path, os.X_OK):
                problems.append(f"host path is not executable: {host_path}")
    if problems:
        for problem in problems:
            print(f"[{stamp()}] CHECK FAIL: {problem}", file=sys.stderr)
        return 1
    print(f"[{stamp()}] CHECK OK: {target}")
    print(f"[{stamp()}] CHECK OK: host {HOST} exists and is executable")
    print(f"[{stamp()}] CHECK OK: extension id {EXTENSION_ID} is allowed")
    return 0


def do_uninstall(home):
    target = manifest_path(home)
    if not target.exists():
        print(f"[{stamp()}] nothing to remove, no manifest at {target}")
        return 0
    target.unlink()
    print(f"[{stamp()}] removed {target}")
    print(f"[{stamp()}] host script left on disk at {HOST}")
    return 0


def do_sign():
    if shutil.which("web-ext") is None:
        print(
            f"[{stamp()}] web-ext is not installed. Install it with "
            "'npm install -g web-ext', then run: "
            "web-ext sign --channel unlisted "
            "--api-key <AMO-key> --api-secret <AMO-secret> "
            "--source-dir extension",
            file=sys.stderr,
        )
        print(
            f"[{stamp()}] AMO keys come from addons.mozilla.org, never "
            "store them in this repo.",
            file=sys.stderr,
        )
        return 2
    artifacts = HERE / "web-ext-artifacts"
    result = subprocess.run(
        ["web-ext", "build", "--source-dir", str(EXTENSION_DIR),
         "--artifacts-dir", str(artifacts)],
        capture_output=True, text=True, timeout=300,
    )
    print(result.stdout, end="")
    print(result.stderr, file=sys.stderr, end="")
    if result.returncode != 0:
        print(f"[{stamp()}] web-ext build failed", file=sys.stderr)
        return result.returncode
    print(f"[{stamp()}] built extension zip in {artifacts}")
    print(
        f"[{stamp()}] next: web-ext sign --channel unlisted "
        "--api-key <AMO-key> --api-secret <AMO-secret> "
        f"--source-dir {EXTENSION_DIR}"
    )
    return 0


def do_policies(browser_dir, xpi):
    if not xpi:
        print(f"[{stamp()}] --policies needs --xpi <signed.xpi>", file=sys.stderr)
        return 1
    xpi_path = Path(xpi)
    if not xpi_path.exists():
        print(f"[{stamp()}] signed xpi missing: {xpi_path}", file=sys.stderr)
        return 1
    target_dir = Path(browser_dir) / "distribution"
    target_dir.mkdir(parents=True, exist_ok=True)
    policies = {
        "policies": {
            "ExtensionSettings": {
                EXTENSION_ID: {
                    "installation_mode": "force_installed",
                    "install_url": xpi_path.resolve().as_uri(),
                }
            }
        }
    }
    target = target_dir / "policies.json"
    target.write_text(json.dumps(policies, indent=2) + "\n", encoding="utf-8")
    print(f"[{stamp()}] wrote {target}")
    print(f"[{stamp()}] force-installs {EXTENSION_ID} from {xpi_path.resolve()}")
    print(f"[{stamp()}] restart the browser for policies to apply")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bridge host installer")
    parser.add_argument("--home", default=None, help="home dir, default Path.home()")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--sign", action="store_true")
    parser.add_argument("--policies", default=None, help="browser dir for policies.json")
    parser.add_argument("--xpi", default=None, help="signed .xpi for --policies")
    args = parser.parse_args(argv)
    home = Path(args.home) if args.home else Path.home()
    if str(home) in ("", "/"):
        print("cannot determine home directory", file=sys.stderr)
        return 1
    if args.check:
        return do_check(home)
    if args.uninstall:
        return do_uninstall(home)
    if args.sign:
        return do_sign()
    if args.policies:
        return do_policies(args.policies, args.xpi)
    return do_install(home)


if __name__ == "__main__":
    sys.exit(main())
