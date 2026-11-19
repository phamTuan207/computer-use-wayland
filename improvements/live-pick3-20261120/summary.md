# TASK 2: Pick 3 small-target A/B with UI-TARS-2B-SFT (grounding-pick3-jedi 59bcac2) - VERDICT: BLOCKED (loader deps missing)

Branch: `grounding-pick3-jedi`, HEAD `59bcac2` (docs) / `6cebb8e` (code:
CU_MULTI_CANDIDATE=auto, should_engage, overview round, verify_crop_local,
observe_to_act_ok 5s rule, scripts/local_grounder.py registry).
Suite gate CITED, not rerun: full suite 1395 tests, 7 failures, 0 errors,
2 skipped, FAIL set identical to the 1339-test baseline
(from improvements/grounding-pick3-jedi.md in the branch). HEAD verified via
the branch log; no checkout change, no re-run needed.
Jedi-3B is REJECTED per the parent task (gate FAIL, 10.21s/call, 0/3
measured) and was not used under any circumstance.

## The block, measured live (06:52-06:55 +07)

The UI-TARS loader deps are missing in the current environment. All four,
checked three ways:

- System python3: `import torch` NO, `import transformers` NO,
  `import huggingface_hub` NO, `import bitsandbytes` NO (all
  ModuleNotFoundError).
- Only venv on the laptop (`/home/james/.venvs/checkov`): torch NO.
  `pip list` shows no torch / transformers / huggingface_hub /
  bitsandbytes / accelerate anywhere.
- The module's own check: `scripts/local_grounder.py gate --model
  uitars-2b-sft --dry-run` (worktree code, no broker, no download)
  reports `"missing_loader_deps": ["torch", "transformers",
  "huggingface_hub", "bitsandbytes"]`, preflight ok otherwise:
  disk_free_gb 12.7 (needs 8.0), vram_free_mib 4284 (needs 500),
  download_dir /tmp/local-grounder.
- No cached weights to fall back on: /tmp/pick3-gate is gone,
  /tmp/local-grounder is gone (the Pick 3 gate venv and its 9.2 GB model
  snapshot were wiped by the reboot, as the branch doc says).
- Environment around the gap: root disk 98 percent full (12G free of
  385G), /tmp tmpfs 13G free, GPU 4284 MiB free (voxtype/ComfyUI are
  lighter now than the 88 MiB free seen in the Pick 3 gate).

## Consequence

- Method arm (Pick 3 auto + UI-TARS verification) CANNOT run: the
  specified grounder cannot load. No substitution was made; Jedi was not
  used.
- Baseline arm (Pick 3 OFF, plain grounding) was NOT run: the A/B verdict
  needs both arms, and orphaned baseline numbers have no comparison
  value. No Luna executor arms were launched for Task 2: 0 model calls,
  0 broker sessions, 0 targets measured. Per-target hit/miss, wall, calls
  and misclicks are N/A.
- No install was attempted. The parent task prescribes BLOCKED for exactly
  this case, and installing torch + transformers + bitsandbytes is a
  multi-GB download on a 98-percent-full root disk, which needs an
  explicit go-ahead plus a disk decision (venv + snapshot live in /tmp
  by the module default, 13G free there; root has 12G free).

## What works (smoke checks, no broker, worktree code)

- Focused unit tests: `python3 -m unittest tests.test_multi_candidate
  tests.test_local_grounder`: 89 tests, OK (skipped=1), 0.926s. Matches
  the branch doc (89 tests, skipped=1).
- `CU_MULTI_CANDIDATE=auto ... multi_candidate.py ground --task-kind
  terminal`: refused with the terminal reason ("terminal task: pick3 is
  pure overhead there (0 misclicks either arm, clean pair 46.0s vs
  20.0s)"), rc=1. Exactly as documented.
- `ground --task-kind small-target --target-size 18` with a valid
  candidates reply: engages, candidate (500,500 in 0-1000) maps to
  (462,258) px, 200px zoom crop, rc=0. (My first reply used the wrong
  key "points"; the parser wants "candidates". The gate itself engaged
  in both runs.)
- tesseract 5.5.4 present at /usr/bin/tesseract (verify_crop_local dep).
- The main checkout was NOT switched for Task 2 (still harness-prefetch
  7c840d7, prefetch.conf drop-in, relay 1332257); no relay restart was
  needed since no live arms ran.

## What unblocks it

Set up a venv with torch, transformers, huggingface_hub, bitsandbytes,
then download the UI-TARS-2B-SFT snapshot (ByteDance-Seed/UI-TARS-2B-SFT;
the Pick 3 gate snapshot was 9.2 GB, deleted at cleanup) and run the
gate + the A/B. Follow-up option that needs NO loader deps: a Pick-3-only
A/B (hardened Pick 3, Luna vision top-3 + on-laptop tesseract verify, no
local grounder) on the same n=6-9 small-target set. That differs from the
specified method arm, so it needs the parent's authorization first.
Small-target set for the re-run (from speed-proto-pick3.md): T1 Zen
new-tab plus, T2 back arrow, T3 Claude input attach plus (systematic
rightward error class: true plus at 0-1000 x about 510, guesses 588/613/
640), plus 3-6 new 16-20px targets to reach n=6-9. Prior A/B: baseline
1/3, Pick 3 2/3, 4 extra crops about 0.49s broker service. Success bar:
hit-rate win with wall per target no worse than baseline +5s; terminal
tasks keep Pick 3 OFF.
