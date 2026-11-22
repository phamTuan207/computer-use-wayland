#!/usr/bin/env python3
"""Read-only diagnostic for the run 3 phase 1 abort (W-ZT-B).

Opens one ZenSession, reads the Marionette current tab through the
same endpoints list_tabs uses (GET /window, /url, /title) plus one
JS evaluate of document.URL/title/readyState, then deletes the
session in finally. No tab is opened, navigated, typed into,
clicked, or closed. No switch is issued: the evaluate runs in
whatever tab Marionette already has current.
"""
import sys

sys.path.insert(0, '/home/james/computer-use-wayland/scripts')
import zen_dom


def main():
    with zen_dom.ZenSession() as z:
        cur = z._wd('GET', '/session/%s/window' % z.session)['value']
        url = z._wd('GET', '/session/%s/url' % z.session)['value']
        title = z._wd('GET', '/session/%s/title' % z.session)['value']
        print('current_handle_prefix:', cur[:8])
        print('url_endpoint:', repr(url))
        print('title_endpoint:', repr(title))
        try:
            js = z.evaluate(
                'return JSON.stringify({u: document.URL, '
                't: document.title, rs: document.readyState, '
                'h1: (document.querySelector("h1") || {}).textContent, '
                'inputs: document.querySelectorAll("input").length});')
            print('js:', js)
        except Exception as exc:  # noqa: BLE001 - diagnostic only
            print('js_error:', type(exc).__name__, str(exc)[:200])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
