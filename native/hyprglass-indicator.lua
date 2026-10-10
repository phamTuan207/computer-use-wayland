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
    refraction_strength = 0.35,
    refraction_flow = 0.0,
    chromatic_aberration = 0.0,
    edge_thickness = 0.22,
    lens_distortion = 0.08,
    -- Preserve backdrop colour: readability belongs to the lettering, not a
    -- dark or frosted plate. Explicit values override inherited theme tint.
    blur_strength = 0.0,
    brightness = 1.0,
    contrast = 1.0,
    saturation = 1.0,
    adaptive_dim = 0.0,
    adaptive_boost = 0.0,
    glass_opacity = 1.0,
    tint_color = 0xffffff00,
    bevel_strength = 0.65,
    bevel_size = 2.0,
    bevel_tint = 0.0,
    bevel_angle = 300.0,
    specular_strength = 0.55,
    fresnel_strength = 0.18,
    noise_strength = 0.0,
  })
end
