"""Pick 4 grounding fast path helpers (speed-swarm prototype).

Pure coordinate math, no desktop access, so it is unit-testable on the VM.
Flag: CU_PICK4_FASTPATH=1. Default off. With the flag off, a11y describe()
omits extents, a11y query/ground refuse, and the CDP snapshot omits rects,
so the tree behaves exactly like the baseline.

Safety: a click never happens from an unverified coordinate. These helpers
only compute a candidate box and the crop region that verifies it. The
executor must observe that crop and confirm the target is visible at the
box center before any click, and the pointer miss check and screen-changed
refusal still apply to the act itself.
"""
import os

FLAG_ENV = 'CU_PICK4_FASTPATH'

# Crop verification context (M34 crop context rule): keep the target plus
# neighbouring controls in the crop so the verifier can disambiguate it.
CROP_PAD = 24
CROP_MIN_SIDE = 90
CROP_MAX_SIDE = 400


def enabled(env=None):
    """True only when the Pick 4 opt-in flag is exactly '1'."""
    values = os.environ if env is None else env
    return values.get(FLAG_ENV) == '1'


def _box4(value, name):
    if (not isinstance(value, (list, tuple)) or len(value) != 4 or
            any(isinstance(v, bool) or not isinstance(v, int) for v in value)):
        raise ValueError(name + ' must be four integer pixels [x, y, w, h]')
    if value[2] <= 0 or value[3] <= 0:
        raise ValueError(name + ' must have positive width and height')
    return [int(v) for v in value]


def detect_coord_frame(root_extents, window_bounds, tol=3):
    """Tell whether AT-SPI extents are screen or window relative.

    On Wayland a client cannot know its own screen position, so SCREEN
    extents may come back window relative. The app root is the tell: if
    the root origin sits at the Hyprland window origin the extents are
    screen coordinates; if it sits at (0, 0) they are window relative.
    Anything else is 'unknown' and the caller must fall back to vision.
    """
    root = _box4(root_extents, 'root_extents')
    window = _box4(window_bounds, 'window_bounds')
    if abs(root[0] - window[0]) <= tol and abs(root[1] - window[1]) <= tol:
        return 'screen'
    if abs(root[0]) <= tol and abs(root[1]) <= tol:
        return 'window'
    return 'unknown'


def to_global_box(extents, window_origin, coord_frame):
    """Convert an AT-SPI box to global desktop coordinates.

    window_origin is [x, y] of the Hyprland window. 'screen' boxes pass
    through unchanged; 'window' boxes get the origin added. 'unknown'
    fails closed: no coordinate is ever guessed.
    """
    box = _box4(extents, 'extents')
    origin = _box4([window_origin[0], window_origin[1], 1, 1],
                   'window_origin')[:2]
    if coord_frame == 'screen':
        return box
    if coord_frame == 'window':
        return [box[0] + origin[0], box[1] + origin[1], box[2], box[3]]
    raise ValueError(
        'cannot tell whether extents are screen or window relative; '
        'use vision')


def box_center(box):
    """Center point of a global [x, y, w, h] box."""
    box = _box4(box, 'box')
    return [box[0] + box[2] // 2, box[1] + box[3] // 2]


def crop_for_box(box_global, window_bounds, pad=CROP_PAD,
                 min_side=CROP_MIN_SIDE, max_side=CROP_MAX_SIDE):
    """Window-relative crop that verifies a global box.

    The crop contains the box plus pad pixels of neighbouring context on
    every side (M34), clamped to the window, grown to at least min_side
    where the window allows it, and capped at max_side centered on the
    box. Raises when the box lies outside its window.
    """
    box = _box4(box_global, 'box')
    window = _box4(window_bounds, 'window_bounds')
    bx, by = box[0] - window[0], box[1] - window[1]
    if bx < 0 or by < 0 or bx + box[2] > window[2] or by + box[3] > window[3]:
        raise ValueError('box lies outside its window; use vision')
    x0 = max(0, bx - pad)
    y0 = max(0, by - pad)
    x1 = min(window[2], bx + box[2] + pad)
    y1 = min(window[3], by + box[3] + pad)
    for axis in (0, 1):
        size = (x1 - x0) if axis == 0 else (y1 - y0)
        limit = window[2] if axis == 0 else window[3]
        if size < min_side:
            grow = min_side - size
            start = (x0, y0)[axis]
            end = (x1, y1)[axis]
            take_before = min(grow // 2, start)
            take_after = min(grow - take_before, limit - end)
            if axis == 0:
                x0 -= take_before
                x1 += take_after
            else:
                y0 -= take_before
                y1 += take_after
        size = (x1 - x0) if axis == 0 else (y1 - y0)
        if size > max_side:
            center = (bx + box[2] // 2) if axis == 0 else (by + box[3] // 2)
            start = max(0, min(center - max_side // 2, limit - max_side))
            if axis == 0:
                x0, x1 = start, start + max_side
            else:
                y0, y1 = start, start + max_side
    return [x0, y0, x1 - x0, y1 - y0]


def dom_center(rect):
    """Center point of a CDP getBoundingClientRect dict (viewport coords)."""
    if not isinstance(rect, dict):
        raise ValueError('rect must be an object')
    values = [rect.get(key) for key in ('x', 'y', 'width', 'height')]
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           for v in values):
        raise ValueError('rect needs numeric x, y, width, height')
    if values[2] <= 0 or values[3] <= 0:
        raise ValueError('rect must have positive width and height')
    return [round(values[0] + values[2] / 2),
            round(values[1] + values[3] / 2)]


def matches_query(item_name, item_role, name=None, role=None):
    """Pruned-query match: name substring (case-insensitive), role substring."""
    if name is not None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError('query name must be a non-empty string')
        if name.casefold() not in (item_name or '').casefold():
            return False
    if role is not None:
        if not isinstance(role, str) or not role.strip():
            raise ValueError('query role must be a non-empty string')
        if role.casefold() not in (item_role or '').casefold():
            return False
    return True
