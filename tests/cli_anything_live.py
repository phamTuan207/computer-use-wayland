"""Live cli-anything check, LibreOffice only; no other app is tested live.

Run explicitly (not part of unittest discover):
  python3 tests/cli_anything_live.py

What it does, in a fresh temporary directory:
  1. Build a genuine scratch ODF with the installed /usr/bin/libreoffice
     (headless --convert-to odt from a small .txt) and prove it is a real
     ODF zip with the right mimetype.
  2. Install the libreoffice harness in a venv
     (pip install cli-anything-libreoffice) and run it with --json:
     `document new` to create a project, then `export render` to produce
     a scratch ODF file. Assert each run exits 0 and its stdout parses
     as JSON, and assert the rendered file is a real ODF zip.
  3. Skip cleanly (not fail) if the harness cannot be installed, e.g. no
     network; the skip reason is recorded in the skip message. If venv
     install fails but a harness entry point is already installed on
     PATH, that one is used instead.

Verified on this VM (2026-11-18): LibreOffice 24.2.7.2, harness
cli-anything-libreoffice 1.0.0 from PyPI. Two harness limits found while
probing, deliberately NOT asserted here: `document open` does not accept
a raw .odt (it expects a .lo-cli.json project and returns a JSON
UnicodeDecodeError), and `writer add-paragraph` does not persist across
invocations (the change lives only in that process).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

PACKAGE = "cli-anything-libreoffice"
BINARY = "cli-anything-libreoffice"
ODF_MIMETYPE = b"application/vnd.oasis.opendocument.text"
INSTALL_TIMEOUT_SECONDS = 300
RUN_TIMEOUT_SECONDS = 60
CONVERT_TIMEOUT_SECONDS = 120


def run(argv, cwd, timeout):
    """Run argv (no shell), capturing text output."""
    return subprocess.run(argv, cwd=str(cwd), capture_output=True,
                          text=True, timeout=timeout)


def assert_real_odf(testcase, path):
    """Assert path is a real ODF zip with the ODF text mimetype."""
    testcase.assertTrue(zipfile.is_zipfile(path),
                        "%s is not a zip (not a real ODF file)" % path)
    with zipfile.ZipFile(path) as archive:
        testcase.assertEqual(archive.read("mimetype"), ODF_MIMETYPE)


class CliAnythingLiveLibreOffice(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        if shutil.which("libreoffice") is None:
            self.skipTest("libreoffice not installed on PATH")

    def _install_harness(self):
        """Return the harness binary path; skip if it cannot be provided."""
        venv = self.work / "venv"
        pip = venv / "bin" / "pip"
        binary = venv / "bin" / BINARY
        reason = None
        try:
            result = run([sys.executable, "-m", "venv", str(venv)],
                         self.work, RUN_TIMEOUT_SECONDS)
            if result.returncode != 0:
                raise RuntimeError(
                    "venv creation failed (rc=%d): %s"
                    % (result.returncode, result.stderr.strip()[-500:]))
            result = run([str(pip), "install", PACKAGE],
                         self.work, INSTALL_TIMEOUT_SECONDS)
            if result.returncode != 0:
                raise RuntimeError(
                    "pip install %s failed (rc=%d): %s"
                    % (PACKAGE, result.returncode,
                       result.stderr.strip()[-500:]))
            if not binary.is_file():
                raise RuntimeError(
                    "pip install succeeded but %s is missing" % BINARY)
            return str(binary)
        except (OSError, subprocess.TimeoutExpired,
                subprocess.SubprocessError, RuntimeError) as exc:
            reason = str(exc)
        system_binary = shutil.which(BINARY)
        if system_binary:
            return system_binary
        self.skipTest("harness unavailable, install failed: %s" % reason)

    def test_libreoffice_json_produces_real_odf(self):
        harness = self._install_harness()

        # 1. Genuine scratch ODF from the installed LibreOffice.
        source = self.work / "scratch.txt"
        source.write_text("hello cli-anything\nsecond line\n")
        converted = run(["libreoffice", "--headless", "--convert-to", "odt",
                         "--outdir", str(self.work), str(source)],
                        self.work, CONVERT_TIMEOUT_SECONDS)
        self.assertEqual(converted.returncode, 0,
                         "headless soffice convert failed: %s"
                         % converted.stderr[-500:])
        scratch_odt = self.work / "scratch.odt"
        self.assertTrue(scratch_odt.is_file(), "scratch.odt was not created")
        assert_real_odf(self, scratch_odt)

        # 2. Harness with --json: create a project.
        project = self.work / "project.json"
        created = run([harness, "--json", "document", "new",
                       "--type", "writer", "-n", "live-test",
                       "-o", str(project)],
                      self.work, RUN_TIMEOUT_SECONDS)
        self.assertEqual(created.returncode, 0,
                         "harness document new failed: %s"
                         % created.stderr[-500:])
        payload = json.loads(created.stdout)
        self.assertEqual(payload["name"], "live-test")
        self.assertEqual(payload["type"], "writer")
        self.assertTrue(project.is_file(), "project file was not created")

        # 3. Harness with --json: render the project to a scratch ODF file.
        rendered = self.work / "rendered.odt"
        result = run([harness, "--json", "--project", str(project),
                      "export", "render", str(rendered)],
                     self.work, RUN_TIMEOUT_SECONDS)
        self.assertEqual(result.returncode, 0,
                         "harness export render failed: %s"
                         % result.stderr[-500:])
        payload = json.loads(result.stdout)
        self.assertEqual(payload["output"], str(rendered))
        self.assertTrue(rendered.is_file(), "rendered.odt was not created")
        assert_real_odf(self, rendered)


if __name__ == "__main__":
    unittest.main()
