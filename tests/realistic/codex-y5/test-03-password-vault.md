# test-03-password-vault.md

## Test ID
test-03-password-vault

## Topic
Password manager vault entry creation, password generation, reveal, copy, edit, delete recovery, and lock/unlock.

## Context
An operator needs to save and update a credential in Vault Desk, check the generated password, copy it to the visible fixture clipboard buffer, recover from deleting the entry, and lock then unlock the vault. The fixture uses synthetic service and account labels only: tests/realistic/codex-y5/fixtures/test-03-password-vault.html.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 240 seconds elapsed
- Maximum allowable latency: 360 seconds elapsed

## Goal
Leave Vault Desk unlocked with one edited entry named Research Vault, username qa-operator, and a masked generated password that was copied.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-03-password-vault.html in the browser.
2. Verify #vault-status text is "Locked", #vault-entry-count text is "0", #entry-title-display text is "None", and #delete-status text is "No deletion".
3. Type "vault-access-key" into #master-key-input; its value must be "vault-access-key".
4. Click button #btn-unlock-vault; #vault-status must become "Unlocked".
5. Verify #vault-message text is "Vault unlocked" and #vault-entry-count text is "0".
6. Click button #btn-add-entry; #entry-editor must become visible.
7. Type "Research Portal" into #entry-title-input; its value must be "Research Portal".
8. Type "research-user" into #entry-username-input; its value must be "research-user".
9. Click button #btn-generate-password; #entry-password-input value must become "Cedar!9-Glass?".
10. Verify #entry-password-input value is exactly "Cedar!9-Glass?".
11. Click button #btn-save-entry; #vault-entry-count must become "1".
12. Verify #entry-title-display text is "Research Portal", #entry-username-display text is "research-user", and #password-mask text is "••••••••••••••".
13. Click button #btn-reveal-password; #password-mask must display "Cedar!9-Glass?".
14. Verify #password-mask text is exactly "Cedar!9-Glass?".
15. Click button #btn-copy-password; #copy-status must become "Password copied".
16. Verify #clipboard-buffer value is "Cedar!9-Glass?" and #copy-status text is "Password copied".
17. Click button #btn-edit-entry; #entry-editor must become visible.
18. Replace #entry-title-input with "Research Vault"; its value must be "Research Vault".
19. Replace #entry-username-input with "qa-operator"; its value must be "qa-operator".
20. Click button #btn-save-entry; #entry-title-display must become "Research Vault".
21. Verify #entry-username-display text is "qa-operator" and #password-mask text is "••••••••••••••".
22. Mistake: click button #btn-delete-entry and remove the required entry; #vault-entry-count must drop to "0".
23. Verify #delete-status text is "Entry deleted by mistake" and #entry-title-display text is "None".
24. Recovery: click button #btn-undo-delete; #vault-entry-count must return to "1".
25. Verify #delete-status text is "Entry restored" and #entry-title-display text is "Research Vault".
26. Click button #btn-lock-vault; #vault-status must become "Locked" and #entry-title-display must become "None".
27. Type "vault-access-key" into #master-key-input; its value must be "vault-access-key".
28. Click button #btn-unlock-vault; #vault-status must become "Unlocked".
29. Verify #vault-status text is "Unlocked", #vault-entry-count text is "1", #entry-title-display text is "Research Vault", #entry-username-display text is "qa-operator", #password-mask text is "••••••••••••••", #copy-status text is "Password copied", and #delete-status text is "Entry restored".

## Pass/fail criteria
- Pass: The vault is unlocked with one entry named Research Vault, username qa-operator, the generated password masked, the copy buffer holding the generated value, and the accidental deletion recovered.
- Fail: The vault remains locked, the edited entry is absent or stale, the password was not generated or copied, or delete recovery fails.

## Errors designed to expose
- click miss: The reveal, copy, edit, delete, and undo controls are near one another.
- slow think: The task moves between the vault header, entry editor, and selected-entry panel.
- stale observation: Locking hides the entry and unlocking must restore it.
- wrong diagnosis: The delete action removes the entry until the explicit undo control is used.
- fabrication: The generated password and copy buffer must match the fixed value exactly.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-03-password-vault.html --test 03
```
