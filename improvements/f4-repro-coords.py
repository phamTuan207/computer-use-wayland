"""F4 reproduction: coordinate chain for the RUN-5 geometry.

Run 5's Zen window is FULL WIDTH 1863 (run 4 was narrowed to 925
by OmaCal). The delegate's begin_batch observes with max_width 960,
so the run-5 observation image is DOWNSCALED to 960x606 while the
run-4 image was unscaled (925x1176). The F3 fix was unit-tested
only against the run-4 geometry (tests/test_zen_pointer.py, fake
meta [2509,914,925,1176], image 925x1176). This test replays the
exact run-5 numbers through the same functions the live path uses:

  rect #msg-input (from run-5.json harvest): x 20, y 228.8667,
  w 340, h 36 -> center (190, 246.8667) viewport CSS px
  viewport origin (absolute): window [2509, 914] + moz [258, 21]
  * factor 1 = [2767, 935]
  batch meta: region [2509, 914, 1863, 1176], image_size [960, 606]
  (1863 -> 960, 1176 * 960 / 1863 = 606.06 -> 606)

Checks: screen point lands inside the field rect; the screen->image
conversion succeeds (no ValueError, the F3 refusal shape); the
image point is inside the image; the image->screen round trip
through cu.image_point returns the same screen point (the
desktop_act preflight map); the round-tripped point is still inside
the field rect (the click the desktop backend would actually send).
"""
import sys

sys.path.insert(0, 'scripts')
import fastpath
import cu

RECT = {'x': 20, 'y': 228.86666870117188, 'width': 340, 'height': 36}
ORIGIN = [2767, 935]
META = {
    'region': [2509, 914, 1863, 1176],
    'image_size': [960, 606],
    'window_bounds': [2509, 914, 1863, 1176],
}

screen = fastpath.dom_rect_to_screen_point(RECT, ORIGIN, 1)
print('screen point:', screen)
assert fastpath.point_in_rect(RECT, screen[0] - ORIGIN[0],
                              screen[1] - ORIGIN[1]), \
    'screen point outside field rect in viewport coords'
print('screen point inside field rect: True')

image = fastpath.screen_point_to_image_point(META, screen[0], screen[1])
print('image point:', image)
iw, ih = META['image_size']
assert 0 <= image[0] < iw and 0 <= image[1] < ih, \
    'image point outside image'
print('image point inside image: True')

back = cu.image_point(META, image[0], image[1])
print('round-trip screen point:', back)
assert abs(back[0] - screen[0]) < 1e-6 and abs(back[1] - screen[1]) < 1e-6, \
    'round trip drifted: %r vs %r' % (back, screen)
print('round trip exact: True')
print('F4-REPRO-COORDS: PASS (coordinate chain is NOT the failure)')
