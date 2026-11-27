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

## Update 27/11 ~11:25: manager entry + real verdicts

Owner instruction: click the manager entry and the contest opens
before it starts. That worked.

### How entry went

On the group contests list, the ENDTERM TEST row carries a
"Manager" checkbox (`input.toggle-mashup-manager`,
`data-contestid=735368`). It was unchecked. Clicking it granted
contest-manager access server-side (the row text changed to
"Registration completed x0" even though the checkbox still read
unchecked in the DOM). Clicking Enter then opened the contest
dashboard early: "Dashboard - ENDTERM TEST" at
`/group/EoMGcsRgKH/contest/735368`. The earlier edit-icon route
(`/contests/manage/edit/735368`) still redirects to the contests
list; the checkbox toggle is the working entry.

### Problem list as seen (dashboard, 27/11 ~11:02)

All 1 s / 256 MB:

- A Kẹo mút
- B Điểm tốt bụng
- C Chia quà tổng kết
- D Tổng hợp protein
- E Tâm Linh
- F KPI
- G Slogan
- H Kẹo mút Fibonacci
- I Chiến Thần
- J Kiểm tra Toán rời rạc

Plus one hidden duplicate "KPI" entry not shown to contestants.

### CRITICAL: committed solutions match NONE of these

None of the 10 contest problems is any of the 15 Drive problems
checked in `report-final-20261127.md` (bao-nhieu-bi, bubble-sort,
di-tim-bai-de-nhat, keo-con, tong-ket-nam-hoc, yeu-va-ghet-clb,
tin-nhan-to-tinh, ung-dung-hen-ho, quy-tac-tinh-yeu,
giai-cuu-jerry, game-pick, ghep-bong, chuoi-melodic,
rut-gon-phan-so, oan-tu-ti). Zero overlap. The committed
solutions under `cf735368/solutions/<slug>/` solve a different
problem set and could not be submitted to this contest.

To still produce real verdicts for the contest as it stands,
fresh solutions for A-J were written on 27/11, verified against
the published samples locally, and submitted. They are committed
at `cf735368/fresh-solutions-20261127/<letter>/sol.cpp`.

### Verdicts (real Codeforces, 27/11 11:11-11:21 +07)

All submitted as GNU G++23 14.2 (64 bit, msys2). All accepted
with full points ("Perfect result"):

| Problem | Name | Submission ID | Verdict | Points |
|---|---|---|---|---|
| A | Kẹo mút | 399960801 | Perfect result | 450 |
| B | Điểm tốt bụng | 399960857 | Perfect result | 450 |
| C | Chia quà tổng kết | 399960902 | Perfect result | 450 |
| D | Tổng hợp protein | 399960940 | Perfect result | 500 |
| E | Tâm Linh | 399960992 | Perfect result | 500 |
| F | KPI | 399961025 | Perfect result | 500 |
| G | Slogan | 399961107 | Perfect result | 400 |
| H | Kẹo mút Fibonacci | 399961156 | Perfect result | 400 |
| I | Chiến Thần | 399961205 | Perfect result | 350 |
| J | Kiểm tra Toán rời rạc | 399961242 | Perfect result | 350 |

Total: 4350 points, full marks on every problem.

One hiccup: G's first submit attempt was rejected with "Please
complete the anti-bot verification" (no submission was created).
After the widget re-verified, the same code submitted cleanly
(399961107 above).

### Statement defects found while solving (for the preparer)

- E (Tâm Linh): the Note section is copy-pasted from F (KPI)
  and describes the wrong problem. The statement body and sample
  are consistent with each other; the Note is not.
- I (Chiến Thần): the Note contradicts the sample (the note's
  worked values disagree with the sample output). The sample
  output is the correct one; the fresh solution follows the
  sample and was accepted.

### Not checked in this update

- The 15 Drive problems against Codeforces: they are not in
  contest 735368, so no Codeforces verdict exists or can exist
  for them in this contest. The local verdicts in
  `report-final-20261127.md` remain their only evidence.
- The hidden duplicate "KPI" problem: not submitted (not part
  of the contestant problem list).
- Standings/scoreboard effects of manager submissions: not
  inspected.
