# Computer-use-wayland: realistic task cases, phase 1

- **Session ID:** `ses-cu-testcases-20261115`
- **Model:** `openai/gpt-6-astra`
- **Reasoning:** HIGH
- **Date:** 2026-11-15
- **Pass:** 1 of max 2
- **Deliverable:** 13 task specifications for Luna 6 to execute later and an independent judge to score. No case was executed while writing this document.
- **Sources read first:** `/tmp/testcases-IMPROVEMENTS.md` in full, including the nine-item council ranking, dream verdict, §6 checklist and §7 honesty gate; `/tmp/testcases-muse-ssh-measurements.md` in full; relevant sections of `scripts/session_remote.py`, `scripts/cu.py`, `scripts/session_driver.py`, `scripts/a11y.py`, and `native/pointer.c` under `~/computer-use-wayland`; the supplied 21:03 Pinta failure account.
- **Repository observed:** HEAD `615bac9ad4946f38e5e42d985e63de8cb605dc96`. The working tree contains uncommitted Gate B and other changes. The tree was read, not modified.
- **Local app inventory:** executable paths were found for Pinta, VS Code, Zen Browser, Nautilus, Kitty and Foot. Installed desktop entries identify Omacalc as Calculator and Omawrite as a text/Markdown editor. App launch, accessibility support and current UI layouts were not tested.
- **Pinta baseline:** the user the owner scored the 21:03 yellow-circle demo **0/10**. Four attempts produced rectangle selections or no shape, never the requested circle. Pointer arrival does not change that score.

## Evidence boundaries and execution contract

### What the sources establish

The improvement plan says that no successful click, type or completed task had been established on the remote path, and that no broker start had been attempted after glass became ready at that plan's cutoff. The later supplied 21:03 account reports starts still failing with `native_unavailable`, despite successful individual glass/guard checks. These are different observation times, not permission to infer a successful task between them. The actual failing readiness check during the demo remains unidentified.

The measurements narrative reports approximately 434 ms warm observation, 295 ms status and 829 ms cold observation. The later plan's honesty gate qualifies this: only the 434.4 ms observation has the cited raw-record support; status/cold timings and the 3–4 s SSH anecdote are not independently established by those raw rows. The remaining observation time is not proven SSH latency. These cases impose no latency target and claim no accuracy gain.

The working-tree `native_readiness()` now returns stage diagnostics and selects liquid/plain material based on glass state. The broker now consumes the driver's top-level `session_continues`. These are inspected source changes, **not evidence that the active broker loaded them or that Gate B passed live**. Record the actual execution build and response rather than assuming the historical readiness behavior or the new behavior.

### Common procedure, inherited by every case

These instructions describe the later authorized execution phase only. They do not authorize running anything during this analysis phase.

1. **Isolation and preparation.** Run cases serially on the existing desktop. Create a fresh, unique run directory beneath `/tmp/opencode/`, with a separate `tcNN/` for each case. In each case below, `T` means that case's absolute directory. Substitute its actual absolute path wherever a task or command mentions `T`. Keep input fixtures in `T/input/`, requested results in `T/output/`, and evidence in `T/evidence/`. Setup may create the specified fixtures and launch a dedicated app window. Setup must not pre-create the requested result or perform the interaction being scored. Record before-state and a fixture manifest. Never overwrite an existing run directory.
2. **No dependency on another case.** Each setup specifies its own starting content. In particular, cases involving Pinta do not reuse test #1's image, and browser cases do not require any account or network service. If a required app/control is absent, record `BLOCKED`, score 0, and name the missing prerequisite. Do not install dependencies, update Omarchy, disable signature checks or change system configuration.
3. **Preserve user work.** Use only fresh documents, fixture files and dedicated test windows. Do not close or alter existing user tabs/documents. Do not send messages, buy anything, delete user files, reboot, or manipulate `~/.cache/agent-computer-use/cancelled`. If cancellation, ownership or recovery state refuses execution, stop and record the refusal. Do not clear a latch or bypass the session gate.
4. **Remote session required.** Use the real remote caller and the supported broker transport for all scored input. Give each case a fresh owned session. A successful `start` acknowledgement with `status: starting` is not readiness: require authenticated status to reach `state: running`, `driver: ready`, `guardian: active`, for the same generation. A `native_unavailable` response, failed startup or readiness timeout gives that case 0. Record bounded `stage`/`diagnostic` fields if present; do not guess a missing cause. Do not substitute direct `cu.py act`, direct native-pointer execution or another input channel. Never use ydotool.
5. **Lease and request handling.** Use the supported session client. If using `session_remote.py` directly, its inspected commands are `start --owner ... --lease-file ...`, `status --lease-file ...`, `request --lease-file ... --sequence ... --request ...`, `result --lease-file ... --sequence ...`, and `finish --lease-file ...`. Keep leases in a private mode-0700 directory under the existing computer-use cache, not directly in world-writable `/tmp`. Never publish lease secrets. Read `next_sequence` from authenticated status. Retrieve an accepted request's outcome by its sequence; never resubmit uncertain input as a fresh action.
6. **Observe, resolve, act, verify.** Identify the current window, then obtain a fresh observation. Desktop typing requires a window observation; screen observations only support pointer actions. Use image coordinates associated with the exact observation metadata; do not send global desktop coordinates as image coordinates. `image_point()` maps the image through its stored region and dimensions. A display-scaled or manually magnified screenshot is not a new calibrated observation.
7. **Small controls.** For designated pointer-targeting cases, click the actual icon using a fresh tight crop or larger `--max-width` observation. Keep that observation's identity and coordinate space. Check the selected tool/control state before the dependent action. Do not use a keyboard shortcut or semantic click as a replacement for the particular icon click being tested. Other cases may use AT-SPI only when the actual action or EditableText interface works; an `editable` flag alone is insufficient. Zen is not Chromium CDP.
8. **Checkpoint batching.** Batch already-known actions, up to the supported limit of 32, but stop at a dialog, navigation, tool change or uncertain layout. Inspect the returned successful after-image for the result; do not request duplicates needlessly. Re-observe before new coordinate input after a layout/focus change or refusal. With `image_policy: auto`, retain the referenced prior image for `visual.status: unchanged` and retain the new identity. Use `always` only when evidence delivery actually needs another copy. A normal clean capture may hide the overlay; its absence in such a capture is not proof the overlay never ran.
9. **Bounded recovery.** After a confirmed pre-input refusal, continue only if the trusted driver says the session continues; obtain a new observation and resolve the target again. Permit at most one evidence-driven corrective targeting attempt per control. Record both attempts. After an uncertain click/drag/type, inspect application state before doing anything else; never repeat the input blindly. Stop on terminal/unknown outcome. Do not keep trying historical coordinates until a screenshot looks plausible.
10. **Independent evidence.** Store before/after images actually received by the remote executor, relevant UI-state evidence and read-only filesystem checks. Shell/stdlib checks may inspect files after interaction. They must not manufacture, repair or export the requested result behind the GUI. For a terminal task, typing the specified command into the terminal is the intended GUI interaction; invoking that command from an external tool is not equivalent.
11. **Finish.** Request broker finish and verify completed cleanup, rather than treating `cleaning` as finished. Preserve results and evidence for the judge. Leave the requested app state where the case says to leave it. Never close unrelated apps. If cleanup is incomplete, report it and withhold the final-state point. Do not force recovery.

