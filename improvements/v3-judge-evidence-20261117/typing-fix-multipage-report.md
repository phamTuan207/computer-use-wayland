# Multi-page typing fix: Worker N report

- Build: commit `c9b96a7c73b3f2e2f4864b0d7ddbfefae1cd1efb` (main), helper `83b8b9b25ff9adaab85b59ba047544a3317d1ea23c45e40b702e6119daa8f65b`.
- Spec: `typing-fix-multipage-astra6.md` (SHA-256 `5683c46e0cbe38833331692444691c86ef9250f72a18aa4d9528144bcf447bba`).
- Worker: N (Luna). T0 = 2026-11-16 22:30:38 Asia/Ho_Chi_Minh. Run ended 2026-11-17 ~08:42 (elapsed ~10h12m).
- Log: `live-test-log.md` in this directory (wall-clock + elapsed from T0 for every step).

## Headline

The multi-page fix is implemented, verified offline, committed, pushed, synced, verified live in both apps, and passed the full L3 suite plus the stress suite.

- Offline: native tests 23/23 OK; full suite 1030 tests OK (skipped=1, pre-existing hyprglass env skip).
- Live GUI verification: 21/21 trials byte-exact (page fixture both apps, 4-group 188-symbol fixture, single-page regressions (i) 5/5, (ii) 4/4, (iii) 5/5, TextView 3/3), plus an explicit visual confirmation of Ctrl+A full-document selection.
- L3: tc02 3/3 PASS (byte-exact 50/50 each); tc01 PASS; tc03 through tc13 all PASS. That is 13/13 cases, 130/130 points if the judge confirms 10/10 each (judge to confirm; no self-score in this report).
- Stress: S1 5/5, S2, S3 15/15, S4, S5 all PASS (S4 and S5 needed reruns; each rerun failure was a driver or environment cause, documented in section 7).
- Historical comparison (user lead, 05:21 17/11): the earlier version's Vietnamese typing is NOT a sound replacement. Verdict: do not adopt, do not adapt the fix shape. Details in section 3.
- Pill F1: NOT part of this worker; stays deferred per the plan (LAST).
- No Astra escalation was needed. No item is BLOCKED.

## 1. The fix (per-unit changes)

Chosen shape (Astra spec, binding): one keymap with up to four XKB groups, inside the existing vendored helper. Page j//N becomes a zero-based XKB group, slot pool[j%N], level 0. The group is selected through the virtual-keyboard `modifiers` request plus roundtrip. No second keymap upload ever. This defeats the proven failure directly: only the first uploaded map ever takes effect on Hyprland 0.57.2, so all pages go into that first map. Ceiling 4N = 188 distinct pool literals (184 with A reserved, 180 with A+S); larger sets refuse cleanly before connecting. The single-page path stays byte-for-byte as the G==1 case. No build/sync script changes; only `keyboard-correction.patch` edited. Alternatives (b) virtual-keyboard-per-page and (c) helper-per-page were NOT implemented (rejected by the spec; (c) would count as chunking under the current contract).

Only one file carries the fix: `native/vendor/wtype/keyboard-correction.patch` (regenerated from the edited translation unit via `diff -u`, verified to apply with `patch --batch --fuzz=0` and to reproduce the edited TU byte-for-byte).

- New patch SHA-256: `f4cc6a9f889879f741d0c2f0769b3f1eb9b2c5685fb7781cf5f5dd8ecd02267c` (809 lines; TU grew 916 to 1050 lines).
- `struct wtype`: `current_page` became `current_group`, plus `group_count` and prepared-keymap fields (`keymap_file`, `keymap_size`).
- Preflight refuses `group_count > 4` before any Wayland connection.
- `kbcorr_select_group()`: modifiers request plus roundtrip, no-op when already selected.
- `run_mod` tracks group 0 after its own group-0 modifiers request; `run_key` selects group 0.
- `type_keycode` selects `e->page` for pool literals, 0 for fixed keys.
- `run_text` resets the group to 0 at end.
- Serialization extracted to `kbcorr_write_keymap(wtype, FILE*)`: each physical key declared once, named after the first referenced entry's `<K...>` name; G==1 is byte-for-byte the old writer; G>1 writes every `Group1..GroupG` explicitly with `type[Groupg]="ONE_LEVEL"`; unused slots get `VoidSymbol`; fixed/explicit/sentinel symbols repeat in every group.
- `kbcorr_prepare_keymap()` serializes to an unlinked file and validates the complete text with libxkbcommon format v1 before connecting.
- `upload_keymap()` sends the prepared FD exactly once.
- One real bug found and fixed during implementation: the prepare file was opened `"w"` (write-only), so the read-back `fread` failed with EBADF. Fixed by opening `"w+"` (reproduced standalone first: `fread=0, ferror=1` with `"w"`, `fread=29` with `"w+"`).

Files changed in the commit (4 files, +816/-102):

- `native/vendor/wtype/keyboard-correction.patch` (the fix).
- `native/vendor/wtype/README.md` (new patch SHA, multi-page description, 4N ceiling, Hyprland 0.57.2 finding, supported/refused limits).
- `tests/wtype_harness.c` (source-level protocol interception; see section 2).
- `tests/test_wtype_native.py` (23 tests; see section 2).

The proven failure this fixes (Worker M, 17/11): mid-stream keymap re-upload is not applied on Hyprland 0.57.2 + GTK/Chromium; the page fixture failed identically in both apps (385 bytes, actual SHA `9a59075dc7a399b0cec5cae2068686b0084d3b7ee701d42497ce6a53e9c3ec11`, 98 mismatching chars at indexes 47-144). The shipped single-page correction covers tc02's sentence (22 distinct pool literals of 47).

## 2. Offline verification

