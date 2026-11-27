#!/usr/bin/env python3
"""Test discover tooling: per-test runner, hermetic diff gate, sharding.

Bottleneck study M16/M17 (improvements/bottleneck-study-20261127.md):
- M16: run the discover in a tool-stripped environment so tests that
  secretly depend on optional binaries (the tc02 tesseract pair)
  fail in CI instead of in a lane. This is a detector for that
  class, never a hermeticity certificate: a test that passes with a
  full PATH but fails with a stripped PATH depends on an optional
  tool without mocking or guarding it. Tests failing in both
  environments are pre-existing and reported, not gated.
- M17: shard the discover across parallel subprocesses, balanced
  by test count. The serial run stays the gate of record; with
  --compare-serial any per-test mismatch exits nonzero (the
  quarantine signal: sharding is not trusted until explained).

Modes:
  run       one discover run; prints "RESULT <test-id> <status>"
            lines (ok|fail|error|skip) plus a SUMMARY line.
  hermetic  run normal + stripped, diff per test, gate on
            stripped-only failures.
  shard     N parallel shards; optional --compare-serial.

Python standard library only.
"""
import argparse
import os
import subprocess
import sys
import tempfile
import time
import unittest


def load_suite(start_dir, pattern, top_level=None):
    loader = unittest.TestLoader()
    return loader.discover(start_dir, pattern=pattern, top_level_dir=top_level)


