#!/usr/bin/env python3
"""AT-SPI prototype: press a desktop button without a screenshot.

Idea
AT-SPI2 is the Linux accessibility protocol. Applications expose a
tree of accessible objects over a dedicated D-Bus bus: applications,
windows, buttons, entries. A client walks that tree, finds a widget
by name and role, and calls its semantic action, for example the
click or press action of a push button. No coordinates, no pointer,
no screenshot are involved. Text is read through the Text interface
and written through the EditableText interface.

Modes
live: use pyatspi against the real session. Needs a graphical
session with accessibility enabled, a session bus, and target apps
that expose a tree, GTK and Qt with their accessibility switches on,
Chromium and Electron only with their renderer accessibility flag.
selftest: run the same search and press logic against an in-memory
fake accessible tree that implements the same small interface the
live wrapper uses. This proves the logic and times it on any
machine, including a headless one. It does not prove a real desktop
press, and its report says so.
auto: try live, record why live is unavailable if it is, then run
the selftest. This is the default.

Timing and logging
Every step records wall clock, ISO 8601 UTC start and end, and
elapsed seconds from a monotonic clock, prints one line per step,
and can write a JSON log with --log-json PATH.

Usage
  python3 tests/atspi_prototype.py
  python3 tests/atspi_prototype.py --mode live --app gedit --button Save
  python3 tests/atspi_prototype.py --mode selftest --log-json /tmp/atspi.json

Exit code 0 means the requested mode passed. In auto mode, exit 0
means the selftest passed and the live availability was recorded,
whatever it was. In live mode, exit 1 means live control failed,
with the reason in the log, never hidden.
"""

import argparse
import datetime
import json
import sys
import time
from pathlib import Path


def wall_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class StepLog:
    def __init__(self):
        self.steps = []

    def run(self, name, func):
        wall_start = wall_now()
        start = time.perf_counter()
        try:
            detail = func()
            ok, error = True, None
        except Exception as exc:
            detail, ok, error = None, False, f"{type(exc).__name__}: {exc}"
        entry = {"step": name, "ok": ok, "wall_start": wall_start,
                 "wall_end": wall_now(),
                 "elapsed_s": round(time.perf_counter() - start, 4),
                 "detail": detail, "error": error}
        self.steps.append(entry)
        print(f"[{entry['wall_start']}] {name} "
              f"{'ok' if ok else 'FAIL'} elapsed_s={entry['elapsed_s']} "
              f"detail={detail} error={error}", flush=True)
        if not ok:
            raise RuntimeError(f"step failed: {name}: {error}")
        return detail


# ---------------------------------------------------------------------------
# Shared logic. A node, real or fake, provides:
# name, role, children(), is_visible_enabled(), actions(), do_action(index),
# get_text(), set_text(value). The search and press functions below only use
# that interface, so the selftest exercises the exact live logic.
# ---------------------------------------------------------------------------

def walk(node, max_depth=25, depth=0):
    yield node
    if depth >= max_depth:
        return
    for child in node.children():
        if child is not None:
            yield from walk(child, max_depth, depth + 1)


def list_windows(roots):
    out = []
    for app in roots:
        for child in app.children():
            if child is not None and child.role in ("frame", "dialog", "window"):
                out.append({"app": app.name, "window": child.name,
                            "role": child.role})
    return out


def find_widget(roots, app_part, role, name):
    for app in roots:
        if app is None or app_part not in (app.name or ""):
            continue
        for node in walk(app):
            if node.role == role and node.name == name and node.is_visible_enabled():
                return node
    return None


def press_button(node):
    names = node.actions()
    if not names:
        raise RuntimeError("widget exposes no actions")
    index = 0
    for wanted in ("click", "press", "activate"):
        if wanted in names:
            index = names.index(wanted)
            break
    ok = node.do_action(index)
    if not ok:
        raise RuntimeError(
            f"do_action returned False for action {names[index]!r} "
            f"on widget {node.name!r}")
    return {"actions": names, "used": names[index], "ok": bool(ok)}