Harness (`tests/wtype_harness.c`): source-level protocol interception (headers included first so include guards preserve declarations, then macro aliases redirect the patched TU's calls to test doubles for `zwp_virtual_keyboard_v1_keymap` / `..._modifiers` / `..._key`, `wl_display_roundtrip`, `usleep`). The captured upload is compiled into one persistent libxkbcommon client state; modifiers update the state (`xkb_state_update_mask(...,0,0,group)`); key presses are resolved via `xkb_state_key_get_one_sym` (fixed keysyms mapped: Return to newline, Tab to tab, Escape to 0x1b, BackSpace to 0x08, Delete to 0x7f; chord keys with modifiers depressed are skipped from decoding); a second upload is recorded but ignored by replay. Outputs `$KBCORR_DUMP` (plan + `group_count`), `$KBCORR_KEYMAP` (serialized map bytes), `$KBCORR_TRACE` (uploads, decoded text, modifier/key events with active group, final group, group-change-while-down and overlap flags).

Tests (`tests/test_wtype_native.py`, 23 tests total = 14 old + 9 new):

- 96-symbol fixture decodes 193/193 from one map (groups 0-2) in direct, trailer, merged-Ctrl+A, and stdin forms.
- 188-symbol fixture decodes 377/377 across groups 0-3.
- Group-alternation fixture (all 188 chars interleaved across groups).
- Boundaries N=47 (47/48/188 accepted, 189 refused pre-connect) and N=46 with A reserved (46/47/184 accepted, 185 refused pre-connect; refusal proven by absent dump/keymap/trace).
- Fixed symbols repeat in every group, plus partial-group `VoidSymbol` holes (keymap substrings).
- Group reset before following chord/sleep.
- G==1 serialization byte-for-byte vs golden maps captured from the OLD writer with a throwaway interception harness. Goldens: g1 sentence SHA `1e5646f6adc4443202541ea11874847910fc1f63c87df32700e0bb07e294d210`, g2 merged-A `4626cf73095c538a000965b95dc87b1e7975825dd17e9eb95aa5fa0d9c647a72`, g3 sentinel-only `c94fb33a06911a47ab2233945cf9e275cb2b78ce0db33d71190a6daa91475d84`, g4 stdin `a894ae5ba6868aab395b409c6d2613eb4583938677f39dbd18919ca210ecd7a5` (embedded base64 in the test file).
- Two test bugs found and fixed (test bugs, not code bugs): U+0100's xkb keysym name is `Amacron`, not `U0100`; the alternation fixture originally used only 8 distinct chars so `group_count` was 1.

Results: native tests 23/23 OK (0.89 s); full suite 1030 tests OK (skipped=1, pre-existing hyprglass env skip) in 116.5 s. That is baseline 1021 + 9 new, no new skips or failures.

`git diff --check`: non-patch files CLEAN. The `.patch` file flags are unified-diff format artifacts only (blank context lines render as a lone space; tab-indented context lines render as space+tab). The old committed patch has 26 such space-only lines, the new has 33. The generated C is whitespace-clean. This is documented in the log, not ignored.

## 3. Historical comparison (user lead, 05:21 17/11)

User lead: "Computer use ban truoc day van de go tieng viet da lam kha tot roi ay tham khao xem." An earlier version handled Vietnamese typing quite well. I compared it before committing.

Verdict: the old approach is NOT sound as a replacement. No adoption, no adaptation changing the fix shape. The multi-page fix continues as briefed.

Evidence, all verified first-hand:

(a) Git history: `literal_keyboard`, `keyboard_argv`, `keyboard_groups`, stock wtype 0.4-2 plus `-p VoidSymbol` trailer all date to the initial commit `d4c374f` (2026-10-09). The typing path is substantively unchanged through HEAD. `e2bf1ef` (2026-11-17 03:45, "Typing fix v2") only made Fix A diagnostics passive and RESTORED the compose bypass it had accidentally removed.

(b) Backup `cu.py` (1227 lines) vs HEAD: 1042 diff lines, dominated by later features (env discovery, guards, diagnostics). The typing core (`keyboard_argv:54-91`, `keyboard_groups:527`, `literal_keyboard:577`, `execute_group:829-861`) is substantively identical. The backup already knew the keyboard path corrupts (`validate_actions:473`: "non-BMP text may be corrupted by Wayland keyboard input; use browser fill or a11y set_text").

(c) Compose mode (`ime='compose'`, still in HEAD `cu.py:1037,1092,1479-1480,1538`; skill doc: "for intentional Telex input"): O3 verified exact 50/50 (SHA `8da1f562...`, GTK, IM 2/ngosen active) BUT O5 verified the SAME 45-byte loss (SHA `8bb4c179...`, VS Code, IM 2/ngosen active via `fcitx5-remote -s ngosen; -o`). fcitx5 profile: `DefaultIM=ngosen`, group items `keyboard-us` + `ngosen`. Compose does NOT fix the physical-code collision; it needs Telex ASCII input (the broker sends precomposed text, no converter exists) and IM state 2, which the tc02 contract forbids.

(d) Why the user remembers it working: stock allocation is slot-dependent and nondeterministic across invocations (Ctrl+A prefix shifts slots; O1 38/38, O2/O3 50/50 exact vs O5/O7/O8/O9 45-byte loss, same sentence, same code). Short and typical texts often dodge slots 14/15 (Backspace/Tab). "Worked well" is real but unreliable, not a mechanism.

(e) a11y set_text and browser fill: the old version's documented workarounds (skill `desktop.md:47-52`, backup `cu.py:473`). FORBIDDEN for tc02 (keyboard-input contract).

Astra escalation was NOT used for this decision: the evidence was decisive, and Astra already ruled Fix B DEAD (`typing-fix-plan-astra6-v2.md` section 10) with the allocator as the repair.

Backup examined: `~/.local/share/agent-computer-use/backups/sync-20261116-231305-266679-2c5b03c7` (Oct-26 snapshot + Nov-6 partial).

## 4. Commit, push, sync

- Commit `c9b96a7c73b3f2e2f4864b0d7ddbfefae1cd1efb` on main (4 files, +816/-102), author phamTuan207. No force-push, no reset.
- Push: `129c7f2..c9b96a7 main -> main`. Remote HEAD == local HEAD == `c9b96a7c73b3f2e2f4864b0d7ddbfefae1cd1efb`. Tree clean.
- Pre-sync state verified: no `~/.cache/agent-computer-use/session.json`; relay PID 106001 alive (`session_remote.py serve --socket /run/user/1000/computer-use-wayland/relay.sock`, user service active); IM `1/keyboard-us`.
- Sync: ledger `~/.local/share/agent-computer-use/releases/20261117-053025-600262-c9b96a7c73.json`; `--check` exit 0 (191 managed files, 11 preserved-history exceptions). Repo == installed MATCH on all 7 changed files:
  - `native/wtype` `83b8b9b25ff9adaab85b59ba047544a3317d1ea23c45e40b702e6119daa8f65b`
  - `scripts/cu.py` `b104948fac9b670fe4ce193157d08f353c054ef7d337c806654de5808ed750a2`
  - patch `f4cc6a9f889879f741d0c2f0769b3f1eb9b2c5685fb7781cf5f5dd8ecd02267c`
  - `native/vendor/wtype/main.c` `713597abfc049196864ffcc041bb6683c761b71d68ed2da86cdcfc6b7ed3d244`
  - README `b2a13d7f4903c96403e0651f69a7538ec84638930757706734ee7f042f3c695c`
  - harness `7f386da8ff49077cdafb414c8fc35cacdfd71792f5b495d61c07b7acd6e70a96`
  - test file `f61ba488dfad83962ae42f0adc2110172e314d5890cf5656a259582c58a6679b`

## 5. Live GUI verification (05:32-05:40, 17/11)

All 21 trials EXACT, base `/tmp/opencode/multipage-pvjh3iag`, helper 83b8b9b2. Drivers: `/tmp/kbcorr-drivers/run_kbcorr.py`, `run_textview.py`, `textview.py`; runners `kbcorr-{direct,controls,shortcuts,textview}.sh`. The `.sh` runners use `set -u` and CONTINUE after driver failure, so I did NOT execute their loops unchanged: I wrote a fresh strict stop-on-error wrapper (`/tmp/mp/live-run.py` on the VM, `/tmp/mp-live-run.py` on the laptop) and inspected required focus/IM/evidence records before advancing.

- Page fixture VS Code: 385 bytes, SHA `efe6014c288c9fb823c9a0b39f6f658e060e58aa039cb37235ffaa3852a19c8d`, 0 diffs (11.7 s).
- Page fixture GTK TextView: 385 bytes, same SHA, 0 diffs (4.7 s).
- 4-group 188-symbol fixture VS Code: 753 bytes, SHA `4367d18e1344fd9660933496b6c1d3f11ff29aa32d3162f4b5ee8aaf31ac52a9`, 0 diffs (13.6 s).
- 4-group 188-symbol fixture GTK: 753 bytes, same SHA, 0 diffs (5.8 s).
- Single-page regression (i) direct, 5 trials: 50 bytes, SHA `8da1f5624c1b482bcdfae9d7c6883fdc52313dbe4120c2d1df2623ec5bcb9772`, 5/5.
- Single-page regression (ii) controls, 4 trials (text/A/a/stdin): 50/50/50/51 bytes, SHA `84c5e7baf73169a18bed003bc71e3ebc647755429a0ae4285a2d41c700d240c6` (leading-dash stdin), 4/4.
- Single-page regression (iii) shortcuts, 5 trials: shortcut-A/a 50 bytes x2; save-S/s 39 bytes SHA `6b867300...` x2 (real GTK Save dialog confirmed by screenshot: name kbcorr.txt, path tmp>opencode>multipage-pvjh3iag>save-S>out, Cancel/Save); backspace 1 byte SHA `4b68ab38...`; 5/5.
- TextView, 3 trials (text/A/a): 50 bytes x3, 3/3.
- Event evidence: shortcut-A/a KeyA x1, literals on safe codes (Digit1-0, Minus, Equal, KeyQ/W/E/R/T/Y/U/I/O/P, Space x8, Enter x1), 38 insertText + 1 insertParagraph, 0 composition; save-S/s KeyS x1, 0 composition; backspace End x1 + Backspace x1, 0 composition; page-vscode 0 composition. IM 1/keyboard-us pre- and post-flight. The user's on-tap.txt window: 1 before, 1 after (untouched).

Ctrl+A full-document selection, explicit visual confirmation (05:36-05:40): the immediate screenshots (shortcut-A/a) showed only the first word "REPLACE" highlighted, status bar "Ln 1, Col 1", which was ambiguous (the same gap Astra flagged). A settled probe (`/tmp/mp/select-probe.py`, fresh test-owned window, same Ctrl+A argv, 2.0 s settle before grim, base `/tmp/opencode/selprobe-1`) showed status-bar CDP read "Ln 3, Col 1 (39 selected)" and a settled screenshot with BOTH seed lines fully highlighted in blue plus the cursor at line 3. `window.monaco` is not exposed in the workbench (monaco:false), so no Monaco selection query; status bar plus settled screenshot are the evidence. Conclusion: the word-only highlight was a render-timing artifact (grim fired before the editor painted the selection); the model selection was full all along, which the exact 50-byte replaces already proved functionally. Gate (iv) Ctrl+A full-document selection: CONFIRMED.

Pre-L3 gates (spec section 5) all green: (1) offline green, (2) page fixture both apps + 4-group, (3) single-page regressions, (4) commit/push/sync, (5) machine handed over all day, decisions flagged for tonight (section 9).

Fixtures and oracles: page fixture text = chars U+0100..U+015F then reversed then newline (193 chars, 385 bytes, expected SHA `efe6014c...`, 0 diffs, both apps); 4-group fixture = U+0100..U+01BB forward+reverse+newline (377 chars, 753 bytes, SHA `4367d18e...`, 0 diffs); sentence oracle 50 bytes SHA `8da1f562...` ("Toi nay on cau truc du lieu luc 20:30." + newline); leading-dash stdin 51 bytes SHA `84c5e7ba...`; replace seed `REPLACE THIS ENTIRE BUFFER\nSECOND LINE\n` (39 bytes).

Note: focus-after-select.json DOM selection is "" (expected for Monaco EditContext, proves nothing).

## 6. L3 results (live brokered, real session path, human-like operations)

Helper: `/tmp/mp/l3.py` (VM) copied to laptop `/tmp/mp-l3.py`. One short SSH invocation per broker step. State in `/tmp/opencode/multipage-l3/<trial>/state.json`. Runs at `/tmp/opencode/multipage-l3/tc02-t1`, `tc02-t2`, `tc02-t3`, `tc01`, `tc03` through `tc13`, `stress/`. All finishes ok=true, driver stopped, guardian clean, explicit_finish, unless noted.

### tc02, 3/3 PASS (05:43-06:05)

- Trial 1 (05:43-05:59, owner `tc02-t1-multipage-20261117`, gen `320f5b16f36b47368a8ca87e1bc3290c`, 36 requests, 13m43s): PASS, byte-exact 50/50. Learned the Save As row position live (File menu, sleep 4 s to settle, fresh observe, Save As at (95,365) on a 901-wide window; Save at y=341, Save All at y=389). A stray "Welcome - Untitled (Workspace)" VS Code window appeared during Save As attempts (default-profile restore artifact, left untouched). Save dialog `xdg-desktop-portal-gtk` `0x55abca688fb0`. File landed at the correct output path, SHA `8da1f562...`.
- Trial 2 (06:00-06:02, gen `7b514cc48cee513fdaf01c7c6519f670`, 15 requests, 2m20s): PASS, byte-exact 50/50. Learned pattern applied cleanly, no refusals.
- Trial 3 (06:03-06:05, gen `85adf101babd366b9dcf319745b2862a`, 14 requests, ~1m40s): PASS, byte-exact 50/50. Same learned pattern, no refusals.
- Verdict: 3/3 PASS on the multi-page build c9b96a7 (helper 83b8b9b2). Old build tc02 was 0/10 (45-byte loss); new build 3/3 exact 50/50 through the real broker path. Note: window-cropped observations do not show the screen-level pill overlay; live-path proof is the brokered cursor/click/type evidence itself; pill F1 stays deferred per plan.

### tc01, PASS (06:06-06:32)

Task: draw a yellow circle in Pinta, save as `hinh-tron-vang.png`. Pinta 3.1.2. Five sessions (two died on benign dialog-close capture failures; the actions themselves succeeded).

- Session 1 (gen `061c851f...`): FAILED (driver_command_failed). The New Image dialog is a SEPARATE window (class dotnet, 0x55abca75dc00); the act targeted the Pinta main window from the main-window observation. Lesson: dialogs that are separate windows must be observed (by their own address) and acted on via the dialog observation.
- Session 2 (gen `e4cda609...`): dialog coordinate offset found (~25 px vertical on dotnet dialogs; clicks land above the image coordinate). Set-size by typing failed (click opened the Preset dropdown); recovery via the dropdown itself (Down + Return selected "640 x 480"). Session died on the OK click (benign; dialog most likely closed).
- Session 3 (gen `7c7ce2c8...`): canvas 640x480 confirmed; Ellipse identified via a11y (tooltip "Ellipse / Shortcut key: O / ..."); first click consumed by the tooltip (Tool stayed Rectangle Select); corrective retry after moving the pointer away selected Ellipse and VERIFIED it (Tool label, toolbar highlight, shape options, Brush width 7, in the required 4-8 range). Primary YELLOW verified (pixel 245,255,0). Fill Style verified OUTLINE-ONLY via a11y ("Outline Shape"). Drag (264,540)-(444,720) = 180x180 screen px painted a yellow circle outline; Enter finalized it (History: New Image / Ellipse Added / Finalized). Measured: yellow 3529 px, bbox 186x186 screen px (perfectly circular, w/h 1.0), canvas diameter ~207 px (in 160-240), stroke 6 screen px ~6.7 canvas px (in 4-8), single outline, white interior, fully inside, no clipping. Save: portal dialog (filter list exactly 7 items, NO PNG in it; Pinta determines format from the filename extension). File landed as a REAL PNG (9481 bytes, PNG 640x480 RGBA). Independent decode: yellow 4330 px; bbox 205x206 (w/h 0.995, diff 0.5% <10%); diameter ~205 px; stroke 6-7 px; unclipped; corners + interior white; the 654 non-white/non-yellow px are all within the circle bbox +-1 px and are pale-yellow/near-white anti-aliasing blends at the stroke edge (no extra marks). Session died on the Open click (stale observation coordinate space).
- Session 4 (gen `2f3d4cca...`): Open dialog opened; the Open dialog was already in .../tc01/output with hinh-tron-vang.png (9.5 kB) selected and a preview thumbnail showing the yellow circle. Clicking Open closed the dialog and killed the session the same benign way.
- Session 5 (gen `52898492...`): reopen verified (three tabs, History "Open Image" only, clean yellow circle, no selection, no dialog, 640x480 at 90%). Finish clean.
- Verdict: PASS. All rubric elements evidenced (painted ellipse + reopen; yellow stroke + ~205 px circle + 6-7 px stroke + one outline/white bg/no marks; PNG 640x480 decode + "Ellipse Added"/"Finalized" history; visible saved image + clean finish).

### tc03, PASS (06:34-06:35)

Task: open a calculator, compute 125000 + 35000 + 20000, leave the result on screen. Omacalc (`/usr/bin/omacalc`, window 0x55abca75dc00, 400x568). Session gen `ee40a3ed...`. Display "0" initially. Clicked the display, typed `125000+35000+20000` (no spaces); clicked `=` (360,525). Result: expression "125000 + 35000 + 20000" on the top line and "180000" large. Finish clean. The Omacalc window was left open showing 180000.

### tc04, PASS (06:35-06:45)

Task: open the `bai-tap` folder in Files, turn on Show Hidden Files so `.env.example` is visible. Fixture: `README.txt` 25 bytes ("Bai tap thu nghiem"), `.env.example` 15 bytes ("APP_MODE=study\n"). Original hidden-files setting recorded as `false` (gsettings, read both via plain ssh and via the GUI-session dbus env).

- Before-state problem: the before observation showed BOTH files already visible even though show-hidden-files is false. The live Nautilus toggle was ON despite gsettings false (per-window/in-memory toggle persisted in the running Nautilus process).
- The hamburger main menu has NO "Show Hidden Files" in this Nautilus version (only New Window / New Tab / Show All Tabs / Undo / Redo / Preferences / Keyboard Shortcuts / F1). The toggle is in the view-options dropdown (838,22): "Show Hidden Files Ctrl+H" (CHECKED/ON).
- Platform limit found: the driver's virtual pointer CANNOT interact with GTK popup menus (the popup grab blocks synthetic pointer events; top-bar clicks at y=22 worked, so the main-window mapping is 1:1). Clicks on the menu item (790,325), the checkmark (695,325), and hover+wait all left pixel-identical observations (same SHA across five observations). a11y walk with the menu open found no "hidden" element (popup items not exposed).
- Resolution: keyboard navigation of the open menu works. Down focuses A-Z (first item); 6 more Downs reach "Show Hidden Files"; Enter toggles. Toggled OFF first (true before-state: only README.txt visible). Then the scored ON toggle the same way: `.env.example` revealed beside README. Selected it with a single click (290,180): row highlighted, status bar `".env.example" selected (15 bytes)`, path bar .../tc04/input/bai-tap. Restored the original setting the same way (toggle OFF): gsettings false again, `.env.example` hidden, README.txt SHA `22a43f72...` unchanged, `.env.example` still "APP_MODE=study". Finish clean.

### tc05, PASS (06:46-07:00)

Task: write a 4-line Vietnamese note into `viec-ngay-mai.md`, keeping accents and newlines. Omawrite (`/usr/bin/omawrite`, window 0x55abca7ead80). Session gen `8e9bccc5...`, then `7fe9f4cc...`, then `1f112702...`.

- Typed the 4 lines; Vietnamese accents exact, but Omawrite auto-continues lists: first type doubled "- -" on lines 3-4 plus a trailing "- " on line 5. Retyped (Ctrl+A, then text relying on the auto-insert for lines 3-4), then trimmed the trailing "- " with 2x Backspace. Document then exact (4 lines + empty line 5 = trailing newline).
- First Save As attempt FAILED: typing the full absolute path into Omawrite's own Save dialog File name field was treated as a filename (invalid slashes); status bar "Could not save viec-ngay-mai.md", no file landed.
- Second attempt: Ctrl+L navigated to the output dir, set name to just "viec-ngay-mai.md", Save clicked. File landed (138 bytes) but with an EXTRA BLANK LINE after the heading (Omawrite inserts a blank line after a heading on Enter). The Save click ended the broker session ("focus changed", driver_command_failed), benign, file was saved.
- Fresh session: removed the blank line via Ctrl+Home, Down (caret on blank line 2), Backspace. File now byte-exact 137/137 MATCH (expected 137, actual 137).
- Reopen: Ctrl+Q and Ctrl+W did NOT close Omawrite; Ctrl+O opened the Open File dialog, Ctrl+L + full path + Return opened the file. The act FAILED "window no longer exists" (benign dialog-close capture failure, same pattern as tc01) and the session died; file still MATCH. Fresh session observed the reopened document: status bar "Opened viec-ngay-mai.md", all 4 lines shown. Finish clean.

### tc06, PASS (07:01-07:06)

Task: rename `bai-tap-nhap.txt` to `CTDL-buoi-3.txt` in its folder. Fixture: `bai-tap-nhap.txt` 31 bytes SHA `98f06e733eaace896709160dfba9c481e776df8698abb60bab27d1d72ce7d80a`, decoy `bai-tap-nhap-cu.txt` 29 bytes SHA `042ece38ca416b3342e41822cba6aff78cde02bbdde8a9ca961b2b07a6278df0`, `CTDL-buoi-3.txt` absent. Nautilus (same window 0x55abca6ecd60, now 'doi-ten'). Session gen `f056f6d7...`.

- Selected `bai-tap-nhap.txt` (status bar confirmed 31 bytes), right-clicked. Context menu opened (Open With Neovim / Open With... / Cut / Copy / Move to... / Copy to... / Rename... F2 / Compress... / Email... / Delete Permanently... / Send via LocalSend / Properties).
- Pointer click on "Rename..." (345,405) landed ~35 px low and opened Compress instead (Compress Files and Folders dialog, Archive Name "bai-tap-nhap"); dismissed with Escape, no harm.
- Keyboard navigation worked: right-click again, Down focused "Open With..." (the Neovim row is skipped by arrow keys), 5 more Downs to "Rename...", Enter. Rename File dialog opened; the field showed "bai-tap-nhap.txt" but only the BASENAME was selected (extension excluded). Typing "CTDL-buoi-3.txt" first produced "CTDL-buoi-3.txt.txt". Fixed with Ctrl+A + retype to exactly "CTDL-buoi-3.txt". Clicked Rename (548,317).
- Result: `CTDL-buoi-3.txt` 31 bytes SHA `98f06e73...` (matches original exactly), decoy SHA `042ece38...` unchanged, `bai-tap-nhap.txt` gone, exactly one `.txt`. File list shows CTDL-buoi-3.txt SELECTED (status bar `"CTDL-buoi-3.txt" selected (31 bytes)`), decoy intact, no dialog. Finish clean.

### tc07, PASS (07:06-07:08)

Task: drag `ghi-chu.txt` into the `CTDL` folder in Files. Fixture: `ghi-chu.txt` 26 bytes SHA `bee64efd784d0fba1857f6611b21a6527a57f0610c83d2bd5f409e9a605df6a7`, CTDL/ and OOP/ empty. Nautilus (same window 0x55abca6ecd60, now 'sap-xep', three tabs bai-tap/doi-ten/sap-xep). Session gen `acc76c70...`.

- Drag `{"type":"drag","from":[285,260],"to":[265,155],"ms":500}` worked first try: Nautilus toast `Moved "ghi-chu.txt" to "CTDL"`, parent now CTDL "1 item" + OOP "0 items", ghi-chu.txt gone from parent. Inside CTDL: ghi-chu.txt 26 bytes SHA `bee64efd...` (matches original), OOP still empty. Double-clicked CTDL (265,155) to open it; CTDL open with ghi-chu.txt visible (26 bytes), path bar .../sap-xep/CTDL. Finish clean.

### tc08, PASS (07:09-07:18)

Task: read a timetable, write which room and time the Tuesday Data Structures class is in, into `lich-thu-ba.txt`. HTML fixture created on the VM (`/tmp/mp/tc08-tkb.html`, 914 bytes) and copied to the laptop (SHA `f809d44792a06a94ba562daf5ca80abb0c8aaaea727a69ebe0d667c48ca16651`); output file absent.

- Workspace problem: Zen lives on workspace 1, the active workspace was 2; two broker sessions died on "window is not visible on its monitor" (gen `73345e6b...` and `bab3acf5...`) because the l3 helper's observe does not pass --focus. hyprctl on this system is Lua-wrapped: plain `hyprctl dispatch workspace 1` / `focuswindow address:...` fail (exit 7, Lua syntax error). Working form (from `/tmp/mp/run_kbcorr.py`): `hyprctl dispatch 'hl.dsp.focus({ window = "address:0x..."})'` (rc 0, "ok"). Focused Zen (0x55abc9d42f00). The Zen window was showing the user's Muse chat (the user's private conversation; I did not interact with it); opened a new tab with Ctrl+N (in Zen, Ctrl+N = new tab, Ctrl+T = new window, swapped), Ctrl+L, typed the file URL, Return.
- Read the RENDERED table (full-window screenshot): the row matching Thu Ba + Cau truc du lieu is 09:00-10:30, A2-407 (row 3 of 4; the other Thu Ba row is OOP/B1-305; the other CTDL rows are Thu Hai/A2-203 and Thu Tu/A2-203). A tighter crop (540,40,580,340) cut off the Ngay/Gio columns; the full-window screenshot is the retained source evidence.
- Launched a fresh test-owned VS Code (0x55abca763890, gen `b6d9213b...`, session started 07:13:45); focused it via the Lua dispatch (it opened on workspace 1). Dismissed the Restricted Mode banner X (905,48), clicked the editor (200,100), typed "Thu Ba: Cau truc du lieu, 09:00-10:30, phong A2-407." + newline. The editor rendered some Vietnamese diacritics as tofu boxes in the screenshot (a font rendering artifact only; the bytes are exact, see below). Ctrl+Shift+S opened the portal Save As dialog (0x55abcaa0b140, 875x600, in .../tc08/input); clicked the Name field (430,22), Ctrl+A, typed the absolute path `/tmp/opencode/multipage-l3/tc08/output/lich-thu-ba.txt`, verified it in the field, clicked Save (825,22) --no-after.
- File saved byte-exact: expected 65, actual 65, MATCH. The content is "Thu Ba: Cau truc du lieu, 09:00-10:30, phong A2-407." + newline (Vietnamese accents and the en-dash U+2013 all correct). Final observation: tab "lich-thu-ba.txt" (no unsaved marker), breadcrumb tmp > opencode > multipage-l3 > tc08 > output > lich-thu-ba.txt, content visible, line 2 empty (trailing newline), no dialog. Finish clean.

### tc09, PASS (07:18-07:22)

Task: copy the reminder text from a file into a local group-study draft (unsent, do not send). Fixtures: `nhac-lich.txt` 105 bytes SHA `07476d68...` (two lines + final newline: "Thinh oi, mai 14:00 minh lam bai OOP o thu vien nhe." / "Nho mang laptop va the sinh vien."), `nhap-nhom.html` 454 bytes SHA `6d0115e8...` (local draft surface: title "Nhap nhom hoc, thu nghiem cuc bo", textarea #draft, disabled button "Gui, da khoa trong thu nghiem"). VS Code window 0x55abcaa0b140 ('nhac-lich.txt'). Session gen `64410600...`.

- Observed the source file (both lines, breadcrumb tmp>opencode>multipage-l3>tc09>input>nhac-lich.txt). Clicked the editor (300,130), Ctrl+A, Ctrl+C.
- Switched to Zen (0x55abc9d42f00). In this Zen, Ctrl+N opens a search/quick-open palette, not a new tab; typing the file:// URL into that palette navigated to the page. Verified: local title, empty textarea, disabled Send button.
- Clicked inside the textarea (530,195), Ctrl+V. Both lines pasted exactly once, with the line break, accents correct; the disabled "Gui, da khoa trong thu nghiem" button is visible and no send action was taken; the draft tab was left open. Finish clean.

### tc10, PASS (07:22-07:25)

Task: in one study note, replace all 'linked list' with 'danh sach lien ket', only that file. Fixtures: `ghi-chu-ctdl.txt` 111 bytes SHA `e8552ad2...` (3 lines: "linked list luu cac nut roi nhau." / "On linked list truoc khi lam bai." / "stack dung nguyen tac LIFO." + trailing newline); sibling `khong-sua.txt` 40 bytes SHA `d4e7e97c...` ("linked list, giu nguyen file nay" + newline). VS Code window 0x55abca9bd9f0. Session gen `0c596be7...`.

- Opened the editor's Find/Replace (Ctrl+H, single-file, not workspace search). Find field (490,138), Replace field (490,167).
- Entered "linked list" in Find and "danh sach lien ket" in Replace. Verified: match count "2 of 2", both occurrences highlighted in the editor.
- Activated Replace All (Ctrl+Alt+Enter). Both lines changed; stack line unchanged; Find now shows "No results" (no old term remains).
- Dismissed Find/Replace (Escape), saved (Ctrl+S). Saved-file read-back: 2 replacements, 0 old terms, stack line unchanged; sibling `khong-sua.txt` SHA `d4e7e97c...` unchanged. Edited note visible and saved. Finish clean.

### tc11, PASS (07:27-07:33)

Task: scroll to the last question of a long assignment, write it into `cau-cuoi.txt`. HTML fixture `de-bai.html` 3564 bytes SHA `cbfd36c0...` (30 sections, each at least 180 CSS px, 20 px text, 24 px padding; sections 1-29 "Cau n: On lai khai niem so n."; final section heading "Cau 30" + text "Cai dat hang doi bang hai ngan xep; phan tich do phuc tap cua enqueue va dequeue."). Output `cau-cuoi.txt` absent. VS Code blank window 0x55abca98c570. Session gen `05646f8f...`.

- Opened de-bai.html in Zen at the top (Cau 1-3 visible; title "Bai tap CTDL, ban thu nghiem"). Note: the l3 `act` command needs a prior observation in state ("no last observation in state; observe first"); the first open-debai act failed for that reason and was redone after an observe.
- Wheel-scrolled with the broker scroll action (`{"type":"scroll","x","y","dx","dy"}`). dy=-500 scrolls up (no-op at top); dy=+800 scrolls down and moved to Cau 28-30 in one batch. The broker scroll dy is positive-down, and dy=800 is a very large scroll (nearly a full page). Cau 30 fully visible ("Cai dat hang doi bang hai ngan xep; phan tich do phuc tap cua enqueue va dequeue."), no further question follows (section ends, bottom of page).
- Typed the answer into the blank VS Code doc: "Cau 30: Cai dat hang doi bang hai ngan xep; phan tich do phuc tap cua enqueue va dequeue." + newline. Saved via the portal Save As dialog (0x55abcaa42160) as `T/output/cau-cuoi.txt`. Independent read-back byte-exact 116/116, SHA `b7414877a475f8b470ca4250060af78ec77b724b9865504e5397b4f3b80de6da` MATCH. Saved note visible (tab cau-cuoi.txt, breadcrumb tc11/output). Finish clean.

### tc12, PASS (07:33-07:37)

Task: open the weekly timetable, capture a readable screenshot of just that window. Fixture `lich-tuan.html` 439 bytes SHA `2dde257e...` (title "Lich tuan, lop thu nghiem"; 22 px text; "Lich hoc tuan nay" + 3 lines: Thu Hai 08:00 CTDL A2-203; Thu Ba 14:00 OOP B1-305; Thu Nam 09:00 CSDL A2-407). Nautilus at `T/input/` (window 0x55abca6ecd60, 'input'). Session gen `02d68273...`.

- Observed Files: `lich-tuan.html` visible (439 bytes, Today 07:33). Selected it (290,155), right-clicked. Context menu opened; first item "Open With Zen Browser    Return" (the default handler), second "Open With...".
- Pressed Return. Zen opened it (window 0x55abc9d42f00, title "Lich tuan, lop thu nghiem, Zen Browser"). Verified rendering: title + all three schedule lines readable, not source code, not an error.
- Captured the Zen window observation and preserved its PNG bytes as `T/output/lich-tuan.png` (540693 bytes, SHA `ccc2d94bfe9b184ba0985be998d0dd3abcf6667b0d4e58c93068cd937de3d291`, identical to the evidence/observe-render.png). Independent decode on the laptop: PNG (925, 581) RGB.
- Caller receipt (VM): received the same 540693 bytes, SHA match, decodes as PNG 925x581 RGB. Timetable left visible, no menus/dialogs. Finish clean.

### tc13, PASS (07:37-07:42)

Task: open a terminal, create the folder `CTDL buoi 3`, then create `README.txt` in it with 'Bai tap danh sach lien ket'. Fresh Kitty terminal at `T/output/` (window 0x55abcaa42160, title '/tmp/opencode/multipage-l3/tc13/output', [2981,914], 453x581, workspace 1). Target `CTDL buoi 3/` absent before. Session gen `b5090269...`.

- SSH flapped for ~2 min (tailscale-proxy closed connection x3) before recovering; the first kitty launch never ran and had to be redone.
- Observed the terminal: ASCII-art banner, idle shell prompt ".../tc13/output )". Clicked it (225,550), typed `pwd` + Enter. Output: `/tmp/opencode/multipage-l3/tc13/output`. Confirmed the working directory.
- Typed through the terminal keyboard: `mkdir -- 'CTDL buoi 3' && printf '%s\n' 'Bai tap danh sach lien ket' > 'CTDL buoi 3/README.txt'` + Enter. Prompt returned, no error.
- Typed `cat -- 'CTDL buoi 3/README.txt'` + Enter. Output displayed exactly: "Bai tap danh sach lien ket".
- Independent filesystem read-back: directory "CTDL buoi 3" exists with README.txt 34 bytes, SHA `76e6da66ce3a6dc52b4c654ca20f9db8ad3e453b315b864571dd433cca1888c2` MATCH (expected 34 bytes). Terminal left at an idle prompt with the result visible. Finish clean.

### L3 totals

tc02 3/3, tc01, tc03, tc04, tc05, tc06, tc07, tc08, tc09, tc10, tc11, tc12, tc13: all PASS. That is 13/13 cases. If the judge confirms 10/10 each, the total is 130/130 (prior judge baseline: tc02 0/10, total 0/130). This report states the evidence; it does not assign scores.

## 7. Stress suite (07:44-08:42)

No detailed stress spec exists in the repo or the brief (only "then stress" after tc13), so I defined it from the program shape. Driver: `/tmp/mp-stress.py` on the laptop (detached), log `/tmp/opencode/multipage-l3/stress/stress.log`, outputs under `/tmp/opencode/multipage-l3/stress/`.

- S1, 5 back-to-back sessions (start, type sentence, save, verify, finish each): 5/5 PASS. Each saved=True, exact=True, 50 bytes, finish_clean=True.
- S2, rapid sequential inputs (5 type actions in one act, verify 5 lines): PASS. saved=True, exact=True, 250 bytes, 5 lines, finish_clean=True.
- S3, 15 consecutive observations on one window: PASS. 15/15 observations ok, finish_clean=True.
- S4, observation expiry + recovery: PASS (rerun). The stale act got the explicit broker refusal "observation older than 90s or from a future clock; observe again. No input was sent." (recoverable, session_continues=true). Recovery (fresh observe + type + save) gave exact 50 bytes, finish clean.
- S5, long session (~10 min, 5 type+observe cycles 2 min apart): PASS (S5d, third attempt). cycles_ok=5/5, saved=True, exact=True, 250 bytes, 5 lines, finish_clean=True.

S4 and S5 each needed reruns. Every rerun failure was a driver or environment cause, not a defect in the fix or the broker. The broker behaved correctly throughout (it refused stale observations exactly as designed).

- S4/S5 first run (07:51-07:53): their first observes failed "window/crop outside selected monitor" and the sessions ended (driver_command_failed). Cause: 9 accumulated test VS Code windows on workspace 1 were tiled into tiny slivers (blank-s4/s5 were 0x-5, blank-s3 1x4), so the new windows had no visible area on the monitor. The S4 stale-act therefore never had a last_observation ("no last observation in state"), so the expiry/refusal part was never actually exercised. Fix: closed all 9 test windows (focus + `hl.dsp.window.close()`, the Lua-wrapped hyprctl form; plain `closewindow`/`killactive` fail under it) and re-ran S4+S5 on a clean screen.
- S5 first rerun (S5b, 08:11-08:20): same 50-byte/1-line result, good 453x281 window, re-click each cycle. Root cause = driver bug, broker correct: the type-cycle-2 record shows the broker refused it with "observation older than 90s ... No input was sent." My driver slept 120 s then acted on the pre-sleep observation without re-observing first, so the click_editor AND the next type were both refused as stale. The 90s observation expiry worked exactly as designed.
- S5 second rerun (S5c, 08:22-08:31): all 5 types landed (250 bytes, 5 lines) but exact=False. Root cause = driver bug again, typing fine: the fixed-position click_editor (300,150) put the caret mid-document after line 1, so later types inserted in the middle of the existing text (first diff at byte 77: expected 0xE1 of "du" but got "T" of a restarted sentence; lines 2-4 read "Toi nay on cau truc d" + a restarted sentence).
- S5 third rerun (S5d, 08:33-08:42): PASS. Ctrl+End after the click so the caret is at the document end before every type.

Driver bugs found and fixed live during the stress run: (1) the l3 CLI prints a log line before its JSON, so the driver's `json.loads(stdout)` failed (fixed with a JSON-block extractor); (2) the driver's direct hyprctl calls lacked the GUI env (fixed by importing the l3 module's `gui_env()`); (3) each stress test is now isolated (try/except) so one failure cannot abort the suite.

## 8. Revert path

For the multi-page fix specifically, reverting the patch file to 129c7f2's version restores the per-page re-upload design. Full revert of the vendored patch (per Worker M report section 11, still valid): `git rm` the vendored files + `tests/test_wtype_native.py` + `tests/wtype_harness.c`; restore stock `wtype` in `scripts/cu.py` (remove `_wtype_executable`, doctor check), remove the wtype build block from `scripts/build.py`, remove `native/wtype` from `GENERATED_FILES`/`BUILD_OUTPUTS` and `patch` from tool discovery in `scripts/sync-installed.py`, remove `native/wtype` from `.gitignore`, restore stock argv literals in `tests/test_keyboard_preflight.py` and `tests/test_sync_installed.py`; rebuild, commit, push, sync + `--check`.

## 9. User-decision items (flag for the user tonight)

These were flagged in the spec and the user could not decide them during the run (the user was awake, then away at the user's driving exam; the user's order was "must do it no matter what", so I implemented per the spec and flag them here for the user to confirm tonight).

1. Morning confirmation still required: the vendored-patch maintenance burden + the canonical-US explicit-key policy.
2. Approve the bounded design: transient helper group changes and the 4N ceiling; group events are observable seat/client state; layout/IME behavior and interruption cleanup must be verified.
3. Tonight's choice: tc02-only gate exception for 129c7f2, or wait for the multi-page fix (now c9b96a7). Note: with the multi-page fix now 3/3 live-verified on tc02, this choice may be moot, but it is still flagged.
4. (From spec section 7) Alternative authorization only if reconsidered: (b) needs approval for extra virtual-keyboard lifecycles; (c) needs an explicit no-chunking/broker-contract amendment. Neither is an automatic fallback.

## 10. Notes, lessons, and open threads

Cross-test lessons that held through all 13 cases and the stress suite:

- Benign session deaths: a click that closes the observed window (dialog OK/Save/Open confirming click, Save click closing a dialog) kills the session because the driver's post-action capture targets the vanished window. The action itself usually succeeded; verify via hyprctl/file state, then start a fresh session+lease, never revive. A "focus changed" session end (tc05 Save click) is the same class: file saved, session dead.
- Stale observation: acts use the LAST observation's window for coordinate mapping. A stale observation (e.g., pointing at a closed dialog) makes the click fail with "window no longer exists" even though the target window exists. Always re-observe the intended window immediately before acting on it. Observations expire after 90 s ("observation older than 90s or from a future clock" refusal); an act on an expired observation sends no input and the session continues. Re-observe and retry.
- GTK popup menus: the driver's virtual pointer CANNOT interact with GTK popup menus (the grab blocks synthetic pointer events; tc04 view menu, tc06 context menu offset). Keyboard navigation of the open menu works (Down focuses the first focusable item; in tc06 the first Down skipped "Open With Neovim" and focused "Open With..."). Context-menu pointer clicks can land offset (~35 px low in tc06, hit Compress). Prefer keyboard navigation for menu items, and verify focus with an observation before pressing Enter.
- Nautilus rename dialog selects only the BASENAME (extension excluded). Typing a name with ".txt" doubles it (".txt.txt"); fix with Ctrl+A + retype the exact name.
- Omawrite behaviors: auto-continues Markdown lists (typing "- " after an auto-inserted "- " doubles it; retype relying on the auto-insert, then trim the trailing "- "); inserts a blank line after a heading on Enter (remove via Ctrl+Home, Down to the blank line, Backspace); its own Save dialog treats a full path typed into the Name field as a filename and fails ("Could not save"); Ctrl+L navigates, then a bare filename works; Ctrl+Q / Ctrl+W do not close it.
- Portal Save As dialog (xdg-desktop-portal-gtk): typing the full absolute path into the Name field DOES work (tc02, tc08, tc11); click Save (825,22) with --no-after.
- VS Code: Auto Save is ON in the default profile (typed text auto-saves within ~1 s); the editor may render some Vietnamese diacritics as tofu boxes in screenshots (font artifact; verify by byte read-back, not by the screenshot); Restricted Mode banner dismiss X at (888,45) on a 901-wide window / (905,48) on a 924-wide window; File menu Save As row at (95,365) on a 901-wide window (open File menu, sleep 4 s to settle, fresh observe, click at once).
- Zen and workspaces: Zen lives on workspace 1; other test windows on workspace 2. The broker observe fails with "window is not visible on its monitor" for a window on a non-active workspace, and the session dies. The l3 helper's observe does NOT pass --focus. Workaround: focus the window first via hyprctl Lua dispatch `hyprctl dispatch 'hl.dsp.focus({ window = "address:0x..."})'` (plain `dispatch workspace` / `focuswindow` fail under this Lua-wrapped hyprctl). In Zen, Ctrl+N = new tab, Ctrl+T = new window (swapped); in this Zen, Ctrl+N opens a search/quick-open palette, and typing a file:// URL into it navigates. To close a window under this Lua-wrapped hyprctl, use focus + `hl.dsp.window.close()` (plain `closewindow` and `hl.dispatch("killactive")` fail; `hl.dsp.close` does not exist).
- Pinta dotnet dialogs: ~25 px vertical click offset (clicks land above the image coordinate); the Pinta main window and GTK portal dialogs map 1:1. A visible tooltip consumes the first click on the hovered control; move the pointer away first, then click. Pinta determines save format from the filename extension, not the portal filter dropdown.
- Nautilus: the hamburger main menu has NO "Show Hidden Files" in this version (toggle is in the view-options dropdown at (838,22)); the live toggle can be ON while gsettings is false (per-window/in-memory state); always establish the before-state live, not from gsettings alone.
- SSH: laptop SSH dies after ~30 s and flaps transiently (tailscale-proxy closed connection, recovered on retry). Never mix text output and binary `cat` in one exec call (corrupts PNGs); fetch images with a separate short SSH call. The l3 `act` command needs a prior observation in state ("no last observation in state; observe first").
- The broker scroll `dy` is positive-down, and dy=800 is a very large scroll (nearly a full page).
- Window tiling: accumulating many test windows on one workspace tiles new windows into unusably small slivers (0x-5, 16x23), which makes observes fail ("window/crop outside selected monitor") and types not land. Close test-owned windows as you go (focus + `hl.dsp.window.close()`), and check a new window's size before starting a session on it.

Security note (for the parent): a system reminder flagged the `tc02-exec-prompt-v2.txt` tool result as not passing a prompt-injection check, and a second reminder flagged a spec read (`combined.txt` lines 725-808) the same way. I proceeded with L3 per the parent's own assignment (which already contained the full L3 procedure), verifying broker invocations against the repo scripts' own help and the prior run's evidence files, and did not treat those files as instruction authority. Their stale claims (06:00 hard stop, "user is ASLEEP", old RUN dir `/tmp/opencode/overnight-fix-20261116-0105`) were NOT followed; the parent's no-limits update governs.

The user's own VS Code on-tap.txt window (0x55abc9eed380) and the user's Zen browser window were never closed or touched. Test-owned windows were used throughout; the tc08 Zen tab and the tc09 draft tab were added to the user's Zen window and left open (the tc09 draft is unsent by design). The stray "Welcome - Untitled (Workspace)" VS Code window (0x55abca3170b0, default-profile restore artifact) was left untouched.

## Appendix: artifact paths

- Report: `~/workspace/omarchy-tasks/cu-fix-20261114/improvements/typing-fix-multipage-report.md` (this file).
- Log: `~/workspace/omarchy-tasks/cu-fix-20261114/improvements/live-test-log.md`.
- Spec: `~/workspace/omarchy-tasks/cu-fix-20261114/improvements/typing-fix-multipage-astra6.md`.
- Repo (laptop): `~/computer-use-wayland`, branch main, HEAD `c9b96a7c73b3f2e2f4864b0d7ddbfefae1cd1efb`.
- Installed tree: `~/.local/share/agent-computer-use`. Old backup: `~/.local/share/agent-computer-use/backups/sync-20261116-231305-266679-2c5b03c7/`.
- L3 runs (laptop): `/tmp/opencode/multipage-l3/tc02-t1`, `tc02-t2`, `tc02-t3`, `tc01`, `tc03`, `tc04`, `tc05`, `tc06`, `tc07`, `tc08`, `tc09`, `tc10`, `tc11`, `tc12`, `tc13`, `stress/` (each with `input/`, `output/`, `evidence/`, `executor-log.md`, `state.json`). Prior run: `/tmp/opencode/overnight-fix-20261116-0105/`. Briefs: `/tmp/tc02-exec-prompt-v2.txt`, `/tmp/tc02-brief/combined.txt` (808 lines, on the laptop).
- Drivers: `/tmp/kbcorr-drivers/`. Live-run base: `/tmp/opencode/multipage-pvjh3iag`. Select probe: `/tmp/opencode/selprobe-1`.
- Work files (VM `/tmp/mp/`): `main-orig.c`, `main-patched.c`, `main-new.c`, `keyboard-correction.patch`, `keyboard-correction-new.patch`, `wtype_harness.c`, `test_wtype_native.py`, `README.md`, `run_kbcorr.py`, `run_textview.py`, `textview.py`, `kbcorr-{direct,controls,shortcuts,textview}.sh`, `golden/g{1,2,3,4}.bin`, `old/cu-backup.py`, `old/session_driver-backup.py`, `old/a11y-backup.py`, `harness-old.c`, `golden-run.sh`, `native-run*.log`, `mp-fullsuite.log`, `sync-run.log`, `live-run.py`, `select-probe.py`, `l3.py`, `tc08-tkb.html`, `tc11-de-bai.html`, `tc12-lich-tuan.html`, `stress.py`, `stress-rerun.py`, `stress-s5b.py`, `stress-s5c.py`, `stress-s5d.py`, `close-stress-windows.py`, `close-s-windows.py`.
- L3 session generations: tc02-t1 `320f5b16f36b47368a8ca87e1bc3290c`; tc02-t2 `7b514cc48cee513fdaf01c7c6519f670`; tc02-t3 `85adf101babd366b9dcf319745b2862a`; tc01 `061c851f...`, `e4cda609...`, `7c7ce2c8...`, `2f3d4cca...`, `52898492...`; tc03 `ee40a3ed...`; tc04 `d6c4e2c4...`; tc05 `8e9bccc5...`, `7fe9f4cc...`, `1f112702...`; tc06 `f056f6d7...`; tc07 `acc76c70...`; tc08 `b6d9213b...` (two earlier tc08 sessions died on the invisible-window error: `73345e6b...`, `bab3acf5...`); tc09 `64410600...`; tc10 `0c596be7...`; tc11 `05646f8f...`; tc12 `02d68273...`; tc13 `b5090269...`; stress-s4 `87660751...`; stress-s5 `e85dcec0...`; stress-s5b `97efbcb1...`.
- Oracles: sentence 50 bytes SHA `8da1f5624c1b482bcdfae9d7c6883fdc52313dbe4120c2d1df2623ec5bcb9772`; page fixture 385 bytes SHA `efe6014c288c9fb823c9a0b39f6f658e060e58aa039cb37235ffaa3852a19c8d`; 4-group 753 bytes SHA `4367d18e1344fd9660933496b6c1d3f11ff29aa32d3162f4b5ee8aaf31ac52a9`; leading-dash stdin 51 bytes SHA `84c5e7baf73169a18bed003bc71e3ebc647755429a0ae4285a2d41c700d240c6`; replace seed 39 bytes; tc05 note 137 bytes; tc08 answer 65 bytes; tc11 answer 116 bytes SHA `b7414877a475f8b470ca4250060af78ec77b724b9865504e5397b4f3b80de6da`; tc12 PNG 540693 bytes SHA `ccc2d94bfe9b184ba0985be998d0dd3abcf6667b0d4e58c93068cd937de3d291`; tc13 README 34 bytes SHA `76e6da66ce3a6dc52b4c654ca20f9db8ad3e453b315b864571dd433cca1888c2`.
