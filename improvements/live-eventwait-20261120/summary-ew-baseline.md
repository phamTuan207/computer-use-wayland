# EVENT-WAIT-SEQ BASELINE arm summary

## Setup

- Run completed on 2026-11-20. Checkout HEAD at setup: `56f5af4`.
- Broker at setup: `state=idle`, `owner=null`, `driver=idle`, `guardian=idle`, cancellation clear.
- Relay at setup: `started_git_head=56f5af4e521e1c20b26b56dc31d662e34f1c2668`; `loaded_code_sha256=84f65d16ad3dd26b23c1ef75d8614cbb8c1e6539d0512cce65c8c8111d65d4a5`. Both matched.
- Checkout state at setup was the expected pre-existing state: `M improvements/live-test-log.md` with md5 `0fee1435cfb43d554404caf487ed80f2`, plus untracked `improvements/latency-probe-20261120-results.csv`, `improvements/latency-probe2-20261120-results.csv`, `improvements/live-a2t-20261120/`, and `improvements/live-a4r-20261120/`. Nothing in the checkout was modified by this run.
- Suite gate cited from `/home/james/computer-use-wayland-eventwait/improvements/summary-event-wait-seq.md`: clean baseline 1339 tests, 7 failures, 0 errors, 2 skipped; post-change 1360 tests, 7 failures, 0 errors, 2 skipped, same failure hash `e6442202b3a4ca9c7b1db55479b62b44b35d624d34c40895ea5619fb7ce14720`. All 21 new event-wait tests passed. No suite was rerun on this control arm.
- The terminal was launched after detecting the live Hyprland instance from its lock file. Exactly one client matched title `ewbase-term`; its address was saved and reused. All terminal input and observation went through the broker.

## Measurements

Wall is start submit to the `VERIFIED` timestamp. Think is the residual after subtracting session startup-to-ready time, task operation request service, and explicit task sleeps. Broker service includes task operation requests plus finish. Model calls are task operation requests plus finish; session start and status polling are excluded. Observes include initial grounding and every separate follow-up observe. Refusals, misclicks, deaths, timeouts, and missed events are zero for all four tasks.

| Task | Wall s | Think s | Broker service s, ops + finish | Calls | Observes, including initial | Task sleeps, count / seconds | Refusals / misclicks / deaths | Timeouts | Missed events | Image bytes per observe, then total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1 | 102.939 | 99.638 | 0.732 | 4 | 2 (1 verify) | 1 / 2.000s | 0 / 0 / 0 | 0 | 0 | 447,479, 452,353 / 899,832 |
| P2 | 46.349 | 42.961 | 0.827 | 4 | 2 (1 verify) | 1 / 2.000s | 0 / 0 / 0 | 0 | 0 | 452,353, 447,917 / 900,270 |
| P3 | 110.307 | 101.982 | 1.654 | 8 | 4 (3 verify) | 3 / 6.000s | 0 / 0 / 0 | 0 | 0 | 447,917, 449,925, 458,985, 457,742 / 1,814,569 |
| P4 | 218.380 | 208.965 | 2.848 | 8 | 4 (3 verify) | 3 / 6.000s | 0 / 0 / 0 | 0 | 0 | 457,742, 470,017, 492,305, 490,150 / 1,910,214 |

Totals: wall 477.975s, think 453.546s, broker service 6.061s, 24 model calls, 12 observes, 8 task sleeps for 16.001s, 5,524,885 image bytes. There were 20 task operation requests and 4 finish calls. The task sleep counts include the dirt checks for P3 and P4. The wrapper also inserted 8 session-start polling sleeps at 0.25s each, total 2.0s, and terminal setup used one 1.0s sleep. Across the run that is 17 sleeps and about 19.0s, of which 16.0s are task waits.

## Terminal OCR, own read, and ground truth

| Task | Tesseract from final verification observe | Own read from image | Ground truth | Result |
| --- | --- | --- | --- | --- |
| P1 C-03 | `/dev/mapper/omarchy_root 3856 3726 116 98% /` | Avail `11G` | `df -h /` showed Avail `11G` | Correct. OCR read `116` instead of `11G`. |
| P2 E-04 | `96.0` | `96.0` | `96.0` | Correct. |
| P3 B-01 | `/tmp/hoc-ky-2`; `/tmp/hoc-ky-2/oop`; `/tmp/hoc-ky-2/ktvm`; `/tmp/hoc-ky-2/dsa` | The same four paths | Root plus `dsa`, `ktvm`, and `oop`, 4 directories | Correct. The pre-task terminal `ls` showed `/tmp/hoc-ky-2` absent. |
| P4 A-01 | `Y tudng 1: app nhdc udng nudc`; `Y tudng 2: bot tém t&t bai giang.`; blank line; `Y tudng 3: web ban d6 secondhand.` | `Ý tưởng 1: app nhắc uống nước.`; `Ý tưởng 2: bot tóm tắt bài giảng.`; `Ý tưởng 3: web bán đồ secondhand.` | Those exact 3 lines | Correct from the observed `cat` output. The one `printf` command used octal UTF-8 bytes so the file content did not depend on accented keyboard input. Tesseract dropped or changed diacritics. The pre-task terminal `ls` showed `/tmp/y-tuong.txt` absent. |

## Teardown verification

- All four broker sessions finished. Each finish returned `status=finished`, `driver=stopped`, `guardian=clean`. The successful immediate post-finish `timed.py status` checks showed `state=finished`, `driver=stopped`.
- A later teardown `timed.py status` using the finished P4 lease returned `ok=false` with null state and driver fields. No direct `session_remote.py` status call was made. The last successful broker check was the P4 post-finish check, which showed a free finished session; current `idle/null` state was not re-read.
- `ewbase-term` was closed with `hyprctl dispatch 'hl.dsp.window.close()'`. The requested `rm -rf` cleanup was rejected by automatic review. Cleanup completed with `unlink /tmp/y-tuong.txt` and `rmdir` on the three empty child directories and `/tmp/hoc-ky-2`; a shell absence check passed for both task artifacts.
- The desktop client query found three clients: `org.omarchy.herdrdrop` with title `omarchy: ~`, `zen` (Zen Browser), and `kitty` with title `ewbase-exec`. It found no `ewbase-term` and no Chromium. The active `ewbase-exec` is the runner for this report and should close when this process exits. The client list did not show a separate `drift` window, so the desktop was not a fully clean match to the requested list at query time.
- The teardown checkout check changed during the run: HEAD was `144d512f`; `git status --short` showed the same four untracked entries from setup but no modified log line; `improvements/live-test-log.md` md5 was `8fe7ca04d085ee4f36dd9a5c1edce1f6`, different from setup. This was detected after all measurements and cleanup. No further machine or checkout operations were performed after that check; only this report was written under the run directory. The cause of the HEAD and log change was not determined.
- Relay was not restarted.

## Verdict and open items

The baseline measurement completed with all four task outcomes correct, 4/4. This is n=1 per task and is control-arm data only; it does not support a precise speedup factor. The teardown guard did not pass because the checkout HEAD and log md5 changed after measurement. The final broker status query also did not return state fields, although the last successful post-finish check showed the broker free. The coordinator should compare these numbers with the event-wait method arm, check the concurrent checkout/log change, and confirm the controller window closes after this runner exits.
