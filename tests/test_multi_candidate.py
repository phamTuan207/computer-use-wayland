"""Tests for scripts/multi_candidate.py (Pick 3, M5).

Run from the repo root: python3 -m unittest tests.test_multi_candidate
No broker, no desktop, no model calls. OCR tests skip cleanly when
tesseract is not installed.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import multi_candidate as mc  # noqa: E402


class FlagTests(unittest.TestCase):
    def test_default_off(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(mc.enabled())

    def test_only_exact_1_enables(self):
        for value in ("0", "true", "yes", ""):
            with mock.patch.dict(os.environ,
                                 {mc.FLAG_ENV: value}, clear=True):
                self.assertFalse(mc.enabled(), value)
        with mock.patch.dict(os.environ,
                             {mc.FLAG_ENV: "1"}, clear=True):
            self.assertTrue(mc.enabled())


class ParseTests(unittest.TestCase):
    def test_top3_sorted_by_confidence(self):
        reply = json.dumps({"candidates": [
            {"x": 100, "y": 100, "confidence": 0.5, "label": "low"},
            {"x": 500, "y": 500, "confidence": 0.95, "label": "best"},
            {"x": 300, "y": 300, "confidence": 0.7, "label": "mid"},
        ]})
        cands, errors = mc.parse_candidates(reply, 1000, 1000)
        self.assertEqual(errors, [])
        self.assertEqual([(c.x, c.y) for c in cands],
                         [(500, 500), (300, 300), (100, 100)])
        self.assertAlmostEqual(cands[0].confidence, 0.95)

    def test_cap_at_three_keeps_most_confident(self):
        reply = json.dumps({"candidates": [
            {"x": i * 100, "y": 100, "confidence": i / 10.0}
            for i in range(1, 6)]})
        cands, _ = mc.parse_candidates(reply, 1000, 1000)
        self.assertEqual(len(cands), 3)
        self.assertEqual([c.x for c in cands], [500, 400, 300])

    def test_legacy_single_candidate(self):
        cands, errors = mc.parse_candidates(
            '{"x": 250, "y": 750, "confidence": 0.8}', 2000, 1000)
        self.assertEqual(errors, [])
        self.assertEqual(len(cands), 1)
        self.assertEqual((cands[0].x, cands[0].y), (500, 750))

    def test_scale_conversion(self):
        cands, _ = mc.parse_candidates(
            '{"candidates": [{"x": 500, "y": 500, "confidence": 1}]}',
            1920, 1176)
        self.assertEqual((cands[0].x, cands[0].y), (960, 588))

    def test_out_of_range_dropped(self):
        reply = json.dumps({"candidates": [
            {"x": 1200, "y": 500, "confidence": 0.9},
            {"x": 500, "y": 500, "confidence": 0.8},
            {"x": -5, "y": 500, "confidence": 0.7},
        ]})
        cands, errors = mc.parse_candidates(reply, 1000, 1000)
        self.assertEqual(len(cands), 1)
        self.assertEqual(len(errors), 2)

    def test_near_duplicates_merged(self):
        reply = json.dumps({"candidates": [
            {"x": 500, "y": 500, "confidence": 0.9},
            {"x": 505, "y": 503, "confidence": 0.8},
            {"x": 700, "y": 700, "confidence": 0.6},
        ]})
        cands, errors = mc.parse_candidates(reply, 1000, 1000)
        self.assertEqual(len(cands), 2)
        self.assertEqual(len(errors), 1)

    def test_garbage_replies_never_raise(self):
        for reply in ("", "no json here", "{bad json", "[1, 2]",
                      '{"candidates": "nope"}',
                      '{"candidates": [{"x": "a", "y": 5}]}'):
            cands, errors = mc.parse_candidates(reply, 1000, 1000)
            self.assertEqual(cands, [])
            self.assertTrue(errors)

    def test_text_around_json_is_tolerated(self):
        reply = ('Here are the candidates:\n'
                 '{"candidates": [{"x": 100, "y": 200, "confidence": 0.9}]}'
                 '\nThat is my answer.')
        cands, errors = mc.parse_candidates(reply, 1000, 1000)
        self.assertEqual(errors, [])
        self.assertEqual((cands[0].x, cands[0].y), (100, 200))


class ZoomGateTests(unittest.TestCase):
    def test_small_target_zooms(self):
        self.assertTrue(mc.zoom_needed(16, 0.99))
        self.assertTrue(mc.zoom_needed(31, 0.99))

    def test_low_confidence_zooms(self):
        self.assertTrue(mc.zoom_needed(100, 0.5))
        self.assertTrue(mc.zoom_needed(None, 0.69))

    def test_large_confident_target_does_not_zoom(self):
        self.assertFalse(mc.zoom_needed(100, 0.9))
        self.assertFalse(mc.zoom_needed(32, 0.7))
        self.assertFalse(mc.zoom_needed(None, None))


class CropTests(unittest.TestCase):
    def test_default_crop_centred_140(self):
        crop, in_crop = mc.crop_for_candidate(500, 500, [0, 0, 1920, 1176])
        self.assertEqual(crop, [430, 430, 140, 140])
        self.assertEqual(in_crop, (70, 70))

    def test_zoom_crop_200_for_small_target(self):
        crop, _ = mc.crop_for_candidate(500, 500, [0, 0, 1920, 1176],
                                        target_size_px=16, confidence=0.9)
        self.assertEqual(crop[2:], [200, 200])

    def test_crop_clamped_inside_window(self):
        crop, in_crop = mc.crop_for_candidate(10, 10, [0, 0, 1920, 1176])
        self.assertEqual(crop, [0, 0, 140, 140])
        self.assertEqual(in_crop, (10, 10))
        crop, in_crop = mc.crop_for_candidate(
            1910, 1166, [0, 0, 1920, 1176])
        self.assertEqual(crop, [1780, 1036, 140, 140])
        self.assertEqual(in_crop, (130, 130))

    def test_crop_clamped_to_window_origin(self):
        crop, in_crop = mc.crop_for_candidate(
            510, 510, [100, 100, 800, 600])
        self.assertEqual(crop[0], 440)
        self.assertEqual(crop[1], 440)
        self.assertTrue(100 <= crop[0] and 100 <= crop[1])

    def test_tiny_window_shrinks_crop(self):
        crop, _ = mc.crop_for_candidate(50, 50, [0, 0, 100, 80])
        self.assertEqual(crop, [10, 0, 80, 80])

    def test_crop_never_below_90_or_above_200(self):
        for point in [(500, 500), (10, 10), (1910, 1166)]:
            crop, _ = mc.crop_for_candidate(*point, [0, 0, 1920, 1176])
            self.assertTrue(90 <= crop[2] <= 200)
            self.assertTrue(90 <= crop[3] <= 200)

    def test_observe_args_shape(self):
        args = mc.crop_observe_args("0xabc", [430, 430, 140, 140])
        self.assertEqual(args, ["observe", "--window", "0xabc", "--crop",
                                "430", "430", "140", "140",
                                "--max-width", "960"])


class StampTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = os.path.join(self.tmp.name, "src.png")
        self.out = os.path.join(self.tmp.name, "stamped.png")
        from PIL import Image
        Image.new("RGB", (400, 300), (255, 255, 255)).save(self.src)

    def test_stamp_creates_changed_copy(self):
        mc.stamp_failed_points(self.src, [(100, 100), (200, 150)], self.out)
        self.assertTrue(os.path.exists(self.out))
        from PIL import Image
        stamped = Image.open(self.out)
        self.assertEqual(stamped.size, (400, 300))
        self.assertEqual(stamped.getpixel((100, 100)), (255, 0, 0))
        self.assertNotEqual(
            Path(self.src).read_bytes(), Path(self.out).read_bytes())

    def test_stamp_missing_source_raises(self):
        with self.assertRaises(FileNotFoundError):
            mc.stamp_failed_points(os.path.join(self.tmp.name, "no.png"),
                                   [(1, 1)], self.out)

    def test_stamp_empty_points_is_plain_copy(self):
        mc.stamp_failed_points(self.src, [], self.out)
        self.assertTrue(os.path.exists(self.out))


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_none_expected_is_unverifiable(self):
        ok, text = mc.verify_crop_text("/nonexistent.png", None)
        self.assertIsNone(ok)

    def test_missing_tesseract_is_unverifiable(self):
        if shutil.which("tesseract") is not None:
            self.skipTest("tesseract installed, skip missing-binary case")
        ok, _ = mc.verify_crop_text("/nonexistent.png", "File")
        self.assertIsNone(ok)


class CliTests(unittest.TestCase):
    def run_cli(self, *args, env_extra=None):
        env = dict(os.environ)
        env.pop(mc.FLAG_ENV, None)
        env.update(env_extra or {})
        proc = subprocess.run(
            [sys.executable, "-m", "scripts.multi_candidate", *args],
            capture_output=True, text=True, cwd=Path(__file__).parents[1],
            env=env, timeout=30)
        return proc

    def test_ground_off_by_default(self):
        proc = self.run_cli("ground", "--image-w", "1000", "--image-h",
                            "1000", "--window", "0", "0", "1000", "1000",
                            "--reply", '{"x": 500, "y": 500}')
        self.assertEqual(proc.returncode, 1)
        self.assertIn("pick3 is off", proc.stdout)

    def test_ground_on_returns_crops(self):
        reply = json.dumps({"candidates": [
            {"x": 500, "y": 500, "confidence": 0.9, "label": "a"},
            {"x": 100, "y": 100, "confidence": 0.4, "label": "b"},
        ]})
        proc = self.run_cli("ground", "--image-w", "1000", "--image-h",
                            "1000", "--window", "0", "0", "1000", "1000",
                            "--reply", reply,
                            env_extra={mc.FLAG_ENV: "1"})
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(len(data["candidates"]), 2)
        self.assertEqual(data["candidates"][0]["crop"], [430, 430, 140, 140])

    def test_prompt_prints_discipline(self):
        proc = self.run_cli("prompt")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("top 3 candidate", proc.stdout)
        self.assertIn("Never click from the full-frame", proc.stdout)

    def test_prompt_has_no_em_dash(self):
        proc = self.run_cli("prompt")
        self.assertNotIn("\u2014", proc.stdout)
        self.assertNotIn("\u2013", proc.stdout)


class AttemptRecordTests(unittest.TestCase):
    def test_record_round_trips(self):
        attempt = mc.GroundingAttempt(
            target="File menu", misclicks=0, crops_used=2)
        attempt.candidates = [mc.Candidate(10, 20, 0.9, "File")]
        attempt.verified_index = 0
        data = attempt.as_dict()
        self.assertEqual(data["verified_index"], 0)
        self.assertEqual(data["candidates"][0]["x"], 10)
        json.dumps(data)


if __name__ == "__main__":
    unittest.main()
