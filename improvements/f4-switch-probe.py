"""F4 root-cause probe 4: does switching to the fixture tab leave a
transient (ghost/cross-fade) that an immediate grim capture catches?

Replays the run's phase 2-4 shape, read-only except for the
scratch tab: open the fixture in a scratch tab, switch to it, then
capture the Zen window immediately (S0), at +500ms (S1) and +1000ms
(S2). If S0 is ghosted/blurred and S2 is sharp, the tab switch
leaves a transient that begin_batch (which observes right after
the switch, inside the send program) catches. Uses the same
Harness + zen-tab.py transport as the f4diag runner, pill first,
cleanup closes the scratch tab and restores the owner's tab.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, 'scripts')
import s2_flip_live

WORKDIR = Path('/tmp/c5-zenproof-f4diag')
LAPTOP_RUN = '~/c5-zenproof-run'
LAPTOP_DRIVER = LAPTOP_RUN + '/zen-tab.py'
VM_DRIVER = Path('improvements/c5-zenproof-runs/zen-tab.py')
TARGET = 'two_vision_fixture.html?clone=zen'
FIXTURE_URL = ('file://~/computer-use-wayland/tests/'
               'two_vision_fixture.html?clone=zen')

h = s2_flip_live.Harness(str(WORKDIR), 'f4probe4')


def ssh(cmd, label, timeout=60):
    rc, out, err, _wall = h.ssh(cmd, label, timeout=timeout)
    if rc != 0:
        raise RuntimeError('%s rc=%d: %s %s' % (label, rc,
                                                out[-200:], err[-200:]))
    return out


def tab(*args, timeout=60):
    cmd = 'python3 %s %s' % (LAPTOP_DRIVER,
                             ' '.join(__import__('shlex').quote(a)
                                      for a in args))
    out = ssh(cmd, 'zen-tab ' + args[0], timeout=timeout)
    return json.loads(out.strip().splitlines()[-1])


# Pill first (gate 4.29).
rc, out, err, _w = h.ssh(h.pill_acquire_cmd(), 'pill-acquire', timeout=60)
if rc != 0:
    raise SystemExit('pill acquire failed')
import re
pid = int(re.search(r'PILL_SLEEP_PID=(\d+)', out).group(1))
print('PILL_SLEEP_PID=%d' % pid)
status = json.loads(ssh('python3 %s status' % s2_flip_live.LAPTOP_OVERLAY,
                        'pill-status'))
print('pill visible:', status.get('visible'))
assert status.get('visible') is True

try:
    # As-found: Zen window bounds + current tab.
    clients = json.loads(ssh(
        'export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ '
        '| head -n1); hyprctl -j clients', 'hypr clients'))
    zen = [c for c in clients
           if str(c.get('class', '')).lower().startswith('zen')][0]
    bounds = zen['at'] + zen['size']
    print('Zen bounds:', bounds)
    ssh('export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ '
        '| head -n1); hyprctl dispatch "hl.dsp.focus({ window = '
        '\\"address:%s\\" })"' % zen['address'], 'focus Zen')
    tabs = tab('list')
    original_url = None
    for t in tabs['tabs']:
        if t.get('handle') == tabs['current']:
            original_url = t.get('url')
    print('tabs_before:', tabs['count'], 'current:', original_url)
    # Open the scratch fixture tab, then switch to it (phase 2 + 4
    # shape, back to back like the run).
    opened = tab('open', FIXTURE_URL, timeout=60)
    print('open ok:', opened.get('ok'), 'url:', opened.get('url'))
    switched = tab('switch', TARGET, timeout=60)
    print('switch ok:', switched.get('ok'), 'url:', switched.get('url'))

    def grim(name):
        x, y, w, h = bounds
        ssh('XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 '
            'grim -g "%d,%d %dx%d" /tmp/f4-probe4-%s.png'
            % (x, y, w, h, name), 'grim ' + name, timeout=60)

    # S0 immediately after the switch, then S1 +500ms, S2 +1000ms.
    grim('s0')
    time.sleep(0.5)
    grim('s1')
    time.sleep(0.5)
    grim('s2')
    print('captured s0/s1/s2')
    # Copy frames to the VM for diffing.
    for name in ('s0', 's1', 's2'):
        proc = subprocess.run(
            ['scp', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=25',
             '-o', 'StrictHostKeyChecking=accept-new',
             '-o', 'IdentitiesOnly=yes',
             '-o', 'ProxyCommand=python3 /home/hatch/workspace/'
                    'tailscale-proxy.py %h %p',
             '-i', '/home/hatch/.ssh/id_ed25519',
             'user@192.0.2.1:/tmp/f4-probe4-%s.png' % name,
             str(WORKDIR / ('probe4-%s.png' % name))],
            capture_output=True, text=True, timeout=120)
        print(name, 'scp rc=%d' % proc.returncode)
finally:
    # Cleanup: close the scratch tab, restore the owner's tab.
    try:
        closed = tab('close', TARGET, original_url, timeout=60)
        print('cleanup close:', closed.get('ok'))
    except Exception as exc:  # noqa: BLE001 - record only
        print('cleanup close failed:', str(exc)[:200])
    try:
        out = ssh('python3 %s release --agent S2-flip --pid %d'
                  % (s2_flip_live.LAPTOP_OVERLAY, pid),
                  'pill-release', timeout=60)
        print('pill release:', out.strip()[:200])
    except Exception as exc:  # noqa: BLE001 - record only
        print('pill release failed:', str(exc)[:200])
print('PROBE4 DONE')
