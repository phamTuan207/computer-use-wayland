#!/usr/bin/env python3
"""Y6d C2 re-run (VM part), extended after adjudication: verdict logic 16/16,
v3 unit tests (discovery/gate/guard/ldd/pill-liveness/cleanup/env), static checks.

Extracts the exact blocks verbatim from
improvements/worker-y6b-run-nested-wayland-v2.sh and runs them against
controlled fixtures. Prints PASS/FAIL per case with the source line numbers.
Fixtures use LISTENING unix sockets: the v3 discovery connect probe skips
bound-but-not-listening sockets (a dead socket), so bind-only fixtures would
fail the probe by design.
"""
import os
import re
import socket
import subprocess
import sys
import tempfile
import time

RUNNER = os.path.expanduser(
    "~/workspace/computer-use-wayland/improvements/worker-y6b-run-nested-wayland-v2.sh")
CONF = os.path.expanduser(
    "~/workspace/computer-use-wayland/improvements/worker-y6b-hyprland-wayland-v2.lua")
lines = open(RUNNER).read().splitlines()
failures = []
sockets_keepalive = []


def find(marker, start=0):
    for i in range(start, len(lines)):
        if marker in lines[i]:
            return i
    raise SystemExit("marker not found: " + marker)


def extract(start_marker, end_marker, start=0):
    a = find(start_marker, start)
    b = find(end_marker, a)
    return a + 1, b + 1, "\n".join(lines[a:b + 1]) + "\n"


def run_bash(script, timeout=90):
    return subprocess.run(["bash", "-c", script], capture_output=True,
                          text=True, timeout=timeout)


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""))
    if not ok:
        failures.append(name)


def live_socket(d, name):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(os.path.join(d, name))
    s.listen(1)
    sockets_keepalive.append(s)
    return s


def dead_socket(d, name):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(os.path.join(d, name))
    s.close()


HDR = 'fail() { echo "FAIL: $1"; exit 1; }\n'

# --- 5. Verdict logic: all 16 (A_OUTCOME, B_OUTCOME) combos, exactly 1 VERDICT line
a, b, block = extract("# Verdict lines (U10, U11, U14)",
                     'echo "Y6-WAYLAND: done')
print(f"verdict block: lines {a}-{b}")
combos = ["negative", "reproduced", "inconclusive", "void"]
bad = 0
for av in combos:
    for bv in combos:
        harness = ("A_OUTCOME=%s; B_OUTCOME=%s; A_DIFF=0; A_BG_DIFF=0; "
                   "B_PILL_DIFF=0; B_BG_DIFF=0; B_PILL_ONLY=0\n" % (av, bv)) + block
        r = run_bash(harness)
        n = len([l for l in r.stdout.splitlines()
                 if l.startswith("Y6-WAYLAND: VERDICT:")])
        if n != 1 or r.returncode != 0:
            bad += 1
            print(f"  combo A={av} B={bv}: VERDICT lines={n} rc={r.returncode}")
check("verdict logic 16/16 combos exactly 1 VERDICT line", bad == 0,
      f"{16 - bad}/16 ok")

# --- 7a. Socket discovery block (now with the connect probe)
a, b, disc = extract("# Discover the nested Wayland socket name",
                    'echo "Y6-WAYLAND: nested socket $NEST_DISPLAY"')
print(f"discovery block: lines {a}-{b}")


def discovery_case(name, setup, want_display=None, want_fail=None):
    d = tempfile.mkdtemp(prefix="y6d-disc-")
    setup(d)
    script = HDR + f'RUN_DIR="{d}"\n' + disc
    t0 = time.monotonic()
    r = run_bash(script, timeout=60)
    el = time.monotonic() - t0
    if want_display is not None:
        ok = r.returncode == 0 and f"nested socket {want_display}" in r.stdout
        check("discovery: " + name, ok,
              f"rc={r.returncode} elapsed={el:.1f}s out={r.stdout.strip()[-80:]}")
    else:
        ok = r.returncode != 0 and want_fail in (r.stdout + r.stderr)
        check("discovery: " + name, ok,
              f"rc={r.returncode} elapsed={el:.1f}s out={r.stdout.strip()[-80:]}")


