"""Zen in a disposable profile: Bamboo, literal text, draft/submit, wheel scroll."""
import sys,json,subprocess,tempfile,time,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import cu
ROOT=Path(__file__).resolve().parents[1]

def main():
 env=cu.environment();env.pop('GTK_IM_MODULE',None)
 original=cu.hypr(env,'activewindow').get('address')
 initial=cu.run(['fcitx5-remote'],env).strip();name=cu.run(['fcitx5-remote','-n'],env).strip()
 with tempfile.TemporaryDirectory(prefix='cu-zen-') as tmp:
  profile=Path(tmp)/'profile';profile.mkdir()
  (profile/'user.js').write_text('user_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.startup.homepage_override.mstone", "ignore");\nuser_pref("zen.welcome-screen.seen", true);\n')
  log=open(Path(tmp)/'zen.log','w')
  p=subprocess.Popen(['zen-browser','--no-remote','--profile',str(profile),(ROOT/'tests/exact_fixture.html').as_uri()],env=env,stdout=log,stderr=log)
  try:
   for _ in range(150):
    c=next((c for c in cu.hypr(env,'clients') if c.get('pid')==p.pid and c.get('title','').startswith('CU Exact Lab|')),None)
    if c:break
    if p.poll() is not None:raise RuntimeError('isolated Zen exited')
    time.sleep(.1)
   else:raise RuntimeError('isolated Zen fixture unavailable')
   address=c['address'];cu.focus(env,address);time.sleep(.5)
   def data():
    return json.loads(cu.window(env,address)['title'].split('|',1)[1].rsplit(' — ',1)[0])
   def until(predicate):
    deadline=time.monotonic()+2
    while True:
     d=data()
     if predicate(d):return d
     if time.monotonic()>deadline:raise AssertionError(d)
     time.sleep(.02)
   cu.run(['fcitx5-remote','-s','bamboo'],env);cu.run(['fcitx5-remote','-o'],env);time.sleep(.1)
   assert cu.run(['fcitx5-remote','-n'],env).strip()=='bamboo'
   # Verify the user's manual toggle twice; no change to their binding/config.
   state=cu.run(['fcitx5-remote'],env).strip()
   for expected in ('1','2'):
    cu.run(cu.keyboard_argv([{'type':'key','keys':['Ctrl','space']}]),env);time.sleep(.1)
    assert cu.run(['fcitx5-remote'],env).strip()==expected
   texts=['test computer use-sent via codex','Tiếng Việt có dấu','https://example.org/test?x=1','--test literal']*3
   times=[];full=[];compact=[]
   for text in texts:
    obs=cu.observe(env,address,max_width=960)
    a=[{'type':'key','keys':['Ctrl','a']},{'type':'type','text':text}]
    start=time.monotonic();r=cu.desktop_act(env,obs,a);times.append(round((time.monotonic()-start)*1000));assert r['ok'],r
    until(lambda d:d['text']==text and d['sent']==0)
    assert cu.run(['fcitx5-remote'],env).strip()=='2'
    full.append(len(json.dumps(r)));compact.append(len(json.dumps(cu.compact_result(r))))
   cli='computer-use'
   compact_obs=json.loads(cu.run([cli,'observe','--window',address,'--max-width','960'],env))
   assert 'window_bounds' not in compact_obs and Path(compact_obs['observation']).exists()
   r=json.loads(cu.run([cli,'act','--observation',compact_obs['observation'],'--actions','-'],env,input=json.dumps([{'type':'key','keys':['Ctrl','a']},{'type':'type','text':'CLI exact test'}])))
   assert r['ok'] and 'window_bounds' not in r['after'],r;until(lambda d:d['text']=='CLI exact test')
   obs=cu.observe(env,address,max_width=960)
   r=cu.desktop_act(env,obs,[{'type':'key','keys':['Ctrl','a']},{'type':'type','text':'chaof ','ime':'compose'}]);assert r['ok'],r;until(lambda d:d['text']=='chào ')
   obs=cu.observe(env,address,max_width=960);r=cu.desktop_act(env,obs,[{'type':'key','keys':['Enter']}]);assert r['ok'],r;until(lambda d:d['sent']==1)
   c=cu.window(env,address);d=data();obs=cu.observe(env,address,max_width=960)
   # Locate this fixture's unique magenta border in the actual saved image;
   # browser chrome/privacy coordinates are not a reliable screen origin.
   from PIL import Image,ImageChops
   red,green,blue=Image.open(obs['image']).convert('RGB').split()
   marker=ImageChops.multiply(ImageChops.multiply(red.point(lambda p:255 if p>220 else 0),green.point(lambda p:255 if p<30 else 0)),blue.point(lambda p:255 if p>220 else 0)).getbbox()
   assert marker,'fixture marker missing'
   x=(marker[0]+marker[2])/2;y=(marker[1]+marker[3])/2
   r=cu.desktop_act(env,obs,[{'type':'scroll','x':x,'y':y,'dy':180}]);assert r['ok'],r;until(lambda d:d['scroll']>0)
   for i in range(20):
    time.sleep(.15)
    before=data()['scroll'];dy=-90 if i%2==0 else 90
    obs=cu.observe(env,address,max_width=960)
    r=cu.desktop_act(env,obs,[{'type':'scroll','x':x,'y':y,'dy':dy}]);assert r['ok'],r
    until(lambda d:d['scroll']<before if dy<0 else d['scroll']>before)
   report={'browser':'Zen disposable profile','bamboo_literal_cases':len(texts),'ime_restored':True,'ctrl_space_roundtrip':True,'telex_compose':True,'compact_cli_roundtrip':True,'separate_local_submission':True,'nested_wheel_scroll_cases':21,'median_batch_ms':round(statistics.median(times)),'max_batch_ms':max(times),'mean_verbose_chars':round(statistics.mean(full)),'mean_compact_chars':round(statistics.mean(compact))}
   (ROOT/'tests/optimization-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
  except Exception:
   if 'obs' in locals():
    info={'client':cu.window(env,address),'page':data(),'image':obs['image']}
    (ROOT/'tests/zen-diagnostic.json').write_text(json.dumps(info))
   raise
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:p.kill();p.wait()
   log.close()
   if original:cu.focus(env,original)
   if name:cu.run(['fcitx5-remote','-s',name],env)
   if initial in ('1','2'):cu.run(['fcitx5-remote','-o' if initial=='2' else '-c'],env)

if __name__=='__main__':main()
