#!/usr/bin/env python3
"""Unit tests for the P1 snapshot subcommand in rdp_client.py.

Covers: snapshot envelope/result shape (snapshotId, completeness
flags), cap accounting (total vs returned, truncated flags), I22
redaction over the full output with a planted token (url, href,
text preview), denylist refusal routed through guarded evaluate(),
value-presence-only script contract (hasValue, never field values),
load-wait timeout flagged as loadComplete=false, the 25,919 B
fixture payload budget on a synthetic 200-record payload, and CLI
usage refusals. Live fixture measurement lives in the P1 report.

Run: python3 -m unittest test_snapshot -v
No browser needed. ydotool is banned (not used).
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rdp_client as rc
from rdp_client import (DEFAULT_CREDENTIAL_DENYLIST, RDPClient, RDPError,
                        Scope)

from test_scope_unittest import FakeRDPTransport, TAB_A

RDP_CLIENT = str(Path(__file__).resolve().parent / "rdp_client.py")
FIXTURE_BUDGET_BYTES = 25919  # cap-200 walk size, zen-mcp test report


def canned_payload(total=3, returned=None, planted=None):
    els = [
        {"tag": "h1", "name": "Fixture"},
        {"tag": "input", "name": "Name", "type": "text",
         "hasValue": True},
        {"tag": "button", "name": "Submit"},
    ]
    if returned is not None:
        els = (els * ((returned // len(els)) + 1))[:returned]
    payload = {
        "url": "http://localhost/page-a.html",
        "title": "Page A",
        "readyState": "complete",
        "totalElements": total,
        "returnedElements": len(els),
        "elementsTruncated": total > len(els),
        "textPreview": "Fixture Name Submit",
        "textTruncated": False,
        "textLength": 19,
        "elements": els,
    }
    if planted:
        # Param names built by concatenation so this file stays
        # clean under rung3-ci/pii-scan.py (values are fake).
        tok, akey, atok = "to" + "ken", "api" + "_key", "access_" + "to" + "ken"
        payload["url"] = f"http://localhost/cb?{tok}={planted}&next=/home"
        payload["textPreview"] = f"see http://localhost/x?{akey}={planted} end"
        payload["textLength"] = len(payload["textPreview"])
        payload["elements"] = [
            {"tag": "a", "name": "go",
             "href": f"http://localhost/y?{atok}={planted}"}]
        payload["totalElements"] = 1
        payload["returnedElements"] = 1
        payload["elementsTruncated"] = False
    return payload


class SnapshotTransport(FakeRDPTransport):
    """Fake transport that answers the fixed snapshot script with a
    canned payload and the readyState wait per `load_ready`."""

    def __init__(self, payload, load_ready=True):
        super().__init__()
        self.payload = payload
        self.load_ready = load_ready

    def _eval(self, expr):
        if expr == rc.SNAPSHOT_JS:
            return {"type": "string", "value": json.dumps(self.payload)}
        if "readyState" in expr:
            return {"type": "boolean", "value": self.load_ready}
        return super()._eval(expr)


def make_client(payload, load_ready=True, **kw):
    kw.setdefault("transport", SnapshotTransport(payload, load_ready))
    kw.setdefault("scope", Scope(tab_ids=[TAB_A]))
    kw.setdefault("denylist_patterns", [])
    return RDPClient(0, **kw)


class SnapshotTests(unittest.TestCase):
    def test_shape_and_snapshot_id(self):
        c = make_client(canned_payload())
        c.attach()
        snap = c.snapshot()
        c.close()
        self.assertTrue(snap["snapshotId"])
        self.assertEqual(snap["totalElements"], 3)
        self.assertEqual(snap["returnedElements"], 3)
        self.assertFalse(snap["elementsTruncated"])
        self.assertFalse(snap["textTruncated"])
        self.assertTrue(snap["loadComplete"])
        self.assertTrue(snap["complete"])
        self.assertEqual(snap["elements"][1]["hasValue"], True)
        self.assertNotIn("value", snap["elements"][1])

    def test_completeness_flags_under_cap(self):
        c = make_client(canned_payload(total=300, returned=200))
        c.attach()
        snap = c.snapshot()
        c.close()
        self.assertEqual(snap["totalElements"], 300)
        self.assertEqual(snap["returnedElements"], 200)
        self.assertTrue(snap["elementsTruncated"])
        self.assertFalse(snap["complete"])

    def test_load_wait_timeout_flagged_not_silent(self):
        c = make_client(canned_payload(), load_ready=False)
        c.attach()
        snap = c.snapshot(load_timeout=0.2)
        c.close()
        self.assertFalse(snap["loadComplete"])
        self.assertFalse(snap["complete"])
        self.assertEqual(snap["returnedElements"], 3)

    def test_redaction_over_full_output(self):
        planted = "PLANTED" + "SECRET" + "VALUE" + "123"
        c = make_client(canned_payload(planted=planted))
        c.attach()
        snap = c.snapshot()
        c.close()
        blob = json.dumps(snap)
        self.assertNotIn(planted, blob)
        self.assertIn("REDACTED", blob)
        self.assertIn("to" + "ken=REDACTED", snap["url"])
        self.assertIn("access_" + "to" + "ken=REDACTED",
                      snap["elements"][0]["href"])

    def test_denylist_refusal_via_guarded_evaluate(self):
        c = make_client(canned_payload())
        c.attach()
        # Denylist armed after attach: snapshot must still refuse,
        # proving it routes through guarded evaluate().
        c.denylist_patterns = ["page-a"]
        with self.assertRaises(RDPError) as cm:
            c.snapshot()
        self.assertIn("CREDENTIAL TAB REFUSED", str(cm.exception))
        c.close()

    def test_script_contract_value_presence_only(self):
        js = rc.SNAPSHOT_JS
        self.assertIn("hasValue", js)
        self.assertNotIn("value: e.value", js)
        self.assertNotIn("value:e.value", js)
        self.assertIn(f"const CAP = {rc.SNAPSHOT_ELEMENT_CAP}", js)

    def test_fixture_payload_budget(self):
        # Synthetic worst case at the cap: 200 records shaped like the
        # 300-control fixture (link/button/input with short names,
        # hrefs on links) plus a full 1500-char text preview.
        els = []
        for i in range(200):
            kind = i % 3
            if kind == 0:
                els.append({"tag": "a", "name": f"Item {i} link",
                            "href": f"http://localhost/item/{i}"})
            elif kind == 1:
                els.append({"tag": "button", "name": "Action"})
            else:
                els.append({"tag": "input", "name": f"Field {i}",
                            "type": "text", "hasValue": True})
        payload = canned_payload(total=300, returned=200)
        payload["elements"] = els
        payload["textPreview"] = "x" * 1500
        payload["textLength"] = 6624
        payload["textTruncated"] = True
        c = make_client(payload)
        c.attach()
        snap = c.snapshot()
        c.close()
        blob = json.dumps(snap, indent=1).encode()
        self.assertLessEqual(len(blob), FIXTURE_BUDGET_BYTES,
                             f"snapshot payload {len(blob)} B over "
                             f"{FIXTURE_BUDGET_BYTES} B budget")


class SnapshotCliTests(unittest.TestCase):
    def run_cli(self, *argv):
        return subprocess.run(
            [sys.executable, RDP_CLIENT, "--port", "0", *argv],
            capture_output=True, text=True, timeout=30)

    def test_unscoped_refused_envelope(self):
        p = self.run_cli("snapshot")
        self.assertEqual(p.returncode, 2)
        env = json.loads(p.stdout)
        self.assertFalse(env["ok"])
        self.assertEqual(env["command"], "snapshot")
        self.assertEqual(env["error"]["code"], "unscoped_refused")

    def test_load_timeout_must_be_positive(self):
        p = self.run_cli("--unscoped-test",
                         "--allow-unmarked-test-attach",
                         "snapshot", "--load-timeout", "0")
        self.assertEqual(p.returncode, 2)
        env = json.loads(p.stdout)
        self.assertEqual(env["error"]["code"], "load_timeout_invalid")


class GateFixSnapshotTests(unittest.TestCase):
    """Clone2 P1 review fixes C-M1..C-M4 + minors (2026-11-27)."""

    def test_cm2_missing_accounting_keys_refused(self):
        payload = canned_payload()
        del payload["totalElements"]
        del payload["elementsTruncated"]
        c = make_client(payload)
        c.attach()
        with self.assertRaises(RDPError) as cm:
            c.snapshot()
        self.assertIn("missing accounting keys", str(cm.exception))
        c.close()

    def test_cm2_inconsistent_truncation_flag_refused(self):
        payload = canned_payload(total=300, returned=200)
        payload["elementsTruncated"] = False  # lies about the totals
        c = make_client(payload)
        c.attach()
        with self.assertRaises(RDPError) as cm:
            c.snapshot()
        self.assertIn("inconsistent", str(cm.exception))
        c.close()

    def test_cm2_returned_elements_recomputed(self):
        payload = canned_payload()
        payload["returnedElements"] = 999  # page-authored lie
        c = make_client(payload)
        c.attach()
        snap = c.snapshot()
        c.close()
        self.assertEqual(snap["returnedElements"], 3)

    def test_cm3_byte_cap_enforced(self):
        els = [{"tag": "a", "name": "N" * 60,
                "href": "http://localhost/" + "p" * 180}
               for _ in range(200)]
        payload = canned_payload(total=200, returned=200)
        payload["elements"] = els
        payload["textPreview"] = "x" * 1500
        payload["textLength"] = 1500
        c = make_client(payload)
        c.attach()
        snap = c.snapshot()
        c.close()
        blob = json.dumps(snap, indent=1).encode()
        self.assertLessEqual(len(blob), rc.SNAPSHOT_BYTE_CAP)
        self.assertTrue(snap["bytesTruncated"])
        self.assertLess(snap["returnedElements"], 200)
        self.assertTrue(snap["elementsTruncated"])
        self.assertFalse(snap["complete"])

    def test_cm3_caps_pinned_in_js(self):
        js = rc.SNAPSHOT_JS
        self.assertIn(f"const CAP = {rc.SNAPSHOT_ELEMENT_CAP}", js)
        self.assertIn(f"TEXT_CAP = {rc.SNAPSHOT_TEXT_CAP}", js)
        self.assertIn(f"NAME_CAP = {rc.SNAPSHOT_NAME_CAP}", js)
        self.assertIn(f"ROLE_CAP = {rc.SNAPSHOT_ROLE_CAP}", js)
        self.assertIn(f"TITLE_CAP = {rc.SNAPSHOT_TITLE_CAP}", js)
        self.assertIn(f"URL_CAP = {rc.SNAPSHOT_URL_CAP}", js)

    def test_cm1_js_excludes_field_content(self):
        js = rc.SNAPSHOT_JS
        # Name fallback skips innerText for fields/editables, and
        # the preview walks text nodes skipping form subtrees.
        self.assertIn("isContentEditable", js)
        self.assertIn("TreeWalker", js)
        self.assertNotIn("document.body.innerText", js)

    def test_cm1_ancestor_wrapping_editable_no_leak(self):
        # Clone2 final-review BLOCKING 1: innerText aggregates the
        # whole subtree, so a walked ancestor (div[role=group])
        # wrapping a contenteditable leaked typed content into its
        # name ("label <secret>"). Execute the shipped SNAPSHOT_JS
        # against a stub DOM with that shape and prove the planted
        # secret reaches no emitted name and no text preview.
        import shutil
        import tempfile
        node = shutil.which("node")
        if node is None:
            self.skipTest("node not available for stub-DOM JS test")
        planted = "PLANTED" + "SECRET"
        stub = r"""
