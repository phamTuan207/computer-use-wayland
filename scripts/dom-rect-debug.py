#!/usr/bin/env python3
"""DOM-rect debug artifact (I16, DOM version).

Draws element rects from an existing DOM snapshot/harvest JSON
onto a screenshot, producing an annotated PNG for eyeballing
grounding errors (wrong rect, wrong scale, wrong origin).

Inputs are existing outputs only: a cdp.mjs observe snapshot
({"elements": [{"ref", "rect": {x,y,width,height}, ...}]}) or a
harvest ({"items": {selector: {"rect": {...}}}}), plus a PNG
screenshot of the same surface.

Usage:
  python3 scripts/dom-rect-debug.py --snapshot snap.json \
      --screenshot shot.png [--out annotated.png] \
      [--scale 1.0] [--origin-x 0] [--origin-y 0]

Rects are CSS px relative to the page viewport. --scale maps
them to screenshot px (device pixel ratio / capture scale);
--origin-x/y is the viewport's top-left inside the screenshot
(window position for full-screen captures).

Machine-layer rule: annotated screenshots of real sessions are
local debug artifacts. Never commit them; this script and its
synthetic tests are the only repo parts.
"""
import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def rects_from_snapshot(data):
    """Yield (label, rect) from either supported JSON shape."""
    if isinstance(data.get("elements"), list):
        for el in data["elements"]:
            if not isinstance(el, dict):
                continue
            rect = el.get("rect")
            if isinstance(rect, dict):
                yield str(el.get("ref", "?")), rect
    items = data.get("items")
    if isinstance(items, dict):
        for sel, item in items.items():
            if isinstance(item, dict) and isinstance(item.get("rect"), dict):
                yield sel, item["rect"]


def annotate(snapshot_path, screenshot_path, out_path,
             scale=1.0, origin_x=0, origin_y=0):
    data = json.loads(Path(snapshot_path).read_text())
    img = Image.open(screenshot_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    drawn = 0
    skipped = 0
    for label, rect in rects_from_snapshot(data):
        try:
            x = origin_x + float(rect["x"]) * scale
            y = origin_y + float(rect["y"]) * scale
            w = float(rect["width"]) * scale
            h = float(rect["height"]) * scale
        except (KeyError, TypeError, ValueError):
            skipped += 1
            continue
        if w <= 0 or h <= 0:
            skipped += 1
            continue
        if not all(math.isfinite(value) for value in (x, y, w, h)):
            skipped += 1
            continue
        draw.rectangle([x, y, x + w, y + h], outline=(255, 0, 0), width=2)
        draw.text((x + 2, max(0, y - 12)), label, fill=(255, 0, 0))
        drawn += 1
    img.save(out_path)
    return {"drawn": drawn, "skipped": skipped, "output": str(out_path)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--screenshot", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--origin-x", type=float, default=0)
    ap.add_argument("--origin-y", type=float, default=0)
    args = ap.parse_args(argv)
    out = args.out or (args.screenshot + ".rects.png")
    if Path(out).resolve() == Path(args.screenshot).resolve():
        ap.error("--out must not be the same file as --screenshot")
    result = annotate(args.snapshot, args.screenshot, out,
                      scale=args.scale, origin_x=args.origin_x,
                      origin_y=args.origin_y)
    print(json.dumps(result))
    return 0 if result["drawn"] else 1


if __name__ == "__main__":
    sys.exit(main())
