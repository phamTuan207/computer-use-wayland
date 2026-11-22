"""Zen pointer/keyboard delegate (step-9 prototype, item 5).

The Zen backend refuses input with no_pointer_delegate until a
delegate is wired. This delegate translates Zen DOM actions plus
their screen points into desktop actions and dispatches them
through a CodeExecBackend (real pointer via desktop_act), stamping
each action with the scope + observation_id of one fresh window
observation per batch. The backend calls begin_batch once per
batch (focus the Zen window first, then observe, per the step-8
lesson) and then calls the delegate once per dispatched action.

The delegate is a callable: pointer(action, screen_point) -> bool,
matching the backend's _pointer contract (True means the input was
sent and the target received it). It returns False, never raises,
when an action cannot be mapped (drag, unknown type, no point for
a point action, no batch observation, or a point outside the batch
observation image) or when the desktop act did not complete every
action. A CodeExecBackend.act refusal (CB-2) propagates: a wrong
stamp is a wiring bug, not a runtime condition, and must be loud.

Coordinate frames (run 4 F3): the backend hands this delegate
GLOBAL screen points (viewport rect center plus the absolute
viewport origin), but desktop_act consumes IMAGE points: its
preflight maps them through cu.image_point, which refuses any
point outside the observation image. The delegate therefore
converts every screen point to an image point against the batch
observation meta (fastpath.screen_point_to_image_point, the
inverse of cu.image_point) before building desktop actions. Run 4
sent the raw screen point (2939, 1168) as an image point against
a 925x1176 window image and was refused with 'point outside
observed image'; the converted point is (430, 254.87), which
round-trips to the same global point.
"""

import time

import fastpath

DESKTOP_MAX_WIDTH = 960
# F4 settle (begin_batch observation stability): the window may be
# mid-transition when begin_batch observes it (a tab-switch
# cross-fade leaves the previous tab ghosted through the new one
# for ~1s; the batch meta then differs from the settled screen by
# a global mean of ~3.6, and desktop_act's preflight correctly
# refuses it as 'screen changed'). Re-observe until two
# consecutive observations agree, so the batch meta is a stable
# frame. Threshold 0.5 sits well above static-screen noise (~0.02)
# and well below the preflight refusal threshold (3.0). Budget 2s
# covers the observed ~1s transient; on expiry the latest meta is
# used and the preflight stays the gatekeeper.
SETTLE_BUDGET_S = 2.0
SETTLE_POLL_S = 0.1
SETTLE_MEAN_THRESHOLD = 0.5


