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
"""
import fastpath


class DomActError(RuntimeError):
    pass


def ground_input(session, meta, selector):
    """Ground one input from the live DOM. Returns evidence, no click.

    session is a zen_dom.ZenSession (or a duck-typed fake with
    locate/viewport_origin/hit_check). meta is the observation the
    click will be written against. Raises DomActError when the
    element is missing, the point falls outside the observed image,
    or the rect center does not hit the element itself. No screenshot
    is read and no observe is taken.
    """
    rect = session.locate(selector)
    if rect is None:
        raise DomActError(f"no element matches {selector!r}")
    origin = session.viewport_origin()
    try:
        point = fastpath.dom_rect_to_image_point(meta, rect, origin)
    except ValueError as exc:
        raise DomActError(str(exc)) from exc
    if not session.hit_check(selector):
        raise DomActError(
            f"rect center of {selector!r} does not hit the element; "
            "it is covered or off-viewport, refusing the click")
    return {'selector': selector, 'rect': rect,
            'viewport_origin': origin, 'point': point, 'hit': True}


def ground_many(session, meta, selectors):
    """Ground many inputs from ONE observation meta.

    The 2-vision benchmark shape: VISION 1 determines the coordinates
    of ALL input bars and buttons, then the script runs with no more
    vision. Fails fast on the first ungroundable selector, before any
    click, so a half-grounded batch never starts.
    """
    points = {}
    for selector in selectors:
        points[selector] = ground_input(session, meta, selector)
    return points


def focus_type(session, act_fn, meta, selector, text, enter=False):
    """Click an input, type, and verify, from one observation.

    act_fn is a callable (meta, actions, focus_check, type_check)
    returning a result dict, normally a closure over cu.desktop_act.
    It runs ONE batch (click + type, plus Enter when asked) against
    the given meta. The focus_check closure runs inside the batch
    before the first type group: when the click missed, the batch
    stops before any keystroke. The type_check closure runs after
    the batch: it reads the field value, the sufficient check. The
    DOM flow itself adds zero observes; the act batch uses exactly
    the observes a plain batch uses.
    """
    ground = ground_input(session, meta, selector)
    calls = {'dom': 3}
    actions = [{'type': 'click', 'x': ground['point'][0],
                'y': ground['point'][1]},
               {'type': 'type', 'text': text}]
    if enter:
        actions.append({'type': 'key', 'keys': ['Enter']})

    def focus_check():
        calls['dom'] += 1
        ok = session.focus_check(selector)
        return (bool(ok),
                None if ok else 'activeElement is not the target input')

    def type_check():
        calls['dom'] += 1
        ok = session.verify_typed(selector, text)
        return (bool(ok),
                None if ok else 'field value does not hold the typed text')

    result = act_fn(meta, actions, focus_check=focus_check,
                    type_check=type_check)
    if not isinstance(result, dict):
        raise DomActError('act_fn must return a result dict')
    return {'ok': result.get('ok') is True,
            'completed': result.get('completed', 0),
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
            'act_observes': result.get('observes'),
            'error': result.get('error'),
            'error_code': result.get('error_code')}
