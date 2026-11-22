#!/usr/bin/env python3
"""Zen tab driver for the W-ZENPREP live proof (laptop side).

One ZenSession per invocation, deleted in finally. Each subcommand
opens its own session, so the single remote session slot is held
only for that step and freed before the next step starts. Never
navigates, types into, or clicks on any existing tab: the only tab
ever opened or closed is the scratch tab, and the only tab ever
navigated is that scratch tab.

Subcommands (each prints one JSON object on stdout):
  list                      list tabs (titles, urls), current first read
  open                      open a NEW tab on the fixture, viewport gate,
                            harvest #msg-input rect
  switch <handle>           make <handle> the Marionette current tab,
                            verify by reading it back
  eval <handle> <expr>      switch to <handle>, evaluate JS expr, print value
  close <new> <original>    close tab <new>, switch current to <original>,
                            verify count and current title
  kill-hung                 kill hung remote-control clients (recovery only)

No em dash or en dash anywhere. Exit 0 on success, 1 on failure
(with an error JSON object).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/james/computer-use-wayland/scripts')
import zen_dom

FIXTURE_URL = ('file:///home/james/computer-use-wayland/tests/'
               'two_vision_fixture.html?clone=zen')
SCRATCH_TITLE = 'Clone zen thread'


def _session():
    return zen_dom.ZenSession()


def _handles(z):
    return z._wd("GET", f"/session/{z.session}/window/handles")["value"]


def _current(z):
    return z._wd("GET", f"/session/{z.session}/window")["value"]


def _title(z):
    return z._wd("GET", f"/session/{z.session}/title")["value"]


def _switch(z, handle):
    z._wd("POST", f"/session/{z.session}/window", {"handle": handle})
    current = _current(z)
    if current != handle:
        raise zen_dom.ZenDomError(
            'switch did not take effect: current %s != %s'
            % (current[:8], handle[:8]))
    return current


def cmd_list():
    with _session() as z:
        tabs = z.list_tabs()
        return {'ok': True, 'count': len(tabs), 'tabs': tabs,
                'current': _current(z)[:8]}


def cmd_open():
    with _session() as z:
        before = _handles(z)
        current_before = _current(z)
        title_before = _title(z)
        resp = z._wd("POST", f"/session/{z.session}/window/new",
                     {"type": "tab"})
        new_handle = resp["value"]["handle"]
        try:
            z._wd("POST", f"/session/{z.session}/url",
                  {"url": FIXTURE_URL})
            deadline = time.perf_counter() + 10
            ready = ""
            while time.perf_counter() < deadline:
                ready = z.evaluate("return document.readyState")
                if ready == "complete":
                    break
                time.sleep(0.1)
            title = _title(z)
            if title != SCRATCH_TITLE:
                raise zen_dom.ZenDomError(
                    'scratch tab title %r != %r' % (title, SCRATCH_TITLE))
            if ready != "complete":
                raise zen_dom.ZenDomError(
                    'scratch tab readyState %r, not complete' % (ready,))
            # Viewport gate (finding C): a Marionette opened tab on
            # live windowed Zen may report a 0x0 viewport, in which
            # case no screen point is meaningful and no input runs.
            metrics = z.evaluate(
                "return {innerWidth: window.innerWidth,"
                " innerHeight: window.innerHeight,"
                " hasFocus: document.hasFocus()};")
            rect = z.evaluate(
                "return (function(){var e=document.querySelector"
                "('#msg-input'); if(!e) return null;"
                " var r=e.getBoundingClientRect();"
                " return {x: r.x, y: r.y, width: r.width,"
                " height: r.height};})();")
            if rect is None:
                raise zen_dom.ZenDomError(
                    'scratch tab has no #msg-input rect')
            at = z.evaluate(
                "return (function(){var e=document.querySelector"
                "('#msg-input'); var r=e.getBoundingClientRect();"
                " var el=document.elementFromPoint("
                "r.x + r.width / 2, r.y + r.height / 2);"
                " return el ? (el.id || el.tagName) : null;})();")
            viewport_ok = bool(
                metrics.get('innerWidth', 0) > 0
                and metrics.get('innerHeight', 0) > 0
                and metrics.get('hasFocus') is True
                and at is not None)
            harvest = z.harvest(['#msg-input'])
            return {'ok': True, 'new_handle': new_handle,
                    'new_handle_prefix': new_handle[:8],
                    'title': title, 'ready': ready,
                    'count_before': len(before),
                    'count_after': len(_handles(z)),
                    'current_before': current_before[:8],
                    'title_before': title_before,
                    'metrics': metrics, 'rect': rect,
                    'element_at_point': at,
                    'viewport_ok': viewport_ok,
                    'harvest': harvest}
        except Exception:
            # Best-effort close of the scratch tab we just opened,
            # then re-raise so the caller records the failure.
            try:
                z._wd("DELETE", f"/session/{z.session}/window", {})
            except Exception:
                pass
            raise


def cmd_switch(handle):
    with _session() as z:
        handles = _handles(z)
        full = None
        for h in handles:
            if h == handle or h.startswith(handle):
                full = h
                break
        if full is None:
            raise zen_dom.ZenDomError(
                'no handle matches %r (%d handles)' % (handle, len(handles)))
        _switch(z, full)
        return {'ok': True, 'handle': full[:8], 'title': _title(z)}


def cmd_eval(handle, expr):
    with _session() as z:
        handles = _handles(z)
        full = None
        for h in handles:
            if h == handle or h.startswith(handle):
                full = h
                break
        if full is None:
            raise zen_dom.ZenDomError(
                'no handle matches %r (%d handles)' % (handle, len(handles)))
        _switch(z, full)
        value = z.evaluate("return (%s);" % expr)
        return {'ok': True, 'handle': full[:8], 'value': value}


def cmd_close(new_handle, original_handle):
    with _session() as z:
        handles = _handles(z)
        count_before = len(handles)
        new_full = None
        orig_full = None
        for h in handles:
            if h == new_handle or h.startswith(new_handle):
                new_full = h
            if h == original_handle or h.startswith(original_handle):
                orig_full = h
        if new_full is None:
            raise zen_dom.ZenDomError(
                'scratch handle %r is gone already' % (new_handle,))
        if orig_full is None:
            raise zen_dom.ZenDomError(
                'original handle %r is gone; refusing to close blind'
                % (original_handle,))
        _switch(z, new_full)
        z._wd("DELETE", f"/session/{z.session}/window", {})
        after = _handles(z)
        if new_full in after:
            raise zen_dom.ZenDomError('scratch tab still listed after close')
        _switch(z, orig_full)
        title = _title(z)
        return {'ok': True, 'count_before': count_before,
                'count_after': len(after), 'current_title': title,
                'current_handle': orig_full[:8]}


def main(argv):
    try:
        if not argv:
            raise ValueError('usage: zen-tab.py <list|open|switch|eval|close|kill-hung> ...')
        cmd = argv[0]
        if cmd == 'list':
            result = cmd_list()
        elif cmd == 'open':
            result = cmd_open()
        elif cmd == 'switch':
            result = cmd_switch(argv[1])
        elif cmd == 'eval':
            result = cmd_eval(argv[1], argv[2])
        elif cmd == 'close':
            result = cmd_close(argv[1], argv[2])
        elif cmd == 'kill-hung':
            result = {'ok': True,
                      'killed': zen_dom.kill_hung_remote_clients()}
        else:
            raise ValueError('unknown subcommand %r' % (cmd,))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:  # noqa: BLE001 - print a JSON error, exit 1
        print(json.dumps({'ok': False, 'error': '%s: %s'
                          % (type(exc).__name__, str(exc)[:400])},
                         ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
