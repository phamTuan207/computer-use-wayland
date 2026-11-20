#!/usr/bin/env python3
"""Move-only calibration client for the planned session broker.

This file performs no desktop work at import time. Its live entry point requires
an existing broker lease; offline tests inject a fake client and image capture.
"""
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import statistics
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import cu

WINDOW_RE=re.compile(r'0x[0-9a-fA-F]+')
PENDING={'accepted','running','pending'}
DONE={'complete','completed','done'}
WIDTHS=(960,1280,1920)
SAFE_POINTS=((.15,.15),(.5,.25),(.8,.5),(.25,.8),(.85,.85))


class CalibrationError(RuntimeError):
    pass


class BrokerClient:
    """Submit existing driver envelopes through session_remote.py."""
    def __init__(self,lease_file,*,python=sys.executable,broker_script=None,
                 poll_interval=.1,timeout=180):
        self.lease_file=Path(lease_file)
        self.python=python
        self.broker_script=Path(broker_script or ROOT/'scripts/session_remote.py')
        self.poll_interval=poll_interval
        self.timeout=timeout
        self.sequence=1

    def _cli(self,args):
        process=subprocess.run([self.python,str(self.broker_script),*args],
                               capture_output=True,text=True,timeout=15)
        try:body=json.loads(process.stdout) if process.stdout.strip() else {}
        except ValueError as exc:raise CalibrationError('broker returned invalid JSON') from exc
        if process.returncode:
            detail=body.get('error') if isinstance(body,dict) else None
            raise CalibrationError('broker command failed'+(': '+str(detail)[:300] if detail else ''))
        if not isinstance(body,dict):raise CalibrationError('broker response must be an object')
        if body.get('ok') is False:raise CalibrationError('broker refused request: '+str(body.get('error','unknown error'))[:300])
        return body

    @staticmethod
    def _status(response):
        status=response.get('status') or response.get('state')
        if not isinstance(status,str):return None
        return status.lower()

    def _driver_result(self,response):
        for key in ('response','driver_response','driver_result'):
            nested=response.get(key)
            if isinstance(nested,dict):
                response=nested
                break
        if isinstance(response.get('returncode'),int):
            if response['returncode']!=0:
                result=response.get('result')
                detail=result.get('error') if isinstance(result,dict) else None
                raise CalibrationError('driver command failed'+(': '+str(detail)[:300] if detail else ''))
            return response.get('result')
        nested=response.get('result')
        if isinstance(nested,dict) and isinstance(nested.get('returncode'),int):
            return self._driver_result(nested)
        if 'result' in response and self._status(response) in DONE:
            return response['result']
        if self._status(response) in DONE:
            return response.get('value',response)
        return response

    def run(self,args,stdin=''):
        if not isinstance(args,list) or not args or not all(isinstance(a,str) for a in args):
            raise CalibrationError('broker command arguments must be strings')
        if not isinstance(stdin,str):raise CalibrationError('broker stdin must be text')
        with tempfile.TemporaryDirectory(prefix='cu-calibration-') as folder:
            os.chmod(folder,0o700)
            request=Path(folder)/'request.json'
            raw=json.dumps({'args':args,'stdin':stdin,'image_policy':'always'},separators=(',',':')).encode()
            fd=os.open(request,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'wb') as stream:stream.write(raw)
            seq=self.sequence
            accepted=self._cli(['request','--lease-file',str(self.lease_file),
                                '--sequence',str(seq),'--request',str(request)])
            status=self._status(accepted)
            if status in PENDING:
                deadline=time.monotonic()+self.timeout
                while True:
                    if time.monotonic()>=deadline:
                        raise CalibrationError('broker result timed out; request outcome is unknown and was not replayed')
                    response=self._cli(['result','--lease-file',str(self.lease_file),'--sequence',str(seq)])
                    if self._status(response) not in PENDING:break
                    time.sleep(self.poll_interval)
            else:response=accepted
            self.sequence+=1
            return self._driver_result(response)


def _desktop_state(client):
    doctor=client.run(['doctor'])
    if not isinstance(doctor,dict) or doctor.get('cursorpos_error') or not isinstance(doctor.get('cursorpos'),dict):
        raise CalibrationError('broker did not return a cursor position')
    point=doctor['cursorpos']
    for key in ('x','y'):
        value=point.get(key)
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
            raise CalibrationError('broker returned an invalid cursor position')
    return {'cursorpos':{'x':point['x'],'y':point['y']},
            'active_window':doctor.get('active_window')}


