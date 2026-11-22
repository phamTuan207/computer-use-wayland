"""Redteam CLICK3-RTR2: break the AMEND3 surgical fix pass.

Worker CLICK3-RTR2, round 2 redteam. Every test asserts the REQUIRED
behavior, so a test that fails on the current code IS the finding: the
code does the wrong thing, and the test names what it must do instead.
Tests that pass are marked SURVIVES in the log: the attack fails and
the code holds. VM only, no live laptop, no browser tasks, never
ydotool. No em dash or en dash anywhere. Run:
python3 tests/test_click3_redteam2.py
"""
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import dom_act
import fastpath
import zen_dom
from test_dom_act import FakeDomSession, G30_FIELD, G30_META
from test_zen_dom import FakeWdSession
from test_keyboard_preflight import DesktopPreflight, cu

NODE = shutil.which('node')


def _blank(w=20, h=20):
    from PIL import Image
    return Image.new('RGB', (w, h))


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


class R3aStackedFieldTests(unittest.TestCase):
    def test_band_stacked_fields_low_click_with_x_range_must_not_verify(self):
        # R3a, AMEND3 residual: the band is narrowed in x only. The y
        # window is still anchor_y +- 12 around the CLICK point, not
        # the field rect. Two stacked fields share the x-range; a
        # click near the bottom edge of the upper field puts the
        # lower field's first line inside the band, so text typed
        # into the LOWER field verifies the UPPER field's type.
        # Upper field A spans y 100..120, click at y 118; lower
        # field B spans y 124..144 and shares x 100..300.
        # TESTREPAIR (round 3): y_range=(100, 120) added. Without it
        # the two pixels (y 110 and y 126) are symmetric about the
        # anchor 118 and no symmetric band can distinguish them; the
        # field y-range is what distinguishes them.
        from PIL import Image
        old = Image.new('RGB', (400, 200))
        new = old.copy()
        for x in range(110, 122):
            new.putpixel((x, 126), (255, 255, 255))
        self.assertFalse(
            cu._input_line_changed(old, new, 118, x_range=(100, 300),
                                   y_range=(100, 120)),
            'text in the stacked lower field verified the upper '
            'field: the band y is click-anchored, not field-anchored')

    def test_band_text_inside_target_field_still_verifies(self):
        # Positive control for the stacked test: the same 12 pixels
        # inside the target field itself (y 110, on the click line)
        # MUST verify, so the band is not blind, only mis-aimed.
        from PIL import Image
        old = Image.new('RGB', (400, 200))
        new = old.copy()
        for x in range(110, 122):
            new.putpixel((x, 110), (255, 255, 255))
        self.assertTrue(
            cu._input_line_changed(old, new, 118, x_range=(100, 300)),
            'text inside the target field stopped verifying')

    def test_band_text_below_band_must_not_verify(self):
        # Negative control: text one field further down (y 140,
        # outside anchor 118 +- 12) must not verify, so the test
        # setup discriminates by y.
        from PIL import Image
        old = Image.new('RGB', (400, 200))
        new = old.copy()
        for x in range(110, 122):
            new.putpixel((x, 140), (255, 255, 255))
        self.assertFalse(
            cu._input_line_changed(old, new, 118, x_range=(100, 300)),
            'text below the band verified')


