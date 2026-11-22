"""Step-0 measurement bundle tests (FINAL direction e05fc58, worker 2):
P6 vision-call timing, CB-7 dispatch/first-pointer/target_breached,
CB-10 phase split, CB-3 uniformity + J37 codec separation, CB-5 eval
removal, CB-9 deploy manifest.

No live desktop, browser, or SSH is needed for any test here. The
vision timer runs on a fake clock; the J37 cases are synthetic PIL
frames with real JPEG q90 4:4:4 encodes; the manifest is written to a
temp installed root. Live numbers (SSH timings, soak, calibration)
are measured separately and recorded in the worker log.
"""
import importlib.util
import io
import json
import pathlib
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cu = _load("cu", SCRIPTS / "cu.py")
first_action = _load("first_action", SCRIPTS / "first_action.py")
vision_measure = _load("vision_measure", SCRIPTS / "vision_measure.py")
sync_installed = _load("sync_installed", SCRIPTS / "sync-installed.py")

from PIL import Image, ImageDraw  # noqa: E402


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class VisionTimerTest(unittest.TestCase):
    def test_vision_call_and_inference_split(self):
        clock = FakeClock()
        timer = vision_measure.VisionCallTimer(
            None, clock=clock, run_id="t1")
        timer.mark_observation_delivered({"max_width": 960})
        clock.advance(0.5)  # harness overhead before the model call
        timer.mark_inference_start()
        clock.advance(2.5)  # the model read
        timer.mark_inference_end()
        clock.advance(0.25)  # parse overhead after the model call
        rec = timer.mark_target_returned(ok=True, target="input#x")
        self.assertEqual(rec["vision_call_ms"], 3250.0)
        self.assertEqual(rec["inference_ms"], 2500.0)
        self.assertEqual(rec["inference_split"], "measured")
        self.assertEqual(rec["capture_params"]["max_width"], 960)
        self.assertEqual(rec["capture_params"]["jpeg_quality"], 90)
        self.assertIsNone(rec["error_class"])

    def test_inference_unmeasured_when_harness_cannot_split(self):
        clock = FakeClock()
        timer = vision_measure.VisionCallTimer(None, clock=clock)
        timer.mark_observation_delivered()
        clock.advance(3.0)
        rec = timer.mark_target_returned(ok=True)
        self.assertEqual(rec["vision_call_ms"], 3000.0)
        self.assertIsNone(rec["inference_ms"])
        self.assertTrue(rec["inference_split"].startswith("not_split"))
        # Never fill inference_ms with the whole-call number.

    def test_miss_without_evidence_is_unknown_not_guessed(self):
        clock = FakeClock()
        timer = vision_measure.VisionCallTimer(None, clock=clock)
        timer.mark_observation_delivered()
        rec = timer.mark_target_returned(ok=False)
        self.assertEqual(rec["error_class"], "unknown")

    def test_miss_classes_recorded(self):
        clock = FakeClock()
        timer = vision_measure.VisionCallTimer(None, clock=clock)
        timer.mark_observation_delivered()
        rec = timer.mark_target_returned(ok=False,
                                         error_class="wrong_frame")
        self.assertEqual(rec["error_class"], "wrong_frame")

    def test_no_delivery_timestamp_is_an_error(self):
        timer = vision_measure.VisionCallTimer(None, clock=FakeClock())
        with self.assertRaises(ValueError):
            timer.mark_target_returned(ok=True)


class ClassifyMissTest(unittest.TestCase):
    def test_stale_frame_is_wrong_frame(self):
        self.assertEqual(
            vision_measure.classify_miss(
                (10, 10), (20, 20), "window", "window", frame_fresh=False),
            "wrong_frame")

    def test_scope_mismatch_is_wrong_frame(self):
        self.assertEqual(
            vision_measure.classify_miss(
                (10, 10), (10, 10), "screen", "window", frame_fresh=True),
            "wrong_frame")

    def test_wrong_point_on_right_frame_is_wrong_target(self):
        self.assertEqual(
            vision_measure.classify_miss(
                (10, 10), (20, 20), "window", "window", frame_fresh=True),
            "wrong_target")

    def test_no_returned_point_is_unknown(self):
        self.assertEqual(
            vision_measure.classify_miss(
                None, (20, 20), "window", "window", frame_fresh=True),
            "unknown")


