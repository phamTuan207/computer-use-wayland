"""Tests for scripts/claim_check.py (Phase 2.4: 2.4.1-2.4.9)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from claim_check import (I_DONT_KNOW, ClaimCheck, check_tool_suggestion,
                         check_visible_claim)


class ClaimCheckTest(unittest.TestCase):
    def test_unverified_claim_returns_i_dont_know(self):
        checker = ClaimCheck()
        claim = checker.add("the link must use the same browser")
        self.assertTrue(
            checker.assert_or_admit(claim).startswith(I_DONT_KNOW))

    def test_verified_claim_with_source_and_date_is_assertable(self):
        checker = ClaimCheck()
        claim = checker.add("Zen is Firefox-based, no CDP endpoint")
        checker.verify(claim, source="Zen docs + live test 2026-11-21")
        self.assertEqual(checker.assert_or_admit(claim), claim.text)
        self.assertTrue(claim.assertable())

    def test_verify_requires_a_named_source(self):
        checker = ClaimCheck()
        claim = checker.add("something")
        with self.assertRaises(ValueError):
            checker.verify(claim, source="  ")

    def test_fabrication_tripwire_blocks_unverified_same_browser_claim(self):
        checker = ClaimCheck()
        claim = checker.add("confirmation must use the same browser")
        out = checker.assert_or_admit(claim)
        self.assertTrue(out.startswith(I_DONT_KNOW))
        self.assertIn("fabricated before", out)

    def test_subagent_claim_is_not_a_fact_until_checked(self):
        checker = ClaimCheck()
        claim = checker.add(
            "the Browse button is a label over a hidden input",
            origin="subagent:picker-diagnosis")
        out = checker.assert_or_admit(claim)
        self.assertTrue(out.startswith(I_DONT_KNOW))
        self.assertIn("subagent", out)
        # Checking against the screen verifies it.
        checker.verify(
            claim,
            source="screen: hovered off-centre, button darkened, click worked")
        self.assertEqual(checker.assert_or_admit(claim), claim.text)

    def test_tool_suggestion_without_evidence_is_refused(self):
        result = check_tool_suggestion("Playwright", "logged-in Zen tab")
        self.assertFalse(result["ok"])
        self.assertIn(I_DONT_KNOW, result["message"])

    def test_tool_suggestion_with_evidence_is_allowed(self):
        result = check_tool_suggestion(
            "Puppeteer BiDi", "logged-in Zen tab",
            evidence="tests/puppeteer_bidi.mjs listed live Zen tabs 2026-11-21")
        self.assertTrue(result["ok"])

    def test_no_image_claim_during_voice_call(self):
        result = check_visible_claim(False, "the new screenshot",
                                     already_received="dashboard-19-44.png")
        self.assertFalse(result["ok"])
        self.assertIn("dashboard-19-44.png", result["message"])
        self.assertIn("Do not describe or count", result["message"])

    def test_visible_claim_when_image_is_present(self):
        self.assertTrue(check_visible_claim(True, "the dashboard")["ok"])


if __name__ == "__main__":
    unittest.main()
