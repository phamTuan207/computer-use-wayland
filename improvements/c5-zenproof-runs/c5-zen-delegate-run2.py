#!/usr/bin/env python3
"""Zen pointer delegate live proof, run 2 (W-ZENPROOF2, COORD-CLICK-9).

Runs the live proof per improvements/w-zen-delegate-liveproof-prep.md
section 5, phases 1-6, against the scratch fixture tab in Zen on
ws1. Run 1 (W-ZENPREP) aborted in phase 1 on the R13 gate (active
window was mochi Chromium, lanes live); it sent no input, so run 2
uses a fresh intent and message per G0d anyway. Reuses the step 9
harness transport (Harness.ssh over the mux) for laptop commands
and a oneshot session-driver for the code-exec program, with
CU_DOM_BACKEND=zen added to the remote command line. The program
itself is the Zen form from the prep file (not the CDP builder
output): dom_observe with a scope, ref on the key action.

No model calls. No input to any existing tab at any point. The only
send is the marked test message into the local file fixture. If any
gate fails, the run aborts (BLOCKED before input, FAIL after it) and
phase 6 cleanup still runs best-effort.

Usage (from the repo root on the VM):
  python3 improvements/c5-zenproof-runs/c5-zen-delegate-run2.py
Exit 0 only when outcome is 'sent'; anything else exits 1.
Result: /tmp/c5-zenproof-2/run-2.json plus p9-zen-r2.png.
"""
import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import s2_flip_live  # noqa: E402

RUN_NO = 2
MESSAGE = 'ZEN-DELEGATE-R2-IGNORE-TEST'
INTENT = 'c5-zen-delegate-r2'
# Fix (a): target the scratch tab by URL substring, never by
# document.title. The fixture title is the static 'Two-vision
# benchmark fixture'; its JS only sets the H1 text. The URL
# substring is what _resolve_target matches on (title/url/handle
# substring), and it is also the action scope, which must equal
# the dom_observe target. SCRATCH_H1 is a content confirmation
# read from the page, not a tab identity.
TARGET = 'two_vision_fixture.html?clone=zen'
SCRATCH_H1 = 'Clone zen thread'
SCOPE = '#msg-input'
BUBBLE_SELECTOR = '#thread .bubble:last-child'
FIXTURE_URL = ('file:///home/james/computer-use-wayland/tests/'
               'two_vision_fixture.html?clone=zen')
FIXTURE_SHA = ('147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6'
               'cbf')
WORKDIR = Path('/tmp/c5-zenproof-2')
LAPTOP_RUN = '/home/james/c5-zenproof-run'
LAPTOP_DRIVER = LAPTOP_RUN + '/zen-tab.py'
VM_DRIVER = (Path(__file__).resolve().parent / 'zen-tab.py')
SCP_OPTS = ['-o', 'BatchMode=yes', '-o', 'ConnectTimeout=25',
            '-o', 'StrictHostKeyChecking=accept-new',
            '-o', 'IdentitiesOnly=yes',
            '-o', 'ProxyCommand=python3 /home/hatch/workspace/'
                   'tailscale-proxy.py %h %p',
            '-i', '/home/hatch/.ssh/id_ed25519']
LAPTOP_HOST = 'james@100.70.92.52'

PROBE_PROGRAM = (
    "dom_start()\n"
    "snap = dom_observe('two_vision_fixture.html?clone=zen',"
    " '#msg-input', 80)\n"
    # PROBE line shape: PROBE <snapshot-id> <url> <count>. The URL
    # has no spaces, so the runner splits on whitespace. The title
    # is evidence only, on its own SNAP-TITLE line, never a gate:
    # the document title is the static fixture title.
    "print('PROBE', snap['snapshot'], snap.get('url'),"
    " len(snap.get('elements') or []))\n"
    "print('SNAP-TITLE', snap.get('title'))\n"
)

