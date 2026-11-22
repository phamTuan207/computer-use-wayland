#!/usr/bin/env python3
"""P6: measure the vision call (FINAL direction e05fc58, P6 row, ADOPT
with specification fix; CB-7 and CB-10 folded into this ONE measurement
workstream, not a second one).

The problem P6 fixes: capture is 15-30ms and DOM rects 0.030s, but the
model read that locates the target is seconds and timed nowhere. Every
speed claim about the screenshot path is incomplete until that number
is in the logs, and nobody may claim the 10s target is met.

Specification fix (from RTD, accepted by all eight final positions):
the model call happens in the calling agent's loop, outside cu.py, so
the timestamp points and the logging owner must be named here, or P6
gets recorded as done when only capture timing was logged again. The
owner of this logging is THE HARNESS (the code that hands the
observation to the model and reads the located target back), never
cu.py. cu.py logs capture_ms only; it cannot see the model call.

Timestamp points (the contract):
- t_observation_delivered: the moment the observation JPEG (with its
  pinned capture params) is handed to the agent/model loop.
- t_inference_start / t_inference_end: the model call itself, when the
  harness can split it from the surrounding call. When the harness
  cannot split it (opaque client), inference_ms is None and the record
  says so; it is never filled with the whole-call number.
- t_target_returned: the moment the located target (or the miss) comes
  back from the model.
- vision_call_ms = t_target_returned - t_observation_delivered (the
  whole call as the agent experiences it).
- inference_ms = t_inference_end - t_inference_start (the model only).
- The gap vision_call_ms - inference_ms is harness overhead (prompt
  build, transport, parse). All three are recorded; no one of them is
  quoted as "the vision time" alone.

Error class per miss (P6b). A miss is one of exactly two classes:
- "wrong_target": the model read the image and located the WRONG
  element in it (G30 is class (a)). Evidence: the returned point
  lands on a different element than the intended one.
- "wrong_frame": orchestration fed the model the WRONG frame or scope
  (J40 and the after-image trap are class (b)). Evidence: the returned
  point is right for the frame it was given, but the frame was stale,
  screen-scoped when a window was meant, or otherwise not the frame
  the batch acts on.
- "unknown" when the evidence does not decide between the two. A miss
  with no evidence is recorded unknown, never guessed into a class.

Capture parameters (P6c): every record pins max_width, jpeg_quality,
and jpeg_subsampling with the measurement. The pinned values are
observe/act-now max_width 960 (CB-3 uniformity), JPEG q90, subsampling
0 (4:4:4). See cu.CAPTURE_MAX_WIDTH and cu.CAPTURE_JPEG_QUALITY.
A record whose capture params differ from the pinned set must say so;
comparing vision times across different capture params is meaningless.

CB-7 (folded in): the act-now envelope (first_action.py) records
dispatch_ms (VM send + SSH connect + shell startup, from the order
wall time the VM passes in) separately from laptop work, and
target_breached compares FIRST-pointer time against the 30 s
threshold, not whole-batch time. This module does not measure
dispatch; the VM-side caller owns that number.
CB-10 (folded in): overlay flicker vs model think-time are measured
separately, per phase. Think time is THIS module (inference_ms per
vision call). Overlay acquire time is the act-now envelope phase_ms
(first_action.py). The flicker itself is UNPROBED until the LIQUID
flicker probe runs (load the plugin, reproduce the flicker, count
repaints); that probe belongs to the A4 worker and is a precondition
for the session-level pill judgment. Do not quote a flicker number
from this module: it measures think time, not flicker.

Usage (harness):
    from vision_measure import VisionCallTimer, CAPTURE_PARAMS
    timer = VisionCallTimer(metrics_path)
    timer.mark_observation_delivered(meta)  # meta carries capture params
    timer.mark_inference_start()
    ... model call ...
    timer.mark_inference_end()
    call = timer.mark_target_returned(ok=True)  # or ok=False with
        # error_class="wrong_target" / "wrong_frame" / "unknown"
    # call is the JSON-able record, also appended to metrics_path.
"""
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:  # pragma: no cover
    from datetime import timezone
    TZ = timezone.utc

# Pinned capture parameters (P6c). One max_width for all captures
# (CB-3 uniformity); JPEG q90 4:4:4 (cu.save_observation).
CAPTURE_MAX_WIDTH = 960
CAPTURE_JPEG_QUALITY = 90
CAPTURE_JPEG_SUBSAMPLING = 0  # 4:4:4, no chroma subsampling
CAPTURE_PARAMS = {
    "max_width": CAPTURE_MAX_WIDTH,
    "jpeg_quality": CAPTURE_JPEG_QUALITY,
    "jpeg_subsampling": CAPTURE_JPEG_SUBSAMPLING,
}

ERROR_CLASSES = ("wrong_target", "wrong_frame", "unknown")


def wall_text(now=None):
    moment = now or datetime.now(TZ)
    return moment.strftime("%Y-%m-%d %H:%M:%S %Z")


