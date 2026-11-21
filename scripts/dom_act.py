"""DOM-first focus+type flow: one observation grounds the whole batch.

The G30 root cause is a vision-grounding error: Muse read the input
bar 64px too high from a JPEG and clicked dead space five times, while
Codex re-grounded from the DOM rect center and typed at once. This
module is the code form of that lesson. For a browser target, never
read a screenshot to locate a field: the DOM rect is ground truth
(getBoundingClientRect, sub-pixel CSS px), the viewport origin turns
it into a screen point, and fastpath.dom_rect_to_image_point turns
that into the observation image point. Verify with cheap JS evals,
never a fresh observe: hit_check (elementFromPoint) before the click,
focus_check (document.activeElement) before the type, verify_typed
(field value) after it. The desktop act batch itself (click + type +
Enter) runs against the ONE given observation, so one vision drives
the whole sequence; the DOM calls add zero observes.

Two browser paths exist in this repo. This module is the
Marionette/Zen path (zen_dom.ZenSession plus cu.desktop_act). The
Chromium path is scripts/cdp.mjs, whose fill action already does the
same shape (rect center click, activeElement check, value verify)
with no observation at all; the 2-vision benchmark worker picks the
path per browser. The a11y path (scripts/a11y.py ground) is the third
option for non-browser targets. All three share the rule: ground from
the tree, verify from state, never re-read a screenshot to locate
something the tree already names.

A click point is never inherited from a previous worker without
re-grounding: ground_input re-reads the rect from the live DOM every
time, and hit_check refuses a covered element before any click.

Conversion (live C12 probe 2026-11-22 03:36): mozInnerScreenX/Y are
WINDOW-relative in this Zen build, so the absolute viewport origin is
the Hyprland window origin + mozInnerScreenX/Y, times the
CSS-to-screen factor (zen_dom.viewport_origin computes and verifies
it). The window origin comes from the observation meta's
window_bounds, else its region. AT-SPI cannot see Zen, so the
geometry check that replaces it is the monitor-bounds +
dimension-closure check in zen_dom.check_viewport_geometry.

"VISION 1" in the combined design is a DOM harvest, not a screenshot:
one-shot bulk grounding (harvest) reads every input + button from one
evaluate, and the script then runs with no more vision until VISION 2
(the outcome screenshot). Nothing in this module takes a screenshot
to locate a field.
"""
import fastpath


class DomActError(RuntimeError):
    pass


def _window_origin(meta):
    """[x, y] Hyprland window origin from an observation meta."""
    if not isinstance(meta, dict):
        raise DomActError('meta must be an object')
    bounds = meta.get('window_bounds')
    if (isinstance(bounds, (list, tuple)) and len(bounds) == 4):
        return [bounds[0], bounds[1]]
    region = meta.get('region')
    if (isinstance(region, (list, tuple)) and len(region) == 4):
        return [region[0], region[1]]
    raise DomActError('meta needs window_bounds or region for the '
                      'window origin (mozInnerScreen is window-relative)')


def _scale_factor(session):
    """CSS-to-screen factor recorded with the origin read (1 default)."""
    factor = getattr(session, 'last_scale_factor', 1)
    if (isinstance(factor, bool) or not isinstance(factor, (int, float))
            or factor <= 0):
        return 1
    return factor


def _sent_intents(session):
    """Exactly-once intent ledger, stored on the session object.

    One set per session: a fresh session starts empty, so two tests
    (or two tabs) never share intents, while a retry of the same send
    on the same session sees the recorded intent and does not
    double-send. Sessions that cannot carry attributes fall back to a
    module-level dict keyed by id(session); the ids are only ever read
    while the session is alive.
    """
    ledger = getattr(session, 'sent_intents', None)
    if isinstance(ledger, set):
        return ledger
    try:
        session.sent_intents = set()
        return session.sent_intents
    except Exception:
        return _FALLBACK_LEDGERS.setdefault(id(session), set())


_FALLBACK_LEDGERS = {}


def _verify(session, selector, text, before):
    """verify_typed with the before-value rule, tolerating old fakes.

    Sessions whose verify_typed takes (selector, expected, before)
    enforce the prefill rule (a field that already held the text fails
    unless a real typed event was recorded). Older two-argument
    sessions get the plain equality call.
    """
    try:
        return session.verify_typed(selector, text, before)
    except TypeError:
        return session.verify_typed(selector, text)