class DispatchAndFirstPointerTest(unittest.TestCase):
    def test_dispatch_ms_from_order_wall(self):
        ms = first_action._dispatch_ms(
            "2026-11-22T07:00:00.000+07:00",
            "2026-11-22T07:00:04.667+07:00")
        self.assertEqual(ms, 4667.0)

    def test_dispatch_ms_none_when_not_provided(self):
        self.assertIsNone(first_action._dispatch_ms(
            None, "2026-11-22T07:00:04.667+07:00"))
        self.assertIsNone(first_action._dispatch_ms(
            "not-a-time", "2026-11-22T07:00:04.667+07:00"))

    def test_dispatch_ms_none_on_clock_skew(self):
        # Order after laptop start: clocks disagree, never invent one.
        self.assertIsNone(first_action._dispatch_ms(
            "2026-11-22T07:00:05.000+07:00",
            "2026-11-22T07:00:04.667+07:00"))

    def test_first_pointer_skips_keyboard_groups(self):
        result = {"action_ms": [
            {"index": 0, "type": "keyboard_group", "ms": 120.0},
            {"index": 1, "type": "click", "ms": 410.5},
            {"index": 2, "type": "type", "ms": 900.0}]}
        self.assertEqual(
            first_action._first_pointer_action_ms(result), 410.5)

    def test_first_pointer_none_without_action_ms(self):
        self.assertIsNone(
            first_action._first_pointer_action_ms({"completed": 1}))
        self.assertIsNone(first_action._first_pointer_action_ms(
            {"action_ms": [{"index": 0, "type": "type", "ms": 100.0}]}))

    def test_capture_params_pinned(self):
        params = first_action._capture_params(
            {"max_width": 960, "jpeg_quality": 90, "jpeg_subsampling": 0})
        self.assertEqual(params, {"max_width": 960, "jpeg_quality": 90,
                                  "jpeg_subsampling": 0})


class UniformityTest(unittest.TestCase):
    def test_one_max_width_960(self):
        import inspect
        self.assertEqual(cu.CAPTURE_MAX_WIDTH, 960)
        self.assertEqual(cu.CAPTURE_JPEG_QUALITY, 90)
        self.assertEqual(cu.CAPTURE_JPEG_SUBSAMPLING, 0)
        self.assertEqual(
            inspect.signature(cu.observe).parameters["max_width"].default,
            960)
        self.assertEqual(
            inspect.signature(cu.observe_screen).parameters["max_width"].default,
            960)

    def test_no_1920_capture_left_in_first_action(self):
        text = (SCRIPTS / "first_action.py").read_text()
        self.assertNotIn("1920", text)


class J37CodecTest(unittest.TestCase):
    def _jpeg_roundtrip(self, image):
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=90, subsampling=0)
        return Image.open(io.BytesIO(buf.getvalue())).convert("RGB")

    def test_codec_noise_patch_does_not_refuse(self):
        """J37, precise case: a LOCALIZED photographic patch whose
        JPEG q90 re-encode trips the patch mean (over 6) while no
        pixel beats the codec ceiling. The old mean-only patch rule
        refused this; the new rule names it codec_scale_only and does
        not count it as changed. The global mean stays under 3, so
        the global limb does not trip either."""
        random.seed(11)
        img = Image.new("RGB", (960, 600), "white")
        block = Image.frombytes(
            "RGB", (100, 100),
            bytes(random.randrange(256) for _ in range(100 * 100 * 3)))
        img.paste(block, (430, 250))
        dec = self._jpeg_roundtrip(img)
        actions = [{"type": "click", "x": 480, "y": 300}]
        detail = cu._action_points_change_detail(img, dec, actions)
        self.assertFalse(detail["changed"])
        self.assertTrue(detail["codec_suspect"])
        self.assertGreater(detail["max_patch_mean"], 6)
        self.assertLessEqual(detail["max_pixel_diff"], 50)
        self.assertFalse(cu.screen_changed(img, dec, actions))
        full = cu.screen_change_detail(img, dec, actions)
        self.assertFalse(full["changed"])
        self.assertEqual(full["reason"], "codec_scale_only")
        self.assertTrue(full["codec_suspect"])
        # The preflight proceed condition holds end to end: the
        # settled frame is a raw re-capture (identical to new), and
        # the old-vs-settled patch check is the codec-aware one.
        self.assertFalse(cu.screen_changed(dec, dec, actions))
        self.assertFalse(cu._action_points_changed(img, dec, actions))

    def test_codec_noise_global_mean_still_triggers_settle_retry(self):
        """Whole-frame photographic noise: the global mean beats 3
        (6.27 here), so screen_changed still trips and the preflight
        spends its one settle retry, exactly as the existing
        brightness-shift test pins. The retry then proceeds, because
        the old-vs-settled patch check is codec-aware. The global
        limb is a retry trigger, never a refusal by itself."""
        random.seed(7)
        px = bytes(random.randrange(256)
                   for _ in range(960 * 600 * 3))
        img = Image.frombytes("RGB", (960, 600), px)
        dec = self._jpeg_roundtrip(img)
        actions = [{"type": "click", "x": 480, "y": 300}]
        self.assertTrue(cu.screen_changed(img, dec, actions))
        full = cu.screen_change_detail(img, dec, actions)
        self.assertEqual(full["reason"], "global_mean")
        self.assertTrue(full["codec_suspect"])
        self.assertFalse(cu._action_points_changed(img, dec, actions))

    def test_real_change_still_counts(self):
        """A black rectangle appearing: patch mean and max both trip."""
        img = Image.new("RGB", (960, 600), "white")
        changed = img.copy()
        ImageDraw.Draw(changed).rectangle([470, 290, 520, 320],
                                          fill="black")
        actions = [{"type": "click", "x": 480, "y": 300}]
        self.assertTrue(cu._action_points_changed(img, changed, actions))
        self.assertTrue(cu.screen_changed(img, changed, actions))
        detail = cu.screen_change_detail(img, changed, actions)
        self.assertEqual(detail["reason"], "action_point")

    def test_real_change_far_from_action_point_still_counts(self):
        img = Image.new("RGB", (960, 600), "white")
        changed = img.copy()
        ImageDraw.Draw(changed).rectangle([50, 50, 300, 200],
                                          fill="black")
        actions = [{"type": "click", "x": 480, "y": 300}]
        self.assertTrue(cu.screen_changed(img, changed, actions))

    def test_identical_frames_unchanged(self):
        img = Image.new("RGB", (960, 600), "white")
        actions = [{"type": "click", "x": 480, "y": 300}]
        self.assertFalse(cu.screen_changed(img, img, actions))


