#!/usr/bin/env python3
"""Thin runner over the vendored cli-anything harnesses. Stdlib only.

The allowlist is the vendored registry snapshot at
skill/cli-anything/registry.json (repo-owned once vendored, NOT live
upstream data): an app runs only if it is listed there AND its harness
binary resolves on PATH. This script is not a generic shell: it takes
argv only, never parses shell syntax, never uses shell=True, and never
pipes agent text into a shell string.

Subcommands:
  list                 One JSON object per line: name/entry/skill/requires.
  info <app>           One JSON object: vendored skill path + install command.
  run <app> -- <args>  Run the app's harness with --json forced when the
                       harness supports it. Prints exactly one bounded JSON
                       envelope: app, args, returncode, stdout_truncated,
                       stderr_truncated. Timeout is 60 s.

A bare invocation with no subcommand is refused (exit 2). REPL mode is
forbidden for agents: `run` with no args after `--` is refused, because
a bare harness invocation drops into an interactive REPL.

Registry layout (vendored snapshot): a JSON object with a "clis" list.
Each entry has name, entry_point (harness binary on PATH), install_cmd,
requires (free-text string) and skill_md (upstream skill path). A plain
dict of name -> entry is also accepted, for forward compatibility.

Environment (tests only): CLI_ANYTHING_REGISTRY overrides the snapshot
path. Nothing else is configurable.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TIMEOUT_SECONDS = 60
JSON_PROBE_TIMEOUT_SECONDS = 10
MAX_OUTPUT_CHARS = 4096
TRUNCATION_MARKER = "\n...[truncated]"

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "skill" / "cli-anything" / "registry.json"
SKILL_DIR = ROOT / "skill" / "cli-anything"

USAGE = (
    "usage: cli-anything.py list\n"
    "       cli-anything.py info <app>\n"
    "       cli-anything.py run <app> -- <args...>\n"
)


def registry_path():
    """Snapshot path, overridable only via CLI_ANYTHING_REGISTRY (tests)."""
    override = os.environ.get("CLI_ANYTHING_REGISTRY")
    return Path(override) if override else DEFAULT_REGISTRY


def load_registry(path):
    """Return {name: entry} from the vendored snapshot at path."""
    try:
        data = json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise RuntimeError("registry snapshot not found: %s" % path)
    except json.JSONDecodeError as exc:
        raise RuntimeError("registry snapshot is not valid JSON: %s" % exc)
    if isinstance(data, dict) and isinstance(data.get("clis"), list):
        entries = data["clis"]
    elif isinstance(data, dict) and data and all(
            isinstance(value, dict) for value in data.values()):
        entries = data.values()
    else:
        raise RuntimeError("registry snapshot has an unexpected shape: %s" % path)
    registry = {}
    for entry in entries:
        name = entry.get("name")
        if not name or not isinstance(entry, dict):
            raise RuntimeError("registry entry without a name: %r" % (entry,))
        for key in ("entry_point", "install_cmd", "requires", "skill_md"):
            if key not in entry:
                raise RuntimeError(
                    "registry entry %r is missing %r" % (name, key))
        registry[name] = entry
    return registry


def skill_path(app):
    """Vendored skill path for app (whether or not the file exists yet)."""
    return SKILL_DIR / ("%s.md" % app)


def truncate(text):
    """Bound text to MAX_OUTPUT_CHARS, marking the cut."""
    if len(text) > MAX_OUTPUT_CHARS:
        return text[:MAX_OUTPUT_CHARS] + TRUNCATION_MARKER
    return text


def print_envelope(envelope):
    """Print exactly one JSON object on stdout."""
    print(json.dumps(envelope), flush=True)


def cmd_list(registry):
    """One JSON object per line: name/entry/skill/requires."""
    for name in sorted(registry):
        entry = registry[name]
        print_envelope({
            "name": name,
            "entry": entry["entry_point"],
            "skill": entry["skill_md"],
            "requires": entry["requires"],
        })
    return 0


def cmd_info(registry, app):
    """Print the vendored skill path and install command for app."""
    entry = registry.get(app)
    if entry is None:
        print("unknown app: %s" % app, file=sys.stderr)
        return 2
    print_envelope({
        "app": app,
        "skill_path": str(skill_path(app)),
        "install": entry["install_cmd"],
    })
    return 0


def supports_json(binary):
    """True if `<binary> --help` advertises a --json flag. Never fatal."""
    try:
        result = subprocess.run(
            [binary, "--help"], capture_output=True, text=True,
            timeout=JSON_PROBE_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return "--json" in result.stdout


def cmd_run(registry, app, args):
    """Run the allowlisted harness with argv only; one JSON envelope out."""
    envelope = {"app": app, "args": list(args), "returncode": None,
                "stdout_truncated": "", "stderr_truncated": ""}
    entry = registry.get(app)
    if entry is None:
        envelope["error"] = "app not in vendored registry: %s" % app
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 2
    if not args:
        envelope["error"] = (
            "refusing bare harness invocation (REPL mode is forbidden)")
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 2
    binary = entry["entry_point"]
    if shutil.which(binary) is None:
        envelope["error"] = "harness binary not on PATH: %s" % binary
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 2
    argv = [binary]
    if "--json" not in args and supports_json(binary):
        argv.append("--json")
    argv.extend(args)
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        envelope["timeout"] = True
        envelope["error"] = "timed out after %ds" % TIMEOUT_SECONDS
        envelope["stdout_truncated"] = truncate(exc.stdout or "")
        envelope["stderr_truncated"] = truncate(exc.stderr or "")
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 124
    except OSError as exc:
        envelope["error"] = "failed to run %s: %s" % (binary, exc)
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 1
    envelope["returncode"] = result.returncode
    envelope["stdout_truncated"] = truncate(result.stdout)
    envelope["stderr_truncated"] = truncate(result.stderr)
    print_envelope(envelope)
    return 0 if result.returncode == 0 else 1


def main(argv):
    """Dispatch list/info/run. No subcommand (or a bad one) is refused."""
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    if argv == ["--help"] or argv == ["-h"]:
        print(USAGE, end="")
        return 0
    try:
        registry = load_registry(registry_path())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if argv[0] == "list" and len(argv) == 1:
        return cmd_list(registry)
    if argv[0] == "info" and len(argv) == 2:
        return cmd_info(registry, argv[1])
    if argv[0] == "run" and len(argv) >= 3 and argv[2] == "--":
        return cmd_run(registry, argv[1], argv[3:])
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