class ZenPointerDelegate:
    """Pointer delegate around a CodeExecBackend."""

    def __init__(self, code_backend, focus_fn=None,
                 max_width=DESKTOP_MAX_WIDTH):
        self._code_backend = code_backend
        self._focus_fn = focus_fn
        self._max_width = max_width
        self._meta = None
        # F4 diagnostic: the last dispatch outcome, so a failed
        # dom_act can say WHERE it failed instead of collapsing
        # every cause into the verify basis. Set on every __call__:
        # 'translated' False means _translate refused (no meta, no
        # image point, unmappable type); 'act_ok'/'act_completed'
        # carry the desktop_act result when the action was sent.
        # Read-only diagnostics, never used to change dispatch.
        self.last_dispatch = None
        # F4 diagnostic: the begin_batch settle outcome
        # {'reads', 'stable', 'elapsed_ms'}, set by begin_batch.
        self.last_settle = None
        # F4 follow-up: the post-type/key refresh settle and its
        # error, kept SEPARATE from last_settle. REDTEAM (F4,
        # 66c34f8): the refresh overwrote last_settle, so the
        # dom_act 'settle' no longer described the batch start.
        # last_settle is the BEGIN settle only; the refresh settle
        # rides last_refresh_settle, and a refresh failure is
        # recorded in last_refresh_error instead of swallowed.
        self.last_refresh_settle = None
        self.last_refresh_error = None
        # The window address begin_batch observed, kept so a
        # post-type meta refresh can re-observe the same window.
        self._window_address = None

    def _observe(self, window_address):
        """One window observation, validated as a batch binding.

        Raises ValueError when the meta cannot carry a binding (no
        id, no scope, no persisted observation path): the batch
        refuses before any input.
        """
        meta = self._code_backend.observe_window(
            window_address, crop=None, max_width=self._max_width)
        if not isinstance(meta, dict) or not meta.get('id'):
            raise ValueError(
                'Zen pointer delegate: window observation has no id; '
                'actions cannot be bound (CB-2)')
        if not meta.get('scope'):
            raise ValueError(
                'Zen pointer delegate: window observation has no '
                'scope; actions cannot be bound (CB-2)')
        if not meta.get('observation'):
            raise ValueError(
                'Zen pointer delegate: window observation has no '
                'persisted observation path; desktop_act cannot '
                'validate it')
        return meta

    @staticmethod
    def _mean_diff(meta_a, meta_b):
        """Mean absolute pixel difference between two observation
        images, or inf when they cannot be compared. Both images
        are the stored JPEGs, so a static screen compares near 0
        and a mid-transition frame compares in the units (a
        tab-switch cross-fade measured ~3.6)."""
        try:
            from PIL import Image, ImageChops, ImageStat
            a = Image.open(meta_a['image']).convert('RGB')
            b = Image.open(meta_b['image']).convert('RGB')
        except Exception:
            return float('inf')
        if a.size != b.size:
            return float('inf')
        return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3

    def _settle_observation(self, window_address, meta):
        """Re-observe until the window is visually stable (F4).

        Returns the latest observation and a settle record
        {'reads': n, 'stable': bool, 'elapsed_ms': ms}. The first
        observation may be a mid-transition frame (previous tab
        ghosted through); two consecutive observations agreeing
        within SETTLE_MEAN_THRESHOLD prove the transient resolved.
        On budget expiry the latest meta is returned anyway and
        stable is False, so desktop_act's preflight stays the
        gatekeeper instead of the delegate refusing on its own.
        """
        start = time.monotonic()
        reads = 1
        stable = False
        # The loop always compares the latest two observations.
        while True:
            nxt = self._observe(window_address)
            reads += 1
            if self._mean_diff(meta, nxt) <= SETTLE_MEAN_THRESHOLD:
                meta = nxt
                stable = True
                break
            meta = nxt
            if time.monotonic() - start >= SETTLE_BUDGET_S:
                break
            time.sleep(SETTLE_POLL_S)
        return meta, {'reads': reads, 'stable': stable,
                      'elapsed_ms': round((time.monotonic() - start)
                                          * 1000, 3)}

    def begin_batch(self, window_address):
        """Focus the window, then observe it once for this batch.

        Returns the fresh observation meta. Raises ValueError when
        there is no window address or the meta cannot carry a
        binding (no id, no scope, no persisted observation path):
        the batch refuses before any input. The observation is
        settled first (F4): a frame captured mid-transition would
        make desktop_act's preflight refuse the whole batch as
        'screen changed', so begin_batch re-observes until the
        window is visually stable.
        """
        if not isinstance(window_address, str) or not window_address:
            raise ValueError(
                'Zen pointer delegate needs a window address to '
                'observe; got %r' % (window_address,))
        if self._focus_fn is not None:
            self._focus_fn(window_address)
        self._window_address = window_address
        meta = self._observe(window_address)
        meta, settle = self._settle_observation(window_address, meta)
        self._meta = meta
        # F4 diagnostic: the settle outcome rides the meta so a
        # later refusal can say whether the batch started stable.
        self.last_settle = settle
        # Re-review follow-up (council + redteam): reset the
        # refresh settle and error here, so a later type/key-less
        # batch does not surface the previous batch's refresh
        # settle. Same staleness class as the viewport_settle fix.
        self.last_refresh_settle = None
        self.last_refresh_error = None
        return meta

    def __call__(self, action, screen_point):
        if self._meta is None:
            self.last_dispatch = {'translated': False,
                                  'reason': 'no-batch-meta'}
            return False
        desktop = self._translate(action, screen_point)
        if desktop is None:
            self.last_dispatch = {'translated': False,
                                  'reason': 'translate-refused'}
            return False
        for item in desktop:
            item['scope'] = self._meta['scope']
            item['observation_id'] = self._meta['id']
        result = self._code_backend.act(
            self._meta, desktop, self._meta['observation'])
        if not isinstance(result, dict):
            self.last_dispatch = {'translated': True,
                                  'act_ok': None,
                                  'act_completed': None,
                                  'act_expected': len(desktop),
                                  'reason': 'act-not-a-dict'}
            return False
        self.last_dispatch = {
            'translated': True,
            'act_ok': result.get('ok'),
            'act_completed': result.get('completed'),
            'act_expected': len(desktop),
            'act_error': result.get('error'),
            'act_error_code': result.get('error_code'),
            'act_screen_change': result.get('screen_change'),
            'type_verified': result.get('type_verified'),
            'type_verified_basis': result.get('type_verified_basis'),
            # F4 follow-up: the desktop_act IME trace, so a doubled
            # or mangled typed value can be traced to the input
            # method state around the type (fcitx5 switch/restore)
            # instead of guessed. Additive only.
            'ime_state_trace': result.get('ime_state_trace'),
            'ime_restore_failed': result.get('ime_restore_failed'),
            'wtype_stderr': result.get('wtype_stderr'),
        }
        ok = (result.get('ok') is True
              and result.get('completed') == len(desktop))
        if ok and any(item.get('type') in ('type', 'key')
                      for item in desktop):
            # F4 follow-up: a type or a key changes the screen
            # (the text now shows in the field; Enter sends the
            # bubble), so the batch meta is stale for the NEXT
            # action's desktop_act preflight, which would refuse
            # it as 'screen changed' (f4diag run 8: set_value
            # verified, then the focus was refused). REDTEAM (F4,
            # 66c34f8): a key dispatch has the same failure class
            # as a type, so it refreshes too. Refresh the meta
            # (observe + settle) so the next dispatch compares
            # against the screen WITH the typed text / sent bubble.
            # A refresh failure must not fail the action that
            # already succeeded; the next dispatch keeps the stale
            # meta and its preflight stays the gatekeeper. The
            # refresh settle is recorded separately (it must not
            # overwrite last_settle, the BEGIN settle) and a
            # refresh failure is recorded, never swallowed.
            try:
                address = self._window_address
                fresh = self._observe(address)
                fresh, settle = self._settle_observation(address, fresh)
                self._meta = fresh
                self.last_refresh_settle = settle
                self.last_refresh_error = None
            except Exception as exc:
                # Re-review follow-up: clear the settle next to
                # the error, so a stale refresh settle is not left
                # in place beside a fresh failure.
                self.last_refresh_settle = None
                self.last_refresh_error = type(exc).__name__
        return ok

    def _image_point(self, screen_point):
        """[x, y] in the batch observation image, or None.

        The backend passes GLOBAL screen points, but desktop_act
        consumes IMAGE points, so the point is converted against
        the batch observation meta (the inverse of
        cu.image_point). A point outside the observed image, or a
        meta without an image frame, maps to None: the delegate
        refuses the action instead of dispatching a point the
        desktop preflight would reject. Floats are kept, not
        truncated: validate_actions and image_point both accept
        finite floats, and truncating would shift the click by up
        to one image px.
        """
        if (not isinstance(screen_point, (list, tuple))
                or len(screen_point) != 2):
            return None
        x, y = screen_point
        if isinstance(x, bool) or isinstance(y, bool):
            return None
        if not isinstance(x, (int, float)) \
                or not isinstance(y, (int, float)):
            return None
        if self._meta is None:
            return None
        try:
            return fastpath.screen_point_to_image_point(
                self._meta, x, y)
        except (ValueError, TypeError):
            return None

    def _translate(self, action, screen_point):
        """Zen DOM action -> desktop actions, or None when the
        action cannot be mapped. A DOM focus is a desktop click at
        the point (the click focuses the field); confirm_click and
        hover_click were already confirmed in the DOM layer, so
        they click too. A drag needs from/to, which a single point
        cannot express. wait/assert never reach the delegate from
        the backend, and refuse here if they do. The point is the
        IMAGE point of the screen point (see _image_point): a
        screen point outside the batch observation image refuses
        the action instead of dispatching."""
        if not isinstance(action, dict):
            return None
        action_type = action.get('type')
        if action_type == 'key':
            keys = action.get('keys')
            if (not isinstance(keys, list) or not keys
                    or any(not isinstance(k, str) for k in keys)):
                return None
            return [{'type': 'key', 'keys': list(keys)}]
        point = self._image_point(screen_point)
        if point is None:
            return None
        x, y = point
        if action_type in ('click', 'double_click', 'focus',
                           'confirm_click', 'hover_click'):
            return [{'type': action_type if action_type in (
                'click', 'double_click') else 'click', 'x': x, 'y': y}]
        if action_type in ('fill', 'set_value'):
            text = action.get('text')
            if not isinstance(text, str):
                return None
            return [{'type': 'click', 'x': x, 'y': y},
                    {'type': 'type', 'text': text}]
        if action_type in ('move', 'hover'):
            return [{'type': action_type, 'x': x, 'y': y}]
        if action_type == 'scroll':
            dy = action.get('dy')
            if not isinstance(dy, (int, float)) or isinstance(dy, bool):
                return None
            dx = action.get('dx', 0)
            if not isinstance(dx, (int, float)) or isinstance(dx, bool):
                return None
            return [{'type': 'scroll', 'x': x, 'y': y, 'dx': dx,
                     'dy': dy}]
        return None
