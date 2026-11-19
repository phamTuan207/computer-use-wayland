"""Repo-owned `vault move` for Obsidian; non-live, no Obsidian needed.

Run directly: python3 tests/test_obsidian_vault_move.py
(Also picked up by `python3 -m unittest discover -s tests -p 'test_*.py'`.)

Spins up a fake Local REST API on 127.0.0.1 (plain HTTP on an ephemeral
port, pointed at with OBSIDIAN_API_URL) that records the MOVE request
and answers 204, like the real plugin. Asserts the runner issues
exactly the proven call (method MOVE, per-segment URL encoding,
Destination header, Bearer auth) and that usage, auth, and API errors
fail with the right exit code and envelope. A fake harness binary on
PATH proves non-move obsidian commands still go through the binary.
"""

import json
import os
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "cli-anything.py"
REGISTRY = ROOT / "skill" / "cli-anything" / "registry.json"

FAKE_BINARY = """#!/bin/bash
echo "$@" >> "$FAKE_BINARY_LOG"
if [ "$1" = "--help" ]; then
  echo "--json supported"
  exit 0
fi
echo '{"ok": true}'
exit 0
"""


class FakeApiHandler(BaseHTTPRequestHandler):
    """Record the request, then answer like the Local REST API plugin."""

    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def _record(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        self.server.requests.append({
            "method": self.command,
            "path": self.path,
            "destination": self.headers.get("Destination"),
            "authorization": self.headers.get("Authorization"),
        })

    def do_MOVE(self):
        self._record()
        if self.server.mode == "error404":
            body = b'{"error": "not found"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        self._record()
        body = b'{"error": "not found"}'
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class ObsidianVaultMoveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeApiHandler)
        cls.server.daemon_threads = True
        cls.server.requests = []
        cls.server.mode = "ok"
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.server.requests.clear()
        self.server.mode = "ok"
        self.tmp = tempfile.TemporaryDirectory()
        self.bin_dir = Path(self.tmp.name) / "bin"
        self.bin_dir.mkdir()
        binary = self.bin_dir / "cli-anything-obsidian"
        binary.write_text(FAKE_BINARY)
        binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP
                     | stat.S_IXOTH)
        self.binary_log = Path(self.tmp.name) / "binary.log"
        self.binary_log.write_text("")

    def tearDown(self):
        self.tmp.cleanup()

    def _env(self, with_binary=True, api_key="test-key-123", api_url=None):
        env = dict(os.environ)
        env["CLI_ANYTHING_REGISTRY"] = str(REGISTRY)
        env["OBSIDIAN_API_URL"] = api_url or (
            "http://127.0.0.1:%d" % self.port)
        if api_key is None:
            env.pop("OBSIDIAN_API_KEY", None)
        else:
            env["OBSIDIAN_API_KEY"] = api_key
        env["FAKE_BINARY_LOG"] = str(self.binary_log)
        path = str(self.bin_dir) if with_binary else ""
        env["PATH"] = (path + os.pathsep + env["PATH"]) if path \
            else "/usr/bin:/bin"
        return env

    def _run(self, argv, **env_kwargs):
        result = subprocess.run(
            [sys.executable, str(RUNNER), *argv],
            capture_output=True, text=True, timeout=30,
            env=self._env(**env_kwargs))
        return result

    def _envelope(self, result):
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("runner stdout is not one JSON envelope: %r"
                      % result.stdout)

    def test_move_issues_proven_call(self):
        result = self._run(["run", "obsidian", "--", "vault", "move",
                            "A B.md", "Sub/A B.md"])
        self.assertEqual(result.returncode, 0, result.stderr)
        envelope = self._envelope(result)
        self.assertEqual(envelope["returncode"], 0)
        self.assertNotIn("error", envelope)
        self.assertEqual(envelope["result"]["source"], "A B.md")
        self.assertEqual(envelope["result"]["destination"], "Sub/A B.md")
        self.assertEqual(envelope["result"]["status"], 204)
        self.assertEqual(len(self.server.requests), 1)
        seen = self.server.requests[0]
        self.assertEqual(seen["method"], "MOVE")
        self.assertEqual(seen["path"], "/vault/A%20B.md")
        self.assertEqual(seen["destination"], "Sub/A B.md")
        self.assertEqual(seen["authorization"], "Bearer test-key-123")

    def test_move_encodes_special_chars_per_segment(self):
        result = self._run(["run", "obsidian", "--", "vault", "move",
                            "A&B.md", "C#D.md"])
        self.assertEqual(result.returncode, 0, result.stderr)
        seen = self.server.requests[0]
        self.assertEqual(seen["path"], "/vault/A%26B.md")
        self.assertEqual(seen["destination"], "C#D.md")

    def test_move_wrong_arg_count(self):
        for args in (["vault", "move", "only-one.md"],
                     ["vault", "move", "a.md", "b.md", "extra.md"]):
            result = self._run(["run", "obsidian", "--", *args])
            self.assertEqual(result.returncode, 2, result.stdout)
            envelope = self._envelope(result)
            self.assertIn("usage: vault move", envelope["error"])
        self.assertEqual(len(self.server.requests), 0)

    def test_move_same_source_and_destination(self):
        result = self._run(["run", "obsidian", "--", "vault", "move",
                            "same.md", "same.md"])
        self.assertEqual(result.returncode, 2, result.stdout)
        envelope = self._envelope(result)
        self.assertIn("same", envelope["error"])
        self.assertEqual(len(self.server.requests), 0)

    def test_move_missing_api_key(self):
        result = self._run(["run", "obsidian", "--", "vault", "move",
                            "a.md", "b.md"], api_key=None)
        self.assertEqual(result.returncode, 1, result.stdout)
        envelope = self._envelope(result)
        self.assertEqual(envelope["returncode"], 1)
        self.assertIn("OBSIDIAN_API_KEY", envelope["error"])
        self.assertEqual(len(self.server.requests), 0)

    def test_move_api_error_surfaces_status(self):
        self.server.mode = "error404"
        result = self._run(["run", "obsidian", "--", "vault", "move",
                            "gone.md", "b.md"])
        self.assertEqual(result.returncode, 1, result.stdout)
        envelope = self._envelope(result)
        self.assertEqual(envelope["returncode"], 1)
        self.assertIn("404", envelope["error"])

    def test_move_server_down(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        closed_port = sock.getsockname()[1]
        sock.close()
        result = self._run(["run", "obsidian", "--", "vault", "move",
                            "a.md", "b.md"],
                           api_url="http://127.0.0.1:%d" % closed_port)
        self.assertEqual(result.returncode, 1, result.stdout)
        envelope = self._envelope(result)
        self.assertIn("Cannot connect", envelope["error"])

    def test_move_needs_no_harness_binary(self):
        result = self._run(["run", "obsidian", "--", "vault", "move",
                            "a.md", "b.md"], with_binary=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.server.requests), 1)

    def test_non_move_obsidian_goes_to_binary(self):
        result = self._run(["run", "obsidian", "--", "vault", "list"])
        self.assertEqual(result.returncode, 0, result.stderr)
        envelope = self._envelope(result)
        self.assertEqual(envelope["returncode"], 0)
        self.assertEqual(len(self.server.requests), 0)
        self.assertIn("--json vault list", self.binary_log.read_text())

    def test_unknown_app_still_rejected(self):
        result = self._run(["run", "nosuchapp", "--", "vault", "move",
                            "a.md", "b.md"])
        self.assertEqual(result.returncode, 2, result.stdout)
        envelope = self._envelope(result)
        self.assertIn("not in vendored registry", envelope["error"])
        self.assertEqual(len(self.server.requests), 0)


if __name__ == "__main__":
    unittest.main()
