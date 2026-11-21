# Council Voice 3: Y14b fix-pass review (plan/log fixes only)

Scope: the FIX DIFF ONLY, commit 8bee524 plus ebe5853 (log hash record
only), on todolist-push. My scope is the plan/log fixes: predecessor
Council 3 paper 41fa919 fixes F1-F7, the H2/H3 claim correction, the H4
margin note, the adjudication section, and the recorded fix-commit
hashes. I did NOT re-review the runner code fixes (H1/M1/M2/M3/L1,
gate, H4 move) except where a plan sentence makes a claim about the
code; those verdicts belong to the other fix-pass reviewers.

Scope correction, recorded: the brief says "8bee524 vs its parent
f732d6a". That is not the parentage. 8bee524's parent is 431b2a9
(`git rev-parse 8bee524^` = 431b2a969cb6fbcd4018bf7029519e35d0ecf3e6);
f732d6a is the re-stage commit itself, an ancestor. The fix diff I
reviewed is 431b2a9..8bee524 (3 files: plan, log, run_batch3.py) plus
ebe5853 (log only). Nothing in this paper depends on the wrong
parentage; the plan/log hunks are identical either way, but the
record should be straight.

Reviewer: Council Voice 3 (independent, no subagents, no live Zen
driving). Review window: 21:34-21:39 +07, 21/11/2026. Method: every
claim below was checked with git/grep/md5sum against the repo at HEAD
ebe5853, and the F6 md5 list and the F6 find command were re-run by
me from scratch, not trusted. All commands and outputs are recorded
in the Evidence section.

## Verdict: AMEND

F1-F5 and F7 all landed correctly, the H2/H3 claim correction is
right, the adjudication section decides every finding, and the
recorded fix-commit hashes verify. The one failure is F6, and it is
narrow but load-bearing: all 23 pinned md5 values are correct, and
the seek citation L169 is correct, but the pinned ship-time command
as written does NOT run against the layout the runner requires (wrong
find path, proven below against a faithful layout), its file set
misses two load-bearing t09 pages, and its run_batch3.py md5 line
has the same path problem plus a hash-comparison wording error.
Ship must wait for the four small plan-only fixes R1-R4. This is
AMEND, not BLOCK: the wrong find path fails loudly (empty output,
which cannot be mistaken for a match), the 23 values themselves are
right, and the t09 gap covers 2 auxiliary files in the same copy
step, not the suite core. But as written the procedure cannot be
executed, so the slot would stall or run unchecked on those files.

## 1. F1: PASS (plan L423 now says 1d23532)

- Plan L423: "suite copied from main 1d23532, md5-verified; see the
  pinned ship procedure in the re-stage section below."
- Remaining ed78e83 hits in the plan (6, all checked): L42-43 (the
  byte-identical range statement, historical), L486 (Y12 verified the
  ed78e83 suite, historical), L516-520 (the dated 19:40 UPDATE
  paragraph plus the do-not-run-on-ed78e83 instruction,
  historical/quoted), L530 (old staged suite vs new, historical),
  L743 (quoted redteam-2 AMEND condition, historical). None reads as
  a live staging instruction.