**Execution order:** retain test #1 as the Pinta regression identifier. Execute #2 first as the single-task remote proof gate. If #2 cannot start, stop the suite and label the remaining cases `NOT RUN — broker gate`, each contributing 0 to the attempted suite total; do not claim they independently reproduced a targeting failure. If #2 starts but fails its application task, inspect the evidence before proceeding; no parallel workers, new compositor or performance baseline is authorized by this suite.

**Timing record:** for every attempted case record caller-side monotonic timestamps for start submission, readiness, action submission, response receipt, actual image-byte receipt, first verified application result and finish completion. Record transferred bytes, action attempts, refusals and unknown outcomes separately. Application execution time, image transfer and model deliberation are different intervals. A local image pathname alone is not remote image receipt. One successful case is not a latency distribution; the plan's ≥20 samples per compared path belongs to a later, separately authorized measurement phase.

### Consistent scoring: 10 points per case

Every rubric below uses the same four named checks and weights:

- **R — Application result: 4 points.** Two concrete observable milestones, 2 points each.
- **F — Fidelity: 3 points.** Three correctness checks, 1 point each.
- **E — Independent evidence: 2 points.** Two corroborating checks, 1 point each.
- **S — Final state: 1 point.** The requested final app state and successful session finish, both required.

**Zero gate overrides all subscores.** A case with no meaningful task-specific application result is 0, even if the app opened, a tool highlighted, a cursor moved, a broker started or logs said `completed`. Setup fixtures and executor-authored success assertions earn nothing. Each case defines its minimum meaningful result. Only after that gate is met may the judge award the listed partial points, based on visible results or actual result files. Evidence points require evidence of a task result, not merely a log of attempts. A prohibited shortcut makes the case invalid and 0.

**Pass = 10/10.** Scores 1–9 mean partial completion, not a pass. A run report must distinguish `PASS`, `PARTIAL`, `FAIL`, `BLOCKED` and `NOT RUN`, with the score and artifact references. Report both the total out of 130 and the count of full passes. Missing cases must not silently disappear from the denominator.

## Test #1 — Pinta yellow circle: the targeting regression

**Difficulty:** Medium. **Weakness:** small toolbar/palette targeting, crop coordinates and tool-state verification.

**Task text:** “vẽ cho tôi 1 hình tròn màu vàng trong pinta đi, lưu thành `hinh-tron-vang.png` nhé”

**Setup**

- Start a dedicated Pinta document with a white 640×480 canvas, no selection and no pre-existing marks. Reserve `T/output/hinh-tron-vang.png`; it must not exist.
- The required result is one yellow circular outline on white, entirely inside the canvas, with no other marks. Use a visible stroke of roughly 4–8 canvas pixels and a diameter of roughly 160–240 canvas pixels.
- Obtain a baseline screenshot showing the blank canvas and available tool controls. The executor must inspect the installed UI to identify Ellipse and the shape options.

**Known four-attempt failure context — do not replay these coordinates**

1. Ellipse guessed at `(1038, 960)` from a scaled crop; yellow at `(1310, 1150)`. Drag produced **Rectangle Select**, not a circle.
2. Ellipse guessed at `(1038, 935)`; yellow at `(1278, 1148)`. Again rectangle selection. Escape cleared the first selection; the subsequent drag left no visible shape and no new History entry.
3. Ellipse guessed at `(1038, 979)` from a magnified toolbar crop; yellow at `(1283, 1150)`. Another rectangle selection, with a second Rectangle Select history entry.
4. Ellipse at `(1012, 956)` and yellow at `(1248, 1162)` from `visual_grounding`. Still Rectangle Select, with a third Rectangle Select history entry.

