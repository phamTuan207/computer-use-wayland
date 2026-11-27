"""JS-capture helpers for test_zen_dom (subset of the todolist redteam suite).

On todolist-push this file is the full CLICK3-RTR2 redteam suite
(1002 lines, exercises the todolist-lineage dom_act/cdp paths). Main
does not carry those paths, so only the four helpers test_zen_dom
imports are landed here: _run_node, _capture_js, _wrap_bare_return,
_TOP_DOC_SHIM. The full suite stays on todolist-push; if it is ever
landed on main, this file is replaced wholesale.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import zen_dom

NODE = shutil.which('node')


def _run_node(code):
    proc = subprocess.run([NODE, '-e', code], capture_output=True,
                          text=True, timeout=20)
    if proc.returncode != 0:
        raise AssertionError('node failed: ' + proc.stderr[:500])
    return proc.stdout.strip()


def _capture_js(method_name, *args, session=None):
    """The exact JS string a zen_dom helper sends to evaluate().

    Pass session= to capture several helpers from ONE ZenSession:
    arm_typed_flag and typed_flag share a per-arm property name
    recorded on the session (TESTREPAIR item 7), so a flag captured
    from a different session than its arm would read a name that
    was never installed."""
    if session is None:
        session = zen_dom.ZenSession()
    captured = {}

    def _eval(script, args=None):
        captured['script'] = script
        return None

    session.evaluate = _eval
    try:
        getattr(session, method_name)(*args)
    except Exception:
        pass
    return captured['script']


def _wrap_bare_return(script):
    """A bare `return ...` script (typed_flag, harvest, and since
    DOMZEN-FIX every zen_dom helper) needs a function wrapper to run
    under node -e; IIFEs pass through. The leading comment is
    optional: some helpers carry one (/* zen_harvest */), most do
    not (bare `return (function(){...})()`)."""
    if re.match(r'\s*(?:/\*[^*]*\*/\s*)?return\b', script):
        return '(function(){' + script + '})()'
    return script


_TOP_DOC_SHIM = (
    "var window = {};\n"
    "var __listeners = {};\n"
    "var __el = {tagName: 'INPUT', isContentEditable: false,"
    " readOnly: false, value: '',\n"
    " addEventListener: function(t, fn){"
    " (__listeners[t] = __listeners[t] || []).push(fn); },\n"
    " dispatchEvent: function(ev){ var l = __listeners[ev.type] || [];"
    " for (var i = 0; i < l.length; i++) l[i](ev); return true; }};\n"
    "function MutationObserver(cb){ this.observe = function(){}; }\n"
    "var document = {\n"
    " querySelector: function(sel){"
    " return sel === '#msg-input' ? __el : null; },\n"
    " querySelectorAll: function(sel){ return []; }};\n")
