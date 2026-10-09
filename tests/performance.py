"""Read-only microbenchmarks. No compositor, pointer, keyboard or session writes.

python3 tests/performance.py --scripts scripts --samples 40
Compare the same command with an unedited scripts copy. Timings are local,
synthetic frame timings are NOT live desktop/session timings.
"""
import argparse
import io
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from unittest.mock import patch


def summary(values):
    ordered=sorted(values)
    return {'n':len(values),'median_ms':round(statistics.median(values),3),
            'p95_ms':round(ordered[min(len(ordered)-1,int(len(ordered)*.95))],3)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scripts',type=Path,default=Path(__file__).resolve().parents[1]/'scripts')
    parser.add_argument('--samples',type=int,default=40)
    args=parser.parse_args()
    if args.samples<1:parser.error('--samples must be positive')
    scripts=args.scripts.resolve();sys.path.insert(0,str(scripts))
    import cu
    from PIL import Image, ImageDraw
    results={}
    def measure(name,fn):
        values=[]
        for _ in range(args.samples):
            start=time.perf_counter();fn();values.append((time.perf_counter()-start)*1000)
        results[name]=summary(values)
    measure('python_pass',lambda:subprocess.run([sys.executable,'-c','pass'],check=True,capture_output=True))
    code='import sys;sys.path.insert(0,'+repr(str(scripts))+');import cu'
    measure('python_import_cu',lambda:subprocess.run([sys.executable,'-c',code],check=True,capture_output=True))
    measure('cli_help',lambda:subprocess.run([sys.executable,'-c',code+';cu.main()','--help'],check=True,capture_output=True))
    measure('cli_status',lambda:subprocess.run([sys.executable,'-c',code+';cu.main()','status'],check=True,capture_output=True))
    # In-memory PPM; no desktop pixels or identifying metadata enter the results.
    image=Image.new('RGB',(1920,1200),(128,64,32));out=io.BytesIO();image.save(out,format='PPM');raw=out.getvalue()
    scaled=image.resize((1280,800))
    measure('stale_full_image_compare',lambda:cu.screen_changed(scaled,scaled,[{'type':'click','x':600,'y':400}]))
    changed=scaled.copy();ImageDraw.Draw(changed).rectangle((0,0,400,799),fill='white')
    actions=[{'type':'click','x':600,'y':400}]
    old_patch=scaled.crop((576,376,625,425));new_patch=changed.crop((576,376,625,425))
    measure('rejected_patch_only_compare',lambda:cu.screen_changed(old_patch,new_patch,[]))
    results['patch_only_misses_global_change']={
        'full_guard':cu.screen_changed(scaled,changed,actions),
        'patch_guard':cu.screen_changed(old_patch,new_patch,[])}
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