class ZenDomEvalGateTest(unittest.TestCase):
    def _run(self, argv, env=None):
        merged = dict(__import__("os").environ)
        merged.pop("CU_ZEN_DOM_DEBUG", None)
        if env:
            merged.update(env)
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "zen_dom.py")] + argv,
            capture_output=True, text=True, timeout=30, env=merged)

    def test_eval_refused_without_debug(self):
        proc = self._run(["eval", "return document.title"])
        self.assertEqual(proc.returncode, 1)
        body = json.loads(proc.stdout)
        self.assertIs(body["ok"], False)
        self.assertIn("debug-only", body["error"])
        self.assertIn("CB-5", body["error"])

    def test_eval_passes_gate_with_debug_flag(self):
        # Passes the CB-5 gate, then fails on the missing Zen session
        # (no Zen on the VM). The failure must NOT be the gate refusal.
        proc = self._run(["eval", "--debug", "return document.title"])
        self.assertNotIn("debug-only", proc.stdout)
        self.assertNotIn("debug-only", proc.stderr)

    def test_eval_passes_gate_with_debug_env(self):
        proc = self._run(["eval", "return document.title"],
                         env={"CU_ZEN_DOM_DEBUG": "1"})
        self.assertNotIn("debug-only", proc.stdout)


class DeployManifestTest(unittest.TestCase):
    def _ledger(self, commit="a" * 40, digest="b" * 64):
        return {"installer": "computer-use-wayland/sync-installed.py",
                "format": 1, "source_root": "/repo",
                "source_commit": commit,
                "source_content_sha256": digest,
                "managed_files": {"scripts/cu.py": {}, "scripts/x.py": {}},
                "artifacts": {"installed": {"native/indicator": {}}},
                "snapshot_path": "/tmp/snap"}

    def test_write_and_verify_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = pathlib.Path(tmp) / "installed"
            installed.mkdir()
            ledger = self._ledger()
            ledger_path = installed / "releases" / "x.json"
            ledger_path.parent.mkdir()
            ledger_path.write_text("{}")
            path = sync_installed._write_deploy_manifest(
                installed, ledger, ledger_path)
            self.assertEqual(
                path, installed / "deploy-manifest.json")
            manifest = json.loads(path.read_text())
            self.assertEqual(manifest["source_commit"], "a" * 40)
            self.assertEqual(manifest["ledger_path"], str(ledger_path))
            self.assertEqual(manifest["managed_files"], 2)
            self.assertEqual(
                manifest["artifacts"], {"native/indicator": {}})
            checked = sync_installed._verify_deploy_manifest(
                installed, ledger, ledger_path)
            self.assertEqual(checked["source_commit"], "a" * 40)

    def test_mismatch_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = pathlib.Path(tmp) / "installed"
            installed.mkdir()
            ledger = self._ledger()
            ledger_path = installed / "releases" / "x.json"
            ledger_path.parent.mkdir()
            ledger_path.write_text("{}")
            sync_installed._write_deploy_manifest(
                installed, ledger, ledger_path)
            other = self._ledger(commit="c" * 40)
            with self.assertRaises(sync_installed.SyncError):
                sync_installed._verify_deploy_manifest(
                    installed, other, ledger_path)

    def test_missing_manifest_warns_but_does_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = pathlib.Path(tmp) / "installed"
            installed.mkdir()
            ledger = self._ledger()
            ledger_path = installed / "releases" / "x.json"
            self.assertIsNone(
                sync_installed._verify_deploy_manifest(
                    installed, ledger, ledger_path))


