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

Credit: the harnesses this runner invokes are CLI-Anything by HKUDS (Data Intelligence Lab, University of Hong Kong, led by Prof. Chao Huang), https://github.com/HKUDS/CLI-Anything, Apache License 2.0, vendored
from upstream HEAD 34f5195 on 2026-11-18 and used with the owner's
permission (granted 2026-11-19). This runner itself is repo-owned;
only the harness binaries and skill docs are upstream work.

Registry layout (vendored snapshot): a JSON object with a "clis" list.
Each entry has name, entry_point (harness binary on PATH), install_cmd,
requires (free-text string) and skill_md (upstream skill path). A plain
dict of name -> entry is also accepted, for forward compatibility.

Environment (tests only): CLI_ANYTHING_REGISTRY overrides the snapshot
path. Nothing else is configurable.

Repo-owned extension: `run obsidian -- vault move <source> <destination>`
moves a note inside the vault through the Obsidian Local REST API
(HTTP MOVE on /vault/<path> with a Destination header). Upstream
cli-anything-obsidian 1.1.1 has no move/rename command, so without this
the briefed command fails with "No such command 'move'". The move is
the one vault operation that needs the API: the plugin's move calls
app.fileManager.renameFile, the link-updating rename, while a plain
shell mv leaves backlinks pointing at the old path (proven 19/11, see
improvements/summary-vault-move-proof.md). Auth is the same as the
upstream harness: OBSIDIAN_API_KEY in the environment, never on the
command line. Base URL defaults to https://127.0.0.1:27124 (the plugin's
default port on loopback) and can be overridden with OBSIDIAN_API_URL.
The plugin serves a self-signed certificate, so TLS verification is
off for this loopback call, same as the upstream harness (verify=False).
"""

import json
import os
import shutil
import ssl
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TIMEOUT_SECONDS = 60
JSON_PROBE_TIMEOUT_SECONDS = 10
MAX_OUTPUT_CHARS = 4096
TRUNCATION_MARKER = "\n...[truncated]"
MAX_RETAINED_BYTES = 1_048_576

# Repo-owned Obsidian extension: `vault move` (see obsidian_vault_move).
# Upstream cli-anything-obsidian 1.1.1 has no move/rename command, so the
# harness cannot move a note. The move goes straight to the same Local
# REST API the harness wraps, with the same auth and the same server.
# Timeout matches the upstream per-call default (30 s).
OBSIDIAN_API_URL_DEFAULT = "https://127.0.0.1:27124"
OBSIDIAN_MOVE_TIMEOUT_SECONDS = 30

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "skill" / "cli-anything" / "registry.json"
SKILL_DIR = ROOT / "skill" / "cli-anything"

USAGE = (
    "usage: cli-anything.py list\n"
    "       cli-anything.py info <app>\n"
    "       cli-anything.py run <app> -- <args...>\n"
    "       cli-anything.py run obsidian -- vault move <source> <destination>\n"
    "           (repo-owned extension; upstream has no move command)\n"
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


def to_text(value):
    """Decode bytes (or None) to str safely; str passes through."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def truncate(text):
    """Bound text to MAX_OUTPUT_CHARS, marker included in the limit."""
    text = to_text(text)
    if len(text) > MAX_OUTPUT_CHARS:
        cut = MAX_OUTPUT_CHARS - len(TRUNCATION_MARKER)
        return text[:cut] + TRUNCATION_MARKER
    return text


def _drain_capped(stream, cap):
    """Read stream to EOF, keeping only the first cap bytes.

    Excess is drained and discarded, so the child never blocks on a
    full pipe while this side keeps only a bounded amount in RAM.
    """
    chunks = []
    kept = 0
    while True:
        data = stream.read(65536)
        if not data:
            break
        if kept < cap:
            take = data[:cap - kept]
            chunks.append(take)
            kept += len(take)
    return b"".join(chunks)


