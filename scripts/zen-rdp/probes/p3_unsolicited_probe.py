#!/usr/bin/env python3
"""P3 spike probe: which event classes arrive UNSOLICITED on our RDP socket?

Evidence only (decision doc: improvements/zen-mcp-adoption-decision-20261127.md,
"P3 browser event feed: SPIKE FIRST, library-mode only"). This probe does
NOT build the feed. It answers one question: do coarse lifecycle events
(tab changes, navigation, target destruction) arrive reliably enough on
the raw RDP socket for a library-mode feed?

Method: a standalone raw RDP client (same length-prefixed JSON framing
as rdp_client.py) that, unlike RDPClient.request(), LOGS every packet
it skips instead of discarding it silently. Each packet is classified
solicited (the response a request was waiting for) or unsolicited
(arrived while waiting for something else, or during an idle drain).
The probe performs tab/navigation operations, then a tab-restore storm
shape (many tabs opened rapidly while requests are in flight) and
verifies request/response pairing stays correct (demux proof).

Discipline (from the decision doc spike scope):
- Bounded 200-entry log with dropped-count flag.
- Cursor read only (entries carry seq numbers; read from cursor).
- I22 redaction (rdp_client._redact_url / _redact_text) applied BEFORE
  any URL is logged.
- NO long-poll, NO reader thread in the shipped client, NO server-side
  watches. This probe is synchronous: unsolicited packets are observed
  inside request() waits and in short idle drains. It subscribes to
  nothing server-side; whatever arrives, arrives unasked.

Usage (dedicated throwaway session only, never the owner's Zen):
  python3 p3_unsolicited_probe.py --port 9235 \
      --profile-marker <profile-dir-substr> \
      [--fixture-url http://127.0.0.1:<port>/page.html] \
      [--storm-tabs 12] [--out probe-log.json]

Output: JSON with packet-class inventory, demux proof result, and the
bounded event log. Exit 0 on completion (evidence, not pass/fail);
exit 1 on transport failure. Stdlib only. ydotool banned (not used).
"""
import argparse
import json
import socket
import sys
import time
from collections import Counter, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rdp_client import _redact_text, _redact_url, check_port_owner

MAX_LOG = 200


def _now_ms():
    return round(time.monotonic() * 1000, 1)


class BoundedLog:
    """Bounded 200-entry log with dropped-count flag, cursor read only."""

    def __init__(self, capacity=MAX_LOG):
        self.capacity = capacity
        self._entries = deque(maxlen=capacity)
        self.dropped = 0
        self._seq = 0

    def append(self, entry):
        self._seq += 1
        entry = dict(entry, seq=self._seq)
        if len(self._entries) >= self.capacity:
            self.dropped += 1
        self._entries.append(entry)
        return entry

    def read_from(self, cursor):
        """Cursor read: entries with seq > cursor, plus next cursor."""
        out = [e for e in self._entries if e["seq"] > cursor]
        nxt = out[-1]["seq"] if out else cursor
        return out, nxt

    def snapshot(self):
        return {
            "capacity": self.capacity,
            "retained": len(self._entries),
            "dropped": self.dropped,
            "dropped_flag": self.dropped > 0,
            "entries": list(self._entries),
        }


def _summarize_packet(pkt):
    """Redacted one-line summary of a packet for the log. URLs pass
    through I22 redaction BEFORE they are stored."""
    summary = {
        "from": pkt.get("from"),
        "type": pkt.get("type"),
        "keys": sorted(k for k in pkt.keys() if k not in ("from", "type")),
    }
    url = pkt.get("url")
    if isinstance(url, str):
        summary["url"] = _redact_url(url)
    # Tab payloads carry urls inside; count them, never log raw.
    tabs = pkt.get("tabs")
    if isinstance(tabs, list):
        summary["tab_count"] = len(tabs)
    err = pkt.get("error")
    if err:
        summary["error"] = _redact_text(str(err))[:200]
    return summary


