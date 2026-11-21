# test-02-network-settings.md

## Test ID
test-02-network-settings

## Topic
System network and device settings: Wi-Fi connectivity, known networks management, Bluetooth device pairing, connection metering, and configuration verification.

## Context
A systems administrator needs to configure wireless networking and peripherals on a corporate workstation.
The workstation runs a local browser-based network configuration interface (fixtures/test-02-network-settings.html).
The user must enable the Wi-Fi adapter, authenticate and connect to "HomeFiber-5G", remove the deprecated "CafeFree"
network from known networks, pair a peripheral mouse ("MX Master 3S"), test Bluetooth adapter toggling while verifying
device persistence, configure the Wi-Fi connection as metered, and apply network settings from the status panel.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Enable Wi-Fi, connect to "HomeFiber-5G", forget "CafeFree", pair "MX Master 3S", toggle Bluetooth off and on,
set Wi-Fi to metered, verify configuration in status panel, and apply settings.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-02-network-settings.html in the browser.
2. Verify element #wifi-toggle-status text is "Disabled" and #connected-network-name text is "Not Connected".
3. Click button #toggle-wifi to enable the Wi-Fi adapter.
4. Verify element #wifi-toggle-status text is "Enabled" and element #wifi-content is displayed.
5. Click list item #network-row-homefiber to initiate connection to "HomeFiber-5G".
6. Verify modal #wifi-auth-modal has class "active".
7. Click input #input-wifi-password and type "HomeKey2026".
8. Click button #btn-connect-wifi to authenticate and connect.
9. Verify element #connected-network-name text is "HomeFiber-5G" and #wifi-connection-badge text is "Connected".
10. Click button #btn-manage-known-networks to expand the known networks list.
11. Verify element #known-networks-panel is visible.
12. Click button #btn-forget-cafefree to remove network "CafeFree".
13. Verify element #item-cafefree is removed from the DOM.
14. Click tab #nav-tab-bluetooth to switch to Bluetooth settings panel.
15. Verify element #bluetooth-panel has class "active".
16. Verify element #bt-toggle-status text is "Enabled".
17. Click button #btn-scan-bt-devices to scan for nearby discoverable peripherals.
18. Verify element #available-bt-list is visible and contains element #bt-device-mx-master.
19. Click button #btn-pair-mx-master to pair with "MX Master 3S".
20. Verify element #paired-bt-list contains element #paired-item-mx-master with status badge "Paired".
21. Click button #toggle-bluetooth to disable Bluetooth.
22. Verify element #bt-toggle-status text is "Disabled".
23. Click button #toggle-bluetooth again to re-enable Bluetooth.
24. Verify element #bt-toggle-status text is "Enabled".
25. Verify element #paired-item-mx-master remains present in #paired-bt-list.
26. Click tab #nav-tab-wifi to return to the Wi-Fi settings panel.
27. Click button #btn-network-properties to open connection properties for HomeFiber-5G.
28. Verify modal #network-properties-panel has class "active".
29. Click checkbox #toggle-metered-connection to set connection as metered.
30. Verify element #metered-status-indicator text is "Metered".
31. Click button #btn-save-wifi-properties to save the metered setting.
32. Click tab #nav-tab-status to view the status overview panel.
33. Verify element #summary-wifi-ssid text is "HomeFiber-5G".
34. Verify element #summary-wifi-metered text is "Yes".
35. Verify element #summary-bt-device text is "MX Master 3S".

## Pass/fail criteria
- Pass: Wi-Fi connected to "HomeFiber-5G", "CafeFree" removed, "MX Master 3S" paired and retained across Bluetooth toggling, Wi-Fi marked metered, and status overview accurately reflects all settings.
- Fail: Wi-Fi not connected, "CafeFree" still present, Bluetooth mouse not paired, metered setting not enabled, or status summary incorrect.

## Errors designed to expose
- click miss: Switching between navigation tabs and targeting small modal checkboxes.
- slow think: Delays during modal transitions and device scan operations.
- stale observation: Checking paired device persistence before Bluetooth toggle re-rendering completes.
- wrong diagnosis: Confusing scanning for devices with active pairing.
- fabrication: Asserting metered state without inspecting summary panel text.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-02-network-settings.html --test 02
```
