#!/usr/bin/env python3
"""CB-9 bench manifest for a checkout-run bench (FINAL direction, section 4).

The 18f2304 mechanism (scripts/sync-installed.py, _write_deploy_manifest)
writes deploy-manifest.json into a SYNCED installed tree, keyed to a
release ledger. It does not cover this bench shape: the fixture 2-vision
bench runs from a repo CHECKOUT, not from an installed tree, so there is
no installed tree, no ledger, and no releases/ dir to key a manifest to.
This script is the minimal extension for that shape. It reuses the sync
mechanism's own digest functions (_source_bundle, _digest_entries,
_sha256) so the source_content_sha256 here means exactly what it means
in a sync manifest, and it writes the same top level keys
(installer, format, source_commit, source_content_sha256, installed_root)
plus a bench section.

Definition of "installed" for a checkout-run bench: the checkout under
test IS the installed tree. The bench executes exactly these artifacts,
and only these, so the manifest hashes exactly these:

- tests/two_vision_bench.py (the executed script, repo relative path)
- tests/two_vision_fixture.html (the fixture the script reads; the
  script hardcodes the main-checkout fixture path, so the manifest
  records that path too and requires it byte-identical to the checkout
  copy, else verification fails)
- the Firefox launcher and firefox-bin it starts, and geckodriver
- the Python interpreter and selenium version that run the script

The bench imports NO repo script (no cu.py, no first_action.py, no
session driver), so no repo script belongs in the artifact list. The
whole-tree source_content_sha256 still pins the full checkout, so a
bench quote cannot silently drift to a different tree.

The log of the same build is recorded by PATH, not by hash: the log is
written after the manifest (it quotes the manifest), so hashing it here
would be circular. Verification requires the log file to exist and to
name the same run_id and source commit.

Usage:
  bench_manifest.py write --repo <checkout> --results <results.json>
      --log <log path in repo, relative> --out <manifest path>
  bench_manifest.py verify --manifest <path> --repo <checkout>
      [--results <results.json>]
"""

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

BENCH_SCRIPT = "tests/two_vision_bench.py"
FIXTURE = "tests/two_vision_fixture.html"
FIXTURE_MAIN_PATH = str(
    Path.home() / "workspace/computer-use-wayland/tests/two_vision_fixture.html"
)
FIREFOX = str(Path.home() / "workspace/tools/firefox/firefox")
FIREFOX_BIN = str(Path.home() / "workspace/tools/firefox/firefox-bin")
GECKODRIVER = str(Path.home() / "workspace/tools/geckodriver")
INSTALLER = "computer-use-wayland/scripts/bench_manifest.py"
FORMAT = 1


class ManifestError(RuntimeError):
    pass


def _load_sync_module(repo):
    path = Path(repo) / "scripts" / "sync-installed.py"
    if not path.is_file():
        raise ManifestError(f"sync-installed.py missing: {path}")
    spec = importlib.util.spec_from_file_location(
        "_bench_sync_installed", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo, *args):
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args], text=True,
            stderr=subprocess.PIPE).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ManifestError(f"git {' '.join(args)} failed") from exc


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob(repo, rel):
    return _git(repo, "hash-object", rel)


def _clean_status(repo, ignore_paths=()):
    """git status porcelain minus pycache and minus listed record files.

    The manifest's own log is a record file, not source: it is expected
    to sit untracked next to the manifest at verify time, so it must
    not count as tree dirt."""
    raw = _git(repo, "status", "--porcelain")
    ignored = {p.strip("/") for p in ignore_paths}
    kept = []
    for line in raw.splitlines():
        if "__pycache__" in line or line.endswith(".pyc"):
            continue
        path = line[3:].strip().rstrip("/")
        if any(path == base or path.startswith(base + "/")
               or base.startswith(path + "/") for base in ignored):
            continue
        kept.append(line)
    return "\n".join(kept)


def _version(binary, *args):
    try:
        out = subprocess.check_output(
            [binary, *args], text=True, stderr=subprocess.STDOUT,
            timeout=30).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return out.splitlines()[0] if out else None


def _file_artifact(repo, rel):
    path = Path(repo) / rel
    if not path.is_file() or path.is_symlink():
        raise ManifestError(f"bench artifact missing or unsafe: {path}")
    return {
        "path": rel,
        "sha256": _sha256(path),
        "git_blob": _git_blob(repo, rel),
        "size": path.stat().st_size,
    }