- Observation (not a fix demand): L516-520 is stale in tense ("I
  must re-stage the suite from the new main HEAD when Y15 lands").
  Y15 has landed and the re-stage is done. It is a dated UPDATE
  record and the re-stage section governs, so I leave it, but a
  future reader should not treat it as an open instruction.

## 2. F2: PASS (plan L46-48)

- "Y12 verified the merged suite headless (see 'Y12 headless
  verdict' below); its D1 defect is fixed by Y15 in 1d23532, which
  this re-stage adopts." Past tense, with the pointer. The trailing
  provisional-result sentence is kept verbatim, which is correct.

## 3. F3: PASS (plan L438-455, verified against the code)

The launch-gate bullet now describes the /proc tokenizer scan
(_scan_other_runners, "replaces the old pgrep -f sweep, which
missed bare-relative launches and false-positived on path
mentions"), the served-fixture md5 check ("the runner fetches the
t10 fixture over HTTP after start_server() and compares its md5 to
the on-disk root, refusing on mismatch or fetch failure"), and the
per-test re-scan ("run_one re-scans at the top of each test
(redteam M2): a runner starting mid-suite aborts that test as INFRA
before any tab is driven"). All three match the fixed code:

- _scan_other_runners defined at run_batch3.py L2353, called in
  launch_gate (L2499) and run_one (L2181).
- _verify_served_fixture at L2515; main() refuses with exit 2 on
  False (L2582).
- run_one re-scans at L2181 and returns the INFRA summary at
  L2183-2190 before any WD() session is opened.

No pgrep-sweep wording survives in the bullet.

## 4. F4: PASS (plan L543)

- "all byte-identical to run_codex_y5.py except the
  _is_runner_cmdline docstring tail, which records this Y14
  application instead of the 'must apply' note (logic identical)."
  The overstatement is qualified exactly as F4 specified.

## 5. F5: PASS (plan L498-512)

- The Consequence paragraph is headed "SUPERSEDED by the re-stage
  (Y14b, 1d23532). The paragraph below described the min <= 2 runner
  plus the supplementary D1 probe as the current state; both are
  gone. The Y15 checker plus the re-stage section govern now."
- The original text is kept for the record in parentheses, with its
  tense converted to past ("did NOT prove", "carried", "answered",
  "read 1", "carried"). The only remaining "min <= 2" hits in the
  plan are inside this superseded paragraph (L499, L504). No live
  instruction still describes the probe as current.

## 6. F6: PARTIAL (values PASS, procedure FAILS as written)

### 6a. Seek citation: PASS

- Plan now cites "check.mjs L169". Verified against check.mjs at
  1d23532: the seek assert `if (pos < 85 || pos > 100)` is at L169
  (lines 160-175 read; the assert is the 10th line of that window).
  The old checker at ed78e83 had the same assert at L106, inside
  the previously cited L103-106 range, so the staleness diagnosis
  was right and the new citation is right.

### 6b. Pinned md5 values: PASS, all 23 verified by me

I extracted the suite at 1d23532 with `git archive` and ran the
plan's find command shape over it. All 23 md5s match the plan list
exactly (run_all.mjs, lib/browser.mjs, lib/server.mjs, and t01-t10
check.mjs + fixture.html). Full output is in the Evidence section.
The values are correct; the failures below are the command and the
file set, not the numbers.

### 6c. G1 (required): the find path is wrong for the actual layout

The plan (L561-565) says: "after copying the suite to
/tmp/y14-server on the laptop, run from that dir: find
tests/realistic/clone1-batch3 -type f ..."

The runner requires the suite at /tmp/y14-server/clone1-batch3/...,
not /tmp/y14-server/tests/realistic/clone1-batch3/...:

- _verify_served_fixture reads disk path root + "clone1-batch3" +
  "t10-music-player" + "fixture.html" (run_batch3.py L2524-2526)
  and fetches base_url + "/clone1-batch3/t10-music-player/
  fixture.html" (L2530-2531).
- Every test URL is base + "/clone1-batch3/<test>/fixture.html"
  (run_batch3.py L425, L498, L564, L651, L750, L967, L1077, L1179,
  L1285, L1465).
- The plan itself says "the root exists and holds
  clone1-batch3/t01-terminal/fixture.html" (launch-gate note).
- The plan gives no explicit copy command anywhere (grep for cp,
  git archive, sparse checkout: no hits), so the layout is defined
  only by the runner's paths, and those paths say clone1-batch3
  sits directly under the root.

Proof, faithful layout: I built /tmp/y14b-c3-faithful containing
only clone1-batch3/ (the layout the runner requires) and ran the
verbatim plan command from it. Result: `find:
'tests/realistic/clone1-batch3': No such file or directory`, zero
output rows. The corrected command `find clone1-batch3 -type f ...`
from the same dir returns all 23 rows. The command as written does
not work. Fix R1: change the path to `find clone1-batch3`.

### 6d. G2 (required): the file set misses two load-bearing t09 pages

The pinned set is every check.mjs, every fixture.html, lib/, and
run_all.mjs. That misses t09-multi-window/detail.html and
prefs.html, which the t09 test actually drives:

- fixture.html L48 opens detail.html (`window.open` via
  'detail.html?project=' + id) and L54 opens prefs.html.
- check.mjs drives both popups (detail prefill checks L97-109,
  prefs dark checks L114-120).

A tampered detail.html or prefs.html in the laptop copy would pass
the pinned procedure unnoticed. Their expected md5s at 1d23532,
computed by me from git blobs:

- t09 detail.html 40dfc0db44aa8448341587f8559b773a
- t09 prefs.html 1169a1d5a1a6599093bdedac9c2aa74e

The corrected find command with `-name 'detail.html' -o -name
'prefs.html'` added returns 25 rows, and both md5s above match the
blobs. Note for fairness: predecessor C3's F6 spec itself listed
only check.mjs/fixture.html/lib/run_all.mjs, so the fix satisfies
the letter of F6. The gap is in the spec's file set, and it is mine
to report, not the fix author's to have foreseen from F6 alone.
Fix R2: add both names to the find command and both md5s to the
expected list.

### 6e. G3 (required): the run_batch3.py md5 line has the same path problem and a hash mix-up

The plan (L590-592) says: "Also md5sum
tests/realistic/run_batch3.py and compare against the fix commit's
blob hash, recorded in the re-stage log's fix-pass entry."

- Path: from /tmp/y14-server (where the procedure runs, and where
  the runner itself is run per its own docstring: "Usage (on the
  laptop, from /tmp/y14-server)"), the path
  tests/realistic/run_batch3.py does not exist. The file is
  run_batch3.py in that dir.
- Hash: md5sum output is an md5. It must be compared against the
  recorded md5 65818867865ad4772e78cc2bcac015d6, not against "the
  fix commit's blob hash" ed4de81d914f3a75df31554c0b2369110f7e27b0
  (a git blob hash is a different function). The log records both,
  so the comparison target as written is ambiguous at best and
  wrong at worst. Fix R3: "md5sum run_batch3.py and compare against
  the md5 65818867865ad4772e78cc2bcac015d6 recorded in the log".

## 7. F7: PASS (log wording)

- L15: "touches ONLY t10-music-player/check.mjs ... and
  t10-music-player/README.md (+97) within
  tests/realistic/clone1-batch3/ (the range overall touches 7 files;
  the other 5 are outside the suite and irrelevant to the runner)."
  Qualified as specified.
- L62: "all 5 functions identical in logic (docstring tail of
  _is_runner_cmdline differs by design ...)". The self-contradiction
  is fixed.
- L21-22: "run_batch3.py as at commit 70061e2 (blob 72d8eb6)".
  Verified: `git rev-parse 70061e2:tests/realistic/run_batch3.py` =
  72d8eb6d5b773b6ba76cd490a66ac168fb663e85.
- Transcription count: log L78-85 now says "72 ordered assert
  alignments (69 checker asserts + 3 volume extras, independently
  re-derived by Council 1)" with the explicit note "(An earlier log
  draft said 68; the correct count is 72.)" The plan's re-stage
  section matches (L551-553: "transcription 72 ... (69 checker
  asserts + 3 volume extras)"). Remaining "68" hits in the plan/log
  are md5 hex fragments or the explicit stale-count notes, not live
  claims. One cosmetic wart, not a fix demand: L21-22 reads "(blob
  72d8eb6) (Y14 redteam-2 AMEND fixes H1-H5 + M1)", two adjacent
  parentheticals; harmless.

## 8. H2/H3 claim correction: PASS

- Plan L30-40: the "live run is the real test" claim for R1/R2/R3b
  is withdrawn in so many words ("was wrong and is withdrawn"); the
  playing wrap is "reset-only tested (liveness after the wrap is
  untested: a wrap that stops the timer passes exact-zero + sampler
  and is masked by the next playlist click)"; the later advancing
  reads are "gain-only with no upper bound (a late position jump
  passes)"; and "a post-wrap advancing check and a later-read upper
  bound belong in a future checker revision (proposed follow-up,
  flagged to Muse)."
