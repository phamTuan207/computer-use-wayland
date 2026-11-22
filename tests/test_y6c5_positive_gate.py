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
import time
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
    assert "y6-profile-applied.txt" in block, "gate does not poll the marker file"
    assert "features.layers.enabled" in block, "gate lacks the layers.enabled signal"
    assert 'grep -a -q "Y6-NEST-OPTICS: applied" "$LOG" "$NEST_LOG"' not in block, (
        "gate still decides on a log grep for the applied marker")
    assert "marker file" in block, "gate fail string must name the marker file"
    assert "applied marker absent" not in block, (
        "old log-based fail string still in gate")
    assert "Y6C5_GATE_TIMEOUT_S" in block, "gate timeout not overridable for tests"
    # B2-3 redteam R-R2: the poll must require BOTH marker lines, not
    # just the optics line.
    assert 'grep -a -q "^Y6-NEST-OPTICS: applied" "$MARKER_FILE"' in block, (
        "gate poll lacks the optics marker grep")
    assert 'grep -a -q "^Y6-NEST-HOOK: profile applied" "$MARKER_FILE"' in block, (
        "gate poll lacks the hook marker grep")
    # B2-3 redteam R2-3: each marker must START its own line. A single
    # line containing both strings is not two lines, so the greps must
    # be anchored at line start, or a forged one-line marker passes.
    assert '"^Y6-NEST-OPTICS: applied"' in block, (
        "gate poll optics grep is not anchored at line start")
    assert '"^Y6-NEST-HOOK: profile applied"' in block, (
        "gate poll hook grep is not anchored at line start")
    # B2-3 redteam R-R3: the second G4 must sit inside the A2 block,
    # after the marker poll, before the gate OK echo.
    assert "second configerrors check" in block, "gate lacks the second G4"
    assert "configerrors empty after profile gate (G4 second OK)" in block, (
        "gate lacks the second-G4 pass echo")
    assert "nest-plugin-list-after-gate.json" in block, "gate lacks plugin-list re-check"
    assert "nest-glass-status-after-gate.json" in block, "gate lacks status re-check"
    # B2-3: layers.enabled must be checked from a status re-fetched AFTER
    # the marker, never from the pre-gate status file. The pre-gate file
    # name must not appear as a layers-check input inside the A2 block.
    assert 'python3 - "$NEST/nest-glass-status.json"' not in block, (
        "gate still checks layers.enabled from the stale pre-gate status")
    assert 'layers.get("enabled")' in block, "gate lacks the layers.enabled re-check"
    assert "re-fetched after the marker" in block, (
        "gate lacks the after-marker re-fetch comment")
    assert 'grep -a -h "Y6-NEST-OPTICS: applied" "$LOG" "$NEST_LOG" 2>/dev/null | head -3 || echo' not in block, (
        "dead corroboration line still in gate: head exits 0, so the echo never runs")
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