The broker returned `native_unavailable`; no pill appeared. Manual glass-ready and cursor-guard checks passed, but the actual failing broker check was not identified. The user's photo showed rainbow/moiré refraction on the canvas. Cursor position matched the drag endpoint. Neither the photograph's refraction nor cursor arrival is proof of painted pixels. The supplied diagnosis is tool/icon targeting, not demonstrated pointer-motion error.

**Executor steps**

1. Start the owned broker session and confirm actual readiness. Observe the Pinta window and its toolbar at usable resolution.
2. Identify the Ellipse icon from its visible label/tooltip or accessibility name, then perform a **desktop pointer click** on that icon. Capture/check selected-tool state. If Rectangle Select remains active, do not drag; obtain a fresh crop and allow only the single corrective attempt.
3. Select yellow with a pointer click on the identified palette swatch or color control. Verify the primary color is yellow. Select outline-only mode and the visible stroke width. Verify these controls before drawing.
4. Re-observe the canvas. Drag an equal-width/equal-height bounding box entirely within it; use the app's observed circle constraint if needed. Commit the shape if the tool requires it.
5. Inspect the canvas and History. A selection rectangle is a failed shape, not progress toward this task. If there is no painted ellipse, stop instead of trying the four historical points again.
6. Save through Pinta's Save As dialog to `T/output/hinh-tron-vang.png`, explicitly selecting PNG if required. Observe each dialog before input. Resolve only format prompts belonging to this new file.
7. Reopen that PNG in Pinta and inspect it. Preserve the original post-draw screenshot and History evidence; reopening may reset History. Finish the session.

**Observable outcome and judge verification**

The reopened PNG shows one yellow circular outline on a white 640×480 canvas. The judge inspects the full canvas, the pre-save History/tool evidence and the independently decoded PNG. Width and height of the painted shape should differ by no more than 10%; it must not be a rectangle or an elongated oval. The saved pixels, not the compositor effect, establish yellow.

**Zero gate:** no painted ellipse on the canvas and no valid saved ellipse image = **0**. The original Rectangle Select demo remains **0**, regardless of selected-tool screenshots.

**Rubric**

- **R (4):** a painted ellipse exists on the canvas (2); the saved PNG reopens with that ellipse (2).
- **F (3):** yellow stroke (1); circular proportions and specified approximate size/stroke (1); one outline, white background, no extra marks or clipping (1).
- **E (2):** PNG decodes as 640×480 with nonblank yellow shape pixels (1); pre-save History and selected-tool evidence support Ellipse rather than Rectangle Select (1).
- **S (1):** saved result is left visible without an active selection or dialog, and broker finish completes.

## Test #2 — Remote session proof: click, type and save a study note

**Difficulty:** Medium. **Weakness:** broker `native_unavailable` and end-to-end remote continuation.

**Task text:** “mở VS Code, ghi ‘Tối nay ôn cấu trúc dữ liệu lúc 20:30.’ rồi lưu vào `on-tap.txt` cho tôi”

**Setup**

- Use a dedicated VS Code window with a new empty text document; do not open the user's repository. `T/output/on-tap.txt` is absent.
- There must be no active test-owned session. Use a fresh owner/lease for this case. Do not remove someone else's session to obtain that state.
- Expected file text, with one trailing newline:

```text
Tối nay ôn cấu trúc dữ liệu lúc 20:30.
```

**Executor steps**

1. From the actual remote caller, submit broker `start` and retain its response. Wait for authenticated running/ready/active state for that generation. If startup fails, stop: **this test is 0 even if individual readiness probes pass**.
2. Obtain and receive a Pinta-independent VS Code window observation. Click the blank editor using desktop input and verify the editor caret/focus.
3. Type the exact Vietnamese line and a newline through the same session. Observe actual editor text. Do not use an external file write or AT-SPI setter for this case; it specifically proves a click plus keyboard text input.
4. Open Save As, observe the dialog, enter the absolute result path and save. Check that the editor tab shows `on-tap.txt` without an unsaved indicator.
5. Independently read the saved file and compare its UTF-8 text exactly. Capture the visible line in VS Code.
6. Finish through the broker, verify cleanup, and retain all caller timestamps, generation and request sequences without secrets.

**Observable outcome and judge verification**

VS Code visibly contains the accented sentence; the requested file exists with the exact bytes. The judge combines the application screenshot/file read-back with broker startup and finish records. An active service, `status: starting`, glass readiness, a driver-ready line alone or a cursor position cannot pass this case.

**Zero gate:** broker start never reaches usable readiness, or no task text appears in the editor/file = **0**. Text produced through a bypass input path is invalid.

**Rubric**

- **R (4):** task text appears in the editor following the brokered click/type sequence (2); a nonempty `on-tap.txt` is saved through the UI (2).
- **F (3):** exact sentence and accents (1); exact filename/path (1); one sentence, one trailing newline, no duplicate insertion (1).
- **E (2):** independent file read-back matches the visible text (1); trace connects successful start/readiness, click/type, application result and finish under the same generation with caller-side image receipt (1).
- **S (1):** file is saved, no dialog remains, and broker finish completes with no recovery required.

