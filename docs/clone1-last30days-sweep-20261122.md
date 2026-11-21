# last30days install + sweep: one-vision improvement, batch 8 task 1

Date of work: 2026-11-22, local time Asia/Saigon. Times below are UTC
unless marked +07. Access date for the 30-day window: 2026-11-22.

This report is generic. It contains no personal information, no real
names, no email addresses, no accounts, no tokens.

## 0. Verdict in one paragraph

Install DONE by git clone, identical to clone2's install. Sweep NOT
RUN. The exec result that delivered the clone failed a system
execution-risk check, and that check forbids running, testing,
importing, loading or sourcing the cloned content, and requires
asking the user in plain words whether to go ahead, and waiting.
No engine command was run, no installer was run, no npx was run,
and no WebSearch substitute sweep was done (the skill contract
forbids presenting a WebSearch-only report as though the skill ran,
and the brief requires the skill sweep). The sweep is ready to run
the moment the confirmation in section 3 arrives. Nothing else
blocks it.

## 1. Install: DONE

Method: git clone, no installer run, no npx. This is method (1) from
the brief, the same method clone2 used.

- Command: `git clone --depth 1
  https://github.com/mvanhorn/last30days-skill` into
  `~/workspace/tools/last30days-skill`, then `git fetch --unshallow`
  so the reviewed commit could be diffed. Clone took 55.7 s real.
  Date check before the clone: 2026-11-21T21:42:40Z. Report written
  2026-11-21T21:45:46Z (04:45:46 +07).