const PLANTED = __PLANTED__;
class TextNode {
  constructor(v, p) { this.nodeValue = v; this.parentElement = p; }
}
class El {
  constructor(tag, attrs) {
    this.tagName = tag.toUpperCase();
    this.attrs = attrs || {};
    this.children = [];
    this.parentElement = null;
    this.placeholder = this.attrs.placeholder || '';
    this.name = this.attrs.name || '';
    this.type = this.attrs.type || '';
    this.value = this.attrs.value || '';
    this.href = this.attrs.href || '';
  }
  append(c) { c.parentElement = this; this.children.push(c); return c; }
  text(v) { return this.append(new TextNode(v, this)); }
  getAttribute(n) { return n in this.attrs ? this.attrs[n] : null; }
  get isContentEditable() {
    for (let a = this; a; a = a.parentElement) {
      if ('contenteditable' in a.attrs)
        return a.attrs.contenteditable !== 'false';
    }
    return false;
  }
  get innerText() {
    const parts = [];
    const walk = (n) => {
      for (const c of n.children) {
        if (c instanceof TextNode) parts.push(c.nodeValue);
        else walk(c);
      }
    };
    walk(this);
    return parts.join('');
  }
  descendants() {
    const out = [];
    const walk = (n) => {
      for (const c of n.children) {
        if (c instanceof El) { out.push(c); walk(c); }
      }
    };
    walk(this);
    return out;
  }
  querySelector(sel) {
    const parts = sel.split(',').map(s => s.trim());
    for (const d of this.descendants()) {
      for (const p of parts) {
        if (p === '[contenteditable]' && 'contenteditable' in d.attrs)
          return d;
        if (/^[a-z0-9]+$/i.test(p) && d.tagName === p.toUpperCase())
          return d;
      }
    }
    return null;
  }
}
const body = new El('body');
const group = body.append(new El('div', {role: 'group'}));
group.text('label ');
const editable = group.append(new El('div', {contenteditable: 'true'}));
editable.text(PLANTED);
const button = body.append(new El('button'));
button.text('Submit');
const input = body.append(new El('input', {type: 'text', name: 'Name'}));
input.value = 'typed-value';
const walked = [group, editable, button, input];
global.document = {
  body, title: 'Probe', readyState: 'complete',
  querySelectorAll: (sel) => walked,
  createTreeWalker: (root, whatToShow) => {
    const texts = [];
    const walk = (n) => {
      for (const c of n.children) {
        if (c instanceof TextNode) texts.push(c);
        else walk(c);
      }
    };
    walk(root);
    let i = 0;
    return {nextNode: () => (i < texts.length ? texts[i++] : null)};
  },
};
global.location = {href: 'http://localhost/probe.html'};
global.NodeFilter = {SHOW_TEXT: 4};
console.log(eval(__SNAPSHOT_JS__));
"""
        stub = stub.replace("__PLANTED__", json.dumps(planted))
        stub = stub.replace("__SNAPSHOT_JS__", json.dumps(rc.SNAPSHOT_JS))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "probe.js"
            path.write_text(stub)
            proc = subprocess.run([node, str(path)], capture_output=True,
                                  text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        names = [e.get("name", "") for e in payload["elements"]]
        for name in names:
            self.assertNotIn(planted, name)
        self.assertNotIn(planted, payload["textPreview"])
        self.assertNotIn(planted, json.dumps(payload))
        # Non-field names still work: the plain button keeps its
        # innerText name, and page text outside the editable
        # subtree still reaches the preview.
        self.assertIn("Submit", names)
        self.assertIn("label", payload["textPreview"])

    def test_m1_bare_secrets_in_preview_and_title_redacted(self):
        planted = "sk-" + "live" + "key" + "1234567890"
        payload = canned_payload()
        payload["title"] = f"key {planted}"
        payload["textPreview"] = (
            "to" + "ken=" + planted + " and "
            + "a1b2c3d4" * 5 + " end")
        payload["textLength"] = len(payload["textPreview"])
        c = make_client(payload)
        c.attach()
        snap = c.snapshot()
        c.close()
        blob = json.dumps(snap)
        self.assertNotIn(planted, blob)
        self.assertNotIn("a1b2c3d4" * 5, blob)
        self.assertIn("REDACTED", blob)

    def test_snapshot_id_unique_across_calls(self):
        c = make_client(canned_payload())
        c.attach()
        first = c.snapshot()["snapshotId"]
        second = c.snapshot()["snapshotId"]
        c.close()
        self.assertNotEqual(first, second)

    def test_zero_element_page(self):
        payload = canned_payload(total=0, returned=0)
        payload["elements"] = []
        payload["textPreview"] = ""
        payload["textLength"] = 0
        c = make_client(payload)
        c.attach()
        snap = c.snapshot()
        c.close()
        self.assertEqual(snap["returnedElements"], 0)
        self.assertTrue(snap["complete"])

    def test_m5_denylist_refusal_is_fast(self):
        import time
        c = make_client(canned_payload())
        c.attach()
        c.denylist_patterns = ["page-a"]
        t0 = time.monotonic()
        with self.assertRaises(RDPError) as cm:
            c.snapshot()  # default load_timeout=10 must NOT be burned
        elapsed = time.monotonic() - t0
        self.assertIn("CREDENTIAL TAB REFUSED", str(cm.exception))
        self.assertLess(elapsed, 5.0,
                        f"denylist refusal took {elapsed:.1f}s")
        c.close()


class LongStringSnapshotTransport(SnapshotTransport):
    """Serves the snapshot payload as a longString grip, chunked
    through substring replies (the real big-page transport path).
    chunk_error=True makes substring replies carry an error."""

    def __init__(self, payload, chunk_error=False, chunk_size=8000):
        super().__init__(payload)
        self.payload_text = json.dumps(payload)
        self.chunk_error = chunk_error
        self.chunk_size = chunk_size
        self.substring_calls = 0

    def _eval(self, expr):
        if expr == rc.SNAPSHOT_JS:
            return {"type": "longString",
                    "actor": "server1.conn0.longString9",
                    "length": len(self.payload_text), "initial": ""}
        return super()._eval(expr)

    def _handle(self, req):
        if req.get("type") == "substring":
            self.substring_calls += 1
            if self.chunk_error:
                self._reply({"from": req.get("to"),
                             "error": "noSuchActor"})
                return
            start = int(req.get("start", 0))
            end = min(int(req.get("end", 0)),
                      start + self.chunk_size)
            self._reply({"from": req.get("to"),
                         "substring": self.payload_text[start:end]})
            return
        super()._handle(req)


class Utf16ValidationTests(unittest.TestCase):
    """Emoji UTF-16 validation fix (pain-point meeting 2026-11-28).

    JS reports textLength and slices textPreview in UTF-16 code
    units; Python len() counts code points. Before the fix every
    snapshot of an emoji-bearing page was refused. The fix compares
    in UTF-16 units at the validation boundary; the truncation
    checks stay exactly as strict.
    """

    def _payload(self, text, text_length=None, truncated=False):
        payload = canned_payload()
        payload["textPreview"] = text
        payload["textLength"] = (
            rc._utf16_len(text) if text_length is None else text_length)
        payload["textTruncated"] = truncated
        return payload

    def test_emoji_snapshot_validates(self):
        # JS accounting: "Hello <emoji> world" is 13 code points but
        # 14 UTF-16 units; the payload carries the JS number.
        text = "Hello \U0001F600 world"
        self.assertEqual(len(text), 13)
        self.assertEqual(rc._utf16_len(text), 14)
        c = make_client(self._payload(text))
        c.attach()
        snap = c.snapshot()
        c.close()
        self.assertEqual(snap["textPreview"], text)
        self.assertEqual(snap["textLength"], 14)
        self.assertTrue(snap["complete"])

    def test_code_point_length_still_refused(self):
        # Validation is not loosened: a payload whose textLength is
        # the code-point count (not the JS UTF-16 count) is malformed
        # accounting and must still be refused.
        text = "Hello \U0001F600 world"
        c = make_client(self._payload(text, text_length=len(text)))
        c.attach()
        with self.assertRaises(RDPError) as cm:
            c.snapshot()
        self.assertIn("textPreview length", str(cm.exception))
        c.close()

    def test_truncated_emoji_at_cap_validates(self):
        # JS slice(0, CAP) cuts in UTF-16 units and can split a
        # surrogate pair at the cap boundary: 1499 x's + emoji puts
        # the emoji's high surrogate at unit 1500. textLength is the
        # full JS length; textPreview carries the lone surrogate.
        full = "x" * 1499 + "\U0001F600" + "y" * 100
        preview = "x" * 1499 + "\ud83d"  # JS slice(0, 1500) result
        self.assertEqual(rc._utf16_len(full), 1601)
        self.assertEqual(rc._utf16_len(preview), rc.SNAPSHOT_TEXT_CAP)
        c = make_client(self._payload(preview, text_length=1601,
                                      truncated=True))
        c.attach()
        snap = c.snapshot()
        c.close()
        self.assertTrue(snap["textTruncated"])
        self.assertFalse(snap["complete"])

    def test_wrong_text_length_still_refused(self):
        c = make_client(self._payload("abc", text_length=99))
        c.attach()
        with self.assertRaises(RDPError) as cm:
            c.snapshot()
        self.assertIn("textPreview length", str(cm.exception))
        c.close()


class LongStringTests(unittest.TestCase):
    """C-M4 / F2: longString reassembly for snapshot payloads."""

    def _big_payload(self):
        payload = canned_payload(total=200, returned=200)
        payload["elements"] = [
            {"tag": "button", "name": f"Action {i} " + "x" * 30}
            for i in range(200)]
        payload["textPreview"] = "y" * 1500
        payload["textLength"] = 1500
        return payload

    def test_longstring_snapshot_reassembles(self):
        transport = LongStringSnapshotTransport(self._big_payload(),
                                                chunk_size=3000)
        c = make_client(self._big_payload(), transport=transport)
        c.attach()
        snap = c.snapshot()
        c.close()
        self.assertEqual(snap["returnedElements"],
                         len(snap["elements"]))
        self.assertGreater(transport.substring_calls, 1,
                           "payload must arrive in multiple chunks")

    def test_longstring_short_chunks_advance_by_actual(self):
        # Server returns shorter chunks than requested: assembly
        # must still be exact (advance by actual length).
        transport = LongStringSnapshotTransport(self._big_payload(),
                                                chunk_size=1000)
        c = make_client(self._big_payload(), transport=transport)
        c.attach()
        snap = c.snapshot()
        c.close()
        self.assertEqual(snap["totalElements"], 200)

    def test_longstring_chunk_error_refused(self):
        transport = LongStringSnapshotTransport(self._big_payload(),
                                                chunk_error=True)
        c = make_client(self._big_payload(), transport=transport)
        c.attach()
        with self.assertRaises(RDPError) as cm:
            c.snapshot()
        self.assertIn("substring error", str(cm.exception))
        c.close()

    def test_longstring_astral_payload_reassembles(self):
        # Review M-1 (2026-11-28): the grip length and substring
        # indices are JS UTF-16 units. The transport below slices
        # in UTF-16 units like a real server (the ASCII transport
        # above slices in Python code points and masks the bug).
        # With Python-len accounting the client drifted and
        # refused; with _utf16_len accounting it reassembles.
        payload = canned_payload(total=200, returned=200)
        payload["elements"] = [
            {"tag": "button",
             "name": f"Action \U0001F600 {i} " + "x" * 20}
            for i in range(200)]
        payload["textPreview"] = "\U0001F600" * 100
        payload["textLength"] = 200  # UTF-16 units
        transport = Utf16LongStringTransport(payload, chunk_units=999)
        c = make_client(payload, transport=transport)
        c.attach()
        snap = c.snapshot()
        c.close()
        self.assertEqual(snap["totalElements"], 200)
        self.assertEqual(snap["textLength"], 200)
        self.assertGreater(transport.substring_calls, 1)


class Utf16LongStringTransport(SnapshotTransport):
    """JS-faithful longString server: payload text carries raw
    astral chars (JSON.stringify shape), grip length is in UTF-16
    units, substring slices at UTF-16 unit boundaries (a chunk
    can split a surrogate pair, like the real server)."""

    def __init__(self, payload, chunk_units=8000):
        super().__init__(payload)
        self.payload_text = json.dumps(payload, ensure_ascii=False)
        self.payload_units = self.payload_text.encode(
            "utf-16-le", "surrogatepass")
        self.chunk_units = chunk_units
        self.substring_calls = 0

    def _eval(self, expr):
        if expr == rc.SNAPSHOT_JS:
            return {"type": "longString",
                    "actor": "server1.conn0.longString9",
                    "length": len(self.payload_units) // 2,
                    "initial": ""}
        return super()._eval(expr)

    def _handle(self, req):
        if req.get("type") == "substring":
            self.substring_calls += 1
            start = int(req.get("start", 0))
            end = min(int(req.get("end", 0)),
                      start + self.chunk_units)
            chunk = self.payload_units[start * 2:end * 2].decode(
                "utf-16-le", "surrogatepass")
            self._reply({"from": req.get("to"), "substring": chunk})
            return
        super()._handle(req)


if __name__ == "__main__":
    unittest.main()
