#!/usr/bin/env python3
"""Real input demo restricted to tests/demo.py's inert GTK application."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import sys
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--layout',type=Path,required=True)
    parser.add_argument('--events',type=Path,required=True)
    parser.add_argument('--engine',type=Path,default=Path(__file__).resolve().parents[1]/'scripts')
    args=parser.parse_args()
    if not os.environ.get('CU_SESSION_TOKEN'):
        parser.error('launch with computer-use session -- python3 tests/demo_driver.py ...')
    sys.path.insert(0,str(args.engine.resolve()))
    import cu
    env=cu.environment()
    matches=[c for c in cu.hypr(env,'clients') if c.get('title')=='Computer Use Demo'
             and c.get('class')=='local.computeruse.Demo']
    if len(matches)!=1:raise RuntimeError('exactly one inert demo window is required')
    address=matches[0]['address']
    previous=cu.hypr(env,'activewindow').get('address')
    cu.prepare_state()
    results=[]
    with open(cu.STATE/'desktop.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        try:
            cu.focus(env,address)
            # Setup only: allow workspace movement to finish before taking pixels.
            cu.wait_cancelable(.25)
            layout=json.loads(args.layout.read_text())
            baseline=json.loads(args.events.read_text())
            def step(label,make_actions):
                meta=cu.observe(env,address,max_width=1920)
                def point(name,fx=.5,fy=.5):
                    x,y,w,h=layout[name]
                    return [(x+w*fx)*meta['image_size'][0]/meta['region'][2],
                            (y+h*fy)*meta['image_size'][1]/meta['region'][3]]
                started=time.perf_counter()
                result=cu.desktop_act(env,meta,make_actions(point))
                if not result['ok']:raise RuntimeError(result.get('error','demo input refused'))
                results.append({'step':label,'ms':round((time.perf_counter()-started)*1000,1)})
            step('focus entry',lambda p:[dict(type='click',x=p('entry')[0],y=p('entry')[1])])
            text='Computer use — thử máy ✓'
            step('literal text',lambda p:[dict(type='key',keys=['Ctrl','a']),dict(type='type',text=text)])
            step('button',lambda p:[dict(type='click',x=p('button')[0],y=p('button')[1])])
            step('double click',lambda p:[dict(type='double_click',x=p('button')[0],y=p('button')[1])])
            step('drag',lambda p:[dict(type='drag',**{'from':p('canvas'),
                 'to':p('canvas',.65,.65),'ms':300})])
            step('Ctrl click',lambda p:[dict(type='click',x=p('canvas',.2,.2)[0],
                 y=p('canvas',.2,.2)[1],modifiers=['Ctrl'])])
            step('scroll',lambda p:[dict(type='scroll',x=p('canvas',.2,.2)[0],
                 y=p('canvas',.2,.2)[1],dy=30)])
            events=json.loads(args.events.read_text())[len(baseline):]
            assert any(e.get('event')=='entry' and e.get('text')==text for e in events),'literal text not delivered'
            assert sum(e.get('event')=='button' for e in events)==3,'button count differs'
            assert any(e.get('event')=='drag' and abs(e.get('dx',0))>10 for e in events),'drag not delivered'
            assert any(e.get('event')=='canvas' and 'Ctrl' in e.get('mods','') for e in events),'Ctrl not delivered'
            assert any(e.get('event')=='scroll' for e in events),'scroll not delivered'
            print(json.dumps({'ok':True,'steps':results}),flush=True)
        finally:
            # Do not override a new focus choice or bypass a cancellation latch.
            if previous and previous!=address and cu.hypr(env,'activewindow').get('address')==address:
                if any(c.get('address')==previous for c in cu.hypr(env,'clients')):
                    cu.focus(env,previous)


if __name__=='__main__':main()
