"""Scratch-repo tests for scripts/watchdog_append.py (M28a).

Builds a bare remote plus two clones under a temp dir and proves
the three properties the rolling branch exists for:
  1. appends accumulate (rollup returns every entry, in order),
  2. history is never rewritten (every earlier tip stays an
     ancestor of every later tip; history is linear),
  3. concurrent appends from two clones lose nothing (the retry
     on non-fast-forward lands every entry).
Plus the PII gate refusing a credential-bearing entry.
Run: python3 -m unittest tests.test_watchdog_append
"""
import os
import subprocess
import sys
import tempfile
import threading
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "scripts", "watchdog_append.py")
PII_SCAN = os.path.join(REPO_ROOT, "rung3-ci", "pii-scan.py")


def run(*args, **kwargs):
    proc = subprocess.run(args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, **kwargs)
    if proc.returncode != 0:
        raise AssertionError("%s failed rc=%d\n%s\n%s" % (
            " ".join(args), proc.returncode, proc.stdout, proc.stderr))
    return proc.stdout.strip()


def git(repo, *args):
    return run("git", "-C", repo, *args)


def append(repo, text, lane="testlane", extra=()):
    proc = subprocess.run(
        [sys.executable, SCRIPT, "append", "--lane", lane,
         "--repo", repo, "--pii-scan", PII_SCAN] + list(extra),
        input=text, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True)
    return proc


class WatchdogAppendTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="watchdog-append-test-")
        self.remote = os.path.join(self.tmp, "remote.git")
        run("git", "init", "--bare", "-q", self.remote)
        self.clone_a = self._clone("a")
        self.clone_b = self._clone("b")

    def _clone(self, name):
        path = os.path.join(self.tmp, name)
        run("git", "clone", "-q", self.remote, path)
        git(path, "config", "user.email", "test@example.invalid")
        git(path, "config", "user.name", "watchdog test")
        return path

    def tearDown(self):
        run("rm", "-rf", self.tmp)

    def tip(self):
        out = run("git", "-C", self.remote, "rev-parse",
                  "refs/heads/watchdog/testlane")
        return out

    def rollup(self, repo):
        out = os.path.join(self.tmp, "rolled.md")
        run(sys.executable, SCRIPT, "rollup", "--lane", "testlane",
            "--repo", repo, "--out", out)
        with open(out, encoding="utf-8") as fh:
            return fh.read()

    def test_appends_accumulate(self):
        for i in range(3):
            proc = append(self.clone_a, "## tick %d\nall clear\n" % i)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("APPENDED:", proc.stdout)
        body = self.rollup(self.clone_b)
        for i in range(3):
            self.assertIn("tick %d" % i, body)
        self.assertLess(body.index("tick 0"), body.index("tick 2"))

    def test_history_never_rewritten(self):
        tips = []
        for i in range(4):
            proc = append(self.clone_a, "## tick %d\n" % i)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            tips.append(self.tip())
        for earlier, later in zip(tips, tips[1:]):
            proc = subprocess.run(
                ["git", "-C", self.remote, "merge-base",
                 "--is-ancestor", earlier, later])
            self.assertEqual(proc.returncode, 0,
                             "%s not ancestor of %s" % (earlier, later))
        parents = run("git", "-C", self.remote, "rev-list",
                      "--parents", tips[-1]).splitlines()
        self.assertEqual(len(parents), 4)
        for line in parents:
            self.assertLessEqual(len(line.split()), 2,
                                 "history must stay linear: " + line)

    def test_concurrent_appends_lose_nothing(self):
        per_writer = 5
        failures = []

        def writer(repo, tag):
            for i in range(per_writer):
                proc = append(repo, "## %s tick %d\n" % (tag, i))
                if proc.returncode != 0:
                    failures.append((tag, i, proc.stderr))

        threads = [threading.Thread(target=writer,
                                     args=(self.clone_a, "alpha")),
                   threading.Thread(target=writer,
                                     args=(self.clone_b, "beta"))]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(failures, [])
        body = self.rollup(self.clone_a)
        for tag in ("alpha", "beta"):
            for i in range(per_writer):
                self.assertIn("%s tick %d" % (tag, i), body)
        count = run("git", "-C", self.remote, "rev-list", "--count",
                    "refs/heads/watchdog/testlane")
        self.assertEqual(int(count), 2 * per_writer)

    def test_pii_entry_refused(self):
        proc = append(self.clone_a, "## tick\ncontact: a@b.example\n")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("PII gate refused", proc.stderr + proc.stdout)
        proc = subprocess.run(
            ["git", "-C", self.remote, "rev-parse", "--verify",
             "refs/heads/watchdog/testlane"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotEqual(proc.returncode, 0,
                            "refused entry must not create the branch")

    def test_no_force_push_path(self):
        with open(SCRIPT, encoding="utf-8") as fh:
            source = fh.read()
        self.assertNotIn("--force", source)
        self.assertNotIn("force-with-lease", source)


if __name__ == "__main__":
    unittest.main()
