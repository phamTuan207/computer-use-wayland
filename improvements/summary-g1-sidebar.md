# G1 sidebar probe, scripted follow-up -- NEGATIVE with evidence

## Run metadata

- Owner: the owner
- Repo: `~/computer-use-wayland`, branch `speed-swarm`, HEAD `0491c10` (verified at start, no fast-forward needed)
- Relay: restarted 12:26:41 +07 for the probe (MainPID 113859, drop-in pick4.conf with CU_PICK4_FASTPATH=1, started_git_head 0491c10); restored to clean env 12:33:47 +07 (MainPID 118290, no CU vars, broker idle, next_sequence 1, started_git_head 0491c10)
- Session owner: `pick4-g1sb`. Run dir: `/tmp/speed-pick4-20261118/g1-sidebar`
- Nautilus window `0x55ac9a76b5d0` at [3448, 914], 924x1176, title Home. Nautilus AT-SPI PID 116441.
- Operator: scripted, zero model think. All gaps are operator round-trips (VM to laptop SSH), not model think.
- String args ONLY in every envelope (invalid_arg_type rule). No integer args anywhere.

## Verdict

NEGATIVE, with exact evidence. Sidebar-item precision is NOT achievable through the current a11y path. No sidebar row was matched, grounded, or clicked through the broker, and no ground, crop, or click was performed on a sidebar row, because no ref for one exists in any broker-visible snapshot. Three independent blockers, each proven below. A fourth naming fact matters for any future attempt: the Home sidebar row is named "Open Personal Folder", not "Home".

## Blocker 1: depth cap 12, rows live at depth 16 to 19

- Broker a11y observe (seq 6, svc 0.161s): 4 elements, truncated False. e1 frame Home [0, 0, 924, 1176], e2 panel '' [0, 0, 924, 1176], e3 list Sidebar [0, 0, 184, 1130], e4 label chrome-hichoggbehbpg...desktop [0, 0, 439, 18]. The Sidebar container is visible. Its rows are not.
- Broker a11y drill into e3 (seq 7, svc 0.138s): 1 element, the Sidebar list itself, truncated True. Drill cannot descend: observe() caps child traversal at depth 12 (len(path) < 12) and the skeleton drill limit is min(len(base)+3, 12) = 12, which equals the Sidebar depth already.
- Direct AT-SPI walk (no broker, 664 nodes, 0.20s wall, max depth 33): Sidebar list at depth 12, path [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], 1 child. Its rows sit at depth 16 (list item), with image and label children at depth 19. The walk cap of 12 stops 4 levels short of the rows.
- Code: scripts/a11y.py observe(), `limit = min(len(base)+3, 12) if skeleton else 12`, children pushed only when `len(path) < limit`.

## Blocker 2: rows have no actions, so the observe append rule drops them

- observe() appends an element only when `skeleton or item['actions'] or item.get('editable')`. The Home row (depth 16 list item, "Open Personal Folder") has NO actions. Even if the depth cap were raised, a non-skeleton observe would traverse past the rows without listing them, and query() matches listed elements only.
- The depth 19 label "Home" does have actions, but they are clipboard.copy, selection.delete, clipboard.paste, link.open, clipboard.cut, link.copy, menu.popup, selection.select-all. No click, press, or toggle. An a11y act click would refuse it ("no native click action").

## Blocker 3: degenerate extents, all rows report the identical box

- Cross-checked three ways (broker observe, direct walk, direct extents plus position plus size read): every sidebar list item reports extents [0, 0, 172, 36], position [0, 0], size [172, 36]. All 13 rows: Open Personal Folder, Recent Files, Starred Files, Open Network Locations, Open Trash, ~/Work, ~/Documents, ~/Downloads, ~/Projects, ~/Videos, ~/Pictures, Mount and Open "63 GB Volume", Mount and Open "32 GB Volume".
- Size is right per row (172x36); position is missing for every row. Ground could not distinguish one row from another even with the depth cap fixed. All Nautilus extents are window-relative (x=0, y=0 everywhere, frame [0, 0, 924, 1176] equals the window size), consistent with the G1 re-probe coord_frame window finding.
- The Home row is selected=true in the live tree (Nautilus is showing Home), and its label child reads "Home". The row exists and is identifiable by tree position, just not by broker query or by extents.