## Test #3 — Calculate a small student budget

**Difficulty:** Easy. **Weakness:** keyboard focus and verifying a calculation, rather than submitted keys.

**Task text:** “mở máy tính tính hộ tôi 125000 + 35000 + 20000, để kết quả trên màn hình nhé”

**Setup**

- Open a dedicated Omacalc instance from its installed Calculator entry. Do not assume it has the GNOME Calculator keypad.
- Begin with an empty expression. No result file is needed. Expected mathematical result: `180000`.

**Executor steps**

1. Start the session and observe Omacalc. Identify its actual expression field.
2. Click the field, enter `125000 + 35000 + 20000`, and use the app's observed evaluation control or Enter if its UI indicates that behavior.
3. Verify the displayed result. If the app evaluates live, do not insist on a nonexistent equals button.
4. Capture expression and result together where possible, leave the result visible, and finish.

**Observable outcome and judge verification**

The calculator displays the entered expression and the evaluated result `180000`, allowing normal locale separators such as `180,000` or `180.000`. The judge reads the calculator display and independently checks the arithmetic; a shell calculator output is not the application result.

**Zero gate:** no entered budget expression and no resulting calculation visible in Omacalc = **0**. Opening an empty calculator earns nothing.

**Rubric**

- **R (4):** the budget expression is visible in the calculator (2); an evaluated numeric result is visible (2).
- **F (3):** all three operands are correct (1); addition is used twice (1); result is numerically 180000 (1).
- **E (2):** a readable result screenshot is delivered (1); retained expression/history or a second UI view corroborates which calculation produced it (1).
- **S (1):** result stays visible without a stray menu/dialog, and broker finish completes.

## Test #4 — Reveal a hidden environment example through the Files menu

**Difficulty:** Easy. **Weakness:** small menu-icon targeting and native toggle state.

**Task text:** “mở thư mục bài tập trong Files, bật hiện file ẩn để tôi thấy `.env.example` với”

**Setup**

- Create `T/input/bai-tap/README.txt` containing `Bài tập thử nghiệm` and `T/input/bai-tap/.env.example` containing `APP_MODE=study` plus a newline. Neither contains secrets.
- Open Nautilus at `T/input/bai-tap/` in a dedicated window. Record the original hidden-files setting; establish a before-state where `.env.example` is hidden. This is setup, not credit.

**Executor steps**

1. Start the session, observe the folder and confirm that README is visible but `.env.example` is not.
2. Resolve the Files main-menu icon using a fresh crop/tooltip or accessible name, then **pointer-click that icon**. A keyboard shortcut is not a substitute for this step.
3. Read the opened menu. Activate Show Hidden Files or its translated equivalent once; check the toggle state if exposed.
4. Verify that `.env.example` appears beside README. Select `.env.example` without opening/editing it and capture the list and folder path.
5. Record evidence, then restore the original hidden-files setting. Finish the session. Restoring after evidence avoids leaving a global preference changed.

**Observable outcome and judge verification**

The hidden file visibly appears in the intended fixture directory. The judge compares before/after views and the checked toggle, and confirms the fixture file was not edited.

**Zero gate:** `.env.example` never becomes visible in Files = **0**, even if the menu opens.

**Rubric**

- **R (4):** `.env.example` is revealed in the file list (2); it is visibly selected in the correct folder (2).
- **F (3):** exact fixture folder (1); exact hidden filename (1); README remains present and file contents are unchanged (1).
- **E (2):** before/after images demonstrate the visibility change (1); menu-toggle evidence corroborates Show Hidden Files rather than a different folder/search result (1).
- **S (1):** original hidden-files preference is restored after evidence and broker finish completes.

## Test #5 — Save Vietnamese notes through a real Save As dialog

**Difficulty:** Medium. **Weakness:** multiline typing, accents, leading dash and dialog focus.

**Task text:** “ghi giúp tôi mấy việc mai làm vào `viec-ngay-mai.md`, giữ nguyên dấu tiếng Việt với xuống dòng nhé”

**Setup**

- Open a fresh unsaved document in a dedicated Omawrite window. If that installed editor cannot expose a usable editing/save surface, record the blocker rather than replacing the task silently.
- The target `T/output/viec-ngay-mai.md` is absent. Required text, including its final newline:

```text
# Việc ngày mai
- 08:00: học Cấu trúc dữ liệu.
- 14:00: làm bài OOP với Thịnh.
- Mang thẻ sinh viên, đừng quên!
```

**Executor steps**

1. Start the session, observe the editor and click the document body. Confirm actual text focus, not a search field.
2. Type the four lines exactly through desktop keyboard input. Inspect rendered text or the editor's source view for lost accents, missing dashes and duplicated lines.
3. Open Save As and observe the dialog. Enter `T/output/viec-ngay-mai.md`, save and resolve only this file's prompts.
4. Read the file independently as UTF-8 and compare all lines. Reopen the saved file in the editor and capture its contents.
5. Leave the saved document visible and finish.

**Observable outcome and judge verification**

The saved Markdown file contains the four exact lines. The judge uses byte/text read-back as the oracle where Markdown rendering hides `#` or list markers, and uses the reopened document as application corroboration.

**Zero gate:** none of the requested note text appears in the editor or saved file = **0**.

**Rubric**

