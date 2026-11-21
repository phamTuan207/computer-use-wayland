# test-10-extension-settings.md

## Test ID
test-10-extension-settings

## Topic
Browser extension enable and disable, per-site permissions, options page changes, reset to defaults, and persistence after reload.

## Context
A user configures Clean Page in the local Extension Control Center. They enable and disable the extension, set site-specific permissions, change options, verify those choices after reload, reset all settings to defaults, then reload again to verify the reset persisted. The fixture is tests/realistic/codex-y5/fixtures/test-10-extension-settings.html and uses reserved example.test hostnames.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 270 seconds elapsed
- Maximum allowable latency: 390 seconds elapsed

## Goal
Finish with the default extension enabled, both site permissions set to Ask, both options On, and the saved defaults restored after reload.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-10-extension-settings.html in the browser.
2. Verify #extension-enabled-state text is "Disabled", #site-calendar-permission text is "Ask", #site-drive-permission text is "Ask", #option-notify-state text is "On", #option-auto-update-state text is "On", #options-save-status text is "Not saved", and #extension-persistence-status text is "Not reloaded".
3. Click button #btn-toggle-extension; #extension-enabled-state must become "Enabled".
4. Verify #extension-enabled-state text is "Enabled".
5. Click button #btn-toggle-extension again; #extension-enabled-state must become "Disabled".
6. Verify #extension-enabled-state text is "Disabled".
7. Click button #btn-toggle-extension a third time; #extension-enabled-state must become "Enabled".
8. Click button #btn-open-sites; #site-access-page must become visible.
9. Mistake: select value "Block" in #site-calendar-select; its selected value must be "Block".
10. Click button #btn-save-site-permissions; #site-calendar-permission must become "Block".
11. Verify #site-calendar-permission text is "Block" and #site-drive-permission text is "Ask".
12. Recovery: select value "Allow" in #site-calendar-select; its selected value must be "Allow".
13. Select value "Block" in #site-drive-select; its selected value must be "Block".
14. Click button #btn-save-site-permissions; #site-calendar-permission must become "Allow" and #site-drive-permission must become "Block".
15. Verify #site-calendar-permission text is "Allow" and #site-drive-permission text is "Block".
16. Click button #btn-open-options; #options-page must become visible.
17. Click checkbox #option-notify-toggle to turn notices off; #option-notify-state must become "Off".
18. Click checkbox #option-auto-update-toggle to turn automatic updates off; #option-auto-update-state must become "Off".
19. Click button #btn-save-options; #options-save-status must become "Options saved".
20. Verify #option-notify-state text is "Off", #option-auto-update-state text is "Off", and #options-save-status text is "Options saved".
21. Click button #btn-reload-settings; after reload #extension-persistence-status must become "State restored after reload".
22. Verify #extension-persistence-status text is "State restored after reload", #extension-enabled-state text is "Enabled", #site-calendar-permission text is "Allow", #site-drive-permission text is "Block", #option-notify-state text is "Off", and #option-auto-update-state text is "Off".
23. Click button #btn-open-options; #options-page must become visible.
24. Click button #btn-reset-defaults; #options-save-status must become "Defaults restored".
25. Verify #extension-enabled-state text is "Enabled", #site-calendar-permission text is "Ask", #site-drive-permission text is "Ask", #option-notify-state text is "On", and #option-auto-update-state text is "On".
26. Click button #btn-reload-settings again; after reload #extension-persistence-status must become "State restored after reload".
27. Verify #extension-persistence-status text is "State restored after reload", #extension-enabled-state text is "Enabled", #site-calendar-permission text is "Ask", #site-drive-permission text is "Ask", #option-notify-state text is "On", #option-auto-update-state text is "On", and #options-save-status text is "Defaults restored".

## Pass/fail criteria
- Pass: Extension defaults are restored and survive reload: enabled, both site permissions Ask, notices On, and automatic updates On.
- Fail: Enable or disable has no effect, site permissions do not persist, the options page does not save, reset does not restore defaults, or the reload shows stale values.

## Errors designed to expose
- click miss: The master toggle, site access tab, and options controls use separate page sections.
- slow think: The task requires two reloads with different saved states.
- stale observation: The first reload must show the changed values, while the second must show the reset values.
- wrong diagnosis: Blocking the calendar site is a deliberate mistake that must be corrected to Allow before reset.
- fabrication: The final permission and option values are read from visible DOM summaries after reload.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-10-extension-settings.html --test 10
```
