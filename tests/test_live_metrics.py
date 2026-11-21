"""Tests for scripts/live_metrics.py and the run_live.py hooks (Y11).

Design frozen in improvements/worker-y11-design.md. Conventions follow
tests/test_timing.py: sys.path insert of scripts/, FakeClock, tmp dirs,
unittest. No live browser is needed for any test here; the live proof
run covers the real Zen path.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "tests" / "realistic"))

import hit_rate  # noqa: E402
import live_metrics  # noqa: E402
from jsonlutil import verify_jsonl  # noqa: E402
import run_live  # noqa: E402


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def _probe(*, relation="exact", clickable=False, top_id="submit",
           top_path="body/button:nth-of-type(1)", top_tag="button",
           found=True, rect=None, point=None, viewport=None,
           pointer_none=False):
    return {
        "found": found,
        "rect": rect if rect is not None else {"x": 0, "y": 0,
                                               "w": 100, "h": 40},
        "point": point if point is not None else {"x": 50, "y": 20},
        "viewport": viewport if viewport is not None else {"w": 1920,
                                                           "h": 1200},
        "intended": {"id": "submit",
                     "path": "body/button:nth-of-type(1)", "tag": "button"},
        "top": ({"id": top_id, "path": top_path, "tag": top_tag}
                if relation is not None else None),
        "relation": relation,
        "clickable_on_path": clickable,
        "pointer_events_none": pointer_none,
    }


def _rows(path):
    return [json.loads(line) for line in
            Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


class LiveMetricsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.clock = FakeClock()

    def tearDown(self):
        self.tmp.cleanup()

    def _metrics(self, name="m.jsonl", run_id="20261121-190000-1-a1b2c3"):
        return live_metrics.LiveMetrics(self.dir / name, run_id,
                                        clock=self.clock)

    def test_slugify_examples(self):
        self.assertEqual(live_metrics.slugify("#btn-save-board"),
                         "btn-save-board")
        self.assertEqual(
            live_metrics.slugify("#rows tr:nth-child(2) a"),
            "rows-tr-nth-child-2-a")
        self.assertEqual(
            live_metrics.slugify("button[onclick=\"clickCell('a2')\"]"),
            "button-onclick-clickcell-a2")
        self.assertEqual(live_metrics.slugify(""), "el")

    def test_append_attempt_rejects_live_selectors(self):
        # The live path must NOT route through hit_rate.append_attempt:
        # it rejects the very selectors the harness clicks.
        path = self.dir / "clicks.jsonl"
        with self.assertRaises(ValueError):
            hit_rate.append_attempt(
                path, case_id="t01", attempt=1, backend="dom",
                intended_target="#btn-save-board",
                actual_target="#btn-save-board")
        self.assertFalse(path.exists())

    def test_mixed_file_parses_and_has_exactly_one_summary(self):
        m = self._metrics()
        m.set_test("t01")
        m.begin_step("open fixture", "goto")
        self.clock.advance(0.5)
        m.note_action("goto", {"url": "http://x/fixture.html"})
        m.finish_step(True, None)
        m.begin_step("click upload", "click")
        m.record_click("#upload", _probe())
        m.finish_step(True, None)
        m.begin_step("type title", "type")
        m.record_type("#title", "Sample", "Sample")
        m.finish_step(True, None)
        summary = m.summary([{"test": "t01", "pass": True,
                              "elapsed_s": 1.5}])
        self.assertEqual(verify_jsonl(m.path), [])
        rows = _rows(m.path)
        self.assertEqual(
            sum(1 for r in rows if r["event"] == "summary"), 1)
        self.assertEqual(summary["steps"], 3)
        self.assertEqual(summary["clicks"]["attempts"], 1)
        self.assertEqual(summary["clicks"]["hit_rate"], 1.0)

    def test_envelope_on_every_row(self):
        m = self._metrics()
        m.set_test("t01")
        m.begin_step("s", "click")
        m.record_click("#a", _probe())
        m.finish_step(True, None)
        m.summary([{"test": "t01", "pass": True, "elapsed_s": 0.1}])
        for row in _rows(m.path):
            self.assertEqual(row["schema"], 1)
            self.assertEqual(row["run"], "20261121-190000-1-a1b2c3")
            self.assertIn("wall", row)
            self.assertIn("elapsed_s", row)
            self.assertIn(row["event"], ("step", "action", "click_attempt",
                                         "type_attempt", "summary"))
            self.assertIn("test", row)
            self.assertIn("attempt", row)

    def test_scripted_steps_have_null_think(self):
        m = self._metrics()
        m.set_test("t01")
        m.begin_step("s", "click")
        self.clock.advance(2.0)
        row = m.finish_step(True, None)
        self.assertIsNone(row["think_s"])
        self.assertEqual(row["think_source"], "scripted")
        self.assertFalse(row["slow_think"])
        self.assertEqual(row["act_s"], 2.0)
        summary = m.summary([{"test": "t01", "pass": True,
                              "elapsed_s": 2.0}])
        self.assertIsNone(summary["think_median_s"])
        self.assertIsNone(summary["think_max_s"])
        self.assertEqual(summary["model_calls"], 0)
        self.assertIsNone(summary["actions_per_call"])
        self.assertIsNone(summary["low_pace"])
        self.assertIn("no model decisions", summary["think_disclaimer"])

    def test_wait_exec_buckets_sum_within_act(self):
        m = self._metrics()
        m.set_test("t01")
        m.begin_step("s", "goto")
        m.note_wait(0.5)
        m.note_exec(0.2)
        self.clock.advance(1.0)
        row = m.finish_step(True, None)
        self.assertEqual(row["wait_s"], 0.5)
        self.assertEqual(row["exec_s"], 0.2)
        self.assertEqual(row["act_s"], 1.0)
        self.assertLessEqual(row["wait_s"] + row["exec_s"], row["act_s"])

    def test_hit_classification_exact_and_contains(self):
        m = self._metrics()
        m.set_test("t01")
        rec = m.record_click("#submit", _probe(relation="exact"))
        self.assertTrue(rec["hit"])
        rec = m.record_click(
            "#submit",
            _probe(relation="contains", clickable=False, top_id=None,
                   top_path="body/button:nth-of-type(1)/span:nth-of-type(1)",
                   top_tag="span"))
        self.assertTrue(rec["hit"])
        rows = [r for r in _rows(m.path) if r["event"] == "click_attempt"]
        self.assertEqual(rows[0]["hit_basis"], "exact")
        self.assertEqual(rows[1]["hit_basis"], "contains")

    def test_hit_classification_misses(self):
        cases = [
            # clickable descendant at the center: a delete button
            # inside the card deletes instead of opening it.
            (_probe(relation="contains", clickable=True, top_id="delete",
                    top_path="body/div:nth-of-type(1)/button:nth-of-type(1)",
                    top_tag="button"), "wrong_target"),
            (_probe(relation="ancestor", top_id="card",
                    top_path="body/div:nth-of-type(1)", top_tag="div"),
             "wrong_target"),
            (_probe(relation="other", top_id="toast",
                    top_path="body/div:nth-of-type(2)", top_tag="div"),
             "occlusion"),
            (_probe(relation="other", pointer_none=True), "wrong_target"),
            (_probe(relation=None, top_id=None, top_path=None, top_tag=None),
             "unknown"),
            (_probe(rect={"x": 0, "y": 0, "w": 0, "h": 40}),
             "coordinate_mapping"),
            (_probe(point={"x": 5000, "y": 20}), "coordinate_mapping"),
        ]
        m = self._metrics()
        m.set_test("t01")
        for probe, issue in cases:
            rec = m.record_click("#x", probe)
            self.assertFalse(rec["hit"])
        rows = [r for r in _rows(m.path) if r["event"] == "click_attempt"]
        self.assertEqual([r["issue_group"] for r in rows],
                         [issue for _, issue in cases])

    def test_exception_path_logs_a_miss(self):
        m = self._metrics()
        m.set_test("t01")
        rec = m.record_click("#missing", {"found": False},
                             error="RuntimeError: element not found")
        self.assertFalse(rec["hit"])
        row = [r for r in _rows(m.path)
               if r["event"] == "click_attempt"][0]
        self.assertEqual(row["issue_group"], "unknown")
        self.assertIn("element not found", row["error"])
        # A probe hit plus a driver failure is unresponsive.
        rec = m.record_click("#submit", _probe(),
                             error="RuntimeError: click intercepted")
        row = [r for r in _rows(m.path)
               if r["event"] == "click_attempt"][1]
        self.assertEqual(row["issue_group"], "unresponsive")

    def test_classify_probe_direct(self):
        self.assertEqual(
            live_metrics.classify_probe(_probe()),
            (True, "exact", None))
        self.assertEqual(
            live_metrics.classify_probe({"found": False}),
            (False, "none", "unknown"))
        self.assertEqual(
            live_metrics.classify_probe(_probe(), "RuntimeError: boom"),
            (False, "none", "unresponsive"))

    def test_js_clicks_excluded_but_listed_and_flagged(self):
        m = self._metrics()
        m.set_test("t01")
        m.begin_step("s", "click")
        for _ in range(8):
            m.record_click("#b", _probe())
        m.note_action("click_js", {"js": "document.querySelector('#x')",
                                   "js_len": 30})
        m.finish_step(True, None)
        summary = m.summary([{"test": "t01", "pass": True,
                              "elapsed_s": 1.0}])
        self.assertEqual(summary["clicks"]["attempts"], 8)
        self.assertEqual(summary["js_clicks_excluded"], 1)
        self.assertEqual(len(summary["js_clicks"]), 1)
        self.assertTrue(summary["unreliable"])
        self.assertIn("exceeds", summary["unreliable_reason"])

    def test_dom_to_js_retry_flags_unreliable(self):
        m = self._metrics()
        m.set_test("t01")
        m.begin_step("s", "click")
        m.record_click("#b", _probe(relation="other", top_id="toast",
                                    top_path="body/div:nth-of-type(2)",
                                    top_tag="div"))
        m.note_action("click_js", {"js": "x", "js_len": 1})
        m.finish_step(True, None)
        summary = m.summary([{"test": "t01", "pass": True,
                              "elapsed_s": 1.0}])
        self.assertTrue(summary["dom_to_js_retry"])
        self.assertTrue(summary["unreliable"])
        self.assertIn("retried", summary["unreliable_reason"])

    def test_eval_click_counts_toward_js_share(self):
        m = self._metrics()
        m.set_test("t01")
        m.begin_step("s", "eval")
        for _ in range(8):
            m.record_click("#b", _probe())
        m.note_action("eval", {"script_len": 40, "has_click": True})
        m.finish_step(True, None)
        summary = m.summary([{"test": "t01", "pass": True,
                              "elapsed_s": 1.0}])
        self.assertEqual(summary["eval_clicks_excluded"], 1)
        self.assertTrue(summary["unreliable"])

    def test_type_attempt_hit_miss_null(self):
        m = self._metrics()
        m.set_test("t01")
        self.assertTrue(
            m.record_type("#a", "hello", "hello")["hit"])
        self.assertFalse(
            m.record_type("#a", "hello", "hallo")["hit"])
        self.assertIsNone(
            m.record_type("#a", "hello", None)["hit"])
        summary = m.summary([{"test": "t01", "pass": True,
                              "elapsed_s": 0.1}])
        self.assertEqual(summary["type_attempts"],
                         {"attempts": 3, "hits": 1, "misses": 1,
                          "unknown": 1})

    def test_slug_collision_registry(self):
        m = self._metrics()
        first = m._slug_for("a/b")
        second = m._slug_for("a b")
        self.assertEqual(first, "a-b")
        self.assertNotEqual(second, "a-b")
        self.assertTrue(second.startswith("a-b-"))
        self.assertRegex(second, r"^[a-z0-9][a-z0-9_-]{0,63}$")
        self.assertEqual(m._slug_for("a/b"), "a-b")

    def test_run_id_formation(self):
        self.assertEqual(live_metrics.make_run_id("ok-id_1"), "ok-id_1")
        first = live_metrics.make_run_id("bad id!")
        second = live_metrics.make_run_id()
        self.assertRegex(first, r"^[0-9]{8}-[0-9]{6}-[0-9]+-[0-9a-f]{6}$")
        self.assertNotEqual(first, second)
        self.assertEqual(live_metrics.default_metrics_path(
            "/tmp/worker-p-live.jsonl"), "/tmp/worker-p-live-metrics.jsonl")
        self.assertEqual(live_metrics.default_metrics_path("/tmp/x"),
                         "/tmp/x-metrics.jsonl")

    def test_unwritable_path_degrades_without_raising(self):
        blocker = self.dir / "blocker"
        blocker.write_text("not a directory", encoding="utf-8")
        m = live_metrics.LiveMetrics(blocker / "m.jsonl", "run-1",
                                     clock=self.clock)
        self.assertTrue(m.disabled)
        self.assertIsNotNone(m.error)
        m.set_test("t01")
        m.begin_step("s", "click")
        m.record_click("#a", _probe())
        m.finish_step(True, None)
        m.summary([{"test": "t01", "pass": True, "elapsed_s": 0.1}])
        self.assertFalse((blocker / "m.jsonl").exists())

    def test_torn_tail_quarantined(self):
        path = self.dir / "m.jsonl"
        path.write_bytes(b'{"event": "step", "step": "old"}\n'
                         b'{"event": "step", "step": "tor')
        m = self._metrics("m.jsonl")
        self.assertFalse(m.disabled)
        m.set_test("t01")
        m.begin_step("s", "click")
        m.finish_step(True, None)
        self.assertEqual(verify_jsonl(path), [])
        torn = list(self.dir.glob("m.jsonl.torn-*"))
        self.assertEqual(len(torn), 1)
        rows = _rows(path)
        self.assertEqual(rows[0]["step"], "old")
        self.assertEqual(rows[1]["step"], "s")

    def test_two_instances_have_different_run_ids(self):
        first = live_metrics.make_run_id()
        second = live_metrics.make_run_id()
        self.assertNotEqual(first, second)


class MeteredDecoratorTest(unittest.TestCase):
    def test_outermost_only_and_fail_open(self):
        tmp = tempfile.TemporaryDirectory()
        try:
            path = Path(tmp.name) / "m.jsonl"
            clock = FakeClock()
            m = live_metrics.LiveMetrics(path, "run-1", clock=clock)
            m.set_test("t01")
            m.begin_step("s", "click")

            class FakeDriver:
                def __init__(self, metrics):
                    self.metrics = metrics
                    self._meter_depth = 0

                @run_live._metered("exec")
                def do_click(self):
                    self.do_inner()
                    return "clicked"

                @run_live._metered("exec")
                def do_inner(self):
                    return "inner"

            d = FakeDriver(m)
            self.assertEqual(d.do_click(), "clicked")
            rows = _rows(path)
            actions = [r for r in rows if r["event"] == "action"]
            self.assertEqual(len(actions), 1)
            self.assertEqual(actions[0]["kind"], "do_click")
            self.assertEqual(actions[0]["step"], "s")

            class NoMetrics:
                def __init__(self):
                    self.metrics = None
                    self._meter_depth = 0

                @run_live._metered("exec")
                def do_click(self):
                    return "clicked"

            self.assertEqual(NoMetrics().do_click(), "clicked")
        finally:
            tmp.cleanup()


class RunnerHookTest(unittest.TestCase):
    def test_log_step_unchanged_with_metrics(self):
        tmp = tempfile.TemporaryDirectory()
        try:
            d = Path(tmp.name)
            log1, log2 = d / "a.jsonl", d / "b.jsonl"
            old_log = run_live.LOG_PATH
            try:
                run_live.LOG_PATH = log1
                r1 = run_live.Runner("t01", "http://x")
                r1.step("s1", "click", lambda: "v")
                r1.step("s2", "wait", lambda: None)
                run_live.LOG_PATH = log2
                clock = FakeClock()
                m = live_metrics.LiveMetrics(d / "m.jsonl", "run-1",
                                             clock=clock)
                r2 = run_live.Runner("t01", "http://x", metrics=m)
                r2.step("s1", "click", lambda: "v")
                r2.step("s2", "wait", lambda: None)
                m.summary([{"test": "t01", "pass": True,
                            "elapsed_s": 0.1}])
            finally:
                run_live.LOG_PATH = old_log
            rows1 = _rows(log1)
            rows2 = _rows(log2)
            for row in rows1 + rows2:
                row.pop("ts", None)
            self.assertEqual(rows1, rows2)
            mrows = _rows(d / "m.jsonl")
            steps = [r for r in mrows if r["event"] == "step"]
            self.assertEqual(len(steps), 2)
            self.assertTrue(all(s["think_s"] is None for s in steps))
            self.assertTrue(all(s["think_source"] == "scripted"
                                for s in steps))
            self.assertEqual(verify_jsonl(d / "m.jsonl"), [])
        finally:
            tmp.cleanup()

    def test_step_failure_still_raises_and_logs(self):
        tmp = tempfile.TemporaryDirectory()
        try:
            d = Path(tmp.name)
            old_log = run_live.LOG_PATH
            try:
                run_live.LOG_PATH = d / "a.jsonl"
                clock = FakeClock()
                m = live_metrics.LiveMetrics(d / "m.jsonl", "run-1",
                                             clock=clock)
                r = run_live.Runner("t01", "http://x", metrics=m)

                def boom():
                    raise ValueError("nope")

                with self.assertRaises(RuntimeError):
                    r.step("s1", "click", boom)
                m.summary([{"test": "t01", "pass": False,
                            "elapsed_s": 0.1}])
            finally:
                run_live.LOG_PATH = old_log
            rows = _rows(d / "m.jsonl")
            step = [x for x in rows if x["event"] == "step"][0]
            self.assertFalse(step["ok"])
            self.assertIn("nope", step["error"])
            summary = [x for x in rows if x["event"] == "summary"][0]
            self.assertEqual(summary["steps_fail"], 1)
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