def classify_miss(returned_point, intended_point, frame_scope,
                  acted_scope, frame_fresh=True):
    """Classify a vision miss into P6b error classes from evidence.

    returned_point / intended_point are (x, y) image points (or None
    when the model returned no point). frame_scope is the scope of the
    frame the model was given ('window' / 'screen'); acted_scope is
    the scope the batch acts on. frame_fresh is False when the frame
    was stale (superseded by a layout change, or an after-image reused
    as an observation).

    Returns "wrong_frame" when the frame itself was wrong (stale, or
    scope mismatch between the given frame and the acted scope):
    the point can be right for the frame and still miss, so the frame
    is the fault. Returns "wrong_target" when the frame was right and
    fresh but the returned point differs from the intended point.
    Returns "unknown" when there is no returned point and no frame
    fault to blame, or when the inputs do not decide it.
    """
    if not frame_fresh:
        return "wrong_frame"
    if frame_scope is not None and acted_scope is not None:
        if frame_scope != acted_scope:
            return "wrong_frame"
    if returned_point is None or intended_point is None:
        return "unknown"
    try:
        rx, ry = float(returned_point[0]), float(returned_point[1])
        ix, iy = float(intended_point[0]), float(intended_point[1])
    except (TypeError, ValueError, IndexError):
        return "unknown"
    if (rx, ry) == (ix, iy):
        return "unknown"
    return "wrong_target"


class VisionCallTimer:
    """One vision call, timed by the harness that owns the model call.

    clock defaults to time.monotonic (seconds). Pass a fake clock in
    tests. metrics_path may be None: the record is then returned but
    not written anywhere. Writes are fail-open: a write failure is
    reported on stderr once and never raises into the harness.
    """

    def __init__(self, metrics_path=None, *, clock=time.monotonic,
                 run_id=None):
        self.metrics_path = Path(metrics_path) if metrics_path else None
        self._clock = clock
        self.run_id = run_id
        self._delivered = None
        self._inference_start = None
        self._inference_end = None
        self._capture_params = dict(CAPTURE_PARAMS)
        self._write_failed = False

    def mark_observation_delivered(self, meta=None):
        """t_observation_delivered. meta is the observation meta dict;
        its capture params (max_width, image_format) are pinned into
        the record when present, so a record always names the capture
        it measured. Returns the timestamp (clock seconds)."""
        self._delivered = self._clock()
        if isinstance(meta, dict):
            params = dict(CAPTURE_PARAMS)
            if isinstance(meta.get("max_width"), int):
                params["max_width"] = meta["max_width"]
            if meta.get("image_format"):
                params["image_format"] = meta["image_format"]
            if isinstance(meta.get("capture_ms"), (int, float)):
                params["capture_ms"] = meta["capture_ms"]
            self._capture_params = params
        return self._delivered

    def mark_inference_start(self):
        self._inference_start = self._clock()
        return self._inference_start

    def mark_inference_end(self):
        self._inference_end = self._clock()
        return self._inference_end

    def mark_target_returned(self, ok=True, error_class=None,
                             target=None):
        """t_target_returned. Returns the record dict and appends it
        to metrics_path when set. ok=False needs an error_class; a
        missing class is recorded "unknown", never guessed. target is
        the returned point or element id when known (no page text)."""
        if self._delivered is None:
            raise ValueError(
                "mark_observation_delivered must run before "
                "mark_target_returned: a vision call with no delivery "
                "timestamp has no vision_call_ms")
        t_end = self._clock()
        vision_call_ms = round((t_end - self._delivered) * 1000, 3)
        if (self._inference_start is not None
                and self._inference_end is not None):
            inference_ms = round(
                (self._inference_end - self._inference_start) * 1000, 3)
        else:
            inference_ms = None
        if ok:
            error_class = None
        else:
            if error_class not in ERROR_CLASSES:
                error_class = "unknown"
        record = {
            "event": "vision_call",
            "wall": wall_text(),
            "run": self.run_id,
            "vision_call_ms": vision_call_ms,
            "inference_ms": inference_ms,
            "inference_split": (
                "measured" if inference_ms is not None
                else "not_split: harness could not separate the model "
                "call from the surrounding call"),
            "capture_params": self._capture_params,
            "ok": bool(ok),
            "error_class": error_class,
            "target": target,
        }
        if self.metrics_path is not None and not self._write_failed:
            try:
                self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
                line = (json.dumps(record, sort_keys=True,
                                  ensure_ascii=False, allow_nan=False)
                        + "\n")
                fd = os.open(str(self.metrics_path),
                             os.O_WRONLY | os.O_APPEND | os.O_CREAT,
                             0o600)
                try:
                    os.fchmod(fd, 0o600)
                    os.write(fd, line.encode("utf-8"))
                finally:
                    os.close(fd)
            except Exception as exc:  # fail-open, report once
                self._write_failed = True
                print(f"[vision] metrics write failed: {exc}",
                      file=sys.stderr)
        return record
