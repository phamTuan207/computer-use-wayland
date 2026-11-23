#!/usr/bin/env python3
"""Layer-2 preflight probe driver (W-A1FIX, F4).

Runs the probes in tests/realistic/a1-pilot/preflight-probe.md live on
the agent Chromium (127.0.0.1:9223, workspace 2) through the code-exec
path, one interactive one-shot session per probe, P1 then P2 as two
sequential submits over the same session stdin. P1 and P2 MUST share
one session: each dom_start() closes prior browser-start contexts, so
a fresh session per submit would close P1's tab before P2 can read
it, and P2 would see a pristine fixture instead of P1's effects
(a false zero-effect verdict). The session stays open across the two
submits; it ends when stdin closes.

Mechanism (S2 flip pattern): CU_CODE_EXEC=1 on the one-shot
session-driver command line only, because the relay was started
without the flag and the broker cannot set env per request (F3
defect, fixed separately by a relay restart).

Adaptations to the probe programs as written in preflight-probe.md,
recorded, none of them a design change (no threshold, case, cap,
fixture, run order, or checker change):
- Every dom_act action carries "scope": tab["id"] and
  "observation_id": snap["snapshot"], and every desktop act action
  carries "scope": obs["scope"] and "observation_id": obs["id"].
  Without them the adapter refuses the batch with a CB-2 sandbox
  error ("action 0 is missing scope") before the bad-ref preflight
  is ever reached, so the probe as written cannot run on the current
  adapter: the desktop act fails first (api_calls 3), and the dom_act
  would fail next. The Case B program itself must carry the same
  fields (step 7 P2). Probe intent, bad ref, and expected outcome
  are unchanged. Finding for COORD-CLICK-6: the frozen runbook's
  template navigate act (section 5, step 2) shows the same unstamped
  shape, so the executor would hit the same CB-2 refusal at run 1;
  a pre-run-1 runbook amendment stamping the template is owed
  (amendments before run 1 are free).
- Each P2 program ends with a desktop observe plus prints of the
  observed window title/address and the verify image path, so the
  probe directory gets a real verify.png for the checker
  cross-check. The assertions themselves are unchanged.
- Each P1 program prints the navigate act result and retries the
  navigate act once (fresh observe, re-act) when the first act
  returns ok:false. The navigate act is flaky (3 of 5 P1s failed
  on it in the first full run, 18:09:16-18:09:41 +07, while the
  same act passed in the single-probe run minutes earlier): a
  setup failure, re-run after the setup is fixed, never recorded
  as a probe result. The retry changes no assertion and no batch.
- Each P1 and P2 prints its tab id; the driver requires P1 and P2
  to read the SAME tab. P2 looks its tab up by the exact target id
  P1 printed, never by URL: one-shot session contexts leak across
  sessions, so a stale tab from an earlier probe could otherwise
  satisfy a URL lookup and fake a zero-effect verdict. A P2 that
  reads a different tab than its P1 fails the probe. Tabs are never
  closed with CDP /json/close: closing a fixture tab that way
  preceded the agent Chromium exiting at 18:11:22 +07 on 22/11
  (systemd scope end, no crash report, no OOM), and the browser
  had to be relaunched via the chromium-intel wrapper (PID 56452,
  class chromium, 9223, mochi's chat tab did NOT restore). The
  relaunch is recorded in the W-A1FIX log, section F4.
- The driver focuses the agent Chromium window (hyprctl hl.dsp.focus
  on the class-chromium window, verified active) immediately before
  each probe session. The navigate act failed about 40 percent of
  P1s across the first runs (18:09-18:19 +07) with 'type verification
  failed: input line unchanged after typing', first act and
  in-program retry alike: keystrokes land nowhere when the window
  lacks focus, so the frame never changes. Focusing is harness
  setup, not a probe change: the runbook already requires the
  desktop verified before run 1. Focus is contended while mei works
  live in Brave on the same workspace (18:20:11 +07: active was
  Brave, not Chromium), so focus retries up to 3 times.
- New-tab-only (W-F4FIX, rule 18:23): every P1 opens a NEW tab with
  Ctrl+T as the first action of the navigate act, then navigates
  THAT tab; no existing tab is ever navigated. The tab is picked by
  id-diff (URL matches, id not in the before list taken right after
  dom_start), so a stale fixture tab from an earlier probe can never
  satisfy the lookup. The navigate retry reuses the new tab (no
  second Ctrl+T). At the end of the run the operator closes ONLY the
  tabs this run opened, by their exact tab ids from the summary,
  verifying after each close that 9223 still answers and every
  pre-existing tab is still listed; Chromium is never restarted.
- Pill (W-F4FIX, rule 18:30): this driver runs every probe inside a
  real computer-use session (cu.py session plus session-driver
  relay). The session guardian (scripts/cursor_session.py) creates
  the indicator pill before the driver starts and fails the session
  outright when the pill cannot appear (hyprglass gate, indicator
  loss monitoring), so all browser writes inside a probe happen
  under a visible pill. This is not raw CDP: no probe input runs
  outside a session.
- Probe 5 finding (18:20:48 +07, adapter defect, NOT a setup
  failure): the first dom_act's failed assert returns
  {ok:false, completed:0, error:'assertion failed'} from cdp.mjs,
  and browser_worker.py closes the browser worker on ANY ok:false
  response, so the retry branch's dom_observe dies with 'browser
  worker ended; stop this task' and the shared session's P2 dies
  the same way at its first browser call. In-program retry after a
  failed dom_act is therefore impossible on the current adapter,
  which also breaks the runbook section 5 step 2 template rule
  (retry inside the program after ok:false). STOP-FIX-REPROBE
  applies: fix the adapter (worker survives a failed assert) or
  amend the runbook (retry only via a recovery call in a fresh
  program, never in-program). That decision is COORD-CLICK-6's.
  --program P2 --tab <id> re-runs a P2 alone in a fresh session
  (fresh worker) to read the actual state after a failed P1
  without the shared-session artifact. The probe-5 end state
  written to the probe dir follows the ACTUAL outcome: pick4-ok
  only when the retry genuinely landed, else 'not clicked yet'.

Usage (from the VM):
  python3 tests/realistic/a1-pilot/run_preflight_probes.py \
    --out /tmp/a1fix-preflight
  python3 tests/realistic/a1-pilot/run_preflight_probes.py \
    --probe click --out /tmp/a1fix-preflight
  python3 tests/realistic/a1-pilot/run_preflight_probes.py \
    --probe retry-logging --program P2 --tab 025266AE11C86425817A3AF6E0FB7B26
Stdout prints one JSON line per submit plus a final summary JSON.
The probe log (preflight-log.jsonl) and per-probe directories
(end-state.json, run-log.jsonl, verify.png) are written under
/tmp/a1-pilot-20261121/runs/preflight/ on the LAPTOP by remote
commands, so the checker cross-check runs there.

Exit: 0 all probes match the hand-verified expectation, 1 a probe
mismatches (STOP, FIX THE ADAPTER, RE-PROBE), 3 infra error.
No em dash or en dash in this file.
"""

