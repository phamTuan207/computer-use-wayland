#!/usr/bin/env python3
"""Zen pointer delegate live proof, run 1 (W-ZENPREP, COORD-CLICK-6).

Runs the live proof per improvements/w-zen-delegate-liveproof-prep.md
section 5, phases 1-6, against the scratch fixture tab in Zen on
ws1. Reuses the step 9 harness transport (Harness.ssh over the mux)
for laptop commands and a oneshot session-driver for the code-exec
program, with CU_DOM_BACKEND=zen added to the remote command line.
The program itself is the Zen form from the prep file (not the CDP
builder output): dom_observe with a scope, ref on the key action.

No model calls. No input to any existing tab at any point. The only
send is the marked test message into the local file fixture. If any
gate fails, the run aborts (BLOCKED before input, FAIL after it) and
phase 6 cleanup still runs best-effort.

Usage (from the repo root on the VM):
  python3 improvements/c5-zenproof-runs/c5-zen-delegate-run.py
Exit 0 only when outcome is 'sent'; anything else exits 1.
Result: /tmp/c5-zenproof-1/run-1.json plus p9-zen-r1.png.
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

RUN_NO = 1
MESSAGE = 'ZEN-DELEGATE-R1-IGNORE-TEST'
INTENT = 'c5-zen-delegate-r1'
TARGET = 'Clone zen thread'
SCOPE = '#msg-input'
BUBBLE_SELECTOR = '#thread .bubble:last-child'
FIXTURE_URL = ('file:///home/james/computer-use-wayland/tests/'
               'two_vision_fixture.html?clone=zen')
FIXTURE_SHA = ('147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6'
               'cbf')
WORKDIR = Path('/tmp/c5-zenproof-1')
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
    "snap = dom_observe('Clone zen thread', '#msg-input', 80)\n"
    "print('PROBE', snap['snapshot'], snap.get('title'),"
    " len(snap.get('elements') or []))\n"
)

SEND_PROGRAM = (
    "dom_start()\n"
    "snap = dom_observe('Clone zen thread', '#msg-input', 80)\n"
    "res = dom_act(snap, [\n"
    "    {\"type\": \"set_value\", \"ref\": \"#msg-input\", \"text\": \""
    + MESSAGE + "\", \"scope\": \"Clone zen thread\","
    " \"observation_id\": snap[\"snapshot\"]},\n"
    "    {\"type\": \"focus\", \"ref\": \"#msg-input\", \"scope\":"
    " \"Clone zen thread\", \"observation_id\": snap[\"snapshot\"]},\n"
    "    {\"type\": \"key\", \"ref\": \"#msg-input\", \"keys\": [\"Enter\"],"
    " \"scope\": \"Clone zen thread\","
    " \"observation_id\": snap[\"snapshot\"]},\n"
    "    {\"type\": \"assert\", \"selector\": \"#thread .bubble:last-child\","
    " \"text\": \"" + MESSAGE + "\", \"timeout_ms\": 3000,"
    " \"scope\": \"Clone zen thread\","
    " \"observation_id\": snap[\"snapshot\"]},\n"
    "])\n"
    "print(\"dom_act ok\", res.get(\"ok\"), \"completed\","
    " res.get(\"completed\"), \"ms\", res.get(\"execution_ms\"),"
    " \"error\", res.get(\"error\"))\n"
    "assert_state(res.get(\"ok\") is True, \"dom_act failed\")\n"
)


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


class Runner:
    def __init__(self):
        self.h = s2_flip_live.Harness(str(WORKDIR), RUN_NO)
        self.results = {'run': RUN_NO, 'fixture': FIXTURE_URL,
                        'fixture_sha256': FIXTURE_SHA,
                        'message': MESSAGE, 'intent': INTENT,
                        'model_calls': 0, 'program_variant': 'set_value',
                        'target': TARGET}
        self.scratch_handle = None
        self.original_handle = None
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
        obj = self.tab('eval', self.scratch_handle, expr, timeout=timeout)
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
        tabs = self.tab('list')
        self.results['tabs_before'] = tabs
        for t in tabs['tabs']:
            if t.get('handle') == tabs['current']:
                self.original_handle = t['handle']
                self.original_title = t.get('title')
        if not self.original_handle:
            raise RuntimeError('could not identify the current tab')
        out, _e, _w = self.ssh('ls -l /tmp/geckodriver',
                               'geckodriver check', timeout=30)
        if 'geckodriver' not in out:
            raise RuntimeError('/tmp/geckodriver missing on the laptop')
        out, _e, _w = self.ssh(
            'sha256sum /home/james/computer-use-wayland/tests/'
            'two_vision_fixture.html', 'fixture sha', timeout=30)
        if FIXTURE_SHA not in out:
            raise RuntimeError('fixture sha mismatch on the laptop: %s'
                               % (out.strip()[:200],))
        out, _e, _w = self.ssh(
            "ps aux | grep -E 'session-driver|session_remote' | grep -v grep | wc -l",
            'other lanes check', timeout=30)
        if int(out.strip() or '0') != 0:
            raise RuntimeError('another session-driver is running')
        out, _e, _w = self.ssh(
            "ls ~/.cache/agent-computer-use/*.lease 2>/dev/null | wc -l",
            'lease check', timeout=30)
        if int(out.strip() or '0') != 0:
            raise RuntimeError('a live lease file exists on the laptop')

    def phase2(self):
        self.ssh('mkdir -p ' + LAPTOP_RUN, 'mkdir run dir', timeout=30)
        scp_to_laptop(VM_DRIVER, LAPTOP_DRIVER)
        out, _e, _w = self.ssh('sha256sum ' + LAPTOP_DRIVER,
                               'driver sha', timeout=30)
        import hashlib
        want = hashlib.sha256(VM_DRIVER.read_bytes()).hexdigest()
        if want not in out:
            raise RuntimeError('driver sha mismatch after scp')
        opened = self.tab('open', timeout=60)
        self.results['open'] = opened
        self.scratch_handle = opened['new_handle']
        if opened.get('viewport_ok') is not True:
            self.results['outcome'] = 'blocked'
            self.results['error'] = (
                'viewport gate failed: %s' % (opened,))
            raise _Blocked('viewport gate failed')

    def phase3(self):
        switched = self.tab('switch', self.scratch_handle, timeout=60)
        if switched.get('title') != TARGET:
            raise RuntimeError('switch landed on %r, not the scratch tab'
                               % (switched.get('title'),))
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
        probe_lines = [l for l in log if 'PROBE' in l]
        if env.get('ok') is not True or not probe_lines:
            raise RuntimeError('read-only probe failed: %s' % (env,))
        # PROBE line shape: PROBE <snapshot-id> <title words...> <count>
        parts = probe_lines[-1].split()
        title = ' '.join(parts[2:-1])
        count = parts[-1]
        if len(parts) < 4 or title != TARGET or count != '1':
            raise RuntimeError('probe snapshot is not the scratch tab: %s'
                               % (probe_lines,))
        self.results['pre'] = {
            'bubble_present': self.ev(
                'window.__bubblePresent(%s)' % json.dumps(MESSAGE)),
            'bubbles': self.ev('window.__sentBubbles()'),
            'input_value': self.ev(
                "document.getElementById('msg-input').value"),
            'input_events': self.ev('window.__inputEvents'),
        }
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
        png = WORKDIR / 'p9-zen-r1.png'
        out, _e, p9_wall = self.ssh(
            'grim -g "%d,%d %dx%d" %s/p9-zen-r1.png'
            % (x, y, w, h, LAPTOP_RUN), 'p9 capture', timeout=60)
        proc = subprocess.run(
            ['scp'] + SCP_OPTS + [LAPTOP_HOST + ':' + LAPTOP_RUN +
                                  '/p9-zen-r1.png', str(png)],
            capture_output=True, text=True, timeout=120)
        if proc.returncode != 0 or not png.exists():
            raise RuntimeError('P9 copy failed rc=%d: %s'
                               % (proc.returncode, proc.stderr[-200:]))
        self.results['p9'] = {'ok': True, 'png': str(png),
                              'wall_ms': round(p9_wall, 1)}

    def cleanup(self):
        """Close the scratch tab, restore the owner's tab, verify."""
        if not self.scratch_handle:
            return {'skipped': True}
        try:
            closed = self.tab('close', self.scratch_handle,
                              self.original_handle, timeout=60)
        except Exception as exc:  # noqa: BLE001 - record, do not mask
            return {'ok': False, 'error': str(exc)[:300]}
        clients = self.hypr('clients')
        zen = [c for c in clients
               if str(c.get('class', '')).lower().startswith('zen')]
        alive = bool(zen) and str(zen[0].get('address', '')).lower() == \
            str(self.zen_address).lower()
        tabs = self.tab('list')
        return {'ok': True, 'close': closed, 'zen_alive': alive,
                'same_address': alive,
                'tabs_after': tabs,
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
        (WORKDIR / 'run-1.json').write_text(
            json.dumps(self.results, indent=2))
        print(json.dumps(self.results, indent=2))
        return 0 if self.results['outcome'] == 'sent' else 1


class _Blocked(Exception):
    pass


if __name__ == '__main__':
    raise SystemExit(Runner().run())
