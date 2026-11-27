#!/usr/bin/env python3
"""P2a M5 evidence: execute the SHIPPED act counting JS under Node
against a 100-button fixture (pain-point meeting 2026-11-28
BUILD NOW item 3; Clone2 review M5).

The unit tests in test_act.py stub evaluate() with canned
verdicts, so they never prove the in-page count itself. This
test runs the real _ACT_JS (via rc._act_script) in a Node DOM
stub, the same pattern as the BLOCKING-1 snapshot test in
test_snapshot.py, and asserts:
- true count 100 on 100 identical buttons (never a capped
  count like zen-mcp's "6 on 100"),
- ambiguous refusal, zero clicks,
- at/above the SCAN_CAP boundary the verdict is scan_truncated
  with candidatesTruncated=true (honest lower bound),
- sensitivity: with SCAN_CAP artificially cut to 6 the verdict
  is no longer count==100, so this test would fail if the count
  were ever capped.

No runtime behaviour change; evidence only. The same fixture
shape ships as fixtures/act-100-buttons.html for live
dedicated-session runs.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rdp_client as rc

# Minimal DOM stub: just the surface _ACT_JS touches. Every
# button is visible, enabled, role button, text "Action".
# click() bumps a global counter the assertions read back.
STUB = r"""
let CLICKS = 0;
class El {
  constructor(tag, attrs = {}) {
    this.tagName = tag.toUpperCase();
    this.attrs = attrs;
    this.children = [];
    this._text = '';
    this.disabled = false;
    this.readOnly = false;
    this.isContentEditable = false;
    this.labels = [];
    this.value = '';
    this.type = attrs.type || '';
  }
  getAttribute(name) { return name in this.attrs ? this.attrs[name] : null; }
  hasAttribute(name) { return name in this.attrs; }
  get textContent() {
    return this._text + this.children.map(c => c.textContent).join('');
  }
  set textContent(v) { this._text = v; }
  getClientRects() { return [{}]; }
  click() { CLICKS += 1; }
  dispatchEvent() { return true; }
}
function makeButtons(n) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const b = new El('button');
    b.textContent = 'Action';
    out.push(b);
  }
  return out;
}
const BUTTONS = makeButtons(__N_BUTTONS__);
global.document = {
  querySelectorAll: (sel) => BUTTONS,
  querySelector: (sel) => null,
  getElementById: (id) => null,
};
global.getComputedStyle = (el) => ({
  display: 'block', visibility: 'visible', opacity: '1'});
global.CSS = {escape: (s) => s};
global.Event = class { constructor(type, opts) { this.type = type; } };
global.HTMLInputElement = class {};
global.HTMLTextAreaElement = class {};
const verdict = eval(__ACT_JS__);
console.log(JSON.stringify({verdict: JSON.parse(verdict),
                            clicks: CLICKS}));
"""


def run_act_js(descriptor, action="click", n_buttons=100,
               script=None):
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not available")
    if script is None:
        script = rc._act_script(descriptor, action)
    stub = STUB.replace("__N_BUTTONS__", str(n_buttons))
    stub = stub.replace("__ACT_JS__", json.dumps(script))
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "act_count.js"
        path.write_text(stub)
        proc = subprocess.run([node, str(path)], capture_output=True,
                              text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


class ActCountJsTests(unittest.TestCase):
    def test_true_count_100_ambiguous_zero_clicks(self):
        out = run_act_js({"text": "Action"}, n_buttons=100)
        v = out["verdict"]
        self.assertFalse(v["acted"])
        self.assertEqual(v["reason"], "ambiguous")
        self.assertEqual(v["count"], 100)
        self.assertFalse(v["candidatesTruncated"])
        self.assertEqual(v["poolScope"], "top-document")
        self.assertEqual(out["clicks"], 0)

    def test_unique_button_acts_once(self):
        out = run_act_js({"text": "Action"}, n_buttons=1)
        v = out["verdict"]
        self.assertTrue(v["acted"])
        self.assertEqual(v["count"], 1)
        self.assertEqual(out["clicks"], 1)

    def test_zero_buttons_not_found(self):
        out = run_act_js({"text": "Action"}, n_buttons=0)
        v = out["verdict"]
        self.assertFalse(v["acted"])
        self.assertEqual(v["reason"], "not_found")
        self.assertEqual(v["count"], 0)
        self.assertEqual(out["clicks"], 0)

    def test_above_scan_cap_is_honest_truncation(self):
        # SCAN_CAP is 10000 in the shipped script: a pool of 10001
        # must refuse as scan_truncated with candidatesTruncated,
        # never act, and never report a capped count as true.
        out = run_act_js({"text": "Action"}, n_buttons=10001)
        v = out["verdict"]
        self.assertFalse(v["acted"])
        self.assertEqual(v["reason"], "scan_truncated")
        self.assertTrue(v["candidatesTruncated"])
        self.assertEqual(out["clicks"], 0)

    def test_capped_count_would_fail_this_test(self):
        # Sensitivity: cut SCAN_CAP to 6 (zen-mcp's silent cap
        # shape). The verdict must stop being count==100, which is
        # exactly what test_true_count_100 asserts, so a future
        # capped count fails the suite instead of passing quietly.
        capped = rc._act_script({"text": "Action"}, "click").replace(
            "const SCAN_CAP = 10000;", "const SCAN_CAP = 6;")
        self.assertNotEqual(capped,
                            rc._act_script({"text": "Action"}, "click"))
        out = run_act_js({"text": "Action"}, n_buttons=100,
                         script=capped)
        v = out["verdict"]
        self.assertFalse(
            v["count"] == 100 and not v["candidatesTruncated"],
            "capped count still looks exhaustive; M5 test is blind")
        self.assertEqual(out["clicks"], 0)


if __name__ == "__main__":
    unittest.main()
