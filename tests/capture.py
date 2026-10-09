# Run: python3 tests/capture.py (no desktop or network).
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
from contextlib import nullcontext
from unittest.mock import patch
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cu',root/'scripts/cu.py')
cu=importlib.util.module_from_spec(spec);spec.loader.exec_module(cu)

def check(name):print('ok '+name)
def raises(message,fn):
    try:fn()
    except (RuntimeError,ValueError) as e:assert str(e)==message,str(e)
    else:raise AssertionError('expected '+message)

def encoded(image,kind):
    buf=io.BytesIO();image.save(buf,format=kind);return buf.getvalue()

ppm=b'P6\n# comment: longer than a fixed 17-byte header\n2 1\n255\n'+bytes([10,32,35,255,0,128])
image=Image.open(io.BytesIO(ppm)).convert('RGB')
assert image.size==(2,1) and image.tobytes()==bytes([10,32,35,255,0,128])
check('native PPM reader: long header, comment, exact pixels')
assert Image.open(io.BytesIO(encoded(image,'PNG'))).convert('RGB').tobytes()==image.tobytes()
check('PPM and PNG decode to identical pixels')

monitor={'id':0,'name':'test','width':1920,'height':1200,'scale':1,'x':0,'y':0}
client={'address':'0x1','monitor':0,'at':[0,0],'size':[1920,1200]}
base=Image.new('RGB',(1920,1200),'white')
actions=[{'type':'click','x':211,'y':211}]
with tempfile.TemporaryDirectory() as folder,patch.object(cu,'STATE',Path(folder)/'state'),patch.object(cu,'CANCEL',Path(folder)/'cancelled'):
    meta={'backend':'desktop','scope':'window','window':'0x1','window_bounds':[0,0,1920,1200],
          'monitor':'test','monitor_box':[0,0,1920,1200],'monitor_scale':1,'monitor_transform':0,'region':[0,0,1920,1200]}
    old=cu.save_observation(base,meta.copy(),1280)
    for name,changed,expected in [('unchanged',base,False),('global',Image.new('RGB',base.size,(240,240,240)),True),
                                  ('patch',base.copy(),True),('distant patch',base.copy(),False)]:
        if name in ('patch','distant patch'):
            x,y=(300,300) if name=='patch' else (1200,900)
            ImageDraw.Draw(changed).rectangle((x,y,x+35,y+35),fill='black')
        new,fresh=cu.save_observation(changed,meta.copy(),1280,persist=False)
        assert new.size==(1280,800)
        saved=cu.save_observation(new,fresh,1280)
        with Image.open(old['image']) as previous,Image.open(saved['image']) as disk:
            assert new.tobytes()==disk.tobytes()
            assert cu.screen_changed(previous,new,actions)==cu.screen_changed(previous,disk,actions)==expected
    check('resize and global/49x49 patch verdicts match memory and disk')

    with patch.object(cu,'check_cancel'),patch.object(cu,'hypr',return_value={'address':'0x1'}),patch.object(cu,'run') as dispatch:
        cu.focus({},'0x1');dispatch.assert_not_called()
    with patch.object(cu,'check_cancel'),patch.object(cu,'window',return_value=client),patch.object(cu,'hypr',side_effect=[{'address':'0x2'},{'address':'0x1'}]),patch.object(cu,'run',return_value='ok\n') as dispatch:
        cu.focus({},'0x1');assert dispatch.call_count==1
    check('focus: no redundant dispatch, verifies acknowledged focus')

    for screen in (False,True):
        pixels=[base]
        def hypr(env,what):return [monitor] if what=='monitors' else {'address':'0x1'}
        def grim(argv,env,text):
            assert argv==['grim','-s','1','-g','0,0 1920x1200','-t','ppm','-'] and text is False
            return encoded(pixels[0],'PPM')
        with patch.object(cu,'hypr',side_effect=hypr),patch.object(cu,'window',return_value=client),\
             patch.object(cu,'run',side_effect=grim),\
             patch.object(cu,'focus') as focus,patch.object(cu,'Pointer') as pointer:
            def observe(persist):
                return (cu.observe_screen({},'test',persist=persist) if screen else
                        cu.observe({},'0x1',activate=False,persist=persist))
            before=set(cu.STATE.iterdir())
            new,fresh=observe(False)
            assert set(cu.STATE.iterdir())==before and new.size==(1280,800)
            # Stop after comparison, before even constructing a virtual pointer.
            class Stop(Exception):pass
            def comparison(previous,current,batch):
                assert previous.size==current.size==(1280,800)
                assert previous.tobytes()==current.tobytes()
                assert set(cu.STATE.iterdir())==before
                raise Stop
            observed=observe(True);before=set(cu.STATE.iterdir())
            with patch.object(cu,'screen_changed',side_effect=comparison):
                try:cu.desktop_act({},observed,actions)
                except Stop:pass
                else:raise AssertionError('comparison not reached')
            pointer.assert_not_called()
            pixels[0]=Image.new('RGB',base.size,'black')
            result=cu.desktop_act({},observed,actions)
            assert result['ok'] is False and result['completed']==0
            after=result['after']
            assert len(set(cu.STATE.iterdir())-before)==2
            with Image.open(after['image']) as saved:
                assert saved.format=='PNG' and saved.size==(1280,800)
            compact=cu.compact_result(result)['after']
            assert compact['region']==[0,0,1920,1200] and compact['scale']==round(1280/1920,6)
            pointer.assert_not_called()
            if screen:focus.assert_not_called()
            else:assert focus.call_count==2
    check('window/screen pre-action capture writes nothing; refusal saves readable PNG and scale')

    # Capture has no overlay discovery, IPC or cursor configuration dependencies.
    with patch.object(cu,'hypr',return_value=[monitor]),patch.object(cu,'run',return_value=encoded(base,'PPM')) as capture:
        cu.observe_screen({},'test',persist=False)
        assert capture.call_count==1 and capture.call_args.args[0][0]=='grim'
    check('capture only invokes grim; no overlay hot path remains')

    moved=dict(client,at=[1,0])
    with patch.object(cu,'hypr',return_value=[monitor]),patch.object(cu,'window',side_effect=[client,moved]),patch.object(cu,'run',return_value=encoded(base,'PPM')):
        raises('window moved during capture; observe again',lambda:cu.observe({},'0x1',activate=False,persist=False))
    check('capture body geometry error remains unmasked')

    raises('python3: {"ok":false,"error":"validation reason"}',lambda:cu.run_cancelable(
        [sys.executable,'-c','import sys; print(\'{"ok":false,"error":"validation reason"}\'); sys.exit(1)']))
    check('failed adapter stdout survives in error')
    for typ,field,value,expected in [('assert','timeout_ms',3000,60),('assert','timeout_ms',9000,60),('wait','ms',2000,60)]:
        with patch.object(cu,'run_cancelable',return_value='{}') as adapter:
            cu.browser({'actions':[{'type':typ,field:value}]*32})
            assert adapter.call_args.kwargs['timeout']==expected
    check('browser timeout clamps 32 asserts/waits to 60 seconds')
    # urllib is imported lazily inside browser_start, so patch the module itself
    # rather than a name on cu, which no longer exists at import time.
    with patch('urllib.request.urlopen',return_value=io.StringIO('{}')) as urlopen:
        assert cu.browser_start({},'http://[::1]:9222')['reused'] is True
        assert urlopen.call_args.args[0]=='http://[::1]:9222/json/version'
    check('IPv6 loopback endpoint accepted and probed unchanged')

subprocess.run(['node',str(root/'tests/cdp_keys.mjs')],check=True)
subprocess.run(['node',str(root/'tests/cdp_validation.mjs')],check=True)
print('all capture/adapter regressions pass')
