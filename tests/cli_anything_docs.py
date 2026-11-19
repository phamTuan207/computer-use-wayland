"""Vendored cli-anything docs; non-live, no network, no app needed.

Run directly: python3 tests/cli_anything_docs.py
(Not picked up by `python3 -m unittest discover -s tests -p 'test_*.py'`
because of the file name; it follows the repo's *_live.py explicit-run
convention instead.)

Asserts, against the vendored snapshot at skill/cli-anything/registry.json
and the vendored skill files at skill/cli-anything/<app>.md:
- the snapshot parses as JSON and lists exactly the twelve first-wave
  apps plus the repo-owned chromium wrapper (13 entries);
- exactly three upstream apps have vendored skill files (obsidian,
  libreoffice, gimp); the other nine snapshot apps are snapshot-only,
  with registry entries but no vendored skill file yet; chromium is the
  fourth skill file but repo-owned, not upstream-vendored, and states a
  repo version instead of an upstream version;
- every vendored upstream skill file states its upstream version in its
  header;
- skill/SKILL.md links to references/cli-anything.md.

NOTE: the registry's `version` for libreoffice (1.0.1) disagrees with the
vendored libreoffice skill file (header and body both say 1.0.0), so the
tests deliberately do NOT assert registry version == skill-file version.
That mismatch is a vendoring inconsistency for the coordinator, not a
property of the skill files.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "skill" / "cli-anything" / "registry.json"
SKILL_DIR = ROOT / "skill" / "cli-anything"
SKILL_MD = ROOT / "skill" / "SKILL.md"
UPSTREAM_HEAD = "34f5195"

# Wave one: only these three have vendored upstream skill files.
VENDORED_SKILLS = {"obsidian", "libreoffice", "gimp"}
# Repo-owned skill files (not upstream-vendored): the Chromium,
# Zen and VS Code wrappers.
REPO_OWNED_SKILLS = {"chromium", "zen", "vscode"}
# Registry entries but no vendored skill file yet.
SNAPSHOT_ONLY = {"inkscape", "krita", "blender", "audacity", "kdenlive",
                 "shotcut", "zotero", "joplin", "calibre"}
EXPECTED_APPS = VENDORED_SKILLS | SNAPSHOT_ONLY | REPO_OWNED_SKILLS

REQUIRED_ENTRY_KEYS = ("name", "entry_point", "install_cmd", "requires",
                       "skill_md", "version")
HEADER_VERSION_RE = re.compile(
    r"Upstream file version:\s*(\d+\.\d+(?:\.\d+)?)")
HEADER_LINES = 15


def load_registry():
    """Return {name: entry} from the vendored snapshot."""
    data = json.loads(REGISTRY.read_text())
    if isinstance(data, dict) and isinstance(data.get("clis"), list):
        entries = data["clis"]
    elif isinstance(data, dict) and data and all(
            isinstance(value, dict) for value in data.values()):
        entries = list(data.values())
    else:
        raise AssertionError("registry snapshot has an unexpected shape")
    return {entry["name"]: entry for entry in entries}


class CliAnythingDocs(unittest.TestCase):
    def test_registry_parses_and_lists_first_wave_apps(self):
        registry = load_registry()
        self.assertEqual(set(registry), EXPECTED_APPS)
        for name, entry in registry.items():
            for key in REQUIRED_ENTRY_KEYS:
                self.assertIn(key, entry, "%s is missing %r" % (name, key))
            self.assertIsInstance(entry["entry_point"], str)
            self.assertTrue(entry["entry_point"],
                            "%s has an empty entry_point" % name)
            self.assertIsInstance(entry["install_cmd"], str)
            self.assertTrue(entry["install_cmd"],
                            "%s has an empty install_cmd" % name)
            self.assertIsInstance(entry["requires"], str)
            self.assertIsInstance(entry["skill_md"], str)

    def test_registry_snapshot_is_pinned_to_upstream_head(self):
        data = json.loads(REGISTRY.read_text())
        header = data.get("header", {})
        self.assertEqual(header.get("upstream_head"), UPSTREAM_HEAD)

    def test_vendored_skills_are_exactly_the_wave_one_three_plus_repo_owned(self):
        registry = load_registry()
        vendored_files = {path.name for path in SKILL_DIR.glob("*.md")}
        self.assertEqual(vendored_files,
                         {app + ".md" for app in
                          VENDORED_SKILLS | REPO_OWNED_SKILLS})
        for app in VENDORED_SKILLS | REPO_OWNED_SKILLS:
            self.assertIn(app, registry,
                          "%s has a vendored skill but no registry entry" % app)
            self.assertTrue((SKILL_DIR / (app + ".md")).is_file())
        for app in SNAPSHOT_ONLY:
            self.assertIn(app, registry,
                          "%s is missing from the registry" % app)
            self.assertFalse((SKILL_DIR / (app + ".md")).exists(),
                             "%s must be snapshot-only in wave one" % app)

    def test_chromium_entry_is_repo_owned_and_versioned(self):
        registry = load_registry()
        entry = registry["chromium"]
        self.assertTrue(entry.get("repo_owned"),
                        "chromium registry entry must be marked repo_owned")
        self.assertEqual(entry.get("version"), "1.0.0")
        self.assertEqual(entry.get("entry_point"), "scripts/chromium_cli.py")
        text = (SKILL_DIR / "chromium.md").read_text()
        header = "\n".join(text.splitlines()[:HEADER_LINES])
        match = re.search(r"Skill version:\s*(\d+\.\d+(?:\.\d+)?)", header)
        self.assertIsNotNone(
            match, "chromium.md header states no repo skill version")
        self.assertEqual(match.group(1), "1.0.0")
        body_match = re.search(
            r"^## Version\s*\n+\s*(\d+\.\d+(?:\.\d+)?)\s*$",
            text, re.MULTILINE)
        self.assertIsNotNone(body_match, "chromium.md has no ## Version section")
        self.assertEqual(body_match.group(1), "1.0.0")

    def test_zen_entry_is_repo_owned_and_versioned(self):
        registry = load_registry()
        entry = registry["zen"]
        self.assertTrue(entry.get("repo_owned"),
                        "zen registry entry must be marked repo_owned")
        self.assertEqual(entry.get("version"), "1.0.0")
        self.assertEqual(entry.get("entry_point"), "cli-anything-zen")
        text = (SKILL_DIR / "zen.md").read_text()
        header = "\n".join(text.splitlines()[:HEADER_LINES])
        match = re.search(r"Skill version:\s*(\d+\.\d+(?:\.\d+)?)", header)
        self.assertIsNotNone(
            match, "zen.md header states no repo skill version")
        self.assertEqual(match.group(1), "1.0.0")
        body_match = re.search(
            r"^## Version\s*\n+\s*(\d+\.\d+(?:\.\d+)?)\s*$",
            text, re.MULTILINE)
        self.assertIsNotNone(body_match, "zen.md has no ## Version section")
        self.assertEqual(body_match.group(1), "1.0.0")

    def test_vscode_entry_is_repo_owned_and_versioned(self):
        registry = load_registry()
        entry = registry["vscode"]
        self.assertTrue(entry.get("repo_owned"),
                        "vscode registry entry must be marked repo_owned")
        self.assertEqual(entry.get("version"), "1.0.0")
        self.assertEqual(entry.get("entry_point"), "scripts/vscode_cli.py")
        text = (SKILL_DIR / "vscode.md").read_text()
        header = "\n".join(text.splitlines()[:HEADER_LINES])
        match = re.search(r"Skill version:\s*(\d+\.\d+(?:\.\d+)?)", header)
        self.assertIsNotNone(
            match, "vscode.md header states no repo skill version")
        self.assertEqual(match.group(1), "1.0.0")
        body_match = re.search(
            r"^## Version\s*\n+\s*(\d+\.\d+(?:\.\d+)?)\s*$",
            text, re.MULTILINE)
        self.assertIsNotNone(body_match, "vscode.md has no ## Version section")
        self.assertEqual(body_match.group(1), "1.0.0")

    def test_vendored_skills_state_upstream_version(self):
        for app in sorted(VENDORED_SKILLS):
            text = (SKILL_DIR / (app + ".md")).read_text()
            header = "\n".join(text.splitlines()[:HEADER_LINES])
            match = HEADER_VERSION_RE.search(header)
            self.assertIsNotNone(
                match, "%s.md header states no upstream version" % app)
            header_version = match.group(1)
            body_match = re.search(
                r"^## Version\s*\n+\s*(\d+\.\d+(?:\.\d+)?)\s*$",
                text, re.MULTILINE)
            self.assertIsNotNone(
                body_match, "%s.md has no ## Version section" % app)
            self.assertEqual(body_match.group(1), header_version,
                             "%s.md header and body versions disagree" % app)

    def test_skill_md_links_cli_anything_reference(self):
        self.assertIn("references/cli-anything.md", SKILL_MD.read_text())


if __name__ == "__main__":
    unittest.main()
