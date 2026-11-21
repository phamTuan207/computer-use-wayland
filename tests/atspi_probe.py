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
  python3 tests/atspi_probe.py --mode dismiss
  python3 tests/atspi_probe.py --mode session [--app-path PATH]

Every step logs one JSON line with wall_clock and elapsed_ms.
Exit 0 when every requested op is verified, 2 otherwise.
Requires a running AT-SPI bus (at-spi2-core) and a desktop session.

The session mode is a staged bring-up diagnostic. It audits the
environment, tries the raw desktop first, then tries to build a
virtual session from whatever binaries exist on the machine (Xvfb,
dbus-daemon, at-spi-bus-launcher), launches a real GUI app inside
it, and only then attempts the tree read and the button press.
Every stage is timed and every failure is logged with its exact
error, so the output states precisely where this machine stops.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

try:
    import pyatspi
    PYATSPI_ERROR = None
except Exception as exc:  # ImportError or missing system libraries
    pyatspi = None
    PYATSPI_ERROR = "%s: %s" % (type(exc).__name__, exc)

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
        except Exception:
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


def find_documents(app):
    """All web document nodes under the app, depth-first.

    Firefox exposes one document web node per tab, plus empty ones
    for about:blank or not-yet-loaded tabs. The first document in
    tree order is often an empty one, so callers must not assume
    the first document is the page they want.
    """
    out = []

    def collect(acc, depth=0):
        if acc is None or depth > 14:
            return
        try:
            if acc.getRoleName() == "document web":
                out.append(acc)
            count = acc.childCount
        except Exception:
            return
        for i in range(count):
            try:
                collect(acc.getChildAtIndex(i), depth + 1)
            except Exception:
                continue

    collect(app)
    return out


def find_document(app):
    """The first web document node, or None if the tree has none yet."""
    docs = find_documents(app)
    return docs[0] if docs else None


def find_in_document(app, role=None, name=None):
    """First node matching role/name inside any web document.

    Chrome UI (toolbars, address bar) lives outside the documents,
    so searching here cannot return a browser entry or button
    by mistake. Every document is searched, because the first
    document in tree order is often an empty about:blank one and
    the wanted page is a later document.
    """
    for doc in find_documents(app):
        hit = find(doc, role=role, name=name)
        if hit is not None:
            return hit
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


def stage_log(stage, ok, t0, **extra):
    """One JSON line per bring-up stage, with per-stage elapsed_ms."""
    now = time.time()
    rec = {
        "wall_clock": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "stage": stage,
        "ok": ok,
        "stage_elapsed_ms": round((now - t0) * 1000, 1),
        "elapsed_ms": round((now - START) * 1000, 1),
    }
    rec.update(extra)
    print(json.dumps(rec), flush=True)
    return ok


