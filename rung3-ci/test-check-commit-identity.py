#!/usr/bin/env python3
"""Unit tests for check-commit-identity.py.

Run: python3 rung3-ci/test-check-commit-identity.py
"""
import importlib.util
import os
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "check_identity", os.path.join(HERE, "check-commit-identity.py"))
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


def git(d, *args, env=None):
    subprocess.run(["git", "-C", d, *args], check=True,
                   capture_output=True, text=True, env=env)


class IdentityTests(unittest.TestCase):
    def test_email_ok_forms(self):
        self.assertTrue(ci.email_ok("1+user@users.noreply.github.com"))
        self.assertTrue(ci.email_ok("noreply@github.com"))
        self.assertTrue(ci.email_ok("Noreply@GitHub.com"))
        self.assertFalse(ci.email_ok("someone@example.com"))
        self.assertFalse(ci.email_ok("agent@local"))

    def test_range_check(self):
        with tempfile.TemporaryDirectory() as d:
            git(d, "init", "-q")
            git(d, "config", "user.name", "t")
            git(d, "config", "user.email",
                "1+t@users.noreply.github.com")
            with open(os.path.join(d, "a.txt"), "w") as fh:
                fh.write("a\n")
            git(d, "add", "a.txt")
            git(d, "commit", "-qm", "good")
            git(d, "config", "user.email", "someone@example.com")
            with open(os.path.join(d, "b.txt"), "w") as fh:
                fh.write("b\n")
            git(d, "add", "b.txt")
            git(d, "commit", "-qm", "bad")
            cwd = os.getcwd()
            os.chdir(d)
            try:
                self.assertEqual(ci.main(["x", "HEAD~1..HEAD"]), 1)
                self.assertEqual(ci.main(["x", "HEAD~1"]), 0)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
