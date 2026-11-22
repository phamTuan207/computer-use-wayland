"""P5 DOM verification per action type for the S2 task class
(clone chat sends), FINAL direction section 1.2 P5, step 5.

The assert set is mandatory PER ACTION TYPE as its assert lands,
never as a blanket mandate: the table below names, for each action
in the S2 class, the DOM assert that must run, and the exception
list names the actions where no DOM assert is possible and pixel
stays the only signal. The pixel band stays as a diagnostic until
a DOM assert exists for that action; it is never a postcondition.

The S2 send chain (the pattern is the V12 sent-bubble gate in
tests/two_vision_bench.py, send_one):

- click (composer) -> focus_check, mandatory. After the click the
  target must be document.activeElement before any keystroke;
  the check runs inside the batch, before the first type group.
- type -> type_check, mandatory. After the type the field value
  read-back must equal the typed text, with the V11 trusted-input
  flag (dom_act.dom_hooks / zen_dom.verify_typed).
- key Enter after a type (the send) -> sent_bubble, mandatory
  postcondition. The thread DOM must hold a sent bubble with the
  exact message text (zen_dom.sent_bubble_contains); the Enter
  batch alone proves nothing.

The same table covers the code-exec (Chromium/CDP) vocabulary:
fill/set_value -> type_check, mandatory, enforced inside cdp.mjs
itself (set_value always performs the native-setter write plus
the read-back verification, cdp.mjs); a send program
(fill/set_value followed by key Enter) must end with an assert
action, the V12 gate in program form, enforced by
code_exec._api_dom_act. A bare `assert` action IS an assert, so
it is covered by construction.

CB-1 shares this exception list (action_result re-exports the
same object): one list, never two that can drift.
"""


class DomAssertError(RuntimeError):
    """A mandatory DOM assert is missing for an action in the batch."""


# action type -> assert spec. 'assert' is the name of the check;
# 'mandatory' is True for every covered action in the S2 class.
# 'when' narrows a conditional assert (key is a send only when it
# follows a type in the same chain).
ASSERTS = {
    'click': {'assert': 'focus_check', 'mandatory': True,
              'check': 'target is document.activeElement after the '
                       'click, before any keystroke'},
    'double_click': {'assert': 'focus_check', 'mandatory': True,
                     'check': 'target is document.activeElement after '
                              'the double click, before any keystroke'},
    'confirm_click': {'assert': 'focus_check', 'mandatory': True,
                      'check': 'target is document.activeElement after '
                               'the confirmed click, before any keystroke'},
    'hover_click': {'assert': 'focus_check', 'mandatory': True,
                    'check': 'target is document.activeElement after '
                             'the hover click, before any keystroke'},
    'type': {'assert': 'type_check', 'mandatory': True,
             'check': 'field value read-back equals the typed text, '
                      'with the V11 trusted-input flag'},
    'fill': {'assert': 'type_check', 'mandatory': True,
             'check': 'field value read-back equals the filled text '
                      '(enforced inside cdp.mjs set_value)'},
    'set_value': {'assert': 'type_check', 'mandatory': True,
                  'check': 'field value read-back equals the set text '
                           '(enforced inside cdp.mjs set_value)'},
    'focus': {'assert': 'focus_check', 'mandatory': True,
              'check': 'target is document.activeElement after the '
                       'focus, before any keystroke'},
    'key': {'assert': 'sent_bubble', 'mandatory': True,
            'when': 'send',
            'check': 'thread DOM holds a sent bubble with the exact '
                     'message text (V12 gate)'},
    'assert': {'assert': 'assert', 'mandatory': True,
               'check': 'the assert action itself, run as the program '
                        'postcondition'},
}

# Actions where a DOM assert is impossible: pixel stays the only
# signal, and the band stays as a diagnostic, never a pass signal.
# Shared with CB-1 (action_result re-exports this object).
DOM_ASSERT_EXCEPTIONS = {
    'scroll': 'scroll position has no DOM postcondition: the viewport '
              'offset is a position, not a confirmation the right '
              'content arrived; pixel is the only signal',
    'hover': 'hover state has no DOM postcondition: :hover is '
             'transient and unreadable as a post-state; pixel is the '
             'only signal',
    'move': 'pointer position only: cursorpos is the signal, not DOM',
    'drag': 'drag end state has no single DOM postcondition; pixel is '
            'the only signal',
    'wait': 'timing only: no postcondition exists',
    'key': 'a non-send key has no generic DOM postcondition: a '
           'shortcut may legitimately change nothing observable',
}

def _is_send_key(action, actions):
    """True when this key action sends a typed message.

    A send key is Enter (or Return) appearing after a type, fill,
    or set_value action in the same batch. A lone Enter with no
    preceding type is not a send: there is no message to gate.
    """
    if not isinstance(action, dict) or action.get('type') != 'key':
        return False
    keys = action.get('keys') or []
    if not any(isinstance(k, str) and k in ('Enter', 'Return', 'enter',
                                            'return') for k in keys):
        return False
    if not isinstance(actions, list):
        return False
    index = actions.index(action)
    return any(isinstance(a, dict)
               and a.get('type') in ('type', 'fill', 'set_value')
               for a in actions[:index])


