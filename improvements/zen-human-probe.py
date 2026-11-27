#!/usr/bin/env python3
"""zen-human-probe - startup probe for the flag-free human Zen profile.

Two independent checks:

1. cmdline scan: every zen-bin main process using a real profile
   (under ~/.config/zen, or no --profile argument at all) must carry
   no automation flags (--remote-debugging-port / --marionette).
   A flagged process started before the split adoption timestamp is
   LEGACY (warn only: it is the pre-split session, replaced at the
   owner's next launch). A flagged process started at/after adoption
   is launch-path leakage (FAIL, loud).

2. throwaway reading (full mode only): a flag-free headless instance
   with a throwaway profile loads a local probe page that beacons the
   page-visible navigator.webdriver signal set back over loopback
   HTTP. Asserts webdriver === false (boolean type), native-form
   getter toString, no documentElement webdriver attribute, and no
   automation-looking window globals. This certifies that the
   flag-free launch configuration of this Zen build reads clean; it
   does not read the owner's live session (that would need flags,
   which would change the reading).

Verdicts: CLEAN / LEGACY-FLAGGED / ESCAPE-HATCH / FAIL. Exit 0
unless FAIL. ESCAPE-HATCH means a flagged human-profile process
exists but a fresh escape-hatch marker
(~/.local/state/zen-split/escape-hatch-active, mtime within 4h,
content = task id) declares a deliberate, logged flagged session;
the exception is recorded, never silent.
Every run appends one JSON line to ~/.local/state/zen-split/probe.log.
FAIL also tries notify-send (critical). Stdlib only.
"""

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ZEN_BIN = "/opt/zen-browser-bin/zen-bin"
REAL_PROFILE_HOME = Path.home() / ".config" / "zen"
STATE_DIR = Path.home() / ".local" / "state" / "zen-split"
LOG_PATH = STATE_DIR / "probe.log"
ADOPTED_PATH = STATE_DIR / "adopted-at"
ESCAPE_PATH = STATE_DIR / "escape-hatch-active"
ESCAPE_MAX_AGE_S = 4 * 3600
FLAG_MARKERS = ("--remote-debugging-port", "--marionette")
CHILD_MARKERS = ("-contentproc", "--type=", "-childID")

PROBE_PAGE = """<!DOCTYPE html><html><head><title>zen-human-probe</title></head>
<body>probe</body><script>
(function () {
  var proto = Object.getPrototypeOf(navigator);
  var dProto = Object.getOwnPropertyDescriptor(proto, 'webdriver');
  var dNav = Object.getOwnPropertyDescriptor(navigator, 'webdriver');
  var d = dProto || dNav;
  var suspicious = [];
  try {
    suspicious = Object.keys(window).filter(function (k) {
      return /webdriver|selenium|cdc_/i.test(k);
    });
  } catch (e) {}
  var payload = {
    webdriver: navigator.webdriver,
    webdriver_type: typeof navigator.webdriver,
    own_on_navigator: !!dNav,
    own_on_proto: !!dProto,
    get_name: d && d.get ? d.get.name : null,
    get_tostring: d && d.get ? String(d.get) : null,
    configurable: d ? d.configurable : null,
    enumerable: d ? d.enumerable : null,
    doc_webdriver_attr: document.documentElement
      ? document.documentElement.getAttribute('webdriver') : null,
    plugins_length: navigator.plugins ? navigator.plugins.length : null,
    suspicious_globals: suspicious,
    title: document.title,
    url: location.href
  };
  document.title = 'wd=' + String(payload.webdriver);
  fetch('/report', {method: 'POST', body: JSON.stringify(payload)})
    .catch(function () {});
})();
</script></html>
"""