def ground_input(session, meta, selector):
    """Ground one input from the live DOM. Returns evidence, no click.

    session is a zen_dom.ZenSession (or a duck-typed fake with
    locate/viewport_origin/hit_check). meta is the observation the
    click will be written against. Raises DomActError when the
    element is missing, the point falls outside the observed image,
    or the rect center does not hit the element itself. No screenshot
    is read and no observe is taken.

    HCU live guard (R7): the hit verdict and the clicked point come
    from different snapshots (locate, then origin, then hit_check, and
    hit_check re-reads its own rect), so the rect is re-read after
    the hit check and the point must still land inside the fresh
    rect. When the element moved between the reads, the point is
    re-grounded once from the fresh rect and re-checked; when it
    moved again, grounding refuses instead of clicking a stale point.
    """
    rect = session.locate(selector)
    if rect is None:
        raise DomActError(f"no element matches {selector!r}")
    window_origin = _window_origin(meta)
    window_size = None
    bounds = meta.get('window_bounds')
    if isinstance(bounds, (list, tuple)) and len(bounds) == 4:
        window_size = [bounds[2], bounds[3]]
    monitor_box = meta.get('monitor_box')
    try:
        origin = session.viewport_origin(window_origin, window_size,
                                         monitor_box)
    except TypeError:
        origin = session.viewport_origin()
    factor = _scale_factor(session)
    try:
        point = fastpath.dom_rect_to_image_point(meta, rect, origin,
                                                 factor)
    except ValueError as exc:
        raise DomActError(str(exc)) from exc
    if not session.hit_check(selector):
        raise DomActError(
            f"rect center of {selector!r} does not hit the element; "
            "it is covered or off-viewport, refusing the click")
    fresh = session.locate(selector)
    if fresh is not None and fresh != rect:
        rect = fresh
        try:
            point = fastpath.dom_rect_to_image_point(meta, rect, origin,
                                                     factor)
        except ValueError as exc:
            raise DomActError(str(exc)) from exc
        if not session.hit_check(selector):
            raise DomActError(
                f"rect center of {selector!r} does not hit the element "
                "after re-grounding; refusing the click")
        again = session.locate(selector)
        if again is not None and again != rect:
            raise DomActError(
                f"element {selector!r} moved again during grounding; "
                "the point is stale, refusing")
    metrics = getattr(session, 'last_display_metrics', None)
    evidence = {'selector': selector, 'rect': rect,
                'viewport_origin': origin, 'point': point, 'hit': True,
                'scale_factor': factor}
    if isinstance(metrics, dict):
        evidence['device_pixel_ratio'] = metrics.get('device_pixel_ratio')
        evidence['screen_pixels_per_css_pixel'] = \
            metrics.get('screen_pixels_per_css_pixel')
        evidence['zoom'] = metrics.get('zoom')
        evidence['moz_inner'] = metrics.get('moz_inner')
    return evidence


def grounded_x_range(ground, meta):
    """Image-px x-range of the grounded field, for the band check.

    ground is ground_input evidence (rect in viewport CSS px, point
    in image px, scale_factor); meta carries image_size and region.
    The rect's image width is its CSS width times the CSS-to-screen
    factor times image px per screen px; the range is centered on
    the image point (the rect center). Returns [x0, x1] floats, or
    None when the meta cannot map the rect (the caller then keeps
    the full-width band).
    """
    try:
        rect = ground['rect']
        point = ground['point']
        factor = ground.get('scale_factor', 1)
        size = meta.get('image_size')
        region = meta.get('region')
        half = rect['width'] * factor * size[0] / region[2] / 2
        return [point[0] - half, point[0] + half]
    except Exception:
        return None


class GroundPoints(dict):
    """Grounding evidence that re-validates on every read (R7).

    ground_many returns this mapping, not a plain dict: each [] access
    re-reads the live rect and, when the element moved since grounding
    (a send shifted the layout), re-grounds that selector before
    returning it. A point from before the previous send is therefore
    never clicked without a fresh check; the HCU live guard is this
    mapping, not design text. .get() and other dict methods bypass
    the guard (they read the stored table directly), so callers must
    use [] access for the point they click. A re-ground that fails
    raises DomActError instead of returning a stale point.
    """

    def __init__(self, session, meta, points):
        super().__init__(points)
        self._session = session
        self._meta = meta

    def __getitem__(self, selector):
        stored = super().__getitem__(selector)
        fresh = self._session.locate(selector)
        if fresh is None:
            raise DomActError(f"no element matches {selector!r} anymore; "
                              "the grounded point is stale, refusing")
        if fresh != stored['rect']:
            refreshed = ground_input(self._session, self._meta, selector)
            super().__setitem__(selector, refreshed)
            return refreshed
        return stored