def run_bounded(argv, timeout):
    """Run argv; return (returncode, stdout_text, stderr_text, timed_out).

    Retained output per stream is capped at MAX_RETAINED_BYTES (drained
    and discarded beyond that), so a flooding harness cannot exhaust
    RAM. Text is decoded with errors="replace", so a timeout never
    leaves bytes in the envelope (QC-1, QC-2).
    """
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    results = {}

    def _reader(stream, key):
        results[key] = _drain_capped(stream, MAX_RETAINED_BYTES)

    t_out = threading.Thread(target=_reader, args=(proc.stdout, "out"),
                             daemon=True)
    t_err = threading.Thread(target=_reader, args=(proc.stderr, "err"),
                             daemon=True)
    t_out.start()
    t_err.start()
    try:
        returncode = proc.wait(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        proc.kill()
        returncode = None
        timed_out = True
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    t_out.join(timeout=5)
    t_err.join(timeout=5)
    stdout = to_text(results.get("out", b""))
    stderr = to_text(results.get("err", b""))
    return returncode, stdout, stderr, timed_out


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
    """Print the vendored skill path and install command for app.

    install is the safe PyPI command (pip install <entry_point>); the
    registry's install_cmd is an unpinned git URL and is returned only
    as install_upstream, never as the command to run (QC-3).
    """
    entry = registry.get(app)
    if entry is None:
        print("unknown app: %s" % app, file=sys.stderr)
        return 2
    if entry.get("repo_owned"):
        install = "ships in this repo: %s" % entry["entry_point"]
    else:
        install = "pip install %s" % entry["entry_point"]
    print_envelope({
        "app": app,
        "skill_path": str(skill_path(app)),
        "install": install,
        "install_upstream": entry["install_cmd"],
    })
    return 0


def supports_json(binary):
    """True if `<binary> --help` advertises a --json flag. Never fatal."""
    try:
        _, stdout, _, timed_out = run_bounded(
            [binary, "--help"], JSON_PROBE_TIMEOUT_SECONDS)
    except OSError:
        return False
    if timed_out:
        return False
    return "--json" in stdout


def obsidian_api_url():
    """Local REST API base URL (tests override it with OBSIDIAN_API_URL)."""
    return os.environ.get("OBSIDIAN_API_URL") or OBSIDIAN_API_URL_DEFAULT


def obsidian_vault_move(source, destination):
    """Move a note via the Obsidian Local REST API; return a result dict.

    Issues exactly the call the installed plugin exposes: HTTP MOVE on
    /vault/<url-encoded source path> with the destination in a
    Destination header and Bearer auth. The plugin answers 204 with an
    empty body on success and performs the move through
    app.fileManager.renameFile, so Obsidian updates backlinks. Raises
    RuntimeError with the upstream-style message on any failure.
    """
    api_key = os.environ.get("OBSIDIAN_API_KEY") or ""
    if not api_key:
        raise RuntimeError(
            "API key required. Set OBSIDIAN_API_KEY env var.")
    base_url = obsidian_api_url().rstrip("/")
    encoded = "/".join(urllib.parse.quote(part, safe="")
                       for part in source.split("/"))
    url = "%s/vault/%s" % (base_url, encoded)
    request = urllib.request.Request(
        url, method="MOVE",
        headers={"Authorization": "Bearer %s" % api_key,
                 "Destination": destination})
    context = None
    if url.lower().startswith("https://"):
        context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(
                request, timeout=OBSIDIAN_MOVE_TIMEOUT_SECONDS,
                context=context) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except OSError:
            body = ""
        raise RuntimeError(
            "Obsidian API error %s on MOVE /vault/%s: %s"
            % (exc.code, encoded, body[:512])) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Cannot connect to Obsidian REST API at %s. "
            "Is Obsidian running with the Local REST API plugin enabled?"
            % base_url) from exc
    except TimeoutError as exc:
        raise RuntimeError(
            "Request to Obsidian timed out: MOVE /vault/%s"
            % encoded) from exc
    return {"source": source, "destination": destination,
            "status": status, "method": "MOVE",
            "note": "rename via Local REST API MOVE "
                    "(app.fileManager.renameFile); Obsidian updates "
                    "backlinks"}


def cmd_run_obsidian_move(envelope, args):
    """Run the repo-owned `vault move`; one JSON envelope out, like cmd_run."""
    rest = args[2:]
    if len(rest) != 2 or not rest[0] or not rest[1]:
        envelope["error"] = (
            "usage: vault move <source> <destination> "
            "(vault-relative paths)")
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 2
    source, destination = rest
    if source == destination:
        envelope["error"] = (
            "vault move: source and destination are the same: %s"
            % source)
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 2
    try:
        result = obsidian_vault_move(source, destination)
    except RuntimeError as exc:
        envelope["error"] = str(exc)
        envelope["returncode"] = 1
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 1
    envelope["returncode"] = 0
    envelope["result"] = result
    envelope["stdout_truncated"] = truncate(json.dumps(result))
    print_envelope(envelope)
    return 0


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
    if app == "obsidian" and len(args) >= 2 and args[0] == "vault" \
            and args[1] == "move":
        # Repo-owned extension: the upstream harness has no move command,
        # so this never reaches the binary. Same envelope shape as cmd_run.
        return cmd_run_obsidian_move(envelope, args)
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
        returncode, stdout, stderr, timed_out = run_bounded(
            argv, TIMEOUT_SECONDS)
    except OSError as exc:
        envelope["error"] = "failed to run %s: %s" % (binary, exc)
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 1
    if timed_out:
        envelope["timeout"] = True
        envelope["error"] = "timed out after %ds" % TIMEOUT_SECONDS
        envelope["stdout_truncated"] = truncate(stdout)
        envelope["stderr_truncated"] = truncate(stderr)
        print_envelope(envelope)
        print(envelope["error"], file=sys.stderr)
        return 124
    envelope["returncode"] = returncode
    envelope["stdout_truncated"] = truncate(stdout)
    envelope["stderr_truncated"] = truncate(stderr)
    print_envelope(envelope)
    return 0 if returncode == 0 else 1


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