- **R (4):** requested note content appears in the document (2); a nonempty Markdown file is saved and can be reopened (2).
- **F (3):** Vietnamese spelling/accents and punctuation match (1); all four lines, leading markers and final newline match (1); exact output filename and directory (1).
- **E (2):** independent UTF-8 read-back verifies content (1); reopening shows the saved note rather than a different untitled buffer (1).
- **S (1):** no unsaved changes/dialog remain and broker finish completes.

## Test #6 — Rename a disposable homework file

**Difficulty:** Medium. **Weakness:** row targeting, rename-dialog focus and extension preservation.

**Task text:** “đổi tên file `bai-tap-nhap.txt` thành `CTDL-buoi-3.txt` trong thư mục này giúp tôi”

**Setup**

- Create `T/input/doi-ten/bai-tap-nhap.txt` containing `Bài 3: danh sách liên kết` plus a newline, and a decoy `bai-tap-nhap-cu.txt` containing `Không đổi tên file này`.
- Record both original hashes. `CTDL-buoi-3.txt` must not exist. Open this directory in Nautilus.

**Executor steps**

1. Start the session and observe filenames. Select exactly `bai-tap-nhap.txt`, not the similarly named decoy.
2. Invoke Rename through the observed context menu or app-provided rename control. Observe whether the extension is included in the selected text.
3. Replace the filename with `CTDL-buoi-3.txt`, avoiding `.txt.txt`, and confirm.
4. Inspect the resulting file list. Independently verify the renamed file's bytes and the unchanged decoy.
5. Leave the renamed file selected and finish.

**Observable outcome and judge verification**

Files shows `CTDL-buoi-3.txt`; the old source name is gone because the fixture was renamed, not deleted. The judge checks its hash against the original and confirms the decoy remains unchanged.

**Zero gate:** neither the requested file nor any fixture file has undergone a visible rename = **0**. Merely opening Rename earns nothing. A wrong fixture rename is observable partial failure, never a pass.

**Rubric**

- **R (4):** a fixture rename is visible in the file list (2); the intended source now exists under the requested new name with its original bytes (2).
- **F (3):** exact new basename (1); exactly one `.txt` extension (1); decoy name and bytes remain unchanged (1).
- **E (2):** filesystem listing corroborates the intended old/new names (1); original/result hash comparison establishes content preservation (1).
- **S (1):** the correct new file is selected, no rename dialog remains, and broker finish completes.

## Test #7 — Drag a note into its course folder

**Difficulty:** Hard. **Weakness:** drag-and-drop receiving target and application-level move verification.

**Task text:** “kéo file `ghi-chu.txt` vào thư mục `CTDL` trong Files cho gọn giúp tôi”

**Setup**

- Create `T/input/sap-xep/ghi-chu.txt` containing `Stack: LIFO; Queue: FIFO.` plus a newline, an empty folder `T/input/sap-xep/CTDL/`, and a decoy folder `T/input/sap-xep/OOP/`.
- Record the source hash. Open the parent directory in a dedicated Nautilus window in a view where file and both folders are visible.

**Executor steps**

1. Start the session, observe the file row/icon and the exact `CTDL` drop target. Verify that the destination is a folder.
2. Perform one desktop pointer drag from the file's item body onto `CTDL`, with no copy modifier. Do not use cut/paste, `mv` or a file API to replace the drag.
3. Inspect the post-drop parent view before any retry. If an unexpected dialog or uncertain outcome occurs, inspect both paths rather than dragging again.
4. Open `CTDL` and verify `ghi-chu.txt` is inside. Read-only filesystem checks confirm source absence, destination hash equality and empty `OOP`.
5. Leave `CTDL` open with the moved file visible and finish.

**Observable outcome and judge verification**

The note has moved into `CTDL` and disappeared from the parent. The judge checks destination UI, filesystem paths and original/result hashes. A cursor ending over the folder is not evidence of a drop.

**Zero gate:** no file placement change occurs in the application/filesystem = **0**. A copied duplicate is only partial completion.

**Rubric**

- **R (4):** `ghi-chu.txt` appears inside `CTDL` following the recorded drag (2); the source disappears from the parent, establishing a move (2).
- **F (3):** destination is CTDL, not OOP (1); exact filename retained (1); bytes match the original (1).
- **E (2):** before-parent and after-destination screenshots corroborate the transfer (1); independent source/destination/hash checks agree (1).
- **S (1):** destination folder is left open with no pending drag/dialog, and broker finish completes.

## Test #8 — Read a timetable, choose the right row, save the answer

**Difficulty:** Hard. **Weakness:** reading the screen before acting, distinguishing similar rows and switching apps.

**Task text:** “xem thời khóa biểu này rồi ghi cho tôi môn Cấu trúc dữ liệu sáng thứ Ba học phòng nào, mấy giờ vào `lich-thu-ba.txt`”

**Setup**

- Create an offline UTF-8 HTML fixture `T/input/thoi-khoa-bieu.html`, with title `Thời khóa biểu — lớp thử nghiệm`, a normal visible table and these exact columns/rows:

| Ngày | Giờ | Môn học | Phòng |
|---|---|---|---|
| Thứ Hai | 08:00–09:30 | Cấu trúc dữ liệu | A2-203 |
| Thứ Ba | 07:00–08:30 | Lập trình hướng đối tượng | B1-305 |
| Thứ Ba | 09:00–10:30 | Cấu trúc dữ liệu | A2-407 |
| Thứ Tư | 09:00–10:30 | Cấu trúc dữ liệu | A2-203 |