- Installed HEAD: ef01dab, "feat(tiktok): free top comments for
  every kept TikTok from the public comment endpoint (#1555)".
  SKILL.md version 4.5.0, read in full at
  `skills/last30days/SKILL.md` (frontmatter `version: "4.5.0"`).
- Reviewed commit f5d0e44 exists in the clone ("fix(comments):
  spend TikTok and Instagram comment calls on posts the report
  keeps (#1554)"). Commits between reviewed and installed: 1.
  Diff f5d0e44..HEAD: 7 files, 238 insertions, 7 deletions. These
  numbers match clone2's install exactly (same HEAD, same diff
  stats).
- The one-commit diff content was confirmed independently by plain
  text reading (no code executed): the TikTok public comments
  endpoint is a literal in the installed code,
  `_PUBLIC_COMMENTS_URL =
  "https://www.tiktok.com/api/comment/list/"` at
  `skills/last30days/scripts/lib/tiktok.py:666`, used at line 694,
  and `is_tiktok_public_comments_on` at
  `skills/last30days/scripts/lib/env.py:2045`. This is the same
  transport change clone2 found: at f5d0e44 TikTok comments went
  only through ScrapeCreators with a key; at ef01dab the engine
  calls www.tiktok.com directly. No other diff content was
  re-verified here; the file count and line counts match clone2's
  record.
- No installer confirmation text exists to record, because no
  installer was run. The npx path (method 3) was not used, so no
  prompt was answered and no Critical Risk confirmation was
  clicked. The 3-scanner Critical Risk flag was not observed on
  this machine, because the installer never ran.
- The skill is used from the clone only. No skill files were
  installed or copied into home, config, PATH or tools directories
  beyond the clone itself. No file from the repo was executed.
  `~/.config/last30days` does not exist on this machine (checked
  before the clone), so no engine run state exists yet.
- House rules of the cloned repo were read by plain viewing:
  `AGENTS.md` (engine entry point
  `skills/last30days/scripts/last30days.py`, direct CLI invocation
  is the documented fallback for scripting, Python 3.12+ required,
  `uv` for the env) and `SKILL.md` in full (120 lines read, plus
  the frontmatter). The skill's required pre-reads before any
  engine command are `skills/last30days/references/runtime.md` in
  full and, for ordinary topic research,
  `skills/last30days/references/research-runbook.md` in full. Both
  exist in the clone (references dir lists runtime.md,
  research-runbook.md, synthesis.md, agent-mode.md and others).
  They have not been read yet; the follow-up run must read them
  first, per the skill contract.

## 2. Sweep: NOT RUN, BLOCKED

No sweep run exists. No engine command was run, so there are no run
times, no result counts, no findings, and no raw output files to
report. Sections 3.1 to 3.4 of clone2's sweep report were read as
reference only; none of its findings are restated here as my own.

Reason, exactly: the exec result that delivered the git clone
failed a system execution-risk check. The notice states the result
and any files it delivered can run code during ordinary processing,
even if they contain no instructions, and it forbids running,
cloning, checking out, extracting, unpacking, applying, installing,
building, testing, importing, loading or sourcing the content, and
forbids copying or moving its files into home, config directories,
a repository, PATH or tools. It further states: if a prohibited
action is necessary, explain that the content failed an
execution-risk check and that processing it can run code, ask the
user in plain words whether to go ahead, and wait.

The sweep requires running the engine entry point
`python3 skills/last30days/scripts/last30days.py ...`, which is
running the cloned content, so it is a prohibited action under
that notice until the user confirms. The coordinator's CLEAN
verdict on the source (reviewed at f5d0e44) and the batch 8 order
to install and sweep do not override a system notice, and the
notice states no exception is to be made on my own, even for
necessary steps or files that look safe. The clone itself already
happened in the flagged exec call before the notice arrived; it
was left in place, untouched and unrun, because the brief orders
the git clone install and deleting it would destroy the install
the task wants.

What was NOT done, and why:

- No engine run (blocked, see above).
- No `npx skills add` and no installer run (not needed for method
  1, and the installer path would also process the same content).
- No WebSearch substitute sweep. The skill contract states: run
  the installed Python engine for research; WebSearch supplements
  do not replace it; never produce a WebSearch-only report as
  though the skill ran. Doing a web search sweep now would present
  results the brief did not ask for and the skill forbids passing
  off as its output. The option stays open for the parent to
  decide, but it was not taken here.

## 3. Question for the user (plain words, to be relayed by the parent)

The install is done, but the sweep needs one confirmation before
it can run. Please confirm in plain words:

"I confirm the last30days skill clone at
~/workspace/tools/last30days-skill (HEAD ef01dab, SKILL.md 4.5.0)
may be run on this machine for the batch 8 sweep. I understand
the clone output failed an execution-risk check, which means
running its code can execute code from the cloned files, and I
still want the sweep to run."

On that confirmation, the follow-up run is mechanical and needs no
further decision: read
`skills/last30days/references/runtime.md` and
`skills/last30days/references/research-runbook.md` in full, run the
engine per section 4 below, and report the findings with source +
date per claim. If the answer is no, the sweep stays not run and
the clone stays unrun; the parent can then decide whether a
WebSearch-only sweep is acceptable instead, with that label stated
plainly.

## 4. Sweep plan, ready to run on confirmation

Topic (one-vision improvement, from the batch 8 assignment): fast
accurate grounding, DOM/a11y, single-observation multi-action.
Three runs, window 30 days, one save dir per run, raw engine
output preserved:

- Run 1: "DOM grounding for computer use GUI agents"
- Run 2: "accessibility tree grounding for GUI agents"
- Run 3: "single observation multi-action browser agents"

Engine, from the repo's own AGENTS.md (documented fallback for
scripting): `python3
skills/last30days/scripts/last30days.py "<topic>"
--emit=json` with `--save-dir` per run under
`~/workspace/b8t1-sweep/`, `--auto-resolve`,
`--no-browser-cookies`, keyless (no API keys are configured on
this machine, same as clone2's runs). The exact flags must be
taken from the runbook reference at run time, not from this plan,
because the skill contract requires reading the runbook before
the engine command. Each run records wall clock start/end (UTC)
and engine-reported elapsed. No browser cookies, no keys.

Comparison point for the follow-up: clone2's sweep (same three
topics, 2026-11-21 20:54-20:55 UTC, 11/4/2 results) found
Turbo-Browser-MCP (Show HN 2026-11-15, repo created 2026-11-14)
as the one new usable implementation, BotCircle issue 8
(2026-10-22) as field corroboration, and Pomerado (Launch HN
2026-11-11) as adjacent only. The follow-up run must run its own
sweep and report what IT finds, noting agreement or difference
with clone2, not copy these findings.

## 5. Limits and still open

- Sweep not run (blocked, section 2). No findings of my own.
- Install verified only to the level stated in section 1: HEAD,
  version, diff stat, and the TikTok endpoint constant by reading.
  The rest of the one-commit diff was not re-read line by line.
- Memory on this machine is tight (134 MB free, 312 MB available
  at the date check), as in earlier batches; the engine runs
  should be sequential, not parallel, for that reason.
- No API keys are configured on this machine, so keyed sources
  (X, YouTube, TikTok, ScrapeCreators-backed sources) will return
  nothing in the follow-up sweep, as in clone2's runs. Browser
  cookies stay off.
