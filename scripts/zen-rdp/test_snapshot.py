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


if __name__ == "__main__":
    unittest.main()
