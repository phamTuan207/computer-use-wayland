"""Offline native tests for the vendored corrected wtype helper.

Builds the patched translation unit (patch --batch --fuzz=0, same step as
scripts/build.py) and a stub harness (tests/wtype_harness.c) that runs the
real parse_args() + kbcorr_preflight() + kbcorr_prepare_keymap() and the
real emission path (upload_keymap + run_commands) with the Wayland
protocol calls intercepted at the source level and stubbed transport /
delays. No Wayland connection, no compositor, no input sent to any
application. The harness captures the single uploaded keymap, compiles it
into one persistent libxkbcommon client state, replays the captured
modifier/key requests through it, and reports the decoded text plus the
full emission trace (upload count, groups, modifier bits). Actual delivery
to applications is verified by the live gates (i)-(iv), not here.

Run: python3 -B -m unittest tests.test_wtype_native -v
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util
_spec = importlib.util.spec_from_file_location("cu", ROOT / "scripts" / "cu.py")
cu = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cu)

SENTENCE = "Tối nay ôn cấu trúc dữ liệu lúc 20:30.\n"
POOL = list(range(2, 14)) + list(range(16, 28)) + \
    list(range(30, 42)) + list(range(43, 54))
FIXED = {" ": 57, "\n": 28, "\r": 28, "\t": 15, "\x1b": 1, "\x08": 14,
         "\x7f": 111}
# WTYPE_COMMAND_* values from the patched TU.
TEXT, MOD_PRESS, MOD_RELEASE, KEY_PRESS, KEY_RELEASE, SLEEP = 0, 1, 2, 3, 4, 5
# WL_KEYBOARD_KEY_STATE_* values.
KEY_RELEASED, KEY_PRESSED = 0, 1

# Golden G==1 serialized keymaps captured from the OLD writer (pre
# multi-page patch) with a throwaway interception harness; the new writer
# must reproduce them byte-for-byte for single-group inputs.
# g1: sentence direct. g2: merged Ctrl+A + sentence. g3: sentinel only.
# g4: leading-dash stdin sentence.
GOLDEN_SENTENCE = base64.b64decode("eGtiX2tleW1hcCB7CnhrYl9rZXljb2RlcyAiKHVubmFtZWQpIiB7Cm1pbmltdW0gPSA4OwptYXhpbXVtID0gMjQ4Owo8SzE+ID0gMTA7CjxLMj4gPSAxMTsKPEszPiA9IDEyOwo8SzQ+ID0gNjU7CjxLNT4gPSAxMzsKPEs2PiA9IDE0Owo8Szc+ID0gMTU7CjxLOD4gPSAxNjsKPEs5PiA9IDE3Owo8SzEwPiA9IDE4Owo8SzExPiA9IDE5Owo8SzEyPiA9IDIwOwo8SzEzPiA9IDIxOwo8SzE0PiA9IDI0Owo8SzE1PiA9IDI1Owo8SzE2PiA9IDI2Owo8SzE3PiA9IDI3Owo8SzE4PiA9IDI4Owo8SzE5PiA9IDI5Owo8SzIwPiA9IDMwOwo8SzIxPiA9IDMxOwo8SzIyPiA9IDMyOwo8SzIzPiA9IDMzOwo8SzI0PiA9IDM2Owo8SzI1PiA9IDI0ODsKfTsKeGtiX3R5cGVzICIodW5uYW1lZCkiIHsgaW5jbHVkZSAiY29tcGxldGUiIH07CnhrYl9jb21wYXRpYmlsaXR5ICIodW5uYW1lZCkiIHsgaW5jbHVkZSAiY29tcGxldGUiIH07CnhrYl9zeW1ib2xzICIodW5uYW1lZCkiIHsKa2V5IDxLMT4ge1tUXX07CmtleSA8SzI+IHtbb2NpcmN1bWZsZXhhY3V0ZV19OwprZXkgPEszPiB7W2ldfTsKa2V5IDxLND4ge1tzcGFjZV19OwprZXkgPEs1PiB7W25dfTsKa2V5IDxLNj4ge1thXX07CmtleSA8Szc+IHtbeV19OwprZXkgPEs4PiB7W29jaXJjdW1mbGV4XX07CmtleSA8Szk+IHtbY119OwprZXkgPEsxMD4ge1thY2lyY3VtZmxleGFjdXRlXX07CmtleSA8SzExPiB7W3VdfTsKa2V5IDxLMTI+IHtbdF19OwprZXkgPEsxMz4ge1tyXX07CmtleSA8SzE0PiB7W3VhY3V0ZV19OwprZXkgPEsxNT4ge1tkXX07CmtleSA8SzE2PiB7W3Vob3JudGlsZGVdfTsKa2V5IDxLMTc+IHtbbF19OwprZXkgPEsxOD4ge1tlY2lyY3VtZmxleGJlbG93ZG90XX07CmtleSA8SzE5PiB7WzJdfTsKa2V5IDxLMjA+IHtbMF19OwprZXkgPEsyMT4ge1tjb2xvbl19OwprZXkgPEsyMj4ge1szXX07CmtleSA8SzIzPiB7W3BlcmlvZF19OwprZXkgPEsyND4ge1tSZXR1cm5dfTsKa2V5IDxLMjU+IHtbVm9pZFN5bWJvbF19Owp9Owp9OwoA")
GOLDEN_MERGED_A = base64.b64decode("eGtiX2tleW1hcCB7CnhrYl9rZXljb2RlcyAiKHVubmFtZWQpIiB7Cm1pbmltdW0gPSA4OwptYXhpbXVtID0gMjQ4Owo8SzE+ID0gMzg7CjxLMj4gPSAxMDsKPEszPiA9IDExOwo8SzQ+ID0gMTI7CjxLNT4gPSA2NTsKPEs2PiA9IDEzOwo8Szc+ID0gMTQ7CjxLOD4gPSAxNTsKPEs5PiA9IDE2Owo8SzEwPiA9IDE3Owo8SzExPiA9IDE4Owo8SzEyPiA9IDE5Owo8SzEzPiA9IDIwOwo8SzE0PiA9IDIxOwo8SzE1PiA9IDI0Owo8SzE2PiA9IDI1Owo8SzE3PiA9IDI2Owo8SzE4PiA9IDI3Owo8SzE5PiA9IDI4Owo8SzIwPiA9IDI5Owo8SzIxPiA9IDMwOwo8SzIyPiA9IDMxOwo8SzIzPiA9IDMyOwo8SzI0PiA9IDMzOwo8SzI1PiA9IDM2Owo8SzI2PiA9IDI0ODsKfTsKeGtiX3R5cGVzICIodW5uYW1lZCkiIHsgaW5jbHVkZSAiY29tcGxldGUiIH07CnhrYl9jb21wYXRpYmlsaXR5ICIodW5uYW1lZCkiIHsgaW5jbHVkZSAiY29tcGxldGUiIH07CnhrYl9zeW1ib2xzICIodW5uYW1lZCkiIHsKa2V5IDxLMT4ge1thXX07CmtleSA8SzI+IHtbVF19OwprZXkgPEszPiB7W29jaXJjdW1mbGV4YWN1dGVdfTsKa2V5IDxLND4ge1tpXX07CmtleSA8SzU+IHtbc3BhY2VdfTsKa2V5IDxLNj4ge1tuXX07CmtleSA8Szc+IHtbYV19OwprZXkgPEs4PiB7W3ldfTsKa2V5IDxLOT4ge1tvY2lyY3VtZmxleF19OwprZXkgPEsxMD4ge1tjXX07CmtleSA8SzExPiB7W2FjaXJjdW1mbGV4YWN1dGVdfTsKa2V5IDxLMTI+IHtbdV19OwprZXkgPEsxMz4ge1t0XX07CmtleSA8SzE0PiB7W3JdfTsKa2V5IDxLMTU+IHtbdWFjdXRlXX07CmtleSA8SzE2PiB7W2RdfTsKa2V5IDxLMTc+IHtbdWhvcm50aWxkZV19OwprZXkgPEsxOD4ge1tsXX07CmtleSA8SzE5PiB7W2VjaXJjdW1mbGV4YmVsb3dkb3RdfTsKa2V5IDxLMjA+IHtbMl19OwprZXkgPEsyMT4ge1swXX07CmtleSA8SzIyPiB7W2NvbG9uXX07CmtleSA8SzIzPiB7WzNdfTsKa2V5IDxLMjQ+IHtbcGVyaW9kXX07CmtleSA8SzI1PiB7W1JldHVybl19OwprZXkgPEsyNj4ge1tWb2lkU3ltYm9sXX07Cn07Cn07CgA=")
GOLDEN_SENTINEL = base64.b64decode("eGtiX2tleW1hcCB7CnhrYl9rZXljb2RlcyAiKHVubmFtZWQpIiB7Cm1pbmltdW0gPSA4OwptYXhpbXVtID0gMjQ4Owo8SzE+ID0gMjQ4Owp9Owp4a2JfdHlwZXMgIih1bm5hbWVkKSIgeyBpbmNsdWRlICJjb21wbGV0ZSIgfTsKeGtiX2NvbXBhdGliaWxpdHkgIih1bm5hbWVkKSIgeyBpbmNsdWRlICJjb21wbGV0ZSIgfTsKeGtiX3N5bWJvbHMgIih1bm5hbWVkKSIgewprZXkgPEsxPiB7W1ZvaWRTeW1ib2xdfTsKfTsKfTsKAA==")
GOLDEN_STDIN = base64.b64decode("eGtiX2tleW1hcCB7CnhrYl9rZXljb2RlcyAiKHVubmFtZWQpIiB7Cm1pbmltdW0gPSA4OwptYXhpbXVtID0gMjQ4Owo8SzE+ID0gMjQ4Owo8SzI+ID0gMTA7CjxLMz4gPSAxMTsKPEs0PiA9IDEyOwo8SzU+ID0gMTM7CjxLNj4gPSA2NTsKPEs3PiA9IDE0Owo8Szg+ID0gMTU7CjxLOT4gPSAxNjsKPEsxMD4gPSAxNzsKPEsxMT4gPSAxODsKPEsxMj4gPSAxOTsKPEsxMz4gPSAyMDsKPEsxND4gPSAyMTsKPEsxNT4gPSAyNDsKPEsxNj4gPSAyNTsKPEsxNz4gPSAyNjsKPEsxOD4gPSAyNzsKPEsxOT4gPSAyODsKPEsyMD4gPSAyOTsKPEsyMT4gPSAzMDsKPEsyMj4gPSAzMTsKPEsyMz4gPSAzMjsKPEsyND4gPSAzMzsKPEsyNT4gPSAzNDsKPEsyNj4gPSAzNjsKfTsKeGtiX3R5cGVzICIodW5uYW1lZCkiIHsgaW5jbHVkZSAiY29tcGxldGUiIH07CnhrYl9jb21wYXRpYmlsaXR5ICIodW5uYW1lZCkiIHsgaW5jbHVkZSAiY29tcGxldGUiIH07CnhrYl9zeW1ib2xzICIodW5uYW1lZCkiIHsKa2V5IDxLMT4ge1tWb2lkU3ltYm9sXX07CmtleSA8SzI+IHtbbWludXNdfTsKa2V5IDxLMz4ge1tUXX07CmtleSA8SzQ+IHtbb2NpcmN1bWZsZXhhY3V0ZV19OwprZXkgPEs1PiB7W2ldfTsKa2V5IDxLNj4ge1tzcGFjZV19OwprZXkgPEs3PiB7W25dfTsKa2V5IDxLOD4ge1thXX07CmtleSA8Szk+IHtbeV19OwprZXkgPEsxMD4ge1tvY2lyY3VtZmxleF19OwprZXkgPEsxMT4ge1tjXX07CmtleSA8SzEyPiB7W2FjaXJjdW1mbGV4YWN1dGVdfTsKa2V5IDxLMTM+IHtbdV19OwprZXkgPEsxND4ge1t0XX07CmtleSA8SzE1PiB7W3JdfTsKa2V5IDxLMTY+IHtbdWFjdXRlXX07CmtleSA8SzE3PiB7W2RdfTsKa2V5IDxLMTg+IHtbdWhvcm50aWxkZV19OwprZXkgPEsxOT4ge1tsXX07CmtleSA8SzIwPiB7W2VjaXJjdW1mbGV4YmVsb3dkb3RdfTsKa2V5IDxLMjE+IHtbMl19OwprZXkgPEsyMj4ge1swXX07CmtleSA8SzIzPiB7W2NvbG9uXX07CmtleSA8SzI0PiB7WzNdfTsKa2V5IDxLMjU+IHtbcGVyaW9kXX07CmtleSA8SzI2PiB7W1JldHVybl19Owp9Owp9OwoA")


def expected_phys(text):
    """First-occurrence physical allocation for a literal string."""
    out = {}
    pool_i = 0
    reserved = set()
    for ch in text:
        if ch in FIXED:
            reserved.add(FIXED[ch])
    effpool = [p for p in POOL if p not in reserved]
    j = 0
    for ch in text:
        if ch in out:
            continue
        if ch in FIXED:
            out[ch] = FIXED[ch]
        else:
            out[ch] = effpool[j % len(effpool)]
            j += 1
    return out


def distinct_chars(n, start=0x100):
    """n distinct printable BMP pool literals (no fixed controls)."""
    return "".join(chr(start + i) for i in range(n))


class WtypeNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="wtype-native-")
        cls.addClassCleanup(cls.tmp.cleanup)
        tmp = Path(cls.tmp.name)
        vendor = ROOT / "native" / "vendor" / "wtype"
        patched = tmp / "main-patched.c"
        subprocess.run(
            ["patch", "--batch", "--fuzz=0", "--output", str(patched),
             str(vendor / "main.c"), str(vendor / "keyboard-correction.patch")],
            check=True, capture_output=True, text=True)
        cls.patched = patched
        flags = subprocess.check_output(
            ["pkg-config", "--cflags", "--libs", "xkbcommon", "wayland-client"],
            text=True).split()
        cls.harness = tmp / "wtype-harness"
        subprocess.run(
            ["cc", "-Wall", "-Wextra", "-O2", "-I", str(tmp),
             "-I", str(ROOT / "native"), "-o", str(cls.harness),
             str(ROOT / "tests" / "wtype_harness.c"),
             str(ROOT / "native" / "keyboard-protocol.c"), *flags],
            check=True, capture_output=True, text=True)
        cls.env = dict(os.environ, LC_ALL="C.UTF-8", LANG="C.UTF-8")
        cls.dump = tmp / "dump.json"
        cls.keymap = tmp / "keymap.bin"
        cls.trace = tmp / "trace.json"

    def run_harness(self, argv, input_bytes=None):
        proc, dump, _, _ = self.run_traced(argv, input_bytes)
        return proc, dump

    def run_traced(self, argv, input_bytes=None):
        for p in (self.dump, self.keymap, self.trace):
            if p.exists():
                p.unlink()
        env = dict(self.env, KBCORR_DUMP=str(self.dump),
                   KBCORR_KEYMAP=str(self.keymap),
                   KBCORR_TRACE=str(self.trace))
        proc = subprocess.run(
            [str(self.harness), *argv], input=input_bytes,
            capture_output=True, timeout=60, env=env)
        dump = json.loads(self.dump.read_text()) if self.dump.exists() else None
        keymap = self.keymap.read_bytes() if self.keymap.exists() else None
        trace = json.loads(self.trace.read_text()) if self.trace.exists() else None
        return proc, dump, keymap, trace

    def phys_seq(self, dump, cmd_index=0):
        """Physical codes for a TEXT command's codes, in order."""
        entries = dump["entries"]
        cmd = dump["commands"][cmd_index]
        return [entries[c - 1]["phys"] for c in cmd["codes"]]

    def assert_clean_emission(self, trace, text, max_group,
                              extra_pairs=0, chord_keys=()):
        """Shared emitted-behavior assertions for a literal text run.

        extra_pairs / chord_keys cover non-literal press/release pairs
        (e.g. the single Ctrl+A chord: one pair on phys 30 with Ctrl
        depressed); every other key must carry no modifier bits.
        """
        self.assertIsNotNone(trace, "no emission trace produced")
        self.assertEqual(trace["uploads"], 1,
                         "more than one keymap upload")
        self.assertEqual(trace["decoded"], text,
                         "replayed client decoding differs from input")
        presses = [k for k in trace["keys"] if k["state"] == KEY_PRESSED]
        releases = [k for k in trace["keys"] if k["state"] == KEY_RELEASED]
        self.assertEqual(len(presses), len(text) + extra_pairs,
                         "one physical press per typed character (+ chord)")
        self.assertEqual(len(releases), len(text) + extra_pairs,
                         "one physical release per typed character (+ chord)")
        self.assertEqual([k["key"] for k in presses],
                         [k["key"] for k in releases],
                         "press/release pairs must match")
        self.assertEqual(trace["groups_seen"], list(range(max_group + 1)))
        for k in trace["keys"]:
            self.assertLessEqual(k["group"], max_group)
            if k["dep"] != 0:
                self.assertIn(
                    k["key"], chord_keys,
                    "modifier bits on a non-chord key")
        self.assertFalse(trace["group_change_while_down"],
                         "group changed while a key was held")
        self.assertFalse(trace["overlap_press"],
                         "a key was pressed while another was held")
        self.assertFalse(trace["key_down_at_end"],
                         "a key was left held at the end")
        self.assertEqual(trace["final_group"], 0,
                         "group was not reset to 0 at the end")

    def test_sentence_allocates_safe_codes(self):
        proc, dump = self.run_harness([SENTENCE])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr, b"")
        want = expected_phys(SENTENCE)
        self.assertEqual(self.phys_seq(dump), [want[ch] for ch in SENTENCE])
        self.assertEqual(len(dump["commands"]), 1)
        self.assertEqual(dump["commands"][0]["type"], TEXT)
        self.assertEqual(len(dump["commands"][0]["codes"]), len(SENTENCE))
        # 22 distinct chars + the sentinel entry.
        self.assertEqual(len(dump["entries"]), len(set(SENTENCE)) + 1)
        for entry in dump["entries"]:
            self.assertIn(entry["phys"], set(POOL) | {28, 57, 240})
        for ch, phys in zip(SENTENCE, self.phys_seq(dump)):
            if ch == " ":
                self.assertEqual(phys, 57)
            if ch == "\n":
                self.assertEqual(phys, 28)
            if ch == "ú":
                self.assertIn(phys, POOL)
            if ch == "d":
                self.assertIn(phys, POOL)
            if ch == "T":
                self.assertNotEqual(phys, 1)
        sentinel = [e for e in dump["entries"] if e["sentinel"]]
        self.assertEqual(len(sentinel), 1)
        self.assertEqual(sentinel[0]["phys"], 240)
        self.assertTrue(sentinel[0]["fixed"])

    def test_canonical_explicit_codes_both_spellings(self):
        for key, phys, xkb in (("A", 30, 0x61), ("a", 30, 0x61),
                               ("S", 31, 0x73), ("s", 31, 0x73)):
            proc, dump = self.run_harness(
                ["-P", key, "-s", "12", "-p", key, "-s", "12",
                 "-p", "VoidSymbol"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            entries = dump["entries"]
            named = [e for e in entries if e["explicit"] and not e["sentinel"]]
            self.assertEqual(len(named), 1)
            self.assertEqual(named[0]["phys"], phys)
            self.assertEqual(named[0]["xkb"], xkb)
            self.assertTrue(named[0]["fixed"])
            cmds = dump["commands"]
            self.assertEqual(
                [c["type"] for c in cmds],
                [KEY_PRESS, SLEEP, KEY_RELEASE, SLEEP, KEY_RELEASE])
            self.assertEqual(
                entries[cmds[0]["single"] - 1]["phys"], phys)
            self.assertTrue(cmds[-1]["noop"])  # sentinel release: no event

    def test_merged_ctrl_a_text(self):
        argv = ["-M", "ctrl", "-P", "A", "-s", "12", "-p", "A",
                "-m", "ctrl", "-s", "12", SENTENCE, "-s", "12",
                "-p", "VoidSymbol"]
        proc, dump = self.run_harness(argv)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        cmds = dump["commands"]
        self.assertEqual(
            [c["type"] for c in cmds],
            [MOD_PRESS, KEY_PRESS, SLEEP, KEY_RELEASE, MOD_RELEASE,
             SLEEP, TEXT, SLEEP, KEY_RELEASE])
        self.assertEqual(cmds[0]["mod"], 4)  # ctrl
        entries = dump["entries"]
        self.assertEqual(entries[cmds[1]["single"] - 1]["phys"], 30)
        self.assertTrue(cmds[-1]["noop"])
        want = expected_phys(SENTENCE)
        self.assertEqual(self.phys_seq(dump, 6), [want[ch] for ch in SENTENCE])

    def test_leading_dash_stdin(self):
        payload = ("-" + SENTENCE).encode("utf-8")
        proc, dump = self.run_harness(["-", "-p", "VoidSymbol"],
                                      input_bytes=payload)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        cmds = dump["commands"]
        self.assertEqual([c["type"] for c in cmds], [TEXT, KEY_RELEASE])
        self.assertTrue(cmds[-1]["noop"])
        want = expected_phys("-" + SENTENCE)
        self.assertEqual(self.phys_seq(dump),
                         [want[ch] for ch in "-" + SENTENCE])
        self.assertIn(self.phys_seq(dump)[0], POOL)

    def test_page_switch_many_distinct_bmp(self):
        chars = "".join(chr(n) for n in range(0x100, 0x160))
        text = chars + chars[::-1] + "\n"
        proc, dump = self.run_harness([text])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        entries = dump["entries"]
        pool_entries = [e for e in entries if e["pool"]]
        self.assertEqual(len(pool_entries), 96)
        pages = sorted({e["page"] for e in pool_entries})
        self.assertEqual(pages, [0, 1, 2])
        self.assertEqual(
            [sum(1 for e in pool_entries if e["page"] == p)
             for p in (0, 1, 2)], [47, 47, 2])
        for e in pool_entries:
            self.assertIn(e["phys"], POOL)
        # 96 pool literals + newline + sentinel.
        self.assertEqual(len(entries), 98)
        # Repeats reuse the same entries: 193 typed chars, 97 distinct.
        self.assertEqual(len(dump["commands"][0]["codes"]), len(text))
        self.assertEqual(len({c for c in dump["commands"][0]["codes"]}), 97)

    def test_sentinel_emits_no_event(self):
        proc, dump = self.run_harness(["-p", "VoidSymbol"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(dump["entries"]), 1)
        self.assertTrue(dump["entries"][0]["sentinel"])
        self.assertEqual(dump["entries"][0]["phys"], 240)
        self.assertEqual(
            [c["type"] for c in dump["commands"]], [KEY_RELEASE])
        self.assertTrue(dump["commands"][0]["noop"])

    def test_sentinel_press_rejected(self):
        proc, _ = self.run_harness(["-P", "VoidSymbol"])
        self.assertNotEqual(proc.returncode, 0)

    def test_unknown_canonical_key_rejected(self):
        # U1F600 is a valid Unicode keysym name but no physical key on a
        # pc105/us board produces it, so canonical resolution must refuse.
        # (XF86AudioPlay does resolve: evdev keycode 172 carries it.)
        proc, _ = self.run_harness(
            ["-P", "U1F600", "-s", "12", "-p", "U1F600"])
        self.assertNotEqual(proc.returncode, 0)

    def test_conflicting_identities_rejected(self):
        proc, _ = self.run_harness(
            ["-P", "Tab", "-s", "12", "-p", "Tab",
             "-P", "ISO_Left_Tab", "-s", "12", "-p", "ISO_Left_Tab",
             "-s", "12", "-p", "VoidSymbol"])
        self.assertNotEqual(proc.returncode, 0)

    def test_held_key_text_rejected(self):
        proc, _ = self.run_harness(["-M", "ctrl", "hello"])
        self.assertNotEqual(proc.returncode, 0)
        proc, _ = self.run_harness(["-P", "A", "hello"])
        self.assertNotEqual(proc.returncode, 0)

    def test_control_and_nonbmp_rejected(self):
        proc, _ = self.run_harness(["a\x01b"])
        self.assertNotEqual(proc.returncode, 0)
        proc, _ = self.run_harness(["a\U0001F600b"])
        self.assertNotEqual(proc.returncode, 0)

    def test_empty_input_noop(self):
        proc, dump = self.run_harness([""])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(dump["entries"]), 1)  # sentinel only
        self.assertEqual(dump["commands"][0]["codes"], [])

    def test_broker_argv_selects_private_helper(self):
        helper = str(cu.ROOT / "native" / "wtype")
        self.assertEqual(
            cu.keyboard_argv([{"type": "type", "text": "hi"}])[0], helper)
        self.assertEqual(
            cu.standalone_type_argv(
                {"type": "type", "text": "-hi", "delay_ms": 0})[0], helper)
        with tempfile.TemporaryDirectory() as empty:
            with mock.patch.object(cu, "ROOT", Path(empty)):
                with self.assertRaises(RuntimeError):
                    cu.keyboard_argv([{"type": "type", "text": "hi"}])

    def test_vendored_inputs_hashes(self):
        vendor = ROOT / "native" / "vendor" / "wtype"
        self.assertEqual(
            hashlib.sha256((vendor / "main.c").read_bytes()).hexdigest(),
            "713597abfc049196864ffcc041bb6683c761b71d68ed2da86cdcfc6b7ed3d244")
        self.assertEqual(
            hashlib.sha256((vendor / "LICENSE").read_bytes()).hexdigest(),
            "e8bd6bac1b3ba6253625830bceb30c5340f74f4bc898d1bd5450596cbd8224f0")
        self.assertEqual(
            hashlib.sha256(
                (vendor / "keyboard-correction.patch").read_bytes()).hexdigest(),
            "f4cc6a9f889879f741d0c2f0769b3f1eb9b2c5685fb7781cf5f5dd8ecd02267c")

    # ---- Multi-page emitted-behavior tests (one keymap, XKB groups) ----

    def test_page_fixture_emitted_behavior(self):
        """96-symbol fixture: 193 chars decode from ONE map, groups 0-2."""
        chars = "".join(chr(n) for n in range(0x100, 0x160))
        text = chars + chars[::-1] + "\n"
        proc, dump, _, trace = self.run_traced([text])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr, b"")
        self.assertEqual(dump["group_count"], 3)
        self.assert_clean_emission(trace, text, 2)

    def test_page_fixture_all_forms(self):
        """Same 96-symbol text via direct, trailer, merged Ctrl+A, stdin."""
        chars = "".join(chr(n) for n in range(0x100, 0x160))
        text = chars + chars[::-1] + "\n"
        forms = [
            ([text], None, {}),
            ([text, "-s", "12", "-p", "VoidSymbol"], None, {}),
            (["-M", "ctrl", "-P", "A", "-s", "12", "-p", "A",
              "-m", "ctrl", "-s", "12", text, "-s", "12",
              "-p", "VoidSymbol"], None,
             {"extra_pairs": 1, "chord_keys": (30,)}),
            (["-", "-p", "VoidSymbol"], text.encode("utf-8"), {}),
        ]
        for argv, payload, kw in forms:
            with self.subTest(argv=argv[:2]):
                proc, dump, _, trace = self.run_traced(argv, payload)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(dump["group_count"], 3)
                self.assert_clean_emission(trace, text, 2, **kw)

    def test_four_group_188_symbol_fixture(self):
        """188 distinct pool literals: 377 chars, groups 0-3, one upload."""
        chars = distinct_chars(188)
        text = chars + chars[::-1] + "\n"
        proc, dump, _, trace = self.run_traced([text])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr, b"")
        self.assertEqual(dump["group_count"], 4)
        self.assert_clean_emission(trace, text, 3)

    def test_group_alternation_first_last_slots(self):
        """Repeated jumps between the first/last slots of all four groups.

        Interleaves all 188 distinct literals so every group is used on
        nearly every step (group_count 4), not just 8 distinct chars.
        """
        chars = distinct_chars(188)
        forward = "".join(
            chars[i] + chars[47 + i] + chars[94 + i] + chars[141 + i]
            for i in range(47))
        text = forward + forward[::-1] + "\n"
        proc, dump, _, trace = self.run_traced([text])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(dump["group_count"], 4)
        self.assert_clean_emission(trace, text, 3)

    def test_boundaries_no_reservation(self):
        """N=47: 47/48/188 accepted, 189 refused before any protocol call."""
        for n, groups in ((47, 1), (48, 2), (188, 4)):
            with self.subTest(n=n):
                text = distinct_chars(n)
                proc, dump, _, trace = self.run_traced([text])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(dump["group_count"], groups)
                self.assert_clean_emission(trace, text, groups - 1)
        text = distinct_chars(189)
        proc, dump, keymap, trace = self.run_traced([text])
        self.assertNotEqual(proc.returncode, 0)
        self.assertIsNone(dump)
        self.assertIsNone(keymap)
        self.assertIsNone(trace)

    def test_boundaries_a_reserved(self):
        """N=46 with A reserved: 46/47/184 accepted, 185 refused pre-connect."""
        def merged(text):
            return ["-M", "ctrl", "-P", "A", "-s", "12", "-p", "A",
                    "-m", "ctrl", "-s", "12", text, "-s", "12",
                    "-p", "VoidSymbol"]
        for n, groups in ((46, 1), (47, 2), (184, 4)):
            with self.subTest(n=n):
                text = distinct_chars(n)
                proc, dump, _, trace = self.run_traced(merged(text))
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(dump["group_count"], groups)
                self.assert_clean_emission(trace, text, groups - 1,
                                           extra_pairs=1, chord_keys=(30,))
        text = distinct_chars(185)
        proc, dump, keymap, trace = self.run_traced(merged(text))
        self.assertNotEqual(proc.returncode, 0)
        self.assertIsNone(dump)
        self.assertIsNone(keymap)
        self.assertIsNone(trace)

    def test_fixed_symbols_repeat_in_every_group(self):
        """Fixed space/newline decode at group 0 between later-group keys;
        partial last group holes are VoidSymbol in the serialized map."""
        chars = "".join(chr(n) for n in range(0x100, 0x160))
        text = chars[:47] + " " + chars[47:94] + "\n" + chars[94:]
        proc, dump, keymap, trace = self.run_traced([text])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(dump["group_count"], 3)
        self.assert_clean_emission(trace, text, 2)
        self.assertIn(b'type[Group1]="ONE_LEVEL"', keymap)
        self.assertIn(b'symbols[Group1]=[Amacron]', keymap)
        self.assertIn(b'symbols[Group2]=[space]', keymap)
        self.assertIn(b'symbols[Group3]=[VoidSymbol]', keymap)
        self.assertIn(b'symbols[Group2]=[Return]', keymap)

    def test_group_reset_before_following_chord_and_sleep(self):
        """After multi-group text, the next explicit chord runs at group 0."""
        chars = "".join(chr(n) for n in range(0x100, 0x160))
        text = chars + chars[::-1] + "\n"
        argv = [text, "-s", "12", "-M", "ctrl", "-P", "A", "-s", "12",
                "-p", "A", "-m", "ctrl", "-s", "12", "-p", "VoidSymbol"]
        proc, dump, _, trace = self.run_traced(argv)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(trace["decoded"], text)
        self.assertEqual(trace["final_group"], 0)
        chord_presses = [k for k in trace["keys"]
                         if k["state"] == KEY_PRESSED and k["dep"] == 4]
        self.assertEqual(len(chord_presses), 1)
        self.assertEqual(chord_presses[0]["key"], 30)  # canonical KeyA
        self.assertEqual(chord_presses[0]["group"], 0)
        mods = trace["modifiers"]
        nonzero_idx = [i for i, m in enumerate(mods) if m["group"] != 0]
        self.assertTrue(nonzero_idx,
                        "expected nonzero-group selections during the text")
        self.assertTrue(
            any(m["group"] == 0 for m in mods[nonzero_idx[-1] + 1:]),
            "no group-0 reset after the last nonzero-group selection")

    def test_one_group_serialization_matches_old_writer(self):
        """G==1 serialized output is byte-for-byte the old writer's."""
        cases = [
            ([SENTENCE], None, GOLDEN_SENTENCE),
            (["-M", "ctrl", "-P", "A", "-s", "12", "-p", "A",
              "-m", "ctrl", "-s", "12", SENTENCE, "-s", "12",
              "-p", "VoidSymbol"], None, GOLDEN_MERGED_A),
            (["-p", "VoidSymbol"], None, GOLDEN_SENTINEL),
            (["-", "-p", "VoidSymbol"],
             ("-" + SENTENCE).encode("utf-8"), GOLDEN_STDIN),
        ]
        for argv, payload, golden in cases:
            with self.subTest(argv=argv[:2]):
                proc, dump, keymap, _ = self.run_traced(argv, payload)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(dump["group_count"], 1)
                self.assertEqual(keymap, golden)


if __name__ == "__main__":
    unittest.main()
