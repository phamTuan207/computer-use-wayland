#!/usr/bin/env python3
"""Unit tests for arch-guard.py (I13).

Run: python3 rung3-ci/test-arch-guard.py
"""
import importlib.util
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "arch_guard", os.path.join(HERE, "arch-guard.py"))
ag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ag)


class ImportMapTests(unittest.TestCase):
    def test_unlisted_import_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "scripts"))
            with open(os.path.join(d, "scripts", "a.py"), "w") as fh:
                fh.write("import b\n")
            with open(os.path.join(d, "scripts", "b.py"), "w") as fh:
                fh.write("X = 1\n")
            map_path = os.path.join(d, "map.txt")
            with open(map_path, "w") as fh:
                fh.write("a: \nb: \n")
            violations = ag.check_imports(root=d, map_path=map_path)
            self.assertEqual(len(violations), 1)
            self.assertIn("imports b", violations[0])
            with open(map_path, "w") as fh:
                fh.write("a: b\nb: \n")
            self.assertEqual(ag.check_imports(root=d, map_path=map_path),
                             [])


class MachineValueTests(unittest.TestCase):
    def test_denylist_hits_and_allowlist(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "scripts"))
            with open(os.path.join(d, "scripts", "x.py"), "w") as fh:
                fh.write('P = "/home/someone/secret"\n')
            os.makedirs(os.path.join(d, "tests", "fixtures"))
            with open(os.path.join(d, "tests", "fixtures", "f.py"),
                      "w") as fh:
                fh.write('P = "/home/someone/fake"\n')
            violations = ag.scan_machine_values(root=d)
            self.assertEqual(len(violations), 1)
            self.assertIn("scripts/x.py", violations[0])


# Synthetic name fragments, assembled at runtime so no test
# fixture contains the real personal name or handle as a
# contiguous literal.
_A = "Ph" + "am"
_B = "Tu" + "an"
_C = "Hu" + "y"
_FULL = _A + " " + _B + " " + _C
_DIAC_A = "Ph" + chr(0x1EA1) + "m"
_DIAC_B = "Tu" + chr(0x1EA5) + "n"
_HANDLE = _A.lower() + _B + "207"


