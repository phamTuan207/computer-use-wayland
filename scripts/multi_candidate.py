"""Multi-candidate grounding with tiny-crop verification (Pick 3, M5).

Track 2 prototype, branch speed-swarm. Opt-in only:
``CU_MULTI_CANDIDATE=1`` enables it, anything else (including unset)
leaves it off. Default OFF, so it coexists with the other picks and is
measured alone.

Idea (speed-swarm-prototype-plan.md, Pick 3): one full-frame vision call
returns the top 3 candidate points for a target, each with a confidence.
Candidates are verified in order with a fresh native 90x90 to 200x200
crop (measured 53 to 58 ms local, 2.4 to 8 KB per crop) instead of
issuing a new full-frame observe per miss. The click uses coordinates
from the fresh crop observation only, never from the full-frame call
alone. If all three crops disagree, fall back to a full frame.

Rules carried from the prior art and the landed Step 2 design:
- Crop context rule (M34): every crop includes at least one adjacent
  control for disambiguation, and for row targets the column headings
  plus one full row on each side. Read-then-act tasks use the full
  frame, not a crop.
- Zoom is gated on small or uncertain targets only (RegionFocus,
  ScreenSeeker, ZoomClick): a zoom round costs an extra vision call,
  so it runs only when the target is small (< 32 px) or the
  confidence is low (< 0.7). Never the default.
- On a failed grounding, the failed point is stamped on the next
  observation image (RegionFocus image-as-map: 43.2 vs 37.2 for text
  history) so the model does not revisit the same wrong point.
- Safety invariants are untouched: this module never clicks, never
  moves the pointer, never types, never touches ownership, leases,
  cancellation, or the broker. It only parses candidates, computes
  crop rectangles, stamps images, and verifies crop text. The act
  path (scripts/cu.py desktop_act) still enforces the fresh
  observation, the pointer miss check, the screen-changed refusal,
  and the 90 s observation expiry. A stale candidate is re-grounded,
  never trusted.

This module is standalone on purpose: it does not import cu.py or any
other pick's module, so the four picks on branch speed-swarm cannot
break each other at import time.
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass, field

FLAG_ENV = "CU_MULTI_CANDIDATE"

# Crop bounds from the plan: 90x90 to 200x200 native crops.
CROP_MIN = 90
CROP_MAX = 200
# Default crop side when nothing else is known. Large enough to hold the
# target plus one neighbouring control (M34 disambiguation rule).
CROP_DEFAULT = 140
# Zoom gate: zoom only for small targets or low confidence.
SMALL_TARGET_PX = 32
LOW_CONFIDENCE = 0.7
# Two candidates closer than this (px, global) are the same guess.
DEDUPE_PX = 8
MAX_CANDIDATES = 3


def enabled():
    """True only when CU_MULTI_CANDIDATE=1. Default off."""
    return os.environ.get(FLAG_ENV) == "1"


@dataclass
class Candidate:
    """One grounding guess, in image-frame pixels.

    Convert to global desktop pixels with image_to_global before any
    global use. See parse_candidates for the frame rule.
    """

    x: int
    y: int
    confidence: float = 0.0
    label: str = ""

    def as_dict(self):
        return {"x": self.x, "y": self.y,
                "confidence": round(self.confidence, 3),
                "label": self.label}


@dataclass
class GroundingAttempt:
    """One logged grounding attempt, for the measurement records."""

    target: str
    candidates: list = field(default_factory=list)
    verified_index: int = -1
    misclicks: int = 0
    crops_used: int = 0
    fell_back_to_full_frame: bool = False

    def as_dict(self):
        return {
            "target": self.target,
            "candidates": [c.as_dict() for c in self.candidates],
            "verified_index": self.verified_index,
            "misclicks": self.misclicks,
            "crops_used": self.crops_used,
            "fell_back_to_full_frame": self.fell_back_to_full_frame,
        }


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_candidates(text, image_width, image_height):
    """Parse the top-3 candidates out of one model grounding reply.

    Accepted shapes (coordinates in the 0-1000 vision scale, as the
    model returns them):
      {"candidates": [{"x":..,"y":..,"confidence":..,"label":".."}, ...]}
      {"x":..,"y":..,"confidence":..}  (legacy single candidate)
    Returns (candidates, errors): candidates sorted by confidence
    descending, capped at 3, near-duplicates merged, out-of-range
    points dropped with an error note each. Coordinates are returned
    in IMAGE pixels: the 0-1000 scale is a fraction of the shown
    frame, so for a full-window observation image_width/height are
    the TRUE window size and the returned points are window-relative;
    add the window origin (see image_to_global) to get global desktop
    pixels. For a full-screen observation pass the monitor size and
    the points are already global up to the monitor origin. Never
    raises on model garbage: a reply with no usable point returns
    ([], [reason]).
    """
    errors = []
    candidates = []
    if not isinstance(text, str) or not text.strip():
        return [], ["empty reply"]
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match is None:
        return [], ["no JSON object in reply"]
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        return [], ["unparsable JSON: %s" % exc]
    if not isinstance(data, dict):
        return [], ["top level JSON is not an object"]
    raw = data.get("candidates")
    if raw is None and _is_number(data.get("x")) and _is_number(data.get("y")):
        raw = [data]
    if not isinstance(raw, list):
        return [], ["no candidates list and no single x/y pair"]
    for item in raw:
        if not isinstance(item, dict):
            errors.append("candidate is not an object, skipped")
            continue
        x = item.get("x")
        y = item.get("y")
        if not _is_number(x) or not _is_number(y):
            errors.append("candidate without numeric x/y, skipped")
            continue
        if not 0 <= x <= 1000 or not 0 <= y <= 1000:
            errors.append("candidate (%s, %s) outside 0-1000, skipped" % (x, y))
            continue
        conf = item.get("confidence", 0.0)
        if not _is_number(conf):
            conf = 0.0
        conf = max(0.0, min(1.0, float(conf)))
        label = item.get("label", "")
        if not isinstance(label, str):
            label = str(label)
        candidates.append(Candidate(
            x=int(round(x / 1000.0 * image_width)),
            y=int(round(y / 1000.0 * image_height)),
            confidence=conf, label=label[:120]))
    # Highest confidence first, merge near-duplicates (keep the more
    # confident one), cap at 3.
    candidates.sort(key=lambda c: c.confidence, reverse=True)
    merged = []
    for cand in candidates:
        if any(abs(cand.x - kept.x) <= DEDUPE_PX
               and abs(cand.y - kept.y) <= DEDUPE_PX for kept in merged):
            errors.append("duplicate candidate near (%d, %d), merged"
                          % (cand.x, cand.y))
            continue
        merged.append(cand)
        if len(merged) >= MAX_CANDIDATES:
            break
    return merged, errors


def image_to_global(x, y, origin):
    """Map an image-frame point to global desktop pixels.

    origin is [ox, oy], the global position of the shown frame's top
    left corner: the window origin for a window observation, the
    monitor origin for a screen observation. The 0-1000 vision scale
    is a fraction of the frame, so the parsed point is frame-relative
    and MUST go through here before any global use (crop math, click
    coordinates). Skipping this step double-counts the origin.
    """
    return int(x) + int(origin[0]), int(y) + int(origin[1])


def zoom_needed(target_size_px, confidence):
    """Zoom gate: True only for small or uncertain targets.

    A zoom round costs an extra vision call, so it runs only when the
    target is small (< 32 px on its longest side) or the best
    candidate confidence is low (< 0.7). Anything else uses the plain
    crop. target_size_px None means unknown size, which does not by
    itself justify a zoom.
    """
    if target_size_px is not None and target_size_px < SMALL_TARGET_PX:
        return True
    if confidence is not None and confidence < LOW_CONFIDENCE:
        return True
    return False


def crop_for_candidate(x, y, window_bounds, target_size_px=None,
                       confidence=None):
    """Crop rectangle (global px) centred on a candidate point.

    window_bounds is [x, y, width, height] of the window the point
    belongs to. The crop is centred on the point, sized 90 to 200 px
    per side: 140 px by default, 200 px when the zoom gate fires (small
    or uncertain target, so the model gets more context), never below
    90 px (M34: the crop must still show a neighbouring control).
    The rect is clamped inside the window bounds and, if the window is
    smaller than the crop, shrunk to the window. Returns
    [cx, cy, cw, ch] plus the point in crop-image coordinates
    (px, py), for the --crop argument of cu.py observe.
    """
    wx, wy, ww, wh = (int(v) for v in window_bounds)
    side = CROP_MAX if zoom_needed(target_size_px, confidence) else CROP_DEFAULT
    side = max(CROP_MIN, min(CROP_MAX, side))
    side = min(side, ww, wh)
    half = side // 2
    cx = min(max(int(x) - half, wx), wx + ww - side)
    cy = min(max(int(y) - half, wy), wy + wh - side)
    px = int(x) - cx
    py = int(y) - cy
    return [cx, cy, side, side], (px, py)


def to_window_relative(crop, window_bounds):
    """Convert a global crop rect to window-relative --crop coords.

    crop_for_candidate returns GLOBAL desktop pixels, but cu.py
    observe --crop takes offsets from the WINDOW origin (it adds the
    window origin itself: region = [wb[0]+x, wb[1]+y, w, h]). Pass
    the output of this helper, not the global rect, to
    crop_observe_args. window_bounds is [x, y, width, height].
    """
    wx, wy = int(window_bounds[0]), int(window_bounds[1])
    return [int(crop[0]) - wx, int(crop[1]) - wy,
            int(crop[2]), int(crop[3])]


def crop_observe_args(address, crop, max_width=960):
    """Broker observe envelope args for one verification crop.

    crop MUST be window-relative (see to_window_relative): cu.py
    observe --crop takes (x, y, w, h) as offsets from the window
    origin, not global pixels. Matches cu.py observe --window --crop
    (nargs=4 ints) --max-width. max_width defaults to 960, the
    profile default; a crop is never wider than 200 px, so no
    downscale ever applies to it.
    """
    return ["observe", "--window", address, "--crop",
            str(crop[0]), str(crop[1]), str(crop[2]), str(crop[3]),
            "--max-width", str(max_width)]


def stamp_failed_points(image_path, points, out_path):
    """Stamp failed grounding points onto a copy of an observation.

    points is a list of (x, y) in image pixels. Each gets a red ring,
    a cross, and its 1-based index, drawn with PIL only. The stamped
    copy is the retry observation (RegionFocus image-as-map), so the
    model sees where it already failed instead of only reading about
    it in text. Returns out_path. Raises FileNotFoundError for a
    missing source image; the caller decides the fallback.
    """
    from PIL import Image, ImageDraw

    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    for index, (x, y) in enumerate(points, start=1):
        x = int(x)
        y = int(y)
        radius = 14
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                     outline=(255, 0, 0), width=3)
        draw.line([x - radius - 4, y, x + radius + 4, y],
                  fill=(255, 0, 0), width=2)
        draw.line([x, y - radius - 4, x, y + radius + 4],
                  fill=(255, 0, 0), width=2)
        draw.text((x + radius + 2, y - radius), str(index),
                  fill=(255, 0, 0))
    image.save(out_path, format="PNG", compress_level=1)
    return out_path


def verify_crop_text(crop_image_path, expected_text):
    """Check expected text is present in a verification crop, via OCR.

    The deterministic local verifier for text targets (Step 2 style):
    run tesseract on the crop PNG and look for the expected string.
    Returns (ok, ocr_text): ok True when the expected text (case
    insensitive, whitespace collapsed) appears, False when the crop
    was read and it does not, and (None, ocr_text) when tesseract is
    missing so no local verdict is possible. Icon targets have no
    text to check: callers must pass expected_text None and treat the
    result as unverifiable locally, leaving the verdict to the model
    reading the crop.
    """
    if expected_text is None:
        return None, ""
    try:
        proc = subprocess.run(
            ["tesseract", crop_image_path, "stdout"],
            capture_output=True, text=True, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None, ""
    ocr_text = proc.stdout or ""
    norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()
    return norm(expected_text) in norm(ocr_text), ocr_text


MULTI_CANDIDATE_PROMPT = """\
Multi-candidate grounding (Pick 3, flag CU_MULTI_CANDIDATE=1):
- In ONE full-frame call, return your top 3 candidate points for the
  target, each with a confidence 0-1 and a short label, as JSON:
  {"candidates": [{"x": 0-1000, "y": 0-1000, "confidence": 0.9,
  "label": "File menu"}, ...]}. Rank honestly by confidence.
