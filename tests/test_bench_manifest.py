#!/usr/bin/env python3
"""Tests for scripts/bench_manifest.py (CB-9 checkout-run bench shape).

Uses a temp git repo with a stub sync-installed.py (only the digest
helpers the manifest reuses) plus dummy bench script and fixture, so
the test does not depend on the real checkout or a live browser.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "bench_manifest.py"

STUB_SYNC = '''\
import hashlib
import json
import subprocess
from pathlib import Path


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_bundle(repo):
    raw = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "-z"], text=True)
    entries = {}
    for name in raw.split("\\0"):
        if not name:
            continue
        entries[name] = {"type": "file", "sha256": _sha256(Path(repo) / name)}
    return entries


def _digest_entries(entries):
    raw = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()
'''


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "_bench_manifest_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BenchManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "tests").mkdir(parents=True)
        (self.repo / "scripts" / "sync-installed.py").write_text(STUB_SYNC)
        (self.repo / "tests" / "two_vision_bench.py").write_text(
            "# dummy bench\n")
        (self.repo / "tests" / "two_vision_fixture.html").write_text(
            "<html></html>\n")
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "add", "."],
                       check=True, env=env)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "init"],
                       check=True, env=env)
        self.results = Path(self.tmp.name) / "results.json"
        self.results.write_text(json.dumps({
            "run_id": "bench-test-1", "mode": "run", "live": False,
            "outcome": "PASS", "wall_s": 1.23, "visions_used": 2,
            "steps": [{"step": 1, "status": "sent"},
                      {"step": 2, "status": "sent"}]}))
        self.log = self.repo / "improvements" / "test-log.md"
        self.module = _load_script()

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, results=None):
        return self.module.write_manifest(
            self.repo, results or self.results,
            "improvements/test-log.md",
            Path(self.tmp.name) / "deploy-manifest.json",
            python_version="3.12.3", selenium_version="4.53.0",
            fixture_main_path=str(
                self.repo / "tests" / "two_vision_fixture.html"))

    def test_write_pins_commit_and_artifacts(self):
        manifest, path = self._write()
        head = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            text=True).strip()
        self.assertEqual(manifest["source_commit"], head)
        self.assertEqual(manifest["bench"]["run_id"], "bench-test-1")
        self.assertEqual(manifest["bench"]["outcome"], "PASS")
        self.assertEqual(manifest["bench_shape"], "checkout-run")
        self.assertTrue(manifest["git_status_clean"])
        bench = manifest["artifacts"]["bench_script"]
        self.assertEqual(
            bench["sha256"],
            hashlib.sha256(b"# dummy bench\n").hexdigest())
        self.assertEqual(manifest["artifacts"]["selenium"], "4.53.0")
        self.assertTrue(path.is_file())

    def test_verify_passes_with_log_then_fails_on_tamper(self):
        manifest, path = self._write()
        head = manifest["source_commit"]
        self.log.parent.mkdir(parents=True)
        self.log.write_text(
            f"run {manifest['bench']['run_id']} at {head}\n")
        checks, failed = self.module.verify_manifest(
            path, self.repo, self.results, log_root=self.repo)
        self.assertEqual(failed, [], [c for c in checks if not c[1]])
        (self.repo / "tests" / "two_vision_bench.py").write_text(
            "# tampered\n")
        _checks, failed = self.module.verify_manifest(
            path, self.repo, self.results, log_root=self.repo)
        self.assertIn("artifact:bench_script", failed)

    def test_write_refuses_non_pass(self):
        bad = Path(self.tmp.name) / "bad.json"
        bad.write_text(json.dumps({
            "run_id": "bench-test-2", "mode": "run", "live": False,
            "outcome": "FAIL", "wall_s": 1.0, "visions_used": 2}))
        with self.assertRaises(self.module.ManifestError):
            self._write(results=bad)

    def test_write_refuses_dirty_checkout(self):
        (self.repo / "tests" / "two_vision_fixture.html").write_text(
            "<html>dirty</html>\n")
        with self.assertRaises(self.module.ManifestError):
            self._write()


if __name__ == "__main__":
    unittest.main()