class R3aUnwiredPathTests(DesktopPreflight):
    def test_band_wrong_field_unwired_path_reports_ok(self):
        # R3a, AMEND3 residual: the x-range only reaches desktop_act
        # through dom_act.focus_type and the first_action fallback.
        # CodeExecBackend.act and the cu CLI act path never pass
        # type_x_ranges (and pass no DOM hooks without a session), so
        # a plain code-exec / CLI type batch still verifies on the
        # old full-width band. 12 real text pixels in ANOTHER field
        # on the anchor line, no type_check, no type_x_ranges.
        # TESTREPAIR (round 3): rewritten in two halves, because the
        # full wired path cannot exercise the band: desktop_act runs
        # the DOM type_check first, and it decides the batch either
        # way (pass: dom-value, band skipped; fail: error set, band
        # skipped), so through CodeExecBackend.act the pixel band is
        # never the decider. Half 1 proves the wiring: a desktop_act
        # spy records that CodeExecBackend.act threads the grounded
        # ranges of the target field (rect x 12..20, y 8..12 in the
        # 20x20 fixture, so [12.0, 20.0] x [8.0, 12.0]) to
        # desktop_act. Half 2 proves the behavior: a direct
        # desktop_act call with THOSE ranges (taken from the spy, not
        # hardcoded) and no type_check hook must not verify
        # wrong-field pixels at x 0..11, while right-field pixels at
        # x 12..17 still verify, so the ranges narrow the band
        # instead of blinding it. The Codex "or" branch (band-only
        # unverified without ranges) is still NOT adopted: it would
        # break the control test_click_type_text_in_input_line_verifies
        # and the relay test. The test name is kept so the round-2/3
        # review references still resolve.
        def _hypr(env, query):
            if query == 'monitors':
                return [dict(self.monitor)]
            if query == 'activewindow':
                return {'address': 'fixture'}
            if query == 'cursorpos':
                return {'x': 15, 'y': 10}
            raise AssertionError('unexpected compositor query ' + query)
        self.hypr_mock.side_effect = _hypr
        from PIL import Image
        from unittest import mock
        wrong = Image.new('RGB', (20, 20))
        for x in range(0, 12):
            wrong.putpixel((x, 10), (255, 255, 255))
        self.after_image = wrong
        field = {'rect': {'x': 12, 'y': 8, 'width': 8, 'height': 4},
                 'focused': True, 'value': '', 'covered': False}
        session = FakeDomSession({'#msg-input': field})
        backend = cu.CodeExecBackend({})
        seen = {}
        real_desktop_act = cu.desktop_act

        def _spy(env, meta, actions, **kwargs):
            seen['type_x_ranges'] = kwargs.get('type_x_ranges')
            seen['type_y_ranges'] = kwargs.get('type_y_ranges')
            return real_desktop_act(env, meta, actions, **kwargs)

        with mock.patch.object(cu, 'desktop_act', side_effect=_spy):
            backend.act(
                self.meta,
                [{'type': 'click', 'x': 15, 'y': 10, 'scope': 'window',
                  'observation_id': self.meta['id']},
                 {'type': 'type', 'text': 'hello', 'scope': 'window',
                  'observation_id': self.meta['id']}],
                None, dom_session=session, dom_selector='#msg-input')
        self.assertEqual(seen.get('type_x_ranges'), [[12.0, 20.0]],
                         'the wired path did not thread the grounded '
                         'x-range to desktop_act: %s' % (seen,))
        self.assertEqual(seen.get('type_y_ranges'), [[8.0, 12.0]],
                         'the wired path did not thread the grounded '
                         'y-range to desktop_act: %s' % (seen,))
        result = cu.desktop_act(
            {}, self.meta,
            [{'type': 'click', 'x': 15, 'y': 10},
             {'type': 'type', 'text': 'hello'}],
            type_x_ranges=seen['type_x_ranges'],
            type_y_ranges=seen['type_y_ranges'])
        self.assertFalse(result['ok'],
                         'wrong-field pixels verified the type with '
                         'the wired ranges supplied: %s' % (result,))
        self.assertIs(result['type_verified'], False)
        self.assertEqual(result['error_code'], 'type_unverified')
        right = Image.new('RGB', (20, 20))
        for x in range(12, 18):
            right.putpixel((x, 10), (255, 255, 255))
        self.after_image = right
        result = cu.desktop_act(
            {}, self.meta,
            [{'type': 'click', 'x': 15, 'y': 10},
             {'type': 'type', 'text': 'hello'}],
            type_x_ranges=seen['type_x_ranges'],
            type_y_ranges=seen['type_y_ranges'])
        self.assertTrue(result['ok'],
                        'the wired ranges blinded the band for '
                        'right-field pixels: %s' % (result,))
        self.assertIs(result['type_verified'], True)

    def test_codeexec_and_cli_act_paths_never_supply_x_ranges(self):
        # BEHAVIOURAL REPLACEMENT for the old source-text pin (B5
        # mutation evidence: forcing type_ranges = [[0.0, 20.0]]
        # unconditionally in CodeExecBackend.act still passed the
        # pin, because it only asserted the string 'type_x_ranges'
        # appears in the act source). On the unwired path (no DOM
        # session, no --dom-selector) act must pass
        # type_x_ranges=None to desktop_act, so an unconditional
        # range fails here. The CLI act branch shares the same
        # helper (dom_act.ground_field_ranges returns (None, None)
        # when nothing grounds; covered by
        # test_missing_range_is_logged_not_silent), so the unwired
        # CLI path is covered by the same unit, not by a source
        # pin. The test name is kept so the round-2/3 review
        # references still resolve.
        from unittest import mock
        backend = cu.CodeExecBackend({})
        seen = {}

        def _spy(env, meta, actions, **kwargs):
            seen['type_x_ranges'] = kwargs.get('type_x_ranges')
            seen['type_y_ranges'] = kwargs.get('type_y_ranges')
            return {'ok': True, 'completed': 1}

        with mock.patch.object(cu, 'desktop_act', side_effect=_spy):
            backend.act(
                self.meta,
                [{'type': 'type', 'text': 'hello', 'scope': 'window',
                  'observation_id': self.meta['id']}],
                None)
        self.assertIsNone(
            seen.get('type_x_ranges'),
            'the unwired path supplied an x-range to desktop_act: '
            '%s' % (seen,))
        self.assertIsNone(
            seen.get('type_y_ranges'),
            'the unwired path supplied a y-range to desktop_act: '
            '%s' % (seen,))