def run_gate_case(log_content, nest_log_content, layers_enabled, timeout_s="2",
                  marker_content=None, layers_enabled_after=None,
                  configerrors_after=""):
    """Execute the extracted A2 block under bash with stubs. Returns exit code.

    layers_enabled is the value in the pre-gate status file
    (nest-glass-status.json). layers_enabled_after is the value returned
    by the stubbed `nest hyprctl hyprglass status` re-fetch after the
    marker; it defaults to layers_enabled. A gate that reads the stale
    pre-gate file will pass/fail on layers_enabled, a gate that re-fetches
    will pass/fail on layers_enabled_after, so the two can be told apart.
    configerrors_after is the value returned by the stubbed `nest hyprctl
    configerrors` re-check after the marker (the second G4); it defaults
    to empty, so a gate without a second G4 passes here and a gate with
    one fails on a non-empty value.
    """
    if layers_enabled_after is None:
        layers_enabled_after = layers_enabled
    block = extract_block(runner_text(), "BEGIN Y6C5-A2", "END Y6C5-A2")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        nest_dir = tmp / "nest"
        nest_dir.mkdir()
        run_dir = tmp / "run"
        run_dir.mkdir()
        if marker_content is not None:
            (run_dir / "y6-profile-applied.txt").write_text(marker_content)
        log_file = tmp / "stdout.log"
        nest_log = tmp / "hyprland.log"
        log_file.write_text(log_content)
        nest_log.write_text(nest_log_content)
        (nest_dir / "nest-glass-status.json").write_text(
            json.dumps(_status_json(layers_enabled)))
        stub_plugin = tmp / "plugin.json"
        stub_plugin.write_text(json.dumps(_plugin_json()))
        stub_status = tmp / "status.json"
        stub_status.write_text(json.dumps(_status_json(layers_enabled_after)))
        prelude = (
            'fail() { echo "STUB-FAIL: $1" >&2; exit 1; }\n'
            'nest() {\n'
            '  case "$*" in\n'
            '    *"plugin list"*) cat "$STUB_PLUGIN_JSON";;\n'
            '    *"hyprglass status"*) cat "$STUB_STATUS_JSON";;\n'
            '    *"configerrors"*) printf "%s" "$STUB_CONFIGERRORS_AFTER";;\n'
            '    *) echo "stub nest: unknown args: $*" >&2; return 1;;\n'
            '  esac\n'
            '}\n'
            'LOG="' + str(log_file) + '"\n'
            'NEST_LOG="' + str(nest_log) + '"\n'
            'NEST="' + str(nest_dir) + '"\n'
            'RUN_DIR="' + str(run_dir) + '"\n'
            'STUB_PLUGIN_JSON="' + str(stub_plugin) + '"\n'
            'STUB_STATUS_JSON="' + str(stub_status) + '"\n'
            "STUB_CONFIGERRORS_AFTER='" + configerrors_after.replace("'", "'\\''") + "'\n"
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


MARKER_FILE_CONTENT = OPTICS_MARKER + "\n" + HOOK_APPLIED + "\n"


def test_a2_gate_exec_healthy_file():
    # A8 shape: marker file present, BOTH logs contain ONLY the parse-1
    # not-ready marker, layers.enabled true. Under the old log-grep gate
    # this run FAILS; under the file gate it must PASS.
    rc, out = run_gate_case(
        NOT_READY + "\n", NOT_READY + "\n", True,
        marker_content=MARKER_FILE_CONTENT)
    assert rc == 0, "healthy gate (marker file, logs parse-1 only) must pass, got rc=" + str(rc) + " out=" + out
    assert "profile gate OK" in out, "healthy gate must print profile gate OK"


def test_a2_gate_exec_no_marker_fails():
    rc, out = run_gate_case(NOT_READY + "\n", "", True)
    assert rc != 0, "gate with no marker file must fail"
    assert "marker file" in out, "gate must report the missing marker file, out=" + out


def test_a2_gate_exec_layers_false_fails():
    rc, out = run_gate_case(
        NOT_READY + "\n", NOT_READY + "\n", False,
        marker_content=MARKER_FILE_CONTENT)
    assert rc != 0, "gate with layers.enabled false must fail"
    assert "layers.enabled is not true" in out, "gate must report layers.enabled, out=" + out


def test_a2_gate_exec_layers_stale_pre_gate_passes():
    # B2-3, A8 shape with a stale pre-gate status: the pre-gate file says
    # layers.enabled false, the status re-fetched after the marker says
    # true. The gate must PASS: it must not read the stale pre-gate file.
    # The old gate read the pre-gate file before the poll and failed here.
    rc, out = run_gate_case(
        NOT_READY + "\n", NOT_READY + "\n", False,
        marker_content=MARKER_FILE_CONTENT, layers_enabled_after=True)
    assert rc == 0, "gate must pass on the after-marker status, not the stale pre-gate one, got rc=" + str(rc) + " out=" + out
    assert "profile gate OK" in out, "gate must print profile gate OK"
    assert "features.layers.enabled=True" in out, "gate must print the re-fetched layers.enabled value"


def test_a2_gate_exec_layers_after_false_fails():
    # B2-3, mirror case: pre-gate status says true, the status re-fetched
    # after the marker says false. The gate must FAIL on the fresh value.
    rc, out = run_gate_case(
        NOT_READY + "\n", NOT_READY + "\n", True,
        marker_content=MARKER_FILE_CONTENT, layers_enabled_after=False)
    assert rc != 0, "gate with layers.enabled false after the marker must fail"
    assert "layers.enabled is not true" in out, "gate must report layers.enabled, out=" + out


def test_a2_gate_exec_log_corroboration_echo():
    # B2-3: the log corroboration echo must actually run. Marker file
    # present, both logs contain only the parse-1 marker, so no applied
    # line ever flushed into the logs. The old `grep | head -3 || echo`
    # line never printed its echo (head exits 0); the new code must.
    rc, out = run_gate_case(
        NOT_READY + "\n", NOT_READY + "\n", True,
        marker_content=MARKER_FILE_CONTENT)
    assert rc == 0, "healthy gate must pass, got rc=" + str(rc) + " out=" + out
    assert "applied marker not in logs" in out, (
        "gate must print the log corroboration message when no applied line flushed, out=" + out)


def test_a2_gate_exec_optics_only_fails():
    # B2-3 redteam R-R2: a marker file with ONLY the optics line must
    # FAIL. The old poll accepted it, even though the batch-1 rerun
    # procedure requires both lines.
    rc, out = run_gate_case(
        NOT_READY + "\n", NOT_READY + "\n", True,
        marker_content=OPTICS_MARKER + "\n")
    assert rc != 0, "gate with optics-only marker must fail, got rc=" + str(rc) + " out=" + out
    assert "marker file" in out, "gate must report the missing marker, out=" + out


def test_a2_gate_exec_hook_only_fails():
    # B2-3 redteam R-R2, mirror case: a marker file with ONLY the hook
    # line must FAIL.
    rc, out = run_gate_case(
        NOT_READY + "\n", NOT_READY + "\n", True,
        marker_content=HOOK_APPLIED + "\n")
    assert rc != 0, "gate with hook-only marker must fail, got rc=" + str(rc) + " out=" + out
    assert "marker file" in out, "gate must report the missing marker, out=" + out


def test_a2_gate_exec_g4_second_fails():
    # B2-3 redteam R-R3: a parse-3 error that appears only after the
    # marker must fail the second G4, even with marker present and
    # layers.enabled true. The first G4 (before A2) cannot catch it.
    rc, out = run_gate_case(
        NOT_READY + "\n", NOT_READY + "\n", True,
        marker_content=MARKER_FILE_CONTENT,
        configerrors_after="config error: duplicate layer() registration")
    assert rc != 0, "gate with a second-G4 config error must fail, got rc=" + str(rc) + " out=" + out
    assert "config errors present" in out, "gate must report the second-G4 errors, out=" + out


def test_a2_gate_exec_one_line_both_markers_fails():
    # B2-3 redteam R2-3: a marker file with ONE line containing BOTH
    # strings must FAIL. The batch-1 procedure requires two lines; a
    # plain substring grep would pass this forged one-line marker.
    rc, out = run_gate_case(
        NOT_READY + "\n", NOT_READY + "\n", True,
        marker_content=OPTICS_MARKER + " " + HOOK_APPLIED + "\n")
    assert rc != 0, "gate with a one-line marker containing both strings must fail, got rc=" + str(rc) + " out=" + out
    assert "marker file" in out, "gate must report the missing marker, out=" + out


def test_a2_gate_exec_parse1_expected():
    # Parse-1 marker present AND marker file present: must pass, and the
    # run must log the parse-1 marker as expected, not as a failure.
    rc, out = run_gate_case(
        NOT_READY + "\n", "", True, marker_content=MARKER_FILE_CONTENT)
    assert rc == 0, "parse-1 marker + marker file must pass, got rc=" + str(rc)
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
    assert "y6-profile-applied.txt" in hook, "hook lacks the marker file write"
    assert "io.open" in hook, "hook lacks io.open for the marker file"
    assert "marker_file:close()" in hook, "hook lacks the marker file close"
    assert "XDG_RUNTIME_DIR" in hook, "hook must resolve the nest run dir from the environment"
    # B2-3, 4a guard: the run dir must sit under /tmp/y6-nested/, a
    # refusal must print, and a failed open must print, never be silent.
    assert 'string.match(run_dir, "^/tmp/y6%-nested/")' in hook, (
        "hook lacks the nest run dir path guard")
    assert "marker file NOT written, XDG_RUNTIME_DIR is not a nest run dir" in hook, (
        "hook lacks the guard refusal print")
    assert "marker file open failed" in hook, "hook lacks the open-failure print"
    assert "A failed open is silent" not in hook, "hook still claims a failed open is silent"
    # B2-3 redteam R-R1: a ".." component in the run dir must be refused
    # outright, even when the prefix matches, or the marker would land in
    # the live dir through path traversal.
    assert 'string.find(run_dir, "%.%.")' in hook, (
        "hook lacks the .. component refusal")
    assert "contains a .. component" in hook, (
        "hook lacks the .. refusal print")
    # B2-3 redteam R2-2: the fixed-name .tmp file must be removed before
    # the hook opens it, or a planted symlink at that name would be
    # truncated by io.open("w") before the rename.
    assert "os.remove(marker_tmp)" in hook, (
        "hook lacks the pre-open .tmp removal")
    # B2-3 redteam R2-1: a symlinked parent dir (/tmp/y6-nested) is
    # invisible to Lua string checks, so the hook must say so and leave
    # that check to the runner, which refuses a symlinked $NEST.
    assert "symlinked $NEST" in hook, (
        "hook lacks the parent-symlink limitation note")
    # B2-3 redteam race note: the marker must be written atomically, via
    # a temp file plus rename, so a reader never sees a half-written file.
    assert "os.rename(marker_tmp, marker_path)" in hook, (
        "hook lacks the atomic marker rename")
    assert "marker file rename failed" in hook, (
        "hook lacks the rename-failure print")
    assert hook.index('print("Y6-NEST-HOOK: profile applied")') < hook.index(
        'y6-profile-applied.txt'), "hook must write the file AFTER the applied print"
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


def test_a7_reload_wording():
    # B2-3, 4e: A8 tested only the automatic parse-2 reload, not a manual
    # reload, so the comment must not claim the reload hypothesis was
    # REFUTED. It must state the correct, weaker claim.
    text = runner_text()
    assert "REFUTED" not in text, "runner still claims the reload hypothesis was REFUTED"
    assert "tested only the automatic parse-2 reload, not" in text, (
        "runner lacks the corrected reload wording")
    assert "does not prove a reload" in text, (
        "runner lacks the corrected absent-marker wording")


def test_g4_before_a2():
    # B2-3, 4c: the G4 configerrors block must sit BEFORE the A2 marker
    # poll, as real code, not as a prose move instruction. In the A8 run
    # G4 never ran because it sat behind the failing A2 gate.
    text = runner_text()
    g4_begin = text.index("# BEGIN Y6C5-A6-G4 configerrors gate")
    g4_end = text.index("# END Y6C5-A6-G4 configerrors gate")
    a2_begin = text.index("# BEGIN Y6C5-A2 positive profile gate")
    assert g4_begin < g4_end < a2_begin, (
        "G4 block must end before the A2 block begins")
    assert "this block now runs BEFORE the A2 marker" in text, (
        "G4 block lacks the before-A2 comment")


def test_g4_second_after_marker():
    # B2-3 redteam R-R3: the second G4 must run AFTER the marker poll
    # and the status re-fetch, before the gate OK echo, so it can catch
    # parse-3 errors that appear only after parse 2 applies the profile.
    text = runner_text()
    poll_at = text.index('grep -a -q "^Y6-NEST-HOOK: profile applied" "$MARKER_FILE"')
    g4_second = text.index("# BEGIN Y6C5-A6-G4 second configerrors check")
    g4_second_end = text.index("# END Y6C5-A6-G4 second configerrors check")
    ok_at = text.index("profile gate OK: applied marker file present")
    assert poll_at < g4_second < g4_second_end < ok_at, (
        "second G4 must sit after the marker poll and before the gate OK echo")


def test_run_dir_symlink_guard():
    # B2-3 redteam R-R1: a symlinked RUN_DIR must fail closed before any
    # rm -rf or mkdir -p touches it, and teardown must never rm -rf
    # through a symlink planted mid-run.
    text = runner_text()
    assert 'if [ -L "$RUN_DIR" ]' in text, "runner lacks the RUN_DIR symlink check"
    assert "is a symlink; refusing to run" in text, (
        "runner lacks the symlink refusal message")
    assert "is a symlink at teardown" in text, (
        "teardown lacks the symlink warning")
    stale_at = text.index('rm -rf "$RUN_DIR/hypr"')
    # Anchor on the full startup-guard lines: the teardown guard contains
    # the same "[ -L ... ]" substring and sits earlier in the file.
    guard_at = text.index('if [ -L "$RUN_DIR" ]; then fail "RUN_DIR $RUN_DIR is a symlink; refusing to run')
    assert guard_at < stale_at, (
        "symlink check must sit before the stale-state rm -rf")
    # B2-3 redteam R2-1: a symlink at the PARENT $NEST redirects every
    # path under it even when RUN_DIR itself is plain, so the runner
    # must refuse a symlinked $NEST too, before the RUN_DIR check.
    assert 'if [ -L "$NEST" ]' in text, "runner lacks the NEST symlink check"
    assert "NEST $NEST is a symlink; refusing to run" in text, (
        "runner lacks the NEST symlink refusal message")
    nest_guard_at = text.index('if [ -L "$NEST" ]; then fail "NEST $NEST is a symlink; refusing to run')
    assert nest_guard_at < stale_at, (
        "NEST symlink check must sit before the stale-state rm -rf")
    assert nest_guard_at < guard_at, (
        "NEST symlink check must sit before the RUN_DIR symlink check")
    assert '|| [ -L "$NEST" ]' in text, (
        "teardown rm -rf guard lacks the NEST symlink check")
    # B2-3 redteam R2-2: the fixed-name marker .tmp must be removed at
    # startup, before the nest runs, or a planted symlink at that name
    # would be truncated by the hook's open before the rename.
    assert 'rm -f "$RUN_DIR/y6-profile-applied.txt.tmp"' in text, (
        "runner lacks the startup marker .tmp cleanup")
    tmp_cleanup_at = text.index('rm -f "$RUN_DIR/y6-profile-applied.txt.tmp"')
    assert tmp_cleanup_at < text.index('setsid bash -c "echo'), (
        "marker .tmp cleanup must sit before the nest launch")
    # B2-3 redteam R3-1: the guard must sit before the FIRST write under
    # $NEST, not just before the first touch of RUN_DIR. The run-log tee
    # is the first write under $NEST, and the live-plugin-list-before
    # write is another one; a guard after either lets a link planted
    # before the run redirect those writes before the refusal, and the
    # refusal itself would be tee'd into the victim dir.
    tee_at = text.index('exec > >(tee -a "$RUN_LOG")')
    assert nest_guard_at < tee_at, (
        "NEST symlink check must sit before the run-log tee (first write under $NEST)")
    assert guard_at < tee_at, (
        "RUN_DIR symlink check must sit before the run-log tee (first write under $NEST)")
    before_list_at = text.index('live hyprctl -j plugin list > "$NEST/live-plugin-list-before.json"')
    assert nest_guard_at < before_list_at, (
        "NEST symlink check must sit before the live plugin list (before) write")
    assert guard_at < before_list_at, (
        "RUN_DIR symlink check must sit before the live plugin list (before) write")
    flag_set_at = text.index('BEFORE_LIST_WRITTEN=1')
    assert flag_set_at > before_list_at, (
        "before-list flag must be set after the before-list write")
    write_line_no = next(
        i for i, line in enumerate(text.splitlines())
        if 'live hyprctl -j plugin list > "$NEST/live-plugin-list-before.json"' in line)
    following = [line for line in text.splitlines()[write_line_no + 1:]
                 if line.strip() and not line.strip().startswith("#")]
    assert following[0].strip() == 'BEFORE_LIST_WRITTEN=1', (
        "before-list flag must be the next statement after the before-list write")
    # R3-1, teardown: the after-list write must not follow a symlink
    # planted mid-run, and must only compare against a before-list this
    # run wrote itself. A stale before-list from an earlier run is not
    # a baseline.
    assert '[ "$BEFORE_LIST_WRITTEN" = "1" ]' in text, (
        "teardown after-list comparison does not require this run's before-list")
    assert 'not writing live plugin list (after)' in text, (
        "teardown lacks the NEST-symlink refusal for the after-list write")
    assert text.index('not writing live plugin list (after)') < text.index(
        'live hyprctl -j plugin list > "$NEST/live-plugin-list-after.json"'), (
        "teardown must re-check the NEST symlink before writing the after-list")


def test_symlink_guard_exec_early():
    # B2-3 redteam R3-1, behavioral proof: run the runner's own guard
    # lines plus its tee line against a symlinked $NEST and prove no
    # file lands in the victim dir and the run refuses; then run the
    # same lines against a plain $NEST and prove the tee log is written.
    # String asserts alone missed this: the old guard passed them while
    # sitting after the tee, so this test runs the real lines.
    text = runner_text()
    fail_line = 'fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }'
    assert text.count(fail_line) == 1, "fail() definition not found exactly once"
    tee_line = 'exec > >(tee -a "$RUN_LOG") 2>&1'
    assert text.count(tee_line) == 1, "tee line not found exactly once"
    # Take the four lines IN FILE ORDER, not in an assumed order: on
    # the pre-fix runner the tee precedes the guard, so running the
    # slice in file order writes into the victim dir before refusing.
    # Assembling them in a fixed order would hide exactly that bug.
    wanted = [line for line in text.splitlines()
              if line == fail_line
              or line.startswith('if [ -L "$NEST" ]; then fail')
              or line.startswith('if [ -L "$RUN_DIR" ]; then fail')
              or line == tee_line]
    assert len(wanted) == 4, (
        "expected fail + 2 guards + tee in file order, got %d: %s"
        % (len(wanted), wanted))
    with tempfile.TemporaryDirectory() as tmp:
        victim = Path(tmp) / "victim"
        victim.mkdir()
        nest_link = Path(tmp) / "nestlink"
        os.symlink(victim, nest_link)
        plain = Path(tmp) / "plain"
        plain.mkdir()
        for nest_dir, expect_rc, expect_log in (
                (nest_link, 1, False), (plain, 0, True)):
            script = Path(tmp) / ("guard-" + nest_dir.name + ".sh")
            script.write_text("\n".join([
                "set -u",
                'NEST="' + str(nest_dir) + '"',
                'RUN_DIR="$NEST/run"',
                'RUN_LOG="$NEST/run-test.log"',
            ] + wanted + [
                'echo "GUARD-PASSED"',
            ]) + "\n")
            proc = subprocess.run(["bash", str(script)], capture_output=True,
                                  text=True, timeout=30)
            assert proc.returncode == expect_rc, (
                "guard script rc=%d, expected %d for %s: %s%s"
                % (proc.returncode, expect_rc, nest_dir, proc.stdout, proc.stderr))
            if not expect_log:
                assert "refusing to run" in proc.stdout, (
                    "symlinked NEST did not refuse: " + proc.stdout)
                assert list(victim.iterdir()) == [], (
                    "guard wrote into the victim dir: "
                    + str(list(victim.iterdir())))
            else:
                assert "GUARD-PASSED" in proc.stdout, (
                    "plain NEST did not reach the tee: " + proc.stdout)
                log = nest_dir / "run-test.log"
                for _ in range(50):
                    if log.is_file() and "GUARD-PASSED" in log.read_text():
                        break
                    time.sleep(0.1)
                else:
                    raise AssertionError(
                        "tee log missing or empty for plain NEST")


def test_fixed_name_version_file_guard():
    # B2-3 redteam R4-1: the live version file has a fixed name in /tmp,
    # so a symlink planted there before the run would be truncated by
    # the redirect before hyprctl even runs. The runner must remove any
    # planted link before redirecting, so the redirect always creates a
    # fresh regular file. Behavioral proof with the real lines, not
    # just string asserts.
    text = runner_text()
    assert 'LIVE_VERSION_FILE=/tmp/y6-live-version.txt' in text, (
        "runner lacks the LIVE_VERSION_FILE definition")
    assert text.count('/tmp/y6-live-version.txt') == 1, (
        "the fixed version path must appear only in the variable definition")
    rm_line = 'rm -f "$LIVE_VERSION_FILE"'
    ver_line = 'live hyprctl version > "$LIVE_VERSION_FILE"'
    assert rm_line in text, "runner lacks the version-file link removal"
    assert ver_line in text, "runner lacks the version redirect"
    assert text.index(rm_line) < text.index(ver_line), (
        "version-file link removal must sit before the version redirect")
    wanted = [line.strip() for line in text.splitlines()
              if line.strip() == rm_line
              or ver_line in line]
    assert len(wanted) == 2, (
        "expected rm + version redirect in file order, got %d: %s"
        % (len(wanted), wanted))
    with tempfile.TemporaryDirectory() as tmp:
        victim = Path(tmp) / "victim.txt"
        victim.write_text("LIVE-DATA-DO-NOT-TOUCH\n")
        link = Path(tmp) / "version.txt"
        os.symlink(victim, link)
        script = Path(tmp) / "version-guard.sh"
        script.write_text("\n".join([
            "set -u",
            'LIVE_VERSION_FILE="' + str(link) + '"',
            'live() { echo "Hyprland 0.57.2 fake-version"; }',
        ] + wanted) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 0, (
            "version guard script rc=%d: %s%s"
            % (proc.returncode, proc.stdout, proc.stderr))
        assert victim.read_text() == "LIVE-DATA-DO-NOT-TOUCH\n", (
            "version redirect truncated the victim file")
        assert not link.is_symlink(), (
            "planted version-file link was not removed")
        assert "fake-version" in link.read_text(), (
            "version file does not hold the hyprctl output")


def test_lock_symlink_guard():
    # B2-3 redteam R4-2: opening the lock with > truncates its target,
    # so a symlink planted at the fixed lock path before the run would
    # truncate the victim file. flock itself never truncates, only the
    # open does, so the runner must refuse a symlinked lock path before
    # opening it. Behavioral proof with the real lines.
    text = runner_text()
    lock_check = 'if [ -L "$LOCK" ]; then fail "lock $LOCK is a symlink; refusing to run'
    assert lock_check in text, "runner lacks the lock symlink check"
    open_line = 'exec 9>"$LOCK"'
    assert open_line in text, "runner lacks the lock open"
    assert text.index(lock_check) < text.index(open_line), (
        "lock symlink check must sit before the lock open")
    assert 'flock -n 9' in text, "runner lacks the flock after the lock open"
    assert text.index(open_line) < text.index('flock -n 9'), (
        "flock must sit after the lock open")
    fail_line = 'fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }'
    wanted = [line for line in text.splitlines()
              if line.startswith('if [ -L "$LOCK" ]; then fail')
              or line.startswith('exec 9>"$LOCK"')
              or line.startswith('flock -n 9')]
    assert len(wanted) == 3, (
        "expected lock check + open + flock in file order, got %d: %s"
        % (len(wanted), wanted))
    with tempfile.TemporaryDirectory() as tmp:
        victim = Path(tmp) / "victim.txt"
        victim.write_text("LOCK-VICTIM-CONTENT\n")
        link = Path(tmp) / "lock"
        os.symlink(victim, link)
        script = Path(tmp) / "lock-guard-link.sh"
        script.write_text("\n".join([
            "set -u",
            fail_line,
            'LOCK="' + str(link) + '"',
        ] + wanted + [
            'echo "LOCK-OK"',
        ]) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 1, (
            "symlinked lock did not refuse: rc=%d %s%s"
            % (proc.returncode, proc.stdout, proc.stderr))
        assert "refusing to run" in proc.stdout, (
            "symlinked lock refusal message missing: " + proc.stdout)
        assert victim.read_text() == "LOCK-VICTIM-CONTENT\n", (
            "lock open truncated the victim file")
        plain = Path(tmp) / "plain.lock"
        script2 = Path(tmp) / "lock-guard-plain.sh"
        script2.write_text("\n".join([
            "set -u",
            fail_line,
            'LOCK="' + str(plain) + '"',
        ] + wanted + [
            'echo "LOCK-OK"',
        ]) + "\n")
        proc2 = subprocess.run(["bash", str(script2)], capture_output=True,
                               text=True, timeout=30)
        assert proc2.returncode == 0, (
            "plain lock path did not open: rc=%d %s%s"
            % (proc2.returncode, proc2.stdout, proc2.stderr))
        assert "LOCK-OK" in proc2.stdout, (
            "plain lock path did not reach the end: " + proc2.stdout)
        assert plain.is_file() and not plain.is_symlink(), (
            "plain lock file was not created as a regular file")


def test_lock_parent_dir_symlink_guard():
    # R5-1: the R4-2 leaf check alone does not stop a symlink at the
    # lock parent dir. LOCK is $HOME/.cache/agent-computer-use/zen_dom.lock.
    # If agent-computer-use is a symlink to a victim dir, [ -L "$LOCK" ]
    # is false (the leaf is a plain file) and exec 9> would truncate the
    # victim lock. Same class as R2-1 (symlink parent of $NEST).
    text = runner_text()
    parent_check = 'if [ -L "$(dirname "$LOCK")" ]; then fail "lock parent dir'
    assert parent_check in text, "lock parent dir symlink check missing"
    leaf_check = 'if [ -L "$LOCK" ]; then fail "lock $LOCK is a symlink'
    open_line = 'exec 9>"$LOCK"'
    flock_line = "flock -n 9"
    assert text.index(leaf_check) < text.index(parent_check) < text.index(open_line) < text.index(flock_line), (
        "leaf check, parent check, open and flock out of order")

    lines = text.splitlines()
    wanted = [l for l in lines if l.startswith('if [ -L "$LOCK" ]; then fail')
               or l.startswith('if [ -L "$(dirname "$LOCK")" ]; then fail')
               or l.startswith('exec 9>"$LOCK"') or l.startswith("flock -n 9")]
    assert len(wanted) == 4, f"expected exactly the 4 lock lines, got {len(wanted)}: {wanted}"

    def run_lock_lines(tmp, lock, script_lines):
        script = Path(tmp) / "lock-parent-guard.sh"
        script.write_text("\n".join([
            "set -u",
            'LOCK="' + lock + '"',
            "fail() { echo \"FAIL: $*\" >&2; exit 1; }",
        ] + script_lines + ["echo LOCK-OK"]) + "\n")
        return subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)

    # Case A: parent dir is a symlink to a victim dir holding a lock file.
    with tempfile.TemporaryDirectory() as tmp:
        victim = Path(tmp) / "victim"
        victim.mkdir()
        victim_lock = victim / "zen_dom.lock"
        victim_lock.write_text("VICTIM-LOCK-DATA\n")
        link = Path(tmp) / "agent-computer-use"
        link.symlink_to(victim, target_is_directory=True)
        res = run_lock_lines(tmp, str(link / "zen_dom.lock"), wanted)
        assert res.returncode == 1, f"parent symlink must refuse, got rc={res.returncode} out={res.stdout} err={res.stderr}"
        assert "refusing to run" in res.stdout + res.stderr
        assert victim_lock.read_text() == "VICTIM-LOCK-DATA\n", "victim lock must be untouched"
        assert not victim_lock.is_symlink()

    # Case B: plain parent dir, the lock opens and flock holds it.
    with tempfile.TemporaryDirectory() as tmp:
        plain = Path(tmp) / "agent-computer-use"
        plain.mkdir()
        lock = plain / "zen_dom.lock"
        res = run_lock_lines(tmp, str(lock), wanted)
        assert res.returncode == 0, f"plain parent must pass, got rc={res.returncode} out={res.stdout} err={res.stderr}"
        assert "LOCK-OK" in res.stdout
        assert lock.is_file() and not lock.is_symlink()


def test_teardown_lock_free_check_symlink_guard():
    # R5-1 side case: teardown line 226 runs flock -n "$LOCK" -c true with
    # no symlink check, even when the run died before the lock was opened.
    # flock never truncates, but it follows the link and creates/locks a
    # file in the victim dir. The teardown check must skip with a warning
    # instead when the lock path or its parent dir is a symlink.
    # R6-1: the same check must also cover every ancestor above the
    # parent, or a $HOME/.cache symlink bypasses it the same way. The
    # block now walks the ancestors first and remembers a hit.
    text = runner_text()
    lines = text.splitlines()
    assert "skipping lock-free check" in text, (
        "teardown flock symlink guard missing (no skipping lock-free check line)")
    start = next(i for i, l in enumerate(lines)
                 if l.strip() == "_lock_ancestor_bad=0")
    end = next(i for i in range(start, len(lines)) if lines[i].strip() == "fi")
    block = lines[start:end + 1]
    assert 'flock -n "$LOCK" -c true' in "\n".join(block), "teardown flock line must be inside the guard"
    assert '|| [ "$_lock_ancestor_bad" = "1" ]; then' in "\n".join(block), (
        "teardown flock guard must test the ancestor-walk hit")
    assert text.index("skipping lock-free check") < text.index("teardown done"), (
        "teardown flock guard must sit inside teardown")

    def run_block(tmp, home, lock, block_lines):
        script = Path(tmp) / "teardown-flock-guard.sh"
        script.write_text("\n".join([
            "set -u",
            'HOME="' + home + '"',
            'LOCK="' + lock + '"',
        ] + block_lines) + "\n")
        return subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)

    # Case A: grandparent dir ($HOME/.cache) is a symlink to a victim
    # dir. No file may be created or locked inside the victim dir,
    # victim content untouched.
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        victim = Path(tmp) / "victim"
        victim.mkdir()
        victim_lock = victim / "agent-computer-use" / "zen_dom.lock"
        victim_lock.parent.mkdir()
        victim_lock.write_text("VICTIM-LOCK-DATA\n")
        cache_link = home / ".cache"
        cache_link.parent.mkdir(parents=True, exist_ok=True)
        cache_link.symlink_to(victim, target_is_directory=True)
        res = run_block(tmp, str(home), str(cache_link / "agent-computer-use" / "zen_dom.lock"), block)
        assert res.returncode == 0
        assert "skipping lock-free check" in res.stdout, (
            "grandparent symlink must skip the lock-free check, out=" + res.stdout)
        assert "lock free after teardown" not in res.stdout
        assert sorted(p.name for p in victim.iterdir()) == ["agent-computer-use"], (
            f"victim dir must gain no file, got {[p.name for p in victim.iterdir()]}")
        assert victim_lock.read_text() == "VICTIM-LOCK-DATA\n"

    # Case B: parent dir is a symlink to a victim dir. No file may be
    # created or locked inside the victim dir, victim content untouched.
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        home.mkdir()
        victim = Path(tmp) / "victim"
        victim.mkdir()
        victim_lock = victim / "zen_dom.lock"
        victim_lock.write_text("VICTIM-LOCK-DATA\n")
        link = home / ".cache" / "agent-computer-use"
        link.parent.mkdir(parents=True)
        link.symlink_to(victim, target_is_directory=True)
        res = run_block(tmp, str(home), str(link / "zen_dom.lock"), block)
        assert res.returncode == 0
        assert "skipping lock-free check" in res.stdout
        assert "lock free after teardown" not in res.stdout
        assert sorted(p.name for p in victim.iterdir()) == ["zen_dom.lock"], (
            f"victim dir must gain no file, got {[p.name for p in victim.iterdir()]}")
        assert victim_lock.read_text() == "VICTIM-LOCK-DATA\n"

    # Case C: plain parent dir, lock file absent. flock creates it and
    # reports the lock free.
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        plain = home / ".cache" / "agent-computer-use"
        plain.mkdir(parents=True)
        lock = plain / "zen_dom.lock"
        res = run_block(tmp, str(home), str(lock), block)
        assert res.returncode == 0
        assert "lock free after teardown" in res.stdout
        assert lock.is_file() and not lock.is_symlink()


def test_lock_grandparent_symlink_guard():
    # R6-1: the R5-1 leaf + parent checks do not stop a symlink at
    # $HOME/.cache (the lock's grandparent). LOCK is
    # $HOME/.cache/agent-computer-use/zen_dom.lock: with .cache a symlink
    # to a victim dir, [ -L "$LOCK" ] is false (the leaf is a plain file)
    # and [ -L "$(dirname "$LOCK")" ] is false (agent-computer-use is a
    # plain dir inside the victim dir), and exec 9> truncates the victim
    # lock. The runner must check EVERY ancestor dir above the parent,
    # from $HOME down. Behavioral proof with the real lines, in file order.
    text = runner_text()
    lines = text.splitlines()
    leaf_check = 'if [ -L "$LOCK" ]; then fail "lock $LOCK is a symlink'
    parent_check = 'if [ -L "$(dirname "$LOCK")" ]; then fail "lock parent dir'
    open_line = 'exec 9>"$LOCK"'
    flock_line = "flock -n 9"
    assert leaf_check in text, "runner lacks the lock leaf check"
    assert parent_check in text, "runner lacks the lock parent check"
    leaf_at = next(i for i, l in enumerate(lines) if leaf_check in l)
    parent_at = next(i for i, l in enumerate(lines) if parent_check in l)
    open_at = next(i for i, l in enumerate(lines) if l.startswith(open_line))
    flock_at = next(i for i, l in enumerate(lines) if l.startswith(flock_line))
    # The ancestor walk sits between the parent check and the open, and
    # starts at the grandparent (leaf and parent are already checked).
    walk_start = next(i for i, l in enumerate(lines)
                      if l.strip() == '_lock_dir=$(dirname "$(dirname "$LOCK")")'
                      and parent_at < i < open_at)
    walk_end = next(i for i in range(walk_start, len(lines))
                    if lines[i].strip() == "done")
    walk = lines[walk_start:walk_end + 1]
    assert any("lock ancestor dir" in l for l in walk), (
        "ancestor walk lacks the ancestor refusal message")
    assert leaf_at < parent_at < walk_start < open_at < flock_at, (
        "leaf check, parent check, ancestor walk, open and flock out of order")
    # Assemble in file order: leaf check, parent check, walk, open, flock.
    wanted = ([lines[leaf_at], lines[parent_at]] + walk
              + [lines[open_at], lines[flock_at]])

    def run_lock_lines(tmp, home, lock):
        script = Path(tmp) / "lock-grandparent-guard.sh"
        script.write_text("\n".join([
            "set -u",
            'HOME="' + home + '"',
            'LOCK="' + lock + '"',
            'fail() { echo "FAIL: $*" >&2; exit 1; }',
        ] + wanted + ["echo LOCK-OK"]) + "\n")
        return subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)

    # Case A: $HOME/.cache is a symlink to a victim dir holding the lock.
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        victim = Path(tmp) / "victim"
        victim.mkdir()
        victim_lock = victim / "agent-computer-use" / "zen_dom.lock"
        victim_lock.parent.mkdir()
        victim_lock.write_text("VICTIM-LOCK-DATA\n")
        cache_link = home / ".cache"
        cache_link.parent.mkdir(parents=True, exist_ok=True)
        cache_link.symlink_to(victim, target_is_directory=True)
        res = run_lock_lines(tmp, str(home), str(cache_link / "agent-computer-use" / "zen_dom.lock"))
        assert res.returncode == 1, (
            "grandparent symlink must refuse, got rc=%d out=%s err=%s"
            % (res.returncode, res.stdout, res.stderr))
        assert "refusing to run" in res.stdout + res.stderr
        assert victim_lock.read_text() == "VICTIM-LOCK-DATA\n", (
            "grandparent symlink must not truncate the victim lock")

    # Case B: plain dirs all the way down, the lock opens and flock holds.
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        plain = home / ".cache" / "agent-computer-use"
        plain.mkdir(parents=True)
        lock = plain / "zen_dom.lock"
        res = run_lock_lines(tmp, str(home), str(lock))
        assert res.returncode == 0, (
            "plain lock path must pass, got rc=%d out=%s err=%s"
            % (res.returncode, res.stdout, res.stderr))
        assert "LOCK-OK" in res.stdout
        assert lock.is_file() and not lock.is_symlink()


