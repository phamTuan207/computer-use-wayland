#!/usr/bin/env python3
"""Spare scorer record validation (M10 reduced).

Validates one run's spare-scorer record (schema in
rung3-ci/spare-scorer.md) using only the standard library.
Checks:
  - run_code has the ledger run-code shape (R3-L<number>);
  - spare_scorers holds exactly one named spare (one named spare
    per run, never a pool);
  - the spare's session differs from every runner session, every
    seated scorer session, and the coordinator session;
  - the independence declaration is recorded as on file;
  - calibration is 4/4 with verdict APPROVED, the verifier session
    differs from the spare's session and the coordinator's, and the
    named sign-off file exists and itself carries 4/4 and APPROVED;
  - standing_warm_seat is present and false (no standing warm
    seat, ever);
  - signed_at, and first_assignment_at when set, are
    timezone-aware ISO timestamps, assignment at or after sign-off
    (the spare scores nothing before its sign-off);
  - no cap_hours_claimed / cap_hours_saved field anywhere in the
    record carries a non-zero value (claims no cap hours, ever).

Usage:
  python3 rung3-ci/check-spare-scorer.py <spare-record.json>
Sign-off paths are resolved relative to the current directory
first, then relative to the repo root (the parent of rung3-ci/).
Exit 0 when the record is valid, 1 with the errors listed,
2 on usage errors. No personal info in this file.
"""
import json
import os
import re
import sys
from datetime import datetime

RUN_RE = re.compile(r"^R3-L[0-9]+$")
CAP_CLAIM_KEYS = ("cap_hours_claimed", "cap_hours_saved")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def parse_ts(value, field, errors):
    if not isinstance(value, str) or not value:
        errors.append("%s must be a non-empty ISO timestamp string" % field)
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        errors.append("%s is not a valid ISO timestamp: %s" % (field, value))
        return None
    if dt.tzinfo is None:
        errors.append("%s must carry a timezone offset: %s" % (field, value))
        return None
    return dt


def find_cap_claims(obj, path, errors):
    if isinstance(obj, dict):
        for key, val in obj.items():
            here = "%s.%s" % (path, key) if path else key
            if key in CAP_CLAIM_KEYS and val not in (None, 0, 0.0, False):
                errors.append("%s claims cap hours (%r); M10 reduced "
                              "claims no cap hours, ever" % (here, val))
            find_cap_claims(val, here, errors)
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            find_cap_claims(val, "%s[%d]" % (path, i), errors)


def resolve_signoff(path):
    for cand in (path, os.path.join(ROOT, path)):
        if os.path.isfile(cand):
            return cand
    return None


def validate(record):
    errors = []
    if not isinstance(record, dict):
        return ["record is not a JSON object"]
    find_cap_claims(record, "", errors)

    if not RUN_RE.match(record.get("run_code") or ""):
        errors.append("bad run_code %r" % record.get("run_code"))
    coordinator = record.get("coordinator_session")
    if not isinstance(coordinator, str) or not coordinator:
        errors.append("coordinator_session must be a non-empty string")

    seated = set()
    for field in ("runner_sessions", "seated_scorer_sessions"):
        vals = record.get(field)
        if not isinstance(vals, list) or \
                not all(isinstance(v, str) and v for v in vals):
            errors.append("%s must be a list of non-empty strings" % field)
        else:
            seated.update(vals)

    spares = record.get("spare_scorers")
    if not isinstance(spares, list) or len(spares) != 1:
        errors.append("spare_scorers must hold exactly one named spare, "
                      "found %s" % (len(spares) if isinstance(spares, list)
                                     else type(spares).__name__))
        return errors
    spare = spares[0]
    if not isinstance(spare, dict):
        return errors + ["spare entry is not a JSON object"]

    if not isinstance(spare.get("name"), str) or not spare.get("name"):
        errors.append("spare name must be a non-empty string")
    session = spare.get("session")
    if not isinstance(session, str) or not session:
        errors.append("spare session must be a non-empty string")
    else:
        if session == coordinator:
            errors.append("spare session equals coordinator session")
        if session in seated:
            errors.append("spare session %s is already a runner or "
                          "seated scorer session" % session)
    if spare.get("independence_declaration") is not True:
        errors.append("independence_declaration must be true "
                      "(declaration on file before calibration)")
    if spare.get("standing_warm_seat") is not False:
        errors.append("standing_warm_seat must be present and false "
                      "(no standing warm seat)")

    cal = spare.get("calibration")
    signed_at = None
    if not isinstance(cal, dict):
        errors.append("calibration must be an object")
    else:
        if cal.get("agreement") != "4/4":
            errors.append("calibration agreement must be 4/4, found %r"
                          % cal.get("agreement"))
        if cal.get("verdict") != "APPROVED":
            errors.append("calibration verdict must be APPROVED, found %r"
                          % cal.get("verdict"))
        verifier = cal.get("verifier_session")
        if not isinstance(verifier, str) or not verifier:
            errors.append("verifier_session must be a non-empty string")
        else:
            if verifier == session:
                errors.append("verifier session equals spare session "
                              "(verifier re-grades independently)")
            if verifier == coordinator:
                errors.append("verifier session equals coordinator session "
                              "(sign-off is not the coordinator's own check)")
        signed_at = parse_ts(cal.get("signed_at"), "calibration.signed_at",
                             errors)
        signoff = cal.get("signoff_file")
        if not isinstance(signoff, str) or not signoff:
            errors.append("calibration.signoff_file must be a non-empty path")
        else:
            found = resolve_signoff(signoff)
            if found is None:
                errors.append("sign-off file not found: %s" % signoff)
            else:
                with open(found, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
                if "4/4" not in text:
                    errors.append("sign-off file %s does not carry 4/4"
                                  % signoff)
                if "APPROVED" not in text:
                    errors.append("sign-off file %s does not carry APPROVED"
                                  % signoff)

    first = spare.get("first_assignment_at")
    if first is not None:
        first_dt = parse_ts(first, "first_assignment_at", errors)
        if first_dt is not None and signed_at is not None \
                and first_dt < signed_at:
            errors.append("first_assignment_at %s precedes calibration "
                          "sign-off %s; the spare scores nothing before "
                          "its sign-off" % (first, cal.get("signed_at")))
    return errors


def main(argv):
    if len(argv) != 2:
        print("usage: check-spare-scorer.py <spare-record.json>",
              file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            record = json.load(fh)
    except (OSError, ValueError) as exc:
        print("SPARE SCORER FAIL: cannot read record: %s" % exc)
        return 1
    errors = validate(record)
    if errors:
        for err in errors:
            print("SPARE SCORER FAIL: %s" % err)
        return 1
    spare = record["spare_scorers"][0]
    print("SPARE SCORER OK: %s (%s) calibrated 4/4 APPROVED, "
          "no standing warm seat" % (spare["name"], spare["session"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