class GeometryTests(unittest.TestCase):
    def test_viewport_origin_factor2_small_window_false_refusal(self):
        # Geometry, AMEND3 step 5 residual: viewport_origin divides
        # the window size by the factor for the closure check, but
        # the containment check then compares a SCREEN-px absolute
        # origin against a CSS-px window rect. At factor 2 a small
        # window (800 screen px wide, 240 CSS px sidebar) has a
        # perfectly valid viewport origin that the check refuses:
        # absolute x 580 is inside the true window rect 100..900
        # screen px, but outside the CSS-px rect 100..500.
        session = FakeWdSession(['aaa11111'])
        session.dom_origin = [240, 8]
        session.dom_factor = 2
        session.dom_inner = [152, 284]
        session.dom_outer = [400, 300]
        try:
            origin = session.viewport_origin([100, 100], [800, 600])
        except Exception as exc:
            self.fail('valid factor-2 geometry refused with %s; the '
                      'absolute origin [580, 116] is inside the true '
                      'window rect 100..900 screen px' % (exc,))
        self.assertEqual(origin, [580, 116],
                         'valid factor-2 geometry returned a wrong '
                         'origin: %s' % (origin,))
        true_absolute = [100 + 240 * 2, 100 + 8 * 2]
        self.assertTrue(100 <= true_absolute[0] < 100 + 800
                        and 100 <= true_absolute[1] < 100 + 600,
                        'the refused origin is inside the true window')

    def test_geometry_check_accepts_factor_forgotten_origin(self):
        # Geometry, validator weakness at factor != 1: the same
        # mixed-unit containment accepts a WRONG origin when the
        # caller forgets the factor. At factor 2 the true absolute
        # origin is (2989, 930); the factor-forgotten (2749, 922) is
        # 240 screen px off, yet check_viewport_geometry returns it
        # without raising, because the CSS-px window rect is wide
        # enough to contain it. The check cannot catch the exact
        # mistake it exists to catch once the factor is not 1.
        got = None
        with self.assertRaises(zen_dom.ZenDomError):
            got = zen_dom.check_viewport_geometry(
                [240, 8], [2749, 922], [2509, 914], [931.5, 588],
                [690, 572], None)
        self.assertNotEqual(got, [2989, 930],
                            'the accepted origin is 240 screen px off '
                            'the true one and was still accepted')


class R1StaleOriginTests(unittest.TestCase):
    def test_stale_window_origin_accepted_silently(self):
        # R1 residual: the chain trusts the window origin from the
        # observation meta and never re-reads it live (no hyprctl
        # call anywhere in the chain). When the window moved between
        # the observation and the grounding, viewport_origin returns
        # a wrong-but-internally-consistent origin with no error,
        # and on a screen-scope observation the wrong point still
        # lands inside the image, so the click goes to where the
        # window WAS, silently.
        # TESTREPAIR (round 3): this test documents the stale value
        # only. viewport_origin called directly returns the stale
        # [340, 108] the meta implies; the mapped point is 1271
        # image px from the true point, which no return value can
        # fix at this level. The ground-time refusal is the sibling
        # test below: ground_input with a live origin that disagrees
        # with the meta must refuse.
        session = FakeWdSession(['aaa11111'])
        session.dom_origin = [240, 8]
        session.dom_inner = [1615, 1160]
        session.dom_outer = [1863, 1176]
        stale = session.viewport_origin([100, 100], [1863, 1176])
        self.assertEqual(stale, [340, 108],
                         'direct viewport_origin returned the stale '
                         '[340, 108] the meta implies; the refusal lives '
                         'in the sibling ground-time test')
        self.assertNotEqual(stale, [2749, 922])
        meta = {'image_size': [1920, 1080],
                'region': [0, 0, 3840, 2160]}
        rect = {'x': 86, 'y': 1101, 'width': 440, 'height': 63}
        point = fastpath.dom_rect_to_image_point(meta, rect, stale, 1)
        true_point = fastpath.dom_rect_to_image_point(
            meta, rect, [2749, 922], 1)
        self.assertTrue(0 <= point[0] < 1920 and 0 <= point[1] < 1080,
                        'stale point fell outside the image')
        dist = ((point[0] - true_point[0]) ** 2
                + (point[1] - true_point[1]) ** 2) ** 0.5
        self.assertGreater(
            dist, 1000,
            'the stale origin maps %.0f image px from the true point '
            '%s: the direct viewport_origin call cannot know the '
            'window moved' % (dist, true_point))

    def test_stale_window_origin_refused_at_ground_time(self):
        # TESTREPAIR (round 3): the ground-time half of the stale
        # origin finding. The meta's window origin is [2533, 914]
        # (G30_META) but a live re-read reports [2600, 914]: the
        # window moved, so ground_input must refuse instead of
        # clicking where the window was.
        session = FakeDomSession({'#msg-input': G30_FIELD},
                                 live_origin=[2600, 914])
        with self.assertRaises(dom_act.DomActError) as caught:
            dom_act.ground_input(session, G30_META, '#msg-input')
        self.assertIn('moved', str(caught.exception))

    def test_region_fallback_readmits_raw_mozinner(self):
        # R1 residual, the literal bypass: _window_origin falls back
        # to the observation REGION origin when window_bounds is
        # absent, and screen-scope observations (cu.observe_screen)
        # carry no window_bounds at all. Against such a meta the
        # region origin is the MONITOR origin, not the window
        # origin, so viewport_origin returns the raw mozInner pair
        # (240, 8) as the absolute origin, the exact old bug, with
        # no error: the containment check passes because the
        # "window" is now the whole monitor.
        # TESTREPAIR (round 3): the fix REFUSES a bounds-less meta,
        # so the test asserts the refusal. The true origin
        # [2749, 922] is not derivable from this meta; only a live
        # hyprctl re-read could supply it, and none exists on the
        # VM, so no ground return could satisfy the old assertions.
        session = FakeWdSession(['aaa11111'])
        session.dom_origin = [240, 8]
        session.dom_inner = [1615, 1160]
        session.dom_outer = [1863, 1176]
        session.dom_fields = {
            '#msg-input': {'rect': {'x': 86, 'y': 1101, 'width': 440,
                                    'height': 63},
                            'focused': True, 'value': '', 'covered': False}}
        meta = {'image_size': [1920, 1080],
                'region': [0, 0, 3840, 2160],
                'monitor_box': [0, 0, 3840, 2160]}
        with self.assertRaises(dom_act.DomActError):
            dom_act.ground_input(session, meta, '#msg-input')


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