def build_manifest(repo, results_path, log_rel,
                   python_version=None, selenium_version=None,
                   fixture_main_path=None):
    repo = Path(repo).resolve()
    sync = _load_sync_module(repo)
    results_path = Path(results_path).resolve()
    if not results_path.is_file():
        raise ManifestError(f"bench results missing: {results_path}")
    with results_path.open(encoding="utf-8") as handle:
        results = json.load(handle)
    for key in ("run_id", "outcome", "wall_s", "visions_used"):
        if key not in results:
            raise ManifestError(f"results.json lacks {key}: {results_path}")
    if results["outcome"] != "PASS":
        raise ManifestError(
            f"refusing to lock a manifest for a non-PASS bench: "
            f"outcome={results['outcome']!r} run_id={results['run_id']!r}")

    bench = _file_artifact(repo, BENCH_SCRIPT)
    fixture = _file_artifact(repo, FIXTURE)
    if fixture_main_path is None:
        fixture_main_path = FIXTURE_MAIN_PATH
    main_fixture = Path(fixture_main_path)
    if not main_fixture.is_file():
        raise ManifestError(f"hardcoded fixture path missing: {main_fixture}")
    main_sha = _sha256(main_fixture)
    if main_sha != fixture["sha256"]:
        raise ManifestError(
            "hardcoded fixture path differs from the checkout copy: "
            f"main={main_sha} checkout={fixture['sha256']}; the bench "
            "did not run against this checkout")
    fixture["hardcoded_path"] = str(main_fixture)
    fixture["hardcoded_path_sha256"] = main_sha

    firefox = {"path": FIREFOX, "sha256": _sha256(FIREFOX),
               "size": Path(FIREFOX).stat().st_size,
               "version": _version(FIREFOX, "--version")}
    firefox_bin = {"path": FIREFOX_BIN, "sha256": _sha256(FIREFOX_BIN),
                   "size": Path(FIREFOX_BIN).stat().st_size}
    geckodriver = {"path": GECKODRIVER, "sha256": _sha256(GECKODRIVER),
                   "size": Path(GECKODRIVER).stat().st_size,
                   "version": _version(GECKODRIVER, "--version")}

    # The bench runs under the probe venv python, not necessarily the
    # interpreter running this script (system python3 has no selenium),
    # so both versions are passed in; fall back to this interpreter.
    if python_version is None:
        python_version = sys.version.split()[0]
    if selenium_version is None:
        try:
            import selenium
            selenium_version = selenium.__version__
        except ImportError as exc:
            raise ManifestError(
                "selenium version unknown: pass --selenium-version "
                "(this interpreter has no selenium)") from exc
    # __pycache__ is a side effect of running the tooling itself and is
    # excluded from the source bundle, so it does not dirty the tree.
    status = _clean_status(repo)
    manifest = {
        "installer": INSTALLER,
        "format": FORMAT,
        "bench_shape": "checkout-run",
        "mechanism_note": (
            "18f2304 _write_deploy_manifest covers synced installed "
            "trees only; this bench runs from a checkout, so the "
            "checkout under test is the installed tree. Same digest "
            "functions as sync-installed.py."),
        "source_commit": _git(repo, "rev-parse", "HEAD"),
        "source_content_sha256": sync._digest_entries(
            sync._source_bundle(repo)),
        "git_status_clean": status == "",
        "git_status": status,
        "installed_root": str(repo),
        "log": log_rel,
        "bench": {
            "run_id": results["run_id"],
            "mode": results.get("mode"),
            "live": results.get("live"),
            "outcome": results["outcome"],
            "wall_s": results["wall_s"],
            "visions_used": results["visions_used"],
            "steps": results.get("steps"),
            "results_path": str(results_path),
        },
        "artifacts": {
            "bench_script": bench,
            "fixture": fixture,
            "firefox": firefox,
            "firefox_bin": firefox_bin,
            "geckodriver": geckodriver,
            "python": python_version,
            "selenium": selenium_version,
        },
    }
    if not manifest["git_status_clean"]:
        raise ManifestError(
            "checkout under test is dirty, refusing to lock: "
            f"git status: {status!r}")
    return manifest


