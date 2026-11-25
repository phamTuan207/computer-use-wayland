#!/usr/bin/env python3
"""Council-2 round 4: user-way proof, gated. Driver holds the pill and a
BiDi holder session (preload shim), runs the search batch per site, observes
the Zen window, then waits for /tmp/council2-gate/<site>-coords.json with
image-space click coords (grounded by the council agent viewing the image).
Then clicks via act-now with --observation, reads landing state via holder
RPC, observes again. Usage: run_round4.py <mode> [sites...]
Stdlib only (ponytail)."""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / "computer-use-wayland" / "scripts"))
from first_action import acquire_overlay, overlay_visible, release_overlay  # noqa: E402

MODE = sys.argv[1] if len(sys.argv) > 1 else "preload"
ONLY = sys.argv[2:] if len(sys.argv) > 2 else None
OUT = Path("/tmp/council2-evidence")
RPC = Path("/tmp/council2-rpc")
GATE = Path("/tmp/council2-gate")
LOG = OUT / f"run4-{MODE}.log"
AGENT = "Council-2"
METHOD = "BiDi test"
ZEN_ADDR = "0x5614f01a0e20"

SITES = [
    ("coolors", "coolors color palette generator", "coolors.co"),
    ("chatgpt", "chatgpt", "chatgpt.com"),
    ("timeanddate", "timeanddate world clock", "timeanddate.com"),
    ("openverse", "openverse free images", "openverse.org"),
]
if ONLY:
    SITES = [s for s in SITES if s[0] in ONLY]

INFO_EXPR = """(() => ({
  webdriver: navigator.webdriver,
  own_on_navigator: Object.prototype.hasOwnProperty.call(navigator, 'webdriver'),
  own_on_proto: Object.prototype.hasOwnProperty.call(Object.getPrototypeOf(navigator), 'webdriver'),
  title: document.title,
  url: location.href,
  body_start: (document.body ? document.body.innerText.slice(0, 250) : ''),
  has_cf_challenge: document.title.includes('Just a moment') || (document.body?.innerText?.includes('Verify you are human') ?? false),
  has_google_sorry: location.href.includes('/sorry/')
}))()"""


def log(obj):
    line = json.dumps({"wall": datetime.now().astimezone().isoformat(timespec="seconds"), "mode": MODE, **obj})
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


def rpc_eval(expr, timeout_s=30):
    req_id = str(time.time_ns())
    (RPC / "req.json").write_text(json.dumps({"id": req_id, "expr": expr}))
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
    path = OUT / f"actions4-{MODE}-{tag}.json"
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


def userway_site(name, query, host):
    tag = f"{MODE}-uw4-{name}"
    start = time.monotonic()
    log({"step": "site_start", "tag": tag, "query": query, "host": host})
    act_now([
        {"type": "key", "keys": ["Ctrl", "l"]},
        {"type": "wait", "ms": 600},
        {"type": "type", "text": query, "delay_ms": 30},
        {"type": "wait", "ms": 600},
        {"type": "key", "keys": ["Return"]},
        {"type": "wait", "ms": 2000},
    ], tag + "-search")
    time.sleep(6)
    serp = rpc_eval("({title: document.title, url: location.href})")
    log({"step": "serp", "tag": tag, "serp": serp})
    obs_json, obs_img = observe(tag + "-serp")
    gate_file = GATE / f"{name}-serp.json"
    gate_file.write_text(json.dumps({"site": name, "observation": obs_json, "image": obs_img, "serp": serp}))
    log({"step": "gate_wait", "tag": tag, "gate": str(gate_file)})
    coords_file = GATE / f"{name}-coords.json"
    deadline = time.monotonic() + 900
    while not coords_file.exists():
        if time.monotonic() > deadline:
            log({"step": "gate_timeout", "tag": tag})
            return
        time.sleep(2)
    coords = json.loads(coords_file.read_text())
    log({"step": "gate_coords", "tag": tag, "coords": coords})
    # Re-observe for freshness, same layout, then click with that observation.
    obs_json2, _ = observe(tag + "-preclick")
    act_now([
        {"type": "click", "x": coords["x"], "y": coords["y"]},
        {"type": "wait", "ms": 2000},
    ], tag + "-click", observation=obs_json2)
    time.sleep(12)
    info = rpc_eval(INFO_EXPR)
    log({"step": "landing", "tag": tag, "elapsed_s": round(time.monotonic() - start, 1), "info": info})
    observe(tag + "-landing")
    act_now([{"type": "scroll", "x": coords["x"], "y": coords["y"], "dy": 600}, {"type": "wait", "ms": 1000}], tag + "-scroll", observation=obs_json2)
    time.sleep(3)
    info2 = rpc_eval(INFO_EXPR)
    log({"step": "after_interact", "tag": tag, "info": info2})
    observe(tag + "-interacted")


def main():
    log({"step": "runner4_start", "sites": [s[0] for s in SITES]})
    reply = acquire_overlay(AGENT, METHOD)
    log({"step": "pill_acquired", "visible": overlay_visible(AGENT), "label": reply.get("label")})
    holder = None
    try:
        subprocess.run(["rm", "-rf", str(RPC), str(GATE)])
        RPC.mkdir(parents=True, exist_ok=True)
        GATE.mkdir(parents=True, exist_ok=True)
        holder = subprocess.Popen(["node", "/tmp/council2-harness/holder.mjs", MODE],
                                  stdout=open(OUT / f"holder4-{MODE}.log", "w"),
                                  stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 60
        while not (RPC / "ready.json").exists():
            if time.monotonic() > deadline:
                raise TimeoutError("holder not ready")
            time.sleep(0.5)
        log({"step": "holder_ready", "ready": json.loads((RPC / "ready.json").read_text())})
        log({"step": "probe_initial", "info": rpc_eval(INFO_EXPR)})
        for name, query, host in SITES:
            try:
                userway_site(name, query, host)
            except Exception as e:
                log({"step": "site_error", "site": name, "error": str(e)[:400]})
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
        err = release_overlay(AGENT)
        log({"step": "pill_released", "error": err, "visible_after": overlay_visible(AGENT)})
    log({"step": "runner4_done"})


if __name__ == "__main__":
    main()