class MachineValueEvasionTests(unittest.TestCase):
    def scan_files(self, files):
        with tempfile.TemporaryDirectory() as d:
            for rel, content in files.items():
                path = os.path.join(d, rel)
                parent = os.path.dirname(path)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                if isinstance(content, bytes):
                    with open(path, "wb") as fh:
                        fh.write(content)
                else:
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(content)
            return ag.scan_machine_values(root=d)

    def test_personal_name_case_variants_caught(self):
        variants = [_FULL.lower(), _FULL.upper(),
                    _DIAC_A.lower(), _DIAC_B.upper()]
        for variant in variants:
            violations = self.scan_files(
                {"scripts/x.py": "N = %r\n" % variant})
            self.assertEqual(len(violations), 1, variant)
            self.assertIn("personal-name", violations[0])

    def test_personal_name_joined_forms_caught(self):
        variants = [_A + _B + _C, _A + "-" + _B + "-" + _C,
                    _A + "_" + _B + "_" + _C, _A + "-" + _B,
                    _B + _C]
        for variant in variants:
            violations = self.scan_files(
                {"scripts/x.py": "N = %r\n" % variant})
            self.assertEqual(len(violations), 1, variant)
            self.assertIn("personal-name", violations[0])

    def test_handle_not_flagged(self):
        content = ("clone https://github.com/%s/repo and user %s\n"
                   % (_HANDLE, _HANDLE))
        self.assertEqual(self.scan_files({"README.md": content}), [])

    def test_home_path_capital_and_bare_caught(self):
        cases = ['P = "/home/Bob/x"\n', 'P = "/home/alice"\n',
                 "home is /home/carol\n"]
        for content in cases:
            violations = self.scan_files({"scripts/x.py": content})
            self.assertEqual(len(violations), 1, content)
            self.assertIn("home-path", violations[0])

    def test_home_path_split_literals_caught(self):
        cases = ['P = "/home/" + "dave/x"\n',
                 'P = "/home/" "erin/x"\n']
        for content in cases:
            violations = self.scan_files({"scripts/x.py": content})
            self.assertEqual(len(violations), 1, content)
            self.assertIn("home-path", violations[0])

    def test_values_split_across_lines_caught(self):
        md = "name: %s\n%s %s\n" % (_A, _B, _C)
        violations = self.scan_files({"docs/n.md": md})
        self.assertEqual(len(violations), 1)
        self.assertIn("personal-name", violations[0])
        py = 'P = "/home/" +\n    "frank/x"\n'
        violations = self.scan_files({"scripts/x.py": py})
        self.assertEqual(len(violations), 1)
        self.assertIn("home-path", violations[0])

    def test_invalid_utf8_still_scanned(self):
        violations = self.scan_files(
            {"scripts/x.py": b'\xff\xfeP = "/home/grace/x"\n'})
        self.assertEqual(len(violations), 1)
        self.assertIn("home-path", violations[0])

    def test_new_suffixes_scanned(self):
        files = {"scripts/a.lua": 'P = "/home/heidi/x"\n',
                 "docs/b.html": '<a href="/home/ivan/x">x</a>\n',
                 "docs/c.css": '.x { background: "/home/judy/x"; }\n',
                 "native/d.c": 'char *p = "/home/karl/x";\n',
                 "scripts/pre-commit": "#!/bin/sh\nP=/home/liam/x\n"}
        violations = self.scan_files(files)
        self.assertEqual(len(violations), 5)
        for rel in files:
            self.assertTrue(any(rel in v for v in violations), rel)

    def test_new_trees_scanned(self):
        files = {".github/workflows/w.yml": "path: /home/mona/x\n",
                 "tests/t.py": 'P = "/home/nina/x"\n',
                 "NOTES.md": "see /home/omar/x\n"}
        violations = self.scan_files(files)
        self.assertEqual(len(violations), 3)
        for rel in files:
            self.assertTrue(any(rel in v for v in violations), rel)

    def test_phase0_trees_scanned(self):
        # Phase 0 (2026-11-28): improvements/, coord/, probes/,
        # snippets/ and rung3-run-log/ joined the scan scope.
        files = {"improvements/a.md": "path: /home/paul/x\n",
                 "coord/b.md": "path: /home/quinn/x\n",
                 "probes/c.py": 'P = "/home/ruth/x"\n',
                 "snippets/d.md": "path: /home/sara/x\n",
                 "rung3-run-log/e.md": "path: /home/tom/x\n"}
        violations = self.scan_files(files)
        self.assertEqual(len(violations), 5)
        for rel in files:
            self.assertTrue(any(rel in v for v in violations), rel)

    def test_vietnamese_common_words_pass(self):
        # The bare surname syllable also appears in the common
        # words for "violation" and "scope"; those are not name
        # references and must pass (Phase 0 precision fix).
        surname = _DIAC_A.lower()
        passing = ["vi " + surname + " V1-V13\n",
                   "Vi " + surname + " dung\n",
                   "VI " + surname.upper() + " DUNG\n",
                   surname + " vi kiem tra\n",
                   _DIAC_A + " vi: rong\n",
                   "ngoai " + surname + " vi\n"]
        for text in passing:
            self.assertEqual(
                self.scan_files({"improvements/n.md": text}), [],
                text)
        # True name forms and other compounds still hit.
        hitting = [_DIAC_A + " " + _DIAC_B + " ordered\n",
                   _DIAC_B + " said\n",
                   "xam " + surname + "\n",
                   surname + " toi\n"]
        for text in hitting:
            violations = self.scan_files(
                {"improvements/n.md": text})
            self.assertEqual(len(violations), 1, text)
            self.assertIn("personal-name", violations[0])

    def test_tailscale_bare_caught_range_doc_allowed(self):
        violations = self.scan_files(
            {"docs/n.md": "addr 100.99.88.77 here\n"})
        self.assertEqual(len(violations), 1)
        self.assertIn("tailscale-ip", violations[0])
        self.assertEqual(self.scan_files(
            {"docs/n.md": "range 100.64.0.0/10 documented\n"}), [])

    def test_legitimate_homes_pass(self):
        content = ('A = "/home/user/x"\nB = "/home/demo"\n'
                   'C = "/home/testuser/y"\n')
        self.assertEqual(self.scan_files({"scripts/x.py": content}),
                         [])

    def test_profile_dir_caught_redacted_passes(self):
        violations = self.scan_files(
            {"docs/n.md": "profile abcd1234.Default here\n"})
        self.assertEqual(len(violations), 1)
        self.assertIn("profile-dir", violations[0])
        self.assertEqual(self.scan_files(
            {"docs/n.md": "profile ********.Default here\n"}), [])