def iter_tests(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from iter_tests(item)
        else:
            yield item


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.outcomes = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes[test.id()] = "ok"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes[test.id()] = "fail"

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes[test.id()] = "error"

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes[test.id()] = "skip"


def run_suite(suite):
    runner = unittest.TextTestRunner(stream=open(os.devnull, "w"),
                                     resultclass=RecordingResult, verbosity=0)
    result = runner.run(suite)
    return result.outcomes


def suite_for_modules(modules, start_dir="tests", pattern="test_*.py"):
    # Filter a discovered suite instead of loadTestsFromName:
    # discover and by-name loading produce different test ids for
    # modules that fail to import (unittest.loader._FailedTest.*),
    # which breaks per-test identity against the serial run.
    prefix = os.path.basename(os.path.normpath(start_dir)) + "."
    wanted = {m[len(prefix):] if m.startswith(prefix) else m
              for m in modules}
    full = load_suite(start_dir, pattern)
    suite = unittest.TestSuite()
    for test in iter_tests(full):
        mod = test.__class__.__module__
        if mod in wanted:
            suite.addTest(test)
        elif mod == "unittest.loader":
            # _FailedTest id ends with the failing module name.
            if test.id().rsplit(".", 1)[-1] in wanted:
                suite.addTest(test)
    return suite


def module_test_counts(start_dir, pattern):
    suite = load_suite(start_dir, pattern)
    counts = {}
    for test in iter_tests(suite):
        mod = test.__class__.__module__
        if mod == "unittest.loader":
            # _FailedTest for a module that failed to import; the
            # failing module name is the last id component.
            mod = test.id().rsplit(".", 1)[-1]
        counts[mod] = counts.get(mod, 0) + 1
    return counts


def balance_shards(counts, n_shards):
    """Greedy largest-first assignment; returns list of module lists."""
    shards = [[] for _ in range(n_shards)]
    loads = [0] * n_shards
    for mod, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        i = loads.index(min(loads))
        shards[i].append(mod)
        loads[i] += count
    return shards


def stripped_env():
    """Environment whose PATH contains only a python3 symlink dir."""
    tmp = tempfile.mkdtemp(prefix="hermetic-bin-")
    os.symlink(sys.executable, os.path.join(tmp, "python3"))
    env = dict(os.environ)
    env["PATH"] = tmp
    return env, tmp


def run_subprocess(args, env=None, timeout=1800):
    start = time.monotonic()
    proc = subprocess.run([sys.executable, os.path.abspath(__file__)] + args,
                          capture_output=True, text=True, env=env,
                          timeout=timeout)
    wall = time.monotonic() - start
    outcomes = {}
    for line in proc.stdout.splitlines():
        if line.startswith("@@RESULT@@ "):
            parts = line.split(" ", 2)
            if len(parts) == 3:
                outcomes[parts[1]] = parts[2]
    return outcomes, wall, proc


def diff_outcomes(normal, stripped):
    """Tests ok normally but fail/error when stripped = tool deps."""
    deps = sorted(t for t, s in normal.items()
                  if s == "ok" and stripped.get(t) in ("fail", "error"))
    pre_existing = sorted(t for t, s in normal.items()
                          if s in ("fail", "error")
                          and stripped.get(t) in ("fail", "error"))
    only_stripped = sorted(set(stripped) - set(normal))
    only_normal = sorted(set(normal) - set(stripped))
    return deps, pre_existing, only_stripped, only_normal


def cmd_run(args):
    if args.modules:
        suite = suite_for_modules(args.modules, args.start_dir)
    else:
        suite = load_suite(args.start_dir, args.pattern)
    outcomes = run_suite(suite)
    for test_id in sorted(outcomes):
        print(f"@@RESULT@@ {test_id} {outcomes[test_id]}")
    counts = {}
    for s in outcomes.values():
        counts[s] = counts.get(s, 0) + 1
    print(f"SUMMARY total={len(outcomes)} " +
          " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


def cmd_hermetic(args):
    base = ["run", "--start-dir", args.start_dir, "--pattern", args.pattern]
    if args.modules:
        base += ["--modules"] + args.modules
    normal, wall_n, _ = run_subprocess(base, timeout=args.timeout)
    env, tmp = stripped_env()
    try:
        stripped, wall_s, _ = run_subprocess(base, env=env,
                                             timeout=args.timeout)
    finally:
        os.unlink(os.path.join(tmp, "python3"))
        os.rmdir(tmp)
    deps, pre_existing, only_stripped, only_normal = diff_outcomes(
        normal, stripped)
    print(f"normal: {len(normal)} tests in {wall_n:.1f}s; "
          f"stripped: {len(stripped)} tests in {wall_s:.1f}s")
    print(f"pre-existing failures (both envs): {len(pre_existing)}")
    if only_stripped or only_normal:
        print(f"WARNING: test sets differ (only-normal={len(only_normal)}, "
              f"only-stripped={len(only_stripped)})")
    if deps:
        print(f"HERMETIC GATE FAIL: {len(deps)} test(s) depend on "
              f"optional tools (pass normally, fail stripped):")
        for t in deps:
            print(f"  {t}")
        return 1
    print("HERMETIC GATE PASS: no stripped-only failures")
    return 0


def cmd_shard(args):
    counts = module_test_counts(args.start_dir, args.pattern)
    if args.modules:
        prefix = os.path.basename(os.path.normpath(args.start_dir)) + "."
        wanted = {m[len(prefix):] if m.startswith(prefix) else m
                  for m in args.modules}
        counts = {m: c for m, c in counts.items() if m in wanted}
    shards = balance_shards(counts, args.shards)
    start = time.monotonic()
    procs = []
    for mods in shards:
        if not mods:
            continue
        cmd = [sys.executable, os.path.abspath(__file__), "run",
               "--start-dir", args.start_dir, "--pattern", args.pattern,
               "--modules"] + mods
        procs.append(subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True))
    outcomes = {}
    for p in procs:
        out, _ = p.communicate(timeout=args.timeout)
        for line in out.splitlines():
            if line.startswith("@@RESULT@@ "):
                parts = line.split(" ", 2)
                if len(parts) == 3:
                    outcomes[parts[1]] = parts[2]
    wall = time.monotonic() - start
    counts_out = {}
    for s in outcomes.values():
        counts_out[s] = counts_out.get(s, 0) + 1
    print(f"sharded: {len(outcomes)} tests in {wall:.1f}s "
          f"({args.shards} shards) " +
          " ".join(f"{k}={v}" for k, v in sorted(counts_out.items())))
    if args.compare_serial:
        base = ["run", "--start-dir", args.start_dir,
                "--pattern", args.pattern]
        if args.modules:
            base += ["--modules"] + args.modules
        serial, wall_serial, _ = run_subprocess(base, timeout=args.timeout)
        print(f"serial: {len(serial)} tests in {wall_serial:.1f}s")
        mismatches = sorted(
            t for t in set(serial) | set(outcomes)
            if serial.get(t) != outcomes.get(t))
        if mismatches:
            print(f"SHARD MISMATCH: {len(mismatches)} test(s) differ "
                  f"from serial; sharding quarantined until explained:")
            for t in mismatches[:20]:
                print(f"  {t}: serial={serial.get(t)} shard={outcomes.get(t)}")
            return 1
        print("SHARD MATCH: per-test identity equals serial")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "hermetic", "shard"):
        p = sub.add_parser(name)
        p.add_argument("--start-dir", default="tests")
        p.add_argument("--pattern", default="test_*.py")
        p.add_argument("--modules", nargs="*", default=None,
                       help="restrict to these test modules")
        p.add_argument("--timeout", type=int, default=1800)
    sub.choices["shard"].add_argument("--shards", type=int, default=4)
    sub.choices["shard"].add_argument("--compare-serial",
                                      action="store_true")
    args = ap.parse_args(argv)
    return {"run": cmd_run, "hermetic": cmd_hermetic,
            "shard": cmd_shard}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
