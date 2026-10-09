"""Read-only microbenchmarks. No compositor, pointer, keyboard or session writes.

python3 tests/performance.py --scripts scripts --samples 40
Compare the same command with an unedited scripts copy. Timings are local,
synthetic frame timings are NOT live desktop/session timings.
"""
import argparse
import contextlib
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
    import cursor_session
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
    monitor=json.dumps([{'name':'test','x':0,'y':0,'width':1920,'height':1200,'scale':1}]).encode()
    calls=[]
    def capture(argv,**kwargs):
        calls.append(argv[0]);return subprocess.CompletedProcess(argv,0,monitor if argv[0]=='hyprctl' else raw,b'')
    def quiet():
        with patch.object(cursor_session.subprocess,'run',side_effect=capture),contextlib.redirect_stderr(io.StringIO()):
            cursor_session.wait_for_quiet({},lambda:False)
    measure('quiet_static_mock_capture',quiet)
    results['quiet_calls_per_sample']={name:calls.count(name)/args.samples for name in set(calls)}
    alternate=io.BytesIO();Image.new('RGB',(1920,1200),'white').save(alternate,format='PPM')
    frames=[raw,alternate.getvalue()];index=[0]
    def busy_capture(argv,**kwargs):
        if argv[0]=='hyprctl':data=monitor
        else:data=frames[index[0]%2];index[0]+=1
        return subprocess.CompletedProcess(argv,0,data,b'')
    def busy():
        with patch.object(cursor_session.subprocess,'run',side_effect=busy_capture):
            try:cursor_session.wait_for_quiet({},lambda:False,attempts=4)
            except RuntimeError as error:
                if 'did not settle after 4 captures' not in str(error):raise
            else:raise AssertionError('busy frames must not pass the gate')
    measure('quiet_busy_mock_capture',busy)
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