def one_socket(d):
    live_socket(d, "wayland-1")
    open(os.path.join(d, "wayland-1.lock"), "w").write("x")


def two_sockets(d):
    live_socket(d, "wayland-1")
    live_socket(d, "wayland-2")


def no_socket(d):
    pass


def dead_only(d):
    dead_socket(d, "wayland-1")
    open(os.path.join(d, "wayland-1.lock"), "w").write("x")


def dead_plus_live(d):
    dead_socket(d, "wayland-1")
    live_socket(d, "wayland-2")


def late_socket(d):
    import threading
    def bind_late():
        time.sleep(3)
        live_socket(d, "wayland-1")
    threading.Thread(target=bind_late, daemon=True).start()


discovery_case("one listening socket + lock file -> wayland-1", one_socket,
               want_display="wayland-1")
discovery_case("two listening sockets -> ambiguous fail", two_sockets,
               want_fail="ambiguous")
discovery_case("no socket -> missing fail", no_socket, want_fail="no nested Wayland socket")
discovery_case("dead socket only -> skipped, missing fail", dead_only,
               want_fail="no nested Wayland socket")
discovery_case("dead socket + live socket -> picks live", dead_plus_live,
               want_display="wayland-2")
discovery_case("socket appears at t=3 -> found", late_socket,
               want_display="wayland-1")

# --- 7b. Backend gate block (retry loop) + nest liveness check
a, b, gate = extract('[ -f "$NEST_LOG" ] || fail "nested per-instance log',
                    'fail "nested Hyprland died after backend start')
print(f"gate block: lines {a}-{b}")


def gate_case(name, setup, want_ok, want_fail=None):
    d = tempfile.mkdtemp(prefix="y6d-gate-")
    log = os.path.join(d, "hyprland.log")
    stdout_log = os.path.join(d, "stdout.log")
    open(stdout_log, "w").write("stdout tail line\n")
    proc = subprocess.Popen(["sleep", "60"])
    setup(d, log, proc.pid)
    script = (HDR + f'NEST_LOG="{log}"\nLOG="{stdout_log}"\n'
              f'NEST_HYPRLAND_PID={proc.pid}\n' + gate)
    t0 = time.monotonic()
    r = run_bash(script, timeout=60)
    el = time.monotonic() - t0
    proc.terminate()
    if want_ok:
        ok = r.returncode == 0
    else:
        ok = r.returncode != 0 and (want_fail is None or want_fail in (r.stdout + r.stderr))
    check("backend gate: " + name, ok, f"rc={r.returncode} elapsed={el:.1f}s")


def gate_present(d, log, pid):
    open(log, "w").write("xxx\nStarting the Wayland backend!\nyyy\n")


def gate_late(d, log, pid):
    import threading
    def write_late():
        time.sleep(6)
        open(log, "w").write("Starting the Wayland backend!\n")
    open(log, "w").write("starting...\n")
    threading.Thread(target=write_late, daemon=True).start()


def gate_absent(d, log, pid):
    open(log, "w").write("xxx\nno backend here\nyyy\n")


def gate_missing(d, log, pid):
    pass


def gate_dead_pid(d, log, pid):
    open(log, "w").write("Starting the Wayland backend!\n")


gate_case("line present + live pid -> pass", gate_present, True)
gate_case("line appears at t=6 -> pass via retry", gate_late, True)
gate_case("line absent -> fail with stdout tail", gate_absent, False,
          want_fail="Wayland backend did not start")
gate_case("log file missing -> fail fast", gate_missing, False,
          want_fail="per-instance log")
# dead-pid variant: run the same gate with a dead pid
d = tempfile.mkdtemp(prefix="y6d-gate-")
log = os.path.join(d, "hyprland.log")
open(log, "w").write("Starting the Wayland backend!\n")
open(os.path.join(d, "stdout.log"), "w").write("x\n")
script = (HDR + f'NEST_LOG="{log}"\nLOG="{d}/stdout.log"\n'
          'NEST_HYPRLAND_PID=999999\n' + gate)
