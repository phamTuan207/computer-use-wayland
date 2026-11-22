"""F4 root-cause probe 2: JPEG asymmetry in desktop_act preflight.

desktop_act compares the batch meta image (JPEG q90 4:4:4 decoded,
from begin_batch) against a fresh uncompressed capture. The
CB-3(b) comment claims a q90 re-encode moves pixels by at most 39,
so the action-point AND rule (mean > 6 AND max > 50) should not
trip on codec alone. But the GLOBAL mean check
(_mean_image_difference > 3) has no such guard. This probe
reproduces the exact comparison on the laptop:
  old = grim frame saved as JPEG q90 4:4:4 then decoded
  new = fresh grim frame of the same static window
Reports the global mean diff and the action-point patch detail
(mean, max) for old-vs-new, plus a fresh-vs-fresh control.
The action point is the #msg-input center in image coords
(230.85, 138.03) for the run-5 batch meta.
"""
import subprocess
import time
from io import BytesIO

from PIL import Image, ImageChops, ImageStat

ZEN = [2509, 914, 1863, 1176]
AX, AY = 230.85, 138.03


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
    if img.width > 960:
        img = img.resize((960, round(img.height * 960 / img.width)),
                         Image.Resampling.LANCZOS)
    return img


def jpeg_roundtrip(img):
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=90, subsampling=0)
    buf.seek(0)
    return Image.open(buf).convert('RGB')


def mean_diff(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


def patch_detail(old, new, cx, cy, half=24):
    x0, y0 = max(0, int(cx) - half), max(0, int(cy) - half)
    x1, y1 = min(old.width, int(cx) + half + 1), min(old.height, int(cy) + half + 1)
    diff = ImageChops.difference(old, new).crop((x0, y0, x1, y1))
    mean = sum(ImageStat.Stat(diff).mean) / 3
    mx = max(hi for _lo, hi in diff.getextrema())
    return mean, mx


# old = the batch meta image (JPEG round trip of the begin_batch capture)
frame0 = grim(ZEN)
old = jpeg_roundtrip(frame0)
time.sleep(1.0)
new = grim(ZEN)
time.sleep(0.15)
settled = grim(ZEN)

md_old_new = mean_diff(old, new)
pm_old_new, px_old_new = patch_detail(old, new, AX, AY)
md_new_settled = mean_diff(new, settled)
pm_old_settled, px_old_settled = patch_detail(old, settled, AX, AY)
print('old(JPEG) vs new(fresh): global_mean=%.3f (screen_changed if >3) | '
      'action_patch mean=%.3f max=%d (changed if mean>6 AND max>50)'
      % (md_old_new, pm_old_new, px_old_new))
print('new(fresh) vs settled(fresh): global_mean=%.3f | '
      'action_patch mean=%.3f max=%d'
      % (md_new_settled, *patch_detail(new, settled, AX, AY)))
print('old(JPEG) vs settled(fresh): action_patch mean=%.3f max=%d '
      '(retry refuses if mean>6 AND max>50)'
      % (pm_old_settled, px_old_settled))
print('PROBE2 DONE')
