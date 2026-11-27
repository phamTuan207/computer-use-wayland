#!/usr/bin/env python3
"""P2b settling tests (code only; P2b itself is NOT landed).

Decision authority: improvements/zen-mcp-adoption-decision-20261127.md,
section "P2 refs + digest + ambiguity refusal: SPLIT". The persistent
ref registry + cross-call digest re-verification is gated on two
settling tests that must pass before the registry ships:

(a) Fault-injection delivery test: drop the RDP response after a click
    fires in-page (via a small TCP proxy between client and server that
    drops the response packet); the in-page submit counter must stay 1
    with retry=unsafe. Single-eval atomicity closes the TOCTOU half but
    NOT transport-level retry of a delivery_uncertain act eval:
    atomicity in-page is not idempotency across the socket. This test
    proves the current client never replays a delivery_uncertain act
    (no double-submit) and that the envelope marks retry=unsafe.

(b) Two identical "Confirm" buttons swap/mutation test: descriptor
    digest shows descriptor stability, NOT element identity. Two
    buttons with identical descriptor fields have equal digests; after
    a DOM swap/replacement the digest still matches while the element
    is a different node. This bounds what a digest can claim: it
    detects descriptor change, it does not prove same-element.

Both live tests need a dedicated throwaway RDP session and SKIP
cleanly when none is available (env RDP_TEST_PORT unset, port not
listening, or profile-marker check fails). Pure-Python unit tests for
the digest function and the proxy framing always run, so the suite
collects and passes without a browser.

Live run (dedicated session only, never the owner's Zen):
  RDP_TEST_PORT=9235 RDP_TEST_PROFILE_MARKER=<profile-dir-substr> \\
    python3 -m unittest test_p2b_settling -v

Fixture pages are served by an in-process HTTP server on 127.0.0.1
(ephemeral port); no external network, no real accounts.
ydotool is banned (not used). Stdlib only.
"""
import hashlib
import json
import os
import socket
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rdp_client as rc
from rdp_client import RDPClient, RDPError, Scope, check_port_owner


# ---------------------------------------------------------------------------
# Descriptor digest (reference definition for P2b; the registry does not
# exist yet, so this test pins the semantics the registry must honour).
# Fields follow the snapshot element record in the decision doc: tag,
# role, type, label, placeholder, href, disabled, checked, readOnly,
# sensitive, editable. Value is NEVER part of the digest (value-presence
# metadata only). Digest is a hash of the canonical field tuple.
#
# Mapping to the shipped SNAPSHOT_JS element record (rdp_client.py),
# which emits {tag, name, type, hasValue, href, role}:
#   tag         <-> tag            (same)
#   role        <-> role           (same; snapshot omits when absent)
#   type        <-> type           (same; form controls only)
#   label       <-> name           (snapshot name = aria-label, else
#                                   visible text, else placeholder,
#                                   else name attr; the digest label
#                                   is the accessible-name analogue)
#   placeholder <-> (folded into snapshot name fallback; not separate)
#   href        <-> href           (same; anchors only, capped)
#   disabled / checked / readOnly / sensitive / editable
#               <-> NOT emitted by SNAPSHOT_JS today (the digest is a
#                   superset proposal for the P2b registry; a future
#                   snapshot revision would add them, presence-only)
#   hasValue    <-> NOT in the digest (value-presence metadata;
#                   a value change must not look like identity change)
# ---------------------------------------------------------------------------
DESCRIPTOR_FIELDS = (
    "tag", "role", "type", "label", "placeholder", "href",
    "disabled", "checked", "readOnly", "sensitive", "editable",
)