def _cursorpos(client):
    return _desktop_state(client)['cursorpos']


def _check_cancel(client):
    status=client.run(['status'])
    if not isinstance(status,dict) or status.get('cancelled') is not False:
        raise CalibrationError('task cancellation or status is unknown; stopping calibration')


def _environment_from_observation(meta):
    identity=meta.get('capture_compositor')
    if not isinstance(identity,dict):
        raise CalibrationError('observation has no compositor identity')
    values={'XDG_RUNTIME_DIR':identity.get('runtime_dir'),
            'WAYLAND_DISPLAY':identity.get('wayland_display'),
            'HYPRLAND_INSTANCE_SIGNATURE':identity.get('instance')}
    if not all(isinstance(value,str) and value for value in values.values()):
        raise CalibrationError('observation has an incomplete compositor identity')
    return values


def _observation(client,window,width,crop=None,clock=time.monotonic):
    args=['observe','--window',window,'--focus','--max-width',str(width)]
    if crop is not None:args+=['--crop',*(str(value) for value in crop)]
    result=client.run(args)
    image_received=clock()
    if not isinstance(result,dict) or result.get('ok') is False:
        raise CalibrationError('broker did not return a desktop observation')
    required=('image','observation','image_size','region','window','window_bounds',
              'monitor','monitor_box','monitor_scale','monitor_transform','id',
              'image_format','image_bytes','image_sha256','observation_schema',
              'capture_boot_id','capture_started_monotonic','capture_started_wall',
              'capture_compositor')
    if any(key not in result for key in required):
        raise CalibrationError('broker observation is missing coordinate identity')
    if result['window']!=window:raise CalibrationError('observation belongs to another window')
    path=Path(result['observation'])
    try:meta=cu.read_json_file(path)
    except (OSError,ValueError) as exc:raise CalibrationError('observation metadata is unavailable') from exc
    if cu.compact_result(meta)!=result:
        raise CalibrationError('returned metadata does not match the saved observation')
    try:cu.validate_desktop_observation(meta,_environment_from_observation(meta),result['observation'])
    except (OSError,ValueError,RuntimeError) as exc:
        raise CalibrationError('observation is stale or failed its identity checks') from exc
    try:
        image_bytes=Path(result['image']).read_bytes()
        if (result['image_format']!='JPEG' or len(image_bytes)!=result['image_bytes'] or
                hashlib.sha256(image_bytes).hexdigest()!=result['image_sha256']):
            raise CalibrationError('returned image does not match its metadata')
        from PIL import Image
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.load()
            if image.format!='JPEG' or image.mode!='RGB' or list(image.size)!=result['image_size']:
                raise CalibrationError('returned image dimensions or format do not match')
    except OSError as exc:raise CalibrationError('returned image is unavailable') from exc
    return result,meta,image_received


def _crop_for_window(window_bounds):
    _,_,width,height=window_bounds
    crop_width=max(1,round(width*.6));crop_height=max(1,round(height*.6))
    return [round((width-crop_width)/2),round((height-crop_height)/2),crop_width,crop_height]


def _cursor_visible(screenshot,clean,monitor_box,actual):
    from PIL import Image,ImageChops
    try:
        with Image.open(screenshot) as raw,Image.open(clean) as clear:
            raw.load();clear.load()
            if raw.size!=clear.size:return None
            mx,my,mw,mh=monitor_box
            if list(raw.size)!=[mw,mh]:return None
            x=round(actual['x']-mx);y=round(actual['y']-my)
            patch=(max(0,x-14),max(0,y-14),min(raw.width,x+15),min(raw.height,y+15))
            return ImageChops.difference(raw.crop(patch),clear.crop(patch)).getbbox() is not None
    except (OSError,ValueError):return None


def grim_capture(monitor,path):
    process=subprocess.run(['grim','-c','-o',monitor,str(path)],capture_output=True,
                           text=True,timeout=15)
    if process.returncode:raise CalibrationError('cursor-visible grim capture failed')
    if not Path(path).is_file():raise CalibrationError('grim did not write the evidence image')