def ground_many_one_shot(session, meta, selectors):
    """Ground many inputs from ONE evaluate (doma11y C1, VISION 1).

    The session must expose harvest(selectors) (zen_dom.ZenSession
    does): one evaluate returns every rect plus the viewport origin
    inputs and display metrics. Returns a GroundPoints mapping (live
    re-validation on read, see the class). Raises DomActError when
    any selector is missing, uncovered, or maps outside the image.
    Fails fast, before any click, so a half-grounded batch never
    starts. One evaluate for the whole inventory, zero observes.
    """
    if not hasattr(session, 'harvest'):
        raise DomActError('session has no harvest(); the one-shot bulk '
                          'grounding needs a session that returns all '
                          'rects in one evaluate')
    window_origin = _window_origin(meta)
    window_size = None
    bounds = meta.get('window_bounds')
    if isinstance(bounds, (list, tuple)) and len(bounds) == 4:
        window_size = [bounds[2], bounds[3]]
    monitor_box = meta.get('monitor_box')
    raw = session.harvest(list(selectors))
    items = raw.get('items') if isinstance(raw, dict) else None
    if not isinstance(items, dict):
        raise DomActError('harvest did not return items')
    moz_inner = raw.get('moz_inner')
    factor = raw.get('screen_pixels_per_css_pixel')
    if not isinstance(factor, (int, float)) or isinstance(factor, bool) \
            or factor <= 0:
        factor = raw.get('device_pixel_ratio', 1)
    if (not isinstance(moz_inner, (list, tuple)) or len(moz_inner) != 2
            or any(isinstance(v, bool)
                   or not isinstance(v, (int, float)) for v in moz_inner)):
        raise DomActError('harvest did not return a mozInner pair')
    try:
        from zen_dom import check_viewport_geometry
        outer = raw.get('outer_size') or [0, 0]
        inner = raw.get('inner_size') or [0, 0]
        # Same unit rule as viewport_origin (amend3 step 5): the
        # check takes the window size in CSS px. window_size from the
        # meta is Hyprland screen px, so divide by the factor; outer
        # is already CSS px and is used as-is when no window size
        # was given.
        size_for_check = (
            [window_size[0] / factor, window_size[1] / factor]
            if window_size is not None else outer)
        absolute = check_viewport_geometry(
            moz_inner,
            [window_origin[0] + moz_inner[0] * factor,
             window_origin[1] + moz_inner[1] * factor],
            window_origin,
            size_for_check,
            inner,
            monitor_box)
    except ImportError:
        absolute = [window_origin[0] + moz_inner[0] * factor,
                    window_origin[1] + moz_inner[1] * factor]
    points = {}
    for selector in selectors:
        item = items.get(selector)
        if item is None:
            raise DomActError(f"no element matches {selector!r}")
        raw_rect = item.get('rect') if isinstance(item, dict) else None
        if raw_rect is None:
            raise DomActError(f"harvest has no rect for {selector!r}")
        # Normalize to the four keys locate() returns, so the live
        # guard's rect equality holds when the element did not move
        # (the harvest rect carries center_x/center_y as well).
        rect = {'x': raw_rect.get('x'), 'y': raw_rect.get('y'),
                'width': raw_rect.get('width'),
                'height': raw_rect.get('height')}
        try:
            point = fastpath.dom_rect_to_image_point(meta, rect, absolute,
                                                     factor)
        except ValueError as exc:
            raise DomActError(str(exc)) from exc
        if not item.get('hit'):
            raise DomActError(
                f"rect center of {selector!r} does not hit the element; "
                "it is covered or off-viewport, refusing the click")
        points[selector] = {
            'selector': selector, 'rect': rect,
            'viewport_origin': absolute, 'point': point, 'hit': True,
            'scale_factor': factor,
            'device_pixel_ratio': raw.get('device_pixel_ratio'),
            'screen_pixels_per_css_pixel':
                raw.get('screen_pixels_per_css_pixel'),
            'zoom': raw.get('zoom'),
            'moz_inner': list(moz_inner)}
    return GroundPoints(session, meta, points)


