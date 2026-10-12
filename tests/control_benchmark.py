#!/usr/bin/env python3
"""Read-only isolated CLI vs resident executor benchmark; no model calls or input."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import session_driver


def benchmark(args,samples):
    timings={'isolated':[],'resident':[]}
    for i in range(samples):
        for mode in (('isolated','resident') if i%2==0 else ('resident','isolated')):
            started=time.perf_counter()
            result=(subprocess.run([sys.executable,str(ROOT/'scripts/cu.py'),*args],capture_output=True,text=True)
                    if mode=='isolated' else session_driver.execute(args,''))
            if result.returncode:raise RuntimeError('benchmark command failed; inspect desktop/session state')
            timings[mode].append((time.perf_counter()-started)*1000)
    return {k:{'samples':len(v),'median_ms':round(statistics.median(v),3),
               'min_ms':round(min(v),3),'max_ms':round(max(v),3)} for k,v in timings.items()}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples',type=int,default=12)
    parser.add_argument('--window')
    parser.add_argument('--crop',type=int,nargs=4)
    options=parser.parse_args()
    if not 3<=options.samples<=30:parser.error('samples must be 3..30')
    if options.crop and not options.window:parser.error('crop requires window')
    report={'status':benchmark(['status'],options.samples)}
    if options.window:
        args=['observe','--window',options.window]
        if options.crop:args+=['--crop',*[str(n) for n in options.crop]]
        report['capture']=benchmark(args,options.samples)
    print(json.dumps(report,separators=(',',':')))