- Open the file in a new Zen tab. Use normal HTML table markup with readable text and no scripts/network resources.
- Have a dedicated empty VS Code text document available. `T/output/lich-thu-ba.txt` is absent.
- For the scored read step, the executor must use the rendered table, not a shell read of the fixture or this specification's expected answer.

**Executor steps**

1. Start the session and observe the Zen window. Read the rendered headings and all candidate rows.
2. Identify the row matching both `Thứ Ba` and `Cấu trúc dữ liệu`. Retain an image showing that row with its column headings.
3. Switch to the dedicated VS Code document, re-observe it and enter one line in this format: `Thứ Ba: Cấu trúc dữ liệu, HH:MM–HH:MM, phòng ROOM.`
4. Save as `T/output/lich-thu-ba.txt` through the UI.
5. Independently read the result file and compare it with the retained source-row screenshot. Leave the note visible and finish.

**Observable outcome and judge verification**

The saved line is `Thứ Ba: Cấu trúc dữ liệu, 09:00–10:30, phòng A2-407.` with a newline. The judge compares the output file to the visible source row, not to the executor's assertion that it read correctly.

**Zero gate:** no timetable-derived answer is entered or saved = **0**. Merely displaying the table earns nothing.

**Rubric**

- **R (4):** a timetable answer appears in the note editor (2); it is saved in a nonempty `lich-thu-ba.txt` (2).
- **F (3):** correct day/course pairing (1); time is 09:00–10:30 (1); room is A2-407 (1).
- **E (2):** retained source screenshot shows the matching row and headings (1); independent result read-back matches the visible note (1).
- **S (1):** saved note remains visible without unsaved changes/dialogs and broker finish completes.

## Test #9 — Copy Vietnamese text across apps into an unsent draft

**Difficulty:** Hard. **Weakness:** clipboard transfer, textarea focus and unsent-state verification.

**Task text:** “copy đoạn nhắc lịch trong file sang ô nháp trang nhóm học giúp tôi, để đó thôi đừng gửi”

**Setup**

- Create `T/input/nhac-lich.txt` with this exact text and one final newline; open it in a dedicated VS Code editor:

```text
Thịnh ơi, mai 14:00 mình làm bài OOP ở thư viện nhé.
Nhớ mang laptop và thẻ sinh viên.
```

- Create `T/input/nhap-nhom.html` using the complete static document below. Open it in a new Zen tab. This is a deliberately local draft surface, **not Zalo or Messenger integration**. It has no submission endpoint or account.

```html
<!doctype html>
<html lang="vi">
<meta charset="utf-8">
<title>Nháp nhóm học — thử nghiệm cục bộ</title>
<body>
  <h1>Nháp nhóm học — thử nghiệm cục bộ</h1>
  <p>Không kết nối mạng. Không gửi tin nhắn.</p>
  <label for="draft">Nội dung nháp</label><br>
  <textarea id="draft" rows="8" cols="75"></textarea><br>
  <button type="button" disabled>Gửi — đã khóa trong thử nghiệm</button>
</body>
</html>
```

**Executor steps**

1. Start the session, observe the VS Code editor, focus its text and select the two lines. Copy through the application's keyboard copy operation.
2. Switch to the Zen fixture tab and obtain a fresh window observation. Verify the local title, empty textarea and disabled Send button.
3. Click inside `Nội dung nháp` and paste with the keyboard. Do not retype from this specification, fill the textarea semantically, or inject clipboard contents externally.
4. Inspect both lines for accents, newline and duplication. Do not press Send or Enter outside the textarea. Keep the unsent draft open.
5. Capture a readable full draft and the disabled button. Finish without closing the tab; the draft need not persist across reload.

**Observable outcome and judge verification**

Both lines appear exactly once in the textarea. There is no sent-message bubble or outgoing action; this fixture cannot send. The judge compares source and destination screenshots and the copy/paste action trace. A real contact or account must never be opened for this case.

**Zero gate:** the target textarea remains empty = **0**. Successful copying alone earns nothing.

**Rubric**

- **R (4):** first source line appears in the draft (2); second source line appears beneath it (2).
- **F (3):** accents and punctuation match (1); line break and single occurrence of each line are preserved (1); content is in the intended local draft field, with no send action (1).
- **E (2):** source/destination screenshots allow a direct content comparison (1); trace shows actual in-app copy and paste, and final UI shows the disabled Send control (1).
- **S (1):** unsent draft remains visible and broker finish completes.

## Test #10 — Replace a term in one study note

**Difficulty:** Medium. **Weakness:** find/replace fields, scope control and saved-content verification.

**Task text:** “trong ghi chú này đổi hết ‘linked list’ thành ‘danh sách liên kết’, chỉ sửa file này thôi nhé”

**Setup**

- Create and open `T/input/ghi-chu-ctdl.txt` in a dedicated VS Code window, with exactly:

```text
linked list lưu các nút rời nhau.
Ôn linked list trước khi làm bài.
stack dùng nguyên tắc LIFO.
```

- Create a sibling `T/input/khong-sua.txt` containing `linked list — giữ nguyên file này` plus a newline. Record its hash. No workspace-wide search is needed.

**Executor steps**

