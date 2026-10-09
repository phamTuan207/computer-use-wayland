"""Live startup proof without moving, clicking or typing; run explicitly.

python3 tests/session_quiet_live.py
Uses isolated cache state and only an act wait:0. Capture comparison is measured
inside the real screen_changed function; the CLI and guard remain unchanged.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import cu


def act_probe(observation):
    from PIL import ImageChops,ImageStat
    original=cu.screen_changed
    def measured(old,new,actions):
        mean=sum(ImageStat.Stat(ImageChops.difference(old,new)).mean)/3
        print('GUARD_MEAN='+str(mean),file=sys.stderr)
        return original(old,new,actions)
    cu.screen_changed=measured
    sys.argv=[str(ROOT/'scripts/cu.py'),'act','--observation',observation,'--actions','-']
    return cu.main()


def driver():
    p=subprocess.run([sys.executable,str(ROOT/'scripts/cu.py'),'observe','--screen','eDP-2'],capture_output=True,text=True,check=True)
    observation=json.loads(p.stdout)
    p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'act-probe',observation['observation']],
                     input='[{"type":"wait","ms":0}]',capture_output=True,text=True)
    mean=next(float(line.split('=',1)[1]) for line in p.stderr.splitlines() if line.startswith('GUARD_MEAN='))
    result=json.loads(p.stdout)
    print(json.dumps({'guard_mean':mean,'act_exit':p.returncode,'act':result,
                      'zoom_during':cu.run(['hyprctl','getoption','cursor:zoom_factor'],cu.environment()).strip()}))
    return p.returncode


def main():
    env=cu.environment()
    with tempfile.TemporaryDirectory(prefix='cu-quiet-live-') as cache:
        env['XDG_CACHE_HOME']=cache
        print('zoom_before: '+cu.run(['hyprctl','getoption','cursor:zoom_factor'],env).strip(),flush=True)
        p=subprocess.run([sys.executable,str(ROOT/'scripts/cu.py'),'session','--',
                          sys.executable,str(Path(__file__).resolve()),'driver'],env=env)
        print('session_exit: '+str(p.returncode),flush=True)
        print('zoom_after: '+cu.run(['hyprctl','getoption','cursor:zoom_factor'],env).strip(),flush=True)
        return p.returncode


if __name__=='__main__':
    if sys.argv[1:2]==['act-probe']:sys.exit(act_probe(sys.argv[2]))
    if sys.argv[1:2]==['driver']:sys.exit(driver())
    sys.exit(main())