r = run_bash(script, timeout=60)
check("backend gate: dead nest pid -> fail", r.returncode != 0
      and "died after backend start" in r.stdout, f"rc={r.returncode}")

# --- 7c. nest() guard: empty NEST_DISPLAY fails closed, set display runs
a = find("nest() {")
nest_def = lines[a]
print(f"nest() def: line {a + 1}")


def nest_case(name, display, want_ok):
    script = HDR + (f'RUN_DIR="/tmp"; SIG="sig"; NEST_DISPLAY="{display}"\n'
                    + nest_def + '\nnest true\n')
    r = run_bash(script, timeout=30)
    ok = (r.returncode == 0) if want_ok else (r.returncode != 0)
    check("nest() guard: " + name, ok, f"rc={r.returncode}")


nest_case("empty display -> fail closed", "", False)
nest_case("display set -> runs", "wayland-1", True)

# guard pre-check line before NEST_OUTPUT (council 1 A1)
pi = find('NEST_OUTPUT=$(nest')
precheck = lines[pi - 1]
print(f"guard pre-check line {pi}: {precheck.strip()[:80]}")
check("guard pre-check exists before NEST_OUTPUT",
      'NEST_DISPLAY' in precheck and 'fail "nest() called before socket discovery"' in precheck)
script = HDR + 'NEST_DISPLAY=""\n' + precheck + '\n'
r = run_bash(script, timeout=30)
check("guard pre-check: empty -> fail", r.returncode != 0, f"rc={r.returncode}")
script = HDR + 'NEST_DISPLAY="wayland-1"\n' + precheck + '\necho STILL-HERE\n'
r = run_bash(script, timeout=30)
check("guard pre-check: set -> continue", r.returncode == 0 and "STILL-HERE" in r.stdout,
      f"rc={r.returncode}")

# --- 7d. ldd pre-flight block
a, b, ldd_block = extract('command -v ldd >/dev/null || fail "ldd not found',
                          'echo "Y6-WAYLAND: plugin ABI OK')
print(f"ldd pre-flight block: lines {a}-{b}")


def ldd_case(name, conf_text, want_ok, want_fail=None):
    d = tempfile.mkdtemp(prefix="y6d-ldd-")
    conf = os.path.join(d, "conf.lua")
    open(conf, "w").write(conf_text)
    script = HDR + f'CONF="{conf}"\n' + ldd_block
    r = run_bash(script, timeout=30)
    if want_ok:
        ok = r.returncode == 0
    else:
        ok = r.returncode != 0 and (want_fail is None or want_fail in (r.stdout + r.stderr))
    check("ldd pre-flight: " + name, ok, f"rc={r.returncode} out={r.stdout.strip()[-120:]}")


good_link = "/tmp/y6d-good-hyprglass.so"
try:
    os.unlink(good_link)
except FileNotFoundError:
    pass
os.symlink("/lib/x86_64-linux-gnu/libc.so.6", good_link)
# Dead-ABI fixture: a .so whose NEEDED entry names libaquamarine.so.14,
# built against a stub lib that is then NOT on the loader path, so ldd
# reports it not found (the same shape as the laptop's backup 1 .so).
dead_so = "/tmp/y6d-dead-hyprglass.so"
stub_dir = "/tmp/y6d-stub"
os.makedirs(stub_dir, exist_ok=True)
open(os.path.join(stub_dir, "stub.c"), "w").write("int aquamarine_stub;\n")
subprocess.run(["gcc", "-shared", "-fPIC", "-o",
                os.path.join(stub_dir, "libaquamarine.so.14"),
                os.path.join(stub_dir, "stub.c")], check=True)
open("/tmp/y6d-dead.c", "w").write(
    "extern int aquamarine_stub;\nint get_it(void) { return aquamarine_stub; }\n")
subprocess.run(["gcc", "-shared", "-fPIC", "-o", dead_so, "/tmp/y6d-dead.c",
                "-L" + stub_dir, "-l:libaquamarine.so.14"], check=True)
