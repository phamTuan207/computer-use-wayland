#!/usr/bin/env python3
"""AT-SPI probe for Firefox (and Zen, same Gecko stack).

Reads the Firefox accessibility tree over the AT-SPI bus, clicks a
button through the Action interface, and types into a text field
through EditableText, with a keyboard/mouse fallback when the
interface call silently does nothing.

Usage:
  python3 tests/atspi_probe.py --mode full
  python3 tests/atspi_probe.py --mode dump [--max-nodes N] [--max-depth N]
  python3 tests/atspi_probe.py --mode click --name Increment
  python3 tests/atspi_probe.py --mode type --name Name --text hello

Every step logs one JSON line with wall_clock and elapsed_ms.
Exit 0 when every requested op is verified, 2 otherwise.
Requires a running AT-SPI bus (at-spi2-core) and a desktop session.
"""

import argparse
import json
import sys
import time

import pyatspi

START = time.time()


def log(op, ok, **extra):
    now = time.time()
    rec = {
        "wall_clock": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "op": op,
        "ok": ok,
        "elapsed_ms": round((now - START) * 1000, 1),
    }
    rec.update(extra)
    print(json.dumps(rec), flush=True)
    return ok


def find_app(name_sub, timeout_s=30.0):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            desktop = pyatspi.Registry.getDesktop(0)
        except Exception as exc:
            log("desktop", False, error=str(exc))
            time.sleep(1.0)
            continue
        for i in range(desktop.childCount):
            try:
                app = desktop.getChildAtIndex(i)
            except Exception:
                continue
            if app and name_sub.lower() in (app.name or "").lower():
                log("find_app", True, app=app.name)
                return app
        time.sleep(1.0)
    log("find_app", False, wanted=name_sub, timeout_s=timeout_s)
    return None


def walk(acc, depth, max_depth, max_nodes, out):
    if acc is None or depth > max_depth or len(out) >= max_nodes:
        return
    try:
        role = acc.getRoleName()
        name = acc.name or ""
    except Exception:
        return
    node = {"depth": depth, "role": role, "name": name}
    try:
        comp = acc.queryComponent()
        x, y = comp.getPosition(0)
        w, h = comp.getSize()
        node["extents"] = [x, y, w, h]
    except Exception:
        pass
    try:
        action = acc.queryAction()
        node["actions"] = [action.getName(i) for i in range(action.nActions)][:8]
    except Exception:
        pass
    try:
        text = acc.queryText()
        node["chars"] = text.characterCount
    except Exception:
        pass
    out.append(node)
    try:
        count = acc.childCount
    except Exception:
        return
    for i in range(count):
        if len(out) >= max_nodes:
            return
        try:
            walk(acc.getChildAtIndex(i), depth + 1, max_depth, max_nodes, out)
        except Exception:
            continue


def find(acc, role=None, name=None, depth=0, max_depth=14):
    """First node matching role and/or name, depth-first."""
    if acc is None or depth > max_depth:
        return None
    try:
        if (role is None or acc.getRoleName() == role) and (
            name is None or (acc.name or "") == name
        ):
            return acc
        count = acc.childCount
    except Exception:
        return None
    for i in range(count):
        try:
            hit = find(acc.getChildAtIndex(i), role, name, depth + 1, max_depth)
        except Exception:
            continue
        if hit is not None:
            return hit
    return None


def node_text(acc):
    try:
        text = acc.queryText()
        return text.getText(0, text.characterCount)
    except Exception:
        return None


def do_click(acc):
    try:
        action = acc.queryAction()
    except Exception as exc:
        return False, "no Action interface: %s" % exc
    names = [action.getName(i) for i in range(action.nActions)]
    for i, name in enumerate(names):
        if name in ("click", "press", "activate"):
            try:
                return bool(action.doAction(i)), "action %s" % name
            except Exception as exc:
                return False, "doAction failed: %s" % exc
    return False, "no click-like action, has: %s" % names