class R10FlagTests(unittest.TestCase):
    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_typed_flag_forgeable_by_page_script(self):
        # R10 residual: the V11 flag is a plain property on window
        # (window.__agentCuTyped[selector]), fully writable by page
        # JS. A page script sets it to true and sets the value, with
        # zero input events, and the real arm/typed_flag/verify JS
        # then reports a typed value. isTrusted cannot be forged,
        # but the flag that records it can, in one line.
        # TESTREPAIR (round 3): the arm no longer creates
        # window.__agentCuTyped, so the forge line throws TypeError
        # and is guarded in try/catch (a forgery attempt that throws
        # is itself evidence the surface is gone); the value
        # assertion is fixed to value == 'hello' AND flag False,
        # because the field's value IS 'hello' (the page script set
        # it) and the flag is the discriminator, not the value.
        # TESTREPAIR item 7: arm and flag share one session, so
        # the flag reads the per-arm property name the arm installed.
        session = zen_dom.ZenSession()
        arm = _capture_js('arm_typed_flag', '#msg-input', session=session)
        flag = _capture_js('typed_flag', '#msg-input', session=session)
        verify = _capture_js('verify_typed', '#msg-input', 'hello')
        code = (_TOP_DOC_SHIM
                + "var __armed = " + _wrap_bare_return(arm) + ";\n"
                + "try{window.__agentCuTyped['#msg-input'] = true;}"
                + "catch(_){}\n"
                + "__el.value = 'hello';\n"
                + "var __flag = " + _wrap_bare_return(flag) + ";\n"
                + "var __v = " + _wrap_bare_return(verify) + ";\n"
                + "console.log(JSON.stringify({armed: __armed,"
                " flag: __flag, value: __v && __v.value}));\n")
        out = json.loads(_run_node(code))
        self.assertTrue(out['armed'], 'arm must succeed on a plain input')
        self.assertFalse(out['flag'],
                         'page script forged the typed flag with zero '
                         'input events: %s' % (out,))
        self.assertEqual(out['value'], 'hello')

    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_typed_flag_sticky_across_js_set_value(self):
        # R10 residual: the flag is a sticky boolean, never
        # correlated with the value. One real keystroke (value 'h')
        # sets it, and a page script then replaces the whole value
        # with the expected text; the real JS reports a typed
        # 'hello' that no keystroke ever produced. The flag proves
        # an input event happened at some point, not that THIS value
        # came from input events.
        # TESTREPAIR item 7: arm and flag share one session, so
        # the flag reads the per-arm property name the arm installed.
        session = zen_dom.ZenSession()
        arm = _capture_js('arm_typed_flag', '#msg-input', session=session)
        flag = _capture_js('typed_flag', '#msg-input', session=session)
        verify = _capture_js('verify_typed', '#msg-input', 'hello')
        code = (_TOP_DOC_SHIM
                + "var __armed = " + _wrap_bare_return(arm) + ";\n"
                + "__el.value = 'h';\n"
                + "__el.dispatchEvent({type: 'input', isTrusted: true});\n"
                + "__el.value = 'hello';\n"
                + "var __flag = " + _wrap_bare_return(flag) + ";\n"
                + "var __v = " + _wrap_bare_return(verify) + ";\n"
                + "console.log(JSON.stringify({armed: __armed,"
                " flag: __flag, value: __v && __v.value}));\n")
        out = json.loads(_run_node(code))
        self.assertTrue(out['armed'], 'arm must succeed on a plain input')
        self.assertFalse(out['flag'] and out['value'] == 'hello',
                         'one keystroke plus a JS-set value verified '
                         'as fully typed: %s' % (out,))

    def test_typed_flag_sticky_python_level(self):
        # Same sticky-flag shape through the real Python
        # verify_typed (FakeWdSession models the flag faithfully):
        # one trusted event while the value was 'h', then a page
        # script sets 'hello' with no event; verify_typed with
        # before='' must not pass, because 'hello' never came from
        # typing.
        session = FakeWdSession(['aaa11111'])
        session.dom_origin = [0, 0]
        session.dom_fields = {
            '#msg-input': {'rect': {'x': 86, 'y': 1101, 'width': 440,
                                    'height': 63},
                            'focused': True, 'value': '', 'covered': False}}
        session.arm_typed_flag('#msg-input')
        session.dom_fields['#msg-input']['value'] = 'h'
        session._typed['#msg-input'] = True
        session.dom_fields['#msg-input']['value'] = 'hello'
        self.assertFalse(session.verify_typed('#msg-input', 'hello',
                                              before=''),
                         'sticky flag verified a JS-set value after '
                         'one unrelated keystroke')


