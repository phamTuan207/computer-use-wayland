"""F4 root-cause probe 3: does re-focusing an already-focused Zen
window trigger a fade/blur animation that a grim capture catches?

Sequence (all on the laptop, read-only, no input sent):
  A. Capture the Zen window twice, 500ms apart, WITHOUT any focus
     call. If both are sharp and identical, the window is stable
     when untouched.
  B. Call hyprctl focus on the Zen window (it is already focused),
     capture IMMEDIATELY, then capture again 500ms later.
     If the immediate capture is blurred/translucent and the later
     one is sharp, the focus call itself triggers the animation.
Reports global mean diffs and saves the frames for sight review.
"""
import subprocess
import time
from io import BytesIO

from PIL import Image, ImageChops, ImageStat

ZEN = [2509, 914, 1863, 1176]
ADDR = '0x56307e2771d0'


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


def hypr_focus(addr):
    env = {'XDG_RUNTIME_DIR': '/run/user/1000',
           'WAYLAND_DISPLAY': 'wayland-1',
           'HYPRLAND_INSTANCE_SIGNATURE': subprocess.run(
               ['ls', '/run/user/1000/hypr/'], capture_output=True,
               text=True).stdout.split()[0],
           'PATH': '/usr/bin:/bin'}
    out = subprocess.run(
        ['hyprctl', 'dispatch',
         'hl.dsp.focus({ window = "address:%s" })' % addr],
        capture_output=True, env=env, timeout=30)
    return out.returncode, out.stdout.decode()[:100]


def mean_diff(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


# A. No focus call: two captures 500ms apart.
a1 = grim(ZEN)
time.sleep(0.5)
a2 = grim(ZEN)
print('A no-focus: mean diff a1->a2 = %.3f' % mean_diff(a1, a2))
a1.save('/tmp/f4-probe3-a1.png')
a2.save('/tmp/f4-probe3-a2.png')

# B. Focus the already-focused window, capture immediately, then +500ms.
rc, msg = hypr_focus(ADDR)
print('focus rc=%d msg=%r' % (rc, msg))
b1 = grim(ZEN)
time.sleep(0.5)
b2 = grim(ZEN)
print('B focus: mean diff b1->b2 = %.3f' % mean_diff(b1, b2))
print('B focus: mean diff a2->b1 = %.3f' % mean_diff(a2, b1))
print('B focus: mean diff a2->b2 = %.3f' % mean_diff(a2, b2))
b1.save('/tmp/f4-probe3-b1.png')
b2.save('/tmp/f4-probe3-b2.png')
print('PROBE3 DONE')
