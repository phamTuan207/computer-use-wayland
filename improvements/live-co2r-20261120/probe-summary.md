# Task 1 (change-only re-measure): scripted diff-delivery probe

Date: 2026-11-20 04:33 +07. Coordinator-run, zero model calls.
Branch: change-only-obs 37f7c63. Relay MainPID 1207463, CU_CODE_EXEC=1,
started_git_head 37f7c63. Session co2r-probe2, generation bbd3c261c8842fc03d947ce750714a78.
Probe wall 04:33:18.989 (driver START) to 04:33:26.955 (driver END).
Code-exec request service 1.709s, in-program elapsed 1640.881ms, 7 API calls.
Run dir on the laptop: /tmp/live-co2r-20261120/probe/ (probe-driver2.log,
records2.jsonl, probe1.py). First driver run failed on a coordinator typo
(a colon inside the args list made invalid Python, same class as the Task 2
probe typo); second run with a fresh lease (co2r-probe2) succeeded.

## Verdict: CROP DELIVERY CONFIRMED

The fix (37f7c63) works live. The diff crop and thumbnail now reach the
executor through the code-exec envelope as viewable files, where Task 2 on
6995a8c delivered zero crop bytes.

## Results

| Observe | Mode | Changed tiles | Fraction | Bbox |
| --- | --- | --- | --- | --- |
| First (no previous) | full | 96/96 | 1.000 | [0, 0, 924, 1176] |
| After typing "x" | diff | 1/96 | 0.010 | [300, 580, 93, 163] |
| After Enter ("x" runs) | diff | 3/96 | 0.031 | [0, 580, 393, 310] |
| No act between | none | 0/96 | 0.000 | None |

Program shape: observe_change_only(window) -> act type "x" (one char, no
newline) -> observe_change_only(previous) -> act type newline (runs "x") ->
observe_change_only(previous) -> observe_change_only(previous) with no act.
Terminal co2r-probe-term, 924x1176 full height (the method executor kitty
was gone, so the probe terminal got the full height).

## Delivery evidence (machine-checked)

1. The verify variable SURVIVED in the envelope variables (Task 2: dropped
   entirely, verify in vars False). probe_crop and probe_thumb are path
   strings in the variables.
2. Diff observe 1: verify["image"] =
   /home/james/.cache/agent-computer-use/3f1410b016e1-diff.png,
   verify["thumbnail"] =
   /home/james/.cache/agent-computer-use/3f1410b016e1-thumb.png, with
   image_path / thumbnail_path aliases carrying the same strings.
   probe_image_present=true, probe_thumb_present=true.
3. Diff observe 2: verify["image"] = 311e25577f65-diff.png,
   verify["thumbnail"] = 311e25577f65-thumb.png, aliases present.
4. The record images list includes the crop PNGs (timed.py collects every
   .png path in the broker response with its byte size):
   3f1410b016e1-diff.png 11,427 bytes and 311e25577f65-diff.png 79,629
   bytes, against full frames of 898,430 bytes each. Task 2 listed only 3
   full 924x1176 frames (894,109 + 894,109 + 894,055 bytes), zero crop bytes.
   The thumbnail files do not appear in the images list (they sit under the
   "thumbnail" key, not "image"), but they ARE delivered as path strings in
   the envelope variables.
5. Files on disk, all mode 0600, all PNG:
   - 3f1410b016e1-diff.png: 93x163, 11,427 bytes, matches bbox [300, 580, 93, 163].
   - 3f1410b016e1-thumb.png: 320x407, 126,253 bytes (low-res full frame).
   - 311e25577f65-diff.png: 393x310, 79,629 bytes, matches bbox [0, 580, 393, 310].
   - 311e25577f65-thumb.png: 320x407, 126,227 bytes.
6. Readability: tesseract PSM 6 on the 393x310 crop reads
   "computer-use-wayland HEAD ? ) x", the typed "x" plus the prompt. The
   93x163 single-character crop does not OCR reliably (PSM 6/7 return noise
   or nothing for one glyph), which is a tesseract single-glyph limit, not a
   delivery failure: the crop file is a valid viewable image of exactly the
   changed region (visually confirmed: the prompt line with the typed "x"
   and the cursor block). Copies of both crops and the first thumbnail are
   kept in this directory as evidence.
7. Byte saving per diff observe: crop 11,427 bytes vs full frame 898,430
   bytes (98.7 percent smaller) for the one-character change; crop 79,629
   bytes vs 898,430 bytes (91.1 percent smaller) for the Enter change.
   The full frame is still captured and bound (result['observation']) for
   act(), so the saving is on the read side (what the executor views), not
   on capture.

## Consequence for the P1-P4 arms

The method arm P1-P4 all returned mode full (fractions 0.802-0.865) because
terminal command outputs repaint most tiles, so no P-task ever produced a
crop and the executor verified from the full frame in all four tasks. That
does NOT mean the fix failed: this probe proves the delivery path works
when diff mode fires. The wall comparison (method 37.894s total vs baseline
2a 172.734s and method 2b 57.567s) still measures the code-exec path, and
the crop saving only materializes on tasks whose changes are localized
enough to stay under the 0.35 threshold.

## Incidents

- Probe run 1 failed on my envelope typo (a colon inside the args list,
  "code-exec", "--program", path, "--intent": "...", made invalid Python,
  so probe-req1.json was never written and the req failed
  FileNotFoundError). The session started and finished clean; no broker
  request sent. Same typo class as the Task 2 probe run 1.
- Probe run 1 close race: the hyprctl eval close printed "ok" but the
  immediate count check still saw 1 window; the window closed shortly
  after (async). The run-2 driver sleeps 2s before checking and retries
  the close once; run 2 closed cleanly (count 0, CLOSE-OK).
- The probe terminal in run 1 was found already gone when the coordinator
  went to close it by hand, confirming the async close.

## State after the probe

Relay unchanged (MainPID 1207463, CU_CODE_EXEC=1, started_git_head
37f7c63). Broker finished, owner co2r-probe2, free for the baseline arm.
Desktop clean (probe terminal closed, count 0). Next: baseline arm on the
same HEAD with a clean relay env (no CU_CODE_EXEC).