SEND_PROGRAM = (
    "dom_start()\n"
    "snap = dom_observe('two_vision_fixture.html?clone=zen',"
    " '#msg-input', 80)\n"
    "res = dom_act(snap, [\n"
    "    {\"type\": \"set_value\", \"ref\": \"#msg-input\", \"text\": \""
    + MESSAGE + "\", \"scope\": \"two_vision_fixture.html?clone=zen\","
    " \"observation_id\": snap[\"snapshot\"]},\n"
    "    {\"type\": \"focus\", \"ref\": \"#msg-input\", \"scope\":"
    " \"two_vision_fixture.html?clone=zen\","
    " \"observation_id\": snap[\"snapshot\"]},\n"
    "    {\"type\": \"key\", \"ref\": \"#msg-input\", \"keys\": [\"Enter\"],"
    " \"scope\": \"two_vision_fixture.html?clone=zen\","
    " \"observation_id\": snap[\"snapshot\"]},\n"
    "    {\"type\": \"assert\", \"selector\": \"#thread .bubble:last-child\","
    " \"text\": \"" + MESSAGE + "\", \"timeout_ms\": 3000,"
    " \"scope\": \"two_vision_fixture.html?clone=zen\","
    " \"observation_id\": snap[\"snapshot\"]},\n"
    "])\n"
    "print(\"dom_act ok\", res.get(\"ok\"), \"completed\","
    " res.get(\"completed\"), \"ms\", res.get(\"execution_ms\"),"
    " \"error\", res.get(\"error\"))\n"
    "assert_state(res.get(\"ok\") is True, \"dom_act failed\")\n"
)


def parse_probe_line(line, target):
    """Parse one PROBE line into (url, count), gating on the URL.

    Line shape: PROBE <snapshot-id> <url> <count>. Raises
    ValueError when the shape is wrong, the snapshot URL does
    not contain the fixture URL substring, or the element count
    is not 1. The document title is never parsed here: it is
    the static fixture title and cannot identify the tab.
    """
    parts = line.split()
    if len(parts) != 4 or parts[0] != 'PROBE':
        raise ValueError('probe line has the wrong shape: %r' % (line,))
    url = parts[2]
    count = parts[3]
    if target not in url:
        raise ValueError('probe snapshot URL %r does not contain %r'
                         % (url, target))
    if count != '1':
        raise ValueError('probe snapshot has %r elements, not 1'
                         % (count,))
    return url, count


