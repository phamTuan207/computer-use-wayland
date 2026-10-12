"""Owned, inert GTK4 fixture. Reset commands arrive on stdin, state stays local."""
import json
import os
from pathlib import Path
import sys

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gio, GLib, Gtk


def main():
    path = Path(sys.argv[1])
    state = {'nonce': '', 'text': '', 'clicks': 0, 'scroll': 0, 'drag': [100, 40]}
    widgets = {}
    pending = [False]
    origin = [0, 0]
    app = Gtk.Application(application_id='local.computeruse.Optimization',
                          flags=Gio.ApplicationFlags.NON_UNIQUE)

    def save():
        pending[0] = False
        if 'window' not in widgets:
            return False
        win = widgets['window']
        layout = {}
        for name in ('entry', 'button', 'scrollbox', 'canvas'):
            ok, bounds = widgets[name].compute_bounds(win)
            if not ok:
                return False
            layout[name] = [bounds.get_x(), bounds.get_y(), bounds.get_width(), bounds.get_height()]
        state['layout'] = layout
        state['text'] = widgets['entry'].get_text()
        state['scroll'] = widgets['scrollbox'].get_vadjustment().get_value()
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state, ensure_ascii=False))
        tmp.chmod(0o600)
        os.replace(tmp, path)
        return False

    def changed(*_):
        if not pending[0]:
            pending[0] = True
            GLib.idle_add(save)

    def draw(_area, cr, width, height):
        cr.set_source_rgb(.1, .2, .6)
        cr.paint()
        cr.set_source_rgb(.5, .9, .7)
        cr.rectangle(*state['drag'], 60, 40)
        cr.fill()

    def drag_begin(gesture, x, y):
        rx, ry = state['drag']
        if not (rx <= x < rx + 60 and ry <= y < ry + 40):
            gesture.set_state(Gtk.EventSequenceState.DENIED)
            return
        origin[:] = state['drag']

    def drag_update(_gesture, dx, dy):
        canvas = widgets['canvas']
        state['drag'] = [min(max(0, origin[0] + dx), canvas.get_width() - 60),
                         min(max(0, origin[1] + dy), canvas.get_height() - 40)]
        canvas.queue_draw()
        changed()

    def clicked(_button):
        state['clicks'] += 1
        changed()

    def control(_fd, condition):
        if condition & GLib.IO_HUP:
            app.quit()
            return False
        line = sys.stdin.readline()
        if not line:
            app.quit()
            return False
        command = json.loads(line)
        # Test-only reset, excluded from measured actions. No input injection.
        state.update(nonce=command['nonce'], clicks=0, drag=[100, 40])
        widgets['entry'].set_text(command.get('text', ''))
        widgets['entry'].grab_focus()
        widgets['scrollbox'].get_vadjustment().set_value(0)
        widgets['canvas'].queue_draw()
        changed()
        return True

    def activate(application):
        win = Gtk.ApplicationWindow(application=application)
        win.set_title('Computer Use Optimization Fixture')
        win.set_default_size(720, 620)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for side in ('top', 'bottom', 'start', 'end'):
            getattr(box, 'set_margin_' + side)(30)
        box.set_margin_top(70)
        win.set_child(box)
        entry = Gtk.Entry()
        button = Gtk.Button(label='Fixture click target')
        scrollbox = Gtk.ScrolledWindow()
        scrollbox.set_size_request(-1, 120)
        scrollbox.set_child(Gtk.Label(label='\n'.join('Fixture row ' + str(i) for i in range(80))))
        canvas = Gtk.DrawingArea()
        canvas.set_content_height(160)
        canvas.set_draw_func(draw)
        gesture = Gtk.GestureDrag()
        gesture.connect('drag-begin', drag_begin)
        gesture.connect('drag-update', drag_update)
        canvas.add_controller(gesture)
        for name, widget in [('entry', entry), ('button', button),
                             ('scrollbox', scrollbox), ('canvas', canvas)]:
            box.append(widget)
            widgets[name] = widget
        widgets['window'] = win
        entry.connect('changed', changed)
        button.connect('clicked', clicked)
        scrollbox.get_vadjustment().connect('value-changed', changed)
        win.present()
        entry.grab_focus()
        GLib.timeout_add(100, lambda: (save(), True)[1])
        GLib.io_add_watch(sys.stdin.fileno(), GLib.IO_IN | GLib.IO_HUP, control)

    app.connect('activate', activate)
    return app.run([sys.argv[0]])


if __name__ == '__main__':
    sys.exit(main())
