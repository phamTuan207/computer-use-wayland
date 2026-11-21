# Worker Y9 step mapping and verification inventory: agy-y2 live run prep

- Repo: computer-use-wayland, branch todolist-push
- Sources: tests/realistic/agy-y2/test-01 through test-10 spec files, tests/realistic/agy-y2/simulate.mjs, tests/realistic/agy-y2/check.mjs, fixtures test-01, test-05, test-07, test-08, test-09, test-10, improvements/worker-y7-fix-log.md
- Purpose: the live runner (Zen, computer-use driver) follows section 1 step by step. The parent diffs the Python ported verify against section 4.
- Conventions: `d.click`, `d.type_text`, `d.clear_and_type`, `d.select`, `d.wait_for` are driver calls. `r.check("name", selector == expected)` is a live-runner intermediate assertion. `simulate.mjs` line numbers are the puppeteer lines performing the same action. simulate.mjs performs NO intermediate assertions in any test, it only drives actions and calls verifyTest at the end, so every `r.check` row shows "none" in the simulate column. That is by design, not a defect. See mismatch M2.
- Runner wait rule: `d.wait_for("js cond", 10, "desc")` waits for the stated DOM condition, not just element presence. Where the spec only says "verify", the runner reads the value first and asserts it, it never asserts from memory.

## Decisions already made (encoded here, not re-debated)

