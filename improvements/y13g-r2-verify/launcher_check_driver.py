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
                  "check_manifest", "_fail"),
                 ("MARKER_RE", "ABORT_RE", "KNOWN_REMOTE_URL")),
    "marker": (("_check_remote", "_normalize_remote_url",
                "check_marker", "_fail"),
               ("MARKER_RE", "ABORT_RE", "KNOWN_REMOTE_URL")),
    "remote": (("_check_remote", "_normalize_remote_url", "_fail"),
               ("KNOWN_REMOTE_URL",)),
    "runner-quiet": (("check_runner_quiet", "_own_ancestry", "_cmdline",
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
    # Token checks (R2 C3-10): write_token + check_token in one
    # driver process, TOKEN_PATH pointed at a temp file via
    # extra (the TOKEN_PATH Assign node is NOT extracted, so the
    # override survives). "token" writes a fresh token then
    # checks it (must pass). "token-stale" writes a 5h-old token
    # file then checks it (must refuse). "token-missing" checks
    # with no file at all (must refuse).
    "token": (("write_token", "check_token", "_fail"),
               ("TOKEN_TTL_S",)),
    "token-stale": (("check_token", "_fail"), ("TOKEN_TTL_S",)),
    "token-missing": (("check_token", "_fail"), ("TOKEN_TTL_S",)),
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
    extra = {"_SHIP_DIR": ship_dir, "SHIP_DIR": ship_dir}
    if check in ("token", "token-stale", "token-missing"):
        # Temp token path under the ship dir's parent (never the
        # real /tmp/worker-y13-handover.json: this driver must
        # not touch a live token).
        import json as _json
        import time as _time
        token_path = os.path.join(
            os.path.dirname(os.path.abspath(ship_dir)),
            "driver-token.json")
        extra["TOKEN_PATH"] = token_path
        if check == "token-stale":
            with open(token_path, "w") as f:
                _json.dump({"asserted_at_unix": _time.time() - 5 * 3600,
                            "basis": "stale test token"}, f)
        elif check == "token-missing":
            if os.path.exists(token_path):
                os.unlink(token_path)
    ns = extract_lib.extract_funcs(
        LAUNCHER, funcs, consts, extra=extra)
    try:
        if check in ("manifest", "marker"):
            ns["check_" + check](repo)
        elif check == "remote":
            ns["_check_remote"](repo)
        elif check == "runner-quiet":
            ns["check_runner_quiet"]()
        elif check == "entry-pyc":
            ns["_check_entry_pyc"]()
        elif check == "scan":
            ns["_scan_ship"]()
        elif check == "token":
            ns["write_token"]()
            ns["check_token"]()
        elif check in ("token-stale", "token-missing"):
            ns["check_token"]()
    except SystemExit as exc:
        print(f"DRIVER-REFUSED rc={exc.code}", file=sys.stderr)
        return 2 if exc.code in (2, None) else int(exc.code or 2)
    print(f"DRIVER-OK check={check} ship={ship_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
