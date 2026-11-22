"""Element refs bound to a snapshot + observation ID (P2, step 7).

Implements the stale-ref disagreement protocol
(docs/stale-ref-disagreement-protocol.md): a ref is bound to a
snapshot ID and a scope, the section 2 checks run immediately
before acting, and the section 3 disposition decides whether a
disagreement re-grounds once, refuses, stops, or re-plans. The
strict path (section 4) stops on ANY disagreement for actions
that can send a message, submit a form, delete data, or move
money; re-ground-and-act never runs inside the old batch there.

Defaults from the protocol's open items: tolerance 0.5 CSS px
(OPEN-1, STABLE_TOLERANCE_PX), snapshot max age 120 s, two
consecutive rect reads for stability (OPEN-2), distinguishing
state recorded per action type where the action has one
(OPEN-3). The step-9 prototype revises these from measured data.
"""

import logging

from dom_asserts import assert_for

logger = logging.getLogger('element_ref')

# Protocol OPEN-1 default: rect agreement within 0.5 CSS px.
RECT_TOLERANCE_PX = 0.5

# Protocol section 2, check 1: a snapshot older than this is expired.
SNAPSHOT_MAX_AGE_SECONDS = 120

# Protocol section 7 reason codes, exactly as specified.
STALE_REASON_CODES = (
    'snapshot_expired',
    'snapshot_unbound',
    'scope_changed',
    'scope_changed_unresolved',
    'element_missing',
    'element_ambiguous',
    'identity_unconfirmed',
    'rect_moved_unconfirmed',
    'unstable',
    'covered',
    'not_visible',
    'not_interactive',
    'navigation',
    'window_moved',
)

# Disposition verdicts (protocol section 3).
VERDICT_REGROUND_AND_ACT = 'reground_and_act'
VERDICT_REFUSE = 'refuse'
VERDICT_STOP = 'stop'
VERDICT_REPLAN = 'replan'


class ElementRefError(ValueError):
    """A ref or action fails plan validation (missing binding)."""


class StaleRefError(ElementRefError):
    """A stale-ref disagreement, carrying the protocol section 7
    error shape. The message starts 'stale_ref: <reason code>' so
    both the first_action envelope and the code-exec prefix are
    derivable from it."""
    def __init__(self, error):
        self.error = error
        super().__init__('stale_ref: %s' % error['error']['reason'])


def make_ref(*, selector=None, ref=None, role=None, name=None,
             snapshot_id=None, scope=None, plan_rect=None,
             distinguishing_state=None):
    """Build one bound ref. The binding (snapshot ID, scope) is
    mandatory: a ref without it cannot be checked, so it is
    refused at construction, naming the missing field."""
    if snapshot_id is None or snapshot_id == '':
        raise ElementRefError(
            'ref is missing snapshot_id: a ref must be bound to a '
            'snapshot ID (protocol section 1)')
    if scope is None or scope == '':
        raise ElementRefError(
            'ref is missing scope: a ref must be bound to a scope '
            '(protocol section 1)')
    if selector is None and ref is None and role is None:
        raise ElementRefError(
            'ref needs a selector, ref, or role to resolve with')
    return {
        'selector': selector,
        'ref': ref,
        'role': role,
        'name': name,
        'snapshot_id': snapshot_id,
        'scope': scope,
        'plan_rect': plan_rect,
        'distinguishing_state': distinguishing_state,
    }


def validate_ref(ref, index=0):
    """Validate one ref dict, naming the missing field. Returns the
    ref unchanged when it is bound."""
    if not isinstance(ref, dict):
        raise ElementRefError(
            'ref %d is not a dict: %r' % (index, ref))
    if not ref.get('snapshot_id'):
        raise ElementRefError(
            'ref %d is missing snapshot_id' % index)
    if not ref.get('scope'):
        raise ElementRefError('ref %d is missing scope' % index)
    if (ref.get('selector') is None and ref.get('ref') is None
            and ref.get('role') is None):
        raise ElementRefError(
            'ref %d needs a selector, ref, or role to resolve with'
            % index)
    return ref


def validate_action(action, index=0):
    """CB-2: scope + observation ID are mandatory in action data.
    Refused at plan validation, naming the missing field."""
    if not isinstance(action, dict):
        raise ElementRefError(
            'action %d is not a dict: %r' % (index, action))
    if not action.get('scope'):
        raise ElementRefError(
            'action %d is missing scope: scope is mandatory in '
            'action data (CB-2)' % index)
    if not action.get('observation_id'):
        raise ElementRefError(
            'action %d is missing observation_id: observation_id is '
            'mandatory in action data (CB-2)' % index)
    return action


def validate_plan(actions):
    """Validate every action in a plan, naming the first bad action
    index. A plan that is not a list is refused outright."""
    if not isinstance(actions, list):
        raise ElementRefError(
            'actions must be a list of actions: %r' % (actions,))
    for index, action in enumerate(actions):
        validate_action(action, index=index)
    return actions


def validate_action_binding(action, *, snapshot_id, scope, index=0):
    """Check one action against the bound snapshot. A mismatched
    observation ID is snapshot_unbound; a mismatched scope is
    scope_changed. Both are StaleRefError, not plain validation
    errors, so callers map them to the section 7 shape."""
    validate_action(action, index=index)
    if action.get('observation_id') != snapshot_id:
        raise StaleRefError(stale_ref_error(
            reason='snapshot_unbound',
            selector=action.get('ref') or action.get('selector'),
            snapshot_id=snapshot_id, scope=scope,
            plan_rect=None, live_rect=None, action_index=index))
    if action.get('scope') != scope:
        raise StaleRefError(stale_ref_error(
            reason='scope_changed',
            selector=action.get('ref') or action.get('selector'),
            snapshot_id=snapshot_id, scope=scope,
            plan_rect=None, live_rect=None, action_index=index))
    return action


