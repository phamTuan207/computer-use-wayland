"""Bounded AT-SPI semantic adapter; no desktop settings changes."""
import json
import os
from pathlib import Path
import sys
import time
import uuid
import gi
gi.require_version('Atspi','2.0')
from gi.repository import Atspi
from cu import STATE,prepare_state,read_json_file,read_json,validate_actions

Atspi.set_timeout(1000,1000)

# Pick 4 fast path (speed-swarm prototype): opt-in via CU_PICK4_FASTPATH=1,
# default off. With the flag off this file behaves exactly like baseline.
FASTPATH_ENV='CU_PICK4_FASTPATH'

def _pick4():
    return os.environ.get(FASTPATH_ENV)=='1'

def _ints4(value):
    """Four ints from an AT-SPI extents tuple or an object with x/y/w/h."""
    if value is None:
        return None
    if isinstance(value,(list,tuple)) and len(value)==4:
        parts=list(value)
    else:
        try:
            parts=[value.x,value.y,value.width,value.height]
        except Exception:
            return None
    if any(isinstance(v,bool) or not isinstance(v,int) for v in parts):
        return None
    if parts[2]<=0 or parts[3]<=0:
        return None
    return parts

def _component_extents(e):
    """Exact AT-SPI Component box, or None when the element exposes none.

    Any failure omits the box; the caller falls back to vision. Mock
    objects in tests return non-int values and are filtered the same way.
    """
    try:
        interface=e.get_component_iface()
        if interface is None:
            return None
        return _ints4(interface.get_extents(Atspi.CoordType.SCREEN))
    except Exception:
        return None

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
    if _pick4():
        extents=_component_extents(e)
        if extents is not None:
            result['extents']=extents
            result['extents_coord']='screen'
    for key in ('pressed', 'checked', 'selected', 'expanded'):
        if states.contains(getattr(Atspi.StateType, key.upper())):
            result[key] = True
    if not states.contains(Atspi.StateType.SENSITIVE):result['disabled']=True
    # Do not collect field values, passwords, full text documents or the entire desktop tree.
    return result

def _completeness(snapshot):
    """Root completeness of a snapshot dict (I15).

    Returns (complete, incomplete, read_errors). New snapshots
    carry all three; legacy ones derive incomplete from
    complete, then truncated. A snapshot with no completeness
    fields at all is unknown, hence incomplete: a read failure
    must never collapse into "absent" or "complete"."""
    errors=snapshot.get('read_errors')
    if isinstance(errors,bool) or not isinstance(errors,int) or errors<0:errors=0
    incomplete=snapshot.get('incomplete')
    if not isinstance(incomplete,bool):
        complete=snapshot.get('complete')
        if isinstance(complete,bool):incomplete=not complete
        elif isinstance(snapshot.get('truncated'),bool):incomplete=snapshot['truncated']
        else:incomplete=True
    if errors:incomplete=True
    return not incomplete,incomplete,errors

def observe(pid,skeleton=False,subtree=None):
    root=app(pid);origin,base=subtree if subtree is not None else (root,[])
    pending=[(origin,base)];items=[];visited=0;start=time.monotonic();truncated=False
    read_errors=0
    cut_paths=set()
    while pending and visited<500 and time.monotonic()-start<2:
        e,path=pending.pop();visited+=1
        try:
            item=describe(e,path,'e'+str(len(items)+1))
            try:count=e.get_child_count()
            except Exception:count=None
            item['children_count']=count
            if skeleton or item['actions'] or item.get('editable'):
                items.append(item)
                if len(items)>=80:
                    if skeleton:truncated=bool(count or pending)
                    break
            limit=min(len(base)+3,12) if skeleton else 12
            if len(path)<limit:
                if count is None:count=e.get_child_count()
                if count>100:
                    truncated=True;cut_paths.add(tuple(path))
                for i in reversed(range(min(count,100))):pending.append((e.get_child_at_index(i),path+[i]))
            elif count:
                truncated=True;cut_paths.add(tuple(path))
        except Exception:
            # I15: a node that cannot be read is unknown, not
            # absent. Count it at the root so the snapshot is
            # marked incomplete instead of silently dropping it.
            read_errors+=1;continue
    # Budget stop (node/time caps) leaves pending children unwalked:
    # their parents are cut too (I5 per-node accounting).
    for _e,path in pending:
        if path:cut_paths.add(tuple(path[:-1]))
    for item in items:
        if tuple(item['path']) in cut_paths:item['cut']=True
    incomplete=bool(pending) or truncated or read_errors>0
    snapshot={'backend':'a11y','pid':pid,'app_name':root.get_name(),'created':time.time(),'elements':items,'truncated':bool(pending) or truncated,'complete':not incomplete,'incomplete':incomplete,'read_errors':read_errors}
    prepare_state();sid=uuid.uuid4().hex[:12];path=STATE/(sid+'.json');snapshot['snapshot']=str(path);snapshot['snapshot_id']=sid
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        os.fchmod(fd,0o600)
        stream=os.fdopen(fd,'w',encoding='utf-8')
    except BaseException:
        try:os.close(fd)
        except OSError:pass
        raise
    with stream:
        stream.write(json.dumps(snapshot))
    return {**snapshot,'elements':[{k:v for k,v in item.items() if skeleton or k!='path'} for item in items]}

