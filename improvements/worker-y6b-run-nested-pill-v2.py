import os
import secrets
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path("~/workspace/computer-use-wayland/scripts").expanduser()))
import indicator

# Minimal idle LIQUID pill inside the nest. STATE is separate from the live
# session, so the nested socket and token can never collide with the live pill.
# The launcher sets Y6_NEST_SIG to the nested instance signature.
# v2 (U9): show runs BEFORE the ready print, and ready is printed only after
# show succeeds, so the launcher ready signal means the pill is visible.
STATE_DIR = Path("/tmp/y6-nested/cache/agent-computer-use")
STATE_DIR.mkdir(parents=True, exist_ok=True)
token = secrets.token_hex(16)
server = indicator.listen(STATE_DIR, token)
env = dict(os.environ)
env["XDG_RUNTIME_DIR"] = "/tmp/y6-nested/run"
# v3 (Y6d): the socket name is discovered by the launcher and passed in the
# environment (was hardcoded wayland-y6); fail loudly if it is missing or empty.
_disp = os.environ["WAYLAND_DISPLAY"]
if not _disp: raise SystemExit("Y6-NEST-PILL: WAYLAND_DISPLAY empty, launcher did not pass a socket name")
env["WAYLAND_DISPLAY"] = _disp
env["HYPRLAND_INSTANCE_SIGNATURE"] = os.environ["Y6_NEST_SIG"]
native = indicator.Native(env)
try:
    print("Y6-NEST-PILL: show=" + native.command("show"), flush=True)
except Exception as exc:
    print("Y6-NEST-PILL: show failed: " + str(exc), flush=True)
    raise SystemExit(1)
print("Y6-NEST-PILL: ready", flush=True)


def serve_loop():
    while True:
        try:
            indicator.serve(server, native, token)
        except Exception as exc:
            print("Y6-NEST-PILL: serve error: " + str(exc), flush=True)
            time.sleep(1)


threading.Thread(target=serve_loop, daemon=True).start()
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    pass
finally:
    native.close()
    server.close()
