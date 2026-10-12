#!/usr/bin/env python3
"""Owned Chromium fixture for target routing; synthetic values only."""
import argparse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

from browser_task_benchmark import finish_report,wait_workspace,write_report

TEXT='Tạo báo cáo nháp — 3 mục'
PAGE='''<!doctype html><meta charset="utf-8"><title>CU Owned Field Lab</title>
<input id="target"><input id="decoy"><button id="save">Save fixture</button><p id="status">Ready</p>
<script>
const q=new URL(location.href).searchParams,scenario=q.get('scenario'),caseId=q.get('case'),expected='Tạo báo cáo nháp — 3 mục';
const target=document.querySelector('#target'),decoy=document.querySelector('#decoy');
if(scenario==='false-success')target.value=expected;
let seq=0,events=[];
function publish(event){
 if(event)events.push({target:event.target.id,type:event.type,key:event.key??'',code:event.code??'',trusted:event.isTrusted});
 fetch('/state',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({case:caseId,seq:++seq,target:target.value,decoy:decoy.value,events})});
}
for(const field of [target,decoy])for(const type of ['keydown','input','change'])field.addEventListener(type,event=>{
 if(type==='keydown'&&field===target&&scenario.startsWith('false-'))decoy.focus();
 publish(event);
});
document.querySelector('#save').onclick=()=>{
 const value=target.value;document.querySelector('#status').textContent='Saved '+value;
 fetch('/done',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({case:caseId,target:value,decoy:decoy.value})});
};
</script>'''.encode()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli',type=Path,default=Path(__file__).resolve().parents[1]/'scripts/cu.py')
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    if os.environ.get('CU_SESSION_TOKEN'):
        parser.error('fixture owns its session; launch with computer-use session')
    return subprocess.run([sys.executable,str(args.cli.resolve()),'session','--',sys.executable,
                           str(Path(__file__).resolve()),'--cli',str(args.cli.resolve()),
                           '--report',str(args.report.resolve()),'--inside']).returncode


