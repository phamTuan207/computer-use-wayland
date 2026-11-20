#!/usr/bin/env python3
"""E2 calibration analysis: vision estimates vs DOM ground truth.

Inputs:
  --estimates JSON list of {id, ix, iy} in observation image pixels.
  --truth     JSON from tests/bidi_truth.mjs (value: innerX/innerY + targets).
  --observation JSON from cu.py observe (image_size, region, window_bounds).
  --hits-out  JSONL path for per-attempt records (hit_rate.py format).
  --report    JSON path for the summary report.
  --case-id   case id prefix, e2-vision (estimates only) or e2-click (real clicks).
  --actual-hits JSON (optional) from bidi window.__hits after real clicks;
              when given, hit is decided by the element that received the
              click event, not by geometry alone.

Geometry: screen = region_origin + image_xy * region_size / image_size
(the same linear map as scripts/cu.py image_point). Truth screen =
(mozInnerScreenX + rect.cx, mozInnerScreenY + rect.cy).
No em dashes in output.
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hit_rate import append_attempt


def image_point(meta, x, y):
    iw, ih = meta['image_size']
    rx, ry, rw, rh = meta['region']
    if not (0 <= x < iw and 0 <= y < ih):
        raise ValueError('point outside observed image: %s,%s' % (x, y))
    return rx + x * rw / iw, ry + y * rh / ih


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else None


def main(argv=None):
    parser = argparse.ArgumentParser(description='E2 calibration analysis.')
    parser.add_argument('--estimates', required=True, type=Path)
    parser.add_argument('--truth', required=True, type=Path)
    parser.add_argument('--observation', required=True, type=Path)
    parser.add_argument('--hits-out', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--case-id', required=True)
    parser.add_argument('--actual-hits', type=Path, default=None)
    args = parser.parse_args(argv)

    estimates = json.loads(args.estimates.read_text(encoding='utf-8'))
    truth = json.loads(args.truth.read_text(encoding='utf-8'))['value']
    meta = json.loads(args.observation.read_text(encoding='utf-8'))
    actual_hits = None
    if args.actual_hits:
        actual_hits = json.loads(args.actual_hits.read_text(encoding='utf-8'))['value']
        if isinstance(actual_hits, dict):
            actual_hits = actual_hits.get('hits')

    targets = {t['id']: t for t in truth['targets']}
    inner_x = truth['innerX']
    inner_y = truth['innerY']

    # Event-received truth: first hit per target id from the page log.
    received = {}
    if actual_hits:
        for h in actual_hits:
            received.setdefault(h['id'], h)

    rows = []
    for est in estimates:
        tid = est['id']
        t = targets[tid]
        sx, sy = image_point(meta, est['ix'], est['iy'])
        tx = inner_x + t['cx']
        ty = inner_y + t['cy']
        dx = sx - tx
        dy = sy - ty
        # Geometric hit: estimated screen point inside the truth rect.
        geo_hit = (inner_x + t['x'] <= sx <= inner_x + t['x'] + t['w'] and
                   inner_y + t['y'] <= sy <= inner_y + t['y'] + t['h'])
        # Which target rect (if any) contains the estimated point.
        actual = None
        for other_id, o in targets.items():
            if (inner_x + o['x'] <= sx <= inner_x + o['x'] + o['w'] and
                    inner_y + o['y'] <= sy <= inner_y + o['y'] + o['h']):
                actual = other_id
                break
        # Event truth wins when available: the element that got the click.
        if received:
            hit = tid in received
            actual = tid if hit else None
        else:
            hit = geo_hit
        if hit:
            issue = None
        elif actual is not None and actual != tid:
            issue = 'wrong_target'
        else:
            issue = 'visual_grounding'
        append_attempt(args.hits_out, case_id=args.case_id, attempt=len(rows) + 1,
                       backend='desktop', intended_target=tid,
                       actual_target=actual, issue_group=issue)
        rows.append({
            'id': tid, 'ix': est['ix'], 'iy': est['iy'],
            'screen_x': round(sx, 1), 'screen_y': round(sy, 1),
            'truth_x': round(tx, 1), 'truth_y': round(ty, 1),
            'dx': round(dx, 1), 'dy': round(dy, 1),
            'abs_err': round(math.hypot(dx, dy), 1),
            'hit': hit, 'actual_target': actual, 'issue': issue,
            'target_w': t['w'], 'target_h': t['h'],
        })

    n = len(rows)
    hits = sum(1 for r in rows if r['hit'])
    dxs = [r['dx'] for r in rows]
    dys = [r['dy'] for r in rows]
    grid_a = [r for r in rows if r['id'].startswith('T')]
    grid_b = [r for r in rows if r['id'].startswith('R')]

    def split_stats(sub):
        if not sub:
            return None
        h = sum(1 for r in sub if r['hit'])
        return {'n': len(sub), 'hits': h, 'hit_rate': h / len(sub),
                'mean_dx': round(sum(r['dx'] for r in sub) / len(sub), 1),
                'mean_dy': round(sum(r['dy'] for r in sub) / len(sub), 1),
                'mean_abs_err': round(sum(r['abs_err'] for r in sub) / len(sub), 1)}

    report = {
        'case_id': args.case_id,
        'n': n, 'hits': hits,
        'hit_rate': hits / n if n else None,
        'mean_dx': round(sum(dxs) / n, 1) if n else None,
        'mean_dy': round(sum(dys) / n, 1) if n else None,
        'std_dx': round(math.sqrt(sum((d - sum(dxs) / n) ** 2 for d in dxs) / n), 1) if n else None,
        'std_dy': round(math.sqrt(sum((d - sum(dys) / n) ** 2 for d in dys) / n), 1) if n else None,
        'mean_abs_err': round(sum(r['abs_err'] for r in rows) / n, 1) if n else None,
        'max_abs_err': max((r['abs_err'] for r in rows), default=None),
        'corr_err_vs_x': pearson([r['truth_x'] for r in rows], [r['dx'] for r in rows]),
        'corr_err_vs_y': pearson([r['truth_y'] for r in rows], [r['dy'] for r in rows]),
        'grid_a_medium_buttons': split_stats(grid_a),
        'grid_b_small_links': split_stats(grid_b),
        'monitor': {'name': meta.get('monitor'), 'scale': meta.get('monitor_scale'),
                    'transform': meta.get('monitor_transform')},
        'image_size': meta.get('image_size'),
        'window_bounds': meta.get('window_bounds'),
        'dpr': truth.get('dpr'),
        'viewport': [truth.get('vw'), truth.get('vh')],
        'rows': rows,
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
