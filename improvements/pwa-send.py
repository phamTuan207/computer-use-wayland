#!/usr/bin/env python3
"""pwa-send.py - Send a message (or run any driver action) in the Muse / mimeo PWA via CDP.
No mouse, no vision, no computer-use. CDP only.

Usage:
  pwa-send.py clone1 "message text"            # send a message to clone1
  pwa-send.py clone2 "message text"            # send a message to clone2
  pwa-send.py mei --action read 5              # read mei's last 5 messages (no send)
  pwa-send.py mochi --action status            # read mochi's status line (no send)
  pwa-send.py clone1 --action read 5           # read last 5 messages
  pwa-send.py clone1 --action status           # read the agent status line
  pwa-send.py clone1 --action list             # list main + side chats
  pwa-send.py clone1 --action search <query>   # search the PWA
  pwa-send.py clone1 --action newchat          # create a new side chat
  pwa-send.py clone1 --action back             # back to the main chat
  pwa-send.py clone1 --action call [holdMs]    # start a call, end it after holdMs
  pwa-send.py clone1 --action attach <file>    # attach a file (laptop path) to the composer
  pwa-send.py clone1 --action unattach         # remove the attachment
  pwa-send.py clone1 --action raw "<js>"       # evaluate arbitrary JS in the page
  pwa-send.py clone1 --action stop [--force]   # stop detection (no --force = detect only)
  pwa-send.py clone1 --action reply [--send <text>]  # reply to last agent msg (menu-limited, see report)
  pwa-send.py clone1 --action react [emoji]    # react to last agent msg (menu-limited, see report)

How it works:
- Resolves the CDP target by URL via /json/list (never hardcodes target IDs).
  Both pages on a port are titled "Muse" now, so title matching cannot tell the
  PWA apart from the chat tab. The driver matches the PWA by "__pwa=1" in the URL
  and the chat tab by a muse.ai URL without "__pwa=1".
- Ships ~/workspace/pwa-driver.js to the laptop over SSH (stdin pipe) and runs it
  with Node (v26, global WebSocket, no dependencies) via ~/workspace/ssh-laptop.sh.
- Prints the driver's JSON result to stdout. Exit code 0 on ok, 1 on failure.

Recipients:
- clone1 = Muse PWA on Brave, CDP 9224, URL https://muse.ai/?__pwa=1
- clone2 = mimeo PWA on Chromium, CDP 9223, URL https://muse.ai/?__pwa=1
- mei = regular chat tab on Brave, CDP 9224, URL https://muse.ai/ (no __pwa=1)
- mochi = regular chat tab on Chromium, CDP 9223, URL https://muse.ai/ (no __pwa=1)
- Mei's tab is never confused with clone1's PWA tab, and mochi's tab is never
  confused with clone2's PWA tab. Never use clone1's tab as a mei target.
- NOTE: mei and mochi are normally messaged through the daemon (send.py), not
  through pwa-send.py. They are recipients here only so read/status resolution
  works for the shared agents watch.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
WORKSPACE = HOME / "workspace"
DRIVER_VM = WORKSPACE / "pwa-driver.js"
DRIVER_LAPTOP = "/tmp/pwa-driver.js"
SSH = str(WORKSPACE / "ssh-laptop.sh")

RECIPIENTS = {
    "clone1": {"port": "9224", "match": "pwa:clone1"},
    "clone2": {"port": "9223", "match": "pwa:clone2"},
    "mei": {"port": "9224", "match": "chat:mei"},
    "mochi": {"port": "9223", "match": "chat:mochi"},
}


def run_ssh(command, input_bytes=None):
    """Run a command on the laptop via ssh-laptop.sh. Returns (rc, stdout, stderr)."""
    p = subprocess.run(
        [SSH, command], input=input_bytes,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,
    )
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def ship_driver():
    """Ship pwa-driver.js to the laptop; verify by sha256. Returns True on match."""
    data = DRIVER_VM.read_bytes()
    rc, out, err = run_ssh(f"cat > {DRIVER_LAPTOP} && sha256sum {DRIVER_LAPTOP}", input_bytes=data)
    if rc != 0:
        print(f"ship failed rc={rc}: {out} {err}", file=sys.stderr)
        return False
    remote_hash = out.split()[0] if out.split() else ""
    local_hash = hashlib.sha256(data).hexdigest()
    if remote_hash != local_hash:
        print(f"ship hash mismatch: local {local_hash} remote {remote_hash}", file=sys.stderr)
        return False
    return True


def main(argv):
    if len(argv) < 2 or argv[1] not in RECIPIENTS:
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        print("usage: pwa-send.py clone1|clone2|mei|mochi <message> | --action <action> [args...]", file=sys.stderr)
        return 2
    rec = RECIPIENTS[argv[1]]
    rest = argv[2:]
    if rest and rest[0] == "--action":
        action = rest[1] if len(rest) > 1 else "send"
        args = rest[2:]
    else:
        action = "send"
        args = rest
    if action == "send" and not args:
        print("nothing to send", file=sys.stderr)
        return 2
    if not DRIVER_VM.exists():
        print(f"driver not found: {DRIVER_VM}", file=sys.stderr)
        return 2
    if not ship_driver():
        return 1
    # Quote args for the remote shell: single-quote each, escape embedded quotes.
    def q(s):
        return "'" + s.replace("'", "'\"'\"'") + "'"
    remote = " ".join(
        ["node", DRIVER_LAPTOP, rec["port"], rec["match"], action] + [q(a) for a in args]
    )
    rc, out, err = run_ssh(remote)
    sys.stdout.write(out)
    if err.strip():
        sys.stderr.write(err)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
