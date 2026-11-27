#!/usr/bin/env python3
"""R10 seamless W4: production-shaped RDP client (stdlib only).

Extends the W2 minimal RDP pattern (~/workspace/r10-seamless-w2/w2_rdp*.py):
connect, listTabs, getTarget, evaluateJSAsync, navigateTo. Adds:
- port-owner guard (refuses if the listening pid is not the expected
  throwaway browser, matched by profile marker in its cmdline)
- fail-loud webdriver probe (exit nonzero if webdriver is not native false)
- navigate-to-load polling, latency bench

Runs on the laptop next to the browser. No geckodriver, no DevTools
frontend. ydotool is banned (not used here; this client sends no OS input).
"""
import argparse
import json
import re
import socket
import subprocess
import sys
import time


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def ms(sec):
    return round(sec * 1000, 1)


class RDPError(Exception):
    pass


def check_port_owner(port, marker):
    """Refuse unless the process listening on `port` looks like the expected
    throwaway browser (cmdline contains `marker`). Returns (pid, cmdline)."""
    try:
        out = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True,
                             timeout=10).stdout
    except Exception as e:
        raise RDPError(f"port-owner check failed to run ss: {e}")
    pid = None
    for line in out.splitlines():
        if re.search(rf":{port}\s", line):
            m = re.search(r"pid=(\d+)", line)
            if m:
                pid = int(m.group(1))
                break
    if pid is None:
        raise RDPError(
            f"port {port}: no listening pid found via ss -tlnp "
            f"(browser not running, or port owned by another process)")
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            cmd = f.read().replace(b"\0", b" ").decode(errors="replace")
    except OSError as e:
        raise RDPError(f"port {port}: cannot read cmdline of pid {pid}: {e}")
    if marker and marker not in cmd:
        raise RDPError(
            f"port {port} is bound by pid {pid} whose cmdline does not contain "
            f"expected marker {marker!r}; refusing to attach. cmdline: {cmd[:300]}")
    return pid, cmd