dead_ldd = subprocess.run(["ldd", dead_so], capture_output=True, text=True)
print("dead fixture ldd:\n" + dead_ldd.stdout.strip())
ldd_case("dead ABI fixture (libaquamarine.so.14 not found) -> fail naming it",
         f'hl.plugin.load("{dead_so}")\n', False, want_fail="libaquamarine.so.14")
ldd_case("good .so (all deps resolve) -> pass",
         f'hl.plugin.load("{good_link}")\n', True)
ldd_case("conf with no hyprglass path -> fail", 'hl.monitor({})\n', False,
         want_fail="no hyprglass.so path")
ldd_case("conf path missing on disk -> fail",
         'hl.plugin.load("/tmp/y6d-no-such-hyprglass.so")\n', False,
         want_fail="missing on disk")

# --- 7e. Pill ready-wait liveness (redteam A2)
a = find('for i in $(seq 1 45); do sleep 1; kill -0 "$PILL_PID"')
wait_line = lines[a]
print(f"pill wait line: {a + 1}")


def pill_wait_case(name, pill_lifetime, ready_present, want_ok, want_fail=None):
    # The fake pill MUST be a child of the test bash (as the real pill is a
    # child of the launcher bash): bash reaps dead children between commands,
    # so kill -0 reports DEAD. A pill spawned by python would stay a zombie
    # of python and kill -0 would succeed for the whole 45s (fixture artifact).
    d = tempfile.mkdtemp(prefix="y6d-pill-")
    log = os.path.join(d, "nest-pill.log")
    if ready_present:
        open(log, "w").write("Y6-NEST-PILL: ready\n")
    else:
        open(log, "w").write("")
    script = (HDR + f'NEST="{d}"\nREADY=""\n'
              f'sleep {pill_lifetime} > /dev/null 2>&1 & PILL_PID=$!\n' + wait_line + '\n'
              '[ -n "$READY" ] || fail "pill did not become ready in 45s"\n')
    t0 = time.monotonic()
    r = run_bash(script, timeout=60)
    el = time.monotonic() - t0
    if want_ok:
        ok = r.returncode == 0
    else:
        ok = r.returncode != 0 and (want_fail is None or want_fail in (r.stdout + r.stderr))
    check("pill wait: " + name, ok, f"rc={r.returncode} elapsed={el:.1f}s")


pill_wait_case("pill dies at t=2 -> fail fast, not 45s", 2, False, False,
               want_fail="died during ready wait")
pill_wait_case("pill alive + ready line -> READY", 30, True, True)

# --- 7f. Stale cleanup block (redteam B4 / council 2 C1)
a, b, clean = extract('rm -rf "$RUN_DIR/hypr"', 'fi; done')
print(f"cleanup block: lines {a}-{b}")


def cleanup_case(name, setup, want_kept):
    d = tempfile.mkdtemp(prefix="y6d-clean-")
    run_dir = os.path.join(d, "run")
    os.makedirs(os.path.join(run_dir, "hypr"))
    setup(run_dir)
    script = HDR + f'RUN_DIR="{run_dir}"\n' + clean
    r = run_bash(script, timeout=30)
    kept = sorted(os.listdir(run_dir))
    ok = r.returncode == 0 and kept == want_kept
    check("cleanup: " + name, ok, f"rc={r.returncode} kept={kept}")


def dirty_setup(run_dir):
    live_socket(run_dir, "wayland-1")
    open(os.path.join(run_dir, "wayland-1.lock"), "w").write("x")
    open(os.path.join(run_dir, "wayland-2"), "w").write("x")
    open(os.path.join(run_dir, "keep.txt"), "w").write("x")
    os.symlink("/nonexistent-target", os.path.join(run_dir, "wayland-7"))


def empty_setup(run_dir):
    pass


cleanup_case("dirty dir -> only keep.txt remains", dirty_setup, ["keep.txt"])
cleanup_case("empty dir -> rc 0", empty_setup, [])