def _validate_input(args):
    if not isinstance(args.window,str) or not WINDOW_RE.fullmatch(args.window):
        raise CalibrationError('an exact window address is required')
    if not args.widths or any(isinstance(w,bool) or not isinstance(w,int) or not 320<=w<=3840 for w in args.widths):
        raise CalibrationError('widths must be integers from 320 to 3840')
    if len(set(args.widths))!=len(args.widths):raise CalibrationError('widths must not repeat')
    if isinstance(args.samples,bool) or not isinstance(args.samples,int) or args.samples<1 or args.samples>100:
        raise CalibrationError('samples must be 1..100')


def _summary(values):
    values=sorted(value for value in values if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value))
    if not values:return {'count':0,'p50':None,'p95':None}
    return {'count':len(values),'p50':statistics.median(values),
            'p95':values[max(0,math.ceil(.95*len(values))-1)]}


def _phase_summaries(samples):
    fields={'capture_ms':('server_phases_ms','capture_ms'),
            'decode_ms':('server_phases_ms','decode_ms'),
            'encode_ms':('server_phases_ms','encode_ms'),
            'preflight_ms':('action_phases_ms','preflight_ms'),
            'execution_ms':('action_phases_ms','execution_ms'),
            'image_to_submit_ms':('client_timing','image_to_submit_ms'),
            'reasoning_ms':('client_timing','reasoning_ms'),
            'submit_to_result_ms':('client_timing','submit_to_result_ms'),
            'image_bytes':(None,'image_bytes')}
    return {name:_summary([sample.get(field) if container is None else
                           sample.get(container,{}).get(field) for sample in samples])
            for name,(container,field) in fields.items()}


def _cursor_visual_status(samples,measure_only):
    if measure_only:return 'not checked'
    values=[sample.get('cursor_evidence',{}).get('cursor_visible') for sample in samples
            if isinstance(sample.get('cursor_evidence'),dict)]
    if not values:return 'incomplete'
    if all(value is True for value in values):return 'cursor visible in paired evidence'
    if any(value is False for value in values):return 'incomplete: cursor absent from paired evidence'
    return 'incomplete: cursor visibility could not be measured'