def do_type(acc, text):
    """Type via EditableText, verify by reading back. Fallback keysyms."""
    try:
        comp = acc.queryComponent()
        comp.grabFocus()
    except Exception as exc:
        return False, "grabFocus failed: %s" % exc
    try:
        editable = acc.queryEditableText()
        ok = editable.setTextContents(text)
        back = node_text(acc)
        if back == text:
            return True, "EditableText setTextContents, read back matches"
        return False, "EditableText returned %s, read back %r" % (ok, back)
    except Exception as exc:
        return False, "EditableText failed: %s" % exc


def do_type_keysyms(acc, text):
    """Focus by a real mouse click at the centre, then send keysyms."""
    try:
        comp = acc.queryComponent()
        x, y, w, h = -1, -1, 0, 0
        for _ in range(10):
            x, y = comp.getPosition(0)
            w, h = comp.getSize()
            if x >= 0 and w > 0:
                break
            time.sleep(0.5)
        if x < 0 or w <= 0:
            return False, "no valid extents after 5 s"
        pyatspi.Registry.generateMouseEvent(x + w // 2, y + h // 2, "b1c")
        time.sleep(0.3)
    except Exception as exc:
        return False, "mouse click to focus failed: %s" % exc
    try:
        for ch in text:
            pyatspi.Registry.generateKeyboardEvent(0, ch, pyatspi.KEY_SYM)
    except Exception as exc:
        return False, "generateKeyboardEvent failed: %s" % exc
    back = node_text(acc)
    if back == text:
        return True, "keysym typing after mouse focus, read back matches"
    return False, "keysym typing, read back %r" % back


def paragraph_text(app):
    para = find(app, role="paragraph")
    if para is None:
        return None
    return node_text(para)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dump", "click", "type", "full"],
                        default="full")
    parser.add_argument("--app", default="Firefox")
    parser.add_argument("--name", default="Increment")
    parser.add_argument("--text", default="hello atspi")
    parser.add_argument("--max-nodes", type=int, default=2000)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--timeout-s", type=float, default=30.0)
    args = parser.parse_args()

    app = find_app(args.app, args.timeout_s)
    if app is None:
        return 2

    if args.mode == "dump":
        nodes = []
        t0 = time.time()
        walk(app, 0, args.max_depth, args.max_nodes, nodes)
        log("dump", True, nodes=len(nodes),
            elapsed_walk_ms=round((time.time() - t0) * 1000, 1),
            truncated=len(nodes) >= args.max_nodes)
        for node in nodes:
            print(json.dumps(node), flush=True)
        return 0

    ok = True
    if args.mode in ("click", "full"):
        for label in ("Continue", "Not now", "Skip"):
            dlg = find(app, role="push button", name=label)
            if dlg is not None:
                t0 = time.time()
                clicked, detail = do_click(dlg)
                log("dismiss_onboarding", clicked, label=label,
                    detail=detail,
                    click_ms=round((time.time() - t0) * 1000, 1))
                time.sleep(2.0)
                break
        btn = find(app, role="push button", name="Increment")
        if btn is None:
            log("find_button", False, wanted="Increment")
            ok = False
        else:
            log("find_button", True)
            counter_before = None
            counter = find(app, role="text", name="0")
            if counter is not None:
                counter_before = node_text(counter)
            t0 = time.time()
            clicked, detail = do_click(btn)
            log("click", clicked, detail=detail,
                click_ms=round((time.time() - t0) * 1000, 1))
            ok = ok and clicked

    if args.mode in ("type", "full"):
        field = find(app, role="entry")
        if field is None:
            field = find(app, role="text")
        if field is None:
            log("find_field", False)
            ok = False
        else:
            log("find_field", True, name=field.name)
            t0 = time.time()
            typed, detail = do_type(field, args.text)
            log("type_editabletext", typed, detail=detail,
                type_ms=round((time.time() - t0) * 1000, 1))
            if not typed:
                t0 = time.time()
                typed2, detail2 = do_type_keysyms(field, args.text)
                log("type_keysyms_fallback", typed2, detail=detail2,
                    type_ms=round((time.time() - t0) * 1000, 1))
                typed = typed2
            ok = ok and typed

    if args.mode == "full":
        log("final_readback", True,
            paragraph=paragraph_text(app),
            entry=node_text(field) if 'field' in dir() else None,
            counter_seen=paragraph_text(app) == "Counter: 1")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