def run(cli,report_path):
    root=cli.resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
    import cu
    from browser_worker import BrowserWorker
    cu.require_session();env=cu.environment()
    original=cu.hypr(env,'activewindow').get('address')
    original_ws=json.loads(cu.run(['hyprctl','-j','activeworkspace'],env))['id']
    occupied={w['id'] for w in cu.hypr(env,'workspaces')}
    workspace=next(i for i in range(101,201) if i not in occupied)
    state={};lock=threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def do_GET(self):
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(PAGE)
        def do_POST(self):
            size=int(self.headers.get('Content-Length','0'))
            if size>10000 or self.path not in ('/state','/done'):
                self.send_error(400);return
            try:data=json.loads(self.rfile.read(size))
            except (ValueError,UnicodeDecodeError):self.send_error(400);return
            if data.get('case') not in ('normal','false-empty','false-success','set-value'):
                self.send_error(400);return
            with lock:
                if self.path=='/state':
                    old=state.get(data['case'],{})
                    if data.get('seq',-1)>=old.get('seq',-1):state[data['case']]=data
                else:state.setdefault(data['case'],{}).update(done=data)
            self.send_response(204);self.end_headers()
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    rows=[];children=[];workers=[];profiles=[]
    result={'kind':'live_browser_field_routing',
            'runtime':'source' if (root/'.git').exists() else 'installed',
            'cases':rows,'tasks_ok':False,
            'cleanup_ok':False,'runtime_sha256':{n:hashlib.sha256((root/'scripts'/n).read_bytes()).hexdigest()
            for n in ('cu.py','browser_worker.py','cdp.mjs')}}
    def wait_state(key,predicate,timeout=3):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            cu.check_cancel()
            with lock:value=dict(state.get(key,{}))
            if predicate(value):return value
            time.sleep(.01)
        raise RuntimeError('owned fixture callback timed out')
    try:
        cu.run(['hyprctl','dispatch',f'hl.dsp.focus({{ workspace = "{workspace}" }})'],env)
        wait_workspace(cu,env,workspace)
        for case in ('normal','false-empty','false-success','set-value'):
            cu.check_cancel();profile=tempfile.TemporaryDirectory(prefix='cu-field-route-');profiles.append(profile)
            case_url=f'http://127.0.0.1:{server.server_port}/?scenario={case}&case={case}'
            child=subprocess.Popen(['chromium','--user-data-dir='+profile.name,'--remote-debugging-port=0',
                '--remote-debugging-address=127.0.0.1','--no-first-run','--no-default-browser-check',
                '--disable-background-networking','--window-size=920,700','--app='+case_url],env=env,
                stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            children.append(child);deadline=time.monotonic()+12;target=endpoint=None
            while time.monotonic()<deadline:
                cu.check_cancel()
                if child.poll() is not None:raise RuntimeError('owned Chromium exited')
                try:
                    port=int((Path(profile.name)/'DevToolsActivePort').read_text().splitlines()[0])
                    endpoint=f'http://127.0.0.1:{port}'
                    with urllib.request.urlopen(endpoint+'/json/list',timeout=.5) as response:tabs=json.load(response)
                    target=next((t['id'] for t in tabs if t.get('type')=='page' and t.get('url')==case_url),None)
                    if target:break
                except (OSError,ValueError,IndexError):pass
                time.sleep(.05)
            if not target:raise RuntimeError('owned Chromium target unavailable')
            worker=BrowserWorker();workers.append(worker);base={'endpoint':endpoint,'target':target,'max_elements':8}
            snapshot=worker.request({**base,'operation':'observe'})
            if not snapshot.get('ok',True):raise RuntimeError('fixture observation failed')
            mode='fill' if case.startswith('false-') or case=='normal' else 'set_value'
            actions=[{'type':mode,'selector':'#target','text':TEXT},
                     {'type':'click','selector':'#save'},
                     {'type':'assert','selector':'#status','text':'Saved '+TEXT,'timeout_ms':1000}]
            started=time.monotonic();act=worker.request({**base,'operation':'act','snapshot':snapshot['snapshot'],'actions':actions})
            with lock:observed=dict(state.get(case,{}))
            if case=='false-empty':
                wait_state(case,lambda d:d.get('decoy')==TEXT)
                if act.get('ok') or act.get('completed')!=0:raise RuntimeError('empty target misroute was not refused')
                row={'case':case,'expected':'fill refused after decoy received text','observed_ok':act.get('ok'),
                     'completed':act.get('completed'),'wrong_target_text':True,'mutation_may_have_occurred':True}
            elif case=='false-success':
                observed=wait_state(case,lambda d:d.get('decoy')==TEXT)
                done=wait_state(case,lambda d:bool(d.get('done')))
                if not act.get('ok') or done['done'].get('target')!=TEXT:raise RuntimeError('false-success baseline did not reproduce')
                row={'case':case,'expected':'fill reports ok although decoy changed','observed_ok':True,
                     'wrong_target_text':True,'app_target_exact':done['done']['target']==TEXT}
            else:
                observed=wait_state(case,lambda d:d.get('target')==TEXT and bool(d.get('events')))
                done=wait_state(case,lambda d:bool(d.get('done')))
                if not act.get('ok') or done['done'].get('target')!=TEXT or done['done'].get('decoy')!='':
                    raise RuntimeError('targeted field route failed app outcome check')
                if case=='set-value' and not any(e['type']=='input' and e['target']=='target' and not e['trusted'] for e in observed['events']):
                    raise RuntimeError('set_value did not expose the documented synthetic input event')
                row={'case':case,'method':mode,'ok':True,'app_target_exact':True,'decoy_unchanged':True,
                     'synthetic_input_event':case=='set-value','task_ms':round((time.monotonic()-started)*1000,3)}
            rows.append(row);result['tasks_ok']=True;write_report(result,report_path)
    except BaseException:
        result['tasks_ok']=False;raise
    finally:
        errors=[]
        for worker in workers:
            try:worker.close()
            except BaseException:errors.append('worker_close')
        for child in children:
            try:
                if child.poll() is None:child.terminate()
                try:child.wait(timeout=4)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=3)
            except BaseException:errors.append('chromium_reap')
        for profile in profiles:
            try:profile.cleanup()
            except BaseException:errors.append('profile_cleanup')
        try:server.shutdown();server.server_close();thread.join(timeout=2)
        except BaseException:errors.append('server_cleanup')
        try:
            if not cu.CANCEL.exists():
                active=json.loads(cu.run(['hyprctl','-j','activeworkspace'],env))['id']
                if active==workspace:
                    cu.run(['hyprctl','dispatch',f'hl.dsp.focus({{ workspace = "{original_ws}" }})'],env)
                    if original and any(w.get('address')==original for w in cu.hypr(env,'clients')):cu.focus(env,original)
                    wait_workspace(cu,env,original_ws)
        except BaseException:errors.append('focus_restore')
        result['cleanup_errors']=errors;result['cleanup_ok']=not errors
        result['ok']=result['tasks_ok'] and result['cleanup_ok']
        write_report(result,report_path)
    return result


if __name__=='__main__':
    import signal
    def interrupted(*_):raise KeyboardInterrupt('fixture interrupted')
    for sig in (signal.SIGTERM,signal.SIGHUP):signal.signal(sig,interrupted)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inside',action='store_true',help=argparse.SUPPRESS);p.add_argument('--cli',type=Path,default=Path(__file__).resolve().parents[1]/'scripts/cu.py');p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    if not a.inside:raise SystemExit(main())
    output=run(a.cli,a.report);print(json.dumps({k:v for k,v in output.items() if k!='cases'},separators=(',',':')))
    raise SystemExit(0 if output['ok'] else 1)
