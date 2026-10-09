#!/usr/bin/env python3
"""Isolated Chromium profile; real Wayland input and CDP assertions. No external sites."""
import importlib.util
import json
from pathlib import Path
import statistics
import subprocess
import tempfile
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cu',ROOT/'scripts/cu.py');cu=importlib.util.module_from_spec(spec);spec.loader.exec_module(cu)

def cdp_eval(target,expression):
    # Use Node's built-in WebSocket, not another Python dependency.
    code="""const t=JSON.parse(process.argv[1]),ws=new WebSocket(t.webSocketDebuggerUrl);ws.onopen=()=>ws.send(JSON.stringify({id:1,method:'Runtime.evaluate',params:{expression:process.argv[2],returnByValue:true}}));ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id===1){console.log(JSON.stringify(r.result.result.value));ws.close();}};setTimeout(()=>process.exit(2),4000).unref();"""
    return json.loads(cu.run(['node','--input-type=module','-e',code,json.dumps(target),expression]))

def main():
    env=cu.environment();original=cu.hypr(env,'activewindow').get('address')
    profile=tempfile.TemporaryDirectory(prefix='cu-test-');endpoint='http://127.0.0.1:19322'
    log=open(Path(profile.name)/'chromium.log','w')
    proc=subprocess.Popen(['chromium','--user-data-dir='+profile.name,'--remote-debugging-port=19322','--remote-debugging-address=127.0.0.1','--no-first-run','--no-default-browser-check','--disable-background-networking',str(ROOT/'tests/fixture.html')],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    report={'native':{},'browser':{}}
    try:
        for _ in range(100):
            try:
                tabs=json.load(urllib.request.urlopen(endpoint+'/json/list',timeout=1))
                target=next(t for t in tabs if t['type']=='page' and 'fixture.html' in t['url'])
                break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('test browser did not start')
        for _ in range(30):
            clients=cu.hypr(env,'clients');client=next((c for c in clients if 'Computer Use Test Lab' in c.get('title','')),None)
            if client:break
            time.sleep(.1)
        if not client:raise RuntimeError('test window missing')
        address=client['address'];cu.focus(env,address);time.sleep(.6)
        cli='computer-use'
        cli_tabs=json.loads(cu.run([cli,'browser','tabs','--endpoint',endpoint],env));assert any(t['id']==target['id'] for t in cli_tabs)
        cli_obs=json.loads(cu.run([cli,'browser','observe','--endpoint',endpoint,'--target',target['id'],'--image'],env));assert Path(cli_obs['image']).exists() and cli_obs['elements']
        report['browser']['cli_tabs_and_image']=True
        def browser(op,**kwargs):return cu.browser({'operation':op,'endpoint':endpoint,'target':target['id'],**kwargs})
        snapshot=browser('observe');refs={e['name']:e['ref'] for e in snapshot['elements']}
        result=browser('act',snapshot=snapshot['snapshot'],actions=[{'type':'fill','ref':refs['Name'],'text':'Tiếng Việt 🐱'},{'type':'click','ref':refs['Save']},{'type':'assert','selector':'#status','text':'Saved Tiếng Việt 🐱'}])
        assert result['ok'],result
        report['browser']['unicode_form_ms']=result['execution_ms'];report['browser']['actions']=result['completed']
        old=snapshot['snapshot'];stale=browser('act',snapshot=old,actions=[{'type':'click','ref':refs['Save']}]);assert not stale['ok'],stale
        report['browser']['stale_ref_rejected']=True
        # DOM reorder / movement retains the actual element ref, not its old coordinates.
        snapshot=browser('observe');ref=next(e['ref'] for e in snapshot['elements'] if e['name']=='Small target')
        cdp_eval(target,"document.querySelector('#tiny').style.marginLeft='160px';true")
        result=browser('act',snapshot=snapshot['snapshot'],actions=[{'type':'click','ref':ref}]);assert result['ok'],result
        snapshot=browser('observe');ref=next(e['ref'] for e in snapshot['elements'] if e['name']=='Small target')
        cdp_eval(target,"document.querySelector('#overlay').style.display='block';true")
        result=browser('act',snapshot=snapshot['snapshot'],actions=[{'type':'click','ref':ref}]);assert not result['ok'],result
        report['browser']['covered_target_rejected']=True
        cdp_eval(target,"document.querySelector('#overlay').style.display='none';document.querySelector('#tiny').style.marginLeft='10px';lab.events=[];true")
        # Find browser content origin using actual compositor geometry and DOM metrics.
        metrics=cdp_eval(target,"({innerWidth,innerHeight,outerWidth,outerHeight,dpr:devicePixelRatio,rect:(()=>{const r=document.querySelector('#tiny').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()})")
        client=cu.window(env,address)
        top=client['at'][1]+client['size'][1]-metrics['innerHeight']
        gx=client['at'][0]+metrics['rect']['x'];gy=top+metrics['rect']['y']
        times=[];start_count=cdp_eval(target,'lab.tiny')
        for i in range(12):
            obs=cu.observe(env,address,max_width=960)
            rx,ry,rw,rh=obs['region'];iw,ih=obs['image_size']
            point={'x':(gx-rx)*iw/rw,'y':(gy-ry)*ih/rh}
            t=time.monotonic();result=cu.desktop_act(env,obs,[{'type':'click',**point}]);times.append((time.monotonic()-t)*1000)
            assert result['ok'],result
            assert cdp_eval(target,'lab.tiny')==start_count+i+1,(i,result)
        events=cdp_eval(target,'lab.events');assert len(events)==12 and all(e['trusted'] and e['id']=='tiny' for e in events),events
        report['native'].update(small_target_hits='12/12',trusted=True,median_batch_ms=round(statistics.median(times)),p95_batch_ms=round(sorted(times)[-1]),preview_width=960)
        # Crop + resize maps back to the same small target.
        obs=cu.observe(env,address,crop=[round(gx-client['at'][0]-50),round(gy-client['at'][1]-50),100,100])
        rx,ry,rw,rh=obs['region'];iw,ih=obs['image_size']
        result=cu.desktop_act(env,obs,[{'type':'click','x':(gx-rx)*iw/rw,'y':(gy-ry)*ih/rh}]);assert result['ok'],result
        report['native']['crop_hit']=True
        # Reject out of bounds before a preceding valid action is executed.
        obs=cu.observe(env,address);before=cdp_eval(target,'lab.tiny')
        try:cu.desktop_act(env,obs,[{'type':'click','x':10,'y':10},{'type':'click','x':99999,'y':10}])
        except ValueError:pass
        else:raise AssertionError('bad batch accepted')
        assert cdp_eval(target,'lab.tiny')==before
        report['native']['bad_batch_rejected']=True
        # The field coordinate is derived by instrumentation; verify native Unicode + chords.
        rect=cdp_eval(target,"(()=>{const r=document.querySelector('#name').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
        obs=cu.observe(env,address);rx,ry,rw,rh=obs['region'];iw,ih=obs['image_size']
        result=cu.desktop_act(env,obs,[{'type':'click','x':(client['at'][0]+rect['x']-rx)*iw/rw,'y':(top+rect['y']-ry)*ih/rh},{'type':'key','keys':['ctrl','a']},{'type':'type','text':'Native Việt'}]);assert result['ok'],result
        actual=cdp_eval(target,"document.querySelector('#name').value")
        assert actual=='Native Việt',actual
        report['native']['unicode_and_chord']=True;report['native']['form_batch_ms']=result['execution_ms']
        # Browser chrome shortcuts must use pressed modifiers, not -m (release).
        obs=cu.observe(env,address)
        result=cu.desktop_act(env,obs,[{'type':'key','keys':['ctrl','t']},{'type':'wait','ms':150}]);assert result['ok'],result
        pages=json.load(urllib.request.urlopen(endpoint+'/json/list'))
        assert len([t for t in pages if t['type']=='page'])==2,pages
        obs=cu.observe(env,address)
        result=cu.desktop_act(env,obs,[{'type':'key','keys':['ctrl','w']},{'type':'wait','ms':150}]);assert result['ok'],result
        assert len([t for t in json.load(urllib.request.urlopen(endpoint+'/json/list')) if t['type']=='page'])==1
        report['native']['ctrl_t_and_ctrl_w']=True
        # Real native drag through browser DND, verified by the drop handler.
        rects=cdp_eval(target,"['drag','drop'].map(id=>{const r=document.getElementById(id).getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})")
        obs=cu.observe(env,address);rx,ry,rw,rh=obs['region'];iw,ih=obs['image_size']
        points=[[(client['at'][0]+x-rx)*iw/rw,(top+y-ry)*ih/rh] for x,y in rects]
        result=cu.desktop_act(env,obs,[{'type':'drag','from':points[0],'to':points[1],'ms':500}]);assert result['ok'],result
        assert cdp_eval(target,'lab.drag')==1
        report['native']['drag_drop']=True
        # A changed display must be rejected before clicking coordinates from the previous image.
        obs=cu.observe(env,address);cdp_eval(target,"document.body.style.background='#222';true")
        result=cu.desktop_act(env,obs,[{'type':'click','x':20,'y':20}])
        assert not result['ok'] and result['completed']==0 and 'screen changed' in result['error'],result
        assert Path(result['after']['image']).exists()
        report['native']['changed_screen_rejected']=True
        print(json.dumps(report,ensure_ascii=False,indent=2))
        (ROOT/'tests/latest-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    finally:
        proc.terminate()
        try:proc.wait(timeout=8)
        except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=3)
        if original:
            try:cu.focus(env,original)
            except Exception:pass
        log.close();profile.cleanup()

if __name__=='__main__':main()