## Broker queries, all accepted, all matched 0 for the sidebar

- Seq 8, query --pid "116441" --name Home: accepted, matched 1, ref e1, role frame, name Home. The frame again, not a sidebar item.
- Seq 9, query --pid "116441" --role "list item": accepted, matched 0.
- Seq 10, query --pid "116441" --name "Open Personal Folder" --role "list item": accepted, matched 0.
- Seq 11, query --pid "116441" --name Home --role label: accepted, matched 0. The depth 19 label is past the cap.
- A11y calls in the clean session: 7 (apps, observe, drill, 4 queries), service 1.055s. Refusals 0, misclicks 0, deaths 0 in the clean session.

## What this means for Pick 4

- The a11y half stays working plumbing only, and only for elements the observe walk can list (top-level frames, panels, action-bearing nodes). Sidebar-item precision is unproven and, on current code, unreachable: it needs a deeper walk (cap above 19 for Nautilus), an append rule that lists action-less rows, AND per-row positions that AT-SPI does not currently supply for Nautilus rows. The third item may be a Nautilus/GTK behavior, not something the harness can fix by walking deeper.
- Do not quote the G1 re-probe as sidebar precision. It proved frame grounding only.

## Counts and timing (clean session sb2)

- Session sb2: start submit 12:29:58.306 +07, ready 0.829s, generation 309667dc17a7c96a7e085d4c09ffa90b. Finish 12:32:58, status finished, driver stopped, guardian clean. Analyzer: 13 records, service total 2.157s, span 180.261s, gap total 177.936s (operator round-trips), a11y 7 reqs 1.055s, act 1 req 0.438s, observe 1 req 0.193s, windows 2 reqs 0.218s.
- First session sb1 failed on operator error (see Incidents) and was replaced; its wall is excluded from the span above.
- Direct AT-SPI walk: 664 nodes in 0.20s. Tree reads are cheap; depth and extents are the blockers, not latency.

## Incidents

- I1 (operator error, not a broker bug): the first sb1 act carried a malformed actions file (printf turned backslash-n into a literal newline inside the JSON string). The broker accepted seq 3, the driver returned ok false "Invalid control character at: line 1 column 49 (char 48)", and the session went to state failed, driver failed, error driver_command_failed. A retry got task_stopped. Finish on the failed task returned rc 1. A fresh start over the failed task succeeded (process dead, recovery none). Lesson for briefs: one malformed actions JSON fails the whole session driver instead of returning a request error; that is a robustness gap worth a follow-up, and all JSON files in probes must be written with json.dump, never printf.
- I2 (operator error): my first timed.py start was killed by my own head pipe (SIGPIPE), and the lease parent dir did not exist yet (lease_file_unavailable). Both fixed by writing output to files and mkdir -p of the lease dir first.
- I3: the first setsid kitty launch failed silently (no WAYLAND_DISPLAY in the SSH env). Retry with XDG_RUNTIME_DIR, WAYLAND_DISPLAY=wayland-1, DISPLAY=:0, and HYPRLAND_INSTANCE_SIGNATURE exported worked: PID 114065, 0x55ac99eb1520, [2509, 914], 1863x1176.
- I4: `hl.dsp.window.focus("0x...")` does not exist (nil value error). `hl.dsp.window.close()` with no args closes the active window, which was Nautilus. The test kitty was closed by kill on its own PID 114065, as the G1 brief allows.

## Cleanup

- Nautilus closed, test kitty closed, no test processes remain. Final hyprctl clients: Jarvis only. Broker idle, next_sequence 1. Relay restored to clean env (drop-in removed, MainPID 118290). No artifacts outside the run dir. No changes to his Zen, Jarvis, or music.
