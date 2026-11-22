"""CB-1 three-part result contract (FINAL direction section 1.4 CB-1,
folded into P5/A8; step 5).

Every action result carries three parts, not one ok:

- input_sent: the input was delivered without an execution error.
  This is what the old bare `ok` meant (G30: a click into empty
  space reported ok because the pointer moved without error).
- target_received: the right target received the input (the composer
  field holds the typed text, the clicked element took focus).
  None when no target state was read for this batch.
- verified: the postcondition passed. True ONLY when a postcondition
  check ran and passed (a DOM value read, a sent-bubble gate). False
  when a postcondition ran and failed, or when a necessary check
  (the input-line band) failed. None when no postcondition exists
  for this batch: an exception-list action (scroll, hover), or a
  batch with no DOM hook wired, where the pixel band stays a
  diagnostic, never a postcondition.

`ok` is the end-state statement, computed from the three parts in
exactly one place (build_contract): ok is True when the postcondition
passed, or when input was sent and no postcondition applies; ok is
False when a postcondition failed, even though input_sent is True.
A caller that reads only `ok` can no longer mistake "sent" for
"done": the split is visible in the same dict.

The per-action exception list is shared with P5: dom_asserts owns
the list, this module re-exports the same object so the two can
never drift apart.
"""
import dom_asserts

DOM_ASSERT_EXCEPTIONS = dom_asserts.DOM_ASSERT_EXCEPTIONS


def build_contract(*, input_sent, target_received=None, verified=None,
                   verified_basis=None):
    """Build the CB-1 fields plus the computed `ok`.

    input_sent, target_received, verified are bools or None as
    described in the module docstring. verified_basis names the
    postcondition that ran (for example 'dom-value',
    'sent-bubble'), or why none ran (for example
    'no-dom-postcondition: pixel band is diagnostic only').
    Returns a dict with input_sent, target_received, verified,
    verified_basis, and ok. ok is True exactly when the intended
    end state holds: verified is True (the postcondition passed,
    which also covers already-satisfied: nothing sent this call
    but the bubble is present), or input was sent and no
    postcondition applies (verified is None) and the target did
    not demonstrably miss (target_received is not False).
    """
    input_sent = bool(input_sent)
    if target_received is not None:
        target_received = bool(target_received)
    if verified is not None:
        verified = bool(verified)
    if verified is True:
        ok = True
    elif verified is False:
        ok = False
    else:
        ok = input_sent and target_received is not False
    return {'input_sent': input_sent,
            'target_received': target_received,
            'verified': verified,
            'verified_basis': verified_basis,
            'ok': ok}


def contract_ok(result):
    """ok for a result dict that already carries the contract fields.

    Falls back to the legacy bare `ok` when the dict predates the
    contract (an older build's session result): the fallback is
    explicit here so no caller silently treats a legacy ok as a
    verified ok without going through this function.
    """
    if not isinstance(result, dict):
        return False
    if 'verified' in result or 'input_sent' in result:
        return build_contract(
            input_sent=result.get('input_sent', result.get('ok')),
            target_received=result.get('target_received'),
            verified=result.get('verified'),
            verified_basis=result.get('verified_basis'))['ok']
    return result.get('ok') is True


def migrate_legacy_result(result):
    """Contract fields for a pre-CB-1 result dict with only `ok`.

    The legacy ok meant "input sent without error", so it migrates
    to input_sent, with verified None: no postcondition was ever
    recorded for that result, and nothing here claims one passed.
    """
    if not isinstance(result, dict):
        return build_contract(input_sent=False, verified=None,
                              verified_basis='not-a-result')
    return build_contract(
        input_sent=result.get('ok') is True,
        target_received=None, verified=None,
        verified_basis='legacy-result: no postcondition recorded')
