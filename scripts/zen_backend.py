"""Zen DOM backend under the element-ref contract (P2, step 7).

The Marionette-backed adapter the router was missing: the router
already maps zen-content to dom-zen, but code_exec.py had zero
zen/marionette/bidi hits and DOM went only through CDP. This class
is the backend code_exec talks to when CU_DOM_BACKEND=zen: it owns
one ZenSession (ZenSession's own file lock enforces one session at
a time), waits for a Zen window class, and runs dom_observe/dom_act
under the stale-ref disagreement protocol
(docs/stale-ref-disagreement-protocol.md) with the same
snapshot-binding shape the CDP path returns.

What it does NOT do (step-9 prototype, with the evidence for why
it cannot be proven here): real pointer/keyboard dispatch. Clicks
are not done through the DOM here (BiDi click failed to fire a
handler, Marionette click fails on windowed Zen), so input must go
through the real mouse/keyboard via cu.desktop_act on a fresh
window observation meta, and only the broker-owned session
(CodeExecBackend.act) can supply that meta. The backend therefore
takes an optional input delegate `pointer(action, screen_point)`:
when none is set, click/fill/key actions return a structured
refusal naming the missing pointer delegate instead of acting.
The prototype must wire a delegate that observes the window once
per batch, stamps each action with that observation's scope +
observation_id, and dispatches through CodeExecBackend.act, then
prove it on the S2 task class with DOM verification mandatory.
The other prototype gaps: tab resolution by full list_tabs scan
(cache the handle list), role/name enrichment for Zen snapshots
(needs a harvest extension in zen_dom; refs are selectors here),
and checked-state asserts (no ZenSession API reads them).

Zen snapshots identify elements by selector (ref == selector);
there is no role/name enrichment yet.
"""

import time

import element_ref
import fastpath
import zen_dom

logger = zen_dom.logger

# Protocol section 2, check 1: a snapshot older than this is expired.
SNAPSHOT_MAX_AGE_SECONDS = element_ref.SNAPSHOT_MAX_AGE_SECONDS


