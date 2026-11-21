"""Redteam CLICK2-RT: break the amend diff e4082ff..4b7d6ac.

Every test asserts the REQUIRED behavior, so a test that fails (or
errors) on the current code IS the finding: the code does the wrong
thing, and the test names what it must do instead. Fix-direction tests
that pass are marked so in their docstrings. VM only, no live laptop,
no browser tasks, no ydotool. Run: python3 tests/test_click2_redteam.py
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
# NOTE: cu must come from test_keyboard_preflight, not a plain import:
# the harness loads cu via importlib spec (its own module object) and
# patches THAT object's focus/window/observe. A plain `import cu` loads
# a second copy whose real focus() runs and raises on the fixture
# address. test_type_verification imports cu the same way.
from test_keyboard_preflight import DesktopPreflight, cu

NODE = shutil.which('node')


class ScriptedAct:
    """Fake act_fn mirroring the desktop_act hook protocol.

    on_type(text) models the field receiving the keystrokes; on_enter()
    models Enter (a send clears the field and records the bubble).
    skip_type models a stubbed type step: wtype exits clean, zero keys.
    """

    def __init__(self, on_type=None, on_enter=None, skip_type=False):
        self.on_type = on_type
        self.on_enter = on_enter
        self.skip_type = skip_type
        self.typed = []
        self.executed = []
        self.calls = 0
        self.enters = 0
        self.sent = []

    def __call__(self, meta, actions, focus_check=None, type_check=None,
                 **kw):
        self.calls += 1
        completed = 0
        focus_done = False
        for act in actions:
            if act.get('type') == 'type' and not focus_done:
                focus_done = True
                if focus_check is not None:
                    try:
                        ok, _reason = focus_check()
                    except Exception:
                        ok = False
                    if not ok:
                        return {'ok': False, 'completed': completed,
                                'error': 'focus check failed',
                                'error_code': 'focus_unverified',
                                'focus_verified': False, 'observes': 0}
            if act.get('type') == 'type':
                if not self.skip_type:
                    self.typed.append(act['text'])
                    if self.on_type:
                        self.on_type(act['text'])
            if act.get('type') == 'key' and act.get('keys') == ['Enter']:
                self.enters += 1
                if self.on_enter:
                    self.on_enter()
            self.executed.append(act)
            completed += 1
        if type_check is not None:
            try:
                ok, _reason = type_check()
            except Exception:
                ok = False
            if not ok:
                return {'ok': False, 'completed': completed,
                        'error': 'type verification failed',
                        'error_code': 'type_unverified',
                        'type_verified': False, 'observes': 0}
        return {'ok': True, 'completed': completed,
                'focus_verified': True, 'type_verified': True,
                'type_verified_basis': 'dom-value', 'observes': 0}


def _blank(w=20, h=20):
    from PIL import Image
    return Image.new('RGB', (w, h))


def _with_pixels(base, points, color=(255, 255, 255)):
    img = base.copy()
    for x, y in points:
        img.putpixel((x, y), color)
    return img


def _run_node(code):
    proc = subprocess.run([NODE, '-e', code], capture_output=True,
                          text=True, timeout=15)
    if proc.returncode != 0:
        raise AssertionError('node failed: ' + proc.stderr[:300])
    return proc.stdout.strip()


def _capture_js(method_name, selector='#msg-input'):
    """The exact JS string a zen_dom helper sends to evaluate()."""
    session = zen_dom.ZenSession()
    captured = {}

    def _eval(script, args=None):
        captured['script'] = script
        return None

    session.evaluate = _eval
    getattr(session, method_name)(selector)
    return captured['script']


class R1ConversionTests(unittest.TestCase):
    def test_raw_moz_inner_screen_origin_must_land(self):
        # R1, rewritten in amend3: the point must land through the
        # corrected chain, zen_dom.viewport_origin output (the
        # absolute origin), not through the raw mozInner pair. Live
        # C12 probe geometry: window (2509, 914), mozInner (240, 8),
        # viewport 1615x1160, absolute origin (2749, 922). Passing
        # the raw pair (240, 8) as the origin is the old bug and must
        # now fail closed instead of being silently rescued.
        session = FakeWdSession(['aaa11111'])
        session.dom_origin = [240, 8]
        session.dom_inner = [1615, 1160]
        session.dom_outer = [1863, 1176]
        origin = session.viewport_origin([2509, 914], [1863, 1176])
        self.assertEqual(origin, [2749, 922])
        meta = {'image_size': [1200, 757],
                'region': [2509, 914, 1863, 1176]}
        rect = {'x': 86, 'y': 1101, 'width': 440, 'height': 63}
        point = fastpath.dom_rect_to_image_point(meta, rect, origin)
        self.assertTrue(0 <= point[0] < 1200 and 0 <= point[1] < 757,
                        'point %s falls outside the observed image' % (point,))
        self.assertAlmostEqual(point[0], 351.7, places=0)
        self.assertAlmostEqual(point[1], 734.4, places=0)
        with self.assertRaises(ValueError):
            fastpath.dom_rect_to_image_point(meta, rect, [240, 8])

    def test_window_origin_added_lands(self):
        # Fix direction (PASSES): window origin + mozInnerScreen +
        # rect center is the true screen point, and it lands inside.
        meta = {'image_size': [1200, 757],
                'region': [2509, 914, 1863, 1176]}
        rect = {'x': 86, 'y': 1101, 'width': 440, 'height': 63}
        point = fastpath.dom_rect_to_image_point(meta, rect, [2749, 922])
        self.assertAlmostEqual(point[0], 351.7, places=0)
        self.assertAlmostEqual(point[1], 734.4, places=0)

    def test_no_dpr_or_zoom_term_recorded(self):
        # R13: no DPR/zoom term exists in the conversion chain, and no
        # snapshot records DPR or zoom. At monitor scale 2 a rect
        # center 306 CSS px from the viewport origin is 612 screen px
        # away; the code maps 306 and lands about 306 screen px off.
        # MDN mozInnerScreenX: reported in CSS pixels, affected by
        # zoom; physical pixels need screenPixelsPerCSSPixel.
        sources = ''
        for name in ('fastpath.py', 'zen_dom.py', 'dom_act.py'):
            sources += (ROOT / 'scripts' / name).read_text()
        self.assertIn('devicePixelRatio', sources)
        self.assertIn('screenPixelsPerCSSPixel', sources)


class R2PrefillTests(unittest.TestCase):
    def test_prefilled_input_stubbed_type_must_not_verify(self):
        # R2: the field already holds the expected text before the
        # batch runs; the type step is stubbed (zero keystrokes) and
        # Enter runs. verify_typed compares equality only, with no
        # before-value and no change requirement, so it passes.
        field = dict(G30_FIELD, value='hello', focused=True)
        session = FakeDomSession({'#msg-input': field})
        act = ScriptedAct(skip_type=True)
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=False)
        self.assertEqual(act.typed, [], 'zero keystrokes were sent')
        self.assertFalse(result['ok'],
                         'prefilled value + stubbed type verified: %s'
                         % (result,))

    def test_js_set_value_without_keystrokes_must_not_verify(self):
        # R10: same channel, different mechanism. A page script sets
        # the value and dispatches synthetic input events; no
        # MutationObserver is armed anywhere (V11 unimplemented), so
        # the DOM value check cannot tell typed text from JS-set text.
        sources = ''
        for name in ('cu.py', 'dom_act.py', 'zen_dom.py'):
            sources += (ROOT / 'scripts' / name).read_text()
        self.assertIn('MutationObserver', sources)
        field = dict(G30_FIELD, value='hello', focused=True)
        session = FakeDomSession({'#msg-input': field})
        act = ScriptedAct(skip_type=True)
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=False)
        self.assertEqual(act.typed, [], 'zero keystrokes were sent')
        self.assertFalse(result['ok'],
                         'JS-set value verified with no typing: %s'
                         % (result,))


class R3BandTests(unittest.TestCase):
    def test_band_wrong_field_same_line_must_not_verify(self):
        # R3a: the band is the FULL image width at the anchor y. Text
        # landing in a different field on the same horizontal line
        # changes the band exactly like text in the target field.
        old = _blank()
        new = _with_pixels(old, [(x, 10) for x in range(0, 3)])
        self.assertFalse(cu._input_line_changed(old, new, 10),
                         'band changed in another field on the same line')

    def test_band_caret_blink_only_must_not_verify(self):
        # R3b: a 3px caret blink (or focus ring) alone changes the band
        # past the min_pixels threshold, with zero text typed. The
        # amend log admits this; the code still reports ok on it.
        old = _blank()
        new = _with_pixels(old, [(10, 10), (11, 10), (12, 10)])
        self.assertFalse(cu._input_line_changed(old, new, 10),
                         'caret blink alone changed the band')

    def test_band_resize_must_not_verify(self):
        # R3c: a size mismatch between frames returns True outright
        # (cu.py _input_line_changed), so a window resize between the
        # pre-batch frame and the after-capture verifies the type.
        old = _blank(20, 20)
        new = _blank(21, 20)
        self.assertFalse(cu._input_line_changed(old, new, 10),
                         'resize alone changed the band')


class R3BandDesktopTests(DesktopPreflight):
    def test_band_wrong_field_reports_ok(self):
        # R3a at the desktop_act level: click (10,10), type hello, no
        # type_check hook. The after image changes only at x 0..2 on
        # the anchor line (another field), yet the batch reports ok.
        self.after_image = _with_pixels(self.image,
                                         [(x, 10) for x in range(0, 3)])
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'click', 'x': 10, 'y': 10},
                                 {'type': 'type', 'text': 'hello'}])
        self.assertFalse(result['ok'],
                         'wrong-field pixels verified the type: %s'
                         % (result,))

    def test_band_caret_only_reports_ok(self):
        # R3b at the desktop_act level: the after image differs only
        # by a 3px caret at the click point, no text anywhere.
        self.after_image = _with_pixels(
            self.image, [(10, 10), (11, 10), (12, 10)])
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'click', 'x': 10, 'y': 10},
                                 {'type': 'type', 'text': 'hello'}])
        self.assertFalse(result['ok'],
                         'caret-only pixels verified the type: %s'
                         % (result,))


class R4UnverifiedOkTests(DesktopPreflight):
    def test_after_capture_false_type_batch_must_not_report_ok(self):
        # R4a: after_capture=False, no type_check hook. The batch
        # reports ok True with type_verified None: ok rests on wtype
        # exit alone, the exact failure the verification was built to
        # kill. The existing test asserts ok True; that test bakes in
        # the hole.
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'type', 'text': 'hello'}],
                                after_capture=False)
        self.assertIsNone(result.get('type_verified'))
        self.assertFalse(result['ok'],
                         'unverified type batch reported ok: %s' % (result,))

    def test_terminal_none_type_batch_must_not_report_ok(self):
        # R4b: expected_terminal_window='none' takes the same skip
        # path (cu.py terminal_address None): ok True, type_verified
        # None, no frame to compare, no DOM check.
        result = cu.desktop_act({}, self.meta,
                                [{'type': 'type', 'text': 'hello'}],
                                expected_terminal_window='none')
        self.assertIsNone(result.get('type_verified'))
        self.assertFalse(result['ok'],
                         'unverified type batch reported ok: %s' % (result,))


class R5StaleDomTests(unittest.TestCase):
    def test_hit_passes_but_point_is_stale(self):
        # R7 (stale DOM): ground_input reads locate, then origin, then
        # hit_check, as three separate evaluates. hit_check re-reads
        # its own rect, so the hit verdict and the clicked point come
        # from different snapshots. Here the element moves between
        # locate and hit_check; the hit passes on the NEW rect while
        # the returned point is the OLD rect center, outside the
        # element. Nothing re-validates the point before the click.
        first = {'x': 86, 'y': 1101, 'width': 440, 'height': 63}
        second = {'x': 86, 'y': 800, 'width': 440, 'height': 63}

        class MovingSession(FakeDomSession):
            def hit_check(self, selector):
                self.fields[selector]['rect'] = second
                return True

        session = MovingSession({'#msg-input': dict(
            G30_FIELD, rect=first)})
        ground = dom_act.ground_input(session, G30_META, '#msg-input')
        current = session.locate('#msg-input')
        self.assertTrue(
            fastpath.point_in_rect(current, ground['point'][0],
                                   ground['point'][1]),
            'ground point %s is outside the live rect %s'
            % (ground['point'], current))

    def test_ground_many_points_go_stale_across_sends(self):
        # R7 (ground_many): the VISION-1 inventory grounds both clone
        # inputs before any send. The first send shifts the layout;
        # the stored second point is never re-validated before use,
        # and the combined design's HCU live guard exists only as
        # design text, in no code.
        fields = {
            '#clone1-input': {'rect': {'x': 86, 'y': 1101, 'width': 440,
                                       'height': 63},
                              'focused': True, 'value': None,
                              'covered': False},
            '#clone2-input': {'rect': {'x': 86, 'y': 1000, 'width': 440,
                                       'height': 63},
                              'focused': True, 'value': None,
                              'covered': False},
        }
        session = FakeDomSession(fields)
        points = dom_act.ground_many(session, G30_META,
                                     ['#clone1-input', '#clone2-input'])
        fields['#clone2-input']['rect'] = {'x': 86, 'y': 700, 'width': 440,
                                           'height': 63}
        current = session.locate('#clone2-input')
        point = points['#clone2-input']['point']
        self.assertTrue(
            fastpath.point_in_rect(current, point[0], point[1]),
            'stored clone2 point %s is outside the live rect %s'
            % (point, current))


class R5EnterOrderingTests(unittest.TestCase):
    def test_successful_send_must_not_fail_verification(self):
        # R5: type_check runs AFTER the whole batch including Enter.
        # A real send clears the input, so verify_typed reads '' and
        # fails a message that DID send. The amend's FakeAct never
        # models Enter clearing the field, so its enter=True happy
        # path test passes vacuously.
        field = dict(G30_FIELD, value=None, focused=True)
        session = FakeDomSession({'#msg-input': field})

        def _type(text):
            session.fields['#msg-input']['value'] = text

        def _enter():
            act.sent.append(session.fields['#msg-input']['value'])
            session.fields['#msg-input']['value'] = ''

        act = ScriptedAct(on_type=_type, on_enter=_enter)
        result = dom_act.focus_type(session, act, G30_META, '#msg-input',
                                    'hello', enter=True)
        self.assertEqual(act.sent, ['hello'], 'the message did send')
        self.assertTrue(result['ok'],
                        'sent message failed verification: %s' % (result,))

    def test_retry_after_partial_send_must_not_double_send(self):
        # R6: no exactly-once mechanism anywhere in dom_act: no sent
        # bubble pre-check (V12), no dedup token, no before-send state
        # read. Retry the same focus_type after the first send and the
        # message goes out twice.
        field = dict(G30_FIELD, value=None, focused=True)
        session = FakeDomSession({'#msg-input': field})

        def _type(text):
            session.fields['#msg-input']['value'] = text

        def _enter():
            act.sent.append(session.fields['#msg-input']['value'])
            session.fields['#msg-input']['value'] = ''

        act = ScriptedAct(on_type=_type, on_enter=_enter)
        dom_act.focus_type(session, act, G30_META, '#msg-input', 'hello',
                           enter=True)
        dom_act.focus_type(session, act, G30_META, '#msg-input', 'hello',
                           enter=True)
        self.assertEqual(act.sent, ['hello'],
                         'retry sent the message twice: %s' % (act.sent,))


class R6HitCheckTests(unittest.TestCase):
    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_hit_check_passes_interactive_child_at_center(self):
        # R8: hit_check returns True for ANY descendant
        # (e.contains(hit)), including an interactive child button
        # sitting at the rect center. The click then activates the
        # child (clear-text / emoji / send affordance inside the
        # composer) instead of focusing the field. Executed against
        # the REAL hit_check JS extracted from zen_dom.py.
        script = _capture_js('hit_check')
        shim = ("var __child = {tagName: 'BUTTON'};\n"
                "var __target = {tagName: 'DIV', isContentEditable: true,"
                " readOnly: false,\n"
                " getBoundingClientRect: function(){ return {left: 0,"
                " top: 0, width: 100, height: 40}; },\n"
                " contains: function(h){ return h === __child; }};\n"
                "var document = {querySelector: function(){ return"
                " __target; },\n"
                " elementFromPoint: function(){ return __child; }};\n")
        out = _run_node(shim + 'console.log(JSON.stringify(' + script
                        + '));')
        self.assertEqual(json.loads(out), False,
                         'hit_check passed with a BUTTON at the center')


class R7ShadowTests(unittest.TestCase):
    def test_focus_check_walks_shadow_roots(self):
        # R9: V3 requires walking shadowRoot.activeElement down; the
        # amend's focus_check is strict document.activeElement===e.
        # An input inside a shadow root can never pass: activeElement
        # is the host, not the inner input. Source check first.
        src = open(ROOT / 'scripts' / 'zen_dom.py').read()
        self.assertIn('shadowRoot', src)

    @unittest.skipUnless(NODE, 'node is required to run production JS')
    def test_focus_check_shadow_host_false_negative(self):
        # R9, executed: the inner input IS focused (inside its shadow
        # root) but document.activeElement is the host, so the real
        # focus_check JS returns False and the batch refuses to type
        # into a focused field.
        script = _capture_js('focus_check')
        # Shim fix (AMEND2): the host MUST carry shadowRoot with the
        # inner input as its activeElement, or the fixture does not
        # model what its own docstring describes (an input focused
        # inside its shadow root). The old strict-equality code still
        # fails this corrected fixture; only a real shadow walk
        # passes it.
        shim = ("var __inner = {tagName: 'INPUT', isContentEditable:"
                " false, readOnly: false};\n"
                "var __host = {tagName: 'DIV', shadowRoot:"
                " {activeElement: __inner}};\n"
                "var document = {querySelector: function(){ return"
                " __inner; }, activeElement: __host};\n")
        out = _run_node(shim + 'console.log(JSON.stringify(' + script
                        + '));')
        self.assertEqual(json.loads(out), True,
                         'focus_check failed a focused shadow input')

    def test_locate_pierces_shadow_roots_or_frames(self):
        # R9: locate uses document.querySelector only: no shadow
        # piercing, no frame traversal, so any input inside a shadow
        # root or an iframe (same-origin or cross-origin) is
        # unfindable, and the combined design's "every input" harvest
        # silently drops it.
        src = open(ROOT / 'scripts' / 'zen_dom.py').read()
        locate = src[src.index('def locate('):src.index('def verify(')]
        self.assertTrue('shadowRoot' in locate or 'contentWindow' in locate
                        or 'frames' in locate,
                        'locate() has no shadow-root or frame traversal')


class R11CdpTests(unittest.TestCase):
    def test_default_cdp_endpoint_is_not_zen_bidi_port(self):
        # R11: cu.BROWSER_ENDPOINT defaults to 127.0.0.1:9222, which is
        # Zen's remote-debugging port serving BiDi only since Firefox
        # 141 (/json returns 404, clone2 proved). cdp.mjs fetches
        # /json/list from the endpoint, so any CDP browser call with
        # the default endpoint fails against the live Zen; and
        # browser_start probes /json/version there, reads the 404 as
        # "no live endpoint", and cold-launches Chromium onto the
        # port Zen already holds.
        self.assertNotEqual(cu.BROWSER_ENDPOINT, 'http://127.0.0.1:9222')

    def test_cdp_set_value_prefill_early_return(self):
        # R11: cdp.mjs set_value returns {ok:true} when the field
        # already holds the text, without setting anything. The
        # Chromium path the combined design relies on has the same
        # prefill false-ok as the Zen path (R2), plus its "verification"
        # is a JS setter followed by synthetic input/change events the
        # action itself dispatches.
        text = (ROOT / 'scripts' / 'cdp.mjs').read_text()
        self.assertNotIn('if(e.value===', text)


class R12SessionTests(unittest.TestCase):
    def test_bidi_client_takes_the_single_session_lock(self):
        # R12: ZenSession enforces the one-session rule with a file
        # lock, but zen_cli.py (BiDi, the repo's tab tool) takes no
        # ZEN_DOM_LOCK. A benchmark flow that switches tabs with
        # zen_cli while a ZenSession holds the Marionette session hits
        # Firefox's "Maximum number of active sessions" cap (clone2
        # measured, all runs). The combined design never names which
        # tool switches tabs, so the wedge is one natural choice away.
        text = (ROOT / 'scripts' / 'zen_cli.py').read_text()
        self.assertTrue('ZEN_DOM_LOCK' in text or 'flock' in text,
                        'zen_cli opens BiDi sessions without the lock')


if __name__ == '__main__':
    unittest.main(verbosity=2)
