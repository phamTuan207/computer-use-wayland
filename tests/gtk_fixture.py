import json
import os
from pathlib import Path
import sys
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Gdk

path=Path(sys.argv[1]);events=[];state={'pid':os.getpid(),'clicks':0,'text':'','events':events}
def save():path.write_text(json.dumps(state,ensure_ascii=False))
win=Gtk.Window(title='Computer Use Keyboard Lab');win.set_default_size(680,360)
box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=15);box.set_border_width(30);win.add(box)
entry=Gtk.Entry();entry.get_accessible().set_name('Test entry');box.pack_start(entry,False,False,0)
button=Gtk.Button(label='Test button');box.pack_start(button,False,False,0)
label=Gtk.Label(label='Keyboard and accessibility test');box.pack_start(label,True,True,0)
def changed(e):
    state['text']=e.get_text();state.setdefault('history',[]).append(state['text']);save()
def clicked(b):state['clicks']+=1;save()
def key(w,e):
    events.append({'key':Gdk.keyval_name(e.keyval),'ctrl':bool(e.state&Gdk.ModifierType.CONTROL_MASK),'shift':bool(e.state&Gdk.ModifierType.SHIFT_MASK),'alt':bool(e.state&Gdk.ModifierType.MOD1_MASK),'type':int(e.type)});save()
    # Record function keys without opening help or affecting the desktop.
    return Gdk.keyval_name(e.keyval) in ('F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12')
entry.connect('changed',changed);button.connect('clicked',clicked)
def focused(w,e):
    state['focus']='entry' if e==entry else 'button' if e==button else None;save()
win.connect('set-focus',focused)
win.connect('key-press-event',key);win.connect('key-release-event',key);win.connect('destroy',Gtk.main_quit)
win.show_all();entry.grab_focus();save();Gtk.main()
