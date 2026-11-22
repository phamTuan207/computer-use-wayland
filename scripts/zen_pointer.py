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
a point action, no batch observation) or when the desktop act did
not complete every action. A CodeExecBackend.act refusal (CB-2)
propagates: a wrong stamp is a wiring bug, not a runtime
condition, and must be loud.
"""

DESKTOP_MAX_WIDTH = 960


class ZenPointerDelegate:
    """Pointer delegate around a CodeExecBackend."""

    def __init__(self, code_backend, focus_fn=None,
                 max_width=DESKTOP_MAX_WIDTH):
        self._code_backend = code_backend
        self._focus_fn = focus_fn
        self._max_width = max_width
        self._meta = None

    def begin_batch(self, window_address):
        """Focus the window, then observe it once for this batch.

        Returns the fresh observation meta. Raises ValueError when
        there is no window address or the meta cannot carry a
        binding (no id, no scope, no persisted observation path):
        the batch refuses before any input.
        """
        if not isinstance(window_address, str) or not window_address:
            raise ValueError(
                'Zen pointer delegate needs a window address to '
                'observe; got %r' % (window_address,))
        if self._focus_fn is not None:
            self._focus_fn(window_address)
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
        self._meta = meta
        return meta

    def __call__(self, action, screen_point):
        if self._meta is None:
            return False
        desktop = self._translate(action, screen_point)
        if desktop is None:
            return False
        for item in desktop:
            item['scope'] = self._meta['scope']
            item['observation_id'] = self._meta['id']
        result = self._code_backend.act(
            self._meta, desktop, self._meta['observation'])
        if not isinstance(result, dict):
            return False
        return (result.get('ok') is True
                and result.get('completed') == len(desktop))

    def _point(self, screen_point):
        """[x, y] as ints, or None when the point is unusable."""
        if (not isinstance(screen_point, (list, tuple))
                or len(screen_point) != 2):
            return None
        x, y = screen_point
        if isinstance(x, bool) or isinstance(y, bool):
            return None
        if not isinstance(x, (int, float)) \
                or not isinstance(y, (int, float)):
            return None
        return [int(x), int(y)]

    def _translate(self, action, screen_point):
        """Zen DOM action -> desktop actions, or None when the
        action cannot be mapped. A DOM focus is a desktop click at
        the point (the click focuses the field); confirm_click and
        hover_click were already confirmed in the DOM layer, so
        they click too. A drag needs from/to, which a single point
        cannot express. wait/assert never reach the delegate from
        the backend, and refuse here if they do."""
        if not isinstance(action, dict):
            return None
        action_type = action.get('type')
        if action_type == 'key':
            keys = action.get('keys')
            if (not isinstance(keys, list) or not keys
                    or any(not isinstance(k, str) for k in keys)):
                return None
            return [{'type': 'key', 'keys': list(keys)}]
        point = self._point(screen_point)
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
