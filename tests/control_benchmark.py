#!/usr/bin/env python3
"""Read-only isolated CLI vs resident executor benchmark; no model calls or input."""
import argparse
import io
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
import tempfile
from unittest.mock import patch

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


def browser_benchmark(endpoint,target,samples):
    import cu
    from browser_worker import BrowserWorker
    request={'operation':'observe','endpoint':endpoint,'target':target,'max_elements':16}
    worker=BrowserWorker();timings={'isolated':[],'resident':[]}
    try:
        started=time.perf_counter();first=worker.request(request)
        cold=(time.perf_counter()-started)*1000
        if not isinstance(first,dict) or not first.get('snapshot'):raise RuntimeError('browser fixture observation failed')
        for i in range(samples):
            for mode in (('isolated','resident') if i%2==0 else ('resident','isolated')):
                started=time.perf_counter()
                result=cu.browser(request) if mode=='isolated' else worker.request(request)
                timings[mode].append((time.perf_counter()-started)*1000)
                if not isinstance(result,dict) or not result.get('snapshot'):raise RuntimeError('browser fixture observation failed')
        return {'cold_worker_ms':round(cold,3),**{k:{'samples':len(v),
            'median_ms':round(statistics.median(v),3),'min_ms':round(min(v),3),
            'max_ms':round(max(v),3)} for k,v in timings.items()}}
    finally:worker.close()


def encoding_benchmark(image,samples):
    from PIL import Image
    timings={1:[],2:[]};sizes={}
    expected=image.convert('RGB').tobytes()
    for i in range(samples):
        for level in ((1,2) if i%2==0 else (2,1)):
            output=io.BytesIO();started=time.perf_counter()
            image.save(output,format='PNG',compress_level=level)
            timings[level].append((time.perf_counter()-started)*1000)
            sizes[level]=output.tell()
            with Image.open(io.BytesIO(output.getvalue())) as decoded:
                assert decoded.size==image.size and decoded.convert('RGB').tobytes()==expected
    return {str(k):{'samples':len(v),'median_ms':round(statistics.median(v),3),
                    'bytes':sizes[k],'lossless_verified':True} for k,v in timings.items()}


def browser_image_benchmark(raw,samples):
    import cu
    from PIL import Image
    expected=Image.open(io.BytesIO(raw)).convert('RGB')
    if expected.width>1280:
        expected=expected.resize((1280,round(expected.height*1280/expected.width)),Image.Resampling.LANCZOS)
    timings={'reencode':[],'reuse':[]};sizes={};preserved={}
    with tempfile.TemporaryDirectory(prefix='cu-png-benchmark-') as folder,patch.object(cu,'STATE',Path(folder)):
        for i in range(samples):
            for mode in (('reencode','reuse') if i%2==0 else ('reuse','reencode')):
                started=time.perf_counter()
                meta=(cu.save_observation(Image.open(io.BytesIO(raw)).convert('RGB'),{},1280) if mode=='reencode'
                      else cu.save_observation(None,{},1280,encoded_png=raw))
                timings[mode].append((time.perf_counter()-started)*1000)
                sizes[mode]=Path(meta['image']).stat().st_size
                preserved[mode]=Path(meta['image']).read_bytes()==raw
                with Image.open(meta['image']) as decoded:
                    assert decoded.size==expected.size and decoded.tobytes()==expected.tobytes()
    return {k:{'samples':len(v),'median_ms':round(statistics.median(v),3),
               'bytes':sizes[k],'original_bytes_preserved':preserved[k],
               'lossless_verified':True} for k,v in timings.items()}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples',type=int,default=12)
    parser.add_argument('--window')
    parser.add_argument('--crop',type=int,nargs=4)
    parser.add_argument('--png',type=Path,help='compare processing an existing PNG, without printing its path or pixels')
    parser.add_argument('--endpoint',default='http://127.0.0.1:9222')
    parser.add_argument('--target',help='exact tab ID of an inert fixture for read-only worker benchmarking')
    options=parser.parse_args()
    if not 3<=options.samples<=30:parser.error('samples must be 3..30')
    if options.crop and not options.window:parser.error('crop requires window')
    report={'status':benchmark(['status'],options.samples)}
    if options.target:report['browser']=browser_benchmark(options.endpoint,options.target,options.samples)
    if options.png:report['browser_png_processing']=browser_image_benchmark(options.png.read_bytes(),options.samples)
    if options.window:
        args=['observe','--window',options.window]
        if options.crop:args+=['--crop',*[str(n) for n in options.crop]]
        report['capture']=benchmark(args,options.samples)
        import cu
        image,_=cu.observe(cu.environment(),options.window,options.crop,persist=False)
        report['png_encoding']=encoding_benchmark(image,options.samples)
    print(json.dumps(report,separators=(',',':')))
