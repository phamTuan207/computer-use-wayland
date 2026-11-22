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
-- Y6C5-A8-INVEST (2026-11-22): the per-instance log file does NOT deliver
-- post-parse-2 prints within the run (ofstream buffering, SIGKILL discards
-- the tail; A8 trial 16:18 2026-11-22 proved the profile applied while the
-- marker never reached either log). The gate therefore cannot grep the log
-- for the applied marker. The hook writes the same marker to a plain file
-- and closes it: a closed file is on disk immediately. Log prints stay as
-- corroboration only. See improvements/worker-click5-y6-a8-invest-log.md.
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
  -- Y6C5-A8-INVEST: same marker, delivered through a file instead of the
  -- buffered log. dofile returned, so optics.lua line 47 already printed
  -- in-process; writing both lines here records the same event. Explicit
  -- close() flushes to disk at once. Path is the nest run dir from the
  -- environment the launcher sets (XDG_RUNTIME_DIR=/tmp/y6-nested/run),
  -- never the live runtime dir. Guard: the run dir must sit under
  -- /tmp/y6-nested/. If it does not, no file is written anywhere, and a
  -- warning print records the refusal. A failed open also prints, it is
  -- never silent: the gate then fails closed on the missing file, and the
  -- log print (if it ever flushes) is the diagnostic.
  -- B2-3 redteam R-R1: the prefix check alone is not enough. A run dir
  -- of /tmp/y6-nested/run/../../../run/user/1000 still matches the
  -- prefix, and io.open follows ".." and symlinks, so the marker would
  -- land in the live dir. Any ".." component is refused outright. The
  -- runner also refuses a symlinked RUN_DIR before mkdir -p, so no
  -- planted symlink can redirect the write. A symlinked PARENT dir
  -- (/tmp/y6-nested itself) is invisible to these string checks; the
  -- runner refuses a symlinked $NEST before launch, which is the only
  -- place that check can live, since Lua has no lstat here.
  local run_dir = os.getenv("XDG_RUNTIME_DIR") or "/tmp/y6-nested/run"
  if not string.match(run_dir, "^/tmp/y6%-nested/") then
    print("Y6-NEST-HOOK: marker file NOT written, XDG_RUNTIME_DIR is not a nest run dir: " .. run_dir)
  elseif string.find(run_dir, "%.%.") then
    print("Y6-NEST-HOOK: marker file NOT written, XDG_RUNTIME_DIR contains a .. component: " .. run_dir)
  else
    local marker_path = run_dir .. "/y6-profile-applied.txt"
    -- Atomic write (redteam race note): write a temp file in the same
    -- dir, close it, then rename over the marker, so a reader never
    -- sees a half-written marker.
    -- B2-3 redteam R2-2: the .tmp name is fixed, so a planted symlink
    -- at that name would be truncated by io.open("w") before the
    -- rename. Remove any pre-existing .tmp first (the runner also
    -- removes it at startup); the window left between this remove and
    -- the open is the hook's own write, with no planted link surviving
    -- the remove.
    local marker_tmp = marker_path .. ".tmp"
    os.remove(marker_tmp)
    local marker_file = io.open(marker_tmp, "w")
    if marker_file then
      marker_file:write("Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour namespace=computer-use-indicator\n")
      marker_file:write("Y6-NEST-HOOK: profile applied\n")
      marker_file:close()
      if not os.rename(marker_tmp, marker_path) then
        print("Y6-NEST-HOOK: marker file rename failed: " .. marker_tmp)
      end
    else
      print("Y6-NEST-HOOK: marker file open failed: " .. marker_tmp)
    end
  end
else
  -- EXPECTED on parse 1 of every run (plugin system does not exist yet).
  -- The runner must log this, never fail on it.
  print("Y6-NEST-HOOK: hyprglass not ready (count=" .. tostring(glass_count) .. " version=" .. tostring(glass_version) .. ")")
end