import argparse
import json
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SSH = str(REPO / 'scripts' / 'ssh-laptop-mux.sh')
LAPTOP_CU = '~/computer-use-wayland/scripts/cu.py'
ENDPOINT = 'http://127.0.0.1:9223'
PICK4_URL = 'http://127.0.0.1:8768/pick4-fixture.html'
F01_URL = 'http://127.0.0.1:8768/test-01-spreadsheet.html'
REMOTE_BASE = '/tmp/a1-pilot-20261121/runs/preflight'
REMOTE_CMD = ('CU_CODE_EXEC=1 python3 %s session -- python3 %s session-driver'
              % (LAPTOP_CU, LAPTOP_CU))

# Scope stamp applied to every dom_act action (CB-2 / step 7 P2).
SCOPE = ', "scope": tab["id"], "observation_id": snap["snapshot"]'


def scoped(action_json):
    """Insert scope + observation_id into one dom_act action literal."""
    assert action_json.rstrip().endswith('}'), action_json
    return action_json.rstrip()[:-1] + SCOPE + '}'


def p1_head(url):
    """Shared P1 head, new-tab-only (rule 18:23, W-F4FIX).

    The navigate act opens a NEW tab with Ctrl+T first, then Ctrl+L
    plus type navigates THAT tab; no existing tab is ever navigated.
    The tab is picked by id-diff (its URL matches and its id was not
    in the before list), so a stale fixture tab from an earlier probe
    can never satisfy the lookup. The navigate retry reuses the new
    tab (no second Ctrl+T)."""
    return (
        'started = dom_start()\n'
        'assert_state(started["ok"], "dom start failed")\n'
        'before = [t["id"] for t in dom_tabs()]\n'
        'wins = windows()\n'
        'chrome = [w for w in wins if w["class"] == "chromium"][0]\n'
        'obs = observe(window=chrome["address"])\n'
        'result = act([{"type": "key", "keys": ["ctrl", "t"], "scope": obs["scope"], "observation_id": obs["id"]}, {"type": "key", "keys": ["ctrl", "l"], "scope": obs["scope"], "observation_id": obs["id"]}, {"type": "type", "text": "' + url + '\\n", "scope": obs["scope"], "observation_id": obs["id"]}], obs)\n'
        'print("navigate act ok", result.get("ok"), "error", result.get("error"))\n'
        'if not result["ok"]:\n'
        '    obs = observe(window=chrome["address"])\n'
        '    result = act([{"type": "key", "keys": ["ctrl", "l"], "scope": obs["scope"], "observation_id": obs["id"]}, {"type": "type", "text": "' + url + '\\n", "scope": obs["scope"], "observation_id": obs["id"]}], obs)\n'
        '    print("navigate retry ok", result.get("ok"), "error", result.get("error"))\n'
        'assert_state(result["ok"], "navigate act failed")\n'
        'tabs = dom_tabs()\n'
        'tab = [t for t in tabs if t["url"] == "' + url + '" and t["id"] not in before][0]\n'
        'print("tab id", tab["id"])\n'
    )