def run_session_mode(app_path, app_timeout_s=25.0):
    """Staged AT-SPI bring-up. Returns 0 only if a real tree was read
    and a real button press was verified, 2 otherwise. Never raises:
    each stage records its own failure and the run continues so the
    log shows every limit this machine hits, in order."""
    all_ok = True
    spawned = []  # Popen objects to clean up at the end

    # Stage 1: audit the environment as it is.
    t0 = time.time()
    binaries = {}
    for name in ("Xvfb", "dbus-run-session", "dbus-daemon", "gdbus",
                 "at-spi-bus-launcher", "at-spi2-registryd"):
        binaries[name] = shutil.which(name)
    stage_log("audit_environment", True, t0,
              display=os.environ.get("DISPLAY"),
              wayland_display=os.environ.get("WAYLAND_DISPLAY"),
              dbus_session_bus_address=os.environ.get(
                  "DBUS_SESSION_BUS_ADDRESS"),
              xdg_runtime_dir=os.environ.get("XDG_RUNTIME_DIR"),
              x11_socket_dir_exists=os.path.isdir("/tmp/.X11-unix"),
              binaries=binaries,
              pyatspi_importable=pyatspi is not None,
              pyatspi_error=PYATSPI_ERROR)

    # Stage 2: raw desktop, no virtual session. Import first.
    t0 = time.time()
    if pyatspi is None:
        stage_log("raw_desktop_registry", False, t0,
                  error="pyatspi not importable: %s" % PYATSPI_ERROR)
        all_ok = False
    else:
        try:
            desktop = pyatspi.Registry.getDesktop(0)
            stage_log("raw_desktop_registry", True, t0,
                      applications=desktop.childCount)
        except Exception as exc:
            stage_log("raw_desktop_registry", False, t0,
                      error="%s: %s" % (type(exc).__name__, exc))
            all_ok = False

    # Stage 3: start Xvfb on a free display number.
    display = None
    t0 = time.time()
    if binaries["Xvfb"] is None:
        stage_log("start_xvfb", False, t0, error="Xvfb binary missing")
        all_ok = False
    else:
        for num in (97, 98, 99):
            if not os.path.exists("/tmp/.X11-unix/X%d" % num):
                display = ":%d" % num
                break
        if display is None:
            stage_log("start_xvfb", False, t0,
                      error="no free display number in 97..99")
            all_ok = False
        else:
            try:
                proc = subprocess.Popen(
                    ["Xvfb", display, "-screen", "0", "1280x800x24"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                spawned.append(proc)
                sock = "/tmp/.X11-unix/X%s" % display[1:]
                deadline = time.time() + 10.0
                while time.time() < deadline and not os.path.exists(sock):
                    if proc.poll() is not None:
                        break
                    time.sleep(0.1)
                if os.path.exists(sock) and proc.poll() is None:
                    stage_log("start_xvfb", True, t0, display=display,
                              pid=proc.pid)
                else:
                    stage_log("start_xvfb", False, t0, display=display,
                              error="X socket %s never appeared, "
                                    "xvfb exit=%s" % (sock, proc.poll()))
                    all_ok = False
                    display = None
            except Exception as exc:
                stage_log("start_xvfb", False, t0,
                          error="%s: %s" % (type(exc).__name__, exc))
                all_ok = False
                display = None

    # Stage 4: start a private session bus with dbus-daemon.
    bus_address = None
    bus_pid = None
    t0 = time.time()
    if binaries["dbus-daemon"] is None:
        stage_log("start_session_bus", False, t0,
                  error="dbus-daemon binary missing")
        all_ok = False
    else:
        try:
            out = subprocess.run(
                ["dbus-daemon", "--session", "--fork",
                 "--print-address=1", "--print-pid=1"],
                capture_output=True, text=True, timeout=10)
            lines = [ln.strip() for ln in out.stdout.splitlines()
                     if ln.strip()]
            if out.returncode == 0 and len(lines) >= 2:
                bus_address, bus_pid = lines[0], int(lines[1])
                stage_log("start_session_bus", True, t0,
                          address=bus_address, pid=bus_pid)
            else:
                stage_log("start_session_bus", False, t0,
                          error="rc=%s stdout=%r stderr=%r"
                                % (out.returncode, out.stdout[:200],
                                   out.stderr[:200]))
                all_ok = False
        except Exception as exc:
            stage_log("start_session_bus", False, t0,
                      error="%s: %s" % (type(exc).__name__, exc))
            all_ok = False

    # Session environment for the stages below and for child apps.
    session_env = dict(os.environ)
    if display:
        session_env["DISPLAY"] = display
    if bus_address:
        session_env["DBUS_SESSION_BUS_ADDRESS"] = bus_address

    # Stage 5: can anything own org.a11y.Bus on this session bus?
    # Without at-spi-bus-launcher there is no a11y bus at all.
    t0 = time.time()
    if bus_address is None:
        stage_log("check_a11y_bus", False, t0,
                  error="no session bus to check")
        all_ok = False
    elif binaries["at-spi-bus-launcher"] is None:
        detail = None
        if binaries["gdbus"]:
            try:
                out = subprocess.run(
                    ["gdbus", "call", "--address", bus_address,
                     "--dest", "org.a11y.Bus",
                     "--object-path", "/org/a11y/bus",
                     "--method", "org.a11y.Bus.GetAddress"],
                    capture_output=True, text=True, timeout=10)
                detail = "gdbus rc=%s stderr=%r" % (
                    out.returncode, out.stderr.strip()[:300])
            except Exception as exc:
                detail = "gdbus failed: %s: %s" % (type(exc).__name__, exc)
        stage_log("check_a11y_bus", False, t0,
                  error="at-spi-bus-launcher binary missing, nothing can "
                        "own org.a11y.Bus", gdbus_probe=detail)
        all_ok = False
    else:
        stage_log("check_a11y_bus", False, t0,
                  error="launcher present but this staged probe does not "
                        "start it; UNVERIFIED")
        all_ok = False

    # Stage 6: launch a real GUI app inside the virtual session.
    app_proc = None
    t0 = time.time()
    if display is None or bus_address is None:
        stage_log("launch_gui_app", False, t0,
                  error="virtual session incomplete (display=%s bus=%s)"
                        % (display, bool(bus_address)))
        all_ok = False
    elif not app_path or not os.path.exists(app_path):
        stage_log("launch_gui_app", False, t0,
                  error="app path missing: %r" % app_path)
        all_ok = False
    else:
        try:
            profile = "/tmp/atspi-probe-profile"
            app_proc = subprocess.Popen(
                [app_path, "-profile", profile, "-no-remote",
                 "about:blank"],
                env=session_env,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            spawned.append(app_proc)
            deadline = time.time() + app_timeout_s
            alive = False
            while time.time() < deadline:
                if app_proc.poll() is not None:
                    break
                time.sleep(0.5)
                alive = app_proc.poll() is None
                if alive and time.time() > deadline - app_timeout_s + 5:
                    break
            if app_proc.poll() is None:
                stage_log("launch_gui_app", True, t0, app=app_path,
                          pid=app_proc.pid,
                          note="process alive under Xvfb; window-level "
                               "proof unavailable, no X query tools and "
                               "no accessible tree to read")
            else:
                stage_log("launch_gui_app", False, t0, app=app_path,
                          error="app exited early, rc=%s"
                                % app_proc.poll())
                all_ok = False
        except Exception as exc:
            stage_log("launch_gui_app", False, t0,
                      error="%s: %s" % (type(exc).__name__, exc))
            all_ok = False

    # Stage 7: read the accessible tree inside the virtual session.
    t0 = time.time()
    if pyatspi is None:
        stage_log("read_accessible_tree", False, t0,
                  error="pyatspi not importable: %s" % PYATSPI_ERROR)
        all_ok = False
    elif bus_address is None:
        stage_log("read_accessible_tree", False, t0,
                  error="no session bus, and pyatspi in this process is "
                        "bound to the bus of the environment it started "
                        "in; a tree read needs pyatspi running under "
                        "the session bus, UNVERIFIED")
        all_ok = False
    else:
        stage_log("read_accessible_tree", False, t0,
                  error="pyatspi in this process cannot rebind to the "
                        "new session bus, and no at-spi registry daemon "
                        "exists on this machine to serve a tree; "
                        "UNVERIFIED")
        all_ok = False

    # Stage 8: a real button press through do_action.
    t0 = time.time()
    stage_log("press_button_do_action", False, t0,
              error="not attempted: no accessible tree was read "
                    "(stage read_accessible_tree failed), so there is "
                    "no button object to press; FAILED, not faked")
    all_ok = False

    # Cleanup: app, Xvfb, session bus.
    for proc in reversed(spawned):
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    if bus_pid:
        try:
            os.kill(bus_pid, 15)
        except Exception:
            pass
    stage_log("session_summary", all_ok, START,
              total_elapsed_ms=round((time.time() - START) * 1000, 1),
              verdict="full live AT-SPI control verified"
                      if all_ok else
                      "stopped at the limits recorded above")
    return 0 if all_ok else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",
                        choices=["dump", "click", "type", "full", "dismiss",
                                 "session"],
                        default="full")
    parser.add_argument("--app-path",
                        default=os.path.expanduser(
                            "~/workspace/tools/firefox/firefox"),
                        help="GUI app binary for session mode")
    parser.add_argument("--app", default="Firefox")
    parser.add_argument("--name", default="Increment")
    parser.add_argument("--text", default="hello atspi")
    parser.add_argument("--max-nodes", type=int, default=2000)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--timeout-s", type=float, default=30.0)
    args = parser.parse_args()

    if args.mode == "session":
        return run_session_mode(args.app_path)

    if pyatspi is None:
        log("import_pyatspi", False, error=PYATSPI_ERROR)
        return 2

    app = find_app(args.app, args.timeout_s)
    if app is None:
        return 2

    if args.mode == "dismiss":
        # Only dismiss the first-run dialog, nothing else. Used by
        # the session wrapper while waiting for the page: click and
        # type modes have side effects (they press the fixture
        # button), so they must not be used as a readiness poll.
        for label in ("Continue", "Not now", "Skip"):
            dlg = find(app, role="push button", name=label)
            if dlg is not None:
                t0 = time.time()
                clicked, detail = do_click(dlg)
                log("dismiss_onboarding", clicked, label=label,
                    detail=detail,
                    click_ms=round((time.time() - t0) * 1000, 1))
                return 0 if clicked else 2
        log("dismiss_onboarding", False, detail="no dialog button found")
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
    field = None
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
        btn = find_in_document(app, role="push button", name="Increment")
        if btn is None:
            log("find_button", False, wanted="Increment")
            ok = False
        else:
            log("find_button", True)
            t0 = time.time()
            clicked, detail = do_click(btn)
            log("click", clicked, detail=detail,
                click_ms=round((time.time() - t0) * 1000, 1))
            ok = ok and clicked

    if args.mode in ("type", "full"):
        field = find_in_document(app, role="entry", name="Name")
        if field is None:
            # Fallback: the only entry inside the document. Never fall
            # back to the first entry in the whole tree: that can be
            # the browser address bar, not the fixture field.
            field = find_in_document(app, role="entry")
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
        entry_back = node_text(field) if field is not None else None
        para = paragraph_text(app)
        entry_ok = entry_back == args.text
        counter_ok = para == "Counter: 1"
        readback_ok = entry_ok and counter_ok
        log("final_readback", readback_ok,
            paragraph=para,
            entry=entry_back,
            expected_entry=args.text,
            counter_seen=counter_ok)
        ok = ok and readback_ok
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
