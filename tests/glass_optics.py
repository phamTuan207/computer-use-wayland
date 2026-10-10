#!/usr/bin/env python3
"""Numerical optics check for the synthetic 1280x720 liquid fixture.

Optional diagnostic, not a unit test: it needs PIL and numpy, plus three captures
produced outside this repository. It measures how far a forced-offset capture's
row means shift relative to the offset-free baseline.

    python3 tests/glass_optics.py baseline.png forced8.png forced16.png
    python3 tests/glass_optics.py --selfcheck

Exit code 0 when every row reaches the correlation floor and its expected lag,
1 when a row disagrees, 2 on bad arguments or unreadable images.

Sign convention: a capture forced to sample `+k` pixels away shows content moved
`k` pixels the other way, so forced 8 reports lag -8. Because the fixture is
periodic at 32 px, forced 16 is ambiguous: lag -16 and lag +16 describe the same
shift, so only the magnitude is asserted.
"""
import json
import sys

import numpy
from PIL import Image

WIDTH, HEIGHT = 1280, 720
ROWS = (20, 44, 47, 50)
X0, X1 = 540, 740          # measured band; the x >= 848 warning area is excluded
FIRST, LAST = 20, 180      # interior window used by the correlation
DETREND = 33               # moving-average window; subtracted, not substituted
CORRELATION_FLOOR = 0.85
EXPECTED = {8: -8, 16: -16}


def moving_average(values, width):
    padded = numpy.pad(values, (width // 2, width // 2), mode='edge')
    return numpy.convolve(padded, numpy.ones(width) / width, mode='valid')


def load(path):
    with Image.open(path) as image:
        rgb = numpy.asarray(image.convert('RGB'), dtype=numpy.float64)
    if rgb.shape[:2] != (HEIGHT, WIDTH):
        raise ValueError('{} is {}x{}, expected {}x{}'
                         .format(path, rgb.shape[1], rgb.shape[0], WIDTH, HEIGHT))
    return rgb


def row_mean(rgb, y):
    """Mean over RGB of one row inside the measured band, detrended by subtraction."""
    values = rgb[y, X0:X1].mean(axis=1)
    return values - moving_average(values, DETREND)


def pearson(a, b):
    a = a - a.mean()
    b = b - b.mean()
    denominator = numpy.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / denominator) if denominator else 0.0


def best_lag(base, other):
    best = (None, -2.0)
    for lag in range(-20, 21):
        score = pearson(base[FIRST:LAST], other[FIRST + lag:LAST + lag])
        if score > best[1]:
            best = (lag, score)
    return best


def matches(offset, lag):
    if offset == 16:      # periodic-32 fixture: -16 and +16 are the same shift
        return abs(abs(lag) - 16) <= 1
    return abs(lag - EXPECTED[offset]) <= 1


def measure(baseline, forced, offset):
    base_rgb, forced_rgb = load(baseline), load(forced)
    rows = []
    for y in ROWS:
        lag, score = best_lag(row_mean(base_rgb, y), row_mean(forced_rgb, y))
        # Threshold on the raw score; rounding is for display only.
        rows.append({'y': y, 'lag': lag, 'corr': round(score, 4),
                     'ok': score >= CORRELATION_FLOOR and matches(offset, lag)})
    return {'forced': offset, 'expected_lag': EXPECTED[offset], 'rows': rows,
            'ok': all(row['ok'] for row in rows)}


def selfcheck():
    """Positive controls on synthetic arrays only: a known shift is recovered."""
    x = numpy.arange(240)
    signal = sum(numpy.sin(x / (3 + k)) * (k + 1) for k in range(5))
    signal -= signal.mean()
    # roll(-8) moves the content 8 to the left, which is what forced 8 produces.
    for offset, shifted in ((8, numpy.roll(signal, -8)), (16, numpy.roll(signal, -16))):
        lag, score = best_lag(signal, shifted)
        assert matches(offset, lag), (offset, lag)
        assert score > 0.99, (offset, score)
    assert pearson(signal, signal) > 0.999


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ['--selfcheck']:
        selfcheck()
        print(json.dumps({'selfcheck': 'ok'}))
        return 0
    if len(args) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        baseline, forced8, forced16 = args
        report = {'fixture': {'width': WIDTH, 'height': HEIGHT}, 'band': [X0, X1],
                  'rows': list(ROWS), 'corr_floor': CORRELATION_FLOOR,
                  'forced16_note': 'periodic 32px fixture: -16 and +16 are the same shift',
                  'runs': [measure(baseline, forced8, 8), measure(baseline, forced16, 16)]}
    except (OSError, ValueError) as error:
        print('glass_optics: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(report, separators=(',', ':')))
    return 0 if all(run['ok'] for run in report['runs']) else 1


if __name__ == '__main__':
    sys.exit(main())