def p1_click():
    return (
        p1_head(PICK4_URL) +
        'snap = dom_observe(tab["id"])\n'
        'btn = [e for e in snap["elements"] if e["name"] == "Show result"][0]\n'
        'clicked = dom_act(snap, [' + scoped('{"type": "click", "ref": btn["ref"]}') + ', ' + scoped('{"type": "click", "ref": "bad-ref-mid-list"}') + ', ' + scoped('{"type": "click", "ref": btn["ref"]}') + '])\n'
        'print("dom_act ok", clicked.get("ok"), "completed", clicked.get("completed"), "error", clicked.get("error"))\n'
    )


def p1_fill(action_type):
    return (
        p1_head(F01_URL) +
        'snap = dom_observe(tab["id"])\n'
        'typed = [e for e in snap["elements"] if e["role"] in ("textbox", "input")][0]\n'
        'cell = [e for e in snap["elements"] if e["name"] == "A2"][0]\n'
        'filled = dom_act(snap, ['
        + scoped('{"type": "click", "ref": cell["ref"]}') + ', '
        + scoped('{"type": "' + action_type + '", "ref": typed["ref"], "text": "2026-11-16"}') + ', '
        + scoped('{"type": "' + action_type + '", "ref": "bad-ref-mid-list", "text": "Widget"}') + ', '
        + scoped('{"type": "' + action_type + '", "ref": typed["ref"], "text": "12"}') + '])\n'
        'print("dom_act ok", filled.get("ok"), "completed", filled.get("completed"), "error", filled.get("error"))\n'
    )


def p1_assert():
    return (
        p1_head(PICK4_URL) +
        'snap = dom_observe(tab["id"])\n'
        'btn = [e for e in snap["elements"] if e["name"] == "Show result"][0]\n'
        'checked = dom_act(snap, [' + scoped('{"type": "click", "ref": btn["ref"]}') + ', ' + scoped('{"type": "assert", "ref": "bad-ref-mid-list", "text": "pick4-ok"}') + ', ' + scoped('{"type": "click", "ref": btn["ref"]}') + '])\n'
        'print("dom_act ok", checked.get("ok"), "completed", checked.get("completed"), "error", checked.get("error"))\n'
    )


