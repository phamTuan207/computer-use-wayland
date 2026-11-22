"""F4 root-cause probe: what changes on screen in the Zen window?

Captures three grim frames of the Zen window (t=0, t=150ms, t=1s,
the same cadence as desktop_act's preflight retry) and reports:
  - global mean pixel difference for each pair
  - the action-point patch difference (mean and max) around the
    #msg-input field center, the same CB-3(b) rule desktop_act
    uses (changed only when patch mean > 6 AND max pixel > 50)
  - the bounding box of pixels that changed by > 50, so we can see
    WHERE the change is (page content vs browser chrome)
Runs on the laptop (grim + PIL there). No input is sent, no tab
is opened or closed: read-only captures of the as-found Zen window.
"""
import json
import subprocess
import time
from io import BytesIO

from PIL import Image, ImageChops, ImageStat

# Zen window bounds from hyprctl (as-found, run-5 geometry).
ZEN = [2509, 914, 1863, 1176]
# #msg-input center in image coords for the run-5 batch meta
# (region = window bounds, image downscaled to max_width 960):
# screen (2957, 1181.87) -> image (230.85, 138.03).
AX, AY = 230.85, 138.03
SCALE = 960.0 / 1863.0


def grim(region):
    x, y, w, h = region
    geo = '%d,%d %dx%d' % (x, y, w, h)
    env = {'XDG_RUNTIME_DIR': '/run/user/1000',
           'WAYLAND_DISPLAY': 'wayland-1',
           'PATH': '/usr/bin:/bin'}
    out = subprocess.run(['grim', '-s', '1', '-g', geo, '-t', 'ppm', '-'],
                         capture_output=True, env=env, timeout=60)
    if out.returncode != 0:
        raise RuntimeError('grim failed: %s' % out.stderr.decode()[:200])
    img = Image.open(BytesIO(out.stdout)).convert('RGB')
    # Downscale to the batch meta size (max_width 960), same as
    # save_observation, so the diff is in image coords.
    if img.width > 960:
        img = img.resize((960, round(img.height * 960 / img.width)),
                         Image.Resampling.LANCZOS)
    return img


def mean_diff(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


def patch_detail(old, new, cx, cy, half=24):
    x0, y0 = max(0, int(cx) - half), max(0, int(cy) - half)
    x1, y1 = min(old.width, int(cx) + half + 1), min(old.height, int(cy) + half + 1)
    diff = ImageChops.difference(old, new).crop((x0, y0, x1, y1))
    mean = sum(ImageStat.Stat(diff).mean) / 3
    mx = max(hi for _lo, hi in diff.getextrema())
    return mean, mx


def changed_bbox(old, new, threshold=50):
    diff = ImageChops.difference(old, new).convert('L')
    # Bounding box of pixels whose max-channel diff exceeds threshold.
    # ImageChops.difference max channel: use point threshold on the
    # greyscale diff (a proxy; exact per-channel max is computed in
    # the patch detail above).
    bw = diff.point(lambda v: 255 if v > threshold else 0)
    return bw.getbbox()


frames = []
for i in range(3):
    frames.append(grim(ZEN))
    if i == 0:
        time.sleep(0.15)
    elif i == 1:
        time.sleep(0.85)
print('frame sizes:', [f.size for f in frames])
pairs = [(0, 1, 't0->t150ms'), (1, 2, 't150ms->t1s'), (0, 2, 't0->t1s')]
for a, b, label in pairs:
    md = mean_diff(frames[a], frames[b])
    pm, px = patch_detail(frames[a], frames[b], AX, AY)
    bb = changed_bbox(frames[a], frames[b])
    print('%s: global_mean=%.3f (screen_changed if >3) | '
          'action_patch mean=%.3f max=%d (changed if mean>6 AND max>50) | '
          'changed_bbox=%s'
          % (label, md, pm, px, bb))
print('PROBE DONE')