def assert_for(action, actions=None):
    """The assert spec or exception entry for one action.

    Returns {'action': type, 'assert': name, 'mandatory': bool,
    'check': description} for a covered action, or {'action': type,
    'exception': reason} for an exception-list action, or None for
    an action type this table does not know (a caller must fail
    closed on None, never assume it is covered).
    """
    if not isinstance(action, dict):
        return None
    action_type = action.get('type')
    if action_type == 'key':
        if _is_send_key(action, actions or []):
            spec = ASSERTS['key']
            return {'action': 'key', 'assert': spec['assert'],
                    'mandatory': True, 'check': spec['check'],
                    'when': 'send'}
        return {'action': 'key',
                'exception': DOM_ASSERT_EXCEPTIONS['key']}
    spec = ASSERTS.get(action_type)
    if spec is not None:
        return {'action': action_type, 'assert': spec['assert'],
                'mandatory': bool(spec.get('mandatory')),
                'check': spec['check']}
    reason = DOM_ASSERT_EXCEPTIONS.get(action_type)
    if reason is not None:
        return {'action': action_type, 'exception': reason}
    return None


def assert_coverage(actions, context=None):
    """Coverage of the assert set over one action batch.

    Returns {'covered': [assert specs], 'exceptions': [{'action',
    'reason'}], 'required': [assert names], 'unknown': [action
    types with no defined assert]}. `required` is what the batch
    needs: every covered assert is mandatory for the S2 class, so
    a batch is covered when its caller can run every name in
    `required` (see require_asserts). Whether a requirement is
    met is a question of availability, not of this table, so this
    function never reports anything missing: a send key requires
    sent_bubble whether the gate lives in the caller (focus_type
    runs sent_bubble_contains) or in the program (a trailing
    assert action in a code-exec send program).
    """
    actions = actions or []
    covered = []
    exceptions = []
    required = []
    unknown = []
    for action in actions:
        entry = assert_for(action, actions)
        if entry is None:
            unknown.append(action.get('type')
                           if isinstance(action, dict) else None)
            continue
        if 'exception' in entry:
            exceptions.append({'action': entry['action'],
                               'reason': entry['exception']})
            continue
        covered.append(entry)
        if entry['assert'] not in required:
            required.append(entry['assert'])
    return {'covered': covered, 'exceptions': exceptions,
            'required': required, 'unknown': unknown}


def _is_focus_establishing(action):
    """True when this action puts focus on its target before a
    later keystroke: any action whose ASSERTS entry is
    focus_check (click, double_click, confirm_click, hover_click,
    focus), plus fill as an explicit exception (it focuses
    internally through its click, cdp.mjs, even though its ASSERTS
    entry is type_check). Defined through the ASSERTS table, not a
    hardcoded list, so a future focus_check action joins
    automatically. `type` is not focus-establishing: in dom_act
    focus_type the click establishes focus and type only types.
    """
    if not isinstance(action, dict):
        return False
    if action.get('type') == 'fill':
        return True
    spec = ASSERTS.get(action.get('type'))
    return bool(spec) and spec.get('assert') == 'focus_check'


def require_asserts(actions, available, context=None):
    """Fail closed when a mandatory assert is unavailable.

    actions is the batch; available maps assert name -> truthy
    when the caller can run that check (a focus_check closure, a
    type_check closure, a sent_bubble_contains method on the
    session). Raises DomAssertError naming every missing mandatory
    assert. Unknown action types also raise: an action with no
    defined assert must not run unverified. Exception-list actions
    never raise.
    """
    actions = actions or []
    available = available or {}
    # A trailing assert action in the program satisfies the
    # sent_bubble requirement for a send: the program asserts the
    # bubble itself (the code-exec V12 gate in program form).
    has_trailing_assert = any(
        isinstance(a, dict) and a.get('type') == 'assert'
        for a in actions)
    missing = []
    # Send-requires-focus (C5-B1 landing): a send key with no
    # preceding focus-establishing action in the same batch raises.
    # "Preceding" means before the send key; a focus after the
    # Enter does not satisfy it. This runs even when a trailing
    # assert satisfies sent_bubble: the assert proves the bubble
    # arrived, not that the Enter went to the right element.
    for index, action in enumerate(actions):
        entry = assert_for(action, actions)
        if entry is None or 'exception' in entry:
            continue
        if entry.get('assert') != 'sent_bubble':
            continue
        if not any(_is_focus_establishing(a) for a in actions[:index]):
            missing.append(
                'send key at index %d needs a preceding '
                'focus-establishing action (click, double_click, '
                'confirm_click, hover_click, focus, or fill) before '
                'the Enter; an unfocused Enter goes to BODY and '
                'fails silently' % index)
    for action in actions:
        entry = assert_for(action, actions)
        if entry is None:
            missing.append('unknown action %r: no assert defined'
                           % (action.get('type')
                              if isinstance(action, dict) else action,))
            continue
        if 'exception' in entry:
            continue
        name = entry['assert']
        if name == 'sent_bubble' and has_trailing_assert:
            continue
        if name == 'assert':
            continue
        if not available.get(name):
            missing.append(
                '%s needs mandatory assert %s (%s)'
                % (entry['action'], name, entry['check']))
    if missing:
        raise DomAssertError(
            'mandatory DOM assert missing for the S2 task class: '
            + '; '.join(missing))
    return True