def p1_retry():
    return (
        p1_head(PICK4_URL) +
        'snap = dom_observe(tab["id"])\n'
        'btn = [e for e in snap["elements"] if e["name"] == "Show result"][0]\n'
        'first = dom_act(snap, [' + scoped('{"type": "assert", "selector": "#result", "text": "pick4-ok"}') + '])\n'
        'print("first dom_act ok", first.get("ok"), "completed", first.get("completed"))\n'
        'if not first["ok"]:\n'
        '    snap = dom_observe(tab["id"])\n'
        '    btn = [e for e in snap["elements"] if e["name"] == "Show result"][0]\n'
        '    clicked = dom_act(snap, [' + scoped('{"type": "click", "ref": btn["ref"]}') + '])\n'
        '    print("retry dom_act ok", clicked.get("ok"), "completed", clicked.get("completed"))\n'
        '    assert_state(clicked["ok"], "retry click failed")\n'
        '    dom_assert(clicked["after"], selector="#result", text="pick4-ok")\n'
        '    print("retry confirmed pick4-ok")\n'
    )


def shot_block():
    """End-of-P2 desktop observe: proves the shot window and yields verify.png."""
    return (
        'wins = windows()\n'
        'chrome = [w for w in wins if w["class"] == "chromium"][0]\n'
        'print("shot window", chrome.get("title"), chrome.get("address"))\n'
        'shot = observe(window=chrome["address"])\n'
        'print("verify_image", shot.get("image"))\n'
    )


def p2_pick4(tab_id):
    return (
        'tabs = dom_tabs()\n'
        'tab = [t for t in tabs if t["id"] == "' + tab_id + '"][0]\n'
        'print("tab id", tab["id"])\n'
        'snap = dom_observe(tab["id"])\n'
        'dom_assert(snap, selector="#result", text="not clicked yet")\n'
        'print("p2 assert passed: #result still not clicked yet")\n'
        + shot_block()
    )


def p2_f01(tab_id):
    return (
        'tabs = dom_tabs()\n'
        'tab = [t for t in tabs if t["id"] == "' + tab_id + '"][0]\n'
        'print("tab id", tab["id"])\n'
        'snap = dom_observe(tab["id"])\n'
        'dom_assert(snap, selector="#a2", text="-")\n'
        'print("p2 assert passed: #a2 still -")\n'
        + shot_block()
    )


def p2_retry(tab_id):
    return (
        'tabs = dom_tabs()\n'
        'tab = [t for t in tabs if t["id"] == "' + tab_id + '"][0]\n'
        'print("tab id", tab["id"])\n'
        'snap = dom_observe(tab["id"])\n'
        'dom_assert(snap, selector="#result", text="pick4-ok")\n'
        'print("p2 assert passed: #result contains pick4-ok")\n'
        + shot_block()
    )


# probe id, fixture, P1, P2, expected P1 error substring, expected P2 effect
PROBES = [
    ('click', 'pick4', p1_click(), p2_pick4, 'not present in the bound snapshot', False),
    ('fill', 'f01', p1_fill('fill'), p2_f01, 'not present in the bound snapshot', False),
    ('set_value', 'f01', p1_fill('set_value'), p2_f01, 'not present in the bound snapshot', False),
    ('assert', 'pick4', p1_assert(), p2_pick4, 'not present in the bound snapshot', False),
    ('retry-logging', 'pick4', p1_retry(), p2_retry, None, True),
]

# Hand-verified checker expectation per probe dir (Stage 1 blind verdict):
# probes 1-4 prove zero effect, so the task is NOT complete: FAIL.
# Probe 5 proves the retry click landed: PASS.
EXPECTED_STAGE1 = {
    'click': False, 'fill': False, 'set_value': False, 'assert': False,
    'retry-logging': True,
}

END_STATE = {
    'click': {'result_text': 'not clicked yet'},
    'fill': {'a2': '-'},
    'set_value': {'a2': '-'},
    'assert': {'result_text': 'not clicked yet'},
    # Exact text grounded in the F2 mouse selftest (18:00:44 +07):
    # a real click on this fixture sets #result to this string.
    'retry-logging': {'result_text': 'pick4-ok hello stranger'},
}


