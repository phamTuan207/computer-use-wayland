"""Opt-in real-desktop observation/preflight benchmark; no movement or typing.

Use a static disposable terminal opened by the operator. Never starts a browser
or touches installed tool files. Each sample uses a fresh session and isolated
cache; the production act guard is unchanged, even when it refuses.
"""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]


def driver(cli,screen,destination):
    def call(args,**kwargs):
        start=time.perf_counter()
        p=subprocess.run([sys.executable,cli,*args],capture_output=True,text=True,timeout=15,**kwargs)
        return p,(time.perf_counter()-start)*1000
    p,elapsed=call(['observe','--screen',screen])
    if p.returncode:raise RuntimeError(p.stderr)
    observation=json.loads(p.stdout)
    p,action_elapsed=call(['act','--observation',observation['observation'],'--actions','-'],
                          input='[{"type":"wait","ms":0}]')
    result=json.loads(p.stdout)
    Path(destination).write_text(json.dumps({'observe_ms':elapsed,'act_ms':action_elapsed,
        'act_exit':p.returncode,'refused':result.get('ok') is False,'error':result.get('error'),
        'capture_ms':observation['capture_ms'],'image_size':observation['image_size']}))
    return p.returncode


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli',type=Path,default=ROOT/'scripts/cu.py')
    parser.add_argument('--screen',default='eDP-2')
    parser.add_argument('--samples',type=int,default=20)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.samples<1:parser.error('--samples must be positive')
    # Read the real compositor environment using the selected tool version.
    sys.path.insert(0,str(args.cli.resolve().parent))
    import cu
    env=cu.environment();env.pop('CU_SESSION_TOKEN',None)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='cu-session-live-') as cache:
        env['XDG_CACHE_HOME']=cache
        for _ in range(args.samples):
            destination=Path(cache)/'result.json';start=time.perf_counter()
            p=subprocess.run([sys.executable,str(args.cli.resolve()),'session','--',
                sys.executable,str(Path(__file__).resolve()),'driver',str(args.cli.resolve()),
                args.screen,str(destination)],env=env,capture_output=True,text=True,timeout=45)
            row=json.loads(destination.read_text()) if destination.exists() else {'startup_error':p.stderr}
            row.update(session_ms=(time.perf_counter()-start)*1000,session_exit=p.returncode,
                       startup_log=p.stderr.strip());rows.append(row)
            destination.unlink(missing_ok=True)
    result={'n':len(rows),'refusals':sum(r.get('refused',False) for r in rows),
            'startup_failures':sum('startup_error' in r for r in rows),
            'act_errors':sum(r.get('act_exit',0)!=0 and not r.get('refused',False) for r in rows),
            'rows':rows}
    for key in ('observe_ms','act_ms','session_ms'):
        values=[r[key] for r in rows if key in r]
        result[key+'_median']=statistics.median(values) if values else None
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return int(bool(result['startup_failures'] or result['act_errors']))


if __name__=='__main__':
    if sys.argv[1:2]==['driver']:sys.exit(driver(*sys.argv[2:]))
    sys.exit(main())
