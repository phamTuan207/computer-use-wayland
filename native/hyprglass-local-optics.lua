-- Upstream optical formula; transparent material scoped to the indicator.
if hl.plugin.hyprglass then
  local material = {
    refraction_strength = 0.75, refraction_flow = 1.0,
    refraction_spread = 0.15, edge_thickness = 0.12,
    lens_distortion = 0.6, blur_strength = 0.18,
    chromatic_aberration = 0.04, fresnel_strength = 0.20,
    specular_strength = 0.50, bevel_strength = 0.70, bevel_size = 3.0,
    bevel_tint = 0.0, bevel_shadow = 0.0, bevel_angle = 315.0,
    noise_strength = 0.0, glass_opacity = 1.0, tint_color = 0xffffff00,
    brightness = 1.0, contrast = 1.0, saturation = 1.0,
    vibrancy = 0.0, vibrancy_darkness = 0.0,
    adaptive_dim = 0.0, adaptive_boost = 0.0,
  }
  local config = {
    enabled = false, manage_window_blur = false, default_preset = "default",
    subsurfaces = { enabled = false },
    layers = { enabled = true, namespaces = "computer-use-indicator",
      preset = "default", mask_mode = "region" },
    dark = material, light = material,
  }
  for key, value in pairs(material) do config[key] = value end
  hl.plugin.hyprglass.config(config)
end