class R10IframeArmTests(unittest.TestCase):
    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_arm_typed_flag_misses_iframe_targets(self):
        # R10 + step 6 residual: arm_typed_flag pierces shadow roots
        # in the TOP document only; it has no iframe traversal, while
        # field_value and verify_typed do. For a target inside a
        # same-origin iframe the arm returns false, no listener is
        # ever installed, and a real trusted input event inside the
        # iframe leaves the flag clear, so verify_typed(before=...)
        # can never pass after real typing there. The value IS
        # readable from the iframe (field_value proves it), but the
        # typed path cannot verify it: step 6's "an iframe target
        # reads and verifies" is false for the typed path.
        # TESTREPAIR item 7: arm and flag share one session, so
        # the flag reads the per-arm property name the arm installed.
        # field_value carries no flag state and needs no pairing.
        session = zen_dom.ZenSession()
        arm = _capture_js('arm_typed_flag', '#msg-input', session=session)
        flag = _capture_js('typed_flag', '#msg-input', session=session)
        field_value = _capture_js('field_value', '#msg-input')
        shim = (
            "var window = {};\n"
            "var __listeners = {};\n"
            "var __el = {tagName: 'INPUT', isContentEditable: false,"
            " readOnly: false, value: 'hello',\n"
            " addEventListener: function(t, fn){"
            " (__listeners[t] = __listeners[t] || []).push(fn); },\n"
            " dispatchEvent: function(ev){"
            " var l = __listeners[ev.type] || [];"
            " for (var i = 0; i < l.length; i++) l[i](ev);"
            " return true; }};\n"
            "function MutationObserver(cb){"
            " this.observe = function(){}; }\n"
            "var __frameDoc = {\n"
            " querySelector: function(sel){"
            " return sel === '#msg-input' ? __el : null; },\n"
            " querySelectorAll: function(sel){ return []; }};\n"
            "var __frame = {contentWindow: {document: __frameDoc}};\n"
            "var document = {\n"
            " querySelector: function(sel){ return null; },\n"
            " querySelectorAll: function(sel){"
            " return sel === 'iframe' ? [__frame] : []; }};\n")
        code = (shim
                + "var __armed = " + _wrap_bare_return(arm) + ";\n"
                + "__el.dispatchEvent({type: 'input',"
                " isTrusted: true});\n"
                + "var __flag = " + _wrap_bare_return(flag) + ";\n"
                + "var __fv = " + _wrap_bare_return(field_value) + ";\n"
                + "console.log(JSON.stringify({armed: __armed,"
                " flag: __flag, fieldValue: __fv}));\n")
        out = json.loads(_run_node(code))
        self.assertEqual(out['fieldValue'], 'hello',
                         'field_value must reach the iframe input')
        self.assertTrue(out['flag'],
                        'real typing inside the iframe left the flag '
                        'clear (arm never reached it): %s' % (out,))