def test_nest_fixed_name_cleanup():
    # R6-2: the $NEST/$RUN_DIR guard only refuses when $NEST or $RUN_DIR
    # itself is a symlink. It does NOT protect fixed-name files directly
    # under $NEST: a symlink planted at one of those names before the
    # run is truncated by the redirect that writes it. The runner must
    # remove any planted link at every fixed-name file under $NEST at
    # startup, before the first write. Behavioral proof with the real
    # cleanup lines, plus a string assert that every fixed-name target
    # in the runner is listed in the cleanup.
    text = runner_text()
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.startswith('rm -f "$NEST/live-plugin-list-before.json"'))
    end = next(i for i in range(start, len(lines)) if '"$LOG"' in lines[i])
    block = lines[start:end + 1]
    block_text = "\n".join(block)
    expected = [
        "live-plugin-list-before.json", "live-plugin-list-after.json",
        "nest-plugin-list.json", "nest-plugin-list.err",
        "nest-glass-status.json", "nest-glass-status.err",
        "nest-plugin-list-after-gate.json", "nest-plugin-list-after-gate.err",
        "nest-glass-status-after-gate.json", "nest-glass-status-after-gate.err",
        "nest-mpv.log", "nest-mpv-static.log", "nest-mpv-armB.log",
        "nest-pill.log", "nest-layers.json",
        "nest-glass-stats-before-arms.json", "nest-glass-stats-before-arms.err",
        "nest-glass-stats-after-arms.json", "nest-glass-stats-after-arms.err",
        '"$LOG"',
    ]
    for name in expected:
        assert name in block_text, (
            "startup cleanup does not cover fixed-name file " + name)
    # The cleanup must sit after the $NEST/$RUN_DIR guard (through a
    # symlinked $NEST it would delete files in the victim dir) and
    # before the run-log tee (the first write under $NEST).
    nest_guard_at = text.index('if [ -L "$NEST" ]; then fail "NEST $NEST is a symlink; refusing to run')
    tee_at = text.index('exec > >(tee -a "$RUN_LOG")')
    cleanup_at = text.index('rm -f "$NEST/live-plugin-list-before.json"')
    assert nest_guard_at < cleanup_at < tee_at, (
        "startup cleanup must sit after the NEST guard and before the run-log tee")
    with tempfile.TemporaryDirectory() as tmp:
        nest = Path(tmp) / "nest"
        nest.mkdir()
        before_victim = Path(tmp) / "before-victim.txt"
        before_victim.write_text("VICTIM-PLUGIN-DATA\n")
        mpv_victim = Path(tmp) / "mpv-victim.txt"
        mpv_victim.write_text("VICTIM-MPV-DATA\n")
        os.symlink(before_victim, nest / "live-plugin-list-before.json")
        os.symlink(mpv_victim, nest / "nest-mpv.log")
        script = Path(tmp) / "nest-cleanup.sh"
        script.write_text("\n".join([
            "set -u",
            'NEST="' + str(nest) + '"',
            'LOG="' + str(nest / "hyprland-wayland.log") + '"',
        ] + block) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 0, (
            "cleanup script rc=%d: %s%s" % (proc.returncode, proc.stdout, proc.stderr))
        assert before_victim.read_text() == "VICTIM-PLUGIN-DATA\n", (
            "cleanup must not truncate the before-list victim file")
        assert mpv_victim.read_text() == "VICTIM-MPV-DATA\n", (
            "cleanup must not truncate the mpv-log victim file")
        assert not (nest / "live-plugin-list-before.json").is_symlink(), (
            "planted before-list link was not removed")
        assert not (nest / "nest-mpv.log").is_symlink(), (
            "planted mpv-log link was not removed")


def test_run_log_symlink_guard():
    # R7-1: the run log name carries a timestamp, but that does not make
    # it safe: a link can be planted for every second in a window before
    # the run, and the tee below opens it with O_APPEND, so the whole run
    # log would be appended into the victim file. The runner must remove
    # any planted link at RUN_LOG before the tee. Behavioral proof with
    # the real lines, not just string asserts.
    text = runner_text()
    rm_line = 'rm -f "$RUN_LOG"'
    tee_line = 'exec > >(tee -a "$RUN_LOG") 2>&1'
    assert rm_line in text, "runner lacks the run-log link removal"
    assert tee_line in text, "runner lacks the run-log tee"
    nest_guard_at = text.index('if [ -L "$NEST" ]; then fail "NEST $NEST is a symlink; refusing to run')
    assert nest_guard_at < text.index(rm_line) < text.index(tee_line), (
        "run-log link removal must sit after the NEST guard and before the run-log tee")
    wanted = [line for line in text.splitlines()
              if line.strip() == rm_line or line == tee_line]
    assert len(wanted) == 2, (
        "expected rm + tee in file order, got %d: %s" % (len(wanted), wanted))
    with tempfile.TemporaryDirectory() as tmp:
        victim = Path(tmp) / "victim.txt"
        victim.write_text("VICTIM-LOG-DATA-DO-NOT-TOUCH\nsecond line\n")
        link = Path(tmp) / "run-20261122-123651.log"
        os.symlink(victim, link)
        script = Path(tmp) / "run-log-guard.sh"
        script.write_text("\n".join([
            "set -u",
            'RUN_LOG="' + str(link) + '"',
        ] + wanted + [
            'echo "RUN-LOG-MARKER"',
        ]) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 0, (
            "run-log guard script rc=%d: %s%s"
            % (proc.returncode, proc.stdout, proc.stderr))
        assert victim.read_text() == "VICTIM-LOG-DATA-DO-NOT-TOUCH\nsecond line\n", (
            "tee appended the run log into the victim file")
        assert not link.is_symlink(), (
            "planted run-log link was not removed")
        # The tee process flushes asynchronously; poll like the guard
        # exec test does instead of assuming it has finished.
        for _ in range(50):
            if link.is_file() and "RUN-LOG-MARKER" in link.read_text():
                break
            time.sleep(0.1)
        else:
            raise AssertionError("tee log missing the marker line")


def test_teardown_cp_dest_guard():
    # R7-2: both teardown copy destinations carry a timestamp, but that
    # does not make them safe: a link can be planted for every second in
    # a window before the run, and cp through a planted symlink would
    # truncate the victim file. The runner must remove any planted link
    # at each destination before copying. Behavioral proof with the real
    # lines, for both the marker copy and the hypr-saved copy.
    text = runner_text()
    marker_rm = 'rm -f "$NEST/y6-profile-applied-$START_TS.txt"'
    marker_cp = 'cp "$RUN_DIR/y6-profile-applied.txt" "$NEST/y6-profile-applied-$START_TS.txt"'
    saved_rm = 'rm -rf "$NEST/hypr-saved-$START_TS-$SIG"'
    saved_cp = 'cp -r "$RUN_DIR/hypr/$SIG" "$NEST/hypr-saved-$START_TS-$SIG"'
    assert marker_rm in text, "runner lacks the marker copy destination removal"
    assert saved_rm in text, "runner lacks the saved-log copy destination removal"
    assert text.index(marker_rm) < text.index(marker_cp), (
        "marker destination removal must sit before the marker copy")
    assert text.index(saved_rm) < text.index(saved_cp), (
        "saved-log destination removal must sit before the saved-log copy")
    # Marker copy: planted symlink at the destination.
    with tempfile.TemporaryDirectory() as tmp:
        nest = Path(tmp) / "nest"
        nest.mkdir()
        run_dir = Path(tmp) / "run"
        run_dir.mkdir()
        (run_dir / "y6-profile-applied.txt").write_text(
            "Y6-NEST-OPTICS: applied blur=0.15\nY6-NEST-HOOK: profile applied\n")
        victim = Path(tmp) / "victim.txt"
        victim.write_text("VICTIM-MARKER-DATA\n")
        dest = nest / "y6-profile-applied-20261122-123651.txt"
        os.symlink(victim, dest)
        wanted = [line.strip() for line in text.splitlines()
                  if line.strip() == marker_rm
                  or marker_cp in line]
        assert len(wanted) == 2, (
            "expected marker rm + cp in file order, got %d: %s" % (len(wanted), wanted))
        script = Path(tmp) / "marker-cp-guard.sh"
        script.write_text("\n".join([
            "set -u",
            'NEST="' + str(nest) + '"',
            'RUN_DIR="' + str(run_dir) + '"',
            'START_TS="20261122-123651"',
        ] + wanted) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 0, (
            "marker copy guard script rc=%d: %s%s"
            % (proc.returncode, proc.stdout, proc.stderr))
        assert victim.read_text() == "VICTIM-MARKER-DATA\n", (
            "marker copy truncated the victim file")
        assert not dest.is_symlink(), (
            "planted marker copy destination link was not removed")
        assert "Y6-NEST-HOOK: profile applied" in dest.read_text(), (
            "marker copy did not land in the destination file")
    # Hypr-saved copy: planted symlink at the destination dir.
    with tempfile.TemporaryDirectory() as tmp:
        nest = Path(tmp) / "nest"
        nest.mkdir()
        run_dir = Path(tmp) / "run"
        src = run_dir / "hypr" / "abc123"
        src.mkdir(parents=True)
        (src / "hyprland.log").write_text("nested log line\n")
        victim_dir = Path(tmp) / "victim-dir"
        victim_dir.mkdir()
        victim_file = victim_dir / "keep.txt"
        victim_file.write_text("VICTIM-SAVED-DATA\n")
        dest = nest / "hypr-saved-20261122-123651-abc123"
        os.symlink(victim_dir, dest, target_is_directory=True)
        wanted = [line.strip() for line in text.splitlines()
                  if line.strip() == saved_rm
                  or saved_cp in line]
        assert len(wanted) == 2, (
            "expected saved-log rm + cp in file order, got %d: %s" % (len(wanted), wanted))
        script = Path(tmp) / "saved-cp-guard.sh"
        script.write_text("\n".join([
            "set -u",
            'NEST="' + str(nest) + '"',
            'RUN_DIR="' + str(run_dir) + '"',
            'START_TS="20261122-123651"',
            'SIG="abc123"',
        ] + wanted) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 0, (
            "saved-log copy guard script rc=%d: %s%s"
            % (proc.returncode, proc.stdout, proc.stderr))
        assert victim_file.read_text() == "VICTIM-SAVED-DATA\n", (
            "saved-log copy wrote into the victim dir")
        assert not dest.is_symlink(), (
            "planted saved-log destination link was not removed")
        assert (dest / "hyprland.log").read_text() == "nested log line\n", (
            "saved-log copy did not land in the destination dir")


def test_frames_symlink_guard():
    # R7-3: the frames dir name carries a timestamp, but that does not
    # make it safe: a link can be planted for every second in a window
    # before the run, mkdir -p would follow it, and grim would then
    # truncate a file inside the victim dir. The runner must refuse
    # outright if FRAMES is a symlink before mkdir -p. Behavioral proof
    # with the real lines.
    text = runner_text()
    guard = 'if [ -L "$FRAMES" ]; then fail "FRAMES $FRAMES is a symlink; refusing to run'
    assert guard in text, "runner lacks the FRAMES symlink check"
    mkdir_line = 'mkdir -p "$RUN_DIR" "$FRAMES" "$NEST/cache"'
    assert mkdir_line in text, "runner lacks the FRAMES mkdir"
    assert text.index(guard) < text.index(mkdir_line), (
        "FRAMES symlink check must sit before the mkdir -p")
    fail_line = 'fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }'
    wanted = [line for line in text.splitlines()
              if line.startswith('if [ -L "$FRAMES" ]; then fail')
              or line.strip() == mkdir_line]
    assert len(wanted) == 2, (
        "expected FRAMES check + mkdir in file order, got %d: %s"
        % (len(wanted), wanted))
    with tempfile.TemporaryDirectory() as tmp:
        nest = Path(tmp) / "nest"
        nest.mkdir()
        victim_dir = Path(tmp) / "victim-dir"
        victim_dir.mkdir()
        victim_file = victim_dir / "control-1.png"
        victim_file.write_text("VICTIM-FRAME-DATA\n")
        link = nest / "frames-20261122-123651"
        os.symlink(victim_dir, link, target_is_directory=True)
        script = Path(tmp) / "frames-guard-link.sh"
        script.write_text("\n".join([
            "set -u",
            fail_line,
            'NEST="' + str(nest) + '"',
            'RUN_DIR="' + str(nest / "run") + '"',
            'FRAMES="' + str(link) + '"',
        ] + wanted) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 1, (
            "symlinked FRAMES did not refuse: rc=%d %s%s"
            % (proc.returncode, proc.stdout, proc.stderr))
        assert "refusing to run" in proc.stdout, (
            "symlinked FRAMES refusal message missing: " + proc.stdout)
        assert victim_file.read_text() == "VICTIM-FRAME-DATA\n", (
            "FRAMES guard wrote into the victim dir")
        assert sorted(p.name for p in victim_dir.iterdir()) == ["control-1.png"], (
            "victim dir gained a file: " + str(list(victim_dir.iterdir())))
        plain_frames = nest / "frames-20261122-123652"
        script2 = Path(tmp) / "frames-guard-plain.sh"
        script2.write_text("\n".join([
            "set -u",
            fail_line,
            'NEST="' + str(nest) + '"',
            'RUN_DIR="' + str(nest / "run") + '"',
            'FRAMES="' + str(plain_frames) + '"',
        ] + wanted) + "\n")
        proc2 = subprocess.run(["bash", str(script2)], capture_output=True,
                               text=True, timeout=30)
        assert proc2.returncode == 0, (
            "plain FRAMES path did not pass: rc=%d %s%s"
            % (proc2.returncode, proc2.stdout, proc2.stderr))
        assert plain_frames.is_dir() and not plain_frames.is_symlink(), (
            "plain FRAMES dir was not created as a regular dir")


def _hijack_pill_socket(state_dir):
    # Helper for the R8-1 tests: run the pill's real lines against
    # state_dir (mkdir, fresh token, indicator.listen) and prove the
    # socket token can be recovered from the socket filename and used to
    # drive hide through the real indicator.serve. Returns the reply.
    # The pill file itself is outside this diff; the lines below are the
    # same three lines the pill runs, with the repo's indicator module.
    sys.path.insert(0, str(ROOT / "scripts"))
    import indicator
    import secrets
    import socket
    import threading

    class _FakeNative:
        def command(self, cmd):
            return "hidden" if cmd == "hide" else "ok"

    state_dir.mkdir(parents=True, exist_ok=True)
    token = secrets.token_hex(16)
    server = indicator.listen(state_dir, token)
    try:
        socks = sorted(state_dir.glob("indicator-*.sock"))
        assert len(socks) == 1, "expected 1 pill socket, got %s" % socks
        recovered = socks[0].name[len("indicator-"):-len(".sock")]
        assert recovered == token, "token in socket name != pill token"
        result = {}

        def serve_once():
            try:
                result["reply"] = indicator.serve(server, _FakeNative(), token)
            except Exception as exc:  # noqa: BLE001 - recorded below
                result["error"] = repr(exc)

        thread = threading.Thread(target=serve_once, daemon=True)
        thread.start()
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect(str(socks[0]))
        client.sendall((json.dumps({"token": recovered, "command": "hide"}) + "\n").encode())
        reply = client.recv(256).decode().strip()
        client.close()
        thread.join(timeout=5)
        assert "error" not in result, "indicator.serve raised: %s" % result.get("error")
        return reply
    finally:
        server.close()


def test_nest_cache_symlink_guard():
    # R8-1 cache level: $NEST/cache is not just a mkdir target. The pill
    # binds its control socket under $NEST/cache/agent-computer-use, and
    # the socket filename carries the pill token, so a planted link at
    # the cache level hands pill control to whoever lists the victim
    # dir (recover the token from the socket name, then hide/show/move/
    # label at will). The runner must refuse outright if $NEST/cache is
    # a symlink before mkdir -p, same pattern as FRAMES. Behavioral
    # proof with the real lines, plus the old-lines hijack proof with
    # the real indicator.listen/serve.
    text = runner_text()
    guard = 'if [ -L "$NEST/cache" ]; then fail "NEST/cache $NEST/cache is a symlink; refusing to run'
    assert guard in text, "runner lacks the NEST/cache symlink check"
    mkdir_line = 'mkdir -p "$RUN_DIR" "$FRAMES" "$NEST/cache"'
    assert mkdir_line in text, "runner lacks the cache mkdir"
    assert text.index(guard) < text.index(mkdir_line), (
        "NEST/cache symlink check must sit before the mkdir -p")
    fail_line = 'fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }'
    wanted = [line for line in text.splitlines()
              if line.startswith('if [ -L "$NEST/cache" ]; then fail')
              or line.strip() == mkdir_line]
    assert len(wanted) == 2, (
        "expected cache check + mkdir in file order, got %d: %s"
        % (len(wanted), wanted))
    with tempfile.TemporaryDirectory() as tmp:
        nest = Path(tmp) / "nest"
        nest.mkdir()
        victim_dir = Path(tmp) / "victim-dir"
        victim_dir.mkdir()
        victim_file = victim_dir / "keep.txt"
        victim_file.write_text("VICTIM-CACHE-DATA-DO-NOT-TOUCH\n")
        link = nest / "cache"
        os.symlink(victim_dir, link, target_is_directory=True)
        script = Path(tmp) / "cache-guard-link.sh"
        script.write_text("\n".join([
            "set -u",
            fail_line,
            'NEST="' + str(nest) + '"',
            'RUN_DIR="' + str(nest / "run") + '"',
            'FRAMES="' + str(nest / "frames-x") + '"',
        ] + wanted) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 1, (
            "symlinked NEST/cache did not refuse: rc=%d %s%s"
            % (proc.returncode, proc.stdout, proc.stderr))
        assert "refusing to run" in proc.stdout, (
            "symlinked NEST/cache refusal message missing: " + proc.stdout)
        assert victim_file.read_text() == "VICTIM-CACHE-DATA-DO-NOT-TOUCH\n", (
            "cache guard wrote into the victim dir")
        assert sorted(p.name for p in victim_dir.iterdir()) == ["keep.txt"], (
            "victim dir gained a file: " + str(list(victim_dir.iterdir())))
        plain_nest = Path(tmp) / "nest-plain"
        plain_nest.mkdir()
        script2 = Path(tmp) / "cache-guard-plain.sh"
        script2.write_text("\n".join([
            "set -u",
            fail_line,
            'NEST="' + str(plain_nest) + '"',
            'RUN_DIR="' + str(plain_nest / "run") + '"',
            'FRAMES="' + str(plain_nest / "frames-x") + '"',
        ] + wanted) + "\n")
        proc2 = subprocess.run(["bash", str(script2)], capture_output=True,
                               text=True, timeout=30)
        assert proc2.returncode == 0, (
            "plain NEST/cache path did not pass: rc=%d %s%s"
            % (proc2.returncode, proc2.stdout, proc2.stderr))
        plain_cache = plain_nest / "cache"
        assert plain_cache.is_dir() and not plain_cache.is_symlink(), (
            "plain NEST/cache dir was not created as a regular dir")
    # Old lines (mkdir only, no guard): the pill socket lands in the
    # victim dir and hide answers with the recovered token.
    with tempfile.TemporaryDirectory() as tmp:
        nest = Path(tmp) / "nest"
        nest.mkdir()
        victim_dir = Path(tmp) / "victim-dir"
        victim_dir.mkdir()
        victim_file = victim_dir / "keep.txt"
        victim_file.write_text("VICTIM-CACHE-DATA-DO-NOT-TOUCH\n")
        os.symlink(victim_dir, nest / "cache", target_is_directory=True)
        script = Path(tmp) / "cache-old-lines.sh"
        script.write_text("\n".join([
            "set -u",
            fail_line,
            'NEST="' + str(nest) + '"',
            'RUN_DIR="' + str(nest / "run") + '"',
            'FRAMES="' + str(nest / "frames-x") + '"',
            mkdir_line,
        ]) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 0, (
            "old mkdir rc=%d %s%s" % (proc.returncode, proc.stdout, proc.stderr))
        reply = _hijack_pill_socket(nest / "cache" / "agent-computer-use")
        assert reply == "hidden", (
            "old lines did not hand over pill control: reply=%r" % reply)
        assert (victim_dir / "agent-computer-use").is_dir(), (
            "pill socket dir did not land in the victim dir")
        assert victim_file.read_text() == "VICTIM-CACHE-DATA-DO-NOT-TOUCH\n"


def test_nest_cache_agent_dir_symlink_guard():
    # R8-1 inner level: $NEST/cache may be a real dir while
    # $NEST/cache/agent-computer-use inside it is a planted symlink, and
    # the pill's STATE_DIR.mkdir(parents=True) follows it, so the socket
    # still lands in the victim dir. The runner must refuse outright if
    # the inner dir is a symlink before mkdir -p, same pattern as the
    # cache level. Behavioral proof with the real lines, plus the
    # old-lines hijack proof with the real indicator.listen/serve.
    text = runner_text()
    guard = 'if [ -L "$NEST/cache/agent-computer-use" ]; then fail "NEST/cache/agent-computer-use $NEST/cache/agent-computer-use is a symlink; refusing to run'
    assert guard in text, "runner lacks the agent-computer-use symlink check"
    mkdir_line = 'mkdir -p "$RUN_DIR" "$FRAMES" "$NEST/cache"'
    assert mkdir_line in text, "runner lacks the cache mkdir"
    assert text.index(guard) < text.index(mkdir_line), (
        "agent-computer-use symlink check must sit before the mkdir -p")
    fail_line = 'fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }'
    wanted = [line for line in text.splitlines()
              if line.startswith('if [ -L "$NEST/cache/agent-computer-use" ]; then fail')
              or line.strip() == mkdir_line]
    assert len(wanted) == 2, (
        "expected agent dir check + mkdir in file order, got %d: %s"
        % (len(wanted), wanted))
    with tempfile.TemporaryDirectory() as tmp:
        nest = Path(tmp) / "nest"
        cache = nest / "cache"
        cache.mkdir(parents=True)
        victim_dir = Path(tmp) / "victim-dir"
        victim_dir.mkdir()
        victim_file = victim_dir / "keep.txt"
        victim_file.write_text("VICTIM-CACHE-DATA-DO-NOT-TOUCH\n")
        link = cache / "agent-computer-use"
        os.symlink(victim_dir, link, target_is_directory=True)
        script = Path(tmp) / "agent-dir-guard-link.sh"
        script.write_text("\n".join([
            "set -u",
            fail_line,
            'NEST="' + str(nest) + '"',
            'RUN_DIR="' + str(nest / "run") + '"',
            'FRAMES="' + str(nest / "frames-x") + '"',
        ] + wanted) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 1, (
            "symlinked agent-computer-use did not refuse: rc=%d %s%s"
            % (proc.returncode, proc.stdout, proc.stderr))
        assert "refusing to run" in proc.stdout, (
            "symlinked agent-computer-use refusal message missing: " + proc.stdout)
        assert victim_file.read_text() == "VICTIM-CACHE-DATA-DO-NOT-TOUCH\n", (
            "agent dir guard wrote into the victim dir")
        assert sorted(p.name for p in victim_dir.iterdir()) == ["keep.txt"], (
            "victim dir gained a file: " + str(list(victim_dir.iterdir())))
        plain_nest = Path(tmp) / "nest-plain"
        plain_cache = plain_nest / "cache"
        plain_cache.mkdir(parents=True)
        script2 = Path(tmp) / "agent-dir-guard-plain.sh"
        script2.write_text("\n".join([
            "set -u",
            fail_line,
            'NEST="' + str(plain_nest) + '"',
            'RUN_DIR="' + str(plain_nest / "run") + '"',
            'FRAMES="' + str(plain_nest / "frames-x") + '"',
        ] + wanted) + "\n")
        proc2 = subprocess.run(["bash", str(script2)], capture_output=True,
                               text=True, timeout=30)
        assert proc2.returncode == 0, (
            "plain cache path did not pass: rc=%d %s%s"
            % (proc2.returncode, proc2.stdout, proc2.stderr))
        assert plain_cache.is_dir() and not plain_cache.is_symlink(), (
            "plain cache dir was not created as a regular dir")
    # Old lines (mkdir only, no guard): the pill socket lands in the
    # victim dir and hide answers with the recovered token.
    with tempfile.TemporaryDirectory() as tmp:
        nest = Path(tmp) / "nest"
        cache = nest / "cache"
        cache.mkdir(parents=True)
        victim_dir = Path(tmp) / "victim-dir"
        victim_dir.mkdir()
        victim_file = victim_dir / "keep.txt"
        victim_file.write_text("VICTIM-CACHE-DATA-DO-NOT-TOUCH\n")
        os.symlink(victim_dir, cache / "agent-computer-use", target_is_directory=True)
        script = Path(tmp) / "agent-dir-old-lines.sh"
        script.write_text("\n".join([
            "set -u",
            fail_line,
            'NEST="' + str(nest) + '"',
            'RUN_DIR="' + str(nest / "run") + '"',
            'FRAMES="' + str(nest / "frames-x") + '"',
            mkdir_line,
        ]) + "\n")
        proc = subprocess.run(["bash", str(script)], capture_output=True,
                              text=True, timeout=30)
        assert proc.returncode == 0, (
            "old mkdir rc=%d %s%s" % (proc.returncode, proc.stdout, proc.stderr))
        reply = _hijack_pill_socket(cache / "agent-computer-use")
        assert reply == "hidden", (
            "old lines did not hand over pill control: reply=%r" % reply)
        assert any(p.name.startswith("indicator-") and p.name.endswith(".sock")
                   for p in victim_dir.iterdir()), (
            "pill socket did not land in the victim dir")
        assert victim_file.read_text() == "VICTIM-CACHE-DATA-DO-NOT-TOUCH\n"


def test_teardown_marker_warn():
    # B2-3, 4d: teardown copies the marker file out BEFORE rm -rf, and a
    # missing marker file at teardown warns, it does not fail and it does
    # not stay silent.
    text = runner_text()
    copy_at = text.index("profile marker file saved to")
    warn_at = text.index("WARN: profile marker file missing at teardown")
    rm_at = text.index('rm -rf "$RUN_DIR"')
    assert copy_at < rm_at, "teardown must copy the marker file out before rm -rf"
    assert warn_at < rm_at, "teardown missing-marker warning must sit before rm -rf"
    assert text.index("profile marker file copy failed") < rm_at, (
        "teardown copy-failure warning must sit before rm -rf")


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
    assert "$NEST_LOG" in block, "A2 gate must still read the live per-instance log for parse-1 + corroboration"
    for line in block.splitlines():
        if line.strip().startswith("#"):
            continue
        assert "hypr-saved" not in line, (
            "A2 gate code must not read a saved-log directory: " + line)
        # No log grep may decide the gate on the applied marker. The only
        # log greps for Y6-NEST-OPTICS: applied allowed are corroboration
        # output (piped to head, never a pass/fail condition).
        if "grep" in line and "Y6-NEST-OPTICS: applied" in line and (
                "$LOG" in line or "$NEST_LOG" in line):
            assert "| head -3" in line, (
                "log grep for the applied marker must be corroboration output only: " + line)
            assert "if " not in line and "GATE_OK" not in line, (
                "log grep for the applied marker must not decide the gate: " + line)


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
        ("A2 gate exec healthy (marker file)", test_a2_gate_exec_healthy_file),
        ("A2 gate exec no marker fails", test_a2_gate_exec_no_marker_fails),
        ("A2 gate exec layers false fails", test_a2_gate_exec_layers_false_fails),
        ("A2 gate exec layers stale pre-gate passes", test_a2_gate_exec_layers_stale_pre_gate_passes),
        ("A2 gate exec layers after false fails", test_a2_gate_exec_layers_after_false_fails),
        ("A2 gate exec log corroboration echo", test_a2_gate_exec_log_corroboration_echo),
        ("A2 gate exec optics-only fails", test_a2_gate_exec_optics_only_fails),
        ("A2 gate exec hook-only fails", test_a2_gate_exec_hook_only_fails),
        ("A2 gate exec one-line both markers fails", test_a2_gate_exec_one_line_both_markers_fails),
        ("A2 gate exec second G4 fails", test_a2_gate_exec_g4_second_fails),
        ("A2 gate exec parse-1 expected", test_a2_gate_exec_parse1_expected),
        ("A6 G4 exec empty passes", test_a6_g4_exec_empty_passes),
        ("A6 G4 exec errors fail", test_a6_g4_exec_errors_fail),
        ("G4 before A2", test_g4_before_a2),
        ("G4 second after marker", test_g4_second_after_marker),
        ("RUN_DIR symlink guard", test_run_dir_symlink_guard),
        ("symlink guard exec early", test_symlink_guard_exec_early),
        ("fixed-name version file guard", test_fixed_name_version_file_guard),
        ("lock symlink guard", test_lock_symlink_guard),
        ("lock parent dir symlink guard", test_lock_parent_dir_symlink_guard),
        ("lock grandparent symlink guard", test_lock_grandparent_symlink_guard),
        ("nest fixed-name cleanup", test_nest_fixed_name_cleanup),
        ("run-log symlink guard", test_run_log_symlink_guard),
        ("teardown copy destination guard", test_teardown_cp_dest_guard),
        ("FRAMES symlink guard", test_frames_symlink_guard),
        ("nest cache symlink guard", test_nest_cache_symlink_guard),
        ("nest cache agent dir symlink guard", test_nest_cache_agent_dir_symlink_guard),
        ("teardown lock-free check symlink guard", test_teardown_lock_free_check_symlink_guard),
        ("teardown marker warn", test_teardown_marker_warn),
        ("A3 markers", test_a3_markers),
        ("A5 present", test_a5_present),
        ("A6 present", test_a6_present),
        ("A7 no reload", test_a7_no_reload),
        ("A7 reload wording", test_a7_reload_wording),
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