def write_manifest(repo, results_path, log_rel, out_path,
                   python_version=None, selenium_version=None,
                   fixture_main_path=None):
    manifest = build_manifest(repo, results_path, log_rel,
                              python_version, selenium_version,
                              fixture_main_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_name(out_path.name + ".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    tmp.replace(out_path)
    return manifest, out_path


def verify_manifest(manifest_path, repo, results_path=None, log_root=None):
    manifest_path = Path(manifest_path)
    if not manifest_path.is_file():
        raise ManifestError(f"manifest missing: {manifest_path}")
    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    repo = Path(repo).resolve()
    log_root = Path(log_root).resolve() if log_root else repo
    sync = _load_sync_module(repo)
    checks = []
    commit = _git(repo, "rev-parse", "HEAD")
    checks.append(("source_commit", manifest.get("source_commit") == commit,
                   f"manifest={manifest.get('source_commit')} repo={commit}"))
    digest = sync._digest_entries(sync._source_bundle(repo))
    checks.append(("source_content_sha256",
                   manifest.get("source_content_sha256") == digest,
                   f"manifest={manifest.get('source_content_sha256')} "
                   f"repo={digest}"))
    status = _clean_status(repo, ignore_paths=(manifest.get("log", ""),))
    checks.append(("git_status_clean", status == "",
                   f"status={status!r}"))
    for role, rel in (("bench_script", BENCH_SCRIPT),
                      ("fixture", FIXTURE)):
        artifact = manifest.get("artifacts", {}).get(role, {})
        path = repo / rel
        ok = (path.is_file() and _sha256(path) == artifact.get("sha256")
              and _git_blob(repo, rel) == artifact.get("git_blob"))
        checks.append((f"artifact:{role}", ok,
                       f"sha256={artifact.get('sha256')} blob="
                       f"{artifact.get('git_blob')}"))
    fixture = manifest.get("artifacts", {}).get("fixture", {})
    main = Path(fixture.get("hardcoded_path", FIXTURE_MAIN_PATH))
    ok = main.is_file() and _sha256(main) == fixture.get("sha256")
    checks.append(("fixture:hardcoded_path", ok,
                   f"path={main} sha256={fixture.get('sha256')}"))
    for role, key in (("firefox", "firefox"), ("firefox_bin", "firefox_bin"),
                      ("geckodriver", "geckodriver")):
        artifact = manifest.get("artifacts", {}).get(key, {})
        path = Path(artifact.get("path", ""))
        ok = path.is_file() and _sha256(path) == artifact.get("sha256")
        checks.append((f"artifact:{role}", ok,
                       f"path={path} sha256={artifact.get('sha256')}"))
    log_path = Path(log_root) / manifest.get("log", "")
    log_ok = log_path.is_file()
    log_text = log_path.read_text(encoding="utf-8") if log_ok else ""
    run_id = manifest.get("bench", {}).get("run_id", "")
    checks.append(("log:exists_and_names_run",
                   log_ok and run_id in log_text
                   and manifest.get("source_commit", "")[:7] in log_text,
                   f"log={log_path} run_id={run_id}"))
    if results_path is not None:
        with Path(results_path).open(encoding="utf-8") as handle:
            results = json.load(handle)
        checks.append(("results:run_id_outcome",
                       results.get("run_id") == run_id
                       and results.get("outcome")
                       == manifest.get("bench", {}).get("outcome"),
                       f"run_id={results.get('run_id')} outcome="
                       f"{results.get('outcome')}"))
    failed = [name for name, ok, _ in checks if not ok]
    return checks, failed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    write = sub.add_parser("write", help="write a bench manifest")
    write.add_argument("--repo", required=True)
    write.add_argument("--results", required=True)
    write.add_argument("--log", required=True,
                       help="log path in repo, relative (must exist at "
                       "verify time, not at write time)")
    write.add_argument("--out", required=True)
    write.add_argument("--python-version",
                       help="python that ran the bench (default: this "
                       "interpreter)")
    write.add_argument("--selenium-version",
                       help="selenium that ran the bench (default: "
                       "imported from this interpreter)")
    verify = sub.add_parser("verify", help="verify a bench manifest")
    verify.add_argument("--manifest", required=True)
    verify.add_argument("--repo", required=True)
    verify.add_argument("--results")
    verify.add_argument("--log-root",
                        help="checkout holding the log file (default: "
                        "--repo); the log is committed with the manifest, "
                        "not in the worktree under test")
    args = parser.parse_args(argv)
    try:
        if args.command == "write":
            manifest, path = write_manifest(
                args.repo, args.results, args.log, args.out,
                args.python_version, args.selenium_version)
            print(f"manifest written: {path}")
            print(f"source_commit: {manifest['source_commit']}")
            print(f"run_id: {manifest['bench']['run_id']} "
                  f"outcome={manifest['bench']['outcome']} "
                  f"wall_s={manifest['bench']['wall_s']}")
            return 0
        checks, failed = verify_manifest(
            args.manifest, args.repo, args.results, args.log_root)
        for name, ok, detail in checks:
            print(f"{'ok' if ok else 'FAIL'} {name}: {detail}")
        if failed:
            print(f"verify FAILED: {', '.join(failed)}", file=sys.stderr)
            return 1
        print("verify OK: manifest matches the checkout under test")
        return 0
    except ManifestError as exc:
        print(f"bench_manifest: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