- D1. Test-10 spec step 15 (click #input-edit-watch-total) is SKIPPED as a fixture gap. The input is display:none (fixture line 114), no handler unhides it or listens to it, and the simulator also skips it (simulate.mjs lines 387-390 go straight from step-over to #btn-open-edit-watch). It is never counted as a driven step.
- D2. Test-01 uptime is covered ONLY by the intermediate check at spec step 15 (#pane-active-output contains "load average: 0.18, 0.22, 0.15"), NOT by the final verify. check.mjs reads terminalOutput (line 51) but never asserts it. See section 4, test-01, READ-NOT-ASSERTED.
- D3. Test-07 selected-count is covered ONLY by the intermediate check at spec step 8 (== "5"), NOT by the final verify. check.mjs reads selectedCount (line 216) but never asserts it. See section 4, test-07, READ-NOT-ASSERTED.
- D4. Test-07 skip-hole closers are the step 24 check (trash-counter "1" AND #file-row-img4 hidden) and the step 28 check (trash-counter "0"). Skipping delete plus restore (spec steps 23-29) still passes all 8 final checks (Y7 doubt 1), so these two intermediate checks are load-bearing.
- D5. Test-09 step 33 pinned expected value is "Milk, Eggs, Bread, Apples" (body value contains). The body value is never asserted in check.mjs, so step 33 is the only coverage.
- D6. Test-09 step 10 asserts the read value equals "Milk, Eggs, Bread" before typing ", Apples". The append relies on the cursor sitting at the end of the existing body text, so the runner reads first, then types.
- D7. Test-09 rename rule is precisely "never save with title Shopping while the archived note is active". The step 7 save MUST use the rename branch, it creates the 'shopping' key. Fixture lines 176-186. See section 3.
- D8. Test-02 has no spec step for clicking #btn-apply-network-settings, but the click is REQUIRED. check.mjs lines 96-97 assert the apply toast, which only appears via that click (fixture lines 364-368). The mapping adds it as an unnumbered required action after spec step 35. See mismatch M1.

## 1. Step-mapping tables

### Test 01, tmux session

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-01-tmux-session.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify initial state | r.check("initial", #session-count == "0" AND #status-indicator == "No Active Session") | none |
| 3 | Click #btn-new-session | d.click('#btn-new-session') | 37 |
| 4 | Verify session modal open | r.check("session-modal-open", #session-modal has class "open") | 38 (waitForSelector #session-modal.open) |
| 5 | Type "deploy" into #input-session-name | d.type_text('#input-session-name', 'deploy') | 39 |
| 6 | Click #btn-create-session | d.click('#btn-create-session') | 40 |
| 7 | Verify session name | r.check("session-name", #active-session-name == "deploy") | none |
| 8 | Verify status attached | r.check("status-attached", #status-indicator contains "deploy: Attached") | none |
| 9 | Verify counts 1 window, 1 pane | r.check("counts-1-1", #window-count == "1" AND #pane-count == "1") | none |
| 10 | Click #btn-split-horizontal | d.click('#btn-split-horizontal') | 43 |
| 11 | Verify pane count 2 | r.check("pane-count-2", #pane-count == "2") | none |
| 12 | Verify #pane-2 present and visible | r.check("pane-2-visible", #pane-2 present AND visible) | none |
| 13 | Type "uptime" into #pane-terminal-input | d.type_text('#pane-terminal-input', 'uptime') | 46 |
| 14 | Click #btn-send-command | d.click('#btn-send-command') | 47 |
| 15 | Verify uptime output (ONLY coverage, D2) | r.check("uptime-output", #pane-active-output contains "load average: 0.18, 0.22, 0.15") | none |
| 16 | Click #btn-new-window | d.click('#btn-new-window') | 50 |
| 17 | Verify window count 2 | r.check("window-count-2", #window-count == "2") | none |
| 18 | Click #btn-rename-window | d.click('#btn-rename-window') | 51 |
| 19 | Verify rename modal open | r.check("rename-modal-open", #rename-window-modal has class "open") | 52 (waitForSelector #rename-window-modal.open) |
| 20 | Clear and type "worker-logs" into #input-window-name | d.clear_and_type('#input-window-name', 'worker-logs') | 53-54 (clear via $eval, then type) |
| 21 | Click #btn-confirm-rename | d.click('#btn-confirm-rename') | 55 |
| 22 | Verify window tab 1 renamed | r.check("tab-1-renamed", #window-tab-1 contains "1:worker-logs") | none |
| 23 | Click #btn-split-vertical | d.click('#btn-split-vertical') | 58 |
| 24 | Verify pane count 2 | r.check("pane-count-2-again", #pane-count == "2") | none |
| 25 | Mistake: click #btn-kill-pane | d.click('#btn-kill-pane') | 61 |
| 26 | Verify pane count 1 and alert text | r.check("pane-killed", #pane-count == "1" AND #alert-banner contains "Pane 2 closed") | none |
| 27 | Recovery: click #btn-undo-pane | d.click('#btn-undo-pane') | 64 |
| 28 | Verify pane count back to 2 | r.check("pane-restored", #pane-count == "2") | none |
| 29 | Click #btn-detach-session | d.click('#btn-detach-session') | 67 |
| 30 | Verify detached status and overview visible | r.check("detached", #status-indicator contains "deploy: Detached" AND #session-overview visible, display block) | 68 (presence-only wait, see M3) |
| 31 | Verify session list shows 2 windows | r.check("overview-2-windows", #session-windows-deploy == "2 windows") | none |
| 32 | Click #btn-attach-deploy | d.click('#btn-attach-deploy') | 69 |
| 33 | Verify status attached again | r.check("status-reattached", #status-indicator contains "deploy: Attached") | none |
| 34 | Click #btn-save-session-state | d.click('#btn-save-session-state') | 72 |
| 35 | Verify saved message | r.check("saved-message", #saved-status-message contains "Session deploy saved with 2 windows") | none |

### Test 02, network settings

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-02-network-settings.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify initial state | r.check("initial", #wifi-toggle-status == "Disabled" AND #connected-network-name == "Not Connected") | none |
| 3 | Click #toggle-wifi | d.click('#toggle-wifi') | 77 |
| 4 | Verify Wi-Fi enabled and content shown | r.check("wifi-enabled", #wifi-toggle-status == "Enabled" AND #wifi-content displayed) | none |
| 5 | Click #network-row-homefiber | d.click('#network-row-homefiber') | 80 |
| 6 | Verify Wi-Fi auth modal active | r.check("wifi-auth-modal", #wifi-auth-modal has class "active") | 81 (waitForSelector #wifi-auth-modal.active) |
| 7 | Type "HomeKey2026" into #input-wifi-password | d.type_text('#input-wifi-password', 'HomeKey2026') | 82 |
| 8 | Click #btn-connect-wifi | d.click('#btn-connect-wifi') | 83 |
| 9 | Verify connected SSID and badge | r.check("connected", #connected-network-name == "HomeFiber-5G" AND #wifi-connection-badge == "Connected") | none |
| 10 | Click #btn-manage-known-networks | d.click('#btn-manage-known-networks') | 86 |
| 11 | Verify known networks panel visible | r.check("known-panel-visible", #known-networks-panel visible, display block) | none |
| 12 | Click #btn-forget-cafefree | d.click('#btn-forget-cafefree') | 87 |
| 13 | Verify #item-cafefree removed from DOM | r.check("cafefree-gone", #item-cafefree absent from DOM) | none |
| 14 | Click tab #nav-tab-bluetooth | d.click('#nav-tab-bluetooth') | 90 |
| 15 | Verify Bluetooth panel active | r.check("bt-panel-active", #bluetooth-panel has class "active") | none |
| 16 | Verify Bluetooth enabled | r.check("bt-enabled", #bt-toggle-status == "Enabled") | none |
| 17 | Click #btn-scan-bt-devices | d.click('#btn-scan-bt-devices') | 91 |
| 18 | Verify available list visible with MX Master | r.check("bt-scan", #available-bt-list visible AND contains #bt-device-mx-master) | none |
| 19 | Click #btn-pair-mx-master | d.click('#btn-pair-mx-master') | 92 |
| 20 | Verify paired list has MX Master 3S Paired | r.check("paired", #paired-bt-list contains #paired-item-mx-master with badge "Paired") | none |
| 21 | Click #toggle-bluetooth (off) | d.click('#toggle-bluetooth') | 95 |
| 22 | Verify Bluetooth disabled | r.check("bt-disabled", #bt-toggle-status == "Disabled") | none |
| 23 | Click #toggle-bluetooth again (on) | d.click('#toggle-bluetooth') | 96 |
| 24 | Verify Bluetooth enabled again | r.check("bt-enabled-again", #bt-toggle-status == "Enabled") | none |
| 25 | Verify paired device persists | r.check("paired-persists", #paired-item-mx-master present in #paired-bt-list) | none |
| 26 | Click tab #nav-tab-wifi | d.click('#nav-tab-wifi') | 99 |
| 27 | Click #btn-network-properties | d.click('#btn-network-properties') | 100 |
| 28 | Verify properties panel active | r.check("props-panel", #network-properties-panel has class "active") | 101 (waitForSelector #network-properties-panel.active) |
| 29 | Click #toggle-metered-connection | d.click('#toggle-metered-connection') | 102 |
| 30 | Verify metered indicator | r.check("metered", #metered-status-indicator == "Metered") | none |
| 31 | Click #btn-save-wifi-properties | d.click('#btn-save-wifi-properties') | 103 |
| 32 | Click tab #nav-tab-status | d.click('#nav-tab-status') | 106 |
| 33 | Verify summary SSID | r.check("summary-ssid", #summary-wifi-ssid == "HomeFiber-5G") | none |
| 34 | Verify summary metered Yes | r.check("summary-metered", #summary-wifi-metered == "Yes") | none |
| 35 | Verify summary BT device | r.check("summary-bt", #summary-bt-device == "MX Master 3S") | none |
| - | REQUIRED, no spec step (D8, M1): click #btn-apply-network-settings | d.click('#btn-apply-network-settings'), then r.check("apply-toast", #settings-status-toast contains "Network settings applied successfully" AND has class "active") | 107 |

### Test 03, photo editor

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-03-photo-editor.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify editor ready, no file | r.check("initial", #editor-status-text == "Ready. No file loaded.") | none |
| 3 | Click #file-item-sunset | d.click('#file-item-sunset') | 112 |
| 4 | Click #btn-load-photo | d.click('#btn-load-photo') | 113 |
| 5 | Verify filename | r.check("filename", #current-filename == "sunset.jpg") | none |
| 6 | Verify dims 1200x900 | r.check("dims-orig", #dim-width == "1200" AND #dim-height == "900") | none |
| 7 | Click #tool-tab-crop | d.click('#tool-tab-crop') | 116 |
| 8 | Verify crop controls active | r.check("crop-active", #crop-controls has class "active") | none |
| 9 | Click #btn-ratio-4-3 | d.click('#btn-ratio-4-3') | 117 |
| 10 | Verify crop ratio 4:3 | r.check("ratio-4-3", #active-crop-ratio == "4:3") | none |
| 11 | Click #btn-apply-crop | d.click('#btn-apply-crop') | 118 |
| 12 | Verify dims 1000x750 | r.check("dims-cropped", #dim-width == "1000" AND #dim-height == "750") | none |
| 13 | Click #tool-tab-filters | d.click('#tool-tab-filters') | 121 |
| 14 | Verify filters panel active | r.check("filters-active", #filters-panel has class "active") | none |
| 15 | Click #btn-filter-vivid | d.click('#btn-filter-vivid') | 122 |
| 16 | Verify filter Vivid | r.check("filter-vivid", #active-filter-name == "Vivid") | none |
| 17 | Click #tool-tab-adjust | d.click('#tool-tab-adjust') | 125 |
| 18 | Verify brightness 0 | r.check("brightness-0", #brightness-display == "0") | none |
| 19 | Click #btn-brightness-plus | d.click('#btn-brightness-plus') | 126 |
| 20 | Verify brightness 20 | r.check("brightness-20", #brightness-display == "20") | none |
| 21 | Mistake: click #btn-undo-adjust | d.click('#btn-undo-adjust') | 127 |
| 22 | Verify brightness back to 0 | r.check("brightness-undone", #brightness-display == "0") | none |
| 23 | Click #tool-tab-transform | d.click('#tool-tab-transform') | 130 |
| 24 | Click #btn-rotate-90-cw | d.click('#btn-rotate-90-cw') | 131 |
| 25 | Verify rotation 90 deg | r.check("rotation-90", #rotation-angle == "90 deg") | none |
| 26 | Verify dims 750x1000 | r.check("dims-rotated", #dim-width == "750" AND #dim-height == "1000") | none |
| 27 | Click #btn-open-export | d.click('#btn-open-export') | 134 |
| 28 | Verify export modal active | r.check("export-modal", #export-modal has class "active") | 135 (waitForSelector #export-modal.active) |
| 29 | Select "PNG" in #select-export-format | d.select('#select-export-format', 'PNG') | 136 (page.select) |
| 30 | Verify dialog format PNG | r.check("dialog-format", #dialog-format-display == "PNG") | none |
| 31 | Verify dialog dims "750 x 1000 px" | r.check("dialog-dims", #dialog-dimensions-display == "750 x 1000 px") | none |
| 32 | Click #btn-confirm-export | d.click('#btn-confirm-export') | 137 |
| 33 | Verify export banner | r.check("export-banner", #export-status-banner contains "Image exported: sunset.png (750x1000, PNG)") | none |

### Test 04, email compose

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-04-email-compose.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify initial counters | r.check("initial", #sent-folder-counter == "12" AND #drafts-folder-counter == "0") | none |
| 3 | Click #btn-compose-mail | d.click('#btn-compose-mail') | 142 |
| 4 | Verify compose pane open | r.check("compose-open", #compose-pane has class "open") | 143 (waitForSelector #compose-pane.open) |
| 5 | Type "team@example.com" into #input-recipient-to | d.type_text('#input-recipient-to', 'team@example.com') | 144 |
| 6 | Click #btn-add-cc | d.click('#btn-add-cc') | 145 |
| 7 | Verify CC group visible | r.check("cc-visible", #cc-group visible) | none |
| 8 | Type "audit@example.com" into #input-recipient-cc | d.type_text('#input-recipient-cc', 'audit@example.com') | 146 |
| 9 | Type "Q4 report" into #input-mail-subject | d.type_text('#input-mail-subject', 'Q4 report') | 147 |
| 10 | Type body into #input-mail-body | d.type_text('#input-mail-body', 'Attached is the Q4 performance overview.') | 148 |
| 11 | Click #btn-open-attachment-picker | d.click('#btn-open-attachment-picker') | 151 |
| 12 | Verify attachment picker modal active | r.check("picker-active", #attachment-picker-modal has class "active") | 152 (waitForSelector #attachment-picker-modal.active) |
| 13 | Click #file-option-report-pdf | d.click('#file-option-report-pdf') | 153 |
| 14 | Click #btn-confirm-attach-file | d.click('#btn-confirm-attach-file') | 154 |
| 15 | Verify attached list has chip | r.check("chip-present", #attached-files-list contains #attachment-chip-report) | none |
| 16 | Verify attachment counter 1 | r.check("attach-count-1", #attachment-counter == "1") | none |
| 17 | Click #btn-save-draft-mail | d.click('#btn-save-draft-mail') | 157 |
| 18 | Verify drafts counter 1 | r.check("drafts-1", #drafts-folder-counter == "1") | none |
| 19 | Click #btn-close-composer | d.click('#btn-close-composer') | 158 |
| 20 | Verify compose pane hidden | r.check("compose-hidden", #compose-pane has class "hidden") | none |
| 21 | Click #nav-folder-drafts | d.click('#nav-folder-drafts') | 161 |
| 22 | Click #draft-entry-q4 | d.click('#draft-entry-q4') | 162 |
| 23 | Verify compose open and subject value | r.check("draft-reopened", #compose-pane has class "open" AND #input-mail-subject value == "Q4 report") | 163 (waitForSelector #compose-pane.open only, no subject read, see M10) |
| 24 | Mistake: click #btn-remove-attachment-report | d.click('#btn-remove-attachment-report') | 166 |
| 25 | Verify counter 0 and list empty | r.check("attach-removed", #attachment-counter == "0" AND #attached-files-list empty) | none |
| 26 | Click #btn-open-attachment-picker again | d.click('#btn-open-attachment-picker') | 169 |
| 27 | Click #file-option-report-pdf again | d.click('#file-option-report-pdf') | 171 |
| 28 | Click #btn-confirm-attach-file again | d.click('#btn-confirm-attach-file') | 172 |
| 29 | Verify counter 1 and chip present | r.check("attach-restored", #attachment-counter == "1" AND #attachment-chip-report present) | none |
| 30 | Click #btn-dispatch-send | d.click('#btn-dispatch-send') | 175 |
| 31 | Verify compose pane hidden | r.check("compose-hidden-after-send", #compose-pane has class "hidden") | none |
| 32 | Verify sent toast | r.check("sent-toast", #toast-alert contains "Email sent to team@example.com with attachment report.pdf") | none |
| 33 | Verify sent counter 13 | r.check("sent-13", #sent-folder-counter == "13") | none |

### Test 05, spreadsheet chart

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-05-spreadsheet-chart.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify sheet name | r.check("sheet-name", #active-sheet-name == "Sales Forecast") | none |
| 3 | Type "Month" into #cell-input-a1 | d.type_text('#cell-input-a1', 'Month') | 180 |
| 4 | Type "Sales" into #cell-input-b1 | d.type_text('#cell-input-b1', 'Sales') | 181 |
| 5 | Type "Jan" into #cell-input-a2 | d.type_text('#cell-input-a2', 'Jan') | 182 |
| 6 | Type "1200" into #cell-input-b2 | d.type_text('#cell-input-b2', '1200') | 183 |
| 7 | Type "Feb" into #cell-input-a3 | d.type_text('#cell-input-a3', 'Feb') | 184 |
| 8 | Type "1500" into #cell-input-b3 | d.type_text('#cell-input-b3', '1500') | 185 |
| 9 | Type "Mar" into #cell-input-a4 | d.type_text('#cell-input-a4', 'Mar') | 186 |
| 10 | Mistake: type "9800" into #cell-input-b4 | d.type_text('#cell-input-b4', '9800') | 189 |
| 11 | Verify #cell-value-b4 is "9800" | r.check("b4-mistake", #cell-value-b4 == "9800") | none |
| 12 | Type "Total" into #cell-input-a5 | d.type_text('#cell-input-a5', 'Total') | 192 |
| 13 | Click #cell-input-b5 to select B5 | d.click('#cell-input-b5') | 193 |
| 14 | Type "=SUM(B2:B4)" into #formula-bar-input | d.type_text('#formula-bar-input', '=SUM(B2:B4)') | 194 |
| 15 | Click #btn-commit-formula | d.click('#btn-commit-formula') | 195 |
| 16 | Verify #cell-value-b5 is "12500" | r.check("total-wrong", #cell-value-b5 == "12500") | none |
| 17 | Type "Average" into #cell-input-a6 | d.type_text('#cell-input-a6', 'Average') | 198 |
| 18 | Click #cell-input-b6 to select B6 | d.click('#cell-input-b6') | 199 |
| 19 | Type "=AVERAGE(B2:B4)" into #formula-bar-input | d.type_text('#formula-bar-input', '=AVERAGE(B2:B4)') | 200 |
| 20 | Click #btn-commit-formula | d.click('#btn-commit-formula') | 201 |
| 21 | Verify #cell-value-b6 is "4166.67" | r.check("avg-wrong", #cell-value-b6 == "4166.67") | none |
| 22 | Clear and type "1800" into #cell-input-b4 | d.clear_and_type('#cell-input-b4', '1800') | 204-206 (click, clear via $eval, type) |
| 23 | Click #btn-recalculate-sheet | d.click('#btn-recalculate-sheet') | 207 |
| 24 | Verify #cell-value-b5 updates to "4500" | r.check("total-fixed", #cell-value-b5 == "4500") | none |
| 25 | Verify #cell-value-b6 updates to "1500.00" | r.check("avg-fixed", #cell-value-b6 == "1500.00") | none |
| 26 | Click #btn-insert-chart-modal | d.click('#btn-insert-chart-modal') | 210 |
| 27 | Verify chart modal active | r.check("chart-modal", #chart-modal has class "active") | 211 (waitForSelector #chart-modal.active) |
| 28 | Select "Bar" in #select-chart-type | d.select('#select-chart-type', 'Bar') | 212 (page.select) |
| 29 | Click #btn-render-chart | d.click('#btn-render-chart') | 213 |
| 30 | Verify chart SVG present | r.check("chart-svg", #chart-wrapper contains #sales-bar-svg) | none |
| 31 | Clear and type "Q1 Regional Sales" into #input-chart-title | d.clear_and_type('#input-chart-title', 'Q1 Regional Sales') | 216-218 (click, clear via $eval, type) |
| 32 | Click #btn-apply-chart-title | d.click('#btn-apply-chart-title') | 219 |
| 33 | Verify chart title | r.check("chart-title", #chart-title-text == "Q1 Regional Sales") | none |
| 34 | Click #btn-save-sheet-state | d.click('#btn-save-sheet-state') | 222 |
| 35 | Verify save toast | r.check("save-toast", #sheet-status-toast contains "Sheet saved: Total=4500, Average=1500.00, Chart=Q1 Regional Sales") | none |

### Test 06, video call

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-06-video-call.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify lobby state | r.check("initial", #call-status-badge == "Lobby" AND #participant-count == "0") | none |
| 3 | Type "Sprint Planning" into #input-meeting-id | d.type_text('#input-meeting-id', 'Sprint Planning') | 227 |
| 4 | Type "James" into #input-display-name | d.type_text('#input-display-name', 'James') | 228 |
| 5 | Click #btn-join-meeting | d.click('#btn-join-meeting') | 229 |
| 6 | Verify connected, 4 participants | r.check("joined", #call-status-badge == "Connected" AND #participant-count == "4") | none |
| 7 | Verify room name | r.check("room", #room-name-display == "Sprint Planning") | none |
| 8 | Click #btn-toggle-mic (mute) | d.click('#btn-toggle-mic') | 232 |
| 9 | Verify mic muted | r.check("mic-muted", #mic-status-indicator == "Muted" AND has class "muted") | none |
| 10 | Click #btn-toggle-mic (unmute) | d.click('#btn-toggle-mic') | 233 |
| 11 | Verify mic unmuted | r.check("mic-unmuted", #mic-status-indicator == "Unmuted" AND has class "active") | none |
| 12 | Click #btn-toggle-cam (off) | d.click('#btn-toggle-cam') | 236 |
| 13 | Verify camera off | r.check("cam-off", #cam-status-indicator == "Camera Off" AND has class "off") | none |
| 14 | Click #btn-toggle-cam (on) | d.click('#btn-toggle-cam') | 237 |
| 15 | Verify camera on | r.check("cam-on", #cam-status-indicator == "Camera On" AND has class "active") | none |
| 16 | Click #btn-share-screen | d.click('#btn-share-screen') | 240 |
| 17 | Verify screenshare modal active | r.check("share-modal", #screenshare-modal has class "active") | 241 (waitForSelector #screenshare-modal.active) |
| 18 | Click #screen-option-desktop | d.click('#screen-option-desktop') | 242 |
| 19 | Click #btn-confirm-screenshare | d.click('#btn-confirm-screenshare') | 243 |
| 20 | Verify share banner visible with text | r.check("share-banner", #screen-share-banner contains "Screen sharing active" AND visible) | none |
| 21 | Click #btn-stop-screenshare | d.click('#btn-stop-screenshare') | 244 |
| 22 | Verify share banner hidden | r.check("share-stopped", #screen-share-banner has class "hidden") | none |
| 23 | Click #btn-raise-hand | d.click('#btn-raise-hand') | 247 |
| 24 | Verify hand raised | r.check("hand-raised", #hand-raise-indicator has class "raised" AND text == "Hand Raised") | none |
| 25 | Click #btn-open-chat | d.click('#btn-open-chat') | 250 |
| 26 | Verify chat sidebar open | r.check("chat-open", #chat-sidebar has class "open") | none |
| 27 | Type "Ready for updates" into #input-chat-message | d.type_text('#input-chat-message', 'Ready for updates') | 251 |
| 28 | Click #btn-send-chat | d.click('#btn-send-chat') | 252 |
| 29 | Verify chat list contains message | r.check("chat-sent", #chat-message-list contains "Ready for updates") | none |
| 30 | Click #btn-leave-meeting | d.click('#btn-leave-meeting') | 255 |
| 31 | Verify disconnected and rejoin panel visible | r.check("left", #call-status-badge == "Disconnected" AND #rejoin-prompt-panel visible) | none |
| 32 | Click #btn-rejoin-meeting | d.click('#btn-rejoin-meeting') | 256 |
| 33 | Verify connected again, 4 participants | r.check("rejoined", #call-status-badge == "Connected" AND #participant-count == "4") | none |
| 34 | Click #btn-save-call-summary | d.click('#btn-save-call-summary') | 259 |
| 35 | Verify summary toast | r.check("summary-toast", #call-summary-toast contains "Meeting Sprint Planning: 4 participants, audio active, video active") | none |

### Test 07, file manager

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-07-file-manager.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify initial counts | r.check("initial", #total-files-count == "8" AND #selected-files-count == "0") | none |
| 3 | Click #checkbox-file-img1 | d.click('#checkbox-file-img1') | 264 |
| 4 | Click #checkbox-file-img2 | d.click('#checkbox-file-img2') | 265 |
| 5 | Click #checkbox-file-img3 | d.click('#checkbox-file-img3') | 266 |
| 6 | Click #checkbox-file-img4 | d.click('#checkbox-file-img4') | 267 |
| 7 | Click #checkbox-file-img5 | d.click('#checkbox-file-img5') | 268 |
| 8 | Verify selected count 5 (ONLY coverage, D3) | r.check("selected-5", #selected-files-count == "5") | none |
| 9 | Click #btn-open-bulk-rename | d.click('#btn-open-bulk-rename') | 271 |
| 10 | Verify bulk rename modal active | r.check("rename-modal", #bulk-rename-modal has class "active") | 272 (waitForSelector #bulk-rename-modal.active) |
| 11 | Type "photo-2026-##" into #input-rename-pattern | d.type_text('#input-rename-pattern', 'photo-2026-##') | 273 |
| 12 | Click #btn-apply-bulk-rename | d.click('#btn-apply-bulk-rename') | 274 |
| 13 | Verify file 1 renamed | r.check("name-1", #file-name-img1 == "photo-2026-01.jpg") | none |
| 14 | Verify file 5 renamed | r.check("name-5", #file-name-img5 == "photo-2026-05.jpg") | none |
| 15 | Click #checkbox-file-img1 (re-select) | d.click('#checkbox-file-img1') | 277 |
| 16 | Click #checkbox-file-img2 (re-select) | d.click('#checkbox-file-img2') | 278 |
| 17 | Click #checkbox-file-img3 (re-select) | d.click('#checkbox-file-img3') | 279 |
| 18 | Click #btn-open-move-dialog | d.click('#btn-open-move-dialog') | 280 |
| 19 | Verify move modal active | r.check("move-modal", #move-modal has class "active") | 281 (waitForSelector #move-modal.active) |
| 20 | Click #move-target-archive | d.click('#move-target-archive') | 282 |
| 21 | Click #btn-confirm-move | d.click('#btn-confirm-move') | 283 |
| 22 | Verify Archive has 3 files | r.check("archive-3", #folder-count-archive contains "3 files") | none |
| 23 | Mistake: click #btn-delete-file-img4 | d.click('#btn-delete-file-img4') | 286 |
| 24 | Verify row hidden and trash 1 (skip-hole closer, D4) | r.check("deleted", #file-row-img4 has class "hidden" AND #trash-counter == "1") | none |
| 25 | Click #nav-folder-trash | d.click('#nav-folder-trash') | 289 |
| 26 | Verify trash table visible with trash row | r.check("trash-view", #trash-table visible AND contains #trash-row-img4) | none |
| 27 | Click #btn-restore-file-img4 | d.click('#btn-restore-file-img4') | 290 |
| 28 | Verify trash counter 0 (skip-hole closer, D4) | r.check("trash-0", #trash-counter == "0") | none |
| 29 | Click #nav-folder-root | d.click('#nav-folder-root') | 291 |
| 30 | Click #btn-new-folder | d.click('#btn-new-folder') | 294 |
| 31 | Verify new folder modal active | r.check("folder-modal", #new-folder-modal has class "active") | 295 (waitForSelector #new-folder-modal.active) |
| 32 | Type "Processed" into #input-new-folder-name | d.type_text('#input-new-folder-name', 'Processed') | 296 |
| 33 | Click #btn-confirm-create-folder | d.click('#btn-confirm-create-folder') | 297 |
| 34 | Click #btn-generate-inventory-report | d.click('#btn-generate-inventory-report') | 300 |
| 35 | Verify inventory toast | r.check("inventory-toast", #inventory-summary-toast contains "Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created") | none |

### Test 08, devtools

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-08-devtools.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify panel collapsed | r.check("initial", #devtools-panel has class "collapsed" AND #devtools-toggle-btn contains "Open DevTools") | none |
| 3 | Click #devtools-toggle-btn | d.click('#devtools-toggle-btn') | 305 |
| 4 | Verify panel expanded | r.check("panel-expanded", #devtools-panel has class "expanded") | none |
| 5 | Click tab #tab-console | d.click('#tab-console') | 308 |
| 6 | Verify console view visible, log count 0 | r.check("console-view", #view-console visible AND #console-log-count == "0") | none |
| 7 | Type "window.appVersion" into #input-console-eval | d.type_text('#input-console-eval', 'window.appVersion') | 309 |
| 8 | Click #btn-eval-console | d.click('#btn-eval-console') | 310 |
| 9 | Verify log contains v2.4.1 | r.check("eval-result", #console-output-log contains "v2.4.1") | none |
| 10 | Verify log count 1 | r.check("log-count-1", #console-log-count == "1") | none |
| 11 | Click tab #tab-network | d.click('#tab-network') | 313 |
| 12 | Verify network view visible, total 6 | r.check("network-view", #view-network visible AND #network-total-count == "6") | none |
| 13 | Type "api" into #input-network-filter | d.type_text('#input-network-filter', 'api') | 314 |
| 14 | Click #btn-apply-network-filter | d.click('#btn-apply-network-filter') | 315 |
| 15 | Verify visible network count 3 | r.check("net-visible-3", #network-visible-count == "3") | none |
| 16 | Verify row api-users visible | r.check("row-users-visible", #row-req-api-users visible) | none |
| 17 | Verify row api-checkout visible | r.check("row-checkout-visible", #row-req-api-checkout visible) | none |
| 18 | Click row #row-req-api-checkout | d.click('#row-req-api-checkout') | 318 |
| 19 | Verify detail pane open | r.check("detail-open", #request-detail-pane has class "open") | none |
| 20 | Verify detail status 404 | r.check("detail-404", #detail-status-code == "404 Not Found") | none |
| 21 | Click tab #tab-detail-response | d.click('#tab-detail-response') | 319 |
| 22 | Verify response body contains endpoint deprecated | r.check("detail-body", #detail-response-body contains "endpoint deprecated") | none |
| 23 | Click #btn-close-detail | d.click('#btn-close-detail') | 320 |
| 24 | Verify detail pane closed | r.check("detail-closed", #request-detail-pane has class "closed") | none |
| 25 | Click tab #tab-console | d.click('#tab-console') | 323 |
| 26 | Verify console view visible | r.check("console-view-again", #view-console visible) | none |
| 27 | Mistake: click #btn-clear-console | d.click('#btn-clear-console') | 324 |
| 28 | Verify log count 0 and log empty | r.check("console-cleared", #console-log-count == "0" AND #console-output-log empty) | none |
| 29 | Type "console.log('ready')" into #input-console-eval | d.type_text('#input-console-eval', "console.log('ready')") | 325 |
| 30 | Click #btn-eval-console | d.click('#btn-eval-console') | 326 |
| 31 | Verify log count 1 | r.check("log-count-1-again", #console-log-count == "1") | none |
| 32 | Click tab #tab-network | d.click('#tab-network') | 329 |
| 33 | Verify visible network count still 3 | r.check("net-visible-3-again", #network-visible-count == "3") | none |
| 34 | Click #btn-save-devtools-report | d.click('#btn-save-devtools-report') | 330 |
| 35 | Verify devtools toast | r.check("devtools-toast", #devtools-toast-summary contains "DevTools diagnostics: 1 logs, 3 filtered network rows, error 404 checked") | none |

### Test 09, notes sync

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-09-notes-sync.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify initial state | r.check("initial", #notes-total-counter == "2" AND #sync-status-indicator contains "Synchronized") | none |
| 3 | Click #btn-create-new-note | d.click('#btn-create-new-note') | 335 |
| 4 | Verify editor title "Untitled Note" | r.check("untitled", #note-editor-title value == "Untitled Note") | none |
| 5 | Clear and type "Shopping" into #note-editor-title | d.clear_and_type('#note-editor-title', 'Shopping') | 336-337 (clear via $eval, then type) |
| 6 | Type "Milk, Eggs, Bread" into #note-editor-body | d.type_text('#note-editor-body', 'Milk, Eggs, Bread') | 338 |
| 7 | Click #btn-save-note-edit (MUST use rename branch, D7) | d.click('#btn-save-note-edit') | 339 |
| 8 | Verify counter 3 and Shopping listed | r.check("shopping-created", #notes-total-counter == "3" AND #note-item-title-shopping == "Shopping") | none |
| 9 | Click tab #tab-device-a | d.click('#tab-device-a') | 342 |
| 10 | Read body, assert "Milk, Eggs, Bread", then append ", Apples" (D6) | r.check("body-before-append", #note-editor-body value == "Milk, Eggs, Bread"); d.type_text('#note-editor-body', ', Apples') | 343 (type only, no read) |
| 11 | Click #btn-stage-device-a | d.click('#btn-stage-device-a') | 344 |
| 12 | Verify Device A status | r.check("device-a-ready", #device-a-status contains "Draft ready: Laptop") | none |
| 13 | Click tab #tab-device-b | d.click('#tab-device-b') | 347 |
| 14 | Clear and type full Device B body | d.clear_and_type('#note-editor-body', 'Milk, Eggs, Bread, Bananas, Orange Juice') | 348-349 (clear via $eval, then type) |
| 15 | Click #btn-stage-device-b | d.click('#btn-stage-device-b') | 350 |
| 16 | Verify Device B status | r.check("device-b-ready", #device-b-status contains "Draft ready: Phone") | none |
| 17 | Click #btn-trigger-cloud-sync | d.click('#btn-trigger-cloud-sync') | 353 |
| 18 | Verify conflict modal active | r.check("conflict-modal", #conflict-resolution-modal has class "active") | 354 (waitForSelector #conflict-resolution-modal.active) |
| 19 | Verify conflict banner text | r.check("conflict-banner", #conflict-detected-banner contains "Sync conflict detected for note Shopping") | none |
| 20 | Click #btn-resolve-keep-both | d.click('#btn-resolve-keep-both') | 355 |
| 21 | Verify conflict modal closed | r.check("conflict-closed", #conflict-resolution-modal has class "closed") | none |
| 22 | Verify counter 4 | r.check("counter-4", #notes-total-counter == "4") | none |
| 23 | Verify conflict copy present | r.check("conflict-copy-present", #note-item-conflict-copy present in notes list) | none |
| 24 | Click #note-item-conflict-copy | d.click('#note-item-conflict-copy') | 358 |
| 25 | Verify editor title contains "Shopping (Conflict Copy)" | r.check("conflict-title-loaded", #note-editor-title value contains "Shopping (Conflict Copy)") | none |
| 26 | Clear and type "Shopping - Phone Copy" into title | d.clear_and_type('#note-editor-title', 'Shopping - Phone Copy') | 359-360 (clear via $eval, then type) |
| 27 | Click #btn-save-note-edit | d.click('#btn-save-note-edit') | 361 |
| 28 | Verify renamed conflict title | r.check("conflict-renamed", #note-item-title-conflict == "Shopping - Phone Copy") | none |
| 29 | Mistake: click #note-item-archived-draft | d.click('#note-item-archived-draft') | 364 |
| 30 | Click #btn-delete-active-note | d.click('#btn-delete-active-note') | 365 |
| 31 | Verify counter back to 3 | r.check("counter-3", #notes-total-counter == "3") | none |
| 32 | Click #note-item-title-shopping | d.click('#note-item-title-shopping') | 368 |
| 33 | Verify primary body contains "Milk, Eggs, Bread, Apples" (ONLY coverage, D5) | r.check("primary-body", #note-editor-body value contains "Milk, Eggs, Bread, Apples") | none |
| 34 | Click #btn-finalize-sync-report | d.click('#btn-finalize-sync-report') | 369 |
| 35 | Verify sync toast | r.check("sync-toast", #sync-summary-toast contains "Sync completed: 3 notes active, Shopping and Shopping - Phone Copy verified") | none |

### Test 10, IDE debug

| Step | Spec action (short) | Runner call | simulate.mjs line(s) |
| --- | --- | --- | --- |
| 1 | Open fixture test-10-ide-debug.html | open fixture URL in browser | 411 (page.goto in simulateOne) |
| 2 | Verify initial state | r.check("initial", #debug-state-badge == "Inactive" AND #active-file-name == "None") | none |
| 3 | Click #file-item-app-js | d.click('#file-item-app-js') | 374 |
| 4 | Verify file loaded | r.check("file-loaded", #active-file-name == "app.js" AND #code-editor visible) | none |
| 5 | Click #gutter-line-12 | d.click('#gutter-line-12') | 377 |
| 6 | Verify breakpoint class on line 12 | r.check("bp-12-class", #gutter-line-12 has class "has-breakpoint") | none |
| 7 | Verify breakpoint count 1 | r.check("bp-count-1", #breakpoint-count-indicator == "1") | none |
| 8 | Click #btn-start-debugger | d.click('#btn-start-debugger') | 380 |
| 9 | Verify paused and stack shows calculateSum line 12 | r.check("paused-12", #debug-state-badge == "Paused" AND #call-stack-list contains "calculateSum (line 12)") | none |
| 10 | Click #btn-step-over (1st) | d.click('#btn-step-over') | 383 |
| 11 | Verify paused line 13 | r.check("paused-13", #current-paused-line == "Line 13") | none |
| 12 | Click #btn-step-over (2nd) | d.click('#btn-step-over') | 384 |
| 13 | Verify paused line 14 | r.check("paused-14", #current-paused-line == "Line 14") | none |
| 14 | Verify watch total 120 | r.check("watch-120", #watch-val-total == "120") | none |
| 15 | SKIPPED, fixture gap (D1): click #input-edit-watch-total | DO NOT DRIVE. No runner call. | none (simulator also skips, lines 387-390 go to #btn-open-edit-watch) |
| 16 | Click #btn-open-edit-watch | d.click('#btn-open-edit-watch') | 387 |
| 17 | Verify edit watch modal active | r.check("watch-modal", #edit-watch-modal has class "active") | 388 (waitForSelector #edit-watch-modal.active) |
| 18 | Clear and type "250" into #input-watch-override-value | d.clear_and_type('#input-watch-override-value', '250') | 389 (type only; no clear in simulator, field starts empty) |
| 19 | Click #btn-confirm-watch-override | d.click('#btn-confirm-watch-override') | 390 |
| 20 | Verify watch total 250 | r.check("watch-250", #watch-val-total == "250") | none |
| 21 | Click #gutter-line-16 | d.click('#gutter-line-16') | 393 |
| 22 | Verify breakpoint class on line 16 | r.check("bp-16-class", #gutter-line-16 has class "has-breakpoint") | none |
| 23 | Verify breakpoint count 2 | r.check("bp-count-2", #breakpoint-count-indicator == "2") | none |
| 24 | Click #btn-continue-debugger | d.click('#btn-continue-debugger') | 394 |
| 25 | Verify paused line 16 | r.check("paused-16", #current-paused-line == "Line 16") | none |
| 26 | Verify stack shows renderSummary line 16 | r.check("stack-16", #call-stack-list contains "renderSummary (line 16)") | none |
| 27 | Verify grand total watch 250 | r.check("grand-250", #watch-val-grand-total == "250") | none |
| 28 | Click #btn-stop-debugger | d.click('#btn-stop-debugger') | 397 |
| 29 | Verify debug state Stopped | r.check("stopped", #debug-state-badge == "Stopped") | none |
| 30 | Verify paused line None | r.check("paused-none", #current-paused-line == "None") | none |
| 31 | Click #btn-save-debug-session | d.click('#btn-save-debug-session') | 400 |
| 32 | Verify debug toast | r.check("debug-toast", #debug-toast-summary contains "Debug session complete: watched total=250, breakpoints=2, final line 16") | none |

## 2. Modal-wait inventory

Every modal, panel, pane, drawer, and sidebar in the suite. "Open proof" is the exact selector and condition the runner waits on or checks. "Opened by" is the spec step that opens it. Waits in simulate.mjs are noted where they exist.

| Modal / panel | Test | Open proof (exact selector and condition) | Opened by spec step | Simulate wait line |
| --- | --- | --- | --- | --- |
| Session modal | 01 | #session-modal has class "open" | 01 step 3 (click #btn-new-session) | 38 waitForSelector #session-modal.open |
| Rename window modal | 01 | #rename-window-modal has class "open" | 01 step 18 (click #btn-rename-window) | 52 waitForSelector #rename-window-modal.open |
| Session overview | 01 | #session-overview style display == "block" (NOT mere presence, see M3) | 01 step 29 (click #btn-detach-session) | 68 waitForSelector #session-overview (presence only, weak) |
| Alert banner (not a modal, listed for completeness) | 01 | #alert-banner has class "active", text contains "Pane 2 closed" | 01 step 25 (click #btn-kill-pane) | none |
| Wi-Fi auth modal | 02 | #wifi-auth-modal has class "active" | 02 step 5 (click #network-row-homefiber) | 81 waitForSelector #wifi-auth-modal.active |
| Known networks panel | 02 | #known-networks-panel style display == "block" | 02 step 10 (click #btn-manage-known-networks) | none |
| Bluetooth panel | 02 | #bluetooth-panel has class "active" | 02 step 14 (click #nav-tab-bluetooth) | none |
| Wi-Fi panel | 02 | #wifi-panel has class "active" | 02 step 26 (click #nav-tab-wifi) | none |
| Network properties panel | 02 | #network-properties-panel has class "active" | 02 step 27 (click #btn-network-properties) | 101 waitForSelector #network-properties-panel.active |
| Status panel | 02 | #status-panel has class "active" | 02 step 32 (click #nav-tab-status) | none |
| Crop controls panel | 03 | #crop-controls has class "active" | 03 step 7 (click #tool-tab-crop) | none |
| Filters panel | 03 | #filters-panel has class "active" | 03 step 13 (click #tool-tab-filters) | none |
| Adjust panel | 03 | #adjust-panel has class "active" | 03 step 17 (click #tool-tab-adjust) | none |
| Transform panel | 03 | #transform-panel has class "active" | 03 step 23 (click #tool-tab-transform) | none |
| Export modal | 03 | #export-modal has class "active" | 03 step 27 (click #btn-open-export) | 135 waitForSelector #export-modal.active |
| Compose pane | 04 | #compose-pane has class "open" (close proof: has class "hidden") | 04 step 3 (click #btn-compose-mail); reopened step 22 (click #draft-entry-q4); closed steps 19 and 30 | 143, 163 waitForSelector #compose-pane.open |
| CC group | 04 | #cc-group visible (style display flex) | 04 step 6 (click #btn-add-cc) | none |
| Attachment picker modal | 04 | #attachment-picker-modal has class "active" | 04 step 11 and step 26 (click #btn-open-attachment-picker) | 152, 170 waitForSelector #attachment-picker-modal.active |
| Chart modal | 05 | #chart-modal has class "active" | 05 step 26 (click #btn-insert-chart-modal) | 211 waitForSelector #chart-modal.active |
| Chart title controls | 05 | #chart-title-controls style display == "block" | 05 step 29 (click #btn-render-chart); shown by the render handler, fixture line 281 | none |
| Screenshare modal | 06 | #screenshare-modal has class "active" | 06 step 16 (click #btn-share-screen) | 241 waitForSelector #screenshare-modal.active |
| Screen share banner | 06 | #screen-share-banner visible (class "hidden" removed) | 06 step 19 (click #btn-confirm-screenshare); hidden again step 21 | none |
| Chat sidebar | 06 | #chat-sidebar has class "open" | 06 step 25 (click #btn-open-chat) | none |
| Rejoin prompt panel | 06 | #rejoin-prompt-panel style display == "flex" | 06 step 30 (click #btn-leave-meeting) | none |
| Bulk rename modal | 07 | #bulk-rename-modal has class "active" | 07 step 9 (click #btn-open-bulk-rename) | 272 waitForSelector #bulk-rename-modal.active |
| Move modal | 07 | #move-modal has class "active" | 07 step 18 (click #btn-open-move-dialog) | 281 waitForSelector #move-modal.active |
| New folder modal | 07 | #new-folder-modal has class "active" | 07 step 30 (click #btn-new-folder) | 295 waitForSelector #new-folder-modal.active |
| Trash view | 07 | #view-trash style display == "block" (via #nav-folder-trash) | 07 step 25 (click #nav-folder-trash) | none |
| Root view | 07 | #view-root style display == "block" (via #nav-folder-root) | 07 step 29 (click #nav-folder-root) | none |
| DevTools panel | 08 | #devtools-panel has class "expanded" (initial state: class "collapsed") | 08 step 3 (click #devtools-toggle-btn) | none |
| Console view | 08 | #view-console has class "active" | 08 step 5 and step 25 (click #tab-console) | none |
| Network view | 08 | #view-network has class "active" | 08 step 11 and step 32 (click #tab-network) | none |
| Request detail pane | 08 | #request-detail-pane has class "open" (close proof: has class "closed") | 08 step 18 (click #row-req-api-checkout); closed step 23 (click #btn-close-detail) | none |
| Detail response view | 08 | #detail-response-body style display == "block" (via #tab-detail-response) | 08 step 21 (click #tab-detail-response) | none |
| Conflict resolution modal | 09 | #conflict-resolution-modal has class "active" (close proof after resolve: has class "closed") | 09 step 17 (click #btn-trigger-cloud-sync); closed step 20 (click #btn-resolve-keep-both) | 354 waitForSelector #conflict-resolution-modal.active |
| Edit watch modal | 10 | #edit-watch-modal has class "active" | 10 step 16 (click #btn-open-edit-watch) | 388 waitForSelector #edit-watch-modal.active |

## 3. Fixture-fact notes

Each fact below was verified by reading or grepping the cited fixture file. File paths are relative to tests/realistic/agy-y2/fixtures/.

### Test-01 pane structure

- Only the active pane's content div gets id `pane-active-output`. Fixture test-01-tmux-session.html lines 205-206: `if (idx === win.activePaneIndex) { content.id = 'pane-active-output'; }`. Every pane first gets id `pane-content-N` (line 204), and the active one is overwritten to `pane-active-output`. The pane wrapper itself gets id `pane-N` (line 196). Consequence: spec step 15 must read #pane-active-output, not #pane-content-2, and after switching windows the id moves to the new active pane.
- Input #pane-terminal-input and button #btn-send-command exist per pane. Fixture lines 215 and 219: each rendered pane creates its own input (line 215, `input.id = 'pane-terminal-input'`) and its own Run button (line 219, `sendBtn.id = 'btn-send-command'`). Duplicate ids across panes exist in the DOM; the driver must target the one in the active pane.
- Uptime output text is pushed by the send handler. Fixture lines 225-226: `if (cmd === 'uptime') { p.output.push(' 10:42:00 up 4 days, 2 users, load average: 0.18, 0.22, 0.15'); }`.
- Kill alert text. Fixture line 385: `el.alertBanner.textContent = 'Pane ' + (win.panes.length + 1) + ' closed';`, so after killing pane 2 the text is "Pane 2 closed" (spec step 26).
- Detach shows the overview. Fixture lines 402-408: the #btn-detach-session handler sets `el.sessionOverview.style.display = 'block'` (line 406). The overview element exists in the DOM from page load (line 81), so a presence-only wait proves nothing (see M3).
- Session windows text. Fixture lines 263-264: renderSessionList builds `<div id="session-windows-' + sess.name + '">` with text `sess.windows.length + ' windows'`, so spec step 31 reads #session-windows-deploy == "2 windows".

### Test-07 selected-files-count resets

- Line 249 sits in the #btn-apply-bulk-rename handler (handler starts line 233). After renaming, it unchecks all boxes, clears state.selected, and sets #selected-files-count to '0' (lines 247-249).
- Line 270 sits in the #btn-confirm-move handler (handler starts line 259). After moving, it unchecks all boxes, clears state.selected, and sets #selected-files-count to '0' (lines 268-270), and updates #folder-count-archive (line 271).
- The live counter itself is driven by the checkbox onchange handler, fixture line 222: `document.getElementById('selected-files-count').textContent = String(state.selected.size);` (handler lines 218-224). Consequence: after bulk rename (step 12) and after move (step 21) the selected count is back to 0, which is why steps 15-17 must re-select img1-3 before the move, and why step 8 is the only moment the count reads 5.
- Restore handler. Fixture lines 289-295: #btn-restore-file-img4 removes the trash row, sets #trash-counter to the remaining trash length, and removes class "hidden" from #file-row-img4 (line 294). The trash row itself is built by the delete handler (lines 285-287).

### Test-09 save handler rename rule

- Fixture test-09-notes-sync.html lines 176-186, the #btn-save-note-edit handler: it writes title and body from the editor into the active note (lines 179-180), then `if (active.title === 'Shopping' && notesState.activeId !== 'shopping')` (line 181) it deletes notes[activeId], sets active.id to 'shopping', stores the note under key 'shopping', and sets activeId to 'shopping' (lines 183-186). So the rename branch fires exactly when the title is 'Shopping' and the active key is not already 'shopping'.
- Step 7 consequence: the new note is created with a generated key `note_<timestamp>` (line 168), so saving it with title 'Shopping' MUST take the rename branch and create the 'shopping' key. That is the intended path (D7).
- Forbidden path: never save with title 'Shopping' while the archived note is active. If the active note were the archived draft and the title were 'Shopping', the handler would delete the archived key and the archived note would vanish without any click on Delete. That is the Y7 doubt 2 bypass, closed for the live run by spec step 33 (body check) and by the rule itself.
- Conflict resolve handler. Fixture lines 237-252: #btn-resolve-keep-both removes 'active', adds 'closed' (lines 238-239), overwrites notes['shopping'] with the Device A buffer (lines 241-245), and creates notes['shopping_conflict'] with title 'Shopping (Conflict Copy)' and the Device B buffer (lines 247-251).
- List id mapping. Fixture line 142 (renderList): `div.id = 'note-item-' + (k === 'shopping_conflict' ? 'conflict-copy' : (k === 'archived' ? 'archived-draft' : k));`, so the archived key renders as #note-item-archived-draft. Title id mapping is line 147: shopping renders as #note-item-title-shopping, shopping_conflict as #note-item-title-conflict.
- Delete handler. Fixture lines 255-266: #btn-delete-active-note deletes notes[activeId] and re-renders, so deleting while the archived draft is active removes that key and drops the counter.
- Device staging. Fixture lines 220-228: #btn-stage-device-a buffers the current body text and sets #device-a-status to 'Draft ready: Laptop'; #btn-stage-device-b does the same for Device B with 'Draft ready: Phone'. The tab clicks (lines 200-218) only switch which stage button and status are shown, they do not change the editor body, so the body text present at step 10 is the step 6 text.

### Test-05 chart title controls

- #chart-title-controls is display:none. Fixture test-05-spreadsheet-chart.html line 136: `<div id="chart-title-controls" style="display: none;">`. The input #input-chart-title (line 139) and #btn-apply-chart-title (line 140) live inside it.
- The handler that shows it is the #btn-render-chart handler, fixture line 278. Line 281: `chartTitleControls.style.display = 'block';` (with chartModal closed line 280 and renderChartSvg called line 283). Consequence: spec step 31 (click #input-chart-title) is only possible after step 29 (click #btn-render-chart). A click before render would hit a hidden input.
- Chart modal open handler is fixture line 251: #btn-insert-chart-modal adds class 'active' to #chart-modal.
- Note: the fixture has no onchange handler for #select-chart-type (grep finds no onchange or addEventListener in this fixture, and the select appears only at line 152). The selected chart type value is never read by any handler. See mismatch M14.

### Test-10 edit watch input

- #input-edit-watch-total is display:none. Fixture test-10-ide-debug.html line 114: `<input type="text" id="input-edit-watch-total" style="display: none;">`.
- Confirmation no handler unhides it or listens to it: grep for `input-edit-watch-total` across the fixture returns only line 114 (the element itself). No other line references that id. The only nearby ids are #btn-open-edit-watch (line 66, handler lines 219-221, opens #edit-watch-modal) and #input-watch-override-value (line 129 area, read by the confirm handler line 228). The confirm handler (lines 227-232) reads #input-watch-override-value, writes #watch-val-total, and closes the modal. It never touches #input-edit-watch-total.
- Consequence: spec step 15 cannot be driven in Zen or in the simulator. It is skipped (D1). The live path to change the watch value is steps 16-19 via the modal and #input-watch-override-value.

### Test-08 row handler

- The handler is on the tr itself. Fixture test-08-devtools.html line 273: `document.getElementById('row-req-api-checkout').onclick = () => {`, and lines 274-275 remove class 'closed' and add class 'open' on #request-detail-pane. The element is a table row: fixture line 140 `<tr id="row-req-api-checkout" class="net-row" data-url="/api/v1/checkout">`.
- Consequence: clicking any td inside that row bubbles to the tr handler, so the runner may click the row text or any cell in the row. Clicking must land inside the row bounds, not on the row id text alone if the row is narrow.
- Detail close handler is fixture lines 278-281: #btn-close-detail removes 'open' and adds 'closed'.

## 4. check.mjs assertion inventory

One list per test. Every check() call in verifyTest, with its selector and expected value, in check.mjs order. Line numbers are check.mjs lines. Values read but never asserted are listed at the end of each test as READ-NOT-ASSERTED. This inventory is what the parent diffs the Python ported verify against.

### Test 01 (check.mjs lines 43-66)

Reads: #active-session-name (43), #status-indicator (44), #window-count (45), #pane-count (46), #window-tab-0 (47), #window-tab-1 (48), #saved-status-message text (49) and class visible (50), .pane-content joined text as terminalOutput (51).

1. Line 59: #active-session-name == "deploy"
2. Line 60: #status-indicator contains "deploy: Attached"
3. Line 61: #window-count == "2"
4. Line 62: #pane-count == "2"
5. Line 63: #window-tab-0 contains "0:bash"
6. Line 64: #window-tab-1 contains "1:worker-logs"
7. Line 65: #saved-status-message has class "visible"
8. Line 66: #saved-status-message contains "Session deploy saved with 2 windows"
- READ-NOT-ASSERTED: terminalOutput (line 51, all .pane-content text joined). Uptime is covered only by spec step 15 (D2).

### Test 02 (check.mjs lines 69-97)

Reads: #wifi-toggle-status (69), #connected-network-name (70), #wifi-connection-badge (71), #item-cafefree element presence (72), #bt-toggle-status (73), #paired-item-mx-master (74), #summary-wifi-ssid (75), #summary-wifi-metered (76), #summary-bt-device (77), #settings-status-toast text and class active (78).

1. Line 87: #wifi-toggle-status == "Enabled"
2. Line 88: #connected-network-name == "HomeFiber-5G"
3. Line 89: #wifi-connection-badge == "Connected"
4. Line 90: #item-cafefree absent from DOM
5. Line 91: #bt-toggle-status == "Enabled"
6. Line 92: #paired-item-mx-master exists AND its text contains "MX Master 3S"
7. Line 93: #summary-wifi-ssid == "HomeFiber-5G"
8. Line 94: #summary-wifi-metered == "Yes"
9. Line 95: #summary-bt-device == "MX Master 3S"
10. Line 96: #settings-status-toast has class "active"
11. Line 97: #settings-status-toast contains "Network settings applied successfully"

### Test 03 (check.mjs lines 100-129)

Reads: #current-filename (100), #dim-width (101), #dim-height (102), #active-crop-ratio (103), #active-filter-name (104), #brightness-display (105), #rotation-angle (106), #export-status-banner text and class active (107), #dialog-format-display (110), #dialog-dimensions-display (111).

1. Line 119: #current-filename == "sunset.jpg"
2. Line 120: #active-crop-ratio == "4:3"
3. Line 121: #active-filter-name == "Vivid"
4. Line 122: #brightness-display == "0"
5. Line 123: #rotation-angle == "90 deg"
6. Line 124: #dim-width == "750"
7. Line 125: #dim-height == "1000"
8. Line 126: #dialog-format-display == "PNG"
9. Line 127: #dialog-dimensions-display contains "750 x 1000"
10. Line 128: #export-status-banner has class "active"
11. Line 129: #export-status-banner contains "Image exported: sunset.png (750x1000, PNG)"

### Test 04 (check.mjs lines 132-150)

Reads: #sent-folder-counter (132), #drafts-folder-counter (133), #sent-row-1 element and computed display (134-135), #toast-alert text and class visible (136).

1. Line 144: #sent-folder-counter == "13"
2. Line 145: #drafts-folder-counter == "0"
3. Line 146: #sent-row-1 exists AND computed display != "none"
4. Line 147: #sent-row-1 text contains "team@example.com"
5. Line 148: #sent-row-1 text contains "Q4 report"
6. Line 149: #toast-alert has class "visible"
7. Line 150: #toast-alert contains "Email sent to team@example.com with attachment report.pdf"

### Test 05 (check.mjs lines 153-186)

Reads: #cell-input-a1 value (153), #cell-input-b1 value (154), #cell-input-a2 value (155), #cell-input-b2 value (156), #cell-input-a3 value (157), #cell-input-b3 value (158), #cell-input-a4 value (159), #cell-input-b4 value (160), #cell-value-b5 text (161), #cell-value-b6 text (162), #sales-bar-svg presence (163), #chart-title-text (164), #sheet-status-toast text and class active (165).

1. Line 175: #cell-input-a1 == "Month"
2. Line 176: #cell-input-b1 == "Sales"
3. Line 177: #cell-input-a2 == "Jan" AND #cell-input-b2 == "1200" (one combined check)
4. Line 178: #cell-input-a3 == "Feb" AND #cell-input-b3 == "1500" (one combined check)
5. Line 179: #cell-input-a4 == "Mar"
6. Line 180: #cell-input-b4 == "1800"
7. Line 181: #cell-value-b5 == "4500"
8. Line 182: #cell-value-b6 == "1500.00"
9. Line 183: #sales-bar-svg exists
10. Line 184: #chart-title-text == "Q1 Regional Sales"
11. Line 185: #sheet-status-toast has class "active"
12. Line 186: #sheet-status-toast contains "Sheet saved: Total=4500, Average=1500.00, Chart=Q1 Regional Sales"

### Test 06 (check.mjs lines 188-213)

Reads: #room-name-display (188), #participant-count (189), #call-status-badge (190), #mic-status-indicator (191), #cam-status-indicator (192), #hand-raise-indicator (193), #chat-message-list text (194), #call-summary-toast text and class active (195).

1. Line 205: #room-name-display == "Sprint Planning"
2. Line 206: #participant-count == "4"
3. Line 207: #call-status-badge == "Connected"
4. Line 208: #mic-status-indicator == "Unmuted"
5. Line 209: #cam-status-indicator == "Camera On"
6. Line 210: #hand-raise-indicator == "Hand Raised"
7. Line 211: #chat-message-list contains "Ready for updates"
8. Line 212: #call-summary-toast has class "active"
9. Line 213: #call-summary-toast contains "Meeting Sprint Planning: 4 participants, audio active, video active"

### Test 07 (check.mjs lines 216-240)

Reads: #selected-files-count (216), #trash-counter (217), #folder-count-archive (218), #file-name-img1 (219), #file-name-img5 (220), #file-row-img4 element and hidden class (221-222), #folder-item-processed presence (223), #inventory-summary-toast text and class active (224).

1. Line 233: #file-name-img1 == "photo-2026-01.jpg"
2. Line 234: #file-name-img5 == "photo-2026-05.jpg"
3. Line 235: #folder-count-archive contains "3 files"
4. Line 236: #trash-counter == "0"
5. Line 237: #file-row-img4 visible (does NOT have class "hidden")
6. Line 238: #folder-item-processed exists
7. Line 239: #inventory-summary-toast has class "active"
8. Line 240: #inventory-summary-toast contains "Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created"
- READ-NOT-ASSERTED: selectedCount (line 216, #selected-files-count). Selected count is covered only by spec step 8 (D3).

### Test 08 (check.mjs lines 243-267)

Reads: #devtools-panel element and class expanded (243-244), #console-log-count (245), #network-visible-count (246), #console-output-log text (247), #row-req-api-checkout element and hidden class (248-249), #row-req-styles element and hidden class (250-251), #devtools-toast-summary text and class active (252).

1. Line 260: #devtools-panel has class "expanded"
2. Line 261: #console-log-count == "1"
3. Line 262: #network-visible-count == "3"
4. Line 263: #console-output-log contains "ready"
5. Line 264: #row-req-api-checkout visible (does NOT have class "hidden")
6. Line 265: #row-req-styles has class "hidden"
7. Line 266: #devtools-toast-summary has class "active"
8. Line 267: #devtools-toast-summary contains "DevTools diagnostics: 1 logs, 3 filtered network rows, error 404 checked"

### Test 09 (check.mjs lines 270-287)

Reads: #notes-total-counter (270), #note-item-title-shopping (271), #note-item-title-conflict (272), #note-item-archived-draft element presence (273), #sync-summary-toast text and class active (274).

1. Line 282: #notes-total-counter == "3"
2. Line 283: #note-item-title-shopping == "Shopping"
3. Line 284: #note-item-title-conflict == "Shopping - Phone Copy"
4. Line 285: #note-item-archived-draft absent from DOM
5. Line 286: #sync-summary-toast has class "active"
6. Line 287: #sync-summary-toast contains "Sync completed: 3 notes active, Shopping and Shopping - Phone Copy verified"
- Note: no body value is read or asserted anywhere in test-09 verifyTest. The primary note body "Milk, Eggs, Bread, Apples" is covered only by spec step 33 (D5).

### Test 10 (check.mjs lines 290-313)

Reads: #active-file-name (290), #breakpoint-count-indicator (291), #debug-state-badge (292), #watch-val-total (293), #watch-val-grand-total (294), #call-stack-list text (295), #debug-toast-summary text and class active (296).

1. Line 306: #active-file-name == "app.js"
2. Line 307: #breakpoint-count-indicator == "2"
3. Line 308: #debug-state-badge == "Stopped"
4. Line 309: #watch-val-total == "250"
5. Line 310: #watch-val-grand-total == "250"
6. Line 311: #call-stack-list contains "renderSummary (line 16)"
7. Line 312: #debug-toast-summary has class "active"
8. Line 313: #debug-toast-summary contains "Debug session complete: watched total=250, breakpoints=2, final line 16"

## 5. Spec / simulate / check mismatches found

- M1. Test-02 apply click has no spec step. Spec steps end at 35 (verify summary BT device). simulate.mjs line 107 clicks #btn-apply-network-settings, and check.mjs lines 96-97 assert the apply toast, which only appears via that click (fixture lines 364-368). The live runner must click Apply after step 35 or the final verify fails. Encoded as the unnumbered required action in the test-02 table (D8).
- M2. simulate.mjs asserts nothing mid-run in any test. All spec verify steps therefore show "none" in the simulate column. The simulator only drives actions (click, type, select, waitForSelector) and calls verifyTest once at the end. The runner's r.check rows have no simulator counterpart by design. Do not treat "none" as a missing simulator step for action rows; for verify rows it is expected.
- M3. Test-01 simulate line 68 waits for #session-overview by presence only. The element exists in the DOM from page load (fixture line 81), so that wait always passes immediately. The real open proof is style display == "block", set by the detach handler (fixture line 406). The runner must check display, not presence.
- M4. Test-10 spec step 15 has no simulator line on purpose. The input is display:none with no handler (section 3). Skipped per D1, never counted as a driven step.
- M5. Test-03 spec step 31 expects "750 x 1000 px" but check.mjs line 127 only asserts contains "750 x 1000" (no "px"). Compatible, not contradictory, but the checker is looser than the spec. Separately, the fixture static default for #dialog-dimensions-display already reads "750 x 1000 px" (fixture line 134), and the value is refreshed from live width and height when the modal opens (fixture line 279), so step 31 alone is weak proof; step 26 (dims 750 and 1000) carries the real proof.
- M6. Test-09 spec step 10 says append ", Apples" but does not say to read the body first. The simulator (line 343) just types, relying on the cursor being at the end. The live runner reads first and asserts "Milk, Eggs, Bread" (D6), because a cursor left mid-text would corrupt the append.
- M7. Test-07 final check cannot catch a skipped delete plus restore (Y7 doubt 1). Skipping spec steps 23-29 still passes all 8 final checks (lines 233-240). The step 24 and step 28 intermediate checks (D4) are the only closers. The Python ported verify must include them as mid-run checks, not just end-state checks.
- M8. Test-09 final check never asserts any note body. A run that stages the wrong Device A buffer but still resolves keep-both would pass all 6 final checks if the titles and counter are right, except the step 33 body check catches it. Same pattern as M7: the Python ported verify must include the step 33 mid-run check.
- M9. Two read-but-never-asserted values in check.mjs: test-01 terminalOutput (line 51) and test-07 selectedCount (line 216). Both are covered only by intermediate spec checks (steps 15 and 8). The Python port must NOT silently drop them; it must assert them mid-run at those steps, or record them as explicitly uncovered.
- M10. Test-04 spec step 23 verifies the reopened draft subject value "Q4 report", but the simulator (lines 161-163) only clicks the draft and waits for #compose-pane.open. It never reads #input-mail-subject. The runner must add the subject read; the simulator gives no precedent for it.
- M11. Test-02 spec has no step verifying the apply toast text. The toast is asserted only in check.mjs lines 96-97. The runner check for it is attached to the unnumbered apply action (D8, M1).
- M12. Test-05 spec step 31 clicks #input-chart-title, but that input is hidden until the render handler shows its container (fixture line 281). The simulator works only because render (line 213) precedes the click (lines 216-218). The runner must wait for #chart-title-controls display block after step 29 before attempting step 31.
- M13. Several final checks omit states that only intermediate steps cover. Test-08 final check does not assert the detail pane open state, the 404 status code, or the response body (spec steps 19-22 only). Test-06 final check does not assert the screenshare banner, chat sidebar, or rejoin panel (spec steps 20, 22, 26, 31 only). Test-02 final check does not assert the metered indicator or the known-networks panel (spec steps 11, 30 only). The Python ported verify must preserve these as mid-run checks; an end-state-only port would silently drop them.
- M14. Test-05 spec steps 28 and 29 select "Bar" and render, but no fixture code reads the #select-chart-type value (grep finds the select only at fixture line 152, no onchange handler), and no check asserts the chart type. Selecting Bar is therefore unasserted anywhere. The render handler (fixture lines 278-284) always renders the bar SVG regardless of the select value. The runner still performs the select per spec, but the port should note the chart-type selection has no observable assertion.
- M15. Test-09 step 25 (editor title contains "Shopping (Conflict Copy)") has no simulator read. The simulator (line 358) only clicks #note-item-conflict-copy and then clears the title (line 359). The runner must read the title before clearing, or the load of the conflict copy is unverified.
- M16. Y7 surviving doubts status, carried forward, not re-decided here. Doubt 1 (test-07 skip hole) is closed by D4 intermediate checks, not by a fixture change. Doubt 2 (test-09 rename-branch bypass) is closed by D7 plus the step 33 body check, not by a fixture change. Doubt 3 (test-07 Root count depends on the moved set excluding img4) is a live-run warning: the move set is exactly img1-3 (spec steps 15-17), moving img4 instead would change the Root count and break the step 35 toast. Doubt 4 (simulate --all aborts on first crash, cannot catch spec/checker drift) is a method gap: this file is the drift catch, it maps every spec step against simulate and check line by line.