1. Start the session and observe the target file's title and contents.
2. Open the current editor's Find/Replace UI, not workspace-wide Replace. Observe both fields.
3. Enter `linked list` in Find and `danh sách liên kết` in Replace. Verify the two fields and match count before activating Replace All for this file.
4. Inspect both changed lines and the unchanged stack line. Save the existing fixture file.
5. Independently read the target file and compare the sibling hash. Leave the edited note visible and finish.

**Observable outcome and judge verification**

Both occurrences in `ghi-chu-ctdl.txt` become `danh sách liên kết`; the stack line and sibling file remain unchanged. The judge reads the saved file, replacement UI evidence and sibling hash.

**Zero gate:** no occurrence is actually replaced in the editor or saved file = **0**. Filled Find/Replace fields alone earn nothing.

**Rubric**

- **R (4):** first occurrence is replaced (2); second occurrence is replaced (2).
- **F (3):** replacement text and accents are exact (1); stack line and other target-file text remain unchanged (1); sibling file remains unchanged (1).
- **E (2):** saved-file read-back contains two replacements and no old term (1); before/after editor evidence shows single-file scope (1).
- **S (1):** edited file is saved, Find/Replace is dismissed, and broker finish completes.

## Test #11 — Scroll a long assignment and identify its last question

**Difficulty:** Hard. **Weakness:** actual wheel scrolling in Zen, reading new content and avoiding stale coordinates.

**Task text:** “kéo xuống cuối đề này xem câu cuối yêu cầu gì, ghi lại vào `cau-cuoi.txt` giúp tôi”

**Setup**

- Create an offline HTML file `T/input/de-bai.html`, UTF-8, titled `Bài tập CTDL — bản thử nghiệm`.
- Use a body with readable 20 px text and 24 px padding. Create 29 consecutive block sections with at least 180 CSS pixels of height each. Section number `n`, for `n` from 1 through 29, contains exactly `Câu n: Ôn lại khái niệm số n.`.
- Append a final section with visible heading `Câu 30` and text `Cài đặt hàng đợi bằng hai ngăn xếp; phân tích độ phức tạp của enqueue và dequeue.`. No scripts, remote resources or hidden content.
- Open in a fresh Zen tab at the top, with the final section initially below the viewport. Prepare an empty dedicated VS Code document. `T/output/cau-cuoi.txt` is absent.

**Executor steps**

1. Start the session and observe the top heading/first question to establish scroll position.
2. Place the pointer over the document content and perform wheel scroll actions in bounded batches. Inspect actual visible question numbers after each batch. Do not replace wheel scrolling with End, page search, DOM scrolling or a shell file read.
3. Stop once Câu 30 and its full text are visible. Capture the final section; verify that no further question follows it.
4. Switch to the note editor, re-observe and type `Câu 30: ` followed by the final question exactly. Save as `T/output/cau-cuoi.txt` with a newline.
5. Independently compare the file with the final-section screenshot. Leave the note visible and finish.

**Observable outcome and judge verification**

Zen visibly advances from the beginning to Câu 30 using wheel input. The saved note contains the final question, not an earlier decoy. The judge uses top/bottom screenshots, the wheel-action trace and the file read-back.

**Zero gate:** the page never visibly scrolls to later questions and no question-derived note is produced = **0**. Cursor movement over the page earns nothing.

**Rubric**

- **R (4):** the page visibly reaches the final question after wheel input (2); a nonempty final-question note is saved (2).
- **F (3):** correct question number 30 (1); queue-with-two-stacks requirement preserved (1); both `enqueue` and `dequeue` complexity requirements preserved (1).
- **E (2):** top/bottom screenshots and wheel trace demonstrate actual navigation (1); saved-file read-back agrees with the final-section screenshot (1).
- **S (1):** note is saved without a dialog, source tab remains available, and broker finish completes.

## Test #12 — Open a local timetable and capture a readable screenshot

**Difficulty:** Easy. **Weakness:** opening the correct file, framing and actual image delivery.

**Task text:** “mở lịch học tuần này rồi chụp riêng cửa sổ lịch cho tôi, chữ phải đọc được nhé”

**Setup**

- Create `T/input/lich-tuan.html` as a static UTF-8 HTML page titled `Lịch tuần — lớp thử nghiệm`. Use readable 22 px text and this visible content:

```text
Lịch học tuần này
Thứ Hai — 08:00 — Cấu trúc dữ liệu — A2-203
Thứ Ba — 14:00 — Lập trình hướng đối tượng — B1-305
Thứ Năm — 09:00 — Cơ sở dữ liệu — A2-407
```

- Open Nautilus at `T/input/`, with the file visible. The timetable is not already open in a test browser tab. Reserve `T/output/lich-tuan.png`.
- Use the test evidence channel to deliver the screenshot to the judge; do not send it to a real contact or expose other user windows.

**Executor steps**

1. Start the session, observe Files and select the exact HTML file.
2. Use Open With to choose the installed Zen Browser if the default handler is not a browser. Observe the chooser before acting.
3. Verify that Zen renders the timetable rather than showing source code or an error. Adjust the test window or zoom only as needed so all four lines are readable.
4. Capture the selected browser window through the supported observation mechanism. Preserve the delivered PNG bytes as `T/output/lich-tuan.png`; copying those bytes is evidence storage, not an external application-result shortcut.
5. Confirm the caller actually received and can decode the PNG, with byte count. Leave the rendered timetable visible and finish.

