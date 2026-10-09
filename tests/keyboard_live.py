import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cu',ROOT/'scripts/cu.py');cu=importlib.util.module_from_spec(spec);spec.loader.exec_module(cu)

def main():
    env=cu.environment();env.pop('GTK_IM_MODULE',None);env['GTK_A11Y']='1'
    original=cu.hypr(env,'activewindow').get('address')
    with tempfile.TemporaryDirectory(prefix='cu-keyboard-') as tmp:
        state=Path(tmp)/'state.json'
        p=subprocess.Popen(['python3',str(ROOT/'tests/gtk_fixture.py'),str(state)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        report={}
        try:
            for _ in range(60):
                clients=cu.hypr(env,'clients');c=next((c for c in clients if c.get('title')=='Computer Use Keyboard Lab'),None)
                if c and state.exists():break
                time.sleep(.1)
            else:raise RuntimeError('GTK test fixture unavailable')
            address=c['address'];cu.focus(env,address);time.sleep(.3)
            actions=[{'type':'type','text':'abc Việt'},{'type':'key','keys':['CTRL','a']},{'type':'type','text':'abcdef'},{'type':'key','keys':['Home']},{'type':'key','keys':['Shift','ArrowRight'],'repeat':3},{'type':'key','keys':['Delete']},{'type':'key','keys':['End']},{'type':'key','keys':['Backspace']},{'type':'key','keys':['Enter']},{'type':'key','keys':['F1'],'hold_ms':70},{'type':'key','keys':['PageUp']},{'type':'key','keys':['PageDown']},{'type':'key','keys':['Tab']},{'type':'key','keys':['Shift','Tab']}]
            obs=cu.observe(env,address);r=cu.desktop_act(env,obs,actions);assert r['ok'],r
            data=json.loads(state.read_text());assert data['text']=='de',{'text':data['text'],'history':data.get('history')}
            pressed=[e for e in data['events'] if e['type']==8]
            expected=['Return','F1','Page_Up','Page_Down','Tab']
            for key in expected:assert any(e['key']==key for e in pressed),(key,pressed)
            assert any(e['key']=='a' and e['ctrl'] for e in pressed),pressed
            assert sum(e['key']=='Right' and e['shift'] for e in pressed)==3,pressed
            assert any(e['key'] in ('Tab','ISO_Left_Tab') and e['shift'] for e in pressed),pressed
            report.update(keyboard_actions=len(actions),keyboard_groups=len(cu.keyboard_groups(actions)),execution_ms=r['execution_ms'],verified_text=data['text'],keys_verified=expected+['Ctrl+A','Shift+Right x3','Delete','End','Backspace'])
            assert data.get('focus')=='entry',data.get('focus')
            report['tab_reverse_focus_verified']=True
            # Catch GTK's failure for a binding in the final real keymap slot.
            # Each command gets its own fresh wtype keymap, not a trailing real key.
            # GTK selects the entry's contents when focus returns: End first
            # collapses that selection before testing one-character Backspace.
            for keys,text in [(['End'],'de'),(['Backspace'],'d'),(['Home'],'d'),(['Delete'],'')]:
                r=cu.desktop_act(env,cu.observe(env,address),[{'type':'key','keys':keys}]);assert r['ok'],r
                data=json.loads(state.read_text());assert data['text']==text,(keys,data['text'],data.get('focus'))
            report['standalone_editing_keys']=True
            # A semantic field setter bypasses keyboard/layout/emoji conversion entirely.
            def a11y(req):
                r=subprocess.run(['python3',str(ROOT/'scripts/a11y.py')],env=env,input=json.dumps(req),capture_output=True,text=True,timeout=12)
                if not r.stdout:raise RuntimeError(r.stderr)
                return json.loads(r.stdout)
            s=a11y({'operation':'observe','pid':p.pid});assert s.get('elements'),s
            entry=next(e['ref'] for e in s['elements'] if e['name']=='Test entry');button=next(e['ref'] for e in s['elements'] if e['name']=='Test button')
            r=a11y({'operation':'act','snapshot':s['snapshot'],'actions':[{'type':'set_text','ref':entry,'text':'Tiếng Việt 🐱'},{'type':'click','ref':button}]});assert r['ok'],r
            time.sleep(.1);data=json.loads(state.read_text());assert data['text']=='Tiếng Việt 🐱' and data['clicks']==1,data
            report['a11y_unicode_and_button']=True;report['a11y_execution_ms']=r['execution_ms']
            print(json.dumps(report,ensure_ascii=False,indent=2));(ROOT/'tests/keyboard-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        finally:
            p.terminate();p.wait(timeout=5)
            if original:
                try:cu.focus(env,original)
                except Exception:pass

if __name__=='__main__':main()