def ground_many(session, meta, selectors):
    """Ground many inputs from ONE observation meta.

    The 2-vision benchmark shape: VISION 1 grounds BOTH clone
    input bars; the script then runs with no more vision. Uses the
    one-shot harvest when the session has it (one evaluate for the
    whole inventory), else per-element ground_input (3 evals each).
    Returns a GroundPoints mapping that re-validates on every read.
    Fails fast on the first ungroundable selector, before any click,
    so a half-grounded batch never starts.
    """
    if hasattr(session, 'harvest'):
        return ground_many_one_shot(session, meta, selectors)
    points = {}
    for selector in selectors:
        points[selector] = ground_input(session, meta, selector)
    return GroundPoints(session, meta, points)


def typed_text_of(actions):
    """First type action's text, or None when the batch types nothing."""
    for action in actions or []:
        if (isinstance(action, dict) and action.get('type') == 'type'
                and isinstance(action.get('text'), str)):
            return action['text']
    return None


def open_dom_hooks(selector, text):
    """Open one ZenSession and build (session, focus_check, type_check).

    The production wiring helper (item A): a caller that owns a batch
    (cu CLI act, first_action fallback, CodeExecBackend.act) opens the
    hooks here, passes the closures to desktop_act, and closes the
    session after the batch. The session MUST stay open while the
    batch runs: the closures read document.activeElement / field value
    through it. Raises DomActError when the session cannot open or
    the selector cannot be grounded; the caller then falls back to
    the pixel band instead of failing the batch. The session is
    closed again on any failure inside this helper, so a failed open
    never leaks the single-session slot.
    """
    import zen_dom
    session = zen_dom.ZenSession()
    try:
        session.__enter__()
    except Exception as exc:
        raise DomActError('could not open a DOM session for %r: %s'
                          % (selector, exc)) from exc
    try:
        focus_check, type_check = dom_hooks(session, selector, text)
    except Exception:
        try:
            session.__exit__()
        except Exception:
            pass
        raise
    return session, focus_check, type_check


def dom_hooks(session, selector, text):
    """(focus_check, type_check) closures for a production desktop_act.

    The wiring point for item A: a production caller that owns a DOM
    session (first_action fallback, cu CLI act, BrowserAdapter.act)
    builds these closures and passes them to desktop_act, so the
    sufficient DOM value check runs on the live path instead of living
    only in this module's tests. The before-value is captured here
    and the V11 typed-event flag is armed here, both before any
    keystroke; the type_check then enforces the prefill rule (a field
    that already held the text fails unless a real typed event was
    recorded). The session stays owned by the caller (one-session
    rule); this helper never opens or closes it, and never observes.
    Returns (focus_check, type_check); each takes no arguments and
    returns (ok, reason).
    """
    before = session.field_value(selector)
    if hasattr(session, 'arm_typed_flag'):
        session.arm_typed_flag(selector)

    def focus_check():
        ok = session.focus_check(selector)
        return (bool(ok),
                None if ok else 'activeElement is not the target input')

    def type_check():
        ok = _verify(session, selector, text, before)
        return (bool(ok),
                None if ok else 'field value does not hold the typed text')

    return focus_check, type_check


