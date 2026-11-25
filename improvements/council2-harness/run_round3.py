#!/usr/bin/env python3
"""Council-2 round 3: user-way proof via the runner lane (computer-use
act-now real keyboard/mouse) with a held BiDi session (holder.mjs) carrying
the preload shim and reading page state. Usage: run_round3.py <mode>
mode: baseline | preload | proxy. Holds the pill for the whole run.
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
OUT = Path("/tmp/council2-evidence")
RPC = Path("/tmp/council2-rpc")
LOG = OUT / f"run3-{MODE}.log"
AGENT = "Council-2"
METHOD = "BiDi test"
ZEN_ADDR = "0x5614f01a0e20"

SITES = [
    ("coolors", "coolors color palette generator", "coolors.co"),
    ("chatgpt", "chatgpt", "chatgpt.com"),
    ("timeanddate", "timeanddate world clock", "timeanddate.com"),
    ("openverse", "openverse free images", "openverse.org"),
]

INFO_EXPR = """(() => ({
  webdriver: navigator.webdriver,
  own_on_navigator: Object.prototype.hasOwnProperty.call(navigator, 'webdriver'),
  own_on_proto: Object.prototype.hasOwnProperty.call(Object.getPrototypeOf(navigator), 'webdriver'),
  descriptor: (() => { const d = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(navigator), 'webdriver') || Object.getOwnPropertyDescriptor(navigator, 'webdriver'); return d ? {has_get: typeof d.get === 'function', get_name: d.get ? d.get.name : null, configurable: d.configurable, enumerable: d.enumerable} : null; })(),
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


def sh(cmd, timeout_s=120):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    return p.returncode, p.stdout, p.stderr


def rpc_eval(expr, timeout_s=30):
    req_id = str(time.time_ns())
    (RPC / "req.json").write_text(json.dumps({"id": req_id, "expr": expr}))
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            resp = json.loads((RPC / "resp.json").read_text())
            if resp.get("id") == req_id:
                if resp.get("ok"):
                    v = resp["value"]
                    if isinstance(v, list):
                        return {k: (val.get("value") if isinstance(val, dict) else val) for k, val in v}
                    return v
                raise RuntimeError(resp.get("error", "rpc error"))
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        time.sleep(0.3)
    raise TimeoutError("rpc timeout")


def act_now(actions, tag):
    path = OUT / f"actions-{MODE}-{tag}.json"
    path.write_text(json.dumps(actions))
    rc, out, err = sh(["computer-use", "act-now", "--actions", str(path),
                       "--agent", AGENT, "--method", METHOD, "--label", "Computer use active"], 180)
    log({"step": "act_now", "tag": tag, "rc": rc, "out": out[:600], "err": err[:300]})
    return rc


def observe(tag):
    rc, out, err = sh(["computer-use", "observe", "--window", ZEN_ADDR, "--focus"], 120)
    log({"step": "observe", "tag": tag, "rc": rc, "out": out[:800], "err": err[:300]})
    try:
        return json.loads(out)
    except Exception:
        return None


def screen_to_image(meta, sx, sy):
    """Invert cu.image_point: screen = region_xy + image * region_size / image_size."""
    iw, ih = meta["image_size"] if "image_size" in meta else (meta.get("width"), meta.get("height"))
    region = meta.get("region") or meta.get("crop") or [0, 0, iw, ih]
    rx, ry, rw, rh = region
    return (sx - rx) * iw / rw, (sy - ry) * ih / rh


def userway_site(name, query, host):
    tag = f"{MODE}-uw-{name}"
    start = time.monotonic()
    log({"step": "site_start", "tag": tag, "query": query, "host": host})
    # Step 1: focus address bar, type the search query, Enter (user way).
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
    obs = observe(tag + "-serp")
    # Step 2: find the first result link for the host, get its screen point.
    pos = rpc_eval(f"""(() => {{
      const as = [...document.querySelectorAll('a')];
      const a = as.find(x => x.href && x.href.includes('{host}') && x.querySelector('h3'));
      if (!a) return null;
      const r = a.getBoundingClientRect();
      return {{x: window.mozInnerScreenX + r.left + Math.min(r.width / 2, 200),
               y: window.mozInnerScreenY + r.top + r.height / 2,
               href: a.href, dpr: window.devicePixelRatio}};
    }})()""")
    log({"step": "result_pos", "tag": tag, "pos": pos})
    if not pos:
        log({"step": "site_fail", "tag": tag, "reason": "no result link"})
        return
    meta = (obs or {}).get("meta") or obs or {}
    log({"step": "observe_meta_keys", "tag": tag, "keys": sorted(meta.keys())[:20]})
    try:
        ix, iy = screen_to_image(meta, pos["x"] * pos.get("dpr", 1), pos["y"] * pos.get("dpr", 1))
    except Exception as e:
        log({"step": "convert_error", "tag": tag, "error": str(e)})
        ix, iy = pos["x"], pos["y"]
    log({"step": "click_point", "tag": tag, "image_x": round(ix), "image_y": round(iy)})
    act_now([
        {"type": "click", "x": round(ix), "y": round(iy)},
        {"type": "wait", "ms": 2000},
    ], tag + "-click")
    time.sleep(12)
    info = rpc_eval(INFO_EXPR)
    log({"step": "landing", "tag": tag, "elapsed_s": round(time.monotonic() - start, 1), "info": info})
    observe(tag + "-landing")
    # Step 3: interact like a user (scroll), then re-read state.
    act_now([{"type": "scroll", "x": round(ix), "y": round(iy), "dy": 600}, {"type": "wait", "ms": 1000}], tag + "-scroll")
    time.sleep(3)
    info2 = rpc_eval(INFO_EXPR)
    log({"step": "after_interact", "tag": tag, "info": info2})
    observe(tag + "-interacted")


def zen_env():
    import os
    pid = subprocess.run(["pgrep", "-f", "zen-bin --remote-debugging-port"],
                         capture_output=True, text=True).stdout.split()[0]
    env = {}
    raw = Path(f"/proc/{pid}/environ").read_bytes().split(b"\x00")
    for kv in raw:
        if b"=" in kv:
            k, v = kv.decode(errors="replace").split("=", 1)
            env[k] = v
    keep = {k: env[k] for k in ("WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS", "HYPRLAND_INSTANCE_SIGNATURE", "DISPLAY") if k in env}
    log({"step": "zen_env", "pid": pid, "keys": sorted(keep.keys())})
    return keep


def stock_test(url, tag, env, wait_s=30):
    import os
    profile = f"/tmp/zen-stock3-{tag}"
    subprocess.run(["rm", "-rf", profile])
    full_env = dict(os.environ)
    full_env.update(env)
    log({"step": "stock_launch", "tag": tag, "url": url[:80]})
    proc = subprocess.Popen(["/opt/zen-browser-bin/zen-bin", "--profile", profile, "--no-remote", url],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=full_env)
    time.sleep(wait_s)
    shot = OUT / f"stock3-{tag}.png"
    r = subprocess.run(["grim", str(shot)], capture_output=True, text=True, timeout=30, env=full_env)
    size = shot.stat().st_size if shot.exists() else 0
    log({"step": "stock_screenshot", "tag": tag, "file": str(shot), "bytes": size, "grim_rc": r.returncode})
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
    subprocess.run(["rm", "-rf", profile])
    log({"step": "stock_done", "tag": tag, "profile_deleted": True})


def main():
    log({"step": "runner3_start"})
    reply = acquire_overlay(AGENT, METHOD)
    log({"step": "pill_acquired", "visible": overlay_visible(AGENT), "label": reply.get("label")})
    holder = None
    try:
        subprocess.run(["rm", "-rf", str(RPC)])
        RPC.mkdir(parents=True, exist_ok=True)
        holder = subprocess.Popen(["node", "/tmp/council2-harness/holder.mjs", MODE],
                                  stdout=open(OUT / f"holder-{MODE}.log", "w"),
                                  stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 60
        while not (RPC / "ready.json").exists():
            if time.monotonic() > deadline:
                raise TimeoutError("holder not ready")
            time.sleep(0.5)
        log({"step": "holder_ready", "ready": json.loads((RPC / "ready.json").read_text())})
        probe = rpc_eval(INFO_EXPR)
        log({"step": "probe_initial", "info": probe})
        for name, query, host in SITES:
            try:
                userway_site(name, query, host)
            except Exception as e:
                log({"step": "site_error", "site": name, "error": str(e)[:400]})
        if MODE == "preload":
            env = zen_env()
            probe = "data:text/html,<title>wdprobe</title><body><h1 id=w>?</h1><script>document.getElementById('w').textContent='webdriver='+navigator.webdriver</script></body>"
            stock_test(probe, "probe", env, 15)
            stock_test("https://coolors.co", "coolors", env, 30)
            stock_test("https://chatgpt.com", "chatgpt", env, 30)
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
    log({"step": "runner3_done"})


if __name__ == "__main__":
    main()