- The log adjudication matches: H2 corrected per redteam's own
  alternative (b), runner-side check declined as spec divergence,
  checker follow-up flagged to Muse; H3 declined as a documented
  checker limit, recorded as an inherited limit.
- Minor: the log's H3 line does not restate the checker-follow-up
  flag; the plan carries it. Observation only.

## 9. H4 margin note: arithmetic MOSTLY VERIFIED, one count off

- Fixture tick confirmed: fixture.html L45 ("One simulated second
  passes every 100 ms of real time while playing") and setInterval
  100 ms (L88-99). So 850 ms = 8.5 ticks.
- 850 ms decomposition confirmed from the code: the sampler eval
  blocks about 500 ms in-page (run_batch3.py L1488-1506, promise
  resolves at 500 ms) plus the 350 ms sleep before the advancing
  read (L1585). "The correct fixture reads about 8-9" follows:
  850 ms plus round trips at 100 ms/tick is 8.5 ticks plus overhead.
- "~2.4 ticks after the move" holds at median rates: 850 ms + 4
  round trips at about 2 ms (Y11b eval median) = 858 ms = 8.58
  ticks, margin 11 - 8.58 = 2.42.
- Imprecision (fix R4): the plan says "850 ms + 5 Marionette round
  trips". I count 4 on the click-to-middle-read path, each one POST
  /execute/sync (WD.eval, run_live.py L587-589): exact_zero_next,
  sampler, after_sampler read, advancing read. Pre-move it was 6
  (plus the now-playing assert's 2: d.text is find + GET text, 2
  round trips, run_live.py L800-802). Neither 4 nor 6 is 5. Effect
  is at most about 0.19 ticks (one round trip at the 19 ms worst
  case), so the "about 8-9, margin about 2" conclusion stands.
  Related: the "~0.4 ticks" saving is the worst-case saving (2 x
  19 ms = 38 ms); at median rates the move saves about 0.04 ticks.
  The headline numbers are right; the count and the saving should
  be stated as worst-case, or the count corrected to 4.

## 10. Adjudication completeness: PASS, no finding silently dropped

I enumerated every finding from all four papers and checked the
log's Review verdicts (L121-170) plus Adjudication (L172-246):

- Council 1 GO (18b150b): watch item (middle advancing read
  margin) addressed by the H4 move + margin analysis + watch keys
  (log L238-239); log count 68 fixed to 72 (L239); step-abort
  semantics recorded as pre-existing in the verdicts summary
  (L130), with no fix demanded by C1 itself. Decided.
- Council 2 AMEND (b445257): Fix 1 (-m) and Fix 2 (stale comment
  at 2364) FIXED (log L242-243); sibling copies run_codex_y5.py /
  launch_y13.py FLAGGED to Muse/Y13f (L243-244); known residuals
  double-nested flock -c quoting and runpy.run_path in -c recorded
  in the verdicts summary (L138-139) as C2 judged them acceptable
  residuals. Decided, though the residuals are recorded in the
  verdicts summary rather than restated in the adjudication
  paragraph. Acceptable.
- Council 3 AMEND (41fa919): F1-F7 FIXED (log L245-246). Verified
  independently in sections 1-7 above, except F6, which is partial
  per section 6.
- Redteam BLOCK (5e6b385): H1 fixed in part (-m, -c import) with
  adversarial forms declined and flock declined/flagged; H2 claim
  corrected with runner check declined and checker follow-up
  flagged; H3 declined with reason; H4 move done with cap
  re-derivation declined and margin recorded; M1 fixed; M2 fixed in
  part with flock part declined; M3 fixed; M4 fixed; L1 fixed; L2
  declined with reason. Every one has a decided outcome in the
  adjudication (L174-241).

## 11. Fix-commit hash record: PASS (verified myself)

Log L262-265 records: fix commit 8bee524, full hash
8bee5249f6e86fce2763bc807cc9b2b1e40d9de1, run_batch3.py git blob
ed4de81d914f3a75df31554c0b2369110f7e27b0, md5
65818867865ad4772e78cc2bcac015d6. Verified by me:

- `git rev-parse 8bee524` =
  8bee5249f6e86fce2763bc807cc9b2b1e40d9de1
- `git rev-parse 8bee524:tests/realistic/run_batch3.py` =
  ed4de81d914f3a75df31554c0b2369110f7e27b0
- `git show 8bee524:tests/realistic/run_batch3.py | md5sum` =
  65818867865ad4772e78cc2bcac015d6

All three match the log exactly.

## 12. Remaining stale-reference and contradiction sweep: PASS except section 6

- Full grep of ed78e83 in the plan (6 hits) and the log (6 hits):
  no live staging instruction remains (section 1).
- No remaining contradiction between the plan and the fixed code
  beyond the F6 command paths (sections 6c, 6e) and the H4 round
  trip count (section 9). Launch gate, served-fixture check,
  per-test re-scan, now-playing move, transcription count, and the
  SUPERSEDED paragraph all match the code.
- Hygiene of the fix diff 431b2a9..8bee524: 0 em dash, 0 en dash;
  the single "ydotool" hit is the sentence "no ydotool" (a denial,
  not a use). No personal info in the plan/log hunks.

## Required fixes (all plan-only, small)

- R1 (F6 G1): in the ship-time md5 procedure (plan L561-565),
  change `find tests/realistic/clone1-batch3` to `find
  clone1-batch3`, matching the layout the runner requires.
- R2 (F6 G2): add `-name 'detail.html' -o -name 'prefs.html'` to
  the find command and add to the expected list: t09 detail.html
  40dfc0db44aa8448341587f8559b773a, t09 prefs.html
  1169a1d5a1a6599093bdedac9c2aa74e.
- R3 (F6 G3): change "Also md5sum tests/realistic/run_batch3.py
  and compare against the fix commit's blob hash" to "Also md5sum
  run_batch3.py (from /tmp/y14-server) and compare against the md5
  65818867865ad4772e78cc2bcac015d6 recorded in the log".
- R4 (H4): correct "850 ms + 5 Marionette round trips" (plan
  L616-619) to 4 round trips post-move (exact_zero_next, sampler,
  after_sampler, advancing), and state the ~0.4 tick saving as the
  worst-case figure.

After R1-R4 land (plan only, no code change), the paper should be
GO on re-check of those lines alone; no further full review is
needed.

## Evidence (commands run, all on the VM, repo ~/workspace/computer-use-wayland)

- `git fetch origin`; `git rev-parse 8bee524^` = 431b2a9 (scope
  correction); `git diff 431b2a9 8bee524 --stat` (3 files) and full
  plan/log hunks read (432 lines).
- Hash record: `git rev-parse 8bee524`,
  `git rev-parse 8bee524:tests/realistic/run_batch3.py`,
  `git show 8bee524:tests/realistic/run_batch3.py | md5sum`,
  `git rev-parse 70061e2:tests/realistic/run_batch3.py` =
  72d8eb6d5b773b6ba76cd490a66ac168fb663e85.
- F1/F2/F5: `grep -n ed78e83` on plan (6 hits) and log (6 hits);
  plan reads L42-48, L423, L486-520, L530, L743.
- F6 values: `git archive 1d23532 tests/realistic/clone1-batch3 |
  tar -x` into /tmp/y14b-c3-suite; the plan's find command run
  there returned 23 rows; all 23 md5s match the plan list exactly.
- F6 G1: faithful layout /tmp/y14b-c3-faithful with only
  clone1-batch3/; verbatim plan command failed with `find:
  'tests/realistic/clone1-batch3': No such file or directory`, zero
  rows; corrected `find clone1-batch3 ...` returned 23 rows.
- F6 G2: `grep -n detail.html|prefs.html` on t09 fixture.html
  (L48, L54) and check.mjs (L97-120); `git show
  1d23532:.../detail.html | md5sum` = 40dfc0db44aa8448341587f8559b773a;
  prefs.html = 1169a1d5a1a6599093bdedac9c2aa74e; corrected find with
  both names added returns 25 rows with both md5s matching.
- F6 citation: `git show 1d23532:.../t10-music-player/check.mjs`
  L160-175, seek assert at L169; old checker at ed78e83, same
  assert at L106.
- F3/code: greps for _scan_other_runners, _verify_served_fixture,
  run_one (L2174-2190 INFRA return before WD()); main() exit 2 on
  served-fixture mismatch (L2582).
- H4: fixture.html L45 + L88-99 (100 ms tick); sampler 500 ms
  (run_batch3.py L1488-1506) + sleep 0.35 (L1585); WD.eval 1 POST
  (run_live.py L587-589); WD.text = find + GET text (run_live.py
  L800-802); round trip count recomputed as 4 post-move, 6 pre-move.
- Adjudication: full reads of the log L121-269 and finding lists
  from Council 1 (18b150b), Council 2 (b445257), redteam (5e6b385),
  predecessor Council 3 (41fa919).
- Hygiene: fix-diff grep for em dash 0, en dash 0, ydotool 1 hit
  (the denial sentence only).

Timings: review 21:34-21:39 +07 (14:34-14:39 UTC), 21/11/2026.
No personal info in this paper. No em dash or en dash in this paper.