**Observable outcome and judge verification**

The correct local timetable is rendered in Zen and a readable window screenshot exists and is delivered. The judge opens the PNG and reads all entries. A laptop-local image path without image bytes at the caller is incomplete.

**Zero gate:** no timetable is rendered in the browser and no valid timetable screenshot is produced = **0**. Opening Files alone earns nothing.

**Rubric**

- **R (4):** Zen visibly renders the fixture timetable (2); a nonempty valid PNG of it is produced (2).
- **F (3):** title and all three schedule lines are included (1); text is legible and not clipped (1); capture is limited to the test browser window, without unrelated desktop content (1).
- **E (2):** independent PNG decode succeeds (1); caller receipt record includes actual PNG bytes/byte count matching the preserved image (1).
- **S (1):** timetable remains visible without menus/dialogs and broker finish completes.

## Test #13 — Use a terminal to create a course scratch folder

**Difficulty:** Medium. **Weakness:** terminal focus, shell quoting and verifying executed commands.

**Task text:** “mở terminal tạo thư mục `CTDL buoi 3` rồi tạo file `README.txt` ghi ‘Bài tập danh sách liên kết’ trong đó giúp tôi”

**Setup**

- Open a fresh Kitty or Foot terminal with working directory `T/output/`, at an idle shell prompt with no running job.
- `T/output/CTDL buoi 3/` must not exist. The executor must confirm that this is the dedicated test terminal before typing.
- Substitute the real absolute `T` in the following command; the new output directory has a unique run prefix and no shell-special characters except the quoted space in `CTDL buoi 3`.

**Executor steps**

1. Start the session and observe the dedicated terminal. Click it and verify the shell prompt.
2. Type `pwd` and press Enter. Read its output to confirm the terminal is in `T/output/`.
3. Through the terminal keyboard, enter the following command and press Enter. Do not run it from the executor's shell tool:

```sh
mkdir -- 'CTDL buoi 3' && printf '%s\n' 'Bài tập danh sách liên kết' > 'CTDL buoi 3/README.txt'
```

4. Observe the returned prompt and any error. If the command fails, do not blindly repeat the redirect.
5. Type `cat -- 'CTDL buoi 3/README.txt'` and press Enter. Verify the displayed Vietnamese line.
6. Independently inspect the directory and file from a read-only check. Leave the terminal showing the command/result and finish.

**Observable outcome and judge verification**

The directory with spaces exists, contains `README.txt`, and the file's exact UTF-8 text is `Bài tập danh sách liên kết` plus a newline. The terminal displays that same content. The judge checks both application output and filesystem result.

**Zero gate:** no requested directory/file is created and no corresponding terminal result exists = **0**. Typed but unexecuted commands do not count.

**Rubric**

- **R (4):** the requested directory is created by the terminal command (2); its nonempty README file is created (2).
- **F (3):** directory name preserves spaces and capitalization (1); filename is exactly `README.txt` (1); file text and trailing newline are exact (1).
- **E (2):** terminal screenshot shows execution and matching `cat` output (1); independent filesystem read-back verifies path and bytes (1).
- **S (1):** terminal returns to an idle prompt, result remains visible, and broker finish completes.

## Judge record and summary

For each case, record: case ID; execution build/runtime identity; start readiness or exact blocker; meaningful-result zero gate; R/F/E/S subscores; total; artifact paths; observed app result; attempted clicks/drags/types; refusals and uncertain outcomes; corrective attempt, if any; caller timestamps/bytes; finish outcome. Distinguish an app's result from a backend acknowledgement. If the evidence is insufficient, withhold the affected points rather than inferring success.

This suite qualifies single-task behavior only. It does not establish multiple independent pointers, worker isolation, fresh-login readiness, cancellation propagation, throughput or a performance improvement. Those remain separate gates from the improvement plan.

| Test # | Task | Difficulty | Weakness exercised | Points |
|---|---|---|---|---:|
| 1 | Yellow circle in Pinta | Medium | Small Ellipse/palette targets; tool-state regression | 10 |
| 2 | Brokered click/type/save note | Medium | `native_unavailable`; remote start-to-finish proof | 10 |
| 3 | Student-budget calculation | Easy | Field focus; evaluated result | 10 |
| 4 | Reveal `.env.example` in Files | Easy | Small menu icon; native toggle | 10 |
| 5 | Save Vietnamese Markdown | Medium | Accents, dashes, multiline input; Save As | 10 |
| 6 | Rename homework file | Medium | Similar filenames; dialog and extension targeting | 10 |
| 7 | Drag note into CTDL folder | Hard | Drag/drop receiver; move versus copy | 10 |
| 8 | Read timetable and save answer | Hard | Screen reading; matching similar rows; app switching | 10 |
| 9 | Copy into an unsent local draft | Hard | Cross-app clipboard; multiline text; no-send state | 10 |
| 10 | Replace a term in one note | Medium | Find/replace fields; single-file scope | 10 |
| 11 | Scroll to last assignment question | Hard | Zen wheel delivery; reading new content | 10 |
| 12 | Open timetable and deliver screenshot | Easy | Open With; framing; actual PNG receipt | 10 |
| 13 | Create a scratch folder in terminal | Medium | Focus; quoting; executed-command read-back | 10 |
| **Total** | **13 self-contained tasks** | **3 easy / 6 medium / 4 hard** | **Application results, never cursor-only credit** | **130** |
