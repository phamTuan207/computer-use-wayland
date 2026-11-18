"""Repo-owned VS Code wrapper; non-live, no VS Code needed.

Run directly: python3 tests/test_vscode_cli.py
(Also picked up by `python3 -m unittest discover -s tests -p 'test_*.py'`.)

Builds a fake ~/.config/Code tree in a temp dir (workspaceStorage with
real state.vscdb sqlite DBs holding the same
`memento/workbench.parts.editor` key the wrapper parses on the laptop),
a fake `code` binary on PATH that records its argv, and fixture files.
Asserts workspaces/tabs/read/files/extensions/open/diff/status/version/
backups against the fixtures. Nothing here touches a real VS Code.
"""
import json
import os
import sqlite3
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "vscode_cli.py"

EDITOR_KEY = "memento/workbench.parts.editor"

CODE_STUB = """#!/bin/bash
echo "$@" >> "$CODE_STUB_LOG"
if [ "$1" = "--list-extensions" ]; then
  echo "ms-python.python@2026.10.0"
  echo "esbenp.prettier-vscode@12.4.0"
  exit 0
fi
if [ "$1" = "--version" ]; then
  echo "9.9.9"
  echo "fakecommit"
  echo "x64"
  exit 0
fi
if [ "$1" = "--status" ]; then
  exit 0
fi
echo "stub-ok"
exit 0
"""


def editor_state(editors, active_index=0):
    """One serialized editor grid leaf with the given file paths."""
    entries = []
    for path in editors:
        value = json.dumps({"resourceJSON": {"$mid": 1, "fsPath": path,
                                             "external": "file://" + path,
                                             "path": path, "scheme": "file"},
                            "encoding": "utf8"})
        entries.append({"id": "workbench.editors.files.fileEditorInput",
                        "value": value})
    state = {"editorpart.state": {"serializedGrid": {"root": {
        "type": "branch", "data": [{"type": "leaf", "data": {
            "id": 0, "editors": entries, "mru": [active_index],
            "preview": active_index}, "size": 548}], "size": 794},
        "orientation": 0, "width": 794, "height": 548},
        "activeGroup": 0, "mostRecentActiveGroups": [0]}}
    return json.dumps(state)


class VscodeCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.config = self.base / "config"
        storage = self.config / "User" / "workspaceStorage"
        self.ws_a = self.base / "Work" / "iac-eval"
        self.ws_b = self.base / "My Projects" / "Legacy-link"
        self.ws_a.mkdir(parents=True)
        self.ws_b.mkdir(parents=True)
        (self.ws_a / "demo.rego").write_text("package demo\n")
        (self.ws_a / "metrics.py").write_text("x = 1\n" * 100)
        (self.ws_b / "README.md").write_text("# Legacy\n")
        gitdir = self.ws_a / ".git"
        gitdir.mkdir()
        (gitdir / "config").write_text("[core]\n")
        node = self.ws_a / "node_modules" / "pkg"
        node.mkdir(parents=True)
        (node / "index.js").write_text("void 0;\n")
        self.hash_a = "aabbccdd"
        self.hash_b = "eeff0011"
        for ws_hash, folder in ((self.hash_a, self.ws_a),
                                (self.hash_b, self.ws_b)):
            entry = storage / ws_hash
            entry.mkdir(parents=True)
            uri = "file://" + str(folder).replace(" ", "%20")
            (entry / "workspace.json").write_text(
                json.dumps({"folder": uri}))
            db = entry / "state.vscdb"
            conn = sqlite3.connect(db)
            conn.execute("CREATE TABLE ItemTable (key TEXT PRIMARY KEY, "
                         "value TEXT)")
            conn.execute("INSERT INTO ItemTable VALUES (?, ?)",
                         (EDITOR_KEY, editor_state(
                             [str(self.ws_a / "demo.rego"),
                              str(self.ws_a / "metrics.py")], 1)))
            conn.commit()
            conn.close()
        # One workspace with no state.vscdb at all.
        entry = storage / "11223344"
        entry.mkdir(parents=True)
        (entry / "workspace.json").write_text(json.dumps(
            {"workspace": "file:///tmp/agent-sessions.code-workspace"}))
        # Backups fixture.
        backup = self.config / "Backups" / self.hash_a / "untitled"
        backup.mkdir(parents=True)
        (backup / "-7f9c1a2e").write_text("untitled:Untitled-1\n")
        # Fake `code` on PATH.
        bindir = self.base / "bin"
        bindir.mkdir()
        stub = bindir / "code"
        stub.write_text(CODE_STUB)
        stub.chmod(0o755)
        self.stub_log = self.base / "code-argv.log"
        self.env = dict(os.environ)
        self.env["VSCODE_CONFIG_DIR"] = str(self.config)
        self.env["CODE_STUB_LOG"] = str(self.stub_log)
        self.env["PATH"] = str(bindir) + os.pathsep + self.env.get("PATH", "")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *argv):
        """Run the wrapper; return (returncode, parsed stdout JSON)."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *argv],
            capture_output=True, text=True, env=self.env, timeout=30)
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("wrapper stdout is not JSON: %r (stderr %r)"
                      % (result.stdout, result.stderr))
        return result.returncode, parsed

    def test_workspaces_decode_folder_uris(self):
        code, out = self.run_cli("workspaces")
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        paths = {ws["path"] for ws in out["workspaces"]}
        self.assertIn(str(self.ws_a), paths)
        self.assertIn(str(self.ws_b), paths)
        kinds = {ws["path"]: ws["kind"] for ws in out["workspaces"]}
        self.assertEqual(kinds["/tmp/agent-sessions.code-workspace"],
                         "workspace")

    def test_tabs_list_open_editors_with_active(self):
        code, out = self.run_cli("tabs")
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        by_ws = {ws["workspace"]: ws for ws in out["workspaces"]}
        group = by_ws[str(self.ws_a)]["groups"][0]
        self.assertEqual(group["editors"],
                         [str(self.ws_a / "demo.rego"),
                          str(self.ws_a / "metrics.py")])
        self.assertEqual(group["active"], str(self.ws_a / "metrics.py"))
        missing = by_ws["/tmp/agent-sessions.code-workspace"]
        self.assertEqual(missing["groups"], [])
        self.assertIn("no state.vscdb", missing["note"])

    def test_tabs_workspace_filter_and_unknown(self):
        code, out = self.run_cli("tabs", "--workspace", str(self.ws_b))
        self.assertEqual(code, 0)
        self.assertEqual(len(out["workspaces"]), 1)
        self.assertEqual(out["workspaces"][0]["workspace"], str(self.ws_b))
        code, out = self.run_cli("tabs", "--workspace", "/nonexistent/ws")
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])
        self.assertIn("no known workspace", out["error"])

    def test_read_content_and_truncation(self):
        code, out = self.run_cli("read", str(self.ws_a / "demo.rego"))
        self.assertEqual(code, 0)
        self.assertEqual(out["content"], "package demo\n")
        self.assertFalse(out["truncated"])
        code, out = self.run_cli("read", str(self.ws_a / "metrics.py"),
                                 "--max-chars", "10")
        self.assertTrue(out["truncated"])
        self.assertEqual(out["content"], "x = 1\nx = ")
        code, out = self.run_cli("read", str(self.ws_a / "missing.py"))
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])

    def test_read_refuses_oversize_file(self):
        big = self.base / "big.bin"
        big.write_bytes(b"x" * (1_048_576 + 1))
        code, out = self.run_cli("read", str(big))
        self.assertEqual(code, 1)
        self.assertIn("too large", out["error"])

    def test_files_skips_junk_dirs_and_caps(self):
        code, out = self.run_cli("files", str(self.ws_a))
        self.assertEqual(code, 0)
        paths = {item["path"] for item in out["files"]}
        self.assertIn("demo.rego", paths)
        self.assertIn("metrics.py", paths)
        self.assertNotIn(".git/config", paths)
        self.assertNotIn("node_modules/pkg/index.js", paths)
        code, out = self.run_cli("files", str(self.ws_a), "--max", "1")
        self.assertTrue(out["truncated"])
        self.assertEqual(len(out["files"]), 1)
        code, out = self.run_cli("files", "/nonexistent/dir")
        self.assertEqual(code, 1)

    def test_extensions_parses_stub_versions(self):
        code, out = self.run_cli("extensions")
        self.assertEqual(code, 0)
        self.assertEqual(out["extensions"], [
            {"id": "ms-python.python", "version": "2026.10.0"},
            {"id": "esbenp.prettier-vscode", "version": "12.4.0"}])

    def test_open_existing_file_calls_code(self):
        target = self.ws_a / "demo.rego"
        code, out = self.run_cli("open", str(target), "--new-window",
                                 "--goto", "1")
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        logged = self.stub_log.read_text()
        self.assertIn("--new-window", logged)
        self.assertIn("--goto", logged)
        self.assertIn("%s:1" % target, logged)

    def test_open_refuses_missing_path(self):
        code, out = self.run_cli("open", str(self.base / "nope.txt"))
        self.assertEqual(code, 1)
        self.assertIn("does not exist", out["error"])
        self.assertFalse(self.stub_log.exists())

    def test_diff_refuses_missing_file(self):
        code, out = self.run_cli(
            "diff", str(self.ws_a / "demo.rego"), "/nonexistent/b.txt")
        self.assertEqual(code, 1)
        self.assertIn("not a regular file", out["error"])

    def test_status_and_version(self):
        code, out = self.run_cli("status")
        self.assertEqual(code, 0)
        self.assertFalse(out["running"])
        code, out = self.run_cli("version")
        self.assertEqual(code, 0)
        self.assertEqual(out["version"], "9.9.9")

    def test_backups_lists_files_only(self):
        code, out = self.run_cli("backups")
        self.assertEqual(code, 0)
        self.assertEqual(
            [item["path"] for item in out["backups"]],
            ["%s/untitled/-7f9c1a2e" % self.hash_a])
        self.assertIn("not verified readable", out["note"])


if __name__ == "__main__":
    unittest.main()
