# Investigation: owner Zen death 06:33-06:34, 27/11/2026

Independent investigation (no-self-healing rule). The lanes active at
the time did not investigate themselves. All times Asia/Ho_Chi_Minh.

## What died, and when

- The owner's live Zen, PID 4059095 (started 27/11 ~04:14), ports
  9222 (BiDi) / 2828 (Marionette).
- Last proof of life: 06:33:38, CF735368 driver read 13 tabs on port
  9222 successfully (subagent tool event 486725).
- First proof of death: 06:34:00, CF735368 driver's page command got
  "no dedicated Zen session on port 9222: [Errno 111] Connection
  refused" (event 486737).
- Death window: 22 seconds, 06:33:38 to 06:34:00.
- Relaunched by the CF735368 driver at 06:37:47 as PID 37679 with
  full session restore (essentials and zen basics pinned tabs
  verified present by screenshot). No tab loss.

## Mechanism (strongly supported, one link unprovable)

The only laptop GUI action recorded inside the death window, across
every lane, is the Item 4 (R16) drill worker's window-close dispatch
at 06:33:45 to 06:33:55 (event 486728/486730). Its recorded output:
"drill window: 0x5614f0849b40 / ok / STILL-RUNNING", followed by a
listing of the drill profile's session files. The drill Zen (PID
27049, port 9225, window 0x5614f0849b40) survived that call: its pid
was still running at 06:33:55 and its window still listed at 06:34:10
(event 486744). The owner's Zen died inside the same 10 seconds.

Reading: the compositor close closed the FOCUSED window instead of
the addressed drill window. The focused window at 06:33:45 was the
owner's Zen (last focused by the CF735368 driver's act-now typing at
06:33:04; the drill worker's interactions were BiDi-based and do not
change focus). Closing the owner's only Zen window exits Zen cleanly,
which matches every physical trace: no minidump, no crash report, no
OOM record, session restored from the 06:33 sessionstore on relaunch.

The worker's own report states the address-form close
(hl.dsp.window.close({ address = ... })) "returned ok but did not
close" the drill window, with the address selected by pid==drill-pid.
Two sub-mechanisms fit and cannot be separated with surviving
evidence: (a) the address argument is not honored by
hl.dsp.window.close on Hyprland 0.57.2 and the call closes the
focused window; (b) the call sequence focused the wrong window (or
focus silently failed) and a bare close() then closed the focused
owner window. Both produce the identical outcome and the identical
prevention below.

## Lanes exonerated by records

- CF735368 driver: in the window it only read tabs (06:33:38, OK),
  wrote an event-log entry, then found the port refused (06:34:00).
  Its zen_cli session start (06:34:13) bound port 9222 only because
  the port was already free, i.e. after the death; its session stop
  (06:34:45) killed its own new instance PID 29682 (recorded result,
  event 486773); its kill of PIDs 30579/30581/30578 (06:35:19) hit
  its own wedged zen_dom/geckodriver client processes (pgrep output,
  event 486797), after the death.
- Item 3 (R10 Stage 1) worker: sleep + tail of throwaway-profile
  test output only, in the window.
- Item 2+5 worker: VM-side file hashing only.
- Item 6 (R15) worker: VM speed-daemon kill tests only (VM
  processes, not the laptop browser).
- FCC probe lane: no act-now session in the window (first-action log
  entries at 06:32:28, 06:33:04, then 06:39:38); coordinator log
  records plan-only output at 06:32:39.

## Evidence labels

VERIFIED (direct records):
- Death window 06:33:38 (tabs OK) to 06:34:00 (connection refused):
  tool events 486725, 486737.
- Item 4 close dispatch at 06:33:45 to 06:33:55 with output "drill
  window: 0x5614f0849b40 / ok / STILL-RUNNING": events 486728,
  486730.
- Drill window/pid alive after the call (06:33:55, 06:34:10): events
  486730, 486744. Drill window gone by 06:34:40 ("hl.focus: window
  not found"), drill pid EXITED by 06:34:53 after a further close:
  event 486775.
- No crash artifacts: profile minidumps/ and Crash Reports/ empty.
- No OOM: kernel journal 06:30 to 06:37 has no oom/killed-process
  lines. User journal 06:33:30 to 06:34:10 shows only SSH
  disconnects.
- Session files: previous.jsonlz4 last written 06:33; recovery files
  06:39 (new instance).
- zen_cli session stop is pid+cmdline guarded (refuses unless the
  cmdline contains "zen" and the recorded dedicated profile) and
  killed PID 29682, not 4059095: scripts/zen_cli.py cmd_session_stop,
  event 486773.
- Full exec inventory of the death window across all lanes: 14
  events, only 486728 is a laptop GUI action.

ASSUMED (labelled, not load-bearing for attribution):
- The focused window at 06:33:45 was the owner's Zen. Supported by
  the act-now focus at 06:33:04 and by the outcome; no focus log
  survives.
- Sub-mechanism (a) vs (b) above. Unprovable: the exact command text
  of event 486728 is not preserved (stored tool descriptions are
  truncated; the drill scripts on the laptop were cleaned up), and
  the Hyprland log at this log level records no window map/close
  events (checked: no lines for either window address).

## Prevention (one concrete rule)

Ban compositor window-close (hl.dsp.window.close in any form, and
bare close() above all) for test windows on any workspace that also
holds the owner's live browser. Close test browser instances by
recorded pid with a cmdline profile check, the zen_cli session-stop
pattern, which cannot hit the owner's process. If a compositor close
is ever unavoidable, require a pre-close assertion from a fresh
hyprctl clients dump: the target address's pid equals the intended
test pid AND the focused window's pid equals the target pid; abort
otherwise, and re-verify the target pid is gone and the owner Zen
pid is alive immediately after.

## Cost

One owner-browser restart with full session restore; no data loss.
The CF735368 lane lost about 4 minutes. The drill itself passed; its
cleanup close is the defect.
