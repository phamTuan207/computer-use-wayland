-- Upstream optical formula; transparent material scoped to the indicator.
if hl.plugin.hyprglass then
  -- plus-sharp (2026-11-18): apple-plus with less blur and more refraction
  -- bottle fix (2026-11-19): blur restored to 0.25 (was 0.0, interior read as transparent);
  -- refraction now uses the cylindrical-bottle profile in the shayxo patch.
  local material = {
    -- Legacy uses a fixed 9 dp depth; keep this key for the optional lens-edge path.
    refraction_strength = 0.55, refraction_flow = 1.0,
    -- Legacy's refraction band is fixed at 14 dp; edge_thickness still sets contour-field reach.
    refraction_spread = 1.0, edge_thickness = 0.05,
    lens_distortion = 0.6, blur_strength = 0.25,
    chromatic_aberration = 0.07, fresnel_strength = 0.10,
    specular_strength = 0.55, bevel_strength = 0.45, bevel_size = 3.0,
    bevel_tint = 0.0, bevel_shadow = 0.0, bevel_angle = 315.0,
    noise_strength = 0.0, glass_opacity = 1.0, tint_color = 0xffffff00,
    brightness = 1.0, contrast = 1.0, saturation = 1.0,
    vibrancy = 0.0, vibrancy_darkness = 0.0,
    adaptive_dim = 0.0, adaptive_boost = 0.0,
  }
  local config = {
    enabled = false, manage_window_blur = false, default_preset = "default",
    subsurfaces = { enabled = false },
    layers = { enabled = true, preset = "default", mask_mode = "region" },
    dark = material, light = material,
  }
  for key, value in pairs(material) do config[key] = value end
  hl.plugin.hyprglass.config(config)
  -- mask_mode "contour": GTK 4.24 owns the surface background effect, so the
  -- indicator cannot set a protocol blur region (a second get_background_effect
  -- is a protocol error that kills the client). Contour traces the pill outline
  -- from the rendered content instead; the liquid pill interior is transparent,
  -- so "alpha" would leave a hollow frame.
  hl.plugin.hyprglass.layer("computer-use-indicator", {
    preset = "default", mask_mode = "contour"
  })
end
