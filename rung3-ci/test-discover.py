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
  run       one discover run; prints "@@RESULT@@ <test-id> <status>"
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

    @staticmethod
    def qualified_id(test):
        tid = test.id()
        if "." not in tid:
            # FunctionTestCase ids are bare function names; two
            # modules can define the same name (test_cli_exit_codes
            # exists in both test_phase3_brief and
            # test_phase3_cleanup). Qualify with the function module.
            func = getattr(test, "_testFunc", None)
            module = getattr(func, "__module__", None) or \
                type(test).__module__
            tid = module + "." + tid
        return tid

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes[self.qualified_id(test)] = "ok"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes[self.qualified_id(test)] = "fail"

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes[self.qualified_id(test)] = "error"

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes[self.qualified_id(test)] = "skip"

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            # A failure inside subTest never reaches addFailure or
            # addError for the parent test, so record it here or
            # the test vanishes from the outcomes entirely.
            status = ("fail" if issubclass(err[0], test.failureException)
                      else "error")
            tid = self.qualified_id(test)
            if self.outcomes.get(tid) != "error":
                self.outcomes[tid] = status


def run_suite(suite):
    all_ids = {RecordingResult.qualified_id(t) for t in iter_tests(suite)}
    runner = unittest.TextTestRunner(stream=open(os.devnull, "w"),
                                     resultclass=RecordingResult, verbosity=0)
    result = runner.run(suite)
    outcomes = result.outcomes
    # A setUpClass/setUpModule failure records one pseudo-test
    # outcome ("setUpClass (mod.Cls)") and no per-test outcomes;
    # expand it so every discovered test has an outcome.
    for pseudo in [k for k in outcomes
                   if k.startswith(("setUpClass (", "setUpModule ("))]:
        status = outcomes.pop(pseudo)
        prefix = pseudo[pseudo.index("(") + 1:-1] + "."
        for tid in all_ids:
            if tid.startswith(prefix):
                outcomes.setdefault(tid, status)
    return outcomes


def failed_test_module(test):
    """Full module path for a _FailedTest (import failure).

    The id is unittest.loader._FailedTest.<module>; the module
    part keeps its package path (sub1.test_dup, not test_dup).
    """
    tid = test.id()
    prefix = "unittest.loader._FailedTest."
    if tid.startswith(prefix):
        return tid[len(prefix):]
    return tid.rsplit(".", 1)[-1]


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
            # _FailedTest: attribute by full module path.
            if failed_test_module(test) in wanted:
                suite.addTest(test)
    return suite


def module_test_counts(start_dir, pattern):
    suite = load_suite(start_dir, pattern)
    counts = {}
    for test in iter_tests(suite):
        mod = test.__class__.__module__
        if mod == "unittest.loader":
            # _FailedTest for a module that failed to import;
            # attribute by full module path.
            mod = failed_test_module(test)
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


def parse_results(stdout):
    """Parse @@RESULT@@ lines; also report whether SUMMARY arrived.

    The SUMMARY line is printed only after a run completes, so
    its absence means the child died mid-run (e.g. os._exit in
    a test) even when the exit code is 0.
    """
    outcomes = {}
    saw_summary = False
    for line in stdout.splitlines():
        if line.startswith("@@RESULT@@ "):
            # Status is the last word; a test id may itself contain
            # spaces (str()-format ids), so split from the right.
            tid, sep, status = line[len("@@RESULT@@ "):].rpartition(" ")
            if sep:
                outcomes[tid] = status
        elif line.startswith("SUMMARY "):
            saw_summary = True
    return outcomes, saw_summary


def child_problem(label, outcomes, saw_summary, returncode, stderr):
    """Fail-closed check for one run child; None means complete."""
    if returncode != 0:
        lines = (stderr or "").strip().splitlines()
        detail = lines[-1] if lines else "no stderr"
        return f"{label} child exited {returncode}: {detail}"
    if not saw_summary:
        return f"{label} child produced no SUMMARY line (incomplete run)"
    if not outcomes:
        return f"{label} run produced zero test outcomes"
    return None


def expected_test_ids(start_dir, pattern, modules=None):
    """Qualified ids a full run should report (deduplicated).

    Outcomes are keyed by qualified id, and the suite contains
    duplicate ids, so shard completeness is checked against
    this id set, not against the raw test count.
    """
    if modules:
        suite = suite_for_modules(modules, start_dir, pattern)
    else:
        suite = load_suite(start_dir, pattern)
    return {RecordingResult.qualified_id(t) for t in iter_tests(suite)}