def log_line(record):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def notify_fail(message):
    try:
        subprocess.run(
            ["notify-send", "-u", "critical",
             "Zen human-profile probe FAIL", message],
            timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def zen_version():
    try:
        out = subprocess.run([ZEN_BIN, "--version"], capture_output=True,
                             text=True, timeout=10)
        return out.stdout.strip() or out.stderr.strip()
    except Exception as exc:
        return "unknown (%s)" % exc


def boot_epoch():
    try:
        with open("/proc/stat", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("btime "):
                    return int(line.split()[1])
    except Exception:
        pass
    return None


def proc_start_epoch(pid, btime):
    try:
        with open("/proc/%d/stat" % pid, encoding="utf-8") as fh:
            fields = fh.read().rsplit(") ", 1)[-1].split()
        # fields[0] is state (field 3 overall); starttime is field 22.
        start_ticks = int(fields[19])
        hz = os.sysconf("SC_CLK_TCK")
        if btime is None:
            return None
        return btime + start_ticks / float(hz)
    except Exception:
        return None


def read_cmdline(pid):
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as fh:
            raw = fh.read()
        return [p.decode("utf-8", "replace") for p in raw.split(b"\0") if p]
    except Exception:
        return []


def profile_arg(cmdline):
    for i, arg in enumerate(cmdline):
        if arg == "--profile" and i + 1 < len(cmdline):
            return cmdline[i + 1]
        if arg.startswith("--profile="):
            return arg.split("=", 1)[1]
        if arg in ("-P", "--ProfileManager"):
            return "<named-profile>"
    return None


def is_real_profile(profile):
    if profile is None:
        return True
    if profile == "<named-profile>":
        return True
    try:
        resolved = Path(profile).expanduser().resolve()
        home = REAL_PROFILE_HOME.resolve()
        return resolved == home or home in resolved.parents
    except Exception:
        return False


def scan_processes():
    """Return list of dicts for zen-bin main processes on real profiles."""
    btime = boot_epoch()
    found = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        cmdline = read_cmdline(pid)
        if not cmdline:
            continue
        if "zen-bin" not in cmdline[0]:
            continue
        joined = " ".join(cmdline)
        if any(m in joined for m in CHILD_MARKERS):
            continue
        profile = profile_arg(cmdline)
        if not is_real_profile(profile):
            continue
        flagged = [m for m in FLAG_MARKERS if m in joined]
        found.append({
            "pid": pid,
            "profile": profile or "<default>",
            "flagged": bool(flagged),
            "flags": flagged,
            "started_epoch": proc_start_epoch(pid, btime),
        })
    return found


def adopted_epoch():
    try:
        return float(ADOPTED_PATH.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def escape_marker():
    """Return marker text if a fresh escape-hatch marker exists."""
    try:
        age = time.time() - ESCAPE_PATH.stat().st_mtime
        if age <= ESCAPE_MAX_AGE_S:
            return ESCAPE_PATH.read_text(encoding="utf-8").strip()[:200]
    except Exception:
        pass
    return None


def cmdline_verdict(processes, adopted):
    flagged = [p for p in processes if p["flagged"]]
    if not flagged:
        return "CLEAN", flagged
    if adopted is None:
        return "LEGACY-FLAGGED", flagged
    leaks = [p for p in flagged
             if p["started_epoch"] is not None and p["started_epoch"] >= adopted]
    if leaks:
        if escape_marker() is not None:
            return "ESCAPE-HATCH", leaks
        return "FAIL", leaks
    return "LEGACY-FLAGGED", flagged


class ProbeHandler(BaseHTTPRequestHandler):
    report = None
    event = threading.Event()

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/probe.html"):
            body = PROBE_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path.startswith("/report"):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            try:
                ProbeHandler.report = json.loads(raw.decode("utf-8"))
            except Exception:
                ProbeHandler.report = {"raw": raw.decode("utf-8", "replace")}
            ProbeHandler.event.set()
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


def throwaway_reading(timeout_s=40):
    """Flag-free headless throwaway instance; returns (ok, detail)."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), ProbeHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    tmp_profile = tempfile.mkdtemp(prefix="zen-human-probe-")
    log_fh = open(os.path.join(tmp_profile, "zen.log"), "wb")
    proc = None
    try:
        proc = subprocess.Popen(
            [ZEN_BIN, "--headless", "--no-remote", "--profile", tmp_profile,
             "http://127.0.0.1:%d/probe.html" % port],
            stdin=subprocess.DEVNULL, stdout=log_fh, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        got = ProbeHandler.event.wait(timeout=timeout_s)
        if not got:
            return False, {"error": "no beacon within %ds" % timeout_s,
                           "pid": proc.pid}
        payload = ProbeHandler.report or {}
        getter = payload.get("get_tostring") or ""
        ok = (
            payload.get("webdriver") is False
            and payload.get("webdriver_type") == "boolean"
            and getter.startswith("function webdriver()")
            and payload.get("doc_webdriver_attr") is None
            and not payload.get("suspicious_globals")
        )
        return ok, {"payload": payload, "pid": proc.pid}
    finally:
        if proc is not None and proc.poll() is None:
            # Kill by recorded pid, only after a cmdline profile check
            # (never a compositor window close; headless has no window).
            cmdline = read_cmdline(proc.pid)
            if tmp_profile in " ".join(cmdline):
                try:
                    os.kill(proc.pid, signal.SIGTERM)
                    proc.wait(timeout=5)
                except Exception:
                    try:
                        os.kill(proc.pid, signal.SIGKILL)
                    except Exception:
                        pass
        try:
            log_fh.close()
        except Exception:
            pass
        server.shutdown()
        shutil.rmtree(tmp_profile, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("full", "cmdline"), default="full")
    args = parser.parse_args()

    adopted = adopted_epoch()
    processes = scan_processes()
    verdict, offenders = cmdline_verdict(processes, adopted)

    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "mode": args.mode,
        "zen_version": zen_version(),
        "adopted_epoch": adopted,
        "escape_marker": escape_marker(),
        "real_profile_processes": processes,
        "cmdline_verdict": verdict,
    }

    if args.mode == "full":
        ok, detail = throwaway_reading()
        record["throwaway_ok"] = ok
        record["throwaway"] = detail
        if not ok:
            verdict = "FAIL"
        elif verdict == "CLEAN":
            verdict = "CLEAN"

    record["verdict"] = verdict
    log_line(record)
    print(json.dumps(record, indent=2))

    if verdict == "FAIL":
        notify_fail(
            "Human Zen profile presents automation signals "
            "(see ~/.local/state/zen-split/probe.log)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
