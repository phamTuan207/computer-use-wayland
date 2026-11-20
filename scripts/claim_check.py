"""No-fabrication guard: say "I don't know" instead of inventing a fact.

Fixes all of Phase 2.4:
- 2.4.1 (A7/I17): fabricated "same browser required" for a confirmation link.
- 2.4.2 (I18): attributed a verification-fail rule to Hieu; it was Muse's own.
- 2.4.3 (I19): fabricated "native dialog doesn't accept clicks", "separate window".
- 2.4.4 (I22): relayed a subagent's wrong file-picker diagnosis as fact.
- 2.4.5 (I23): fabricated Add to Contest via UID, Share button, Package prerequisite.
- 2.4.6 (I24): guessed "enumerated incorrectly is just a warning"; it blocks packaging.
- 2.4.7 (I25): claimed to see images during a voice call when it could not; miscounted.
- 2.4.8 (I26): suggested Playwright, then admitted Zen has no CDP.
- 2.4.9 (A8): never verified claims against sources; every claim needs source + date.

Rules enforced here, in code rather than in a prompt that can be ignored:
1. A claim is only assertable with a source and an access date. Anything
   else is UNVERIFIED and must be said as "I don't know" or "unverified".
2. A subagent's diagnosis is never relayed as fact. It is relayed as
   "subagent X claims Y, unverified" until checked against the screen or
   the source (I22).
3. A tool suggestion must cite capability evidence: the tool, the target,
   and the evidence the tool can actually drive that target (I26: Zen is
   Firefox, Firefox has no CDP, Playwright cannot attach to a logged-in
   Zen tab).
4. Never claim to perceive something the current channel cannot show.
   During a voice call there is no new image; only images already received
   exist (I25). Counts come from the image actually in front of you, and
   a count must be re-counted before it is asserted.
5. Read the tooltip / error text before characterising it. "Enumerated
   incorrectly" says "Package can not be built" in its tooltip: that is
   a blocker, not a warning (I24). Guessing the severity is fabrication.
"""
from dataclasses import dataclass, field
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:  # pragma: no cover
    from datetime import timezone
    TZ = timezone.utc

I_DONT_KNOW = "I don't know"

# Patterns that were actually fabricated in the 20/11 session, kept as a
# tripwire list. A claim matching one of these shapes must produce its
# source before it is asserted; without a source it is refused.
FABRICATION_TRIPWIRES = (
    "must use the same browser",
    "required to use the same browser",
    "native dialog does not accept clicks",
    "separate window of the browser",
    "only a warning",
    "just a warning",
    "verification fail means stop",
    "must have a package first",
    "add to contest via uid",
    "share button",
)


def today_text(now=None):
    moment = now or datetime.now(TZ)
    return moment.strftime("%Y-%m-%d")


@dataclass
class Claim:
    text: str
    source: str = ""
    accessed: str = ""
    origin: str = "self"  # self | subagent:<id> | user | tutorial | screen
    status: str = "unverified"

    def assertable(self):
        return bool(self.source and self.accessed
                    and self.status == "verified")


@dataclass
class ClaimCheck:
    """Registry for every factual claim an agent wants to assert.

    The point is the pause: to assert, the agent must write down the
    source and the date it was checked. A claim with no source cannot be
    asserted, and the correct output is "I don't know", not a plausible
    technical-sounding reason (I19: the agent invented "native dialog"
    and "separate window" to fill a gap it should have left empty).
    """
    claims: list = field(default_factory=list)

    def add(self, text, *, source="", accessed="", origin="self"):
        claim = Claim(text=text, source=source,
                      accessed=accessed or today_text(), origin=origin)
        self.claims.append(claim)
        return claim

    def verify(self, claim, *, source, accessed=None):
        """Mark verified against a source the checker actually consulted.

        ``source`` must name where it was checked (a file, a URL, the
        screen, a tutorial timestamp), not a vague "docs". A subagent's
        word is not a source: relaying it keeps origin=subagent and
        status=unverified until the screen or the primary source confirms
        it (I22).
        """
        if not source or not source.strip():
            raise ValueError("verification needs a named source")
        claim.source = source
        claim.accessed = accessed or today_text()
        claim.status = "verified"
        return claim

    def tripwire_hit(self, text):
        lowered = text.lower()
        return [t for t in FABRICATION_TRIPWIRES if t in lowered]

    def assert_or_admit(self, claim):
        """Return the claim text if assertable, else the honest fallback.

        This is the function to call before sending any factual sentence
        to the user or to a worker. An unverified claim is not softened,
        hedged, or dressed as a technical explanation: it is replaced
        with "I don't know" plus what would settle it.
        """
        if self.tripwire_hit(claim.text) and not claim.assertable():
            return (f"{I_DONT_KNOW}: '{claim.text}' matches a pattern "
                    f"fabricated before and has no verified source. "
                    f"To settle it, check the primary source or the "
                    f"screen and record source + date.")
        if not claim.assertable():
            origin_note = ""
            if claim.origin.startswith("subagent"):
                origin_note = (f" This came from {claim.origin}; a "
                               f"subagent claim is not a fact until "
                               f"checked (I22).")
            return (f"{I_DONT_KNOW}: no verified source for "
                    f"'{claim.text}'.{origin_note} "
                    f"Check the source and record it before asserting.")
        return claim.text


def check_tool_suggestion(tool, target, *, evidence=""):
    """Research before suggesting (I26).

    A tool suggestion needs capability evidence: the tool, the target,
    and proof the tool can drive that target. "Playwright is faster"
    with no evidence is a guess; the evidence on record is that Zen is
    Firefox, Firefox has no CDP, and Playwright cannot attach to a
    logged-in Zen tab. Without evidence, the suggestion is refused and
    the honest answer is to research first.
    """
    if not evidence or not evidence.strip():
        return {"ok": False,
                "message": (f"{I_DONT_KNOW} whether {tool} can drive "
                            f"{target}: no capability evidence. Research "
                            f"the tool against this target first, then "
                            f"suggest it with the evidence attached.")}
    return {"ok": True, "tool": tool, "target": target,
            "evidence": evidence}


def check_visible_claim(can_see_now, what, *, already_received=None):
    """Never claim to see what the current channel cannot show (I25).

    During a voice call there is no new image. Only images already
    received exist. If ``can_see_now`` is False, any claim about a new
    image is refused, and the caller must say it is working from an
    earlier image, named explicitly.
    """
    if can_see_now:
        return {"ok": True, "what": what}
    if already_received:
        return {"ok": False,
                "message": (f"{I_DONT_KNOW} what the new image shows: "
                            f"this channel shows no image right now. "
                            f"Working only from the earlier image "
                            f"'{already_received}'. Do not describe or "
                            f"count anything in an image not received.")}
    return {"ok": False,
            "message": (f"{I_DONT_KNOW} what the image shows: no image "
                        f"is visible in this channel right now.")}
