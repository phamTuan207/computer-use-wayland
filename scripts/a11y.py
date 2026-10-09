"""Bounded AT-SPI semantic adapter; no desktop settings changes."""
import json
from pathlib import Path
import sys
import time
import uuid
import gi
gi.require_version('Atspi','2.0')
from gi.repository import Atspi
from cu import STATE,prepare_state

Atspi.set_timeout(1000,1000)

def applications():
    d=Atspi.get_desktop(0)
    return [d.get_child_at_index(i) for i in range(d.get_child_count())]

def app(pid):
    matches=[a for a in applications() if a.get_process_id()==pid]
    if len(matches)!=1:raise ValueError('exact app PID required; use a11y apps')
    return matches[0]

def describe(e,path,ref):
    name=e.get_name() or '';role=e.get_role_name();actions=[]
    try:
        interface=e.get_action_iface()
        if interface:actions=[interface.get_action_name(i) for i in range(interface.get_n_actions())]
    except Exception:pass
    states=e.get_state_set();editable=states.contains(Atspi.StateType.EDITABLE)
    result={'ref':ref,'role':role,'name':name[:120],'path':path,'actions':actions}
    if editable:result['editable']=True
    if not states.contains(Atspi.StateType.SENSITIVE):result['disabled']=True
    # Do not collect field values, passwords, full text documents or the entire desktop tree.
    return result

def observe(pid):
    root=app(pid);pending=[(root,[])];items=[];visited=0;start=time.monotonic()
    while pending and visited<500 and time.monotonic()-start<2:
        e,path=pending.pop();visited+=1
        try:
            item=describe(e,path,'e'+str(len(items)+1))
            if item['actions'] or item.get('editable'):
                items.append(item)
                if len(items)>=80:break
            if len(path)<12:
                for i in reversed(range(min(e.get_child_count(),100))):pending.append((e.get_child_at_index(i),path+[i]))
        except Exception:continue
    snapshot={'backend':'a11y','pid':pid,'app_name':root.get_name(),'created':time.time(),'elements':items,'truncated':bool(pending)}
    prepare_state();path=STATE/(uuid.uuid4().hex[:12]+'.json');snapshot['snapshot']=str(path)
    path.write_text(json.dumps(snapshot));path.chmod(0o600)
    return {**snapshot,'elements':[{k:v for k,v in item.items() if k!='path'} for item in items]}

def resolve(root,item):
    e=root
    for i in item['path']:e=e.get_child_at_index(i)
    if not e or e.get_name()[:120]!=item['name'] or e.get_role_name()!=item['role']:raise ValueError('accessibility tree changed; observe again')
    if not e.get_state_set().contains(Atspi.StateType.SENSITIVE):raise ValueError('element is disabled')
    return e

def act(path,actions):
    snapshot=json.loads(Path(path).read_text())
    if snapshot.get('backend')!='a11y' or time.time()-snapshot['created']>90:raise ValueError('stale accessibility snapshot')
    if not isinstance(actions,list) or not 1<=len(actions)<=32:raise ValueError('1..32 actions required')
    root=app(snapshot['pid']);refs={e['ref']:e for e in snapshot['elements']}
    for a in actions:
        if a.get('type') not in ('click','set_text') or a.get('ref') not in refs:raise ValueError('click/set_text and valid ref required')
        e=resolve(root,refs[a['ref']])
        if a['type']=='set_text' and (not isinstance(a.get('text'),str) or len(a['text'])>10000 or not refs[a['ref']].get('editable')):raise ValueError('editable ref and text <=10000 required')
        if a['type']=='click' and not any(n.lower() in ('click','press','toggle') for n in refs[a['ref']]['actions']):raise ValueError('no native click action; use desktop pointer')
    completed=0;result={'ok':True};start=time.monotonic()
    try:
        for a in actions:
            e=resolve(root,refs[a['ref']])
            if a['type']=='click':
                interface=e.get_action_iface();names=[interface.get_action_name(i).lower() for i in range(interface.get_n_actions())]
                index=next((i for i,n in enumerate(names) if n in ('click','press','toggle')),None)
                if index is None:raise ValueError('no native click action; use desktop pointer')
                if not interface.do_action(index):raise RuntimeError('native action refused')
            else:
                if not e.get_editable_text_iface().set_text_contents(a['text']):raise RuntimeError('text setter refused')
                text=e.get_text_iface()
                if Atspi.Text.get_text(text,0,Atspi.Text.get_character_count(text))!=a['text']:raise RuntimeError('text verification failed')
            completed+=1
    except Exception as exc:result.update(ok=False,error=str(exc))
    result.update(completed=completed,execution_ms=round((time.monotonic()-start)*1000))
    result['after']=observe(snapshot['pid'])
    return result

try:
    request=json.load(sys.stdin)
    if request['operation']=='apps':result=[{'pid':a.get_process_id(),'name':a.get_name()} for a in applications()]
    elif request['operation']=='observe':result=observe(request['pid'])
    else:result=act(request['snapshot'],request['actions'])
    print(json.dumps(result,ensure_ascii=False,separators=(',',':')))
except Exception as exc:
    print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False));sys.exit(1)