class Session:
    """One interactive one-shot session-driver over mux SSH.

    Stdout is read by a dedicated thread into a queue: mixing select
    with a buffered readline can strand a line already in the buffer
    while select reports no new data, which reads as a false timeout.
    """

    def __init__(self):
        self.proc = subprocess.Popen(
            [SSH, REMOTE_CMD], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1)
        self.lines = queue.Queue()
        self.stderr_lines = []
        self.out_thread = threading.Thread(target=self._drain_stdout, daemon=True)
        self.out_thread.start()
        self.err_thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self.err_thread.start()
        line = self._read_line(timeout=60)
        if line is None:
            raise RuntimeError('no ready line from session driver')
        try:
            ready = json.loads(line)
        except ValueError:
            raise RuntimeError('bad ready line: %s' % line[:200])
        if not ready.get('ok'):
            raise RuntimeError('driver not ready: %s' % line[:200])

    def _drain_stdout(self):
        try:
            for line in self.proc.stdout:
                self.lines.put(line)
        except Exception:
            pass

    def _drain_stderr(self):
        try:
            for line in self.proc.stderr:
                self.stderr_lines.append(line)
        except Exception:
            pass

    def _read_line(self, timeout):
        try:
            return self.lines.get(timeout=timeout)
        except queue.Empty:
            return None

    def submit(self, program, intent, timeout=120):
        line = json.dumps(
            {'args': ['code-exec', '--endpoint', ENDPOINT, '--program', '-',
                      '--intent', intent],
             'stdin': program, 'image_policy': 'auto'},
            ensure_ascii=False, separators=(',', ':')) + '\n'
        t0 = time.monotonic()
        self.proc.stdin.write(line)
        self.proc.stdin.flush()
        envelope = None
        extras = []
        while True:
            raw = self._read_line(timeout=max(1, timeout - (time.monotonic() - t0)))
            if raw is None:
                raise RuntimeError('timeout waiting for result of %s' % intent)
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except ValueError:
                extras.append(raw)
                continue
            if isinstance(obj, dict) and 'result' in obj:
                envelope = obj['result']
                break
            extras.append(raw)
        wall_ms = (time.monotonic() - t0) * 1000.0
        return wall_ms, envelope, extras

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=10)


