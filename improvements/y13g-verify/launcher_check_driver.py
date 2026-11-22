#!/usr/bin/env python3
"""Run one launcher check against a staged ship, out of process.

The launcher cannot be imported (its module-top guard exits 2),
so this driver AST-extracts the check functions from the
COMMITTED launcher file and calls one of them with SHIP_DIR
pointed at a staged ship. It never imports the ship and never
execs ship code: a forged entry .pyc is only marshal-loaded by
_check_entry_pyc, never executed, so a POISON-MARKER in this
driver's output would prove the check itself executed ship code.

Usage:
  python3 launcher_check_driver.py --ship-dir DIR --check CHECK
      [--repo REPO]
  CHECK: entry-pyc | scan | manifest | marker | runner-quiet

Exit 0: the check passed. Exit 2: the check refused (message on
stderr). Any other exit is a driver error. Stdout/stderr are the
evidence: a marker string here means ship code executed.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import extract_lib

LAUNCHER = os.path.join(REPO, "tests", "realistic", "launch_y13.py")

CHECKS = {
    "entry-pyc": (("_check_entry_pyc", "_fail"), ()),
    "scan": (("_scan_ship", "_ship_manifest_entries", "_fail"), ()),
    "manifest": (("_check_remote", "_normalize_remote_url",
                  "check_manifest", "_fail",
                  "_is_exempt_cache_dir", "_is_entry_pyc_rel"),
                 ("MARKER_RE", "ABORT_RE", "KNOWN_REMOTE_URL",
                  "_ENTRY_STEMS")),
    "marker": (("_check_remote", "_normalize_remote_url",
                "check_marker", "_fail"),
               ("MARKER_RE", "ABORT_RE", "KNOWN_REMOTE_URL")),
    "runner-quiet": (("check_runner_quiet", "_own_ancestry", "_cmdline",
                      "_environ",
                      "_is_runner_cmdline", "_is_codex_process",
                      "_command_executes_runner", "_fail",
                      "_script_basename_is_runner", "_is_python_token",
                      "_shlex_tokens", "_runner_md5s",
                      "_path_is_runner_copy", "_token_is_runner_script",
                      "_c_code_executes_runner", "_m_module_is_runner",
                      "_python_executes_runner", "_is_timeout_dur",
                      "_argv_tokens"),
                     ("_RUNNER_MODULE_NAMES", "_RUNNER_MANIFEST_PATHS",
                      "_RUNNER_MD5S", "_PY_NO_VALUE",
                      "CODEX_REFUSE_MARKERS")),
}


def main(argv):
    args = argv[1:]
    ship_dir = None
    check = None
    repo = None
    i = 0
    while i < len(args):
        if args[i] == "--ship-dir":
            ship_dir = args[i + 1]
            i += 2
        elif args[i] == "--check":
            check = args[i + 1]
            i += 2
        elif args[i] == "--repo":
            repo = args[i + 1]
            i += 2
        else:
            print(f"unknown arg: {args[i]}", file=sys.stderr)
            return 2
    if check not in CHECKS:
        print(__doc__, file=sys.stderr)
        return 2
    if not ship_dir:
        # Marker checks never touch SHIP_DIR; default it to the
        # repo dir (or cwd) so the extraction still has a value.
        ship_dir = repo or os.getcwd()
    funcs, consts = CHECKS[check]
    ns = extract_lib.extract_funcs(
        LAUNCHER, funcs, consts,
        extra={"_SHIP_DIR": ship_dir, "SHIP_DIR": ship_dir})
    try:
        if check in ("manifest", "marker"):
            ns["check_" + check](repo)
        elif check == "runner-quiet":
            ns["check_runner_quiet"]()
        elif check == "entry-pyc":
            ns["_check_entry_pyc"]()
        elif check == "scan":
            ns["_scan_ship"]()
    except SystemExit as exc:
        print(f"DRIVER-REFUSED rc={exc.code}", file=sys.stderr)
        return 2 if exc.code in (2, None) else int(exc.code or 2)
    print(f"DRIVER-OK check={check} ship={ship_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
