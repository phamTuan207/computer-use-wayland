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

import fastpath

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
