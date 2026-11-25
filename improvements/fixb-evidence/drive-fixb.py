#!/usr/bin/env python3
"""Fix B held-out drive of run shape through the integrated holder setup.

One realistic task-like drive on a non-run target. Pill held, holder owns
the ONE BiDi session with the Proxy shim, real input via act-now, state
reads via holder RPC. Timed wall-clock Asia/Ho_Chi_Minh + elapsed.

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence
shows entry, path, action, and resulting state.
User entry point for this test: held blank tab on ws2, Ctrl+L, type
"cloudflare", Return (DuckDuckGo SERP), click first result.
Forbidden shortcuts for this test: deep link or BiDi navigate to
cloudflare.com, internal setters, test-only endpoints, DOM click.

Usage: drive-fixb.py  (runs detached on the laptop; waits at the coords
gate /tmp/fixb-gate/coords.json, written by the coordinator after viewing
the SERP observe image). Stdlib only (ponytail).
ydotool is banned. Restate the ban in every brief. Never assume it.
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / "computer-use-wayland" / "scripts"))
from first_action import acquire_overlay, release_overlay  # noqa: E402
import overlay as overlay_mod  # noqa: E402

OUT = Path("/tmp/fixb-evidence")
RPC = Path("/tmp/fixb-rpc")
GATE = Path("/tmp/fixb-gate")
LOG = OUT / "drive-fixb.log"
AGENT = "FixB"
METHOD = "BiDi test"
ZEN_ADDR = "0x5614f01a0e20"
QUERY = "cloudflare"
EXPECT_HOST = "cloudflare.com"

INFO_EXPR = """(() => ({
  webdriver: navigator.webdriver,
  own_on_navigator: Object.prototype.hasOwnProperty.call(navigator, 'webdriver'),
  own_on_proto: Object.prototype.hasOwnProperty.call(Object.getPrototypeOf(navigator), 'webdriver'),
  title: document.title,
  url: location.href,
  body_start: (document.body ? document.body.innerText.slice(0, 250) : ''),
  has_cf_challenge: document.title.includes('Just a moment') || (document.body?.innerText?.includes('Verify you are human') ?? false)
}))()"""

T0 = time.monotonic()


def log(obj):
    line = json.dumps({"wall": datetime.now().astimezone().isoformat(timespec="seconds"),
                       "elapsed_s": round(time.monotonic() - T0, 1), **obj})
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def sh(cmd, timeout_s=180):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    return p.returncode, p.stdout, p.stderr


def unwrap(v):
    if isinstance(v, dict) and "type" in v and "value" in v:
        return v["value"]
    if isinstance(v, list):
        out = {}
        for item in v:
            if isinstance(item, list) and len(item) == 2:
                out[item[0]] = unwrap(item[1])
            else:
                return v
        return out
    return v


def rpc(req, timeout_s=60):
    req_id = str(time.time_ns())
    req = {"id": req_id, **req}
    (RPC / "req.json").write_text(json.dumps(req))
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            resp = json.loads((RPC / "resp.json").read_text())
            if resp.get("id") == req_id:
                if resp.get("ok"):
                    return unwrap(resp["value"])
                raise RuntimeError(resp.get("error", "rpc error"))
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        time.sleep(0.3)
    raise TimeoutError("rpc timeout")


def act_now(actions, tag, observation=None):
    path = OUT / f"actions-{tag}.json"
    path.write_text(json.dumps(actions))
    cmd = ["computer-use", "act-now", "--actions", str(path),
           "--agent", AGENT, "--method", METHOD, "--label", "Computer use active"]
    if observation:
        cmd += ["--observation", observation]
    rc, out, err = sh(cmd)
    log({"step": "act_now", "tag": tag, "rc": rc, "out": out[:500], "err": err[:200]})
    return rc


def observe(tag):
    rc, out, err = sh(["computer-use", "observe", "--window", ZEN_ADDR, "--focus"])
    log({"step": "observe", "tag": tag, "rc": rc, "out": out[:500], "err": err[:200]})
    try:
        d = json.loads(out)
        return d.get("observation"), d.get("image")
    except Exception:
        return None, None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    GATE.mkdir(parents=True, exist_ok=True)
    log({"step": "drive_start", "query": QUERY, "expect_host": EXPECT_HOST,
         "entry_point": "held blank tab, Ctrl+L, type query, Return, click first result",
         "forbidden": "deep link, BiDi navigate to target, internal setters, DOM click"})
    reply = acquire_overlay(AGENT, METHOD, label="Computer use active")
    log({"step": "pill_acquired", "visible": reply.get("visible"), "label": reply.get("label")})
    holder = None
    try:
        subprocess.run(["rm", "-rf", str(RPC)])
        RPC.mkdir(parents=True, exist_ok=True)
        holder = subprocess.Popen(["node", "/tmp/fixb-runner/holder-fixb.mjs"],
                                  stdout=open(OUT / "holder-fixb.log", "w"),
                                  stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 90
        while not (RPC / "ready.json").exists():
            if holder.poll() is not None:
                raise RuntimeError("holder exited early, see holder-fixb.log")
            if time.monotonic() > deadline:
                raise TimeoutError("holder not ready")
            time.sleep(0.5)
        ready = json.loads((RPC / "ready.json").read_text())
        log({"step": "holder_ready", "ready": ready})
        probe = ready.get("probe", {})
        if not (probe.get("webdriver") is False and probe.get("own_on_proto") is True
                and probe.get("own_on_navigator") is False):
            raise RuntimeError("probe mismatch, drive aborted loudly: " + json.dumps(probe)[:300])
        log({"step": "probe_ok", "probe": probe})

        # User path: address-bar search like a normal user.
        act_now([
            {"type": "key", "keys": ["Ctrl", "l"]},
            {"type": "wait", "ms": 600},
            {"type": "type", "text": QUERY, "delay_ms": 30},
            {"type": "wait", "ms": 600},
            {"type": "key", "keys": ["Return"]},
            {"type": "wait", "ms": 2000},
        ], "search")
        time.sleep(6)
        serp = rpc({"expr": "({title: document.title, url: location.href})"})
        log({"step": "serp", "serp": serp})
        obs_json, obs_img = observe("serp")
        (GATE / "serp.json").write_text(json.dumps(
            {"observation": obs_json, "image": obs_img, "serp": serp}))
        log({"step": "gate_wait", "gate": str(GATE / "serp.json")})
        coords_file = GATE / "coords.json"
        deadline = time.monotonic() + 1800
        coords = None
        while coords is None:
            if time.monotonic() > deadline:
                log({"step": "gate_timeout"})
                return
            try:
                coords = json.loads(coords_file.read_text())
            except (FileNotFoundError, json.JSONDecodeError):
                coords = None
                time.sleep(2)
        log({"step": "gate_coords", "coords": coords})
        obs_json2, _ = observe("preclick")
        act_now([
            {"type": "click", "x": coords["x"], "y": coords["y"]},
            {"type": "wait", "ms": 2000},
        ], "click", observation=obs_json2)
        time.sleep(12)
        info = rpc({"expr": INFO_EXPR})
        log({"step": "landing", "info": info})
        observe("landing")
        act_now([{"type": "scroll", "x": coords["x"], "y": coords["y"], "dy": 600},
                 {"type": "wait", "ms": 1000}], "scroll", observation=obs_json2)
        time.sleep(3)
        info2 = rpc({"expr": INFO_EXPR})
        log({"step": "after_interact", "info": info2})
        observe("interacted")
        landed_ok = (EXPECT_HOST in str(info.get("url", ""))
                     and info.get("webdriver") is False
                     and info.get("has_cf_challenge") is False)
        log({"step": "drive_verdict", "landed_ok": landed_ok})
    finally:
        try:
            (RPC / "stop").write_text("stop")
        except Exception:
            pass
        if holder is not None:
            try:
                holder.wait(timeout=30)
            except subprocess.TimeoutExpired:
                holder.kill()
                log({"step": "holder_killed_after_timeout"})
        release_overlay(AGENT)
        try:
            visible_after = overlay_mod._send_socket({"command": "status"}).get("visible")
        except Exception:
            visible_after = None
        log({"step": "pill_released", "visible_after": visible_after})
    log({"step": "drive_done"})


if __name__ == "__main__":
    main()
