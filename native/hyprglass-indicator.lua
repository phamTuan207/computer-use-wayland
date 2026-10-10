-- Optional, ABI-specific backdrop material. Load the validated plugin separately.
-- This configuration does not enable glass for ordinary windows or other layers.
if hl.plugin.hyprglass then
  local hg = hl.plugin.hyprglass
  -- preset()/layer() are queued until config commit in the pinned backend.
  -- Direct config values also work through eval without reloading the plugin.
  local material = {
    -- Bend only a narrow curved rim, not the whole interior scene.
    refraction_strength = 1.85,
    refraction_flow = 1.0,
    refraction_spread = 0.0,
    chromatic_aberration = 0.0,
    edge_thickness = 0.24,
    lens_distortion = 0.0,
    -- Preserve backdrop colour: readability belongs to the lettering, not a
    -- dark plate. Soften the live backdrop without tinting it.
    blur_strength = 0.18,
    brightness = 1.0,
    contrast = 1.0,
    saturation = 1.0,
    vibrancy = 0.0,
    vibrancy_darkness = 0.0,
    adaptive_dim = 0.0,
    adaptive_boost = 0.0,
    glass_opacity = 1.0,
    tint_color = 0xffffff00,
    bevel_strength = 0.95,
    bevel_size = 3.0,
    bevel_tint = 0.0,
    bevel_shadow = 0.0,
    bevel_angle = 300.0,
    specular_strength = 0.85,
    fresnel_strength = 0.38,
    noise_strength = 0.0,
  }
  local config = {
    enabled = false, manage_window_blur = false,
    default_preset = "default",
    subsurfaces = { enabled = false },
    layers = { enabled = true, namespaces = "computer-use-indicator",
               preset = "default", mask_mode = "region" },
    dark = material, light = material,
  }
  for key, value in pairs(material) do config[key] = value end
  hg.config(config)
end
