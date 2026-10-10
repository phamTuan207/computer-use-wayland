-- Optional, ABI-specific backdrop material. Load the validated plugin separately.
-- This configuration does not enable glass for ordinary windows or other layers.
if hl.plugin.hyprglass then
  local hg = hl.plugin.hyprglass
  hg.config({ enabled = false, manage_window_blur = false,
              subsurfaces = { enabled = false },
              layers = { enabled = true, mask_mode = "region" } })
  hg.layer("computer-use-indicator", { preset = "cu-indicator", mask_mode = "region" })
  hg.preset("cu-indicator", {
    inherits = "pomme",
    refraction_strength = 0.85,
    chromatic_aberration = 0.015,
    edge_thickness = 0.35,
    blur_strength = 0.16,
    brightness = 0.45,
    glass_opacity = 0.90,
    tint_color = 0x10182050,
    bevel_strength = 0.35,
    bevel_size = 3.0,
    specular_strength = 0.3,
    noise_strength = 0.01,
  })
end