def run_calibration(args,client=None,cursor_capture=grim_capture,clock=time.monotonic):
    """Run calibration with injected broker/capture boundaries for offline tests."""
    _validate_input(args)
    client=client or BrokerClient(args.lease_file)
    _check_cancel(client)
    windows=client.run(['windows','--class','local.computeruse.Demo','--no-titles'])
    if not isinstance(windows,list):raise CalibrationError('fixture discovery returned no window list')
    fixtures=[row for row in windows if isinstance(row,dict) and row.get('address')==args.window]
    if len(fixtures)!=1:raise CalibrationError('window is not the unique inert calibration fixture')
    row=fixtures[0]
    bounds=row.get('at',[])+row.get('size',[]) if isinstance(row.get('at'),list) and isinstance(row.get('size'),list) else None
    if not isinstance(bounds,list) or len(bounds)!=4 or any(isinstance(v,bool) or not isinstance(v,int) for v in bounds) or bounds[2]<=0 or bounds[3]<=0:
        raise CalibrationError('fixture window geometry is invalid')
    output=Path(args.output)
    evidence_dir=output.parent/(output.stem+'-evidence')
    if not args.measure_only:
        evidence_dir.mkdir(mode=0o700,parents=True,exist_ok=False)
    samples=[];pinned_identity=None
    profiles=[('window',None)] if args.measure_only else [('window',None),('crop',_crop_for_window(bounds))]
    per_width=args.samples if args.measure_only else 5
    report={'schema':1,'ok':False,'window':args.window,'window_bounds':bounds,
            'widths':args.widths,'measure_only':bool(args.measure_only),
            'samples_requested_per_width':per_width,'samples':samples,
            'reasoning_mode':'scripted safe point selection',
            'cursor_visual_acceptance':'not checked' if args.measure_only else 'incomplete'}
    try:
        for width in args.widths:
            for profile,crop in profiles:
                for index in range(per_width):
                    _check_cancel(client)
                    observation,meta,image_received=_observation(client,args.window,width,crop,clock)
                    identity=(meta.get('capture_boot_id'),meta.get('capture_compositor'))
                    if pinned_identity is None:pinned_identity=identity
                    elif identity!=pinned_identity:raise CalibrationError('compositor instance changed during calibration')
                    if meta.get('window_bounds')!=bounds:raise CalibrationError('fixture geometry changed during calibration')
                    iw,ih=meta['image_size']
                    fx,fy=SAFE_POINTS[index%len(SAFE_POINTS)]
                    x=min(iw-1,max(0,round((iw-1)*fx)))
                    y=min(ih-1,max(0,round((ih-1)*fy)))
                    intended=cu.image_point(meta,x,y)
                    reasoning_finished=clock()
                    before_state=_desktop_state(client)
                    if before_state['active_window']!=args.window:
                        raise CalibrationError('fixture lost active window before move')
                    cursor_before=before_state['cursorpos']
                    payload=json.dumps([{'type':'move','x':x,'y':y}],separators=(',',':'))
                    submit=clock()
                    acted=client.run(['act','--observation',observation['observation'],
                                      '--actions','-','--no-after'],stdin=payload)
                    result_received=clock()
                    if not isinstance(acted,dict) or acted.get('ok') is not True or acted.get('completed')!=1:
                        raise CalibrationError('move-only action was refused or incomplete')
                    after_state=_desktop_state(client)
                    actual=after_state['cursorpos']
                    error=math.hypot(actual['x']-intended[0],actual['y']-intended[1])
                    sample={'width':width,'scope':profile,'crop':crop,'point_image':[x,y],
                            'intended_global':[intended[0],intended[1]],'cursor_before':cursor_before,
                            'actual_global':[actual['x'],actual['y']],
                            'error_euclidean':error,'observation_id':observation['id'],
                            'observation_path':observation['observation'],'image_path':observation['image'],
                            'observation_created':observation.get('created'),
                            'capture_started_monotonic':observation.get('capture_started_monotonic'),
                            'capture_started_wall':observation.get('capture_started_wall'),
                            'active_window_before':before_state['active_window'],
                            'active_window_after':after_state['active_window'],
                            'capture_identity':identity,'image_size':observation['image_size'],
                            'region':observation['region'],'monitor_box':observation['monitor_box'],
                            'monitor_scale':observation['monitor_scale'],
                            'monitor_transform':observation['monitor_transform'],
                            'image_bytes':observation['image_bytes'],'image_sha256':observation['image_sha256'],
                            'server_phases_ms':{key:observation.get(key) for key in
                                ('capture_ms','decode_ms','encode_ms','capture_elapsed_ms')},
                            'action_phases_ms':{key:acted.get(key) for key in
                                ('preflight_ms','execution_ms','after_capture_ms')},
                            'client_timing':{'image_received':image_received,
                                'reasoning_finished':reasoning_finished,'submit':submit,
                                'result_received':result_received,
                                'image_to_submit_ms':(submit-image_received)*1000,
                                'reasoning_ms':(reasoning_finished-image_received)*1000,
                                'submit_to_result_ms':(result_received-submit)*1000}}
                    if error>3:
                        sample['status']='pointer miss; no click was sent'
                        samples.append(sample)
                        raise CalibrationError('pointer error exceeded 3 logical pixels')
                    sample['status']='move passed'
                    samples.append(sample)
                    if after_state['active_window']!=args.window:
                        sample['status']='active window changed after move'
                        raise CalibrationError('fixture lost active window after move')
                    if not args.measure_only:
                        _check_cancel(client)
                        before_evidence_state=_desktop_state(client)
                        if before_evidence_state['active_window']!=args.window:
                            raise CalibrationError('fixture lost active window before cursor evidence')
                        before_evidence=before_evidence_state['cursorpos']
                        if math.hypot(before_evidence['x']-actual['x'],
                                      before_evidence['y']-actual['y'])>3:
                            raise CalibrationError('cursor moved before paired evidence')
                        shot=evidence_dir/f'{width}-{profile}-{index+1}-cursor.png'
                        cursor_capture(observation['monitor'],shot)
                        _check_cancel(client)
                        after_evidence_state=_desktop_state(client)
                        after_evidence=after_evidence_state['cursorpos']
                        if after_evidence_state['active_window']!=args.window:
                            raise CalibrationError('fixture lost active window after cursor evidence')
                        if math.hypot(after_evidence['x']-actual['x'],
                                      after_evidence['y']-actual['y'])>3:
                            raise CalibrationError('cursor moved during paired evidence')
                        clean_result=client.run(['observe','--screen',observation['monitor'],
                                                 '--max-width','3840'])
                        if (not isinstance(clean_result,dict) or not clean_result.get('image') or
                                    clean_result.get('scope')!='screen' or
                                    clean_result.get('monitor')!=observation['monitor'] or
                                    clean_result.get('monitor_box')!=observation['monitor_box'] or
                                    clean_result.get('capture_compositor')!=observation['capture_compositor'] or
                                    clean_result.get('capture_boot_id')!=observation['capture_boot_id']):
                            raise CalibrationError('clean paired observation was unavailable')
                        try:
                            clean_meta=cu.read_json_file(clean_result['observation'])
                            if cu.compact_result(clean_meta)!=clean_result:
                                raise CalibrationError('clean paired metadata changed')
                            cu.validate_desktop_observation(
                                clean_meta,_environment_from_observation(clean_meta),
                                clean_result['observation'])
                        except (KeyError,OSError,ValueError,RuntimeError) as exc:
                            raise CalibrationError('clean paired observation failed identity checks') from exc
                        clean=evidence_dir/f'{width}-{profile}-{index+1}-clean.jpg'
                        clean_bytes=Path(clean_result['image']).read_bytes()
                        if (clean_result.get('image_format')!='JPEG' or
                                len(clean_bytes)!=clean_result.get('image_bytes') or
                                hashlib.sha256(clean_bytes).hexdigest()!=clean_result.get('image_sha256')):
                            raise CalibrationError('clean paired observation failed image identity checks')
                        fd=os.open(clean,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                        with os.fdopen(fd,'wb') as stream:stream.write(clean_bytes)
                        cursor_bytes=Path(shot).read_bytes()
                        sample['cursor_evidence']={'path':str(shot),'clean_path':str(clean),
                                'cursor_bytes':len(cursor_bytes),
                                'cursor_sha256':hashlib.sha256(cursor_bytes).hexdigest(),
                                'clean_bytes':len(clean_bytes),
                                'clean_sha256':hashlib.sha256(clean_bytes).hexdigest(),
                                'cursor_before':[before_evidence['x'],before_evidence['y']],
                                'cursor_after':[after_evidence['x'],after_evidence['y']],
                                'active_window_before':before_evidence_state['active_window'],
                                'active_window_after':after_evidence_state['active_window'],
                                'cursor_visible':_cursor_visible(shot,clean,observation['monitor_box'],actual)}
                        report['cursor_visual_acceptance']=_cursor_visual_status(samples,args.measure_only)
        report.update(ok=True,capture_identity=pinned_identity,
                      max_error=max((row['error_euclidean'] for row in samples),default=0),
                      sample_count=len(samples),phase_summaries=_phase_summaries(samples),
                      cursor_visual_acceptance=_cursor_visual_status(samples,args.measure_only))
        return report
    except BaseException as exc:
        report.update(ok=False,error=str(exc),capture_identity=pinned_identity,
                      max_error=max((row['error_euclidean'] for row in samples),default=None),
                      sample_count=len(samples),phase_summaries=_phase_summaries(samples),
                      cursor_visual_acceptance=_cursor_visual_status(samples,args.measure_only))
        return report


def write_report(path,report):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write('\n')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lease-file',required=True)
    parser.add_argument('--window',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--widths',nargs='+',type=int,default=list(WIDTHS))
    parser.add_argument('--measure-only',action='store_true')
    parser.add_argument('--samples',type=int,default=20,
                        help='move-only samples per width in measurement mode (1..100)')
    args=parser.parse_args(argv)
    report=None
    try:
        lease=Path(args.lease_file)
        if lease.is_symlink() or not lease.is_file():raise CalibrationError('private broker lease file is unavailable')
        import stat
        lease_stat=lease.stat()
        if lease_stat.st_uid!=os.geteuid() or stat.S_IMODE(lease_stat.st_mode)!=0o600:
            raise CalibrationError('broker lease file must be owned by this user with mode 0600')
        output=Path(args.output)
        if output.exists() or output.is_symlink():raise CalibrationError('output report already exists')
        report=run_calibration(args)
    except BaseException as exc:
        if report is None:report={'schema':1,'ok':False,'error':str(exc),'samples':[],'sample_count':0}
        try:write_report(args.output,report)
        except FileExistsError:pass
        print(json.dumps({'ok':False,'error':str(exc),'output':args.output}),file=sys.stderr)
        return 1
    write_report(args.output,report)
    if not report.get('ok'):
        print(json.dumps({'ok':False,'error':report.get('error','calibration failed'),
                          'output':args.output,'sample_count':report.get('sample_count',0)}),file=sys.stderr)
        return 1
    print(json.dumps({'ok':True,'output':args.output,'sample_count':report['sample_count'],
                      'max_error':report['max_error']}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