class ProbeClient:
    """Raw RDP client with demux logging. Mirrors RDPClient framing;
    request() logs skipped (unsolicited) packets instead of dropping
    them silently, which is the whole point of the spike."""

    def __init__(self, port, host="127.0.0.1", timeout=15):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.buf = b""
        self.log = BoundedLog()
        self.unsolicited_classes = Counter()
        self.solicited = 0
        self.demux_checks = []
        self.greeting = self._recv_raw()
        self._log_packet(self.greeting, solicited=True, context="greeting")

    # -- framing ------------------------------------------------------
    def _fill(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("RDP socket closed by server")
            self.buf += chunk

    def _recv_raw(self):
        self._fill(1)
        colon = self.buf.find(b":")
        while colon == -1:
            self._fill(len(self.buf) + 1)
            colon = self.buf.find(b":")
        length = int(self.buf[:colon])
        self._fill(colon + 1 + length)
        raw = self.buf[colon + 1: colon + 1 + length]
        self.buf = self.buf[colon + 1 + length:]
        return json.loads(raw.decode("utf-8"))

    def _send(self, obj):
        data = json.dumps(obj).encode("utf-8")
        self.sock.sendall(f"{len(data)}:".encode("ascii") + data)

    # -- logging ------------------------------------------------------
    def _log_packet(self, pkt, solicited, context):
        entry = {
            "at_ms": _now_ms(),
            "solicited": solicited,
            "context": context,
            **_summarize_packet(pkt),
        }
        self.log.append(entry)
        if not solicited:
            cls = pkt.get("type") or f"from:{pkt.get('from')}"
            self.unsolicited_classes[str(cls)] += 1
        else:
            self.solicited += 1
        return entry

    # -- demuxing request (the behaviour under test) ------------------
    def request(self, obj, expect_from=None, expect_key=None,
                expect_type=None, timeout=15, context=""):
        """Send obj, then read packets until the matching response.
        Every non-matching packet is logged as unsolicited (this is
        exactly where RDPClient.request() silently `continue`s)."""
        self.sock.settimeout(timeout)
        self._send(obj)
        waited = 0
        while True:
            msg = self._recv_raw()
            if expect_from is not None and msg.get("from") != expect_from:
                self._log_packet(msg, solicited=False, context=context)
                waited += 1
                continue
            if expect_key is not None and expect_key not in msg \
                    and not msg.get("error"):
                self._log_packet(msg, solicited=False, context=context)
                waited += 1
                continue
            if expect_type is not None and msg.get("type") != expect_type \
                    and not msg.get("error"):
                self._log_packet(msg, solicited=False, context=context)
                waited += 1
                continue
            self._log_packet(msg, solicited=True, context=context)
            if msg.get("error"):
                raise RuntimeError(f"RDP error for {obj.get('type')}: {msg}")
            self.demux_checks.append({
                "request": obj.get("type"), "context": context,
                "unsolicited_skipped": waited, "paired": True,
            })
            return msg

    def drain_idle(self, seconds, context="idle-drain"):
        """Short idle drain: collect whatever arrives unsolicited with
        no request in flight. NOT a long-poll: fixed short window."""
        self.sock.settimeout(seconds)
        got = 0
        try:
            while True:
                msg = self._recv_raw()
                self._log_packet(msg, solicited=False, context=context)
                got += 1
        except (socket.timeout, TimeoutError):
            pass
        finally:
            self.sock.settimeout(15)
        return got

    # -- operations ---------------------------------------------------
    def list_tabs(self, context="listTabs"):
        msg = self.request({"to": "root", "type": "listTabs"},
                           expect_from="root", expect_key="tabs",
                           context=context)
        return msg.get("tabs", [])

    def get_target(self, desc_actor, context="getTarget"):
        msg = self.request({"to": desc_actor, "type": "getTarget"},
                           expect_from=desc_actor, context=context)
        frame = msg.get("frame") or msg.get("target") or {}
        return frame

    def evaluate(self, console_actor, expr, context="evaluate"):
        self._send({"to": console_actor, "type": "evaluateJSAsync",
                    "text": expr})
        self.sock.settimeout(20)
        waited = 0
        while True:
            m = self._recv_raw()
            if m.get("type") == "evaluationResult":
                self._log_packet(m, solicited=True, context=context)
                self.demux_checks.append({
                    "request": "evaluateJSAsync", "context": context,
                    "unsolicited_skipped": waited, "paired": True,
                })
                if m.get("exception"):
                    raise RuntimeError(f"evaluate exception: {str(m)[:300]}")
                res = m.get("result") or {}
                if isinstance(res, dict) and "value" in res:
                    return res["value"]
                return res
            if m.get("error"):
                self._log_packet(m, solicited=True, context=context)
                raise RuntimeError(f"evaluate error: {str(m)[:300]}")
            self._log_packet(m, solicited=False, context=context)
            waited += 1

    def parent_console(self, context="parent"):
        procs = self.request({"to": "root", "type": "listProcesses"},
                             expect_from="root", expect_key="processes",
                             context=context)
        plist = procs.get("processes") or []
        parent = next((p for p in plist if p.get("isParent")), plist[0])
        desc = parent.get("actor")
        tgt = self.request({"to": desc, "type": "getTarget"},
                           expect_from=desc, context=context)
        frame = tgt.get("frame") or tgt.get("target") \
            or tgt.get("process") or {}
        return frame.get("consoleActor")

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


def run_probe(port, fixture_url, storm_tabs):
    c = ProbeClient(port)
    phases = []
    try:
        # Phase 1: attach + basic ops, watch for unsolicited packets.
        tabs = c.list_tabs("phase1-listTabs")
        phases.append({"phase": "attach", "tabs": len(tabs)})
        c.drain_idle(0.5, "phase1-idle-after-listTabs")
        desc = next((t["actor"] for t in tabs if t.get("selected")),
                    tabs[0]["actor"])
        frame = c.get_target(desc, "phase1-getTarget")
        console = frame.get("consoleActor")
        phases.append({"phase": "getTarget", "console": bool(console)})
        c.drain_idle(0.5, "phase1-idle-after-getTarget")
        if console:
            v = c.evaluate(console, "1+1", "phase1-evaluate")
            phases.append({"phase": "evaluate", "result": v})
        c.drain_idle(0.5, "phase1-idle-after-evaluate")

        # Phase 2: navigation in the pinned tab.
        target_actor = frame.get("actor") or desc
        if fixture_url:
            c.request({"to": target_actor, "type": "navigateTo",
                       "url": fixture_url},
                      expect_from=target_actor, context="phase2-navigate")
            phases.append({"phase": "navigate", "url": _redact_url(fixture_url)})
            c.drain_idle(1.0, "phase2-idle-after-navigate")
            # Re-attach (target may have been replaced).
            tabs2 = c.list_tabs("phase2-listTabs")
            frame2 = c.get_target(desc, "phase2-getTarget")
            console2 = frame2.get("consoleActor") or console
            if console2:
                state = c.evaluate(
                    console2,
                    "document.readyState + '|' + location.href",
                    "phase2-evaluate-state")
                phases.append({"phase": "nav-state",
                               "state": _redact_text(str(state))})
            c.drain_idle(0.5, "phase2-idle-after-state")

        # Phase 3: tab-restore storm shape. Open many tabs rapidly via
        # parent JS while interleaving requests; demux must keep
        # request/response pairing correct throughout.
        pconsole = c.parent_console("phase3-parent")
        phases.append({"phase": "parent-console", "ok": bool(pconsole)})
        opened = 0
        if pconsole:
            for i in range(storm_tabs):
                url = fixture_url or "about:blank"
                c.evaluate(
                    pconsole,
                    "gBrowser.addTrustedTab("
                    + json.dumps(url) + "); 'opened'",
                    f"phase3-open-{i}")
                opened += 1
                # Interleave a request while tab churn is in flight.
                c.list_tabs(f"phase3-listTabs-{i}")
            phases.append({"phase": "storm-open", "opened": opened})
            c.drain_idle(1.0, "phase3-idle-after-storm")
            tabs3 = c.list_tabs("phase3-final-listTabs")
            phases.append({"phase": "storm-final-tabs",
                           "tabs": len(tabs3)})
            # Close the storm tabs (keep the first two: fresh profile
            # starts with 2). Close from the end backwards.
            c.evaluate(
                pconsole,
                "(function(){var t=gBrowser.tabs;"
                "for(var i=t.length-1;i>=2;i--){gBrowser.removeTab(t[i]);}"
                "return gBrowser.tabs.length;})()",
                "phase3-close-storm")
            c.drain_idle(1.0, "phase3-idle-after-close")
            tabs4 = c.list_tabs("phase3-after-close-listTabs")
            phases.append({"phase": "after-close-tabs",
                           "tabs": len(tabs4)})
    finally:
        c.close()

    paired = all(d["paired"] for d in c.demux_checks)
    return {
        "probe": "p3-unsolicited-packet-inventory",
        "port": port,
        "fixture_url": _redact_url(fixture_url) if fixture_url else None,
        "storm_tabs": storm_tabs,
        "phases": phases,
        "unsolicited_classes": dict(c.unsolicited_classes),
        "solicited_packets": c.solicited,
        "demux": {
            "requests": len(c.demux_checks),
            "all_paired": paired,
            "max_unsolicited_skipped_in_one_request": max(
                (d["unsolicited_skipped"] for d in c.demux_checks),
                default=0),
            "checks": c.demux_checks,
        },
        "log": c.log.snapshot(),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--profile-marker", default=None,
                    help="substring required in listening pid cmdline "
                         "(fail-closed; dedicated session only)")
    ap.add_argument("--fixture-url", default=None)
    ap.add_argument("--storm-tabs", type=int, default=12)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.profile_marker:
        pid, _ = check_port_owner(args.port, args.profile_marker)
        print(f"port-owner pid={pid} marker ok", file=sys.stderr)
    result = run_probe(args.port, args.fixture_url, args.storm_tabs)
    text = json.dumps(result, indent=1)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
