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


def _rect_center_float(rect):
    """Rect center as floats (no rounding: the image map keeps them)."""
    values = [rect.get(key) for key in ('x', 'y', 'width', 'height')]
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           for v in values):
        raise ValueError('rect needs numeric x, y, width, height')
    if values[2] <= 0 or values[3] <= 0:
        raise ValueError('rect must have positive width and height')
    return [values[0] + values[2] / 2, values[1] + values[3] / 2]


def dom_rect_to_screen_point(rect, viewport_origin, scale_factor=1):
    """Screen point of a DOM rect center (viewport CSS px + origin).

    The calibration_e2 proven chain, corrected by the live C12 probe
    (2026-11-22 03:36, four runs, one real click): mozInnerScreenX/Y
    in this Zen build are WINDOW-relative, so the viewport origin
    passed here must be the ABSOLUTE origin, Hyprland window origin
    + mozInnerScreenX/Y (zen_dom.viewport_origin computes it and
    verifies it with the monitor-bounds + dimension-closure checks).
    Rect centers are viewport-relative CSS px; scale_factor maps CSS
    px to screen px (screenPixelsPerCSSPixel, falling back to
    devicePixelRatio; 1 at the measured scale-1 setup, 2 at monitor
    scale 2, where the unscaled map lands about 306 screen px off).
    No screenshot is read: the DOM rect is ground truth, so the point
    is right the first time.
    """
    center = _rect_center_float(rect)
    if (not isinstance(viewport_origin, (list, tuple))
            or len(viewport_origin) != 2
            or any(isinstance(v, bool) or not isinstance(v, (int, float))
                   for v in viewport_origin)):
        raise ValueError('viewport_origin must be two numbers [x, y]')
    if (isinstance(scale_factor, bool)
            or not isinstance(scale_factor, (int, float))
            or scale_factor <= 0):
        raise ValueError('scale_factor must be a positive number')
    return [viewport_origin[0] + center[0] * scale_factor,
            viewport_origin[1] + center[1] * scale_factor]


def _image_point_for_screen(meta, sx, sy):
    """Image point for a screen point, or None when outside the image."""
    size = meta.get('image_size')
    region = meta.get('region')
    iw, ih = size
    rx, ry, rw, rh = region
    ix = (sx - rx) * iw / rw
    iy = (sy - ry) * ih / rh
    if not (0 <= ix < iw and 0 <= iy < ih):
        return None
    return [ix, iy]


def screen_point_to_image_point(meta, sx, sy):
    """Image point for a screen point (A9: the driver-edge map).

    The second half of the old fused rect-to-image function, now
    public: a screen point (canonical, from
    dom_rect_to_screen_point) maps into the observation image by
    the inverse of cu.image_point. Raises ValueError when the meta
    lacks image_size/region, when the region is degenerate, or
    when the point falls outside the observed image: fail closed,
    never guess a point off the image.
    """
    if not isinstance(meta, dict):
        raise ValueError('meta must be an object')
    size = meta.get('image_size')
    region = meta.get('region')
    if (not isinstance(size, (list, tuple)) or len(size) != 2
            or any(isinstance(v, bool) or not isinstance(v, (int, float))
                   or v <= 0 for v in size)):
        raise ValueError('meta needs a positive image_size [w, h]')
    if (not isinstance(region, (list, tuple)) or len(region) != 4
            or any(isinstance(v, bool) or not isinstance(v, (int, float))
                   for v in region)
            or region[2] <= 0 or region[3] <= 0):
        raise ValueError('meta needs a region [x, y, w, h] with positive size')
    point = _image_point_for_screen(meta, sx, sy)
    if point is not None:
        return point
    raise ValueError(
        'screen point (%s, %s) maps outside the observed image '
        '(%s, %s) of %sx%s'
        % (sx, sy, (sx - region[0]) * size[0] / region[2],
           (sy - region[1]) * size[1] / region[3], size[0], size[1]))


def dom_rect_to_image_point(meta, rect, viewport_origin, scale_factor=1):
    """Image point of a DOM rect center for one observation meta.

    Kept for tests and legacy callers only (final direction): no
    production caller uses it. The live path converts the rect
    once to a screen point (dom_rect_to_screen_point) and derives
    the image point at the driver edge
    (screen_point_to_image_point); this function is exactly that
    composition, kept so its tests keep passing.

    Inverse of cu.image_point (same linear map, region origin and
    image size from the meta): screen = absolute origin + rect center
    times the CSS-to-screen factor, then image = (screen - region
    origin) * image size / region size. Raises ValueError when the
    meta lacks image_size/region, when the region is degenerate, or
    when the point falls outside the observed image (stale observation
    or moved window): fail closed, never guess a point off the image.

    Origin semantics (live probe 03:36): mozInnerScreenX/Y are
    window-relative in this Zen build, so a caller that passes the raw
    pair as the origin is wrong by the window origin (the old bug:
    (240, 8) as absolute maps off-monitor). The origin argument is
    therefore the ABSOLUTE origin from zen_dom.viewport_origin().
    There is no fallback retry: when the absolute reading maps
    outside the observed image the function raises (a stale
    observation, a moved window, or a wrong origin are all refusals,
    never guesses). An earlier safety net that retried with a
    window-relative reading was deleted in amend3: it silently
    rescued exactly the old-bug call, so the R1 test passed via the
    net instead of via the fixed chain, and a wrong origin that
    happened to land inside was used with no warning.
    """
    sx, sy = dom_rect_to_screen_point(rect, viewport_origin, scale_factor)
    return screen_point_to_image_point(meta, sx, sy)


def point_in_rect(rect, x, y):
    """True when the point lies inside a screen rect {x, y, w, h}.

    The hit test for grounding accuracy: a rect-center click lands
    inside the target element exactly when this is True.
    """
    if not isinstance(rect, dict):
        raise ValueError('rect must be an object')
    values = [rect.get(key) for key in ('x', 'y', 'width', 'height')]
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           for v in values):
        raise ValueError('rect needs numeric x, y, width, height')
    return (values[0] <= x <= values[0] + values[2]
            and values[1] <= y <= values[1] + values[3])


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