def run_subprocess(args, env=None, timeout=1800):
    start = time.monotonic()
    proc = subprocess.run([sys.executable, os.path.abspath(__file__)] + args,
                          capture_output=True, text=True, env=env,
                          timeout=timeout)
    wall = time.monotonic() - start
    outcomes, saw_summary = parse_results(proc.stdout)
    return outcomes, wall, proc, saw_summary


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
    normal, wall_n, proc_n, sum_n = run_subprocess(base,
                                                   timeout=args.timeout)
    env, tmp = stripped_env()
    try:
        stripped, wall_s, proc_s, sum_s = run_subprocess(
            base, env=env, timeout=args.timeout)
    finally:
        os.unlink(os.path.join(tmp, "python3"))
        os.rmdir(tmp)
    print(f"normal: {len(normal)} tests in {wall_n:.1f}s; "
          f"stripped: {len(stripped)} tests in {wall_s:.1f}s")
    problems = [p for p in (
        child_problem("normal", normal, sum_n,
                      proc_n.returncode, proc_n.stderr),
        child_problem("stripped", stripped, sum_s,
                      proc_s.returncode, proc_s.stderr)) if p]
    if problems:
        for p in problems:
            print(f"HERMETIC GATE FAIL: {p}")
        return 1
    deps, pre_existing, only_stripped, only_normal = diff_outcomes(
        normal, stripped)
    print(f"pre-existing failures (both envs): {len(pre_existing)}")
    skips_n = sum(1 for s in normal.values() if s == "skip")
    skips_s = sum(1 for s in stripped.values() if s == "skip")
    print(f"skips: normal={skips_n}, stripped={skips_s}")
    if only_stripped or only_normal:
        print(f"HERMETIC GATE FAIL: test sets differ "
              f"(only-normal={len(only_normal)}, "
              f"only-stripped={len(only_stripped)})")
        for t in only_normal[:20]:
            print(f"  only-normal: {t}")
        for t in only_stripped[:20]:
            print(f"  only-stripped: {t}")
        return 1
    if deps:
        print(f"HERMETIC GATE FAIL: {len(deps)} test(s) depend on "
              f"optional tools (pass normally, fail stripped):")
        for t in deps:
            print(f"  {t}")
        return 1
    print("HERMETIC GATE PASS: no stripped-only failures")
    return 0


def cmd_shard(args):
    try:
        counts = module_test_counts(args.start_dir, args.pattern)
    except ImportError as exc:
        print(f"SHARD FAIL: cannot discover tests in "
              f"{args.start_dir}: {exc}")
        return 1
    if args.modules:
        prefix = os.path.basename(os.path.normpath(args.start_dir)) + "."
        wanted = {m[len(prefix):] if m.startswith(prefix) else m
                  for m in args.modules}
        unknown = sorted(wanted - set(counts))
        if unknown:
            print(f"SHARD FAIL: unknown module(s): {', '.join(unknown)}")
            return 1
        counts = {m: c for m, c in counts.items() if m in wanted}
    if not counts or sum(counts.values()) == 0:
        print("SHARD FAIL: no tests discovered")
        return 1
    expected = expected_test_ids(args.start_dir, args.pattern,
                                 args.modules)
    # Load-sensitive modules run serially in the parent: their
    # real-signal timing tests flake under parallel CPU load
    # (measured 2026-11-27: test_ime_cleanup passes 3/3 serial,
    # flakes under 4 shards on a 1.5-CPU VM).
    serial_only = [m for m in counts if m in set(args.serial_only)]
    shard_counts = {m: c for m, c in counts.items()
                    if m not in set(args.serial_only)}
    shards = balance_shards(shard_counts, args.shards)
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
    problems = []
    for p in procs:
        out, err = p.communicate(timeout=args.timeout)
        shard_outcomes, saw_summary = parse_results(out)
        outcomes.update(shard_outcomes)
        problem = child_problem("shard", shard_outcomes, saw_summary,
                                p.returncode, err)
        if problem:
            problems.append(problem)
    if serial_only:
        extra, _wall, proc, saw_summary = run_subprocess(
            ["run", "--start-dir", args.start_dir,
             "--pattern", args.pattern, "--modules"] + serial_only,
            timeout=args.timeout)
        outcomes.update(extra)
        problem = child_problem("serial-only", extra, saw_summary,
                                proc.returncode, proc.stderr)
        if problem:
            problems.append(problem)
    wall = time.monotonic() - start
    counts_out = {}
    for s in outcomes.values():
        counts_out[s] = counts_out.get(s, 0) + 1
    print(f"sharded: {len(outcomes)} tests in {wall:.1f}s "
          f"({args.shards} shards, expected {len(expected)}) " +
          " ".join(f"{k}={v}" for k, v in sorted(counts_out.items())))
    missing = sorted(expected - set(outcomes))
    unexpected = sorted(set(outcomes) - expected)
    if problems or missing or unexpected:
        for p in problems:
            print(f"SHARD FAIL: {p}")
        if missing:
            print(f"SHARD FAIL: {len(missing)} expected test(s) "
                  f"missing from shard results:")
            for t in missing[:20]:
                print(f"  missing: {t}")
        if unexpected:
            print(f"SHARD FAIL: {len(unexpected)} unexpected test(s) "
                  f"in shard results:")
            for t in unexpected[:20]:
                print(f"  unexpected: {t}")
        return 1
    if args.compare_serial:
        base = ["run", "--start-dir", args.start_dir,
                "--pattern", args.pattern]
        if args.modules:
            base += ["--modules"] + args.modules
        serial, wall_serial, proc, saw_summary = run_subprocess(
            base, timeout=args.timeout)
        print(f"serial: {len(serial)} tests in {wall_serial:.1f}s")
        problem = child_problem("serial", serial, saw_summary,
                                proc.returncode, proc.stderr)
        if problem:
            print(f"SHARD FAIL: {problem}")
            return 1
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
    sub.choices["shard"].add_argument(
        "--serial-only", nargs="*", default=["test_ime_cleanup"],
        help="modules run serially in the parent (load-sensitive)")
    args = ap.parse_args(argv)
    return {"run": cmd_run, "hermetic": cmd_hermetic,
            "shard": cmd_shard}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