def ssh_remote(remote_cmd, timeout=60):
    proc = subprocess.run([SSH, remote_cmd], capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def focus_chromium():
    """Focus the agent Chromium window via hyprctl and verify it is
    the active window. The navigate act is flaky without this step
    (about 40 percent of P1s failed 18:09-18:19 +07 with 'type
    verification failed: input line unchanged after typing', both
    the first act and the in-program retry): the keystrokes land
    nowhere when the window lacks focus, so the frame never changes
    and the act fails its verification. The error message itself
    prescribes checking focus before retrying. Returns the window
    address. Raises on failure."""
    rc, out, err = ssh_remote(
        'export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ | head -n1); '
        'hyprctl clients -j | python3 -c "import json,sys; '
        'cs=json.load(sys.stdin); '
        'print([c[\'address\'] for c in cs if c.get(\'class\')==\'chromium\'][0])"')
    if rc != 0:
        raise RuntimeError('chromium window lookup failed rc=%d: %s %s' % (rc, out[:200], err[:200]))
    address = out.strip().splitlines()[-1].strip()
    # Retry the focus up to 3 times: mei works live in Brave on the
    # same workspace and can re-take focus between our dispatch and
    # our check (seen 18:20:11 +07: active was Brave, not Chromium).
    # Focus is a contended resource while mei runs; one attempt is
    # not enough. The dispatch output is kept, never discarded.
    last_active = None
    last_out = ''
    for attempt in range(3):
        rc, out, err = ssh_remote(
            'export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ | head -n1); '
            'hyprctl dispatch \'hl.dsp.focus({ window = "address:%s" })\'; '
            'sleep 1; '
            'hyprctl activewindow -j | python3 -c "import json,sys; '
            'w=json.load(sys.stdin); print(w.get(\'address\'))"' % address)
        last_out = (out + err)[:300]
        if rc != 0:
            continue
        last_active = out.strip().splitlines()[-1].strip()
        if last_active == address:
            return address
        time.sleep(1)
    raise RuntimeError('chromium window did not gain focus in 3 tries: target %s active %s out %s' % (address, last_active, last_out))


def tab_id_from_log(log):
    """First 'tab id <id>' print in a program log, or None."""
    for entry in log or []:
        if isinstance(entry, str) and entry.startswith('tab id '):
            return entry[len('tab id '):].strip()
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--probe', default=None, help='run one probe id only')
    ap.add_argument('--program', default='both', choices=('P1', 'P2', 'both'),
                    help='run one program only (P2 needs --tab, fresh session)')
    ap.add_argument('--tab', default=None, help='tab id for --program P2')
    ap.add_argument('--out', default='/tmp/a1fix-preflight', help='local out dir (unused, log lives on laptop)')
    opts = ap.parse_args(argv)
    selected = [p for p in PROBES if opts.probe is None or p[0] == opts.probe]
    if opts.probe and not selected:
        print(json.dumps({'error': 'unknown probe %s' % opts.probe}))
        return 3
    run_p1 = opts.program in ('P1', 'both')
    run_p2 = opts.program in ('P2', 'both')
    if opts.program == 'P2' and not opts.tab:
        print(json.dumps({'error': '--tab required with --program P2'}))
        return 3
    rc, out, _ = ssh_remote('mkdir -p %s' % REMOTE_BASE)
    if rc != 0:
        print(json.dumps({'error': 'mkdir remote base failed', 'out': out[:300]}))
        return 3
    summary = []
    for probe_id, fixture, p1, p2_builder, expect_err, expect_effect in selected:
        t_probe = time.monotonic()
        # Focus the Chromium window before the session: the navigate
        # act fails its type verification when the window lacks focus.
        focused_address = focus_chromium()
        print(json.dumps({'focus': {'probe': probe_id, 'address': focused_address}}))
        env1 = env2 = None
        wall1 = wall2 = 0.0
        tab_for_p2 = opts.tab
        session = Session()
        try:
            if run_p1:
                wall1, env1, _ = session.submit(p1, 'a1fix-probe-%s-p1' % probe_id)
                tab_for_p2 = tab_id_from_log(env1.get('log') if env1 else None)
            if run_p2:
                if tab_for_p2 is None:
                    env2 = {'ok': False, 'error': 'skipped: no tab id for P2', 'api_calls': 0, 'log': []}
                else:
                    wall2, env2, _ = session.submit(
                        p2_builder(tab_for_p2), 'a1fix-probe-%s-p2' % probe_id)
        finally:
            session.close()
        recs = []
        if run_p1:
            rec1 = {
                'ts': time.strftime('%Y-%m-%dT%H:%M:%S+07:00', time.localtime()),
                'probe': probe_id, 'program': 'P1',
                'ok': bool(env1.get('ok')) if env1 else False,
                'error': (env1.get('error') if env1 else 'no envelope'),
                'dom_effect': None, 'retry_logged': None,
                'wall_ms': round(wall1, 1), 'api_calls': (env1.get('api_calls') if env1 else None),
                'log': (env1.get('log') if env1 else None),
            }
            if probe_id == 'retry-logging':
                logs = ' '.join(str(x) for x in (rec1['log'] or []))
                rec1['retry_logged'] = bool(rec1['ok']) and ('retry confirmed pick4-ok' in logs or 'retry dom_act ok True' in logs)
            recs.append(rec1)
        if run_p2:
            rec2 = {
                'ts': time.strftime('%Y-%m-%dT%H:%M:%S+07:00', time.localtime()),
                'probe': probe_id, 'program': 'P2',
                'ok': bool(env2.get('ok')) if env2 else False,
                'error': (env2.get('error') if env2 else 'no envelope'),
                'dom_effect': (expect_effect if rec2_ok(env2) else None),
                'retry_logged': None,
                'wall_ms': round(wall2, 1), 'api_calls': (env2.get('api_calls') if env2 else None),
                'log': (env2.get('log') if env2 else None),
            }
            recs.append(rec2)
        for rec in recs:
            print(json.dumps({'submit': rec}, ensure_ascii=False))
        # Ship the log line(s) to the laptop.
        log_lines = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in recs)
        b64 = __import__('base64').b64encode(log_lines.encode()).decode()
        rc, out, err = ssh_remote(
            'mkdir -p %s && echo %s | base64 -d >> %s/preflight-log.jsonl && echo APPENDED'
            % (REMOTE_BASE, b64, REMOTE_BASE))
        if rc != 0 or 'APPENDED' not in out:
            print(json.dumps({'error': 'append probe log failed', 'probe': probe_id, 'out': out[:200], 'err': err[:200]}))
            return 3
        if not (run_p1 and run_p2):
            # Single-program run: log line shipped, no probe dir,
            # no summary verdict. The caller judges the single line.
            continue
        p1_good = (not rec1['ok']) and expect_err is not None and expect_err in str(rec1['error'])
        if probe_id == 'retry-logging':
            p1_good = bool(rec1['retry_logged'])
        p2_good = rec2['ok'] and rec2['dom_effect'] == expect_effect
        tab1 = tab_id_from_log(rec1['log'])
        tab2 = tab_id_from_log(rec2['log'])
        same_tab = (tab1 is not None and tab1 == tab2)
        probe_ok = p1_good and p2_good and same_tab
        # Probe dir: end-state.json + run-log.jsonl + verify.png.
        verify_image = None
        for entry in (rec2['log'] or []):
            if isinstance(entry, str) and entry.startswith('verify_image '):
                verify_image = entry[len('verify_image '):].strip()
        dir_name = {'click': 'probe-1-click', 'fill': 'probe-2-fill',
                    'set_value': 'probe-3-set-value', 'assert': 'probe-4-assert',
                    'retry-logging': 'probe-5-retry-logging'}[probe_id]
        end_state_obj = END_STATE[probe_id]
        if probe_id == 'retry-logging' and not probe_ok:
            # The retry did not land (the first failed assert closed
            # the browser worker, 18:20:48 +07): the actual state is
            # still the unclicked one. Writing the expected pick4-ok
            # string here would fabricate a Stage 1 PASS for the
            # checker, so the end state follows the actual outcome.
            end_state_obj = {'result_text': 'not clicked yet'}
        end_state = json.dumps(end_state_obj, ensure_ascii=False)
        run_log = json.dumps({'op': 'run_start', 'ts': rec1['ts'], 'step_index': 0, 'progress_marker': True, 'detail': {'probe': probe_id, 'program': 'P1'}}) + '\n'
        run_log += json.dumps({'op': 'program_submit', 'ts': rec1['ts'], 'step_index': 1, 'progress_marker': True, 'detail': {'probe': probe_id, 'program': 'P1', 'ok': rec1['ok'], 'error': rec1['error']}}) + '\n'
        run_log += json.dumps({'op': 'program_submit', 'ts': rec2['ts'], 'step_index': 2, 'progress_marker': True, 'detail': {'probe': probe_id, 'program': 'P2', 'ok': rec2['ok'], 'error': rec2['error']}}) + '\n'
        run_log += json.dumps({'op': 'run_end', 'ts': rec2['ts'], 'step_index': 3, 'progress_marker': True, 'detail': {'probe': probe_id, 'verdict': 'pass' if probe_ok else 'fail'}}) + '\n'
        b64state = __import__('base64').b64encode(end_state.encode()).decode()
        b64log = __import__('base64').b64encode(run_log.encode()).decode()
        remote_dir = '%s/%s' % (REMOTE_BASE, dir_name)
        cmds = [
            'mkdir -p %s' % remote_dir,
            'echo %s | base64 -d > %s/end-state.json' % (b64state, remote_dir),
            'echo %s | base64 -d > %s/run-log.jsonl' % (b64log, remote_dir),
        ]
        if verify_image:
            cmds.append('cp %s %s/verify.png && ls -l %s/verify.png' % (verify_image, remote_dir, remote_dir))
        rc, out, err = ssh_remote(' && '.join(cmds))
        if rc != 0:
            print(json.dumps({'error': 'probe dir write failed', 'probe': probe_id, 'out': out[:300], 'err': err[:300]}))
            return 3
        summary.append({
            'probe': probe_id, 'fixture': fixture,
            'p1_ok': rec1['ok'], 'p1_error': rec1['error'],
            'p1_good': p1_good, 'p2_ok': rec2['ok'],
            'p2_dom_effect': rec2['dom_effect'], 'p2_good': p2_good,
            'p1_tab': tab1, 'p2_tab': tab2, 'same_tab': same_tab,
            'probe_ok': probe_ok,
            'expected_stage1': (EXPECTED_STAGE1[probe_id] if probe_id != 'retry-logging' else probe_ok),
            'verify_image': verify_image,
            'probe_ms': round((time.monotonic() - t_probe) * 1000, 1),
        })
    all_ok = all(s['probe_ok'] for s in summary)
    print(json.dumps({'summary': 'a1 preflight probes', 'all_ok': all_ok, 'probes': summary}, ensure_ascii=False))
    return 0 if all_ok else 1


def rec2_ok(env):
    return bool(env.get('ok')) if env else False


if __name__ == '__main__':
    raise SystemExit(main())
