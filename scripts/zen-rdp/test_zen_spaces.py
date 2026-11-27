#!/usr/bin/env python3
"""Unit tests for zen_spaces.py P4 wrappers (no browser needed).

Covers: typed list/create happy paths over a stub parent_evaluate,
create_space fire+poll (settle, JS-error state, timeout), argument
validation before any evaluate, parent-gate refusal and audit-entry
shape against a real RDPClient on the fake transport, the pinned
method set, and removal-absence by construction (no wrapper, no JS
string, no move/switch surface).

Run: python3 -m unittest test_zen_spaces -v
ydotool is banned (not used).
"""
import json
import unittest
from pathlib import Path

import zen_spaces
from rdp_client import RDPClient, RDPError
from test_scope_unittest import FakeRDPTransport


class StubClient:
    """parent_evaluate stub: records expressions, replays responses."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.exprs = []

    def parent_evaluate(self, expr, timeout=20):
        self.exprs.append(expr)
        if not self.responses:
            raise AssertionError(f"unexpected parent_evaluate: {expr!r}")
        return self.responses.pop(0)


class SpacesFakeTransport(FakeRDPTransport):
    """Fake RDP server whose parent evaluates return canned JSON."""

    @staticmethod
    def _eval(expr):
        if "typeof" in expr:
            return {"type": "string", "value": json.dumps(
                {m: "function" for m in zen_spaces.PINNED_METHODS})}
        if "getWorkspaces" in expr:
            return {"type": "string", "value": json.dumps({
                "activeWorkspace": "{aaa}",
                "spaces": [{"uuid": "{aaa}", "name": "Space",
                            "containerTabId": 0}]})}
        if "isZenFolder" in expr:
            return {"type": "string", "value": json.dumps(
                {"folders": []})}
        return {"type": "string", "value": "ok"}


class TestListCreate(unittest.TestCase):
    def test_list_spaces(self):
        stub = StubClient([json.dumps({
            "activeWorkspace": "{aaa}",
            "spaces": [{"uuid": "{aaa}", "name": "Space",
                        "containerTabId": 0}]})])
        out = zen_spaces.list_spaces(stub)
        self.assertEqual(out["activeWorkspace"], "{aaa}")
        self.assertEqual(out["spaces"][0]["name"], "Space")
        self.assertEqual(stub.exprs, [zen_spaces._JS_LIST_SPACES])

    def test_list_folders(self):
        stub = StubClient([json.dumps({"folders": [
            {"id": "1-1", "label": "F", "collapsed": False,
             "workspace": "{aaa}", "tabCount": 2}]})])
        out = zen_spaces.list_folders(stub)
        self.assertEqual(out["folders"][0]["tabCount"], 2)
        self.assertEqual(stub.exprs, [zen_spaces._JS_LIST_FOLDERS])

    def test_create_folder(self):
        stub = StubClient([json.dumps({"id": "9-1", "label": "Docs"})])
        out = zen_spaces.create_folder(stub, "Docs", ["example.com"])
        self.assertEqual(out, {"id": "9-1", "label": "Docs"})
        self.assertIn("gZenFolders.createFolder", stub.exprs[0])
        self.assertIn(json.dumps("Docs"), stub.exprs[0])
        self.assertIn(json.dumps(["example.com"]), stub.exprs[0])

    def test_create_space_fire_and_poll(self):
        stub = StubClient([
            "token",  # fire returns the token string
            json.dumps({"done": False}),
            json.dumps({"done": True, "ok": True, "uuid": "{bbb}",
                        "name": "Work"}),
            True,  # slot cleanup
        ])
        out = zen_spaces.create_space(stub, "Work")
        self.assertEqual(out, {"uuid": "{bbb}", "name": "Work"})
        self.assertIn("createAndSaveWorkspace", stub.exprs[0])
        self.assertIn(json.dumps("Work"), stub.exprs[0])
        self.assertIn("undefined, true", stub.exprs[0],
                      "create must not switch the visible space")
        self.assertEqual(len(stub.exprs), 4)

    def test_create_space_js_error_state(self):
        stub = StubClient([
            "token",
            json.dumps({"done": True, "ok": False,
                        "error": "Error: boom"}),
            True,
        ])
        with self.assertRaises(RDPError) as cm:
            zen_spaces.create_space(stub, "Work")
        self.assertIn("boom", str(cm.exception))

    def test_create_space_timeout(self):
        stub = StubClient(["token"] + [json.dumps({"done": False})] * 50)
        with self.assertRaises(RDPError) as cm:
            zen_spaces.create_space(stub, "Work", timeout=0.2)
        self.assertIn("did not settle", str(cm.exception))

    def test_non_json_result_refused(self):
        stub = StubClient([{"type": "object", "class": "Promise"}])
        with self.assertRaises(RDPError):
            zen_spaces.list_spaces(stub)


class TestValidation(unittest.TestCase):
    def test_validation_before_any_evaluate(self):
        stub = StubClient([])
        for call in (
                lambda: zen_spaces.create_space(stub, ""),
                lambda: zen_spaces.create_space(stub, "  "),
                lambda: zen_spaces.create_space(stub, 123),
                lambda: zen_spaces.create_space(stub, "X", timeout=0),
                lambda: zen_spaces.create_folder(stub, "", ["a"]),
                lambda: zen_spaces.create_folder(stub, "L", []),
                lambda: zen_spaces.create_folder(stub, "L", [""]),
                lambda: zen_spaces.create_folder(stub, "L", "notalist"),
        ):
            with self.assertRaises(ValueError):
                call()
        self.assertEqual(stub.exprs, [],
                         "validation must fire before any evaluate")


class TestGateAndAudit(unittest.TestCase):
    def test_gate_refusal_without_allow_parent(self):
        c = RDPClient(0, transport=SpacesFakeTransport(),
                      unscoped_test=True, allow_parent=False,
                      denylist_patterns=[], warn_unscoped=False)
        with self.assertRaises(RDPError) as cm:
            zen_spaces.list_spaces(c)
        self.assertIn("PARENT EVALUATE REFUSED", str(cm.exception))
        self.assertEqual(c._parent_evals, [])
        self.assertEqual(c._actions["parent_evaluate"], 0)
        c.close()

    def test_audit_entry_shape(self):
        c = RDPClient(0, transport=SpacesFakeTransport(),
                      unscoped_test=True, allow_parent=True,
                      denylist_patterns=[], warn_unscoped=False)
        out = zen_spaces.list_spaces(c)
        self.assertEqual(out["spaces"][0]["uuid"], "{aaa}")
        self.assertEqual(c._actions["parent_evaluate"], 1)
        self.assertEqual(len(c._parent_evals), 1)
        entry = c._parent_evals[0]
        self.assertEqual(set(entry), {"expr_prefix", "at"})
        self.assertTrue(entry["expr_prefix"].startswith(
            "JSON.stringify({activeWorkspace"))
        report = c.drive_report()
        self.assertEqual(report["parent_evaluates"], c._parent_evals)
        self.assertEqual(report["actions"]["parent_evaluate"], 1)
        c.close()


class TestPinnedMethods(unittest.TestCase):
    def test_pinned_set_exact(self):
        self.assertEqual(zen_spaces.PINNED_METHODS, (
            "gZenWorkspaces.getWorkspaces",
            "gZenWorkspaces.createAndSaveWorkspace",
            "gZenFolders.createFolder",
        ))

    def test_assert_pinned_ok(self):
        stub = StubClient([json.dumps(
            {m: "function" for m in zen_spaces.PINNED_METHODS})])
        types = zen_spaces.assert_pinned_methods(stub)
        self.assertEqual(set(types), set(zen_spaces.PINNED_METHODS))

    def test_assert_pinned_missing_refused(self):
        stub = StubClient([json.dumps({
            "gZenWorkspaces.getWorkspaces": "function",
            "gZenWorkspaces.createAndSaveWorkspace": "undefined",
            "gZenFolders.createFolder": "function"})])
        with self.assertRaises(RDPError):
            zen_spaces.assert_pinned_methods(stub)

    def test_assert_pinned_live_shape_via_fake_transport(self):
        c = RDPClient(0, transport=SpacesFakeTransport(),
                      unscoped_test=True, allow_parent=True,
                      denylist_patterns=[], warn_unscoped=False)
        types = zen_spaces.assert_pinned_methods(c)
        self.assertTrue(all(v == "function" for v in types.values()))
        c.close()


class TestRemovalAbsent(unittest.TestCase):
    """Removal is rejected by charter: absent by construction."""

    def test_no_removal_or_move_surface(self):
        source = Path(zen_spaces.__file__).read_text()
        for token in ("deleteWorkspace", "removeWorkspace",
                      "deleteFolder", "removeFolder", "contextDelete",
                      "ungroupTab", "changeWorkspaceWithID",
                      "moveTabToWorkspace", "changeFolderToSpace",
                      "delete ", "delete("):
            self.assertNotIn(token, source,
                             f"forbidden token in zen_spaces.py: {token}")
        for name in dir(zen_spaces):
            self.assertNotIn("delete", name.lower())
            self.assertNotIn("remove", name.lower())
            self.assertNotIn("move", name.lower())
            self.assertNotIn("switch", name.lower())

    def test_js_strings_carry_no_removal(self):
        for value in vars(zen_spaces).values():
            if isinstance(value, str) and value.startswith("JSON"):
                self.assertNotIn("delete", value)
                self.assertNotIn("remove", value)


if __name__ == "__main__":
    unittest.main()