# ---------------------------------------------------------------------------
# Fake accessible tree for the selftest. It models a small editor window:
# an entry, a Save button that copies the entry text into a status label,
# and a Cancel button. Actions mutate the tree exactly as a real toolkit
# action mutates the real UI, so verification reads real state back.
# ---------------------------------------------------------------------------

class FakeNode:
    def __init__(self, name, role, children=None, actions=None,
                 text="", on_action=None):
        self.name = name
        self.role = role
        self._children = children or []
        self._actions = actions or []
        self._text = text
        self._on_action = on_action

    def children(self):
        return list(self._children)

    def is_visible_enabled(self):
        return True

    def actions(self):
        return list(self._actions)

    def do_action(self, index):
        if self._on_action is not None:
            self._on_action(self._actions[index])
        return True

    def get_text(self):
        return self._text

    def set_text(self, value):
        self._text = value


def build_fake_desktop():
    status = FakeNode("status", "label", text="not saved")
    entry = FakeNode("note", "entry", text="")

    def on_save(_action_name):
        status.set_text("saved:" + entry.get_text())

    save = FakeNode("Save", "push button", actions=["click"], on_action=on_save)
    cancel = FakeNode("Cancel", "push button", actions=["click"])
    panel = FakeNode("panel", "panel", children=[entry, save, cancel, status])
    frame = FakeNode("Fake Editor", "frame", children=[panel])
    app = FakeNode("fake-editor", "application", children=[frame])
    return [app], {"entry": entry, "status": status}


def run_selftest(log, typed_text):
    roots_holder = {}

    def build():
        roots, refs = build_fake_desktop()
        roots_holder["roots"] = roots
        roots_holder["refs"] = refs
        count = sum(1 for app in roots for _ in walk(app))
        return {"accessible_objects": count}

    log.run("selftest_build_fake_tree", build)
    roots = roots_holder["roots"]
    refs = roots_holder["refs"]

    windows = log.run("list_windows",
                      lambda: list_windows(roots))
    if not windows:
        raise RuntimeError("selftest found no windows")

    holder = {}

    def describe(key, node):
        if node is None:
            raise RuntimeError("widget not found")
        holder[key] = node
        return {"name": node.name, "role": node.role}

    log.run(
        "find_entry",
        lambda: describe("entry", find_widget(roots, "fake-editor", "entry", "note")))
    entry = holder["entry"]
    log.run("set_entry_text",
            lambda: {"value": (entry.set_text(typed_text),
                               entry.get_text())[1]})
    log.run(
        "find_button_by_name_and_role",
        lambda: describe("button", find_widget(roots, "fake-editor", "push button", "Save")))
    button = holder["button"]
    result = log.run("press_button_do_action", lambda: press_button(button))

    def verify():
        value = refs["status"].get_text()
        expected = "saved:" + typed_text
        if value != expected:
            raise RuntimeError(f"status mismatch: {value!r} != {expected!r}")
        return {"status_text": value}

    log.run("verify_ui_changed_after_press", verify)
    return {"windows": windows, "press": result}


# ---------------------------------------------------------------------------
# Live mode, pyatspi. Imported lazily so the selftest runs anywhere.
# ---------------------------------------------------------------------------

class RealNode:
    def __init__(self, obj, pyatspi):
        self._obj = obj
        self._pyatspi = pyatspi

    @property
    def name(self):
        return self._obj.name or ""

    @property
    def role(self):
        try:
            return self._obj.getRoleName()
        except Exception:
            return ""

    def children(self):
        out = []
        for i in range(self._obj.childCount):
            try:
                child = self._obj.getChildAtIndex(i)
            except Exception:
                continue
            if child is not None:
                out.append(RealNode(child, self._pyatspi))
        return out

    def is_visible_enabled(self):
        try:
            states = self._obj.getState()
            return (states.contains(self._pyatspi.STATE_VISIBLE)
                    and states.contains(self._pyatspi.STATE_ENABLED))
        except Exception:
            return False

    def actions(self):
        try:
            action = self._obj.queryAction()
            return [action.getName(i) for i in range(action.nActions)]
        except Exception:
            return []

    def do_action(self, index):
        return bool(self._obj.queryAction().doAction(index))

    def get_text(self):
        text = self._obj.queryText()
        return text.getText(0, text.characterCount)

    def set_text(self, value):
        return bool(self._obj.queryEditableText().setTextContents(value))