def scp_to_laptop(local_path, remote_path):
    proc = subprocess.run(
        ['scp'] + SCP_OPTS + [str(local_path),
                              LAPTOP_HOST + ':' + remote_path],
        capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError('scp failed rc=%d: %s %s'
                           % (proc.returncode, proc.stdout[-300:],
                              proc.stderr[-300:]))
    return True


def _ps_tokens(line):
    return line.split()


def _is_live_driver_line(line):
    """True when one ps line is a live session driver process.

    Token-exact on 'session-driver': the old grep check matched the
    literal pattern text inside its own ssh wrapper command line
    (bash -c 'ps aux | grep -E ...'), so it counted 1 with zero live
    drivers. A real driver carries 'session-driver' as its own argv
    token (cu.py session-driver, or the cu.py session wrapper that
    spawns it); the grep-pattern literal never does.
    """
    return any(tok == 'session-driver' or tok.endswith('/session-driver')
               for tok in _ps_tokens(line))


def _is_live_relay_client_line(line):
    """True when one ps line is a session_remote client holding a lane.

    session_remote.py subcommands: serve is the idle daemon, status
    is a read-only probe, neither holds a lane. start, request,
    result, and finish drive or hold a session, so any of those as
    the subcommand token after session_remote.py means live.
    """
    toks = _ps_tokens(line)
    for i, tok in enumerate(toks):
        if tok.endswith('session_remote.py'):
            if i + 1 < len(toks):
                return toks[i + 1] in ('start', 'request', 'result',
                                       'finish')
            return False
    return False


def assess_lane_liveness(ps_text, relay_status, lease_names):
    """Decide whether another live lane holds the machine (P1.5 fix).

    Replaces the old check, which aborted whenever any *.lease file
    existed (prep file section 10.9: stale leases from 16:04 to
    16:31 with no live driver behind them) and whenever the ps grep
    matched its own ssh wrapper (measured 2026-11-22 18:11 +07: the
    old pipeline returned 1 with zero live drivers). Liveness now
    comes from ps plus relay state only:

    - ps: a live session-driver process, or a session_remote client
      in start/request/result/finish. The relay serve daemon and
      read-only status probes do not count.
    - relay: `session_remote.py status` must answer with state idle,
      finished, or failed, guardian not active, and recovery none.
      An unanswered relay fails closed (a run needs the relay).
    - lease files: recorded as evidence only, never a reason. A
      lease file carries no PID, so its existence alone proves
      nothing about liveness.

    ps_text is the raw output of `ps -eo pid,ppid,etime,args` run
    with no pattern in the remote command, so the probe cannot match
    itself. Returns a dict with live, reasons, drivers (matching ps
    lines), relay (summary), and leases.
    """
    reasons = []
    drivers = []
    for line in (ps_text or '').splitlines():
        if _is_live_driver_line(line) or _is_live_relay_client_line(line):
            drivers.append(line.strip())
    if drivers:
        reasons.append('live driver process: %s'
                       % ('; '.join(drivers)[:300],))
    relay_summary = {}
    if relay_status is None:
        reasons.append('relay status unavailable')
    else:
        relay_summary = {
            'state': relay_status.get('state'),
            'owner': relay_status.get('owner'),
            'driver': relay_status.get('driver'),
            'guardian': relay_status.get('guardian'),
            'recovery': relay_status.get('recovery'),
        }
        state = relay_status.get('state')
        if state not in ('idle', 'finished', 'failed'):
            reasons.append('relay state is %r (owner %r)'
                           % (state, relay_status.get('owner')))
        if relay_status.get('guardian') == 'active':
            reasons.append('relay guardian is active')
        if relay_status.get('recovery') not in ('none', None):
            reasons.append('relay recovery is %r'
                           % (relay_status.get('recovery'),))
    return {'live': bool(reasons), 'reasons': reasons,
            'drivers': drivers, 'relay': relay_summary,
            'leases': list(lease_names or [])}


class Runner:
    def __init__(self):
        self.h = s2_flip_live.Harness(str(WORKDIR), RUN_NO)
        self.results = {'run': RUN_NO, 'fixture': FIXTURE_URL,
                        'fixture_sha256': FIXTURE_SHA,
                        'message': MESSAGE, 'intent': INTENT,
                        'model_calls': 0, 'program_variant': 'set_value',
                        'target': TARGET}
        # Fix (b): tabs are identified by URL, never by stored
        # Marionette handles. Handles are ephemeral per session,
        # so nothing here keeps a handle across zen-tab.py calls.
        # The scratch tab is TARGET (the fixture URL substring);
        # the original tab is its URL, captured in phase 1.
        # self.opened records whether the open succeeded, so
        # cleanup knows whether a scratch tab exists to close.
        self.opened = False
        self.original_url = None
        self.original_title = None
        self.zen_address = None
        self.zen_bounds = None

    def ssh(self, cmd, label, timeout=120):
        rc, out, err, wall = self.h.ssh(cmd, label, timeout=timeout)
        if rc != 0:
            raise RuntimeError('%s failed rc=%d: %s %s'
                               % (label, rc, out.strip()[-300:],
                                  err.strip()[-300:]))
        return out, err, wall

    def tab(self, *args, timeout=60):
        cmd = 'python3 %s %s' % (LAPTOP_DRIVER,
                                 ' '.join(shlex.quote(a) for a in args))
        out, _err, _wall = self.ssh(cmd, 'zen-tab ' + args[0],
                                    timeout=timeout)
        last = out.strip().splitlines()[-1]
        obj = json.loads(last)
        if obj.get('ok') is not True:
            raise RuntimeError('zen-tab %s failed: %s' % (args[0], obj))
        return obj

    def ev(self, expr, timeout=60):
        # Fix (b): evaluate by scratch URL, resolved fresh inside
        # the eval call, never by a stored handle.
        obj = self.tab('eval', TARGET, expr, timeout=timeout)
        return obj['value']

    def oneshot_zen(self, program, intent, timeout=90):
        """One code-exec send through the session-driver, Zen backend.

        Same shape as Harness.oneshot_code_exec, plus
        CU_DOM_BACKEND=zen on the remote command line. The endpoint
        is a dummy: with the Zen backend, dom_start/dom_observe/
        dom_act never touch the CDP endpoint.
        """
        line = json.dumps({'args': ['code-exec', '--endpoint',
                                    'http://127.0.0.1:9223',
                                    '--program', '-', '--intent', intent],
                           'stdin': program, 'image_policy': 'auto'},
                          ensure_ascii=False, separators=(',', ':')) + '\n'
        remote = ('CU_CODE_EXEC=1 CU_DOM_BACKEND=zen python3 %s session'
                  ' -- python3 %s session-driver'
                  % (s2_flip_live.LAPTOP_CU, s2_flip_live.LAPTOP_CU))
        start = time.monotonic()
        rc, out, err, wall = self.h.ssh(remote, 'oneshot-zen',
                                        timeout=timeout, input_text=line)
        wall_ms = (time.monotonic() - start) * 1000.0
        envelope = None
        for raw in out.splitlines():
            try:
                obj = json.loads(raw)
            except ValueError:
                continue
            if isinstance(obj, dict) and 'result' in obj:
                envelope = obj['result']
        if envelope is None:
            raise RuntimeError(
                'one-shot zen code-exec returned no driver result: '
                'rc=%d stdout=%s stderr=%s'
                % (rc, out.strip()[-300:], err.strip()[-300:]))
        return wall_ms, envelope

    def hypr(self, args):
        cmd = ('export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/'
               'hypr/ | head -n1); hyprctl -j ' + args)
        out, _err, _wall = self.ssh(cmd, 'hyprctl ' + args, timeout=60)
        return json.loads(out)

    def phase1(self):
        clients = self.hypr('clients')
        zen = [c for c in clients
               if str(c.get('class', '')).lower().startswith('zen')]
        if not zen:
            raise RuntimeError('no Zen window in hyprctl clients')
        win = zen[0]
        self.zen_address = win.get('address')
        self.zen_bounds = win.get('at', []) + win.get('size', [])
        if win.get('workspace', {}).get('name') not in ('1', 'ws1') \
                and win.get('workspace', {}).get('id') != 1:
            raise RuntimeError('Zen window is not on ws1: %s' % (win,))
        active = self.hypr('activewindow')
        if str(active.get('address', '')).lower() != \
                str(self.zen_address).lower():
            raise RuntimeError(
                'active window is not Zen (%s); aborting'
                % (active.get('address'),))
        self.results['window'] = {
            'address': self.zen_address, 'bounds': self.zen_bounds,
            'workspace': win.get('workspace')}
        # Driver transfer lives here, not in phase 2: phase 1 already
        # needs zen-tab.py for the tab list, but run 1 never reached
        # phase 2 (it aborted at the activewindow gate), so the
        # driver was never copied to the laptop and run 2 aborted
        # in phase 1 with "can't open file zen-tab.py". Copy it
        # before the first tab call.
        self.ssh('mkdir -p ' + LAPTOP_RUN, 'mkdir run dir', timeout=30)
        scp_to_laptop(VM_DRIVER, LAPTOP_DRIVER)
        out, _e, _w = self.ssh('sha256sum ' + LAPTOP_DRIVER,
                               'driver sha', timeout=30)
        import hashlib
        want = hashlib.sha256(VM_DRIVER.read_bytes()).hexdigest()
        if want not in out:
            raise RuntimeError('driver sha mismatch after scp')
        tabs = self.tab('list')
        self.results['tabs_before'] = tabs
        for t in tabs['tabs']:
            if t.get('handle') == tabs['current']:
                # The current handle is only valid inside this one
                # list response. Keep the URL (stable across
                # sessions), never the handle.
                self.original_url = t.get('url')
                self.original_title = t.get('title')
        if not self.original_url:
            raise RuntimeError('could not identify the current tab')
        # Geckodriver check (R14 fix 0cb2b20 supersedes the prep
        # procedure P1.3, which asked for /tmp/geckodriver: the
        # default now resolves to the persistent install at
        # ~/.local/bin/geckodriver, and /tmp/geckodriver no longer
        # exists on the laptop. Ask zen_dom itself for the resolved
        # path and require the file to exist there.
        out, _e, _w = self.ssh(
            'python3 -c "import sys; sys.path.insert(0, \'/home/james/'
            'computer-use-wayland/scripts\'); import zen_dom, os; '
            'print(zen_dom.GECKODRIVER, os.path.isfile('
            'zen_dom.GECKODRIVER))"',
            'geckodriver check', timeout=30)
        if 'True' not in out:
            raise RuntimeError('geckodriver missing at resolved path: %s'
                               % (out.strip()[:200],))
        out, _e, _w = self.ssh(
            'sha256sum /home/james/computer-use-wayland/tests/'
            'two_vision_fixture.html', 'fixture sha', timeout=30)
        if FIXTURE_SHA not in out:
            raise RuntimeError('fixture sha mismatch on the laptop: %s'
                               % (out.strip()[:200],))
        # P1.5 (fixed, prep file section 10.9): liveness comes from ps
        # plus relay state, never from lease file existence. The remote
        # ps command carries no pattern, so it cannot match itself the
        # way the old grep pipeline did.
        out, _e, _w = self.ssh('ps -eo pid,ppid,etime,args',
                               'live lanes ps', timeout=30)
        ps_text = out
        rc, relay_out, _e2, _w2 = self.h.ssh(
            'python3 ' + s2_flip_live.LAPTOP_REMOTE + ' status',
            'relay status', timeout=30)
        relay = None
        if rc == 0:
            try:
                relay = json.loads(relay_out.strip().splitlines()[-1])
            except (ValueError, IndexError):
                relay = None
        out, _e, _w = self.ssh(
            "ls ~/.cache/agent-computer-use/*.lease 2>/dev/null || true",
            'lease list', timeout=30)
        leases = [line.strip() for line in out.strip().splitlines()
                  if line.strip()]
        verdict = assess_lane_liveness(ps_text, relay, leases)
        self.results['liveness'] = verdict
        if verdict['live']:
            raise RuntimeError(
                'another live lane holds the machine: %s'
                % ('; '.join(verdict['reasons']),))

    def phase2(self):
        opened = self.tab('open', timeout=60)
        self.results['open'] = opened
        # The scratch tab is TARGET by URL; the open result
        # confirms its URL and H1, no handle is kept.
        if TARGET not in (opened.get('url') or ''):
            raise RuntimeError('open landed on %r, not the scratch tab'
                               % (opened.get('url'),))
        self.opened = True
        if opened.get('viewport_ok') is not True:
            self.results['outcome'] = 'blocked'
            self.results['error'] = (
                'viewport gate failed: %s' % (opened,))
            raise _Blocked('viewport gate failed')

    def phase3(self):
        switched = self.tab('switch', TARGET, timeout=60)
        if TARGET not in (switched.get('url') or ''):
            raise RuntimeError('switch landed on %r, not the scratch tab'
                               % (switched.get('url'),))
        self.results['switch'] = switched
        active = self.hypr('activewindow')
        if str(active.get('address', '')).lower() != \
                str(self.zen_address).lower():
            raise RuntimeError('active window moved off Zen before probe')
        _wall, env = self.oneshot_zen(PROBE_PROGRAM, INTENT + '-probe',
                                      timeout=90)
        self.results['probe'] = {'wall_ms': round(_wall, 1),
                                 'envelope': env}
        log = env.get('log') or []
        probe_lines = [l for l in log if l.startswith('PROBE ')]
        if env.get('ok') is not True or not probe_lines:
            raise RuntimeError('read-only probe failed: %s' % (env,))
        # Fix (a): the probe gate is the snapshot URL, parsed by
        # parse_probe_line, never the document title.
        url, count = parse_probe_line(probe_lines[-1], TARGET)
        title_lines = [l for l in log if l.startswith('SNAP-TITLE ')]
        snap_title = (title_lines[-1][len('SNAP-TITLE '):]
                      if title_lines else None)
        self.results['probe']['url'] = url
        self.results['probe']['count'] = count
        self.results['probe']['snapshot_title'] = snap_title
        self.results['pre'] = {
            # H1 content confirmation (fix a, second leg): the
            # page in the switched tab really is the zen clone.
            'h1': self.ev(
                "document.getElementById('title').textContent"),
            'bubble_present': self.ev(
                'window.__bubblePresent(%s)' % json.dumps(MESSAGE)),
            'bubbles': self.ev('window.__sentBubbles()'),
            'input_value': self.ev(
                "document.getElementById('msg-input').value"),
            'input_events': self.ev('window.__inputEvents'),
        }
        if self.results['pre']['h1'] != SCRATCH_H1:
            raise RuntimeError('pre-check: H1 is %r, not the zen clone'
                               % (self.results['pre']['h1'],))
        if self.results['pre']['bubble_present']:
            raise RuntimeError('pre-check: message already present')

    def phase4(self):
        active = self.hypr('activewindow')
        if str(active.get('address', '')).lower() != \
                str(self.zen_address).lower():
            raise RuntimeError('active window moved off Zen before send')
        wall_ms, envelope = self.oneshot_zen(SEND_PROGRAM, INTENT,
                                             timeout=90)
        self.results['program'] = {
            'ok': envelope.get('ok'),
            'elapsed_ms': envelope.get('elapsed_ms'),
            'error': envelope.get('error'),
            'log': envelope.get('log'),
            'wall_ms': round(wall_ms, 1),
        }
        completed = None
        for line in envelope.get('log') or []:
            m = re.search(r'dom_act ok (\S+) completed (\d+)', line)
            if m:
                completed = int(m.group(2))
        self.results['program']['completed'] = completed
        if envelope.get('ok') is not True or completed != 4:
            raise RuntimeError('send program did not complete 4/4: %s'
                               % (envelope,))

    def phase5(self):
        self.results['post'] = {
            'bubble_present': self.ev(
                'window.__bubblePresent(%s)' % json.dumps(MESSAGE)),
            'bubbles': self.ev('window.__sentBubbles()'),
            'input_value': self.ev(
                "document.getElementById('msg-input').value"),
            'input_events': self.ev('window.__inputEvents'),
        }
        retry_pre = self.ev(
            'window.__bubblePresent(%s)' % json.dumps(MESSAGE))
        self.results['retry'] = {
            'pre_present': retry_pre,
            'outcome': 'already-sent' if retry_pre else 'would-send'}
        if retry_pre:
            self.results['retry']['bubbles_after_refusal'] = self.ev(
                'window.__sentBubbles()')
        time.sleep(10)
        self.results['delayed'] = {
            'bubbles': self.ev('window.__sentBubbles()'),
            'count': self.ev(
                "window.__sentBubbles().filter(b => b === %s).length"
                % json.dumps(MESSAGE)),
        }
        x, y, w, h = self.zen_bounds
        png = WORKDIR / 'p9-zen-r2.png'
        out, _e, p9_wall = self.ssh(
            'grim -g "%d,%d %dx%d" %s/p9-zen-r2.png'
            % (x, y, w, h, LAPTOP_RUN), 'p9 capture', timeout=60)
        proc = subprocess.run(
            ['scp'] + SCP_OPTS + [LAPTOP_HOST + ':' + LAPTOP_RUN +
                                  '/p9-zen-r2.png', str(png)],
            capture_output=True, text=True, timeout=120)
        if proc.returncode != 0 or not png.exists():
            raise RuntimeError('P9 copy failed rc=%d: %s'
                               % (proc.returncode, proc.stderr[-200:]))
        self.results['p9'] = {'ok': True, 'png': str(png),
                              'wall_ms': round(p9_wall, 1)}

    def cleanup(self):
        """Close the scratch tab, restore the owner's tab, verify.

        Fix (b): close by URL (TARGET for the scratch tab,
        original_url for the owner's tab), never by stored
        handle. Runs whenever the open succeeded, even when a
        later phase blocked: the scratch tab exists then and
        must be closed.
        """
        if not self.opened:
            return {'skipped': True}
        try:
            closed = self.tab('close', TARGET, self.original_url,
                              timeout=60)
        except Exception as exc:  # noqa: BLE001 - record, do not mask
            return {'ok': False, 'error': str(exc)[:300]}
        clients = self.hypr('clients')
        zen = [c for c in clients
               if str(c.get('class', '')).lower().startswith('zen')]
        alive = bool(zen) and str(zen[0].get('address', '')).lower() == \
            str(self.zen_address).lower()
        tabs = self.tab('list')
        current_url = None
        for t in tabs['tabs']:
            if t.get('handle') == tabs['current']:
                current_url = t.get('url')
        return {'ok': True, 'close': closed, 'zen_alive': alive,
                'same_address': alive,
                'tabs_after': tabs,
                'current_url_after': current_url,
                'original_restored': current_url == self.original_url,
                'count_restored': tabs['count'] ==
                self.results['tabs_before']['count']}

    def run(self):
        t0 = time.monotonic()
        try:
            self.phase1()
            self.phase2()
            self.phase3()
            self.phase4()
            self.phase5()
            sent = (self.results['program'].get('ok') is True
                    and self.results['program'].get('completed') == 4
                    and self.results['post']['bubble_present'] is True
                    and self.results['post']['bubbles'] == [MESSAGE]
                    and self.results['post']['input_value'] == ''
                    and self.results['post']['input_events'] >= 1
                    and self.results['retry']['outcome'] == 'already-sent'
                    and self.results['retry'].get('bubbles_after_refusal')
                    == [MESSAGE]
                    and self.results['delayed']['count'] == 1)
            self.results['outcome'] = 'sent' if sent else 'failed-unverified'
        except _Blocked as exc:
            self.results['outcome'] = 'blocked'
            self.results['error'] = str(exc)[:400]
        except Exception as exc:  # noqa: BLE001 - record and re-raise
            self.results['outcome'] = 'error'
            self.results['error'] = str(exc)[:400]
        finally:
            try:
                self.results['cleanup'] = self.cleanup()
            except Exception as exc:  # noqa: BLE001 - record only
                self.results['cleanup'] = {'ok': False,
                                           'error': str(exc)[:300]}
        self.results['wall_ms'] = round((time.monotonic() - t0) * 1000.0, 1)
        WORKDIR.mkdir(parents=True, exist_ok=True)
        (WORKDIR / 'run-2.json').write_text(
            json.dumps(self.results, indent=2))
        print(json.dumps(self.results, indent=2))
        return 0 if self.results['outcome'] == 'sent' else 1


class _Blocked(Exception):
    pass


if __name__ == '__main__':
    raise SystemExit(Runner().run())