def query(pid,name=None,role=None,limit=20):
    """Pruned a11y read: only elements matching a name or role filter.

    One observe (same 500-node, 2s, 80-item bounds), then filter in memory,
    so the returned text stays at roughly 50-200 tokens instead of a full
    tree dump. The snapshot file from observe() is returned so a later
    ground() can re-resolve a ref against the live tree.
    """
    if not _pick4():raise ValueError('pick4 fast path is off; set CU_PICK4_FASTPATH=1')
    if name is None and role is None:raise ValueError('a11y query needs a name or role filter')
    if isinstance(limit,bool) or not isinstance(limit,int) or not 1<=limit<=20:
        raise ValueError('query limit must be 1..20')
    snapshot=observe(pid)
    matched=[]
    for item in snapshot['elements']:
        if name is not None and name.casefold() not in (item.get('name') or '').casefold():continue
        if role is not None and role.casefold() not in (item.get('role') or '').casefold():continue
        matched.append(item)
    _complete,incomplete,errors=_completeness(snapshot)
    incomplete=incomplete or len(matched)>limit
    return {'backend':'a11y-query','pid':pid,'app_name':snapshot['app_name'],
            'created':snapshot['created'],'snapshot':snapshot['snapshot'],
            'elements':matched[:limit],'matched':len(matched),
            'truncated':bool(snapshot.get('truncated')) or len(matched)>limit,
            'complete':not incomplete,'incomplete':incomplete,'read_errors':errors}

def parse_ref(snapshot,ref):
    """Resolve a possibly snapshot-qualified ref to its bare form (I3).

    Qualified form is '<snapshot_id>:<ref>'. A qualified ref whose
    id does not match the loaded snapshot's in-file snapshot_id is
    refused (it belongs to a different observation). A bare ref
    against a snapshot that carries an id is accepted with a
    deprecation warning on stderr. Legacy snapshots without an
    in-file id are grandfathered: bare refs pass silently and a
    qualified ref's id cannot be verified, so its bare part is used.
    """
    if not isinstance(ref,str) or not ref:raise ValueError('valid accessibility ref required')
    sid=snapshot.get('snapshot_id')
    if ':' in ref:
        given,_,bare=ref.partition(':')
        if not bare:raise ValueError('valid accessibility ref required')
        if sid is not None and given!=sid:
            raise ValueError('ref belongs to a different snapshot: '+given)
        return bare
    if sid is not None:
        print('warning: bare accessibility ref '+ref+'; use the '
              'snapshot-qualified form '+sid+':'+ref,file=sys.stderr)
    return ref

def ground(snapshot_path,ref):
    """Re-resolve one snapshot ref against the live tree and return its box.

    The box is fresh (read now, not from the snapshot), and the app root or
    first top-level frame box is returned alongside so the caller can tell
    whether the extents are screen or window relative. No pointer movement,
    no click: the caller must crop-verify the box before any click.
    """
    if not _pick4():raise ValueError('pick4 fast path is off; set CU_PICK4_FASTPATH=1')
    snapshot=read_json_file(snapshot_path)
    if snapshot.get('backend') not in ('a11y','a11y-query') or time.time()-snapshot['created']>90:
        raise ValueError('stale accessibility snapshot')
    ref=parse_ref(snapshot,ref)
    item=next((e for e in snapshot['elements'] if e['ref']==ref),None)
    if item is None:raise ValueError('valid accessibility ref required')
    root=app(snapshot['pid']);element=wait_actionable(root,item)
    extents=_component_extents(element)
    if extents is None:raise ValueError('element exposes no extents; use vision')
    root_extents=_component_extents(root)
    if root_extents is None:
        try:
            count=root.get_child_count()
            if isinstance(count,bool) or not isinstance(count,int):count=0
            count=max(0,min(count,100))
        except Exception:
            count=0
        for index in range(count):
            try:root_extents=_component_extents(root.get_child_at_index(index))
            except Exception:continue
            if root_extents is not None:break
        if root_extents is None:raise ValueError('no window frame extents; use vision')
    complete,incomplete,errors=_completeness(snapshot)
    return {'ok':True,'ref':ref,'qref':(snapshot['snapshot_id']+':'+ref if snapshot.get('snapshot_id') else ref),'role':item['role'],'name':item['name'],
            'extents':extents,'extents_coord':'screen',
            'root_extents':root_extents,
            'snapshot_complete':complete,'snapshot_incomplete':incomplete,'snapshot_read_errors':errors}

