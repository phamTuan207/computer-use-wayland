#!/usr/bin/env python3
"""Y6C5 tests: Y6r A2/A3/A5/A6/A7/A8/A10 fixes for todolist 2.2.3 (I11) + 4.13.

Stdlib only. Run: python3 tests/test_y6c5_positive_gate.py
No nest is launched, no plugin is loaded, no live session is touched.
The A2 gate block and the G4 block are extracted from the runner and executed
under bash with stubbed fail()/nest() and fake logs, so the gate logic itself
is proven, not just its text.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "improvements" / "worker-y6b-run-nested-wayland-v2.sh"
LOAD_TEST = ROOT / "improvements" / "worker-y6e-nested-load-test.sh"
HOOK = ROOT / "improvements" / "y6-nested-conf" / "nested-visuals-hook.lua"
OPTICS = ROOT / "improvements" / "y6-nested-conf" / "optics.lua"
LOG = ROOT / "improvements" / "worker-click5-y6-paper-log.md"

FAILURES = []


def check(name, fn):
    try:
        fn()
    except AssertionError as exc:
        FAILURES.append(name)
        print("FAIL: " + name + ": " + str(exc))
    except Exception as exc:  # noqa: BLE001 - report harness errors as failures
        FAILURES.append(name)
        print("FAIL: " + name + " (harness error): " + repr(exc))
    else:
        print("PASS: " + name)


def runner_text():
    return RUNNER.read_text()


def extract_block(text, begin, end):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if begin in line)
    stop = next(i for i, line in enumerate(lines) if end in line)
    assert start < stop, "block markers out of order: " + begin
    return "\n".join(lines[start + 1:stop]) + "\n"


def test_a2_gate_present():
    text = runner_text()
    assert "# BEGIN Y6C5-A2 positive profile gate" in text, "A2 BEGIN marker missing"
    assert "# END Y6C5-A2 positive profile gate" in text, "A2 END marker missing"
    block = extract_block(text, "BEGIN Y6C5-A2", "END Y6C5-A2")
    assert "Y6-NEST-OPTICS: applied" in block, "gate does not poll the optics marker"
    assert "features.layers.enabled" in block, "gate lacks the layers.enabled signal"
    assert "Y6C5_GATE_TIMEOUT_S" in block, "gate timeout not overridable for tests"
    assert "nest-plugin-list-after-gate.json" in block, "gate lacks plugin-list re-check"
    assert "nest-glass-status-after-gate.json" in block, "gate lacks status re-check"
    assert "parse-1 not-ready marker present (expected, not a failure)" in block, (
        "gate does not log the parse-1 marker as expected")
    assert "hook ran before plugin load (profile not applied)" not in text, (
        "old U6 false-fail string still in runner")
    assert "hook marker absent, profile applied" not in text, (
        "old U6 false positive echo still in runner")


def _status_json(layers_enabled):
    return {
        "schema": 1,
        "version": "1.1.1-cu.1",
        "versionCheck": "match",
        "active": True,
        "shaders": "pending",
        "itemProtocol": True,
        "features": {
            "layers": {"enabled": layers_enabled, "active": True, "reason": None},
            "windows": {"enabled": False, "active": False, "reason": None},
            "subsurfaces": {"enabled": False, "active": False, "reason": None},
        },
    }


def _plugin_json():
    return [{"name": "hyprglass", "version": "1.1.1-cu.1"}]


def run_gate_case(log_content, nest_log_content, layers_enabled, timeout_s="2"):
    """Execute the extracted A2 block under bash with stubs. Returns exit code."""
    block = extract_block(runner_text(), "BEGIN Y6C5-A2", "END Y6C5-A2")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        nest_dir = tmp / "nest"
        nest_dir.mkdir()
        log_file = tmp / "stdout.log"
        nest_log = tmp / "hyprland.log"
        log_file.write_text(log_content)
        nest_log.write_text(nest_log_content)
        (nest_dir / "nest-glass-status.json").write_text(
            json.dumps(_status_json(layers_enabled)))
        stub_plugin = tmp / "plugin.json"
        stub_plugin.write_text(json.dumps(_plugin_json()))
        stub_status = tmp / "status.json"
        stub_status.write_text(json.dumps(_status_json(True)))
        prelude = (
            'fail() { echo "STUB-FAIL: $1" >&2; exit 1; }\n'
            'nest() {\n'
            '  case "$*" in\n'
            '    *"plugin list"*) cat "$STUB_PLUGIN_JSON";;\n'
            '    *"hyprglass status"*) cat "$STUB_STATUS_JSON";;\n'
            '    *"configerrors"*) printf "";;\n'
            '    *) echo "stub nest: unknown args: $*" >&2; return 1;;\n'
            '  esac\n'
            '}\n'
            'LOG="' + str(log_file) + '"\n'
            'NEST_LOG="' + str(nest_log) + '"\n'
            'NEST="' + str(nest_dir) + '"\n'
            'STUB_PLUGIN_JSON="' + str(stub_plugin) + '"\n'
            'STUB_STATUS_JSON="' + str(stub_status) + '"\n'
            'export Y6C5_GATE_TIMEOUT_S="' + timeout_s + '" Y6C5_GATE_INTERVAL_S="0.2"\n'
        )
        script = tmp / "gate-case.sh"
        script.write_text(prelude + block)
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        return proc.returncode, proc.stdout + proc.stderr


OPTICS_MARKER = ("Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 "
                 "mask=contour namespace=computer-use-indicator")
HOOK_APPLIED = "Y6-NEST-HOOK: profile applied"
NOT_READY = "Y6-NEST-HOOK: hyprglass not ready (count=0 version=nil)"


def test_a2_gate_exec_healthy_stdout_log():
    rc, out = run_gate_case(
        "\n".join([NOT_READY, OPTICS_MARKER, HOOK_APPLIED]) + "\n", "", True)
    assert rc == 0, "healthy gate (markers in stdout log) must pass, got rc=" + str(rc) + " out=" + out
    assert "profile gate OK" in out, "healthy gate must print profile gate OK"


def test_a2_gate_exec_healthy_nest_log():
    rc, out = run_gate_case(
        "", "\n".join([NOT_READY, OPTICS_MARKER, HOOK_APPLIED]) + "\n", True)
    assert rc == 0, "healthy gate (markers in nest log) must pass, got rc=" + str(rc) + " out=" + out


def test_a2_gate_exec_no_marker_fails():
    rc, out = run_gate_case(NOT_READY + "\n", "", True)
    assert rc != 0, "gate with no applied marker must fail"
    assert "applied marker absent" in out, "gate must report the absent marker, out=" + out


def test_a2_gate_exec_layers_false_fails():
    rc, out = run_gate_case(
        "\n".join([NOT_READY, OPTICS_MARKER, HOOK_APPLIED]) + "\n", "", False)
    assert rc != 0, "gate with layers.enabled false must fail"
    assert "layers.enabled is not true" in out, "gate must report layers.enabled, out=" + out


def test_a2_gate_exec_parse1_expected():
    # Parse-1 marker present AND optics marker present: must pass, and the
    # run must log the parse-1 marker as expected, not as a failure.
    rc, out = run_gate_case(
        "\n".join([NOT_READY, OPTICS_MARKER]) + "\n", "", True)
    assert rc == 0, "parse-1 marker + optics marker must pass, got rc=" + str(rc)
    assert "expected, not a failure" in out, "gate must log parse-1 as expected"


def run_g4_case(configerrors):
    block = extract_block(runner_text(), "BEGIN Y6C5-A6-G4", "END Y6C5-A6-G4")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        prelude = (
            'fail() { echo "STUB-FAIL: $1" >&2; exit 1; }\n'
            'nest() { printf "%s" "$STUB_CONFIGERRORS"; }\n'
            'STUB_CONFIGERRORS=' + "'" + configerrors.replace("'", "'\\''") + "'\n"
        )
        script = tmp / "g4-case.sh"
        script.write_text(prelude + block)
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        return proc.returncode, proc.stdout + proc.stderr


def test_a6_g4_exec_empty_passes():
    rc, out = run_g4_case("")
    assert rc == 0, "empty configerrors must pass, got rc=" + str(rc) + " out=" + out
    assert "G4 OK" in out, "G4 pass must print G4 OK"


def test_a6_g4_exec_errors_fail():
    rc, out = run_g4_case("config error: optics.lua: bad key")
    assert rc != 0, "non-empty configerrors must fail"
    assert "config errors present" in out, "G4 must report the errors, out=" + out


def test_a3_markers():
    hook = HOOK.read_text()
    optics = OPTICS.read_text()
    assert "Y6-NEST-HOOK: profile applied" in hook, "hook lacks the applied print"
    assert hook.index('dofile("/tmp/y6-nested/conf/optics.lua")') < hook.index(
        'print("Y6-NEST-HOOK: profile applied")'), "hook must print AFTER dofile returns"
    assert "pcall(" not in hook, "hook must not swallow dofile errors with pcall"
    assert "a missing profile is NO-GO" not in hook, "old false liquid-gate comment remains"
    assert "CANNOT prove the profile" in hook, "hook lacks the corrected liquid-gate comment"
    assert OPTICS_MARKER in optics, "optics lacks the applied marker line"
    assert optics.index('hl.plugin.hyprglass.layer(') < optics.index(
        'print("Y6-NEST-OPTICS: applied'), "optics must print AFTER layer() returns"
    assert optics.index('hl.plugin.hyprglass.config(config)') < optics.index(
        'print("Y6-NEST-OPTICS: applied'), "optics must print AFTER config() returns"


def test_a5_present():
    text = runner_text()
    assert "HYPRGLASS_SKIP_VERSION_CHECK" in text, "AMEND4 skip-var check missing"
    assert "AMEND4 OK" in text, "AMEND4 OK echo missing"
    assert "AMEND5-BEFORE OK" in text, "AMEND5 walk missing"
    assert "plugin\\.load\\s*\\(.*?hyprglass" in text or "plugin.load" in text, (
        "AMEND5 walker pattern missing")
    assert "live-plugin-list-before.json" in text, "live plugin BEFORE record missing"
    assert 'cmp -s "$NEST/live-plugin-list-before.json" "$NEST/live-plugin-list-after.json"' in text, (
        "teardown before/after identity comparison missing")


def test_a6_present():
    text = runner_text()
    assert "# BEGIN Y6C5-A6-G4 configerrors gate" in text, "G4 block markers missing"
    assert "nest hyprctl configerrors" in text, "G4 configerrors call missing"
    assert "record_glass_stats" in text, "G6 stats function missing"
    assert "record_glass_stats before-arms" in text, "G6 before-arms call missing"
    assert "record_glass_stats after-arms" in text, "G6 after-arms call missing"
    assert "contourRebuilds" in text, "G6 contourRebuilds reference missing"


def test_a7_no_reload():
    text = runner_text()
    assert "Y6C5-A7 (Y6r R2" in text, "R2 no-reload comment missing"
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert "hyprctl reload" not in line, (
            "non-comment line " + str(i) + " contains hyprctl reload: " + line)


def test_a8_stop_flag():
    text = runner_text()
    assert "Y6_STOP_AFTER_GATES" in text, "A8 stop flag missing"
    cond = 'if [ "${Y6_STOP_AFTER_GATES:-0}" = "1" ]'
    assert cond in text, "A8 stop condition missing"
    stop_at = text.index(cond)
    assert "exit 0" in text[stop_at:stop_at + 500], "stop block must exit 0"
    assert stop_at < text.index("arm A start"), "stop block must sit before the arms"


def test_a10_live_log_only():
    text = runner_text()
    block = extract_block(text, "BEGIN Y6C5-A2", "END Y6C5-A2")
    assert "$NEST_LOG" in block, "A2 gate must grep the live per-instance log"
    for line in block.splitlines():
        if line.strip().startswith("#"):
            continue
        assert "hypr-saved" not in line, (
            "A2 gate code must not read a saved-log directory: " + line)


def test_a4_record_corrected():
    for path in (RUNNER, LOAD_TEST):
        text = path.read_text()
        assert "hook ran before plugin load (profile not applied)" not in text, (
            "old U6 fail string in " + str(path))
        assert "hook marker absent, profile applied" not in text, (
            "old U6 false echo in " + str(path))
    for paper in ("worker-y6e-rebuild-load-log.md",
                  "worker-y6r-council-2-evidence.md",
                  "worker-y6r-council-3-safety.md"):
        text = (ROOT / "improvements" / paper).read_text()
        assert "Errata (Y6C5-A4" in text, "errata block missing in " + paper


def test_a1_staging_documented():
    text = LOG.read_text()
    assert "9ccb27017ab63a9d2bce1d9651425d3b" in text, "staging md5 missing from log"
    assert "0d4ac7a9c2437fb48ecfc505ccd9046b" in text, "rollback md5 missing from log"
    assert "bak-y6c5-20261122" in text, "rollback backup name missing from log"


def test_bash_syntax():
    for path in (RUNNER, LOAD_TEST):
        proc = subprocess.run(["bash", "-n", str(path)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 0, "bash -n failed for " + str(path) + ": " + proc.stderr


def main():
    checks = [
        ("A2 gate present", test_a2_gate_present),
        ("A2 gate exec healthy (stdout log)", test_a2_gate_exec_healthy_stdout_log),
        ("A2 gate exec healthy (nest log)", test_a2_gate_exec_healthy_nest_log),
        ("A2 gate exec no marker fails", test_a2_gate_exec_no_marker_fails),
        ("A2 gate exec layers false fails", test_a2_gate_exec_layers_false_fails),
        ("A2 gate exec parse-1 expected", test_a2_gate_exec_parse1_expected),
        ("A6 G4 exec empty passes", test_a6_g4_exec_empty_passes),
        ("A6 G4 exec errors fail", test_a6_g4_exec_errors_fail),
        ("A3 markers", test_a3_markers),
        ("A5 present", test_a5_present),
        ("A6 present", test_a6_present),
        ("A7 no reload", test_a7_no_reload),
        ("A8 stop flag", test_a8_stop_flag),
        ("A10 live log only", test_a10_live_log_only),
        ("A4 record corrected", test_a4_record_corrected),
        ("A1 staging documented", test_a1_staging_documented),
        ("bash syntax", test_bash_syntax),
    ]
    for name, fn in checks:
        check(name, fn)
    print("---")
    if FAILURES:
        print("RESULT: %d/%d FAILED: %s" % (len(FAILURES), len(checks), ", ".join(FAILURES)))
        return 1
    print("RESULT: all %d checks PASS" % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