class IframeReadTests(unittest.TestCase):
    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_field_value_misses_nested_iframe(self):
        # Step 6 residual: find() traverses ONE level of iframes.
        # A same-origin target inside an iframe inside an iframe
        # returns null: the pierce inside the first frame document
        # never looks for frames of its own. Fail-closed, but the
        # "same-origin frames" claim covers only one level.
        script = _capture_js('field_value', '#msg-input')
        shim = (
            "var __el = {tagName: 'INPUT', isContentEditable: false,"
            " value: 'hello'};\n"
            "var __doc2 = {\n"
            " querySelector: function(sel){"
            " return sel === '#msg-input' ? __el : null; },\n"
            " querySelectorAll: function(sel){ return []; }};\n"
            "var __f2 = {contentWindow: {document: __doc2}};\n"
            "var __doc1 = {\n"
            " querySelector: function(sel){ return null; },\n"
            " querySelectorAll: function(sel){"
            " return sel === 'iframe' ? [__f2] : []; }};\n"
            "var __f1 = {contentWindow: {document: __doc1}};\n"
            "var document = {\n"
            " querySelector: function(sel){ return null; },\n"
            " querySelectorAll: function(sel){"
            " return sel === 'iframe' ? [__f1] : []; }};\n")
        out = _run_node(shim + "console.log(JSON.stringify("
                        + _wrap_bare_return(script) + "));")
        self.assertEqual(json.loads(out), 'hello',
                         'nested same-origin iframe target unread: %s'
                         % (out,))

    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_field_value_misses_iframe_in_shadow_root(self):
        # Step 6 residual: the frame loop uses
        # document.querySelectorAll('iframe'), which sees light-DOM
        # iframes only. An iframe inside a shadow root is invisible
        # to it, and pierce() recurses into shadow roots but never
        # into iframes, so the target reads null.
        script = _capture_js('field_value', '#msg-input')
        shim = (
            "var __el = {tagName: 'INPUT', isContentEditable: false,"
            " value: 'hello'};\n"
            "var __doc2 = {\n"
            " querySelector: function(sel){"
            " return sel === '#msg-input' ? __el : null; },\n"
            " querySelectorAll: function(sel){ return []; }};\n"
            "var __f1 = {contentWindow: {document: __doc2}};\n"
            "var __shadow = {\n"
            " querySelector: function(sel){ return null; },\n"
            " querySelectorAll: function(sel){ return [__f1]; }};\n"
            "var __host = {tagName: 'DIV', shadowRoot: __shadow};\n"
            "var document = {\n"
            " querySelector: function(sel){ return null; },\n"
            " querySelectorAll: function(sel){"
            " return sel === 'iframe' ? [] : [__host]; }};\n")
        out = _run_node(shim + "console.log(JSON.stringify("
                        + _wrap_bare_return(script) + "));")
        self.assertEqual(json.loads(out), 'hello',
                         'iframe inside a shadow root unread: %s'
                         % (out,))

    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_harvest_misses_iframe_targets(self):
        # Step 6 residual, one-shot path: harvest() pierces shadow
        # roots in the top document only and has no frame loop at
        # all, while locate() traverses same-origin iframes. The
        # VISION 1 one-shot grounding therefore returns null for an
        # iframe target that per-element grounding finds, so the two
        # grounding paths disagree about iframe targets.
        script = _capture_js('harvest', ['#msg-input'])
        shim = (
            "var window = {mozInnerScreenX: 240, mozInnerScreenY: 8,"
            " devicePixelRatio: 1, screenPixelsPerCSSPixel: 1,"
            " visualViewport: null, innerWidth: 1615,"
            " innerHeight: 1160, outerWidth: 1863,"
            " outerHeight: 1176};\n"
            "var __el = {tagName: 'INPUT',\n"
            " getBoundingClientRect: function(){ return {x: 86,"
            " y: 1101, width: 440, height: 63}; }};\n"
            "var __frameDoc = {\n"
            " querySelector: function(sel){"
            " return sel === '#msg-input' ? __el : null; },\n"
            " querySelectorAll: function(sel){ return []; }};\n"
            "var __frame = {contentWindow: {document: __frameDoc}};\n"
            "var document = {activeElement: null,\n"
            " querySelector: function(sel){ return null; },\n"
            " querySelectorAll: function(sel){"
            " return sel === 'iframe' ? [__frame] : []; },\n"
            " elementFromPoint: function(){ return null; }};\n")
        code = (shim + "var __h = " + _wrap_bare_return(script) + ";\n"
                + "console.log(JSON.stringify({item:"
                " __h.items['#msg-input']}));\n")
        out = json.loads(_run_node(code))
        self.assertIsNotNone(out['item'],
                             'harvest returned null for an iframe '
                             'target that locate() finds: %s' % (out,))