def focus_type(session, act_fn, meta, selector, text, enter=False):
    """Click an input, type, and verify, from one observation.

    act_fn is a callable (meta, actions, focus_check, type_check,
    type_x_ranges) returning a result dict, normally a closure over
    cu.desktop_act; it must forward type_x_ranges to desktop_act
    (the grounded field's x-range, so the band reads only that
    field). It runs the batch against the given meta. The focus_check
    closure runs inside the batch before the first type group: when
    the click missed, the batch stops before any keystroke. The
    type_check closure runs after the type step, BEFORE Enter when a
    send is asked: the field still holds the text then, so a
    successful send is not failed by its own Enter clearing the field
    (RT R5). Enter runs as its own batch afterwards, and the send is
    then verified by the V12 sent-bubble check
    (sent_bubble_contains on the thread DOM) when the session exposes
    it; when it does not, the Enter batch result is accepted and the
    basis says so. The DOM flow itself adds zero observes; the act
    batches use exactly the observes a plain batch uses.

    Exactly-once (RT R6): an intent ledger on the session records
    (selector, text) once a send succeeds, and a pre-send V12 read
    checks the thread DOM for the exact bubble first. A retry after a
    lost result, or after a failed V12 gate, returns the recorded
    success instead of sending the message a second time. The ledger
    is per session object; a fresh session starts empty.
    """
    ground = ground_input(session, meta, selector)
    calls = {'dom': 4}
    intents = _sent_intents(session)
    if (selector, text) in intents:
        return {'ok': True, 'completed': 0, 'selector': selector,
                'rect': ground['rect'],
                'viewport_origin': ground['viewport_origin'],
                'point': ground['point'], 'hit': True,
                'focus_verified': None, 'type_verified': None,
                'type_verified_basis': 'already-sent',
                'dom_calls': calls['dom'], 'observes_added': 0,
                'act_observes': 0, 'error': None, 'error_code': None,
                'already_sent': True, 'sent_verified': True}
    if hasattr(session, 'sent_bubble_contains'):
        calls['dom'] += 1
        if session.sent_bubble_contains(text):
            intents.add((selector, text))
            return {'ok': True, 'completed': 0, 'selector': selector,
                    'rect': ground['rect'],
                    'viewport_origin': ground['viewport_origin'],
                    'point': ground['point'], 'hit': True,
                    'focus_verified': None, 'type_verified': None,
                    'type_verified_basis': 'already-sent',
                    'dom_calls': calls['dom'], 'observes_added': 0,
                    'act_observes': 0, 'error': None, 'error_code': None,
                    'already_sent': True, 'sent_verified': True}
    focus_check, type_check = dom_hooks(session, selector, text)
    calls['dom'] += 2
    # R3a: the band reads only the grounded field's x-range, so text
    # in another field on the same line cannot verify this type. The
    # range rides to desktop_act through the act_fn kwargs; an act_fn
    # that wraps desktop_act must forward it (the test fakes accept
    # and ignore it).
    x_range = grounded_x_range(ground, meta)
    type_ranges = [x_range] if x_range is not None else None
    actions = [{'type': 'click', 'x': ground['point'][0],
                'y': ground['point'][1]},
               {'type': 'type', 'text': text}]

    def _counted_focus_check():
        calls['dom'] += 1
        return focus_check()

    def _counted_type_check():
        calls['dom'] += 1
        return type_check()

    result = act_fn(meta, actions, focus_check=_counted_focus_check,
                    type_check=_counted_type_check,
                    type_x_ranges=type_ranges)
    if not isinstance(result, dict):
        raise DomActError('act_fn must return a result dict')
    completed = result.get('completed', 0)
    observes = result.get('observes')
    out = {'ok': result.get('ok') is True,
           'completed': completed,
           'selector': selector,
           'rect': ground['rect'],
           'viewport_origin': ground['viewport_origin'],
           'point': ground['point'],
           'hit': True,
           'focus_verified': result.get('focus_verified'),
           'type_verified': result.get('type_verified'),
           'type_verified_basis': result.get('type_verified_basis'),
           'dom_calls': calls['dom'],
           'observes_added': 0,
           'act_observes': observes,
           'error': result.get('error'),
           'error_code': result.get('error_code'),
           'already_sent': False,
           'sent_verified': None,
           'scale_factor': ground.get('scale_factor')}
    if not out['ok'] or not enter:
        return out
    sent = act_fn(meta, [{'type': 'key', 'keys': ['Enter']}])
    if not isinstance(sent, dict):
        raise DomActError('act_fn must return a result dict')
    out['completed'] = completed + sent.get('completed', 0)
    if sent.get('observes') is not None:
        out['act_observes'] = observes
    if sent.get('ok') is not True:
        out['ok'] = False
        out['error'] = sent.get('error')
        out['error_code'] = sent.get('error_code')
        return out
    if hasattr(session, 'sent_bubble_contains'):
        calls['dom'] += 1
        out['dom_calls'] = calls['dom']
        if session.sent_bubble_contains(text):
            intents.add((selector, text))
            out['sent_verified'] = True
            return out
        out['ok'] = False
        out['sent_verified'] = False
        out['error'] = ('send not verified: no sent bubble holds the '
                        'typed text in the thread DOM; the message may '
                        'not have sent, retry checks the bubble first')
        out['error_code'] = 'send_unverified'
        return out
    intents.add((selector, text))
    out['sent_verified'] = None
    out['type_verified_basis'] = (
        (out.get('type_verified_basis') or 'dom-value')
        + '+enter-accepted')
    return out