class ZenDomBackend:
    """One Marionette session against one Zen, under the P2 contract."""

    DOM_WINDOW_CLASS = 'zen'
    SESSION_TIMEOUT_SECONDS = 30

    def __init__(self, session_factory=None, windows_fn=None,
                 pointer=None, marionette_port=None, wd_port=None,
                 session_timeout_s=SESSION_TIMEOUT_SECONDS,
                 verified_moz_inner=None):
        self._session_factory = session_factory or (
            lambda: zen_dom.ZenSession(
                marionette_port=(
                    marionette_port
                    if marionette_port is not None
                    else zen_dom.DEFAULT_MARIONETTE_PORT),
                wd_port=(wd_port if wd_port is not None
                         else zen_dom.DEFAULT_WD_PORT)))
        self._windows_fn = windows_fn
        self._pointer = pointer
        self.session_timeout_s = session_timeout_s
        # An independently measured viewport origin (C12-style
        # screenshot/click cross-check, pixel proof a42ef12), passed
        # to viewport_origin so closure overflow takes the verified
        # path instead of refusing. None by default: the value is a
        # state-dependent live measurement, never hardcoded; the live
        # probe that measures it wires it in. Until then the backend
        # fails closed on a displaced-moz window, which is correct.
        self._verified_moz_inner = verified_moz_inner
        self._session = None
        self._snapshot_count = 0
        self._snapshots = {}

    # -- session ownership: open in dom_start, close in finally. --

    def __enter__(self):
        self.dom_start()
        return self

    def __exit__(self, *args):
        self.close()
        return False

    def dom_start(self):
        """Open the session and wait for a Zen window to appear.

        Returns {'ok': True, 'window': address}. Raises
        ZenDomError when no Zen window appears within the timeout;
        the session is closed again on that failure, so a failed
        start never leaks the single-session slot.
        """
        if self._session is not None:
            return {'ok': True, 'reused': True}
        session = self._session_factory()
        try:
            session.__enter__()
        except Exception as exc:
            raise zen_dom.ZenDomError(
                'could not open a Zen session: %s' % exc) from exc
        self._session = session
        try:
            window = self._wait_for_zen_window()
        except Exception:
            self.close()
            raise
        return {'ok': True, 'window': window.get('address'),
                'class': window.get('class')}

    def _wait_for_zen_window(self):
        """The Zen window-class wait (cf. code_exec._wait_for_dom_window).

        Polls windows_fn() for a window whose class starts with
        'zen' (case-insensitive). Bounded by session_timeout_s;
        a window that never appears fails closed.
        """
        if self._windows_fn is None:
            raise zen_dom.ZenDomError(
                'Zen backend has no windows_fn: it cannot wait for '
                'a Zen window without a Hyprland clients source')
        deadline = time.monotonic() + self.session_timeout_s
        while True:
            try:
                wins = self._windows_fn()
            except Exception as exc:
                raise zen_dom.ZenDomError(
                    'windows() failed while waiting for Zen: %s'
                    % exc) from exc
            if isinstance(wins, list):
                for win in wins:
                    if (isinstance(win, dict)
                            and isinstance(win.get('class'), str)
                            and win['class'].lower().startswith('zen')):
                        return win
            if time.monotonic() >= deadline:
                raise zen_dom.ZenDomError(
                    'no Zen window appeared within %.1fs; start Zen '
                    'and observe windows() again'
                    % self.session_timeout_s)
            time.sleep(min(0.1, max(0.001, deadline - time.monotonic())))

    def windows(self):
        """Hyprland clients, for the code-exec window-class wait."""
        if self._windows_fn is None:
            return []
        return self._windows_fn()

    def set_pointer(self, pointer):
        """Wire the pointer/keyboard delegate after construction
        (step-9 prototype). The delegate is built around a
        CodeExecBackend, which itself needs this backend, so the
        two cannot be wired in either constructor. Until this is
        called the backend refuses input with no_pointer_delegate.
        """
        self._pointer = pointer

    def close(self):
        """Close the session in finally; idempotent."""
        session, self._session = self._session, None
        if session is not None:
            try:
                session.__exit__()
            except Exception:
                pass

    def _require_session(self):
        if self._session is None:
            raise zen_dom.ZenDomError(
                'no Zen session is open; call dom_start() first')
        return self._session

    # -- tabs and observation. --

    def dom_tabs(self):
        """[{handle, title, url}] from the live session."""
        session = self._require_session()
        tabs = session.list_tabs()
        if not isinstance(tabs, list):
            raise zen_dom.ZenDomError(
                'backend dom_tabs returned a non-list result')
        return tabs

    def _resolve_target(self, target):
        """Tab entry for a target: an int handle index, or a
        title/url/handle substring match over list_tabs. The full
        scan is a prototype cost (cache the handle list)."""
        session = self._require_session()
        if isinstance(target, int):
            return session.tab_at(target)
        tabs = session.list_tabs()
        for index, tab in enumerate(tabs):
            if not isinstance(tab, dict):
                continue
            if any(isinstance(tab.get(key), str)
                   and str(target) in tab[key]
                   for key in ('title', 'url', 'handle')):
                return session.tab_at(index)
        raise zen_dom.ZenDomError(
            'no tab matches target %r' % (target,))

    def _zen_window(self):
        """The Zen window client dict, from windows_fn()."""
        if self._windows_fn is None:
            raise zen_dom.ZenDomError(
                'Zen backend has no windows_fn: it cannot read the '
                'Zen window for grounding')
        for win in self._windows_fn():
            if (isinstance(win, dict)
                    and isinstance(win.get('class'), str)
                    and win['class'].lower().startswith('zen')):
                return win
        raise zen_dom.ZenDomError('no Zen window found for grounding')

    def _zen_window_bounds(self):
        """[x, y, w, h] of the Zen window, from windows_fn()."""
        win = self._zen_window()
        at = win.get('at')
        size = win.get('size')
        if (isinstance(at, (list, tuple)) and len(at) == 2
                and isinstance(size, (list, tuple))
                and len(size) == 2):
            return [at[0], at[1], size[0], size[1]]
        raise zen_dom.ZenDomError(
            'Zen window has no usable at/size for grounding: %r'
            % (win,))

    def dom_observe(self, target, scope, max_elements):
        """Snapshot one element by scope in one tab.

        scope is MANDATORY for Zen (a non-empty CSS selector):
        without it there is nothing to bind a ref to. Returns the
        snapshot dict {snapshot, title, url, elements, window,
        window_bounds}; elements carry ref == selector, the plan
        rect, and the distinguishing state (field value) the
        protocol re-checks before acting.
        """
        session = self._require_session()
        if not isinstance(scope, str) or not scope.strip():
            raise zen_dom.ZenDomError(
                'dom_observe on Zen requires a scope: a non-empty '
                'CSS selector to bind the snapshot to')
        tab = self._resolve_target(target)
        harvested = session.harvest([scope])
        pairs = []
        if isinstance(harvested, dict):
            items_map = harvested.get('items')
            if isinstance(items_map, dict):
                pairs = [(selector, item)
                         for selector, item in items_map.items()]
        elif isinstance(harvested, list):
            pairs = [(item.get('selector', scope), item)
                     for item in harvested
                     if isinstance(item, dict)]
        if not pairs:
            raise zen_dom.ZenDomError(
                'harvest did not return items for %r' % (scope,))
        window_bounds = self._zen_window_bounds()
        window_address = self._zen_window().get('address')
        self._snapshot_count += 1
        snapshot_id = 'zen-%d' % self._snapshot_count
        elements = []
        stored = {}
        for selector, item in pairs:
            rect = item.get('rect')
            if not isinstance(rect, dict):
                continue
            state = item.get('state')
            if state is None:
                state = session.field_value(selector)
            plan_rect = {'x': rect.get('x'), 'y': rect.get('y'),
                         'width': rect.get('width'),
                         'height': rect.get('height')}
            elements.append({'ref': selector, 'name': selector,
                             'rect': plan_rect, 'plan_rect': plan_rect,
                             'state': state})
            stored[selector] = {'rect': plan_rect, 'state': state}
        if not elements:
            raise zen_dom.ZenDomError(
                'no element matches %r' % (scope,))
        snapshot = {
            'snapshot': snapshot_id,
            'title': tab.get('title'),
            'url': tab.get('url'),
            'elements': elements,
            'window': window_bounds,
            'window_bounds': window_bounds,
        }
        self._snapshots[snapshot_id] = {
            'target': target,
            'created': time.time(),
            'elements': stored,
            'window_bounds': window_bounds,
            'window_origin': [window_bounds[0], window_bounds[1]],
            'window_address': window_address,
            'snapshot': snapshot,
        }
        return snapshot

    def _bound_snapshot(self, snapshot_id):
        binding = self._snapshots.get(snapshot_id)
        if binding is None:
            raise zen_dom.ZenDomError(
                'DOM snapshot id is not bound to this session; '
                'observe again')
        if time.time() - binding.get('created', 0) \
                > SNAPSHOT_MAX_AGE_SECONDS:
            raise zen_dom.ZenDomError(
                'DOM snapshot is older than 120s; observe again')
        return binding

    # -- action execution under the protocol. --

    def _screen_point(self, session, binding, rect):
        """Screen point of a rect center, via the viewport origin."""
        window_bounds = binding['window_bounds']
        try:
            origin = session.viewport_origin(
                [window_bounds[0], window_bounds[1]],
                [window_bounds[2], window_bounds[3]], None,
                verified_moz_inner=self._verified_moz_inner)
        except TypeError:
            # Duck-typed sessions (test fakes) without the verified
            # keyword take the three-argument form.
            origin = session.viewport_origin(
                [window_bounds[0], window_bounds[1]],
                [window_bounds[2], window_bounds[3]], None)
        return fastpath.dom_rect_to_screen_point(
            rect, origin, getattr(session, 'last_scale_factor', 1))

    def _revalidate(self, session, binding, action, selector):
        """Protocol section 2 checks for one action, in order.

        Returns (reason, live_rect, live_state): reason None when
        every check passes. Binding and scope were already checked
        by the caller; this runs resolve, visible, interactive,
        rect agreement, stability, uncovered, and the
        distinguishing-state match. A window move is checked by
        the caller before the per-action loop.
        """
        stored = binding['elements'].get(selector)
        plan_rect = stored['rect'] if stored else None
        plan_state = stored['state'] if stored else None
        report = session.locate_confirmed(selector)
        if report is None:
            return 'element_missing', None, None
        live_rect = report.get('rect')
        if not report.get('unique'):
            return 'element_ambiguous', live_rect, None
        if not report.get('visible'):
            return 'not_visible', live_rect, None
        if not report.get('interactive'):
            return 'not_interactive', live_rect, None
        live_state = session.field_value(selector)
        if plan_rect is not None and live_rect is not None \
                and not element_ref.rects_agree(plan_rect, live_rect):
            # The rect moved: the identity is confirmed only when
            # the distinguishing state still matches. A move with a
            # changed state is identity_unconfirmed, not rect_moved.
            if element_ref.check_distinguishing_state(plan_state,
                                                      live_state):
                return 'rect_moved', live_rect, live_state
            return 'identity_unconfirmed', live_rect, live_state
        if not report.get('stable'):
            return 'unstable', live_rect, live_state
        if not report.get('uncovered'):
            return 'covered', live_rect, live_state
        if not element_ref.check_distinguishing_state(plan_state,
                                                      live_state):
            return 'identity_unconfirmed', live_rect, live_state
        return None, live_rect, live_state

    def _note_typed(self, binding, selector, session):
        """Lifecycle (protocol section 5): after a verified fill,
        the batch's own typing changed the field, so the recorded
        distinguishing state for later steps in the same batch is
        the new value, not the observe-time one. Without this the
        next action would refuse its own batch's typing as an
        identity change."""
        stored = binding['elements'].get(selector)
        if stored is not None:
            stored['state'] = session.field_value(selector)

    def _dispatch(self, action, screen_point):
        """Send one action through the input delegate.

        Returns (input_sent, target_received). Without a delegate
        the action is refused, never guessed: the caller records
        the refusal in the action result.
        """
        if self._pointer is None:
            return False, False
        sent = self._pointer(action, screen_point)
        return bool(sent), bool(sent)

    def _no_pointer_result(self, index):
        """The structured refusal when no input delegate is set.

        Used BEFORE any _dispatch call, on every dispatch path
        (the main path for all types, and the re-ground path), so
        the error code always names the true cause. The old
        8-type allowlist guard let type/move through to _dispatch
        (which failed closed but reported no-dom-postcondition)
        and let the re-ground path report focus_check or
        dom-value; all three hid the missing delegate.
        """
        return {'action_index': index,
                'input_sent': False,
                'target_received': False,
                'verified': False,
                'verified_basis': 'no-pointer-delegate',
                'ok': False,
                'error': {
                    'code': 'no_pointer_delegate',
                    'reason': 'the Zen backend has no pointer '
                              'delegate: input dispatch needs '
                              'the step-9 prototype wiring '
                              '(CodeExecBackend.act on a fresh '
                              'window observation)'}}

    def _verify(self, session, action, selector, typed_text,
                actions=None):
        """CB-1 postcondition for one dispatched action.

        Returns (verified, verified_basis). Clicks verify by
        focus_check, fills by verify_typed (dom-value), send keys
        by sent_bubble_contains. Scroll/hover/move/wait/key
        (non-send) have no DOM postcondition: verified False with
        the reason named, per the contract's per-action exception
        list.
        """
        action_type = action.get('type')
        if action_type in ('click', 'double_click', 'confirm_click',
                           'hover_click'):
            ok = session.focus_check(selector)
            return bool(ok), 'focus_check'
        if action_type in ('fill', 'set_value'):
            ok = session.verify_typed(selector, action.get('text', ''))
            return bool(ok), 'dom-value'
        if action_type == 'key':
            assert_spec = action.get('assert') \
                if isinstance(action.get('assert'), dict) else None
            if assert_spec is not None \
                    and assert_spec.get('type') == 'sent_bubble':
                ok = session.sent_bubble_contains(
                    assert_spec.get('text', ''))
                return bool(ok), 'sent-bubble'
            if element_ref.is_send_action(action, actions):
                text = typed_text or action.get('text', '')
                ok = session.sent_bubble_contains(text)
                return bool(ok), 'sent-bubble'
            return False, 'no-dom-postcondition:key'
        if action_type == 'assert':
            if action.get('checked') is not None:
                return False, 'checked-assert-unsupported'
            expected = action.get('text', action.get('value'))
            if expected is None:
                return False, 'assert-needs-text-or-value'
            ok = session.verify_typed(selector, expected)
            if ok:
                return True, 'dom-value'
            value = session.field_value(selector)
            return value == expected, 'dom-value'
        return False, 'no-dom-postcondition:%s' % action_type

    def dom_act(self, target, snapshot_id, actions, after_scope=None,
                no_after=False):
        """Run one action batch against a bound Zen snapshot.

        Returns {'ok', 'completed', 'results', 'error'?, 'after'?}.
        A stale-ref disagreement stops the batch with the exact
        protocol section 7 error shape; a strict-path action stops
        on ANY disagreement, and a re-ground may supply the fresh
        snapshot for the re-plan (reported top-level as
        'fresh_snapshot') without executing inside the old batch.
        """
        session = self._require_session()
        binding = self._bound_snapshot(snapshot_id)
        for index, action in enumerate(actions):
            try:
                element_ref.validate_action_binding(
                    action, snapshot_id=snapshot_id, scope=target,
                    index=index)
            except element_ref.ElementRefError as exc:
                raise zen_dom.ZenDomError(str(exc)) from exc
        # Step-9 prototype: the pointer delegate observes the
        # window once per batch (focus first, then observe), so
        # every dispatch in this batch stamps the same fresh
        # observation. A delegate without begin_batch (a plain
        # callable) is used as-is. A begin_batch failure refuses
        # the batch before any input. Read-only batches (wait /
        # assert only) skip it: they dispatch nothing, so they
        # must not focus or observe either.
        needs_input = any(
            isinstance(a, dict) and a.get('type') not in ('wait', 'assert')
            for a in actions)
        if needs_input:
            begin_batch = getattr(self._pointer, 'begin_batch', None)
            if callable(begin_batch):
                begin_batch(binding.get('window_address'))
        # Window move (protocol section 3): the origin changed, so
        # re-ground all refs against the new origin first.
        window_origin = binding['window_origin']
        live_origin = None
        try:
            live_origin = session.live_window_origin(
                binding.get('window_address'))
        except Exception:
            live_origin = None
        results = []
        fresh_snapshot = None
        if live_origin is not None and live_origin != window_origin:
            scope = next(iter(binding['elements']), None)
            if scope is not None:
                fresh = self.dom_observe(target, scope, 80)
                fresh_snapshot = fresh
                binding = self._bound_snapshot(fresh['snapshot'])
        # Strictness is batch-level (protocol section 4): when the
        # batch contains a send, a disagreement on ANY action in it
        # stops the batch, because re-grounding an earlier action
        # would still act inside the send batch.
        batch_strict = any(
            element_ref.is_strict_action(action, actions)
            for action in actions)
        typed_text = None
        completed = 0
        error = None
        for index, action in enumerate(actions):
            action_type = action.get('type')
            selector = action.get('ref') or action.get('selector')
            strict = batch_strict or element_ref.is_strict_action(
                action, actions)
            if action_type == 'wait':
                # Wait is time.sleep only: no input is dispatched,
                # so input_sent and target_received are False even
                # though the action itself succeeds.
                time.sleep((action.get('ms') or 0) / 1000.0)
                results.append({'action_index': index,
                                'input_sent': False,
                                'target_received': False,
                                'verified': False,
                                'verified_basis': 'no-dom-postcondition:wait',
                                'ok': True})
                completed += 1
                continue
            reason, live_rect, _live_state = self._revalidate(
                session, binding, action, selector)
            if reason is not None:
                stored = binding['elements'].get(selector)
                plan_rect = stored['rect'] if stored else None
                # _revalidate returns rect_moved only when the
                # distinguishing state still matches, so a move
                # here is identity-confirmed by construction; any
                # other reason carries its own identity.
                identity_confirmed = (reason == 'rect_moved')
                disposition = element_ref.decide_disposition(
                    reason=reason,
                    identity_confirmed=identity_confirmed,
                    strict=strict, reground_ok=False)
                if reason == 'rect_moved' and not strict:
                    # One re-ground, then act once on the fresh rect
                    # (protocol section 3): re-resolve, confirm the
                    # identity again, and dispatch on the fresh
                    # screen point.
                    report = session.locate_confirmed(selector)
                    if report is not None and report.get('unique') \
                            and report.get('visible') \
                            and report.get('interactive') \
                            and report.get('uncovered') \
                            and report.get('stable'):
                        live_state = session.field_value(selector)
                        if element_ref.check_distinguishing_state(
                                stored['state'] if stored else None,
                                live_state):
                            fresh_rect = report['rect']
                            screen_point = self._screen_point(
                                session, binding, fresh_rect)
                            if self._pointer is None:
                                no_pointer = self._no_pointer_result(
                                    index)
                                no_pointer['re_ground'] = {
                                    'plan_rect': plan_rect,
                                    'live_rect': fresh_rect}
                                results.append(no_pointer)
                                error = {'code': 'no_pointer_delegate',
                                         'reason': 'no-pointer-delegate'}
                                break
                            sent, received = self._dispatch(
                                action, screen_point)
                            verified, basis = self._verify(
                                session, action, selector, typed_text,
                                actions)
                            ok = sent and received and (
                                verified or basis.startswith(
                                    'no-dom-postcondition'))
                            results.append({
                                'action_index': index,
                                'input_sent': sent,
                                'target_received': received,
                                'verified': verified,
                                'verified_basis': basis,
                                'ok': ok,
                                're_ground': {'plan_rect': plan_rect,
                                              'live_rect': fresh_rect}})
                            if ok:
                                completed += 1
                                if action_type in ('fill', 'set_value'):
                                    typed_text = action.get('text', '')
                                    self._note_typed(
                                        binding, selector, session)
                                continue
                            error = {'code': 'action_failed',
                                     'reason': basis}
                            break
                if strict and reason == 'rect_moved' \
                        and identity_confirmed:
                    # The re-plan snapshot: re-ground supplies it,
                    # the action does not execute in the old batch.
                    try:
                        fresh_snapshot = self.dom_observe(
                            target, selector, 80)
                    except Exception:
                        fresh_snapshot = None
                section7 = element_ref.stale_ref_error(
                    reason=disposition['reason'], selector=selector,
                    snapshot_id=snapshot_id, scope=target,
                    plan_rect=plan_rect, live_rect=live_rect,
                    action_index=index)
                error = section7['error']
                results.append(dict(section7, action_index=index))
                break
            if action_type == 'assert':
                # An assert reads state; it needs no pointer and
                # dispatches no input, so input_sent and
                # target_received are False. Its ok comes from the
                # postcondition below, not from input_sent.
                sent = received = False
                screen_point = None
            else:
                screen_point = None
                if action_type != 'key':
                    screen_point = self._screen_point(
                        session, binding, live_rect)
                if self._pointer is None:
                    # Checked before EVERY _dispatch call, for all
                    # types, instead of the old 8-type allowlist:
                    # type/move used to fall through to _dispatch
                    # and report no-dom-postcondition errors.
                    no_pointer = self._no_pointer_result(index)
                    results.append(no_pointer)
                    error = {'code': 'no_pointer_delegate',
                             'reason': 'no-pointer-delegate'}
                    break
                sent, received = self._dispatch(action, screen_point)
            verified, basis = self._verify(
                session, action, selector, typed_text, actions)
            if action_type == 'assert':
                ok = verified
            else:
                ok = sent and received and (
                    verified or basis.startswith('no-dom-postcondition'))
            results.append({'action_index': index,
                            'input_sent': sent,
                            'target_received': received,
                            'verified': verified,
                            'verified_basis': basis,
                            'ok': ok})
            if not ok:
                error = {'code': 'action_failed',
                         'reason': basis}
                break
            completed += 1
            if action_type in ('fill', 'set_value'):
                typed_text = action.get('text', '')
                self._note_typed(binding, selector, session)
        ok = error is None and completed == len(actions)
        result = {'ok': ok, 'completed': completed,
                  'results': results}
        if error is not None:
            result['error'] = error
        if fresh_snapshot is not None:
            result['fresh_snapshot'] = fresh_snapshot
        if ok and not no_after:
            scope = next(iter(binding['elements']), None) \
                if binding['elements'] else None
            if scope is not None:
                try:
                    after = self.dom_observe(target, scope, 80)
                    result['after'] = after
                except Exception:
                    pass
        return result
