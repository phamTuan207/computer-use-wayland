"""F4 diagnostic driver: pill first, grim-verify by sight, focus Zen,
then launch the f4diag runner detached. Mirrors the run-5 launch
procedure (pill gate 4.29). Prints PILL_SLEEP_PID and the runner
log path. The runner itself does phases 1-6 and writes
/tmp/c5-zenproof-f4diag/run-f4diag.json on the VM.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, 'scripts')
import s2_flip_live

WORKDIR = Path('/tmp/c5-zenproof-f4diag')
RUNNER = Path('improvements/c5-zenproof-runs/c5-zen-delegate-f4diag.py')

h = s2_flip_live.Harness(str(WORKDIR), 'f4diag')

# 1. Pill acquire (same command the runner uses when no env pid).
rc, out, err, _wall = h.ssh(h.pill_acquire_cmd(), 'pill-acquire',
                            timeout=60)
if rc != 0:
    raise SystemExit('pill acquire failed rc=%d: %s %s'
                     % (rc, out.strip()[-200:], err.strip()[-200:]))
m = re.search(r'PILL_SLEEP_PID=(\d+)', out)
if not m:
    raise SystemExit('pill acquire ok but no PILL_SLEEP_PID')
pid = int(m.group(1))
print('PILL_SLEEP_PID=%d' % pid)

# 2. Pill status visible check.
rc, out, _err, _wall = h.ssh(
    'python3 %s status' % s2_flip_live.LAPTOP_OVERLAY,
    'pill-status', timeout=60)
status = json.loads(out.strip())
print('pill status:', json.dumps(status))
if status.get('visible') is not True:
    raise SystemExit('pill not visible after acquire')

# 3. Pre-run grim, copy to VM for sight review.
h.ssh('XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 '
      'grim /tmp/c5-zenproof-f4diag-pill-pre.png',
      'pill-pre grim', timeout=60)
proc = subprocess.run(
    ['scp', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=25',
     '-o', 'StrictHostKeyChecking=accept-new',
     '-o', 'IdentitiesOnly=yes',
     '-o', 'ProxyCommand=python3 /home/hatch/workspace/'
            'tailscale-proxy.py %h %p',
     '-i', '/home/hatch/.ssh/id_ed25519',
     'user@192.0.2.1:/tmp/c5-zenproof-f4diag-pill-pre.png',
     str(WORKDIR / 'pill-pre-f4diag.png')],
    capture_output=True, text=True, timeout=120)
print('grim copy rc=%d' % proc.returncode)
print('grim file:', WORKDIR / 'pill-pre-f4diag.png')

# 4. Focus Zen by window address (same as run 5).
clients = json.loads(h.ssh(
    'export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ '
    '| head -n1); hyprctl -j clients', 'hypr clients',
    timeout=60)[1])
zen = [c for c in clients
       if str(c.get('class', '')).lower().startswith('zen')]
if not zen:
    raise SystemExit('no Zen window')
addr = zen[0]['address']
print('Zen address:', addr)
h.ssh('export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ '
      '| head -n1); hyprctl dispatch "hl.dsp.focus({ window = '
      '\\"address:%s\\" })"' % addr, 'focus Zen', timeout=60)
active = json.loads(h.ssh(
    'export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ '
    '| head -n1); hyprctl -j activewindow', 'hypr activewindow',
    timeout=60)[1])
print('active window:', active.get('address'), active.get('class'))
if str(active.get('address', '')).lower() != str(addr).lower():
    raise SystemExit('active window is not Zen')

# 5. Launch the f4diag runner detached, with the pill pid.
WORKDIR.mkdir(parents=True, exist_ok=True)
log = WORKDIR / 'f4diag-launch.log'
with open(log, 'w') as lf:
    env = dict(os.environ)
    env['PILL_SLEEP_PID'] = str(pid)
    proc = subprocess.Popen(
        [sys.executable, str(RUNNER)],
        env=env,
        cwd='.', stdout=lf, stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, start_new_session=True,
        close_fds=True)
print('runner pid:', proc.pid)
print('log:', log)
print('DRIVER DONE')
