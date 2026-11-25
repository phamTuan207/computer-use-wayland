#!/usr/bin/env python3
"""F3 prover drive: one cookie-cleared user-way site check through the holder.

Modeled on drive-fixb.py (Fix B held-out drive, PASS). Same holder, same
pill discipline, same act-now real input, same RPC state reads. Differences
are minimal and listed here (ponytail: reuse before writing):
- Parameterized by argv: query, expect_host, tag, zen_addr.
- Agent name Prover (runbook section 7 step 2).
- SERP host enforced: duckduckgo.com or the drive aborts loudly.
- Second gate for the interact step: landing.json is written, then the
  prover coordinator writes coords2.json (click, click_type, or skip).
  Skip means scroll only. Timeout falls back to scroll and logs it.
- Logs and holder log under /tmp/f3-evidence with the site tag.

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence
shows entry, path, action, and resulting state.
User entry point for this test: held blank tab on ws2, Ctrl+L, type the
query, Return (DuckDuckGo SERP), click first result.
Forbidden shortcuts for this test: deep link, BiDi navigate to the target,
internal setters, test-only endpoints, DOM click, uncleared-cookie retries.

Usage: drive-prover.py <query> <expect_host> <tag> <zen_addr>
Runs detached on the laptop. Stdlib only.
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

QUERY = sys.argv[1]
EXPECT_HOST = sys.argv[2]
TAG = sys.argv[3]
ZEN_ADDR = sys.argv[4]

OUT = Path("/tmp/f3-evidence")
RPC = Path("/tmp/fixb-rpc")
GATE = Path("/tmp/fixb-gate")
LOG = OUT / f"drive-{TAG}.log"
HOLDER_LOG = OUT / f"holder-{TAG}.log"
AGENT = "Prover"
METHOD = "BiDi test"

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
    path = OUT / f"actions-{TAG}-{tag}.json"
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


def wait_gate(path, timeout_s, step_name):
    deadline = time.monotonic() + timeout_s
    while True:
        if time.monotonic() > deadline:
            log({"step": step_name + "_timeout"})
            return None
        try:
            return json.loads(path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            time.sleep(2)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    GATE.mkdir(parents=True, exist_ok=True)
    log({"step": "drive_start", "query": QUERY, "expect_host": EXPECT_HOST, "tag": TAG,
         "entry_point": "held blank tab, Ctrl+L, type query, Return, click first result",
         "forbidden": "deep link, BiDi navigate to target, internal setters, DOM click, uncleared-cookie retries"})
    reply = acquire_overlay(AGENT, METHOD, label="Computer use active")
    log({"step": "pill_acquired", "visible": reply.get("visible"), "label": reply.get("label")})
    if reply.get("visible") is not True:
        log({"step": "pill_fail_closed", "reply": reply})
        raise RuntimeError("pill not visible, fail closed before holder start")
    holder = None
    try:
        subprocess.run(["rm", "-rf", str(RPC)])
        RPC.mkdir(parents=True, exist_ok=True)
        holder = subprocess.Popen(["node", "/tmp/fixb-runner/holder-fixb.mjs"],
                                  stdout=open(HOLDER_LOG, "w"),
                                  stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 90
        while not (RPC / "ready.json").exists():
            if holder.poll() is not None:
                raise RuntimeError("holder exited early, see holder log")
            if time.monotonic() > deadline:
                raise TimeoutError("holder not ready")
            time.sleep(0.5)
        ready = json.loads((RPC / "ready.json").read_text())
        log({"step": "holder_ready", "ready": ready})
        probe = ready.get("probe", {})
        if not (probe.get("webdriver") is False and probe.get("own_on_proto") is True
                and probe.get("own_on_navigator") is False
                and probe.get("get_name") == "get webdriver"):
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
        if "duckduckgo.com" not in str(serp.get("url", "")):
            log({"step": "serp_host_mismatch", "serp": serp})
            raise RuntimeError("SERP host is not duckduckgo.com, stop per runbook")
        obs_json, obs_img = observe("serp")
        (GATE / "serp.json").write_text(json.dumps(
            {"observation": obs_json, "image": obs_img, "serp": serp, "tag": TAG}))
        log({"step": "gate_wait", "gate": str(GATE / "serp.json")})
        coords = wait_gate(GATE / "coords.json", 1800, "gate")
        if coords is None:
            return
        log({"step": "gate_coords", "coords": coords})
        obs_json2, _ = observe("preclick")
        act_now([
            {"type": "click", "x": coords["x"], "y": coords["y"]},
            {"type": "wait", "ms": 2000},
        ], "click", observation=obs_json2)
        time.sleep(12)
        info = rpc({"expr": INFO_EXPR})
        log({"step": "landing", "info": info})
        obs_land, img_land = observe("landing")
        (GATE / "landing.json").write_text(json.dumps(
            {"observation": obs_land, "image": img_land, "info": info, "tag": TAG}))
        log({"step": "gate2_wait", "gate": str(GATE / "landing.json")})
        coords2 = wait_gate(GATE / "coords2.json", 900, "gate2")
        if coords2 is None:
            log({"step": "gate2_timeout_scroll_fallback"})
            act_now([{"type": "scroll", "x": coords["x"], "y": coords["y"], "dy": 600},
                     {"type": "wait", "ms": 1000}], "scroll", observation=obs_json2)
        elif coords2.get("skip"):
            log({"step": "gate2_skip_scroll", "coords2": coords2})
            act_now([{"type": "scroll", "x": coords["x"], "y": coords["y"], "dy": 600},
                     {"type": "wait", "ms": 1000}], "scroll", observation=obs_json2)
        elif coords2.get("action") == "click_type":
            log({"step": "gate2_coords", "coords2": coords2})
            obs_json3, _ = observe("preinteract")
            act_now([
                {"type": "click", "x": coords2["x"], "y": coords2["y"]},
                {"type": "wait", "ms": 800},
                {"type": "type", "text": coords2.get("text", "hello"), "delay_ms": 30},
                {"type": "wait", "ms": 1000},
            ], "interact", observation=obs_json3)
        else:
            log({"step": "gate2_coords", "coords2": coords2})
            obs_json3, _ = observe("preinteract")
            act_now([
                {"type": "click", "x": coords2["x"], "y": coords2["y"]},
                {"type": "wait", "ms": 2000},
            ], "interact", observation=obs_json3)
        time.sleep(3)
        info2 = rpc({"expr": INFO_EXPR})
        log({"step": "after_interact", "info": info2})
        observe("interacted")
        landed_ok = (EXPECT_HOST in str(info.get("url", ""))
                     and info.get("webdriver") is False
                     and info.get("has_cf_challenge") is False
                     and "Just a moment" not in str(info.get("title", "")))
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