# --- 7g. Env propagation: the three WAYLAND_DISPLAY substitutions
def env_case(name, marker):
    li = find(marker)
    line = lines[li]
    prefix = line.split("mpv ")[0] if "mpv " in line else line.split("python3 ")[0]
    stub = ("python3 -c \"import os; "
            "print('DISP='+os.environ.get('WAYLAND_DISPLAY',''))\"\n")
    script = (HDR + 'RUN_DIR="/tmp"; SIG="fakesig"; NEST_DISPLAY="wayland-9"\n'
              'NEST="/tmp"; BACKDROP="/tmp/x"; PILL="/tmp/x"\n' + prefix + stub)
    r = run_bash(script, timeout=30)
    ok = r.returncode == 0 and "DISP=wayland-9" in r.stdout
    check("env propagation: " + name, ok, f"rc={r.returncode} out={r.stdout.strip()[-60:]}")


env_case("backdrop mpv launch", '--loop=inf --no-audio --fullscreen "$BACKDROP"')
env_case("pill launch", 'python3 "$PILL"')
env_case("start_mpv", 'mpv --loop=inf --no-audio --fullscreen "$1"')

# --- 7h. Pill display snippet (council 1 A2): missing/empty/set
pill_lines = open(os.path.expanduser(
    "~/workspace/computer-use-wayland/improvements/worker-y6b-run-nested-pill-v2.py")
    ).read().splitlines()
pi = next(i for i, l in enumerate(pill_lines)
          if l.startswith('_disp = os.environ["WAYLAND_DISPLAY"]'))
snippet = "\n".join(pill_lines[pi:pi + 3])
print(f"pill snippet lines {pi + 1}-{pi + 3}: {snippet.splitlines()[0][:60]}...")


def pill_snippet_case(name, env_setup, want_ok, want_fail=None):
    code = ("import os\n" + env_setup + "env = {}\n" + snippet + "\n"
            "print('DISP=' + env.get('WAYLAND_DISPLAY', 'MISSING'))\n")
    r = subprocess.run(["python3", "-c", code], capture_output=True, text=True,
                       timeout=30)
    if want_ok:
        ok = r.returncode == 0
    else:
        ok = r.returncode != 0 and (want_fail is None
                                     or want_fail in (r.stdout + r.stderr))
    check("pill snippet: " + name, ok,
          f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-100:]}")


pill_snippet_case("WAYLAND_DISPLAY missing -> KeyError",
                  "os.environ.pop('WAYLAND_DISPLAY', None)\n",
                  False, want_fail="KeyError")
pill_snippet_case("WAYLAND_DISPLAY empty -> SystemExit with message",
                  "os.environ['WAYLAND_DISPLAY'] = ''\n",
                  False, want_fail="WAYLAND_DISPLAY empty")
pill_snippet_case("WAYLAND_DISPLAY set -> env set",
                  "os.environ['WAYLAND_DISPLAY'] = 'wayland-1'\n",
                  True)

# --- 6. Static checks on the v3 runner
text = open(RUNNER).read()
check("no pkill -x on a shared process name (code, not comments)",
      not re.search(r"^[^#]*pkill -x", text, re.M))
check("no em/en dash in runner", "\u2014" not in text and "\u2013" not in text)
check("timeout 600 present", "timeout 600 Hyprland" in text)
check("no --socket flag in code (comments may document the removal)",
      not any("--socket" in l for l in text.splitlines()
              if l.strip() and not l.strip().startswith("#")))
check("no hardcoded wayland-y6 remains", "wayland-y6" not in text)
check("tee to timestamped run log", 'tee -a "$RUN_LOG"' in text)
check("timestamped frames dir", 'FRAMES=$NEST/frames-$START_TS' in text)
check("ldd pre-flight block present", "ldd" in text and "dead ABI" in text)
check("gate retry loop present", "BACKEND_OK" in text)
check("socket connect probe present", "connect_ex" in text)
check("pill liveness check present", 'kill -0 "$PILL_PID"' in text)

print()
if failures:
    print(f"RESULT: {len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("RESULT: all VM C2 checks PASS")