def run_live(log, app_part, button_name):
    def import_and_desktop():
        import pyatspi
        desktop = pyatspi.Registry.getDesktop(0)
        roots = [RealNode(app, pyatspi) for app in desktop if app is not None]
        if not roots:
            raise RuntimeError(
                "no applications on the AT-SPI desktop, accessibility "
                "may be off or this is not a graphical session")
        return {"applications": [r.name for r in roots], "_roots": roots}

    info = log.run("live_import_and_list_applications", import_and_desktop)
    roots = info.pop("_roots")
    windows = log.run("live_list_windows", lambda: list_windows(roots))

    holder = {}

    def find_live_button():
        node = find_widget(roots, app_part, "push button", button_name)
        if node is None:
            raise RuntimeError("button not found in the live tree")
        holder["button"] = node
        return {"name": node.name, "role": node.role}

    log.run("live_find_button", find_live_button)
    button = holder["button"]
    result = log.run("live_press_button", lambda: press_button(button))
    return {"windows": windows, "press": result}


def main():
    parser = argparse.ArgumentParser(description="AT-SPI button press prototype")
    parser.add_argument("--mode", choices=["auto", "live", "selftest"],
                        default="auto")
    parser.add_argument("--app", default="gedit",
                        help="application name fragment for live mode")
    parser.add_argument("--button", default="Save",
                        help="button name for live mode")
    parser.add_argument("--text", default="clone2 atspi test",
                        help="text used by the selftest entry")
    parser.add_argument("--log-json", default="")
    args = parser.parse_args()

    summary = {"mode": args.mode, "ok": False}
    total_start = time.perf_counter()
    summary["wall_start"] = wall_now()

    if args.mode in ("live", "auto"):
        live_log = StepLog()
        try:
            live = run_live(live_log, args.app, args.button)
            summary["live"] = {"ok": True, "result": live,
                               "steps": live_log.steps}
            summary["ok"] = True
        except Exception as exc:
            summary["live"] = {"ok": False,
                               "failure": f"{type(exc).__name__}: {exc}",
                               "steps": live_log.steps}
            print(f"LIVE UNAVAILABLE OR FAILED {summary['live']['failure']}",
                  flush=True)
            if args.mode == "live":
                summary["total_elapsed_s"] = round(
                    time.perf_counter() - total_start, 4)
                summary["wall_end"] = wall_now()
                print("SUMMARY " + json.dumps(summary, ensure_ascii=False),
                      flush=True)
                if args.log_json:
                    Path(args.log_json).write_text(
                        json.dumps(summary, ensure_ascii=False, indent=2),
                        encoding="utf-8")
                return 1

    if args.mode in ("selftest", "auto"):
        self_log = StepLog()
        try:
            result = run_selftest(self_log, args.text)
            summary["selftest"] = {"ok": True, "result": result,
                                   "steps": self_log.steps}
            summary["ok"] = True
        except Exception as exc:
            summary["selftest"] = {"ok": False,
                                   "failure": f"{type(exc).__name__}: {exc}",
                                   "steps": self_log.steps}

    summary["total_elapsed_s"] = round(time.perf_counter() - total_start, 4)
    summary["wall_end"] = wall_now()
    print("SUMMARY " + json.dumps(summary, ensure_ascii=False), flush=True)
    if args.log_json:
        Path(args.log_json).write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