def resolve(root,item):
    e=root
    for i in item['path']:e=e.get_child_at_index(i)
    if not e or (e.get_name() or '')[:120]!=item['name'] or e.get_role_name()!=item['role']:raise ValueError('accessibility tree changed; observe again')
    if not e.get_state_set().contains(Atspi.StateType.SENSITIVE):raise ValueError('element is disabled')
    return e

ACTIONABLE_CAP_MS=1000

def wait_actionable(root,item,cap_ms=1000):
    """Auto-wait (I10): poll until the element is enabled, visible
    (when the state exists), and its extents are stable across
    two reads, up to cap_ms. First check is immediate, so a
    ready element costs one extra extents read. Raises the last
    failing reason on expiry; a stale tree raises at once."""
    deadline=time.monotonic()+cap_ms/1000.0
    last_reason='not actionable'
    prev_extents=None
    while True:
        e=resolve(root,item)
        states=e.get_state_set()
        visible=True
        for name in ('VISIBLE','SHOWING'):
            state=getattr(Atspi.StateType,name,None)
            if state is not None and not states.contains(state):
                visible=False
        if not visible:
            last_reason='element is not visible'
            prev_extents=None
        else:
            extents=_component_extents(e)
            if extents is not None and extents==prev_extents:
                return e
            if extents is None:
                # No extents exposed: enabled+visible is all we can
                # prove; do not block the action on a missing box.
                return e
            prev_extents=extents
            last_reason='element extents not stable'
        if time.monotonic()>=deadline:
            raise ValueError(last_reason+' (auto-wait cap %dms)'%cap_ms)
        time.sleep(0.02)

def drill(path,ref):
    snapshot=read_json_file(path)
    if snapshot.get('backend')!='a11y' or time.time()-snapshot['created']>90:raise ValueError('stale accessibility snapshot')
    ref=parse_ref(snapshot,ref)
    item=next((e for e in snapshot['elements'] if e['ref']==ref),None)
    if item is None:raise ValueError('valid accessibility ref required')
    root=app(snapshot['pid']);element=resolve(root,item)
    return observe(snapshot['pid'],skeleton=True,subtree=(element,item['path']))

def act(path,actions):
    snapshot=read_json_file(path)
    if snapshot.get('backend')!='a11y' or time.time()-snapshot['created']>90:raise ValueError('stale accessibility snapshot')
    validate_actions(actions,'a11y')
    actions=[dict(a,ref=parse_ref(snapshot,a.get('ref'))) if isinstance(a,dict) else a for a in actions]
    root=app(snapshot['pid']);refs={e['ref']:e for e in snapshot['elements']}
    for a in actions:
        if a.get('type') not in ('click','set_text') or a.get('ref') not in refs:raise ValueError('click/set_text and valid ref required')
        e=resolve(root,refs[a['ref']])
        if a['type']=='set_text' and (not isinstance(a.get('text'),str) or len(a['text'])>10000 or not refs[a['ref']].get('editable')):raise ValueError('editable ref and text <=10000 required')
        if a['type']=='click' and not any(n.lower() in ('click','press','toggle') for n in refs[a['ref']]['actions']):raise ValueError('no native click action; use desktop pointer')
    complete,incomplete,errors=_completeness(snapshot)
    completed=0;result={'ok':True,'snapshot_complete':complete,'snapshot_incomplete':incomplete,'snapshot_read_errors':errors};start=time.monotonic()
    try:
        for a in actions:
            e=wait_actionable(root,refs[a['ref']])
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
    # An ordinary failure of the final observation keeps completed, timing and any
    # original action error. BaseException still propagates; the batch is never replayed.
    try:
        result['after']=observe(snapshot['pid'])
    except Exception as exc:
        result.update(ok=False,after_unavailable=True,capture_error=str(exc))
        result.setdefault('error','final observation failed: '+str(exc))
    return result

try:
    request=read_json(sys.stdin.buffer if hasattr(sys.stdin,'buffer') else sys.stdin)
    # An unknown operation must never reach act and mutate the desktop.
    operation=request.get('operation') if isinstance(request,dict) else None
    if operation not in ('apps','observe','drill','act','query','ground'):raise ValueError('unknown operation')
    if operation=='apps':result=[{'pid':a.get_process_id(),'name':a.get_name()} for a in applications()]
    elif operation=='observe':result=observe(request['pid'],skeleton=request.get('skeleton',False))
    elif operation=='query':result=query(request['pid'],request.get('name'),request.get('role'),request.get('limit',20))
    elif operation=='ground':result=ground(request['snapshot'],request['ref'])
    elif operation=='drill':result=drill(request['snapshot'],request['ref'])
    else:result=act(request['snapshot'],request['actions'])
    print(json.dumps(result,ensure_ascii=False,separators=(',',':')))
except Exception as exc:
    print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False));sys.exit(1)
