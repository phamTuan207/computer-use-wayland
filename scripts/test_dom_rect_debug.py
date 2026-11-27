#!/usr/bin/env python3
"""Tests for dom-rect-debug.py (I16) on synthetic inputs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "dom_rect_debug", Path(__file__).resolve().parent / "dom-rect-debug.py")
drd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drd)


class DomRectDebugTests(unittest.TestCase):
    def make_case(self, root, snapshot):
        shot = root / "shot.png"
        Image.new("RGB", (200, 100), (255, 255, 255)).save(shot)
        snap = root / "snap.json"
        snap.write_text(json.dumps(snapshot))
        return snap, shot, root / "out.png"

    def test_observe_shape_draws_rect_and_label(self):
        with tempfile.TemporaryDirectory() as d:
            snap, shot, out = self.make_case(Path(d), {"elements": [
                {"ref": "e1", "rect": {"x": 10, "y": 10,
                                       "width": 50, "height": 20}},
                {"ref": "e2", "rect": {"x": 0, "y": 0,
                                       "width": 0, "height": 0}},
                {"ref": "e3"},
                None,
                42,
                {"ref": "e4", "rect": {"x": float("nan"), "y": 1,
                                            "width": 5, "height": 5}},
                {"ref": "e5", "rect": {"x": 1, "y": 1,
                                            "width": float("inf"), "height": 5}},
            ]})
            result = drd.annotate(snap, shot, out)
            self.assertEqual(result["drawn"], 1)
            # Only the 0x0 rect counts as skipped; rect-less
            # elements are normal and simply not drawn.
            self.assertEqual(result["skipped"], 3)
            img = Image.open(out)
            # Top border of e1 at (35, 10) is red.
            self.assertEqual(img.getpixel((35, 10)), (255, 0, 0))

    def test_harvest_shape_and_scale_origin(self):
        with tempfile.TemporaryDirectory() as d:
            snap, shot, out = self.make_case(Path(d), {"items": {
                "#btn": {"rect": {"x": 5, "y": 5, "width": 10,
                                  "height": 10}},
            }})
            result = drd.annotate(snap, shot, out, scale=2.0,
                                  origin_x=100, origin_y=0)
            self.assertEqual(result["drawn"], 1)
            img = Image.open(out)
            # Scaled+offset left border at x=110, mid-height y=20.
            self.assertEqual(img.getpixel((110, 20)), (255, 0, 0))

    def test_out_cannot_overwrite_screenshot(self):
        with tempfile.TemporaryDirectory() as d:
            snap, shot, _out = self.make_case(Path(d), {"elements": []})
            with self.assertRaises(SystemExit):
                drd.main(["--snapshot", str(snap), "--screenshot", str(shot),
                          "--out", str(shot)])


if __name__ == "__main__":
    unittest.main()