class ImportEvasionTests(unittest.TestCase):
    def import_violations(self, files, map_text):
        with tempfile.TemporaryDirectory() as d:
            for rel, content in files.items():
                path = os.path.join(d, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(content)
            map_path = os.path.join(d, "map.txt")
            with open(map_path, "w", encoding="utf-8") as fh:
                fh.write(map_text)
            return ag.check_imports(root=d, map_path=map_path)

    def test_import_module_flagged(self):
        files = {"scripts/a.py": "import importlib\n"
                                 "importlib.import_module('b')\n",
                 "scripts/b.py": "X = 1\n"}
        violations = self.import_violations(files, "a: \nb: \n")
        self.assertEqual(len(violations), 1)
        self.assertIn("imports b", violations[0])
        self.assertEqual(
            self.import_violations(files, "a: b\nb: \n"), [])

    def test_dunder_import_flagged(self):
        files = {"scripts/a.py": "__import__('b')\n",
                 "scripts/b.py": "X = 1\n"}
        violations = self.import_violations(files, "a: \nb: \n")
        self.assertEqual(len(violations), 1)
        self.assertIn("imports b", violations[0])

    def test_spec_from_file_location_flagged(self):
        direct = {"scripts/a.py":
                  "import importlib.util\n"
                  "s = importlib.util.spec_from_file_location"
                  "('b', 'b.py')\n",
                  "scripts/b.py": "X = 1\n"}
        violations = self.import_violations(direct, "a: \nb: \n")
        self.assertEqual(len(violations), 1)
        self.assertIn("imports b", violations[0])
        via_var = {"scripts/a.py":
                   "import importlib.util\n"
                   "from pathlib import Path\n"
                   "p = Path('scripts') / 'b.py'\n"
                   "s = importlib.util.spec_from_file_location"
                   "('b', p)\n",
                   "scripts/b.py": "X = 1\n"}
        violations = self.import_violations(via_var, "a: \nb: \n")
        self.assertEqual(len(violations), 1)
        self.assertIn("imports b", violations[0])

    def test_run_path_flagged(self):
        files = {"scripts/a.py": "import runpy\n"
                                 "runpy.run_path('b.py')\n",
                 "scripts/b.py": "X = 1\n"}
        violations = self.import_violations(files, "a: \nb: \n")
        self.assertEqual(len(violations), 1)
        self.assertIn("imports b", violations[0])

    def test_loader_helper_flagged(self):
        files = {"scripts/a.py":
                 "import importlib.util\n"
                 "def _load(name, filename):\n"
                 "    s = importlib.util.spec_from_file_location"
                 "(name, filename)\n"
                 "    m = importlib.util.module_from_spec(s)\n"
                 "    s.loader.exec_module(m)\n"
                 "    return m\n"
                 "mod = _load('b', 'b.py')\n",
                 "scripts/b.py": "X = 1\n"}
        violations = self.import_violations(files, "a: \nb: \n")
        self.assertEqual(len(violations), 1)
        self.assertIn("imports b", violations[0])

    def test_syntax_error_fails_closed(self):
        files = {"scripts/a.py": "def broken(:\n"}
        violations = self.import_violations(files, "a: \n")
        self.assertEqual(len(violations), 1)
        self.assertIn("unparseable", violations[0])

    def test_subdir_imports_guarded(self):
        files = {"scripts/sub/c.py": "import d\n",
                 "scripts/sub/d.py": "X = 1\n"}
        violations = self.import_violations(
            files, "sub/c: \nsub/d: \n")
        self.assertEqual(len(violations), 1)
        self.assertIn("imports sub/d", violations[0])
        self.assertEqual(self.import_violations(
            files, "sub/c: sub/d\nsub/d: \n"), [])
        files2 = {"scripts/sub/c.py": "import e\n",
                  "scripts/e.py": "X = 1\n"}
        violations = self.import_violations(
            files2, "sub/c: \ne: \n")
        self.assertEqual(len(violations), 1)
        self.assertIn("imports e", violations[0])

    def test_dynamic_nonlocal_ignored(self):
        files = {"scripts/a.py":
                 "import importlib\n"
                 "importlib.import_module('os')\n"
                 "import importlib.util\n"
                 "s = importlib.util.spec_from_file_location"
                 "('x', 'outside.py')\n"}
        self.assertEqual(
            self.import_violations(files, "a: \n"), [])


if __name__ == "__main__":
    unittest.main()