class RDPClient:
    def __init__(self, port, host="127.0.0.1", timeout=15):
        self.port = port
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.buf = b""
        self.greeting = self._recv()
        self.desc_actor = None
        self.target_actor = None
        self.console_actor = None

    def _fill(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RDPError("RDP socket closed by server")
            self.buf += chunk

    def _recv(self):
        self._fill(1)
        colon = self.buf.find(b":")
        while colon == -1:
            self._fill(len(self.buf) + 1)
            colon = self.buf.find(b":")
        length = int(self.buf[:colon])
        self._fill(colon + 1 + length)
        raw = self.buf[colon + 1: colon + 1 + length]
        self.buf = self.buf[colon + 1 + length:]
        return json.loads(raw.decode())

    def _send(self, obj):
        data = json.dumps(obj).encode()
        self.sock.sendall(f"{len(data)}:".encode() + data)

    def request(self, obj, expect_from=None, timeout=15, expect_key=None):
        self.sock.settimeout(timeout)
        self._send(obj)
        while True:
            msg = self._recv()
            if expect_from is not None and msg.get("from") != expect_from:
                continue
            # Unsolicited root events (e.g. tabListChanged) also carry
            # from=root; require the response key when asked.
            if expect_key is not None and expect_key not in msg \
                    and not msg.get("error"):
                continue
            if msg.get("error"):
                raise RDPError(f"RDP error for {obj.get('type')}: {msg}")
            return msg

    def list_tabs(self):
        msg = self.request({"to": "root", "type": "listTabs"},
                           expect_from="root", expect_key="tabs")
        tabs = msg.get("tabs", [])
        if not tabs:
            raise RDPError(f"listTabs returned no tabs: {msg}")
        # Zen fresh profiles have 2 tabs; the VISIBLE one carries
        # selected=true (msg["selected"] is null on this build). Picking
        # index 0 attaches to a background tab (W4 smoke finding).
        sel = None
        for i, t in enumerate(tabs):
            if t.get("selected") is True:
                sel = i
                break
        if sel is None:
            s = msg.get("selected", 0)
            sel = s if isinstance(s, int) and 0 <= s < len(tabs) else 0
        self.desc_actor = tabs[sel]["actor"]
        return tabs, sel

    def refresh_target(self):
        """Re-list tabs and re-get the target (after navigation the
        windowGlobalTarget is replaced; the visible tab stays selected)."""
        self.list_tabs()
        self.get_target()
        return self

    def get_target(self):
        if not self.desc_actor:
            self.list_tabs()
        msg = self.request({"to": self.desc_actor, "type": "getTarget"},
                           expect_from=self.desc_actor)
        frame = msg.get("frame") or msg.get("target") or {}
        self.target_actor = frame.get("actor") or msg.get("actor")
        self.console_actor = frame.get("consoleActor")
        if not self.console_actor and self.target_actor:
            # Fallback: attach on the target and read consoleActor from reply.
            try:
                self._send({"to": self.target_actor, "type": "attach"})
                for _ in range(8):
                    m = self._recv()
                    if m.get("from") != self.target_actor:
                        continue
                    if m.get("consoleActor"):
                        self.console_actor = m["consoleActor"]
                        break
                    if m.get("error"):
                        break
            except Exception:
                pass
        if not self.console_actor:
            raise RDPError(f"getTarget gave no consoleActor: {str(msg)[:500]}")
        return frame

    def attach(self):
        """connect already done in __init__; listTabs + getTarget."""
        self.list_tabs()
        self.get_target()
        return self

    @staticmethod
    def _unwrap(grip):
        if isinstance(grip, dict) and "type" in grip:
            t = grip["type"]
            if t in ("boolean", "number", "string"):
                return grip.get("value")
            if t == "null":
                return None
            if t == "undefined":
                return None
            return grip
        return grip

    def evaluate(self, expr, timeout=20):
        if not self.console_actor:
            raise RDPError("evaluate before attach (no console actor)")
        self.sock.settimeout(timeout)
        self._send({"to": self.console_actor, "type": "evaluateJSAsync",
                    "text": expr})
        while True:
            m = self._recv()
            if m.get("type") == "evaluationResult":
                if m.get("exception"):
                    raise RDPError(f"evaluate exception: {str(m)[:400]}")
                return self._unwrap(m.get("result"))
            if m.get("error"):
                raise RDPError(f"evaluate error: {str(m)[:400]}")

    def navigate(self, url):
        """navigateTo via target actor, fallback to descriptor actor.
        Navigation may replace the windowGlobalTarget, so re-attach after."""
        last = None
        sent = False
        for actor in (self.target_actor, self.desc_actor):
            if not actor:
                continue
            try:
                self.request({"to": actor, "type": "navigateTo",
                              "url": url}, expect_from=actor)
                sent = True
                break
            except Exception as e:
                last = e
        if not sent:
            raise RDPError(f"navigateTo failed for {url}: {last}")
        time.sleep(0.05)
        try:
            self.list_tabs()
            self.get_target()
        except Exception:
            pass  # wait_load re-attaches as needed

    def wait_load(self, url_substr, timeout=30):
        deadline = time.monotonic() + timeout
        last_reattach = 0.0
        while time.monotonic() < deadline:
            try:
                v = self.evaluate(
                    "document.readyState + '|' + location.href", timeout=5)
            except Exception:
                v = None
            if isinstance(v, str) and v.startswith("complete|") \
                    and url_substr in v:
                return v
            # Stale target after navigation: refresh actors periodically.
            if time.monotonic() - last_reattach > 1.0:
                last_reattach = time.monotonic()
                try:
                    self.list_tabs()
                    self.get_target()
                except Exception:
                    pass
            time.sleep(0.05)
        raise RDPError(f"wait_load timeout for {url_substr!r}")

    def probe_webdriver(self):
        """Small evaluates (short grips). Raises RDPError unless native false."""
        wd = self.evaluate("navigator.webdriver")
        typ = self.evaluate("typeof navigator.webdriver")
        getter = self.evaluate(
            "Object.getOwnPropertyDescriptor("
            "Object.getPrototypeOf(navigator),'webdriver').get.toString()")
        doc_attr = self.evaluate(
            "document.documentElement ? "
            "String(document.documentElement.getAttribute('webdriver')) : 'none'")
        plugins = self.evaluate("navigator.plugins ? navigator.plugins.length : -1")
        globals_found = self.evaluate(
            "['cdc_adoQpoasnfa76pfcZLmcfl_Array','__webdriver_evaluate',"
            "'__driver_evaluate','__webdriver_script_fn']"
            ".filter(k => k in window).join(',')")
        probe = {
            "webdriver": wd, "webdriver_type": typ, "getter_tostring": getter,
            "doc_webdriver_attr": doc_attr, "plugins_length": plugins,
            "automation_globals": globals_found,
        }
        native = isinstance(getter, str) and getter.startswith(
            "function webdriver()")
        if wd is not False or typ != "boolean" or not native:
            raise RDPError(
                f"webdriver probe NOT clean (fail-loud): {json.dumps(probe)}")
        probe["verdict"] = "CLEAN"
        return probe

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


def bench(port, marker, local_url, real_url, runs):
    if marker:
        check_port_owner(port, marker)
    out = {"port": port, "runs": runs}
    # attach-to-first-evaluate: fresh connection each run
    xs = []
    for _ in range(runs):
        t0 = time.monotonic()
        c = RDPClient(port)
        c.attach()
        v = c.evaluate("1+1")
        xs.append(time.monotonic() - t0)
        assert v == 2, f"1+1 gave {v!r}"
        c.close()
    out["attach_to_first_evaluate"] = {
        "median_ms": ms(median(xs)), "runs_ms": [ms(x) for x in xs]}
    # held connection for the rest
    c = RDPClient(port)
    c.attach()
    out["probe"] = c.probe_webdriver()
    xs = []
    for _ in range(max(runs, 20)):
        t0 = time.monotonic()
        c.evaluate("1+1")
        xs.append(time.monotonic() - t0)
    out["evaluate_trivial"] = {
        "median_ms": ms(median(xs)), "runs_ms": [ms(x) for x in xs]}
    xs = []
    for _ in range(max(runs, 20)):
        t0 = time.monotonic()
        c.evaluate("document.querySelectorAll('*').length")
        xs.append(time.monotonic() - t0)
    out["evaluate_dom_read"] = {
        "median_ms": ms(median(xs)), "runs_ms": [ms(x) for x in xs]}
    # navigate-to-load, local then real, alternating with about:blank
    for label, url, substr in (("navigate_local", local_url, "slice"),
                               ("navigate_real", real_url, "example")):
        xs = []
        for _ in range(runs):
            c.navigate("about:blank")
            c.wait_load("about:blank", timeout=15)
            t0 = time.monotonic()
            c.navigate(url)
            c.wait_load(substr, timeout=30)
            xs.append(time.monotonic() - t0)
        out[label] = {"url": url, "median_ms": ms(median(xs)),
                      "runs_ms": [ms(x) for x in xs]}
    c.close()
    return out


def main():
    ap = argparse.ArgumentParser(description="RDP client (W4 slice)")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--profile-marker", default=None,
                    help="substring required in the listening pid cmdline")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    e = sub.add_parser("eval")
    e.add_argument("expr")
    n = sub.add_parser("navigate")
    n.add_argument("url")
    b = sub.add_parser("bench")
    b.add_argument("--local-url", required=True)
    b.add_argument("--real-url", default="https://example.com/")
    b.add_argument("--runs", type=int, default=12)
    args = ap.parse_args()
    try:
        if args.cmd == "bench":
            print(json.dumps(bench(args.port, args.profile_marker,
                                   args.local_url, args.real_url,
                                   args.runs), indent=1))
            return 0
        if args.profile_marker:
            pid, _ = check_port_owner(args.port, args.profile_marker)
            print(json.dumps({"port_owner_pid": pid}), file=sys.stderr)
        c = RDPClient(args.port)
        c.attach()
        if args.cmd == "probe":
            print(json.dumps(c.probe_webdriver(), indent=1))
        elif args.cmd == "eval":
            print(json.dumps({"result": c.evaluate(args.expr)}, indent=1))
        elif args.cmd == "navigate":
            c.navigate(args.url)
            print(json.dumps({"navigated": args.url}))
        c.close()
        return 0
    except RDPError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: unexpected {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
