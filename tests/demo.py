#!/usr/bin/env python3
"""Inert GTK4 demo desktop for exercising real mouse and keyboard input.

Safe by construction: no subprocess, no network, no config, no cursor change.
--events and --layout are TEST-ONLY; without them nothing is written.
"""
import argparse
import json
import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, Gtk

CSS = b"""
window { background-color: #14121f; }
#root { background-image: linear-gradient(to bottom right, #241a33, #14182e 55%, #101a2c); border-radius: 18px; }
.title { color: #f3f0ff; font-size: 26px; font-weight: 800; }
.subtitle { color: #b9b2d6; font-size: 14px; }
.counter { color: #8ef0cf; font-size: 15px; font-weight: 700; }
.status { color: #cfd6ff; font-size: 13px; }
#entry { background-color: #ffffff18; color: #f3f0ff; border-radius: 10px; padding: 8px; }
#button { background-image: linear-gradient(to bottom, #7b5cff, #5a3fd6); color: #ffffff; border-radius: 12px; padding: 10px 18px; font-weight: 700; }
#canvas { background-color: #1f3fbf; border-radius: 16px; }
"""

MODS = ((Gdk.ModifierType.SHIFT_MASK, "Shift"), (Gdk.ModifierType.CONTROL_MASK, "Ctrl"),
        (Gdk.ModifierType.ALT_MASK, "Alt"), (Gdk.ModifierType.SUPER_MASK, "Super"), (Gdk.ModifierType.META_MASK, "Meta"))


def modifier_names(state):
    return "+".join(name for flag, name in MODS if state & flag) or "none"


def draw_canvas(cr, width, height, rect):
    cr.set_source_rgb(0.12, 0.25, 0.75)
    cr.rectangle(0, 0, width, height)
    cr.fill()
    if rect[0] < 0:  # first draw: mint rectangle starts centred
        rect[0], rect[1] = max(0, (width - rect[2]) // 2), max(0, (height - rect[3]) // 2)
    cr.set_source_rgb(0.55, 0.94, 0.81)
    cr.rectangle(rect[0], rect[1], rect[2], rect[3])
    cr.fill()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inert GTK4 demo for computer-use input tests")
    parser.add_argument("--events", metavar="PATH", help="TEST-ONLY: persist test events as JSON")
    parser.add_argument("--layout", metavar="PATH", help="TEST-ONLY: save widget rects as JSON")
    args = parser.parse_args(argv)
    events, labels, widgets, published = [], {}, {}, {}
    rect = [-1, -1, 220, 140]  # mint rectangle x, y, w, h; x<0 means not placed yet
    origin = [0, 0]            # drag-start snapshot; drag-update dx/dy are totals
    clicks = scrolls = 0
    app = Gtk.Application(application_id="local.computeruse.Demo")

    def write_json(path, payload):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    def note(event, **fields):
        events.append({"event": event, **fields})
        labels["status"].set_label(" ".join([event] + [f"{k}={v}" for k, v in fields.items()]))
        if args.events:
            write_json(args.events, events)

    def on_button(_button):
        nonlocal clicks
        clicks += 1
        labels["clicks"].set_label(f"Clicks: {clicks}")
        note("button", count=clicks)

    def on_entry(entry):
        note("entry", text=entry.get_text())

    def on_canvas(gesture, _presses, x, y):
        note("canvas", button=gesture.get_current_button(), x=round(x), y=round(y),
             mods=modifier_names(gesture.get_current_event_state()))

    def on_scroll(_controller, dx, dy):
        nonlocal scrolls
        scrolls += 1
        labels["scrolls"].set_label(f"Scroll: {scrolls}")
        note("scroll", dx=round(dx, 2), dy=round(dy, 2), count=scrolls)

    def on_drag_begin(_gesture, _x, _y):
        # drag-update reports totals since this point, not per-frame steps.
        origin[0], origin[1] = rect[0], rect[1]

    def on_drag_update(_gesture, dx, dy):
        canvas = widgets["canvas"]
        width, height = canvas.get_width(), canvas.get_height()
        rect[0] = min(max(0, origin[0] + dx), max(0, width - rect[2]))
        rect[1] = min(max(0, origin[1] + dy), max(0, height - rect[3]))
        canvas.queue_draw()

    def on_drag_end(_gesture, dx, dy):
        note("drag", x=rect[0], y=rect[1], dx=round(dx, 2), dy=round(dy, 2))

    def publish_layout(win):
        # Runs from a GLib timeout after map so the window is allocated. Stays
        # scheduled so a later resize still refreshes the file, and stops once the
        # window is no longer mapped.
        if not args.layout:
            return False
        if not win.get_mapped():
            return False
        data = {}
        for key in ("entry", "button", "canvas"):
            ok, bounds = widgets[key].compute_bounds(win)
            if not ok:
                return True
            data[key] = [bounds.get_x(), bounds.get_y(), bounds.get_width(), bounds.get_height()]
        if data != published:
            published.clear()
            published.update(data)
            write_json(args.layout, data)
        return True

    def labelled(parent, text, css_class, key=None):
        label = Gtk.Label(label=text)
        label.add_css_class(css_class)  # .title/.subtitle/.counter are class selectors
        parent.append(label)
        labels[key or css_class] = label
        return label

    def activate(application):
        # GTK is only initialised once activate runs; the display is None before
        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        win = Gtk.ApplicationWindow(application=application)
        win.set_title("Computer Use Demo")
        win.set_default_size(960, 650)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_name("root")
        # The session pill is drawn top-center; this margin keeps it off the title.
        root.set_margin_top(90)
        root.set_margin_bottom(26)
        root.set_margin_start(26)
        root.set_margin_end(26)
        win.set_child(root)
        labelled(root, "Computer use", "title")
        labelled(root, "Safe demo", "subtitle")
        entry = Gtk.Entry()
        entry.set_name("entry")
        entry.set_placeholder_text("Type here, nothing leaves this window")
        entry.connect("changed", on_entry)
        root.append(entry)
        widgets["entry"] = entry
        button = Gtk.Button(label="Click target")
        button.set_name("button")
        button.connect("clicked", on_button)
        root.append(button)
        widgets["button"] = button
        labelled(root, "Clicks: 0", "counter", "clicks")
        labelled(root, "Scroll: 0", "counter", "scrolls")
        canvas = Gtk.DrawingArea()
        canvas.set_name("canvas")
        canvas.set_content_width(560)
        canvas.set_content_height(320)
        canvas.set_vexpand(True)
        canvas.set_draw_func(lambda _area, cr, w, h: draw_canvas(cr, w, h, rect))
        root.append(canvas)
        widgets["canvas"] = canvas
        labelled(root, "Ready", "status")
        gesture = Gtk.GestureClick()
        gesture.set_button(0)
        gesture.connect("pressed", on_canvas)
        canvas.add_controller(gesture)
        wheel = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.BOTH_AXES)
        wheel.connect("scroll", on_scroll)
        canvas.add_controller(wheel)
        drag = Gtk.GestureDrag()
        drag.connect("drag-begin", on_drag_begin)
        drag.connect("drag-update", on_drag_update)
        drag.connect("drag-end", on_drag_end)
        canvas.add_controller(drag)
        note("ready")
        win.connect("map", lambda w: GLib.timeout_add(200, publish_layout, w))
        win.present()

    app.connect("activate", activate)
    app.connect("shutdown", lambda _app: args.events and write_json(args.events, events))
    return app.run([sys.argv[0]])


if __name__ == "__main__":
    sys.exit(main())