def is_send_action(action, actions=None):
    """True when the action is a send: a key Enter after a type in
    the same batch (dom_asserts sent-bubble rule). A lone Enter is
    not a send."""
    spec = assert_for(action, actions)
    return bool(spec) and spec.get('assert') == 'sent_bubble' \
        and spec.get('when') == 'send'


def is_strict_action(action, actions=None):
    """Protocol section 4 strict path: any action that can send a
    message, submit a form, delete data, or move money. A send key
    is strict; a caller marks the other kinds with
    destructive=True on the action."""
    return is_send_action(action, actions) \
        or action.get('destructive') is True


def rects_agree(plan, live, tolerance=RECT_TOLERANCE_PX):
    """Rect agreement within tolerance, per component (protocol
    section 2, check 6). A missing live rect never agrees."""
    if not isinstance(plan, dict) or not isinstance(live, dict):
        return False
    for key in ('x', 'y', 'width', 'height'):
        if key not in plan or key not in live:
            return False
        if abs(plan[key] - live[key]) > tolerance:
            return False
    return True


def check_binding(*, snapshot_id, scope, age_seconds,
                  expected_snapshot_id, expected_scope):
    """Protocol section 2, checks 1-2, in order: binding first,
    then scope. Returns None when both pass, else the reason code.
    A future clock (negative age) is expired, as is any age over
    120 s. An unbound or mismatched snapshot ID is unbound."""
    if snapshot_id is None or snapshot_id == '' \
            or snapshot_id != expected_snapshot_id:
        return 'snapshot_unbound'
    if age_seconds is None or age_seconds < 0 \
            or age_seconds > SNAPSHOT_MAX_AGE_SECONDS:
        return 'snapshot_expired'
    if scope != expected_scope:
        return 'scope_changed'
    return None


def check_distinguishing_state(plan_state, live_state):
    """Protocol section 2 identity, distinguishing-state half:
    True when no plan state was recorded (nothing to compare) or
    when the live state equals the recorded one."""
    if plan_state is None:
        return True
    return plan_state == live_state


def stale_ref_error(*, reason, selector, snapshot_id, scope,
                    plan_rect, live_rect, action_index):
    """The exact protocol section 7 fail-closed error shape.
    live_rect is None when the element is missing; plan_rect is
    None when no rect was recorded (such a ref cannot take the
    re-ground-and-continue row)."""
    return {
        'input_sent': False,
        'target_received': False,
        'verified': False,
        'verified_basis': 'stale-ref: %s' % reason,
        'ok': False,
        'error': {
            'code': 'stale_ref',
            'reason': reason,
            'selector': selector,
            'snapshot_id': snapshot_id,
            'scope': scope,
            'plan_rect': plan_rect,
            'live_rect': live_rect,
            'action_index': action_index,
            'batch_stopped': True,
        },
    }


def decide_disposition(*, reason, identity_confirmed=False,
                       strict=False, reground_ok=False):
    """Protocol section 3 disposition table, as {verdict, reason}.
    The strict path (section 4) overrides everything: any
    disagreement stops the batch, with the original reason kept.
    An unknown reason fails closed to stop."""
    if strict:
        return {'verdict': VERDICT_STOP, 'reason': reason}
    if reason == 'rect_moved':
        if identity_confirmed and reground_ok:
            return {'verdict': VERDICT_REGROUND_AND_ACT,
                    'reason': 'rect_moved'}
        if identity_confirmed:
            return {'verdict': VERDICT_REFUSE, 'reason': 'rect_moved'}
        return {'verdict': VERDICT_REFUSE,
                'reason': 'identity_unconfirmed'}
    if reason == 'element_missing':
        return {'verdict': VERDICT_REFUSE, 'reason': 'element_missing'}
    if reason == 'element_ambiguous':
        return {'verdict': VERDICT_STOP, 'reason': 'element_ambiguous'}
    if reason == 'scope_changed':
        if reground_ok:
            return {'verdict': VERDICT_REGROUND_AND_ACT,
                    'reason': 'scope_changed'}
        return {'verdict': VERDICT_STOP,
                'reason': 'scope_changed_unresolved'}
    if reason == 'navigation':
        return {'verdict': VERDICT_REPLAN, 'reason': 'navigation'}
    if reason in ('unstable', 'covered', 'not_visible',
                  'not_interactive'):
        return {'verdict': VERDICT_REFUSE, 'reason': reason}
    if reason in ('snapshot_expired', 'snapshot_unbound'):
        if reground_ok:
            return {'verdict': VERDICT_REGROUND_AND_ACT,
                    'reason': reason}
        return {'verdict': VERDICT_STOP, 'reason': reason}
    if reason == 'window_moved':
        if reground_ok:
            return {'verdict': VERDICT_REGROUND_AND_ACT,
                    'reason': 'window_moved'}
        return {'verdict': VERDICT_STOP, 'reason': 'window_moved'}
    logger.warning('unknown stale-ref reason %r, failing closed to '
                   'stop', reason)
    return {'verdict': VERDICT_STOP, 'reason': reason}