def descriptor_digest(desc):
    """Stable digest of a descriptor dict. Missing fields default to
    None/False so partial descriptors hash deterministically. Two
    descriptors with equal field values have equal digests even when
    they describe different DOM nodes (that is the point of test (b))."""
    canon = tuple(desc.get(f) for f in DESCRIPTOR_FIELDS)
    raw = json.dumps(canon, separators=(",", ":"), sort_keys=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# In-page JS: read a descriptor for an element, in the same field order.
DESCRIPTOR_JS = (
    "(function(el){"
    "function lab(e){"
    " var t=(e.getAttribute('aria-label')||'').trim();"
    " if(t) return t;"
    " if(e.id){var l=document.querySelector('label[for=\"'+e.id+'\"]');"
    "  if(l) return (l.textContent||'').trim();}"
    " return (e.textContent||e.value||'').trim();}"
    "return {"
    " tag:(el.tagName||'').toLowerCase(),"
    " role:el.getAttribute('role')||null,"
    " type:el.getAttribute('type')||null,"
    " label:lab(el),"
    " placeholder:el.getAttribute('placeholder')||null,"
    " href:el.getAttribute('href')||null,"
    " disabled:!!el.disabled,"
    " checked:!!el.checked,"
    " readOnly:!!el.readOnly,"
    " sensitive:false,"
    " editable:!!(el.isContentEditable||"
    "  (el.tagName==='INPUT'||el.tagName==='TEXTAREA'))"
    "};})"
)


# ---------------------------------------------------------------------------
# RDP framing helpers (length-prefixed JSON, same wire shape as
# rdp_client.RDPClient._recv/_send).
# ---------------------------------------------------------------------------
def _frame(obj):
    data = json.dumps(obj).encode("utf-8")
    return f"{len(data)}:".encode("ascii") + data


def _parse_frames(buf):
    """Parse complete frames from buf. Returns (packets, rest)."""
    packets = []
    while True:
        colon = buf.find(b":")
        if colon == -1:
            break
        try:
            length = int(buf[:colon])
        except ValueError:
            break
        if len(buf) < colon + 1 + length:
            break
        raw = buf[colon + 1: colon + 1 + length]
        buf = buf[colon + 1 + length:]
        try:
            packets.append(json.loads(raw.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError):
            packets.append({"_unparsed": raw.decode("utf-8", "replace")})
    return packets, buf


class DroppingProxy:
    """One-connection TCP proxy between an RDPClient and the real RDP
    server. Forwards client->server bytes verbatim. Server->client
    packets are parsed frame by frame; when drop_predicate(packet)
    returns True the packet is swallowed (counted in self.dropped)
    instead of forwarded. Everything else is forwarded byte-exact.

    Used by test (a) to drop the evaluationResult of the click eval
    AFTER the click already fired in-page, simulating a lost response
    on a delivered action (delivery_uncertain)."""

    def __init__(self, server_host, server_port, drop_predicate,
                 mutate=None):
        self.server_host = server_host
        self.server_port = server_port
        self.drop_predicate = drop_predicate
        # Optional packet transform: mutate(pkt) -> replacement pkt,
        # or None to forward unchanged. Used to turn a delivered
        # act result into a noSuchActor error (actor died after the
        # click fired) for the B2 no-replay variant.
        self.mutate = mutate
        self.dropped = 0
        self.mutated = 0
        self.forwarded = 0
        self._stop = threading.Event()
        self._listener = None
        self.port = None

    def start(self):
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener.bind(("127.0.0.1", 0))
        self._listener.listen(1)
        self._listener.settimeout(0.5)
        self.port = self._listener.getsockname()[1]
        t = threading.Thread(target=self._serve, daemon=True)
        t.start()
        return self.port

    def stop(self):
        self._stop.set()
        if self._listener is not None:
            try:
                self._listener.close()
            except OSError:
                pass

    def _serve(self):
        client = None
        server = None
        try:
            while not self._stop.is_set():
                try:
                    client, _ = self._listener.accept()
                    break
                except socket.timeout:
                    continue
            if client is None:
                return
            server = socket.create_connection(
                (self.server_host, self.server_port), timeout=10)
            c2s = threading.Thread(target=self._pump_raw,
                                   args=(client, server), daemon=True)
            s2c = threading.Thread(target=self._pump_filtered,
                                   args=(server, client), daemon=True)
            c2s.start()
            s2c.start()
            c2s.join()
            s2c.join()
        except OSError:
            pass
        finally:
            for s in (client, server):
                if s is not None:
                    try:
                        s.close()
                    except OSError:
                        pass

    def _pump_raw(self, src, dst):
        try:
            while not self._stop.is_set():
                data = src.recv(65536)
                if not data:
                    break
                dst.sendall(data)
        except OSError:
            pass

    def _pump_filtered(self, src, dst):
        buf = b""
        try:
            while not self._stop.is_set():
                data = src.recv(65536)
                if not data:
                    break
                buf += data
                packets, buf = _parse_frames(buf)
                for pkt in packets:
                    if self.drop_predicate(pkt):
                        self.dropped += 1
                        continue
                    if self.mutate is not None:
                        replacement = self.mutate(pkt)
                        if replacement is not None:
                            self.mutated += 1
                            dst.sendall(_frame(replacement))
                            continue
                    self.forwarded += 1
                    dst.sendall(_frame(pkt))
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Fixture pages (served locally; test pages only).
# ---------------------------------------------------------------------------
SUBMIT_PAGE = """<!DOCTYPE html><html><head><title>p2b submit</title></head>
<body>
<button id="submit" type="button">Submit</button>
<div id="status">count 0</div>
<script>
window.__submitCount = 0;
document.getElementById('submit').addEventListener('click', function () {
  window.__submitCount += 1;
  document.getElementById('status').textContent =
    'count ' + window.__submitCount;
});
</script>
</body></html>"""

CONFIRM_PAGE = """<!DOCTYPE html><html><head><title>p2b confirm</title></head>
<body>
<div id="slot-a"><button id="btn-a" type="button">Confirm</button></div>
<div id="slot-b"><button id="btn-b" type="button">Confirm</button></div>
<script>
window.__clicks = [];
document.getElementById('btn-a').addEventListener('click', function () {
  window.__clicks.push('a');
});
document.getElementById('btn-b').addEventListener('click', function () {
  window.__clicks.push('b');
});
</script>
</body></html>"""


class _FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/submit"):
            body = SUBMIT_PAGE.encode("utf-8")
        elif self.path.startswith("/confirm"):
            body = CONFIRM_PAGE.encode("utf-8")
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # keep test output clean


def _start_fixture_server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _FixtureHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, srv.server_address[1]


def _live_session_or_skip(testcase):
    """Return (port, marker) for a dedicated session, or skip."""
    port = os.environ.get("RDP_TEST_PORT", "").strip()
    if not port:
        testcase.skipTest(
            "no dedicated RDP session (set RDP_TEST_PORT); "
            "P2b live settling test skipped")
    try:
        port = int(port)
    except ValueError:
        testcase.skipTest(f"RDP_TEST_PORT not an int: {port!r}")
    marker = os.environ.get("RDP_TEST_PROFILE_MARKER", "").strip()
    if marker:
        try:
            check_port_owner(port, marker)
        except RDPError as e:
            testcase.skipTest(f"dedicated session not available: {e}")
    else:
        # No marker: probe the socket; a closed port means no session.
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=2)
            s.close()
        except OSError as e:
            testcase.skipTest(f"no listener on RDP_TEST_PORT: {e}")
    return port, marker


def _make_live_client(port):
    return RDPClient(port, unscoped_test=True, denylist_patterns=[],
                     warn_unscoped=False, timeout=10)


# ---------------------------------------------------------------------------
# Pure-Python unit tests (always run; no browser needed).
# ---------------------------------------------------------------------------
class DigestUnitTests(unittest.TestCase):
    def test_identical_descriptors_equal_digest(self):
        d = {"tag": "button", "role": None, "type": "button",
             "label": "Confirm", "placeholder": None, "href": None,
             "disabled": False, "checked": False, "readOnly": False,
             "sensitive": False, "editable": False}
        self.assertEqual(descriptor_digest(d), descriptor_digest(dict(d)))

    def test_descriptor_change_changes_digest(self):
        d = {"tag": "button", "role": None, "type": "button",
             "label": "Confirm", "placeholder": None, "href": None,
             "disabled": False, "checked": False, "readOnly": False,
             "sensitive": False, "editable": False}
        d2 = dict(d, label="Cancel")
        self.assertNotEqual(descriptor_digest(d), descriptor_digest(d2))
        d3 = dict(d, disabled=True)
        self.assertNotEqual(descriptor_digest(d), descriptor_digest(d3))

    def test_digest_ignores_non_descriptor_fields(self):
        # Element identity (id, probe marker) is NOT a descriptor field:
        # two different nodes with the same descriptor digest equal.
        base = {"tag": "button", "role": None, "type": "button",
                "label": "Confirm", "placeholder": None, "href": None,
                "disabled": False, "checked": False, "readOnly": False,
                "sensitive": False, "editable": False}
        a = dict(base, id="btn-a", probe="node-1")
        b = dict(base, id="btn-b", probe="node-2")
        self.assertEqual(descriptor_digest(a), descriptor_digest(b))

    def test_frame_roundtrip(self):
        obj = {"from": "root", "type": "evaluationResult",
               "result": {"type": "number", "value": 1}}
        packets, rest = _parse_frames(_frame(obj) + _frame(obj))
        self.assertEqual(len(packets), 2)
        self.assertEqual(rest, b"")
        self.assertEqual(packets[0]["type"], "evaluationResult")


class DeliveryClassificationUnitTests(unittest.TestCase):
    """The retry=unsafe half of test (a) is a classification property:
    a lost response on an action eval must classify as
    delivery_uncertain / unsafe, never safe-retry."""

    def test_lost_response_on_eval_is_unsafe(self):
        self.assertEqual(
            rc._classify_error("RDP socket closed by server", "eval"),
            ("transport_error", "delivery_uncertain", "unsafe"))
        self.assertEqual(
            rc._classify_error("evaluate exception: boom", "eval"),
            ("evaluate_failed", "delivery_uncertain", "unsafe"))
        # The shipped act path classifies the same way (M8).
        self.assertEqual(
            rc._classify_error("RDP socket closed by server", "act"),
            ("transport_error", "delivery_uncertain", "unsafe"))


# ---------------------------------------------------------------------------
# Live settling tests (skip without a dedicated session).
# ---------------------------------------------------------------------------
def _is_act_result(pkt):
    """True for the evaluationResult carrying an act verdict with
    acted=true (the click already fired in-page by then)."""
    if pkt.get("type") != "evaluationResult":
        return False
    res = pkt.get("result")
    value = res.get("value") if isinstance(res, dict) else res
    return isinstance(value, str) and '"acted":true' in value


class FaultInjectionDeliveryTests(unittest.TestCase):
    """(a) Drive the SHIPPED RDPClient.act() through the dropping
    proxy (gate fix M8: not a raw evaluate). Drop the act response
    after the click fires in-page; the submit counter must stay 1
    and the failure must classify retry=unsafe. Proves: no
    automatic replay of a delivery_uncertain act, through the real
    act path. The noSuchActor variant proves B2: act executes
    exactly once even when its actor dies after firing."""

    def _setup_fixture(self, port, http_port):
        url = f"http://127.0.0.1:{http_port}/submit.html"
        setup = _make_live_client(port)
        setup.attach()
        setup.navigate(url)
        setup.wait_load("submit", timeout=20)
        self.assertEqual(setup.evaluate("window.__submitCount"), 0)
        setup.close()
        return url

    def _verify_counter(self, port, expected):
        verify = _make_live_client(port)
        verify.attach()
        count = verify.evaluate("window.__submitCount")
        verify.close()
        self.assertEqual(
            count, expected,
            f"submit counter must stay {expected} (no replay); "
            f"got {count!r}")

    def test_dropped_act_response_no_double_submit(self):
        port, _marker = _live_session_or_skip(self)
        srv, http_port = _start_fixture_server()
        proxy = None
        try:
            self._setup_fixture(port, http_port)
            proxy = DroppingProxy("127.0.0.1", port, _is_act_result)
            proxy_port = proxy.start()
            victim = RDPClient(proxy_port, unscoped_test=True,
                               denylist_patterns=[], warn_unscoped=False,
                               timeout=5)
            victim.attach()
            with self.assertRaises((RDPError, TimeoutError, OSError)) as cm:
                victim.act({"role": "button", "name": "Submit"},
                           "click", timeout=5)
            msg = str(cm.exception) or type(cm.exception).__name__
            code, delivery, retry = rc._classify_error(msg, "act")
            self.assertEqual(
                (delivery, retry), ("delivery_uncertain", "unsafe"),
                f"dropped act response must be delivery_uncertain/"
                f"unsafe, got code={code} msg={msg!r}")
            self.assertGreaterEqual(
                proxy.dropped, 1,
                "proxy must have dropped the act evaluationResult")
            try:
                victim.close()
            except Exception:
                pass
            self._verify_counter(port, 1)
        finally:
            if proxy is not None:
                proxy.stop()
            srv.shutdown()
            srv.server_close()

    def test_no_such_actor_after_act_no_replay(self):
        # B2 variant: the act result is replaced by a noSuchActor
        # error (actor died after the click fired). evaluate()'s
        # RT-06 retry must NOT replay the act script.
        port, _marker = _live_session_or_skip(self)
        srv, http_port = _start_fixture_server()
        proxy = None
        try:
            self._setup_fixture(port, http_port)

            def to_no_such_actor(pkt):
                if _is_act_result(pkt):
                    return {"from": pkt.get("from"),
                            "error": "noSuchActor"}
                return None

            proxy = DroppingProxy("127.0.0.1", port,
                                  lambda pkt: False,
                                  mutate=to_no_such_actor)
            proxy_port = proxy.start()
            victim = RDPClient(proxy_port, unscoped_test=True,
                               denylist_patterns=[], warn_unscoped=False,
                               timeout=5)
            victim.attach()
            with self.assertRaises(RDPError) as cm:
                victim.act({"role": "button", "name": "Submit"},
                           "click", timeout=5)
            self.assertIn("noSuchActor", str(cm.exception))
            self.assertEqual(proxy.mutated, 1)
            self.assertEqual(victim._retries, 0,
                             "act must not take the RT-06 retry")
            try:
                victim.close()
            except Exception:
                pass
            self._verify_counter(port, 1)
        finally:
            if proxy is not None:
                proxy.stop()
            srv.shutdown()
            srv.server_close()


class ConfirmSwapDigestTests(unittest.TestCase):
    """(b) Two identical "Confirm" buttons: digest equality across a
    swap/replacement proves descriptor stability, not element
    identity. The registry must therefore treat a digest match as
    "descriptor unchanged", never as "same element"."""

    def test_digest_stable_across_swap_identity_differs(self):
        port, _marker = _live_session_or_skip(self)
        srv, http_port = _start_fixture_server()
        try:
            url = f"http://127.0.0.1:{http_port}/confirm.html"
            c = _make_live_client(port)
            c.attach()
            c.navigate(url)
            c.wait_load("confirm", timeout=20)

            # Tag each button with a JS-side identity marker (not part
            # of the descriptor) and read both descriptors.
            c.evaluate(
                "document.getElementById('btn-a').dataset.probe='node-a';"
                "document.getElementById('btn-b').dataset.probe='node-b';"
                " 'tagged'")
            desc_a = c.evaluate(
                f"JSON.stringify({DESCRIPTOR_JS}"
                "(document.getElementById('btn-a')))")
            desc_b = c.evaluate(
                f"JSON.stringify({DESCRIPTOR_JS}"
                "(document.getElementById('btn-b')))")
            desc_a = json.loads(desc_a)
            desc_b = json.loads(desc_b)
            # Identical descriptors -> equal digests (ambiguity class).
            self.assertEqual(desc_a, desc_b)
            self.assertEqual(descriptor_digest(desc_a),
                             descriptor_digest(desc_b))

            # Swap: move btn-a into slot-b and btn-b into slot-a. The
            # first "Confirm" in document order is now node-b.
            c.evaluate(
                "(function(){"
                "var a=document.getElementById('btn-a');"
                "var b=document.getElementById('btn-b');"
                "var sa=document.getElementById('slot-a');"
                "var sb=document.getElementById('slot-b');"
                "sa.appendChild(b); sb.appendChild(a);"
                "return 'swapped';})()")
            first_probe = c.evaluate(
                "document.querySelectorAll('button')[0].dataset.probe")
            self.assertEqual(first_probe, "node-b",
                             "after swap the first Confirm is node-b")
            desc_first = c.evaluate(
                f"JSON.stringify({DESCRIPTOR_JS}"
                "(document.querySelectorAll('button')[0]))")
            desc_first = json.loads(desc_first)
            # Digest still matches the pre-swap descriptor even though
            # the element identity changed: digest != identity.
            self.assertEqual(
                descriptor_digest(desc_first), descriptor_digest(desc_a),
                "digest must stay stable across the swap (descriptor "
                "stability) while identity differs")

            # Mutation: change one label; its digest must diverge.
            c.evaluate(
                "document.querySelectorAll('button')[0].textContent="
                "'Cancel'; 'mutated'")
            desc_mut = c.evaluate(
                f"JSON.stringify({DESCRIPTOR_JS}"
                "(document.querySelectorAll('button')[0]))")
            desc_mut = json.loads(desc_mut)
            self.assertNotEqual(
                descriptor_digest(desc_mut), descriptor_digest(desc_a),
                "descriptor change (label) must change the digest")
            c.close()
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
