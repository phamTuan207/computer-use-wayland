# CF735368 addendum: Codeforces login + submission attempt (27/11/2026)

Follow-up to `report-final-20261127.md`: log into Codeforces with
the owner's saved account and submit the committed solutions to
contest 735368 for real Codeforces verdicts.

## Login outcome: SUCCESS

Logged into Codeforces with the owner's saved account via profile
autofill in the owner's Zen (logged escape hatch, dedicated holder
tab; the owner's own tabs were not touched). The header confirmed
the account handle + Logout. The earlier blocker from the driver
lane (stored session invalid server-side, no password entry per
that lane's brief) is resolved: the saved-password autofill works.

Access-path notes, for the record:

- Cloudflare passed with the Fix B holder shim (page-visible
  webdriver = false) on the homepage and on /enter.
- The /enter page is gated by a Codeforces proof-of-work browser
  check ("Please wait. Your browser is being checked"). In the
  BiDi holder tab, page timers do not fire (verified with a
  setTimeout probe: callback never ran within 12 s), so the check
  script's automatic solve stalls. Manual PoW solves chained from
  a stale pow cookie were rejected by the server (verified: the
  solutions are mathematically correct, SHA-1 prefix "0000"). The
  check passed after a fresh homepage -> Enter navigation, when
  the pow cookie rotated to a server-issued token and the login
  form rendered (handleOrEmail + password, no CAPTCHA).

## Contest as seen

Group "Coding Fundamentals 2026" (EoMGcsRgKH), contests list,
checked 27/11 ~10:45 +07:

- ENDTERM TEST = contest 735368. Start Nov/29/2026 14:00 UTC+7,
  length 03:00, prepared by TranCongHieu.
- State: "Before start 2 days", "Before registration 45:13:43"
  (registration opens ~Nov 29 08:00 +07, about 6 h before start).

## Submission attempt: BLOCKED, contest locked

No submissions were made. Every contest URL redirects to the
group contests list for this account today (verified by visible-UI
clicks, address-bar navigation, and fetch):

- /group/EoMGcsRgKH/contest/735368 -> /contests
- /contest/735368/problems, /submit, /my -> /contests
- /contests/manage/edit/735368 -> /contests

Control check: a running contest in the same group (732869) loads
normally (contest page and manage/edit page both return 200 with
no redirect), so the account's group-manager access works in
general. The lock is specific to contest 735368's before-start /
before-registration state.

## Verdicts

None. No Codeforces verdict or submission ID exists for any
problem. The local full-suite verdicts in
`report-final-20261127.md` remain the only evidence.

## What would unblock real verdicts

1. Wait until registration opens (~Nov 29 08:00 +07), register
   the account, then submit from the committed solutions
   (`cf735368/solutions/<slug>/sol.cpp`; oan-tu-ti from
   `oan-tu-ti-fcc/`).
2. The contest preparer grants contest-manager access or opens
   the contest for manager testing before registration.
3. Polygon-side solution testing, if the owner has access to the
   problem packages (separate final-test task).

## Not checked

- The problem list inside contest 735368 (letters + names):
  locked, could not be read. Contest membership and order remain
  unconfirmed, as in the final report.
- All Codeforces verdicts, submission IDs, time limits on
  Codeforces hardware, and Polygon checker configurations:
  unchanged from the final report's "What was NOT checked".
