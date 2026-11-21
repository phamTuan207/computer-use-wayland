#!/usr/bin/env python3
"""Hand-drive helper for Worker P agent-think-time samples (21/11/2026).
Reads one JSON command per line on stdin, executes it against live Zen
via geckodriver --connect-existing, prints one JSON result per line.
The AGENT types each command by hand and times its own thinking between
commands, so the wall time per step is real agent time, not script time.
Commands: {"cmd": "new_session"} | {"cmd": "new_tab", "url": ...}
| {"cmd": "find", "css": ...} | {"cmd": "clear", "el": ...}
| {"cmd": "type", "el": ..., "text": ...} | {"cmd": "click", "el": ...}
| {"cmd": "click_js", "js": ...} | {"cmd": "eval", "js": ...}
| {"cmd": "text", "css": ...} | {"cmd": "value", "css": ...}
| {"cmd": "close_tab"} | {"cmd": "delete_session"} | {"cmd": "quit"}
Element ids are returned by find and reused by clear/type/click.
set_file reads a local file, uploads it via the WebDriver /file
endpoint, and sets the file input's value to the remote path.

Metrics mode (Worker Y11, 21/11): --metrics-path/--test/--run-id/
--operator. One step row per command with think_source hand. think_s
comes only from a driver self-reported decided_at (epoch seconds) in
the JSON command; otherwise think_s is null and the row carries
inter_command_gap_s (arrival minus previous result print), which is an
UPPER BOUND on think, never think_s. Click commands run the same
pre-click probe as WD.click (the css is remembered from find);
click_js is excluded from the click rate and disclosed in the summary.
See improvements/worker-y11-design.md.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Live metrics import (same resolution as run_live.py: repo scripts/
# two levels up, else the runner dir, else LIVE_METRICS_DIR).
live_metrics = None
for _cand in (os.environ.get("LIVE_METRICS_DIR") or "",
              str(Path(__file__).resolve().parents[2] / "scripts"),
              str(Path(__file__).resolve().parent)):
    if _cand and Path(_cand, "live_metrics.py").exists():
        if _cand not in sys.path:
            sys.path.insert(0, _cand)
        break
try:
    import live_metrics
except Exception as _lm_exc:  # pragma: no cover - import failure path
    print(f"[metrics] live_metrics unavailable: {_lm_exc}", file=sys.stderr)
    live_metrics = None

WD_PORT = 4450


def wd(method, path, body=None):
    url = f"http://127.0.0.1:{WD_PORT}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def _cmd_detail(cmd, c, find_css):
    """Safe detail for a hand-drive action row (no free text)."""
    try:
        if cmd in ("find", "text", "value"):
            return {"selector": c.get("css", "")}
        if cmd == "click":
            return {"selector": find_css.get(c.get("el"), "")}
        if cmd == "click_js":
            js = c.get("js", "")
            return {"js": str(js)[:200], "js_len": len(str(js))}
        if cmd == "eval":
            js = str(c.get("js", ""))
            return {"script_len": len(js), "has_click": ".click(" in js}
        if cmd == "type":
            return {"text_len": len(c.get("text", ""))}
        if cmd == "set_file":
            return {"filename": Path(c.get("path", "")).name}
        if cmd == "new_tab":
            return {"url": c.get("url", "")}
        return {}
    except Exception:
        return {}


def main():
    parser = argparse.ArgumentParser(
        description="Hand-drive helper for live Zen (Worker P).")
    parser.add_argument("--metrics-path", default=None,
                        help="metrics JSONL path (default from "
                        "LIVE_METRICS env, else "
                        "/tmp/hand-drive-metrics.jsonl)")
    parser.add_argument("--test", default="hand",
                        help="test id for metrics rows")
    parser.add_argument("--run-id", default=None,
                        help="run id (default from LIVE_RUN_ID env, "
                        "else generated)")
    parser.add_argument("--operator", default="human",
                        choices=["human", "agent"],
                        help="who drives: human typing or an agent")
    args = parser.parse_args()
    # Live metrics (Worker Y11): created at startup, not on
    # new_session. One summary row on loop exit (quit, EOF, or error).
    metrics = None
    if live_metrics is not None and os.environ.get("LIVE_METRICS") != "off":
        try:
            mpath = args.metrics_path or os.environ.get("LIVE_METRICS") or \
                live_metrics.default_metrics_path("/tmp/hand-drive-live.jsonl")
            run_id = live_metrics.make_run_id(
                args.run_id or os.environ.get("LIVE_RUN_ID"))
            metrics = live_metrics.LiveMetrics(mpath, run_id)
            metrics.set_test(args.test)
            print(f"[metrics] path={mpath} run={run_id} test={args.test} "
                  f"operator={args.operator}", file=sys.stderr)
        except Exception as exc:
            print(f"[metrics] disabled: {exc}", file=sys.stderr)
            metrics = None
    elif os.environ.get("LIVE_METRICS") == "off":
        print("[metrics] OFF (LIVE_METRICS=off)", file=sys.stderr)
    g = subprocess.Popen(
        ["/tmp/geckodriver", "--connect-existing",
         "--marionette-host", "127.0.0.1", "--marionette-port", "2828",
         "--port", str(WD_PORT), "--log", "warn"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    sid = None
    opened = []
    find_css = {}
    errors = 0
    t_run = time.perf_counter()
    prev_print_epoch = None
    cmd = None
    c = {}
    think_s = None
    gap = None

    def _finish(ok, error):
        # One action row plus the step row, after the result line is
        # printed. prev_print_epoch moves here so the next command's
        # gap starts at the result delivery, not at the metrics write.
        nonlocal prev_print_epoch
        if metrics is not None:
            try:
                metrics.note_action(cmd, _cmd_detail(cmd, c, find_css))
            except Exception:
                pass
            try:
                metrics.finish_step(
                    ok, error, think_s=think_s, think_source="hand",
                    extra={"inter_command_gap_s": (
                        round(gap, 3) if gap is not None else None),
                        "cmd_len": len(line),
                        "operator": args.operator})
            except Exception:
                pass
        prev_print_epoch = time.time()

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                c = json.loads(line)
            except Exception as e:
                print(json.dumps({"ok": False, "error": f"bad json: {e}"}), flush=True)
                continue
            cmd = c.get("cmd")
            t_arrive_epoch = time.time()
            gap = (t_arrive_epoch - prev_print_epoch
                   if prev_print_epoch is not None else None)
            decided_at = c.get("decided_at")
            think_s = None
            if (isinstance(decided_at, (int, float))
                    and prev_print_epoch is not None):
                think_s = decided_at - prev_print_epoch
                if think_s < 0:
                    think_s = None
            if metrics is not None:
                try:
                    mc = c.get("model_calls")
                    if isinstance(mc, int) and mc > 0:
                        metrics.note_model_calls(mc)
                    metrics.begin_step(cmd or "unknown", cmd or "unknown")
                except Exception:
                    pass
            t0 = time.perf_counter()
            try:
                if cmd == "quit":
                    print(json.dumps({"ok": True, "result": "bye"}), flush=True)
                    _finish(True, None)
                    break
                if cmd == "new_session":
                    sid = wd("POST", "/session", {"capabilities": {
                        "alwaysMatch": {"browserName": "firefox"}}})["value"]["sessionId"]
                    out = sid[:8]
                elif cmd == "new_tab":
                    S = f"/session/{sid}"
                    h = wd("POST", S + "/window/new", {"type": "tab"})["value"]["handle"]
                    opened.append(h)
                    wd("POST", S + "/window", {"handle": h})
                    wd("POST", S + "/url", {"url": c["url"]})
                    deadline = time.perf_counter() + 10
                    while time.perf_counter() < deadline:
                        if wd("POST", S + "/execute/sync",
                              {"script": "return document.readyState", "args": []})["value"] == "complete":
                            break
                        time.sleep(0.1)
                    time.sleep(1.0)
                    out = h[:8]
                elif cmd == "find":
                    S = f"/session/{sid}"
                    out = wd("POST", S + "/element",
                             {"using": "css selector", "value": c["css"]})["value"]["element-6066-11e4-a52e-4f735466cecf"]
                    find_css[out] = c["css"]
                elif cmd == "clear":
                    S = f"/session/{sid}"
                    wd("POST", S + f"/element/{c['el']}/clear", {})
                    out = "cleared"
                elif cmd == "type":
                    S = f"/session/{sid}"
                    wd("POST", S + f"/element/{c['el']}/value", {"text": c["text"]})
                    out = "typed"
                elif cmd == "click":
                    S = f"/session/{sid}"
                    # Pre-click probe (same rule as WD.click): the css
                    # is remembered from find. A click without a prior
                    # find has no css and records nothing.
                    probe = None
                    probe_error = None
                    click_error = None
                    css = find_css.get(c.get("el"))
                    if metrics is not None and css \
                            and live_metrics is not None:
                        try:
                            snap = wd("POST", S + "/execute/sync",
                                      {"script": live_metrics.PROBE_JS,
                                       "args": [css]})["value"]
                            if isinstance(snap, dict):
                                probe = snap
                                probe_error = probe.pop("probe_error", None)
                            else:
                                probe_error = ("probe eval returned "
                                               "non-dict sample")
                        except Exception as exc:
                            probe_error = (f"{type(exc).__name__}: {exc}")
                    try:
                        wd("POST", S + f"/element/{c['el']}/click", {})
                    except Exception as exc:
                        click_error = f"{type(exc).__name__}: {exc}"
                        raise
                    finally:
                        if metrics is not None and css:
                            try:
                                metrics.record_click(
                                    css, probe, error=click_error,
                                    probe_error=probe_error)
                            except Exception:
                                pass
                    out = "clicked"
                elif cmd == "click_js":
                    S = f"/session/{sid}"
                    wd("POST", S + "/execute/sync",
                       {"script": c["js"] + ".scrollIntoView({block:'center'}); " + c["js"] + ".click();", "args": []})
                    out = "clicked_js"
                elif cmd == "eval":
                    S = f"/session/{sid}"
                    out = wd("POST", S + "/execute/sync",
                             {"script": c["js"], "args": []})["value"]
                elif cmd == "text":
                    S = f"/session/{sid}"
                    out = wd("POST", S + "/execute/sync",
                             {"script": f"return document.querySelector({json.dumps(c['css'])}).textContent", "args": []})["value"]
                elif cmd == "value":
                    S = f"/session/{sid}"
                    out = wd("POST", S + "/execute/sync",
                             {"script": f"return document.querySelector({json.dumps(c['css'])}).value", "args": []})["value"]
                elif cmd == "set_file":
                    S = f"/session/{sid}"
                    # Geckodriver does NOT implement POST /session/:id/file
                    # (405). Setting the file input's value to a local path
                    # directly is the supported path: geckodriver uploads
                    # it internally.
                    wd("POST", S + f"/element/{c['el']}/value",
                       {"text": c["path"]})
                    out = f"set {c['path']}"
                elif cmd == "close_tab":
                    S = f"/session/{sid}"
                    wd("DELETE", S + "/window", {})
                    out = "closed"
                elif cmd == "delete_session":
                    wd("DELETE", "/session/" + sid, {})
                    out = "deleted"
                    sid = None
                else:
                    raise ValueError(f"unknown cmd {cmd}")
                print(json.dumps({"ok": True, "result": out,
                                  "ms": int((time.perf_counter() - t0) * 1000)}), flush=True)
                _finish(True, None)
            except Exception as e:
                errors += 1
                print(json.dumps({"ok": False, "error": str(e)[:300],
                                  "ms": int((time.perf_counter() - t0) * 1000)}), flush=True)
                _finish(False, f"{type(e).__name__}: {e}")
    finally:
        if metrics is not None:
            try:
                metrics.summary([{"test": args.test,
                                  "pass": errors == 0,
                                  "elapsed_s": time.perf_counter() - t_run}])
            except Exception as exc:
                print(f"[metrics] summary failed: {exc}", file=sys.stderr)
        if sid is not None:
            try:
                wd("DELETE", "/session/" + sid, {})
            except Exception:
                pass
        g.terminate()


if __name__ == "__main__":
    main()
