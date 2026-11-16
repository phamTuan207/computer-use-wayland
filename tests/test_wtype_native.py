"""Offline native tests for the vendored corrected wtype helper.

Builds the patched translation unit (patch --batch --fuzz=0, same step as
scripts/build.py) and a stub harness (tests/wtype_harness.c) that runs the
real parse_args() + kbcorr_preflight() and dumps the planned keymap
entries and command stream as JSON. No Wayland connection, no compositor,
no input sent to any application. Actual key emission is verified by the
live gates (i)-(iv), not here.

Run: python3 -B -m unittest tests.test_wtype_native -v
"""
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

    def run_harness(self, argv, input_bytes=None):
        if self.dump.exists():
            self.dump.unlink()
        env = dict(self.env, KBCORR_DUMP=str(self.dump))
        proc = subprocess.run(
            [str(self.harness), *argv], input=input_bytes,
            capture_output=True, timeout=60, env=env)
        dump = None
        if self.dump.exists():
            dump = json.loads(self.dump.read_text())
        return proc, dump

    def phys_seq(self, dump, cmd_index=0):
        """Physical codes for a TEXT command's codes, in order."""
        entries = dump["entries"]
        cmd = dump["commands"][cmd_index]
        return [entries[c - 1]["phys"] for c in cmd["codes"]]

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
            "5e40dbc831cecee1cb4cada81a26ea0b8196e5d9fdee6a14a6c0173fcff541a6")


if __name__ == "__main__":
    unittest.main()
