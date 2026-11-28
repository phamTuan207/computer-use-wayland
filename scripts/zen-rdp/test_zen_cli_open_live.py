#!/usr/bin/env python3
"""Pilot 2 live smoke: zen_cli open must not move visible selection.

Dual-protocol harness on ONE dedicated throwaway Zen instance that
listens on both a WebDriver BiDi port (--remote-debugging-port) and
an RDP debugger port (--start-debugger-server). BiDi alone cannot
read which tab is selected, so selected-tab ground truth comes from
RDP (listTabs plus parent-process gBrowser.selectedTab), exactly as
measured in pilot2-background-tab.md (2026-11-28). No BiDi-only
assertion is faked here.

Each rep runs the real scripts/zen_cli.py `open` as a subprocess
against the BiDi port, then asserts via RDP that the selected-tab
identity (tag + URI + RDP URL; index and descriptor actor are
positional in Zen and excluded) is unchanged, the new tab exists
and is not selected, and Hyprland focused-window address+class did
not move. The zen_cli result's flash_window_ms (window.open to
re-activate completion, measured inside cmd_open) is recorded per
rep; it is a slight overestimate of the visible steal because it
starts at the evaluate send, before the new tab lands.

Assumes the dual-protocol session is already running (manual launch
with both flags; neither zen_cli session start nor
launch_dedicated.py alone provides both ports). The RDP port owner
pid is verified against --profile-marker before attach (fail
closed). Only tabs this harness opened (unique rep URL marker) are
closed, by parent JS removeTab. The owner session is never touched:
pointed at it, the marker check refuses. No OS input; ydotool is
banned and not used. Test pages are local fixtures on 127.0.0.1.

Usage:
  python3 test_zen_cli_open_live.py --bidi-port <port> \
      --rdp-port <port> --profile-marker <profile-dir> \
      [--zen-cli <path>] [--reps 5] [--out <json-path>]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rdp_client import RDPClient, RDPError, check_port_owner  # noqa: E402

TZ = ZoneInfo("Asia/Ho_Chi_Minh")
TAG_ATTR = "data-pilot2fix"


def now():
    return datetime.now(TZ).isoformat(timespec="milliseconds")


def _page(letter):
    return ("<html><head><title>Pilot2Fix " + letter + "</title></head>"
            "<body><h1>" + letter + "</h1></body></html>")


PAGES = {"/a.html": _page("A"), "/c.html": _page("C")}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        body = PAGES.get(path)
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_args):
        pass


SEL_JS = ("(function(){var tabs=[...gBrowser.tabs];"
          "var sel=gBrowser.selectedTab;"
          "return JSON.stringify({"
          "selectedIndex:tabs.indexOf(sel),"
          "selectedURI:sel.linkedBrowser.currentURI.spec,"
          "selectedTag:sel.getAttribute('" + TAG_ATTR + "')||'',"
          "tabCount:tabs.length,"
          "tabs:tabs.map(function(t,i){return{i:i,"
          "uri:t.linkedBrowser.currentURI.spec,"
          "tag:t.getAttribute('" + TAG_ATTR + "')||'',"
          "selected:t===sel};})});})()")


def _hypr_focus():
    """Focused window address+class only (never the title)."""
    try:
        env = dict(os.environ)
        hypr = Path(f"/run/user/{os.getuid()}") / "hypr"
        if "HYPRLAND_INSTANCE_SIGNATURE" not in env and hypr.is_dir():
            entries = sorted(p.name for p in hypr.iterdir())
            if entries:
                env["HYPRLAND_INSTANCE_SIGNATURE"] = entries[0]
        out = subprocess.run(["hyprctl", "activewindow", "-j"],
                             capture_output=True, text=True, timeout=5,
                             env=env)
        data = json.loads(out.stdout or "{}")
        return {"address": data.get("address"),
                "class": data.get("class")}
    except Exception as e:  # noqa: BLE001 - record, never crash
        return {"error": str(e)[:120]}


def snapshot(client):
    tabs, sel = client.list_tabs()
    parent_raw = client.parent_evaluate(SEL_JS)
    parent = json.loads(parent_raw) if isinstance(parent_raw, str) \
        else parent_raw
    return {
        "ts": now(),
        "rdp": {
            "selected_index": sel,
            "selected_actor": tabs[sel].get("actor"),
            "selected_url": tabs[sel].get("url"),
            "tab_count": len(tabs),
            "tabs": [{"i": i, "actor": t.get("actor"),
                      "url": t.get("url"),
                      "selected": bool(t.get("selected"))}
                     for i, t in enumerate(tabs)],
        },
        "parent": parent,
        "hypr_focus": _hypr_focus(),
    }


def sel_identity(snap):
    """Stable selected identity (tag, URI, RDP URL). Index and
    descriptor actor are positional in Zen and excluded."""
    p = snap["parent"]
    return {"index": p["selectedIndex"], "uri": p["selectedURI"],
            "tag": p["selectedTag"],
            "rdp_actor": snap["rdp"]["selected_actor"],
            "rdp_url": snap["rdp"]["selected_url"],
            "rdp_index": snap["rdp"]["selected_index"]}


def same_selected(before_id, after_id):
    return (before_id["tag"] == after_id["tag"]
            and before_id["uri"] == after_id["uri"]
            and before_id["rdp_url"] == after_id["rdp_url"])


def run_zen_cli(zen_cli, bidi_port, home, *args):
    """One real zen_cli.py invocation; returns (code, parsed, wall_ms)."""
    env = dict(os.environ)
    env["HOME"] = str(home)
    t0 = time.monotonic()
    proc = subprocess.run(
        [sys.executable, str(zen_cli), "--port", str(bidi_port), *args],
        capture_output=True, text=True, timeout=60, env=env)
    wall_ms = round((time.monotonic() - t0) * 1000, 1)
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError:
        parsed = {"ok": False, "raw_stdout": proc.stdout[:500],
                  "stderr": proc.stderr[:500]}
    return proc.returncode, parsed, wall_ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bidi-port", type=int, required=True)
    ap.add_argument("--rdp-port", type=int, required=True)
    ap.add_argument("--profile-marker", required=True,
                    help="substring required in the listening pid "
                         "cmdline (fail-closed)")
    ap.add_argument("--zen-cli", default=None,
                    help="path to zen_cli.py under test (default: "
                         "../zen_cli.py next to this script's dir)")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    zen_cli = Path(args.zen_cli) if args.zen_cli else (
        Path(__file__).resolve().parent.parent / "zen_cli.py")
    results = {"started_at": now(), "bidi_port": args.bidi_port,
               "rdp_port": args.rdp_port,
               "profile_marker": args.profile_marker,
               "zen_cli": str(zen_cli), "reps": []}
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    results["fixture_base"] = base
    home = Path(tempfile.mkdtemp(prefix="zencli-open-live-home-"))
    client = None
    try:
        rdp_pid, _ = check_port_owner(args.rdp_port,
                                      args.profile_marker)
        bidi_pid, _ = check_port_owner(args.bidi_port,
                                       args.profile_marker)
        results["rdp_port_owner_pid"] = rdp_pid
        results["bidi_port_owner_pid"] = bidi_pid
        if rdp_pid != bidi_pid:
            raise RDPError(
                f"BiDi pid {bidi_pid} != RDP pid {rdp_pid}: not one "
                "dual-protocol instance")

        client = RDPClient(args.rdp_port, unscoped_test=True,
                           warn_unscoped=False, allow_parent=True)
        client.attach()
        results["attach_desc"] = client.desc_actor

        client.navigate(base + "/a.html")
        client.wait_load("/a.html", timeout=20)
        tagged = client.parent_evaluate(
            "(function(){var t=[...gBrowser.tabs].find(function(t){"
            "return t.linkedBrowser.currentURI.spec==="
            + json.dumps(base + "/a.html") + ";});"
            "if(t){t.setAttribute('" + TAG_ATTR + "','baseline-A');}"
            "return !!t;})()")
        if not tagged:
            raise RDPError("baseline tab could not be tagged")
        baseline = snapshot(client)
        baseline_id = sel_identity(baseline)
        results["baseline"] = baseline
        results["baseline_identity"] = baseline_id
        if baseline_id["tag"] != "baseline-A":
            raise RDPError(f"baseline not selected: {baseline_id}")

        all_ok = True
        for i in range(args.reps):
            marker = f"rep=live{i}"
            url = f"{base}/c.html?{marker}"
            before = snapshot(client)
            before_id = sel_identity(before)
            # Pin the opener to the baseline tab by its fresh BiDi
            # index, so opener == selected (the common case).
            code, tabs_out, _ = run_zen_cli(
                zen_cli, args.bidi_port, home, "tabs")
            if code != 0 or not tabs_out.get("ok"):
                raise RDPError(f"zen_cli tabs failed: {tabs_out}")
            opener_index = next(
                t["index"] for t in tabs_out["tabs"]
                if t["url"] == base + "/a.html")
            code, opened, wall_ms = run_zen_cli(
                zen_cli, args.bidi_port, home,
                "open", url, "--tab", str(opener_index))
            after = snapshot(client)
            after_id = sel_identity(after)
            new_tab = next(
                (t for t in after["parent"]["tabs"]
                 if marker in (t["uri"] or "")), None)
            rdp_new = next(
                (t for t in after["rdp"]["tabs"]
                 if marker in (t["url"] or "")), None)
            # zen_cli reports the getTree URL at open-return time,
            # which is still about:blank while the new tab is lazy
            # (pre-existing behavior; pilot2 measured the same).
            # Tab identity is therefore asserted against RDP ground
            # truth (index + real URL), not the lazy BiDi URL.
            rep_ok = (
                code == 0 and opened.get("ok") is True
                and opened.get("selection_restored") is True
                and isinstance(opened.get("flash_window_ms"), int)
                and rdp_new is not None
                and opened.get("tab", {}).get("index") == rdp_new["i"]
                and opened.get("tab", {}).get("url") in (url,
                                                         "about:blank")
                and same_selected(before_id, after_id)
                and after_id["tag"] == "baseline-A"
                and new_tab is not None
                and new_tab["selected"] is False
                and rdp_new is not None
                and rdp_new["selected"] is False
                and after["parent"]["tabCount"]
                == before["parent"]["tabCount"] + 1
                and before["hypr_focus"].get("address")
                == after["hypr_focus"].get("address")
                and before["hypr_focus"].get("class")
                == after["hypr_focus"].get("class"))
            # Close only the tab this rep opened (URL marker).
            closed_n = client.parent_evaluate(
                "(function(){var mine=[...gBrowser.tabs].filter("
                "function(t){return t.linkedBrowser.currentURI.spec"
                ".indexOf(" + json.dumps(marker) + ")>=0;});"
                "mine.forEach(function(t){gBrowser.removeTab(t);});"
                "return mine.length;})()")
            time.sleep(0.5)
            after_close = snapshot(client)
            after_close_id = sel_identity(after_close)
            rep_ok = rep_ok and closed_n == 1 \
                and same_selected(before_id, after_close_id) \
                and after_close["parent"]["tabCount"] \
                == before["parent"]["tabCount"]
            all_ok = all_ok and rep_ok
            results["reps"].append({
                "rep": i, "url": url, "opener_bidi_index": opener_index,
                "zen_cli_exit": code, "zen_cli_result": opened,
                "zen_cli_wall_ms": wall_ms,
                "flash_window_ms": opened.get("flash_window_ms"),
                "before": before_id, "after": after_id,
                "selected_unchanged":
                    same_selected(before_id, after_id),
                "new_tab_became_selected":
                    after_id["tag"] != "baseline-A",
                "new_tab_parent": new_tab, "new_tab_rdp": rdp_new,
                "hypr_before": before["hypr_focus"],
                "hypr_after": after["hypr_focus"],
                "tab_count_before": before["parent"]["tabCount"],
                "tab_count_after": after["parent"]["tabCount"],
                "closed_count": closed_n,
                "after_close": after_close_id,
                "after_close_tab_count":
                    after_close["parent"]["tabCount"],
                "rep_ok": rep_ok,
            })

        final = snapshot(client)
        results["final"] = final
        results["final_identity"] = sel_identity(final)
        flashes = [r["flash_window_ms"] for r in results["reps"]
                   if isinstance(r["flash_window_ms"], int)]
        results["flash_window_ms_all"] = flashes
        if flashes:
            results["flash_window_ms_median"] = sorted(flashes)[
                len(flashes) // 2]
            results["flash_window_ms_max"] = max(flashes)
        results["finished_at"] = now()
        results["ok"] = bool(all_ok
                             and same_selected(
                                 baseline_id, sel_identity(final)))
        if args.out:
            Path(args.out).write_text(json.dumps(results, indent=1))
        print(json.dumps(
            {"ok": results["ok"], "reps": len(results["reps"]),
             "flash_window_ms_all": flashes,
             "baseline": baseline_id}, indent=1))
        return 0 if results["ok"] else 1
    except Exception as e:  # noqa: BLE001 - always emit evidence
        results["fatal"] = f"{type(e).__name__}: {e}"
        results["finished_at"] = now()
        results["ok"] = False
        if args.out:
            try:
                Path(args.out).write_text(json.dumps(results, indent=1))
            except Exception:
                pass
        print(json.dumps({"ok": False, "fatal": results["fatal"]},
                         indent=1))
        return 1
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
        server.shutdown()


if __name__ == "__main__":
    sys.exit(main())