class CdpSetValueTests(unittest.TestCase):
    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_set_value_newline_text_fails_verification(self):
        # Attack (1): the AMEND3 delta (oldValue capture, dispatch
        # only on change) is sound for plain strings, but the
        # read-back compares e.value against the UNSANITIZED text.
        # The HTML Standard sanitizes values in the engine: a
        # single-line input strips newlines, a textarea normalizes
        # CR and CRLF to LF. So set_value can never set text
        # containing a newline: the set lands (normalized) and the
        # call still reports 'value verification failed'. Proof
        # runs the REAL set_value template from scripts/cdp.mjs
        # against a spec-faithful fake DOM; no live browser exists
        # on this VM, so the engine half is the documented rule,
        # not a live observation.
        src = (ROOT / 'scripts' / 'cdp.mjs').read_text()
        start = src.index('const source=`') + len('const source=`')
        template = src[start:src.index('`;', start)]
        hstart = src.index('const HIT_USABLE=`') + len('const HIT_USABLE=`')
        hit_usable = src[hstart:src.index('`;', hstart)]
        self.assertIn('oldValue', template)
        driver = (
            "var __tpl = " + json.dumps(template) + ";\n"
            "var __hitUsableSrc = " + json.dumps(hit_usable) + ";\n"
            "var HIT_USABLE = eval(__hitUsableSrc);\n"
            "var __current = null;\n"
            "function pageState(snapshot, locator){ return __current; }\n"
            "var request = {snapshot: 'before'};\n"
            "var locator = JSON.stringify({ref: 'e1'});\n"
            "var document = {elementFromPoint: function(x, y){"
            " return __current; }};\n"
            "function getComputedStyle(e){"
            " return {display: 'block', visibility: 'visible'}; }\n"
            "var innerWidth = 100, innerHeight = 100;\n"
            "class InputEvent { constructor(t, o){ this.type = t;"
            " this.isTrusted = false; Object.assign(this, o || {}); } }\n"
            "class Event { constructor(t, o){ this.type = t;"
            " this.isTrusted = false; Object.assign(this, o || {}); } }\n"
            "class FakeInput { get value(){ return this._value || ''; }"
            " set value(v){"
            " this._value = String(v).replace(/[\\r\\n]/g, ''); } }\n"
            "class FakeTextarea { get value(){ return this._value || ''; }"
            " set value(v){"
            " this._value = String(v).replace(/\\r\\n?/g, '\\n'); } }\n"
            "var HTMLInputElement = FakeInput;"
            " var HTMLTextAreaElement = FakeTextarea;\n"
            "function makeEl(tag, type, initial){\n"
            " var proto = tag === 'INPUT' ? FakeInput.prototype"
            " : FakeTextarea.prototype;\n"
            " var el = Object.create(proto);\n"
            " el.tagName = tag; el.type = type || 'text';\n"
            " el._value = initial || ''; el.disabled = false;\n"
            " el.readOnly = false; el.maxLength = -1;\n"
            " el.isConnected = true; el.events = [];\n"
            " el.matches = function(s){ return false; };\n"
            " el.getAttribute = function(k){ return null; };\n"
            " el.closest = function(s){ return null; };\n"
            " el.contains = function(o){ return o === el; };\n"
            " el.getClientRects = function(){ return [{}]; };\n"
            " el.getBoundingClientRect = function(){ return {left: 10,"
            " top: 10, right: 30, bottom: 30, width: 20, height: 20}; };\n"
            " el.dispatchEvent = function(ev){"
            " el.events.push({type: ev.type, trusted: ev.isTrusted});"
            " return true; };\n"
            " return el; }\n"
            "function runCase(tag, type, initial, text){\n"
            " var el = makeEl(tag, type, initial);\n"
            " __current = el;\n"
            " var text = JSON.stringify(text);\n"
            " var __iife = eval('`' + __tpl + '`');\n"
            " var res = eval(__iife);\n"
            " return {ok: res.ok, error: res.error || null,"
            " events: el.events.map(function(e){ return e.type; }),"
            " value: el.value}; }\n"
            "var out = {textarea_crlf: runCase('TEXTAREA', null, '',"
            " 'a\\r\\nb'),\n"
            " input_newline: runCase('INPUT', 'text', '', 'a\\nb'),\n"
            " input_newline_only_change: runCase('INPUT', 'text',"
            " 'hello', 'hello\\n'),\n"
            " same_text: runCase('INPUT', 'text', 'same', 'same'),\n"
            " whitespace_change: runCase('INPUT', 'text', 'hello',"
            " 'hello ')};\n"
            "console.log(JSON.stringify(out));\n")
        out = json.loads(_run_node(driver))
        # The set lands (normalized) but the call fails: a false
        # failure on text the engine itself canonicalizes.
        self.assertTrue(out['textarea_crlf']['ok'],
                        'CRLF text into a textarea failed although '
                        'the field holds the normalized value: %s'
                        % (out['textarea_crlf'],))
        self.assertEqual(out['textarea_crlf']['value'], 'a\nb')
        self.assertTrue(out['input_newline']['ok'],
                        'newline text into a single-line input failed '
                        'although the field holds the stripped value: '
                        '%s' % (out['input_newline'],))
        self.assertEqual(out['input_newline']['value'], 'ab')
        self.assertTrue(out['input_newline_only_change']['ok'],
                        'newline-only change failed verification: %s'
                        % (out['input_newline_only_change'],))
        # Controls: the AMEND3 delta itself is sound for plain
        # strings. Same text fires no events; a real whitespace
        # change fires both.
        self.assertTrue(out['same_text']['ok'])
        self.assertEqual(out['same_text']['events'], [],
                         'unchanged text fired events: %s'
                         % (out['same_text'],))
        self.assertTrue(out['whitespace_change']['ok'])
        self.assertEqual(out['whitespace_change']['events'],
                         ['input', 'change'],
                         'whitespace-only change fired no events: %s'
                         % (out['whitespace_change'],))

    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_set_value_maxlength_uses_sanitized_length(self):
        # TESTREPAIR (round 3, RT item 8): the maxLength pre-check
        # measured the RAW text, so it refused a set the engine
        # would accept: textarea maxLength 5 with 'ab\r\ncd' (raw 6,
        # sanitized 'ab\ncd' 5 chars) and input maxLength 4 with
        # 'ab\ncd' (raw 5, sanitized 'abcd' 4). The pre-check must
        # compare sanitized.length. Same driver shape as the F1 test
        # above, plus a maxLength per case.
        src = (ROOT / 'scripts' / 'cdp.mjs').read_text()
        start = src.index('const source=`') + len('const source=`')
        template = src[start:src.index('`;', start)]
        hstart = src.index('const HIT_USABLE=`') + len('const HIT_USABLE=`')
        hit_usable = src[hstart:src.index('`;', hstart)]
        self.assertIn('oldValue', template)
        driver = (
            "var __tpl = " + json.dumps(template) + ";\n"
            "var __hitUsableSrc = " + json.dumps(hit_usable) + ";\n"
            "var HIT_USABLE = eval(__hitUsableSrc);\n"
            "var __current = null;\n"
            "function pageState(snapshot, locator){ return __current; }\n"
            "var request = {snapshot: 'before'};\n"
            "var locator = JSON.stringify({ref: 'e1'});\n"
            "var document = {elementFromPoint: function(x, y){"
            " return __current; }};\n"
            "function getComputedStyle(e){"
            " return {display: 'block', visibility: 'visible'}; }\n"
            "var innerWidth = 100, innerHeight = 100;\n"
            "class InputEvent { constructor(t, o){ this.type = t;"
            " this.isTrusted = false; Object.assign(this, o || {}); } }\n"
            "class Event { constructor(t, o){ this.type = t;"
            " this.isTrusted = false; Object.assign(this, o || {}); } }\n"
            "class FakeInput { get value(){ return this._value || ''; }"
            " set value(v){"
            " this._value = String(v).replace(/[\\r\\n]/g, ''); } }\n"
            "class FakeTextarea { get value(){ return this._value || ''; }"
            " set value(v){"
            " this._value = String(v).replace(/\\r\\n?/g, '\\n'); } }\n"
            "var HTMLInputElement = FakeInput;"
            " var HTMLTextAreaElement = FakeTextarea;\n"
            "function makeEl(tag, type, initial, maxLength){\n"
            " var proto = tag === 'INPUT' ? FakeInput.prototype"
            " : FakeTextarea.prototype;\n"
            " var el = Object.create(proto);\n"
            " el.tagName = tag; el.type = type || 'text';\n"
            " el._value = initial || ''; el.disabled = false;\n"
            " el.readOnly = false; el.maxLength = maxLength;\n"
            " el.isConnected = true; el.events = [];\n"
            " el.matches = function(s){ return false; };\n"
            " el.getAttribute = function(k){ return null; };\n"
            " el.closest = function(s){ return null; };\n"
            " el.contains = function(o){ return o === el; };\n"
            " el.getClientRects = function(){ return [{}]; };\n"
            " el.getBoundingClientRect = function(){ return {left: 10,"
            " top: 10, right: 30, bottom: 30, width: 20, height: 20}; };\n"
            " el.dispatchEvent = function(ev){"
            " el.events.push({type: ev.type, trusted: ev.isTrusted});"
            " return true; };\n"
            " return el; }\n"
            "function runCase(tag, type, initial, text, maxLength){\n"
            " var el = makeEl(tag, type, initial, maxLength);\n"
            " __current = el;\n"
            " var text = JSON.stringify(text);\n"
            " var __iife = eval('`' + __tpl + '`');\n"
            " var res = eval(__iife);\n"
            " return {ok: res.ok, error: res.error || null,"
            " events: el.events.map(function(e){ return e.type; }),"
            " value: el.value}; }\n"
            "var out = {textarea_maxlen: runCase('TEXTAREA', null, '',"
            " 'ab\\r\\ncd', 5),\n"
            " input_maxlen: runCase('INPUT', 'text', '', 'ab\\ncd', 4),\n"
            " textarea_over: runCase('TEXTAREA', null, '', 'ab\\r\\ncd', 4),\n"
            " input_over: runCase('INPUT', 'text', '', 'abcd', 3)};\n"
            "console.log(JSON.stringify(out));\n")
        out = json.loads(_run_node(driver))
        self.assertTrue(out['textarea_maxlen']['ok'],
                        'textarea maxLength 5 refused text whose '
                        'sanitized form is 5 chars: %s'
                        % (out['textarea_maxlen'],))
        self.assertEqual(out['textarea_maxlen']['value'], 'ab\ncd')
        self.assertTrue(out['input_maxlen']['ok'],
                        'input maxLength 4 refused text whose '
                        'sanitized form is 4 chars: %s'
                        % (out['input_maxlen'],))
        self.assertEqual(out['input_maxlen']['value'], 'abcd')
        self.assertFalse(out['textarea_over']['ok'])
        self.assertEqual(out['textarea_over']['error'],
                         'value exceeds maxlength')
        self.assertFalse(out['input_over']['ok'])
        self.assertEqual(out['input_over']['error'],
                         'value exceeds maxlength')


if __name__ == '__main__':
    unittest.main()