- Each candidate is then verified with a fresh native 90x90 to 200x200
  crop centred on it. Click ONLY the first candidate whose crop shows
  the target, using coordinates from that fresh crop observation.
- Never click from the full-frame call alone. If all 3 crops disagree,
  take a fresh full-frame observation and re-ground.
- Zoom (a larger crop) only for small targets (under 32 px) or low
  confidence (under 0.7). Never zoom by default.
- On a retry after a failed grounding, the failed points are stamped
  in red on the observation image. Do not return a point within 8 px
  of a stamped point.
- Read-then-act tasks (the answer lives in the relationship between
  columns, not one cell) use the full frame, not a crop.
"""


def main(argv=None):
    """Small CLI so the executor loop can use this module directly.

    ground: parse a model reply, print crop rects for each candidate.
      multi_candidate.py ground --image-w 1096 --image-h 581 \
        --window 2509 1509 1096 581 --origin 2509 1509 \
        --reply '{"candidates": [...]}'
      --image-w/--image-h are the TRUE size of the shown frame (the
      window size for a window observation); --origin is the frame's
      global top-left corner (the window origin). The CLI converts
      frame points to global pixels before cropping.
    stamp: stamp failed points onto an observation copy.
      multi_candidate.py stamp --image in.png --out out.png \
        --points '100,200 300,400'
    verify: OCR-check expected text in a crop.
      multi_candidate.py verify --image crop.png --text 'File'
    prompt: print the executor prompt text.
    """
    import argparse

    parser = argparse.ArgumentParser(prog="multi_candidate")
    sub = parser.add_subparsers(dest="command", required=True)
    ground = sub.add_parser("ground")
    ground.add_argument("--image-w", type=int, required=True)
    ground.add_argument("--image-h", type=int, required=True)
    ground.add_argument("--window", nargs=4, type=int, required=True)
    ground.add_argument("--origin", nargs=2, type=int, default=[0, 0])
    ground.add_argument("--reply", required=True)
    ground.add_argument("--target-size", type=int, default=None)
    stamp = sub.add_parser("stamp")
    stamp.add_argument("--image", required=True)
    stamp.add_argument("--out", required=True)
    stamp.add_argument("--points", required=True,
                       help="space separated x,y pairs")
    verify = sub.add_parser("verify")
    verify.add_argument("--image", required=True)
    verify.add_argument("--text", required=True)
    sub.add_parser("prompt")
    ns = parser.parse_args(argv)
    if ns.command == "ground":
        if not enabled():
            print(json.dumps({"ok": False,
                              "error": "pick3 is off; set CU_MULTI_CANDIDATE=1"}))
            return 1
        candidates, errors = parse_candidates(ns.reply, ns.image_w, ns.image_h)
        out = {"ok": True, "candidates": [], "errors": errors}
        for cand in candidates:
            gx, gy = image_to_global(cand.x, cand.y, ns.origin)
            crop, in_crop = crop_for_candidate(
                gx, gy, ns.window,
                target_size_px=ns.target_size, confidence=cand.confidence)
            out["candidates"].append({
                "candidate": cand.as_dict(),
                "global": [gx, gy],
                "crop": crop,
                "crop_window": to_window_relative(crop, ns.window),
                "point_in_crop": list(in_crop),
                "zoom": zoom_needed(ns.target_size, cand.confidence)})
        print(json.dumps(out))
        return 0
    if ns.command == "stamp":
        points = []
        for pair in ns.points.split():
            px, py = pair.split(",")
            points.append((int(px), int(py)))
        stamp_failed_points(ns.image, points, ns.out)
        print(json.dumps({"ok": True, "out": ns.out,
                          "points": len(points)}))
        return 0
    if ns.command == "verify":
        ok, text = verify_crop_text(ns.image, ns.text)
        print(json.dumps({"ok": ok, "ocr_text": text[:500]}))
        return 0 if ok else 1
    print(MULTI_CANDIDATE_PROMPT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