class FirstActionEnvelopeTest(unittest.TestCase):
    """CB-7/CB-10/P6c envelope fields, via the G28 refusal path
    (stale given observation): no session attempt, no pointer moves,
    no live desktop. Fake cu and fake overlay; the run refuses
    before any action."""

    def test_refusal_envelope_carries_dispatch_phases_and_params(self):
        import contextlib
        import os
        import types
        from datetime import datetime, timedelta, timezone
        from unittest import mock

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        state_dir = pathlib.Path(tmp.name) / "state"
        actions_path = pathlib.Path(tmp.name) / "actions.json"
        actions_path.write_text(json.dumps(
            [{"type": "click", "x": 10, "y": 10}]))
        obs_path = pathlib.Path(tmp.name) / "given.json"
        stale_meta = {"id": "abc123def456",
                      "image": str(pathlib.Path(tmp.name) / "x.jpg"),
                      "monitor_box": [0, 0, 1920, 1200],
                      "created": __import__("time").time() - 200,
                      "scope": "screen"}
        obs_path.write_text(json.dumps(stale_meta))

        fake_cu = types.SimpleNamespace()
        fake_cu.read_json_file = lambda p: json.loads(
            pathlib.Path(p).read_text())
        fake_cu.environment = lambda: {}
        fake_cu.CAPTURE_MAX_WIDTH = 960
        fake_cu.STATE = state_dir
        fresh_meta = {"id": "newid000001",
                      "observation": str(pathlib.Path(tmp.name) / "o.json"),
                      "scope": "screen", "max_width": 960,
                      "jpeg_quality": 90, "jpeg_subsampling": 0}
        fake_cu.observe_screen = (
            lambda env, screen, max_width=None, persist=True: fresh_meta)

        fake_overlay = types.SimpleNamespace()
        fake_overlay.add_holder = lambda *a, **k: None
        fake_overlay._ensure_daemon = lambda: None
        fake_overlay._send_socket = lambda msg: {"visible": True}
        fake_overlay._label_for = lambda a, m: "test"
        fake_overlay.remove_holder = lambda *a, **k: None

        tz7 = timezone(timedelta(hours=7))
        order_wall = (datetime.now(tz7) - timedelta(seconds=2)).isoformat(
            timespec="milliseconds")
        args = first_action.build_parser().parse_args([
            "--actions", str(actions_path),
            "--observation", str(obs_path),
            "--order-wall", order_wall])
        out = io.StringIO()
        with mock.patch.object(first_action, "_load_cu",
                               return_value=fake_cu):
            with mock.patch.dict(sys.modules, {"overlay": fake_overlay}):
                with contextlib.redirect_stdout(out):
                    rc = first_action.run(args)
        self.assertEqual(rc, 1)
        envelope = json.loads(out.getvalue().strip().splitlines()[-1])
        self.assertIs(envelope["ok"], False)
        self.assertEqual(envelope["path"], "refused")
        self.assertEqual(envelope["dispatch_basis"], "order_wall")
        self.assertIsInstance(envelope["dispatch_ms"], float)
        self.assertGreater(envelope["dispatch_ms"], 1500)
        self.assertLess(envelope["dispatch_ms"], 5000)
        self.assertIsNone(envelope["first_pointer_ms"])
        self.assertTrue(envelope["target_breached_basis"].startswith(
            "total_fallback"))
        self.assertIn("overlay_acquire_ms", envelope["phase_ms"])
        self.assertIn("observation_ms", envelope["phase_ms"])
        self.assertIsNone(envelope["think_ms"])
        self.assertIn("not_in_act_now", envelope["think_basis"])
        self.assertTrue(
            envelope["overlay_flicker"].startswith("unprobed"))
        self.assertEqual(
            envelope["observation"]["capture_params"],
            {"max_width": 960, "jpeg_quality": 90,
             "jpeg_subsampling": 0})


if __name__ == "__main__":
    unittest.main()
