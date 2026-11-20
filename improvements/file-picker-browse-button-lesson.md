# File picker Browse button lesson

Date: 2026-11-20. Found during a live upload task where a file-archive
upload step was stuck for over an hour.

## 1. Browse buttons that are labels over a hidden file input

Some web apps render the file picker trigger as a styled label over a
hidden `<input type="file">`. The visible button is not the real input.

- Clicking dead center on the button may not register at all. This is a
  UI quirk, not a browser block.
- The working method: move the mouse to hover OFF-CENTER on the button
  until it shows its hover state (the button darkens), THEN click.
  The hover state confirms the pointer is over the clickable area.
- Do not assume the first failed click means the picker is blocked.
  Before trying exotic workarounds, try the hover-off-center-then-click
  method, and verify with a fresh observation whether the picker opened.

## 2. Stop repeating the same failed action

When a step fails the same way repeatedly, rethink and change approach
after 2-3 failures. Do not keep repeating the identical failed action.

- A click that fails twice at the same coordinates is not going to work
  on the third try. Change the approach: different coordinates, hover
  first, keyboard navigation, or a different targeting method.
- Each retry must be a different approach, not the same action again.
- Log every attempt with what changed, so the next attempt does not
  repeat a known failure.

## 3. Proactive blocker reporting

When a step is stuck on the same error for more than 15 minutes, report
it as a blocker immediately to the coordinator or user. Do not wait to
be asked.

- A step that keeps failing is a blocker, not a retryable error, once
  it passes the 15-minute mark.
- The report must name the step, the error, how long it has been stuck,
  and what approaches were already tried.
- Silence while stuck is the worst outcome: it burns time the user
  could have used to unblock it with one manual action or one new idea.

## 4. The file picker is a separate window

On Linux desktops the native file picker is often a separate portal
window, not part of the browser window.

- Keyboard input goes to the focused window. Confirm which window is
  focused before sending keys. Keys sent to the wrong window can trigger
  unrelated actions (for example, typing a path into the browser address
  bar instead of the picker).
- Do not use browser shortcuts inside a file picker: Ctrl+L focuses the
  browser URL bar, Ctrl+T opens a new window in some browsers. Neither
  belongs in a picker interaction.
- After the picker opens, re-observe and confirm the picker window is
  focused before typing a path or pressing Enter.

## 5. Archive contents matter

When an archive is uploaded to a test-management page, check what the
importer expects before uploading.

- An archive containing both input files and answer files may be counted
  as one test per file, doubling the expected test count. If the importer
  expects input files only, repackage the archive to inputs only,
  keeping the file contents byte-for-byte identical.
- Verify the imported test count immediately after upload. If the count
  does not match the expected number, stop and fix the archive before
  configuring points or committing.
- Some systems do not allow deleting the default test set. If the wrong
  set was imported as the default, create the correct set, make it the
  default, then delete the old one, or delete the whole item and start
  clean.
