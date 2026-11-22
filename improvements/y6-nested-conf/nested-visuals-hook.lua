-- Nested optics hook. Adapted from scripts/setup.py _hook_body (repo).
-- Live hook runs visuals.py on hyprland.start when glass is not yet loaded.
-- The live re-apply command must NOT run inside the nest (it targets the live
-- manifest), so the else branch only prints a marker.
--
-- Y6C5-A3/A4 (2026-11-22, Y6r R1/R3): the parse-1 "not ready" marker is EXPECTED
-- on every successful startup. Parse 1 runs before the plugin system exists, so
-- hl.get_loaded_plugins() is empty by the early-return branch; parse 2 runs
-- after STAGE_LATE loads the plugin and calls reload(), so the hook sees
-- count=1 and dofiles optics.lua. The profile IS applied on parse 2. The old
-- claim that the marker proves the profile missing was wrong and is corrected.
-- The runner checks liquid_available(ready=true) after start, but that gate is
-- metadata-only (scripts/indicator.py docstring): it CANNOT prove the profile
-- was applied, because hyprglass status carries no blur, refraction, preset,
-- or layer-namespace fields. The positive proof is the applied marker below,
-- printed AFTER the dofile returns, plus features.layers.enabled == true.
local loaded = type(hl.get_loaded_plugins) == "function" and hl.get_loaded_plugins() or nil
local glass_count, glass_version = 0, nil
if type(loaded) == "table" then
  for _, plugin in ipairs(loaded) do
    if type(plugin) == "table" and plugin.name == "hyprglass" then
      glass_count, glass_version = glass_count + 1, plugin.version
    end
  end
end
if glass_count == 1 and glass_version == "1.1.1-cu.1" then
  dofile("/tmp/y6-nested/conf/optics.lua")
  -- Y6C5-A3: printed AFTER the dofile returns, so a dofile error (a throwing
  -- optics.lua) means no marker. Bare dofile, no pcall: errors must propagate.
  print("Y6-NEST-HOOK: profile applied")
else
  -- EXPECTED on parse 1 of every run (plugin system does not exist yet).
  -- The runner must log this, never fail on it.
  print("Y6-NEST-HOOK: hyprglass not ready (count=" .. tostring(glass_count) .. " version=" .. tostring(glass_version) .. ")")
end
