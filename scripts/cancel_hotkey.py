#!/usr/bin/env python3
"""Persistent user cancellation latch for a computer-use session."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

STATE = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))) / 'agent-computer-use'
CANCEL = STATE / 'cancelled'
HOTKEY = 'agentComputerUseEscapeBind'

def hypr_eval(code):
    result = subprocess.run(['hyprctl', 'eval', code], capture_output=True, text=True, timeout=2)
    if result.returncode:
        raise RuntimeError('Hyprland rejected temporary Escape binding: ' + result.stderr.strip()[:180])

def hotkey_off():
    hypr_eval(f'if _G.{HOTKEY} then _G.{HOTKEY}:unbind(); _G.{HOTKEY}=nil end')

def hotkey_on():
    devices = subprocess.run(['hyprctl', '-j', 'devices'], capture_output=True, text=True, check=True, timeout=2)
    names = [item['name'] for item in json.loads(devices.stdout).get('keyboards', [])
             if ('keyboard' in item.get('name', '') and 'virtual' not in item['name']
                 and 'consumer-control' not in item['name'] and 'system-control' not in item['name'])]
    if not names:
        raise RuntimeError('No physical keyboard found for Escape cancellation')
    keys = ','.join(json.dumps(name) for name in names)
    cmd = json.dumps(f'python3 {Path(__file__).resolve()} cancel')
    hypr_eval(f'if _G.{HOTKEY} then _G.{HOTKEY}:unbind() end; '
              f'_G.{HOTKEY}=hl.bind("ESCAPE", hl.dsp.exec_cmd({cmd}), '
              f'{{description="Cancel computer-use",device={{inclusive=true,list={{{keys}}}}}}})')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('cancel', 'resume', 'status', 'hotkey-on', 'hotkey-off'))
    command = parser.parse_args().command
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    STATE.chmod(0o700)
    if command == 'cancel':
        fd = os.open(CANCEL, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as stream:
            stream.write('cancelled by user\n')
        # Latch first; the session guardian restores independently of unbinding.
        import cursor_session
        cursor_session.request_stop()
    elif command == 'resume':
        CANCEL.unlink(missing_ok=True)
    elif command == 'hotkey-on':
        hotkey_on()
    elif command == 'hotkey-off':
        hotkey_off()
    else:
        print('cancelled' if CANCEL.exists() else 'ready')
    return 0

if __name__ == '__main__':
    sys.exit(main())
