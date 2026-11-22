#!/usr/bin/env python3
"""Zen tab driver for the W-ZENPREP live proof (laptop side).

One ZenSession per invocation, deleted in finally. Each subcommand
opens its own session, so the single remote session slot is held
only for that step and freed before the next step starts. Never
navigates, types into, or clicks on any existing tab: the only tab
ever opened or closed is the scratch tab, and the only tab ever
navigated is that scratch tab.

Tab identity is the URL, never a stored Marionette handle.
Handles are ephemeral per session on this Zen (W-ZENPROOF2 run 2
proved it: 15 of 15 comparable URLs had a different handle between
two list scans a minute apart), so a handle from one session means
nothing in the next. Every subcommand resolves its tab by URL
substring inside its own session, fresh, and refuses on ambiguity.
The scratch tab is the fixture URL
'two_vision_fixture.html?clone=zen'. Its document title is the
static 'Two-vision benchmark fixture' (the fixture JS only sets
the H1 text to 'Clone zen thread' and never touches
document.title), so document.title is NEVER used to identify the
scratch tab. The H1 text is a content confirmation only.

Before any /url navigate or DELETE, open verifies the new tab was
actually made current (POST /window/new must make the new tab
current; if it does not, one explicit select is tried, and if that
still fails the driver refuses to navigate or close anything).
The new tab must also increase the tab count by exactly 1, and
the current tab is re-verified right after the navigate. The
open exception handler deletes ONLY when the current tab is the
fixture tab by URL AND by handle (the new handle from this open);
it never deletes blind.

Subcommands (each prints one JSON object on stdout):
  list                      list tabs (titles, urls), current first read
  open                      open a NEW tab on the fixture, viewport gate,
                            harvest #msg-input rect
  switch <url-substr>       make the tab whose URL contains <url-substr>
                            the Marionette current tab, verify by
                            reading it back
  eval <url-substr> <expr>  switch to the tab by URL, evaluate JS expr,
                            print value
  close <scratch-url> <original-url>
                            close the scratch tab (by URL), switch
                            current to the original tab (by URL),
                            verify count and current URL
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
# URL identity of the scratch tab (fix a). The fixture's document
# title is the static 'Two-vision benchmark fixture'; its JS only
# sets the H1 text. Target the tab by this URL substring, never by
# document.title. SCRATCH_H1 is a content confirmation, read from
# the page after navigation, not a tab identity.
SCRATCH_URL_SUBSTR = 'two_vision_fixture.html?clone=zen'
SCRATCH_H1 = 'Clone zen thread'


def _session():
    return zen_dom.ZenSession()


def _handles(z):
    return z._wd("GET", f"/session/{z.session}/window/handles")["value"]


def _current(z):
    return z._wd("GET", f"/session/{z.session}/window")["value"]


def _title(z):
    return z._wd("GET", f"/session/{z.session}/title")["value"]


def _url(z):
    return z._wd("GET", f"/session/{z.session}/url")["value"]


def _scan(z):
    """(entries, full_handles) from a fresh list_tabs scan.

    Entries carry truncated handles (8 chars), titles, and URLs.
    Full handles come from the handle list. The scan switches
    through tabs and restores the original tab afterwards (that is
    list_tabs behavior); it only reads. NOTE (Redteam F4): the
    entries and the handle list are two separate fetches at
    different moments, not one atomic snapshot. list_tabs fetches
    the handle list at its own start, switches through tabs, and
    restores; _handles fetches the list again after list_tabs
    returns. A tab opening or closing mid-scan makes _full_handle
    raise (fail-closed), never match the wrong tab.
    """
    return z.list_tabs(), _handles(z)


def _full_handle(full_handles, prefix):
    """The one full handle starting with prefix. Refuses on zero
    (gone) or more than one (ambiguous prefix)."""
    matches = [h for h in full_handles if h.startswith(prefix)]
    if not matches:
        raise zen_dom.ZenDomError(
            'no handle starts with %r (%d handles)'
            % (prefix, len(full_handles)))
    if len(matches) > 1:
        raise zen_dom.ZenDomError(
            'handle prefix %r is ambiguous (%d matches)'
            % (prefix, len(matches)))
    return matches[0]


def _find_in_scan(entries, substr):
    """Tab entry whose URL contains substr, or None when no tab
    matches. Raises on more than one match: URL identity must be
    unique, and the caller must never pick blindly. Entries with
    no URL (a failed read) are skipped, never matched.
    """
    matches = [e for e in entries
               if isinstance(e.get('url'), str)
               and substr in e['url']]
    if not matches:
        return None
    if len(matches) > 1:
        raise zen_dom.ZenDomError(
            'URL %r matches %d tabs, refusing to pick one'
            % (substr, len(matches)))
    return matches[0]


def _resolve_url(z, substr):
    """Full handle of the one tab whose URL contains substr.

    Resolved fresh inside this session, never from a stored
    handle. Raises when no tab matches or the match is
    ambiguous. One scan only (see _scan: the entry and the
    handle list are two fetches at different moments, so a tab
    opening or closing mid-scan makes _full_handle raise
    instead of matching the wrong tab).
    """
    entries, full = _scan(z)
    entry = _find_in_scan(entries, substr)
    if entry is None:
        raise zen_dom.ZenDomError(
            'no tab URL contains %r' % (substr,))
    return _full_handle(full, entry['handle'])


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
        url_before = _url(z)
        # Pre-check (fix b): no tab may already carry the fixture
        # URL. Two fixture tabs would make URL identity ambiguous,
        # and the new tab could not be told apart from the stale
        # one. Refuse before opening anything.
        entries, _full = _scan(z)
        if _find_in_scan(entries, SCRATCH_URL_SUBSTR) is not None:
            raise zen_dom.ZenDomError(
                'a tab already shows the fixture URL; refusing to '
                'open a second one')
        resp = z._wd("POST", f"/session/{z.session}/window/new",
                     {"type": "tab"})
        new_handle = resp["value"]["handle"]
        # Hardening (Council 1 C4): the new tab must increase the
        # tab count by exactly 1. If /window/new ever returned a
        # stale or existing handle, the (c) check below would pass
        # on the wrong tab. A count that did not grow means no new
        # tab exists to navigate, so refuse before any navigate
        # or DELETE.
        count_after_new = len(_handles(z))
        if count_after_new != len(before) + 1:
            raise zen_dom.ZenDomError(
                'new tab did not increase the tab count '
                '(%d -> %d); refusing to navigate or close'
                % (len(before), count_after_new))
        # Fix (c): the new tab must actually be current before any
        # /url navigate or DELETE. Marionette may leave the
        # previous tab current (the run 2 incident: the navigate
        # rewrote the owner's tab and the DELETE closed it). Try
        # one explicit select; if the new tab still is not
        # current, refuse outright: no navigate, no close.
        current_now = _current(z)
        selected_by = 'window/new'
        if current_now != new_handle:
            z._wd("POST", f"/session/{z.session}/window",
                  {"handle": new_handle})
            current_now = _current(z)
            selected_by = 'explicit-select'
        if current_now != new_handle:
            raise zen_dom.ZenDomError(
                'new tab was not made current (current %s != new '
                '%s); refusing to navigate or close'
                % (current_now[:8], new_handle[:8]))
        try:
            z._wd("POST", f"/session/{z.session}/url",
                  {"url": FIXTURE_URL})
            # Hardening (Redteam F1): re-verify the current tab is
            # still the new scratch tab AFTER the navigate. The (c)
            # check and the navigate are two separate HTTP calls;
            # a focus change in between would navigate the wrong
            # tab (the owner's), and every later check (URL, H1,
            # readyState) would still pass on it because they
            # confirm page content, not which tab holds it. The
            # WebDriver protocol offers no atomic
            # verify-and-navigate, so detection plus refusal is
            # the best available: the tab content is changed, but
            # the tab survives, and the handler below will not
            # delete it.
            current_after_nav = _current(z)
            if current_after_nav != new_handle:
                raise zen_dom.ZenDomError(
                    'current tab changed during navigate (current '
                    '%s != new %s); refusing'
                    % (current_after_nav[:8], new_handle[:8]))
            deadline = time.perf_counter() + 10
            ready = ""
            while time.perf_counter() < deadline:
                ready = z.evaluate("return document.readyState")
                if ready == "complete":
                    break
                time.sleep(0.1)
            # Fix (a): identify the scratch tab by URL, never by
            # document.title. The fixture title is the static
            # 'Two-vision benchmark fixture'; the H1 text is a
            # content confirmation that the clone JS ran.
            url = _url(z)
            if SCRATCH_URL_SUBSTR not in url:
                raise zen_dom.ZenDomError(
                    'navigated tab URL %r does not contain %r'
                    % (url, SCRATCH_URL_SUBSTR))
            h1 = z.evaluate(
                "return document.getElementById('title') ? "
                "document.getElementById('title').textContent : null;")
            if h1 != SCRATCH_H1:
                raise zen_dom.ZenDomError(
                    'scratch tab H1 %r != %r' % (h1, SCRATCH_H1))
            if ready != "complete":
                raise zen_dom.ZenDomError(
                    'scratch tab readyState %r, not complete' % (ready,))
            title = _title(z)
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
                    'title': title, 'url': url, 'h1': h1,
                    'selected_by': selected_by,
                    'ready': ready,
                    'count_before': len(before),
                    'count_after_new': count_after_new,
                    'count_after': len(_handles(z)),
                    'current_before': current_before[:8],
                    'title_before': title_before,
                    'url_before': url_before,
                    'metrics': metrics, 'rect': rect,
                    'element_at_point': at,
                    'viewport_ok': viewport_ok,
                    'harvest': harvest}
        except Exception:
            # Close ONLY the scratch tab. DELETE closes the
            # CURRENT window, so first confirm the current tab
            # really is the scratch tab: its URL must contain
            # the fixture substring AND its handle must be the
            # new handle from this open. The URL alone is not
            # enough (Redteam F1): an owner tab navigated to the
            # fixture URL IS the fixture tab by URL, so a
            # URL-only check would delete it. When the current
            # tab is anything else, delete nothing and leave
            # every tab untouched. After a scratch DELETE,
            # best-effort restore the tab that was current
            # before the open.
            try:
                cur_url = _url(z)
            except Exception:
                cur_url = None
            try:
                cur_handle = _current(z)
            except Exception:
                cur_handle = None
            if (cur_url is not None
                    and SCRATCH_URL_SUBSTR in cur_url
                    and cur_handle == new_handle):
                try:
                    z._wd("DELETE", f"/session/{z.session}/window", {})
                except Exception:
                    pass
                try:
                    _switch(z, current_before)
                except Exception:
                    pass
            raise


def cmd_switch(url_substr):
    with _session() as z:
        full = _resolve_url(z, url_substr)
        _switch(z, full)
        return {'ok': True, 'handle': full[:8], 'title': _title(z),
                'url': _url(z)}


def cmd_eval(url_substr, expr):
    with _session() as z:
        full = _resolve_url(z, url_substr)
        _switch(z, full)
        value = z.evaluate("return (%s);" % expr)
        return {'ok': True, 'handle': full[:8], 'url': _url(z),
                'value': value}


def cmd_close(scratch_substr, original_url):
    """Close the scratch tab (by URL), restore the original tab
    (by URL). The scratch close itself is precise by URL, so it
    runs even when the original tab is gone or ambiguous; the
    restore step never guesses. When the scratch tab is already
    gone, the goal is already true and only the restore runs.
    """
    with _session() as z:
        handles = _handles(z)
        count_before = len(handles)
        entries, full = _scan(z)
        scratch = _find_in_scan(entries, scratch_substr)
        if scratch is None:
            result = {'ok': True, 'already_closed': True,
                      'count_before': count_before,
                      'count_after': count_before}
            _restore_original(z, original_url, result)
            return result
        scratch_full = _full_handle(full, scratch['handle'])
        _switch(z, scratch_full)
        z._wd("DELETE", f"/session/{z.session}/window", {})
        after = _handles(z)
        # Verify by a fresh scan that the scratch tab is gone, and
        # re-resolve the original tab after the mutation instead
        # of trusting a handle from before the DELETE.
        entries_after, _full_after = _scan(z)
        if _find_in_scan(entries_after, scratch_substr) is not None:
            raise zen_dom.ZenDomError(
                'scratch tab still listed after close')
        result = {'ok': True, 'count_before': count_before,
                  'count_after': len(after)}
        _restore_original(z, original_url, result)
        return result


def _restore_original(z, original_url, result):
    """Best-effort switch to the original tab, by URL. Never
    guesses: when the URL is missing or matches more than one
    tab, the current tab is left as Zen activated it and the
    result says so. A scan failure is an error, not ambiguity
    (Council 3 C5): it is reported as scan_error, not
    original_ambiguous. A failure to resolve or switch to the
    original tab after the scratch tab is already deleted is
    reported as restore_failed, not raised: the close already
    succeeded, and the runner records the outcome instead of
    masking it with an exception.
    """
    try:
        entries, full = _scan(z)
    except zen_dom.ZenDomError:
        result['original_missing'] = False
        result['original_ambiguous'] = False
        result['scan_error'] = True
        result['current_title'] = _title(z)
        result['current_url'] = _url(z)
        return
    try:
        orig = _find_in_scan(entries, original_url)
    except zen_dom.ZenDomError:
        orig = None
        ambiguous = True
    else:
        ambiguous = False
    if orig is None:
        result['original_missing'] = not ambiguous
        result['original_ambiguous'] = ambiguous
        result['current_title'] = _title(z)
        result['current_url'] = _url(z)
        return
    try:
        orig_full = _full_handle(full, orig['handle'])
        _switch(z, orig_full)
    except zen_dom.ZenDomError:
        result['original_missing'] = False
        result['original_ambiguous'] = False
        result['restore_failed'] = True
        result['current_title'] = _title(z)
        result['current_url'] = _url(z)
        return
    result['current_title'] = _title(z)
    result['current_url'] = _url(z)
    result['current_handle'] = orig_full[:8]


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
