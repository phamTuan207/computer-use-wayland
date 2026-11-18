# Shayxo Legacy / Chrome → Hyprglass port design

- Model: gpt-6-luna is the requested worker identity; the runtime does not expose its model identifier, so I cannot verify that identity. No model switch was made.
- Reasoning effort: max was requested; the runtime does not expose the active effort setting, so I cannot verify it.
- Wall-clock start: 2026-11-18 13:15:52 Asia/Ho_Chi_Minh.
- Wall-clock finish: 2026-11-18 13:48:10 Asia/Ho_Chi_Minh.
- CODEX_OK: NOT VERIFIED. No build or launch was run, as requested.
- Scope: read-only investigation; this document is the only intended repository write.

## Decision note: exact-source conflicts

The coordinator resolved the value conflict: implement the task-supplied value set. The table preserves the pinned source’s actual named Chrome values for comparison. The resulting port is the Shayxo Legacy task-value set, not an exact copy of the named Chrome preset.

At the pinned shayxo commit, GlassStyle.Chrome is Legacy, fine blur 0 dp, band 14 dp, depth 9 dp, and bevel 3 dp. It also sets backdropBlur 14 dp, dispersion 0.010, mirror 0.08, white tint alpha 0.11, adaptivity 0.90, legibility 0.90, specular 0.50, Fresnel 0.08, and innerShadow 0.06. The task-supplied list instead says no pre-blur, dispersion 0.07, no mirror, transparent tint, legibility 0.6, specular 0.55, Fresnel 0.10, and innerShadow 0.07. The source-wins instruction makes these source facts authoritative when describing source Chrome.

The actual Chrome values above were checked in the same pinned commit’s GlassStyle.kt because GlassShaderSource.kt contains shader formulas, not the preset constructor. The quoted rest map is a separate shader fragment in GlassRestMap.kt, not text physically present in GlassShaderSource.kt. These companion files are named explicitly below.

## 1. Verification against the pinned source

Sources checked:

- Shayxo GlassShaderSource.kt, commit f5e1fb56f72f7dc4e2af450d89339a9fece13bf0, 889 lines:
  https://github.com/shayann07/liquidglass/blob/f5e1fb56f72f7dc4e2af450d89339a9fece13bf0/liquidglass/src/commonMain/kotlin/com/wexpa/liquidglass/GlassShaderSource.kt
- Hyprglass src/Shaders.hpp, commit 03a57c4451b4abee38feda2ffb725f55ecc0f2fd, 980 lines:
  https://github.com/hyprnux/hyprglass/blob/03a57c4451b4abee38feda2ffb725f55ecc0f2fd/src/Shaders.hpp
- Companion source for the injected legacy rest map:
  https://github.com/shayann07/liquidglass/blob/f5e1fb56f72f7dc4e2af450d89339a9fece13bf0/liquidglass/src/commonMain/kotlin/com/wexpa/liquidglass/GlassRestMap.kt
- Companion source for the named preset values:
  https://github.com/shayann07/liquidglass/blob/f5e1fb56f72f7dc4e2af450d89339a9fece13bf0/liquidglass/src/commonMain/kotlin/com/wexpa/liquidglass/GlassStyle.kt
- Companion source for the injected Oklab highlight helper:
  https://github.com/shayann07/liquidglass/blob/f5e1fb56f72f7dc4e2af450d89339a9fece13bf0/liquidglass/src/commonMain/kotlin/com/wexpa/liquidglass/GlassOklabSource.kt
- GLSL ES 3.00 specification, for smoothstep argument requirements:
  https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf

| Report excerpt | Check against source | Result |
|---|---|---|
| bevelSlope and snellShift, report §3.1 | GlassShaderSource.kt lines 277–302 | Exact match, including constants and comments. The functions are physically present in the 889-line shader file. |
| Legacy bend, report §3.2 | GlassShaderSource.kt lines 394–479 and 481–482; push at 506–516 | All quoted arithmetic lines occur with the same expressions and constants. The report excerpt combines separated portions of main(); it is not one contiguous block. It correctly leaves out the intervening touch/base and measured-family code, which is irrelevant to the selected Legacy branch. |
| restSourceLegacy, report §3.4 | Not physically present in GlassShaderSource.kt. That file has a source splice at line 304. Exact body is in GlassRestMap.kt lines 142–158. | Exact match to its actual companion source. The requested-file-only check cannot locate it; the report’s own GlassRestMap.kt attribution is correct. |
| Blur helpers and call, report §3.7 | GlassShaderSource.kt lines 223–271 and 613–633 | The shown early return, four-tap small blur, detailAt early return, uBlur × mat × e call, sharp RGB sampling, and rimSharp formula match. The “19 taps” line in the report is an explanatory ellipsis, not a verbatim full kernel listing. |
| Legacy dispersion, report §3.8 | GlassShaderSource.kt lines 510–516 | Exact match: split = uAberration × bend; red uses 1 − split; blue uses 1 + split. |
| Lighting, report §3.9 | GlassShaderSource.kt lines 737–812, with bevel and inner line at 744–752 | All quoted key, counter, edge, Fresnel, and highlight expressions match. The report’s “key lines” excerpt does not include applyHighlight; that helper is injected through GLASS_OKLAB_SOURCE at line 162 and is in GlassOklabSource.kt. |
| Tint/legibility, report §3.10 | GlassShaderSource.kt lines 684–687 | Exact match. This formula disproves the proposed omission rationale: contrast × uLegibility × 0.25 is additive and is not multiplied by uTint.a. |

Line-by-line source index for the quoted code (the report line numbers are the starts of the code blocks in /tmp/pill-copy-shayxo-report.md):

| Report excerpt line(s) | Exact source location | Check |
|---|---|---|
| §3.1 bevelSlope body | GlassShaderSource.kt 281–285 | Each expression and literal matches. |
| §3.1 snellShift body | GlassShaderSource.kt 295–302 | Each expression and literal matches. |
| §3.2 e, pw, slope | GlassShaderSource.kt 467–469 | Matches line by line. |
| §3.2 normalized bend and inner/rim fades | GlassShaderSource.kt 475–479 | Matches line by line; the descending smoothstep text itself needs the GLSL ES complement translation described above. |
| §3.2 mat and lens | GlassShaderSource.kt 481–482 | Matches line by line. |
| §3.2 outward push | GlassShaderSource.kt 510 | Matches exactly. |
| §3.4 restSourceLegacy signature/branches | GlassRestMap.kt 147–158 | Matches line by line; absent from GlassShaderSource.kt itself. |
| §3.7 blurredAt early return and small kernel | GlassShaderSource.kt 223–239 | Shown lines match. |
| §3.7 nineteen-tap kernel | GlassShaderSource.kt 240–261 | Report uses a placeholder for taps; it is an abbreviated excerpt, not a verbatim full function. |
| §3.7 detailAt and blur call | GlassShaderSource.kt 267–270 and 613–614 | Expressions match. |
| §3.7 sharp R/G/B sample | GlassShaderSource.kt 592–596 | Expressions match. |
| §3.7 rimSharp and bg blend | GlassShaderSource.kt 621–633 | Expressions match, including the wide-kernel branch. |
| §3.8 Legacy dispersion | GlassShaderSource.kt 514–516 | Each expression and factor matches. |
| §3.9 bevel band and innerLine | GlassShaderSource.kt 744–752 | Expressions and constants match. |
| §3.9 facing, Schlick, key/counter, edgeLine, highlight | GlassShaderSource.kt 737, 762–788, 808–812 | Expressions and constants match; report’s selected lines are not one contiguous block. |
| §3.10 strength formula | GlassShaderSource.kt 684–687 | All three additive terms and clamp match. |

Pinned-source parameter finding: GlassStyle.kt lines 1349–1364 sets the named Chrome values listed in the decision note. This confirms the report’s Chrome specular 0.50 and Fresnel 0.08, and adds source Chrome overrides the report’s generic default table does not carry into its Chrome summary: backdropBlur 14, dispersion 0.010, mirror 0.08, tint alpha 0.11, legibility 0.90, and innerShadow 0.06. The task list’s 0.07 dispersion, 0.6 legibility, 0.55 specular, 0.10 Fresnel, 0.07 innerShadow, transparent tint, no pre-blur, and no mirror are not the named Chrome preset in this commit. Keep this discrepancy visible.

GLSL ES 300 portability note: float2/float3/float4 become vec2/vec3/vec4; half/half3/half4 become float/vec3/vec4 at the shader’s declared precision. inversesqrt, sqrt, pow, max, min, clamp, mix, smoothstep, abs, dot, length, normalize, and texture exist. SkSL’s content.eval() is a host-shader API, not a GLSL ES sampler operation; the port must use Hyprglass’s sampler2D tex and its coordinate remapping. A crucial caveat: GLSL ES 3.00 says smoothstep results are undefined when edge0 >= edge1. Shayxo intentionally uses descending edges in the source expressions. Translate each descending smoothstep to its rising-edge complement, for example smoothstep(1.0, 0.75, e) becomes 1.0 - smoothstep(0.75, 1.0, e). This preserves the intended easing and avoids relying on undefined GLSL behavior.

## 2. Uniform and Lua map

“Task value” is the value supplied in this request. “Pinned Chrome” is the actual GlassStyle.Chrome value at the cited commit. Pixels assume monitorScale = 1. The Lua key column names literal keys found in the active local profile native/hyprglass-local-optics.lua; a shader uniform name alone does not prove how the host binds it.

| Shayxo parameter | Task value at scale 1 | Pinned Chrome value | Hyprglass Shaders.hpp symbol / current Lua key | Port treatment |
|---|---:|---:|---|---|
| Profile | Legacy (0) | Legacy (0) | No profile uniform in Shaders.hpp for this soft-refraction path; local profile has no profile key | Select the Legacy code path directly; do not run the lens-edge feature path alongside it. |
| Refraction band | 14 dp = 14 px | 14 dp = 14 px | bezelWidthPx = edgeThickness × minDim; Lua edge_thickness is 0.05 in local-optics.lua | Not an exact semantic equivalent: bezelWidthPx is a fraction of minDim and contour minDim is contourReferencePx. Use a new absolute band uniform or a patch constant; do not silently reinterpret edge_thickness. |
| Refraction depth | 9 dp = 9 px | 9 dp = 9 px | refractionStrength, refractionPx = refractionStrength × 50; Lua refraction_strength is 0.55 | Existing gain has different units and is multiplied by 50. Replace that path with an absolute 9 px source depth. |
| Fine blur uBlur | 0 dp = 0 px | 0 dp = 0 px | No uBlur in Shaders.hpp. Lua blur_strength is 0.25 in local-optics.lua | Directly sample sharp tex. Host meaning of blur_strength is [NEEDS-RECON]; zero every upstream/pre-blur that would otherwise soften tex if the intended result is fully sharp. |
| Backdrop pre-blur | 0 dp per task intent | 14 dp = 14 px | No corresponding shader uniform; Lua blur_strength is the nearest current material key but its exact host stage is not proven by Shaders.hpp | Conflict. Source Chrome still pre-blurs. A zero-pre-blur port is not the full source Chrome material. |
| IOR | 1.5 | 1.5 | LENS_IOR is 1.5 only inside HYPRGLASS_FEATURE_LENS_EDGE; otherwise no generic IOR uniform | Use a local constant 1.5 in the replacement. Do not activate the separate lens-edge law. |
| Bevel power | 2 | 2 (inherited default) | No equivalent. roundingPower is outline shape power, not bevel power | New constant 2.0. Keep it distinct from roundingPower. |
| Corner power | 2 | 2 (inherited default) | roundingPower and invRoundingPower; no such key in active local-optics.lua | Reuse roundingPower for the outline. Confirm the host binding [NEEDS-RECON]. |
| Scale | 0 | 0 for this 38 px short edge | No equivalent size-factor uniform | Hard-code 0 for this pill size. Shayxo’s element-size factor reaches zero below a 56 dp minimum edge. |
| Materialize | 1 | 1 (default) | No equivalent; glassOpacity is output alpha, not materialize. Lua glass_opacity = 1.0 | Hard-code 1.0. Do not use glassOpacity as a substitute. |
| Dispersion | 0.07 | 0.010 | chromaticAberration; Lua chromatic_aberration = 0.04 | Existing uniform can feed the new direct fraction after removing Hyprglass’s old ×0.35 factor. Conflict: source Chrome is 0.010, not 0.07. |
| Lit bevel width | 3 dp = 3 px | 3 dp = 3 px | bevelSize × monitorScale; Lua bevel_size = 3.0 | Reuse bevelSize; monitorScale is 1 here. |
| Specular | 0.55 | 0.50 | specularStrength; Lua specular_strength = 0.50 | Reuse but replace its old formula, including the old ×0.08 scale. Conflict: task value differs from source Chrome. |
| Specular power | 6 | 6 (inherited default) | No exponent uniform. specularAngle is an angle, not a power | New constant 6.0. |
| Counter light | 0.35 | 0.35 (inherited default) | No equivalent uniform/key | New constant 0.35. At this value, source formula gives counterPow = 6 × 1.6 = 9.6. |
| Edge light | 1 | 1 (inherited default) | No equivalent uniform/key | New constant 1.0. |
| Bevel peak | 0 | 0 (inherited default) | No equivalent uniform/key | New constant 0.0; this selects the source chamfer profile. |
| Inner shadow | 0.07 | 0.06 | No equivalent formula. Existing bottom shadow is hard-coded 0.06 × bottomBias × edgeProximity² | Replace the old bottom shadow with the source innerLine formula. Conflict: value differs. |
| Legibility | 0.6 | 0.90 | No equivalent tint-legibility uniform/key | New uniform or constant. It remains active with transparent tint whenever the local contrast term is nonzero. Conflict: value differs. |
| Fresnel gain | 0.10 | 0.08 | fresnelStrength; Lua fresnel_strength = 0.10 | Reuse only after replacing the current edgeProximity² × strength × 0.15 formula with Schlick. Conflict: source Chrome is 0.08. |
| Light vector | (-0.35, -0.94) | (-0.35, -0.94) inherited | No vector equivalent. Lua bevel_angle = 315 degrees | Add the vector constant/uniform. Do not use bevelAngle: the target’s angle helper maps 315 degrees to a diagonal, not this overhead vector. |
| Highlight chroma | 0.7 (not listed by task) | 0.7 inherited default | No equivalent | Needed by source applyHighlight; hard-code 0.7 unless a new uniform is justified. |
| Wide tone kernel | 10 dp = 10 px (inherited default; used by exact source Chrome) | 10 dp = 10 px | No wide texture or wide-kernel path in Shaders.hpp | Exact source tone requires a quarter-scale Gaussian backdrop copy and a new sampler/binding. [NEEDS-RECON] |
| Detail share k | 0.34 (inherited default) | 0.34 | No equivalent | New constant/uniform if the three-term tone is ported. |
| Detail lift c | 0 | 0 | No equivalent | New constant/uniform if the three-term tone is ported. |
| Tint | Alpha 0, RGB white in current local profile | White alpha 0.11 in source Chrome | tintColor and tintAlpha; Lua tint_color = 0xffffff00 in active local profile | Keep task transparency only if it is an explicit override. It does not disable source wide tone or the additive legibility term. |
| Tint adaptivity | Not listed; active local profile has neutral adaptive_dim/adaptive_boost | adaptivity 0.90 | No equivalent: adaptiveDim/adaptiveBoost are different operations | New uAdaptive input if reproducing source toneMappedTint. |
| Whole-element tint flip | Not listed | invertsWithBackdrop defaults true; uFlip is decided by source host | No equivalent uniform/key in Shaders.hpp or active Lua profile | New uFlip input or a documented fixed value; exact source behavior needs host policy [NEEDS-RECON]. |
| Legacy mirror | Excluded by task section 5 | 0.08 | No same-source mirror path in target; Lua profile has no mirror key | Excluding it deviates from source Chrome. The pinned Chrome preset uses the Legacy mirror echo; resolve this before calling the port exact. |
| Pad | 9 × 1.4 + zero blur = 12.6 px | 9 × 1.4 + max(0, 14) = 26.6 px | No pixel-pad uniform; uvPadding and sampleUVOffset/sampleUVScale are normalized coordinate plumbing | The host recording/sample region must provide the requested pad. Source Chrome’s own pre-blur changes the recorded pad requirement. |

The active contour configuration was confirmed: indicator.c says the outline comes from mask_mode "contour" in native/hyprglass-local-optics.lua. That profile calls layer("computer-use-indicator", { mask_mode = "contour" }). native/hyprglass-indicator.lua is a separate profile that says region; do not use that file to infer the active mask mode.

## 3. Port, function by function

### 3a. Exact bevel slope and Snell shift

These scalar functions are already GLSL ES-compatible verbatim. They contain no SkSL-only types or calls.

    float bevelSlope(float e, float p) {
        float u = 1.0 - clamp(e, 0.002, 0.998);
        float up = pow(u, p);
        return pow(u, p - 1.0) / pow(max(1.0 - up, 1e-4), 1.0 - 1.0 / p);
    }

    float snellShift(float slope, float ior) {
        float inv = inversesqrt(1.0 + slope * slope);
        float si = slope * inv;
        float ci = inv;
        float st = si / max(ior, 1.0001);
        float ct = sqrt(max(1.0 - st * st, 0.0));
        return (si * ct - ci * st) / max(ci * ct + si * st, 1e-4);
    }

### 3b. Contour signed distance, normal, and Legacy bend

Hyprglass’s contour field stores signed distance in contourSample.r / cornerSdf; the contour-field source says the sign is negative inside and positive outside. In contour mode, bevelSdf = cornerSdf, so map Shayxo’s inward-positive local depth to:

    float depth = max(-bevelSdf, 0.0);

The existing inwardDir is -contourOutward. Shayxo’s n points outward, so the sign relation is n = -inwardDir. For this contour port, however, calculate the source wide-epsilon gradient from the contour SDF and use that result for n; do not use contourOutward’s existing field gradient as the bend normal.

The following is the source wide-epsilon construction translated to the contour field. eps and all distance values are framebuffer pixels. uv, contourUVScale, invFullSize, contourTex, and monitorScale are identifiers present in the pinned Shaders.hpp. The aliases bandPx, fieldUv, n, axisFade, and eps are new locals.

    float bandPx = 14.0 * monitorScale;
    float depth = max(-bevelSdf, 0.0);

    float eps = clamp(bandPx * 0.3, 1.0, 16.0);
    vec2 fieldUv = uv * contourUVScale;
    vec2 ex = vec2(eps * invFullSize.x, 0.0);
    vec2 ey = vec2(0.0, eps * invFullSize.y);
    vec2 g = vec2(
        texture(contourTex, fieldUv + ex * contourUVScale).r
            - texture(contourTex, fieldUv - ex * contourUVScale).r,
        texture(contourTex, fieldUv + ey * contourUVScale).r
            - texture(contourTex, fieldUv - ey * contourUVScale).r);
    float gLen = length(g);
    vec2 n = g / max(gLen, 1e-5);
    float axisFade = smoothstep(0.15, 0.80, gLen / (2.0 * eps));

For scale 1, eps = clamp(14 × 0.3, 1, 16) = 4.2 px. Positive contour SDF gradient points outward. The old inwardDir points the opposite way. Do not retain the current refractionDir/edgeDir blending or the current exponential edgeProximity falloff in the refractive offset.

The source bend translated for GLSL ES 300 uses a complement for the descending smoothstep. uRefractBand, uBevelPower, and uIor below are new patch constants/uniforms, not existing Shaders.hpp uniforms. The task values are shown; the conflicting source Chrome values are in section 2.

    float e = clamp(depth / max(uRefractBand, 0.001), 0.0, 1.0);
    float pw = max(uBevelPower, 1.5);
    float slope = bevelSlope(e, pw);

    float bend = snellShift(slope, uIor)
        / max(snellShift(bevelSlope(0.0, pw), uIor), 1e-4);
    bend *= (1.0 - smoothstep(0.75, 1.0, e))
        * axisFade
        * smoothstep(0.0, 1.5, depth);
    bend = clamp(bend, 0.0, 1.0);

    float scale = 0.0;
    float mat = 1.0;
    float lens = uRefractDepth * mix(0.85, 1.25, scale) * mat;
    vec2 push = n * bend * lens;

Set uRefractBand = 14 × monitorScale px, uRefractDepth = 9 × monitorScale px, uBevelPower = 2, and uIor = 1.5 for the requested values. The source formula has a dome rim guard after the axis/rim fade; for this pill domeWeight evaluates to zero, so that multiplier is exactly 1 and may be omitted. The existing Hyprglass refractionStrength × 50 calculation is replaced, not multiplied into this push.

### 3c. Push distance

The element-size scale is 0: the pill’s short edge is 38 px, below Shayxo’s 56 dp zero-scale threshold. Therefore:

    lens = 9.0 * mix(0.85, 1.25, 0.0) * 1.0
         = 9.0 * 0.85
         = 7.65 px
    push = n * bend * 7.65 px

This is the outward sample displacement; it is not the local SDF depth. The SDF depth starts at zero on the outline and grows inward. Keep those two meanings separate.

### 3d. Long-pill normal and dome decision

The contour shape is a sampled field, so Shayxo’s analytic rounded-rectangle normal branch does not apply. Use the wide-epsilon normal and axisFade above in place of Hyprglass’s existing contourOutward estimate. At the pill medial axis the two SDF differences cancel; gLen approaches zero, axisFade smoothly falls to zero, and the normal cannot flip the displacement across a one-pixel seam.

The nominal pill is 288 × 38 px, so:

    aspect = 288 / 38 = 7.578947...
    inradius = 38 / 2 = 19 px
    band / inradius = 14 / 19 = 0.736842...

The aspect factor smoothstep(1.5, 3.0, aspect) is 1. The band factor smoothstep(0.75, 1.0, band / inradius) is 0 because 0.736842 is below 0.75. Thus domeWeight = 1 × 0 = 0. opticalDepth stays depth; domeRadius and domeGrad are not evaluated; the dome normal blend and dome axisFade blend are identities. Omit the dome field for these dimensions. If the rendered pill width is clamped, its aspect changes, but the second factor still keeps domeWeight at zero so long as its actual inradius remains 19 px and the band remains 14 px.

### 3e. Blur after refraction; zero-blur behavior

Shayxo’s source radius is uBlur × mat × e, where e = depth / band. With the requested uBlur = 0, every in-band radius is exactly 0. In Shayxo’s blurredAt, radius < 0.5 returns backdropAt(p) before any blur taps. The port should implement the reduced path directly: use the sharp sample at the displaced coordinate and include no blurAt/detailAt taps or blur loops in the shader replacement.

Hyprglass’s sampleBlurred() can select frostTex when HYPRGLASS_FEATURE_FROST is compiled. For this no-fine-blur path, sample tex directly through the existing toSampleBoxUV() and toTexUV() remaps; this avoids accidentally retaining the frost sample path. This only guarantees a sharp shader fetch. Whether the renderer has already blurred tex is outside Shaders.hpp and is [NEEDS-RECON].

rimSharp = (1 - e)² remains part of Shayxo’s source treatment. If there is no wide tone copy, uBlur = 0 makes soft == sharp and the rimSharp mix collapses exactly to sharp everywhere; it can be removed. If the source Chrome wide-tone copy is ported, keep the source’s rimSharp colour-fringe equation, which blends sharp samples and does not add fine blur taps. The wide-tone copy is a separate prefiltered texture path, not the uBlur scatter path.

### 3f. Dispersion and exact three-channel sample

The source formula is:

    float split = uAberration * bend;
    vec2 pushR = push * (1.0 - split);
    vec2 pushB = push * (1.0 + split);

Hyprglass’s uv coordinates are normalized, while push is in pixels. Convert by invFullSize, then fetch one channel from each coordinate. sampleSharp is a new helper; tex, toSampleBoxUV, toTexUV, invFullSize, uv, and sample-coordinate transforms are from Shaders.hpp.

    vec3 sampleSharp(vec2 wuv) {
        vec2 tuv = toTexUV(toSampleBoxUV(wuv));
        return texture(tex, clamp(tuv, 0.001, 0.999)).rgb;
    }

    float split = chromaticAberration * bend;
    vec2 pushR = push * (1.0 - split);
    vec2 pushB = push * (1.0 + split);
    vec2 uvR = uv + pushR * invFullSize;
    vec2 uvG = uv + push * invFullSize;
    vec2 uvB = uv + pushB * invFullSize;
    vec3 sharp = vec3(
        sampleSharp(uvR).r,
        sampleSharp(uvG).g,
        sampleSharp(uvB).b);

This is three texture() fetches for R/G/B. Use chromaticAberration directly as uAberration; remove Hyprglass’s existing ×0.35 chromaSpread. The task value is 0.07; pinned Chrome is 0.010; the currently active Lua value is 0.04. Resolve the value before binding it.

### 3g. Lighting; replace existing Hyprglass bevel/specular/Fresnel/shadow

Replace the existing BEVEL, FRESNEL RIM GLOW, SPECULAR, and INNER SHADOW blocks in Shaders.hpp main() (around lines 643–722). Do not leave those blocks active alongside this code. Keep the source normal n and local depth from section 3b. The port uses the requested vector (-0.35, -0.94); current bevel_angle = 315 degrees is a diagonal under Hyprglass’s angle helper and is not equivalent.

For bevelPeak = 0, the source bevel band is the complement of a rising smoothstep. This is the GLSL ES-safe form. uBevel resolves to bevelSize × monitorScale = 3 px at scale 1.

    float bevelPx = bevelSize * monitorScale;
    float bevelBand = 1.0 - smoothstep(0.0, bevelPx, depth);

    float innerLine = max(
        1.0 - smoothstep(0.0, 2.2 * bevelPx, depth) - bevelBand,
        0.0);
    color -= vec3(innerLine * uInnerShadow * mix(0.9, 1.15, 0.0) * 1.0);

    vec2 uLight = vec2(-0.35, -0.94);
    float facing = dot(n, uLight);
    float cosI = inversesqrt(1.0 + slope * slope);
    float f0 = (uIor - 1.0) / (uIor + 1.0);
    f0 = f0 * f0;
    float fresnel = f0 + (1.0 - f0) * pow(max(1.0 - cosI, 0.0), 5.0);

    float counterLight = 0.35;
    float counterPow = 6.0 * mix(1.6, 1.0,
        smoothstep(0.35, 1.0, counterLight));
    float key = pow(max(facing, 0.0), 6.0) * bevelBand;
    float counter = pow(max(-facing, 0.0), counterPow)
        * bevelBand * counterLight;
    float edge = 1.0 - smoothstep(0.0, 2.0, depth);
    float edgeLine = edge * 0.5
        * (max(facing, 0.0) + counterLight * max(-facing, 0.0));

    float highlight = (key + counter) * specularStrength
        + edgeLine * specularStrength * uEdgeLight
        + fresnel * fresnelStrength * bevelBand;
    color = applyHighlight(color, highlight, uHiChroma);

Set uEdgeLight = 1, uHiChroma = 0.7, uInnerShadow to the selected value, and use the selected specularStrength/Fresnel gain from section 2. With counterLight = 0.35, smoothstep(0.35,1.0,0.35) is 0, so counterPow = 6 × 1.6 = 9.6. The edge line is directional and reaches only the outermost 2 px. The source has no held glow for Legacy, so no heldGlow or capRim term is included.

The source calls applyHighlight from its injected GLASS_OKLAB_SOURCE. To keep that lighting math, add this GLSL ES translation as a helper. It changes only SkSL vector/half types to GLSL ES vec types.

    vec3 toLinearApprox(vec3 c) { return c * c; }
    vec3 fromLinearApprox(vec3 c) { return sqrt(max(c, vec3(0.0))); }

    vec3 linearToOklab(vec3 c) {
        float l = 0.4122214708 * c.r + 0.5363325363 * c.g + 0.0514459929 * c.b;
        float m = 0.2119034982 * c.r + 0.6806995451 * c.g + 0.1073969566 * c.b;
        float s = 0.0883024619 * c.r + 0.2817188376 * c.g + 0.6299787005 * c.b;
        float l_ = pow(max(l, 0.0), 0.3333333333);
        float m_ = pow(max(m, 0.0), 0.3333333333);
        float s_ = pow(max(s, 0.0), 0.3333333333);
        return vec3(
            0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_);
    }

    vec3 oklabToLinear(vec3 lab) {
        float l_ = lab.x + 0.3963377774 * lab.y + 0.2158037573 * lab.z;
        float m_ = lab.x - 0.1055613458 * lab.y - 0.0638541728 * lab.z;
        float s_ = lab.x - 0.0894841775 * lab.y - 1.2914855480 * lab.z;
        float l = l_ * l_ * l_;
        float m = m_ * m_ * m_;
        float s = s_ * s_ * s_;
        return vec3(
             4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s);
    }

    vec3 applyHighlight(vec3 col, float amount, float chroma) {
        if (amount <= 0.0) return col;
        vec3 additive = col + vec3(amount);
        if (chroma <= 0.0) return additive;
        vec3 lab = linearToOklab(toLinearApprox(col));
        lab.x = lab.x + amount * 0.90;
        lab.yz = lab.yz * (1.0 + amount * 1.20);
        vec3 lifted = fromLinearApprox(
            clamp(oklabToLinear(lab), vec3(0.0), vec3(1.0)));
        return mix(additive, lifted, clamp(chroma, 0.0, 1.0));
    }

### 3h. Tone and legibility; do not silently omit

Omitting tone and legibility because tint alpha is zero is not supported by GlassShaderSource.kt’s formulas. It computes:

    strength = uTint.a * tintCoverage * mix(mix(0.9, 1.25, scale), 1.0, measured)
        + contrast * uLegibility * 0.25
        + clamp(uFrost, 0.0, 1.0) * 0.35;

    contrast = detailWeight
        * clamp(abs(luma(sharp) - luma(detailCopy)) * 4.0, 0.0, 1.0);

The contrast term is additive, not multiplied by tint alpha. Also, the wide tone kernel transforms bg before the tint blend. With current transparent white tint, scale = 0, mat = 1, tintAlpha = 0, and frost = 0, strength is still contrast × legibility × 0.25 when dispersion makes sharp differ from the unblurred green detailCopy. With the source Chrome wide kernel, the three-term tone remains active regardless of tint alpha.

Source Chrome inherits wideKernel = 10 dp, fineShare = 0.34, and detailLift = 0. Its exact tone formula is lin = B + k(D − B) + c|D − B|. Hyprglass Shaders.hpp has no quarter-scale wide texture. The sampler below is NEW plumbing: wideTex is a quarter-scale Gaussian copy of the same padded backdrop, with the same normalized coordinate domain as tex. The host must bind it [NEEDS-RECON]. The shader math is otherwise the source expression.

    uniform sampler2D wideTex; // NEW: quarter-scale Gaussian copy, same normalized UV domain as tex

    vec3 sampleWide(vec2 wuv) {
        vec2 tuv = toTexUV(toSampleBoxUV(wuv));
        return texture(wideTex, clamp(tuv, 0.001, 0.999)).rgb;
    }

    float luma(vec3 c) {
        return dot(c, vec3(0.2126, 0.7152, 0.0722));
    }

    vec3 toneMappedTint(vec3 tint, float bgLuma, float adapt) {
        float g = clamp(bgLuma, 0.0, 1.0);
        float value = mix(1.0, mix(1.10, 0.88, g), adapt);
        float sat = mix(1.0, mix(0.88, 1.06, g), adapt);
        float mean = dot(tint, vec3(1.0 / 3.0));
        vec3 shifted = vec3(mean) + (tint - vec3(mean)) * sat;
        return clamp(shifted * value, vec3(0.0), vec3(1.0));
    }

    float detailWeight = smoothstep(0.02, 0.10, max(0.34, abs(0.0)));
    vec3 detailCopy = sampleSharp(uvG); // uBlur = 0: source detailAt returns one sharp sample
    float contrast = detailWeight
        * clamp(abs(luma(sharp) - luma(detailCopy)) * 4.0, 0.0, 1.0);
    vec3 soft = mix(sharp, detailCopy, detailWeight);
    float rimSharp = (1.0 - e) * (1.0 - e);
    vec3 axis = detailCopy;
    vec3 bg = soft + (sharp - axis) * rimSharp;

    vec3 wide = sampleWide(uv);
    vec3 detail = bg - wide;
    bg = wide + detail * 0.34 + abs(detail) * 0.0;

    float strength = clamp(
        tintAlpha * 1.0 * mix(0.9, 1.25, 0.0)
            + contrast * uLegibility * 0.25,
        0.0, 0.95);
    float bgLuma = luma(bg);
    vec3 tinted = toneMappedTint(tintColor, bgLuma, uAdaptive);
    tinted = mix(tinted, vec3(1.0) - tinted, clamp(uFlip, 0.0, 1.0));
    color = mix(bg, tinted, strength);

Here detailWeight evaluates to 1 because fineShare = 0.34. tintAlpha is the existing Hyprglass uniform populated from the current tint_color key; for the current transparent tint it is 0, and tintColor is white. uLegibility is new. Use 0.6 only if the task list is explicitly selected; exact pinned Chrome uses 0.90. The formulas demonstrate why transparent tint does not make the whole branch a no-op. Source Chrome also runs toneMappedTint with adaptivity 0.90, then applies the host-decided uFlip. The helper below is translated from GlassShaderSource.kt. uAdaptive and uFlip have no equivalent in Shaders.hpp; uFlip also depends on a host decision, so both bindings are [NEEDS-RECON]. The task’s transparent white tint can be used as tintColor/tintAlpha, but it does not eliminate contrast strength. The code ports the selected three-term tone plus legibility; do not keep the separate Hyprglass brightness/vibrancy/tint overlay on top of it. Current neutral brightness/saturation values are not a substitute for B, D, k, c, contrast, adaptivity, or flip.

### 3i. Padding

The requested no-pre-blur values give the Legacy pad:

    pad = refractionDepth * 1.4 + max(blurRadius, backdropBlur)
        = 9 * 1.4 + max(0, 0)
        = 12.6 px

The pinned Chrome preset instead has backdropBlur = 14 dp, so its formula gives 9 × 1.4 + max(0,14) = 26.6 px. This is another reason the task’s 12.6 px pad is not the complete pinned Chrome configuration.

Hyprglass already maps sample UVs through uvPadding and sampleUVOffset/sampleUVScale, but Shaders.hpp does not promise how many pixels the renderer recorded beyond this layer. The recorded backdrop must contain at least the selected pad beyond every side of the actual contour. At the task values, the maximum blue displacement is 7.65 × (1 + 0.07 × 1) = 8.1855 px, less than 12.6 px. If the record does not include the pad, the outward R/G/B fetches reach the clamped texture boundary and smear or clip the fringe asymmetrically.

## 4. What stays identical and what changes

### Math copied from Shayxo

- bevelSlope and exact Snell tangent-difference snellShift, including all constants.
- e = clamp(opticalDepth / band, 0, 1), bevel power floor 1.5, bend normalized by its own rim Snell shift, and final clamp to [0,1].
- Inner C1 fade at the inner band edge, translated as 1 − smoothstep(0.75,1.0,e).
- 1.5 px outer-rim guard smoothstep(0,1.5,depth).
- outward push n × bend × lens; source scale factor law mix(0.85,1.25,scale).
- Wide-epsilon normal eps = clamp(band × 0.3,1,16), axisFade smoothstep(0.15,0.80,gLen/(2eps)).
- Dome weighting formula was evaluated for this geometry and is exactly zero; no dome displacement or normal blend runs.
- Per-channel split = aberration × bend, with red 1 − split and blue 1 + split.
- Fine blur radius uBlur × mat × e and rimSharp = (1 − e)². With uBlur = 0, no fine blur taps remain.
- Schlick f0 and fifth-power Fresnel; key/counter power, 2 px directional line, and innerLine formula.
- applyHighlight’s Oklab constants and its gamma-2 transfer approximation.
- Three-term tone B + k(D−B) + c|D−B| and additive contrast legibility term, if the source Chrome tone path is retained.
- Legacy pad formula depth × 1.4 + max(fine blur, backdrop pre-blur).

### Plumbing changes only

- SkSL float2/float3/float4 and half types become GLSL ES vec types and floats.
- content.eval(pixelCoordinate) becomes texture(tex, normalizedUV), through existing toSampleBoxUV() and toTexUV().
- The shader input uses existing sampler2D tex; new sharp helper avoids sampleBlurred()/frostTex.
- Contour SDF is sampled from existing contourTex at offsets of eps pixels. contourSample.gb / contourOutward is superseded for this refraction normal; bevelSdf sign is converted with depth = max(-bevelSdf,0).
- New shader parameters are patch constants or new uniforms where section 2 says there is no equivalent. Host key mapping and wideTex binding are [NEEDS-RECON].
- Descending smoothstep calls are rewritten as complements because GLSL ES 3.00 leaves edge0 >= edge1 undefined. No falloff constants change.
- Add the source wide-tone texture binding only if retaining that exact tone math. It is a host texture plumbing change, not another displacement law.

## 5. What is deliberately not copied

- foldSource: measured-profile interaction fold; selected profile is Legacy.
- heldSource, held magnification, held glow: finger-held interaction family; the indicator is a resting Legacy pill.
- Measured rest map: selected profile is Legacy; the Legacy bend branch does not call the measured source map.
- Legacy mirror echo: excluded by the task’s explicit non-copy list. Pinned GlassStyle.Chrome sets mirror = 0.08; the selected zero-mirror value is a documented deviation from true Chrome.
- Wide tone kernel: omitted because this Hyprglass path has no `wideTex` binding or quarter-scale Gaussian copy. The port retains the additive legibility strength and `toneMappedTint`, but samples sharp content in place of the source wide copy, so the source three-term tone `B + k(D-B) + c|D-B|` is not reproduced.

## 6. Risks and checkable open questions

- Which value set should be bound where task values conflict with pinned Chrome? Check the explicit source/task comparison in sections 1–2 before changing Lua.
- Should the Legacy mirror echo be zeroed per the task’s non-copy list, or retained at source Chrome’s mirror = 0.08? Both cannot be exact simultaneously.
- Does the active renderer record an unblurred tex with at least 12.6 px beyond the contour, or 26.6 px if retaining source Chrome’s backdropBlur = 14? Verify the actual sample FBO dimensions and UV padding.
- Is contourReachPx at least band + eps = 18.2 px for the 14 px band? If not, wide-epsilon SDF samples can hit the clamped/flat part of contourTex and axisFade may suppress more than the medial axis.
- Does glassBoxSizePx represent the pill’s actual 288 × 38 contour or the enclosing 320 × 66 surface? The dome calculation above uses the actual pill dimensions; its band factor is zero for 38 px height.
- Is HYPRGLASS_FEATURE_LENS_EDGE disabled for the active soft-refraction patch? The new formula must replace the branch that currently contains the cylindrical-bottle hunk, not sit beside the separate lens-edge branch.
- Does the host permit a wideTex binding and produce the source quarter-scale Gaussian copy? Shaders.hpp alone does not settle this.
- Does the layer’s tex arrive unblurred when blur_strength is set to zero? Shaders.hpp only defines texture sampling; it does not establish the renderer’s pre-blur stage.
- Which build patch actually applies to the active checkout, and how are new uniforms associated with Lua keys? The shader file does not contain that host contract. [NEEDS-RECON]

## 7. Implementer checklist

1. Resolve the value and mirror conflicts in sections 1–2. Do not call the result exact Chrome until this is decided.
2. [NEEDS-RECON] Confirm the active patch artifact and application order. Replace the cylindrical-bottle refraction hunk in the active patch with sections 3a–3f. The task names native/hyprglass-cylindrical-bottle.patch; confirm whether the build uses that file or another patch.
3. In the same patch, replace the current exponential refraction/color-channel offsets and existing bevel/Fresnel/specular/inner-shadow blocks with the source path in sections 3b–3h. Keep the contour sign conversion and use wide epsilon for n.
4. Update native/hyprglass-local-optics.lua only after [NEEDS-RECON] confirms the Lua-to-uniform binding names. Set fine blur to zero; choose either task or pinned Chrome values; add bindings for any new band, depth, light, power, legibility, adaptivity/flip, and tone parameters. The current profile is contour mode, glass_opacity 1, tint_color 0xffffff00.
5. [NEEDS-RECON] Decide whether source Chrome’s backdropBlur 14 dp is intentionally overridden to zero. Verify tex is sharp and recorded padding covers the chosen formula.
6. [NEEDS-RECON] Add/bind wideTex and its quarter-scale Gaussian preparation if retaining exact source Chrome tone. If that host path is unsupported, report the exact deviation instead of silently dropping tone/legibility.
7. [NEEDS-RECON] Run the repository’s pinned Hyprglass build command against commit 03a57c4451b4abee38feda2ffb725f55ecc0f2fd with the active patch. Record the command and successful shader compile output.
8. [NEEDS-RECON] Install the built library using the repository’s intended immutable install path. Record the plugin ABI and installed hash path.
9. [NEEDS-RECON] Refresh and validate the visuals manifest after Lua/profile changes; record the exact command and resulting library/profile hashes.
10. [NEEDS-RECON] Run the repository’s documented shader/contract tests and a live indicator test. Check that the 1 px medial-axis seam is absent, text remains sharp, the outer RGB fringe is not clipped, and no old bevel/Fresnel lighting remains layered underneath.
11. This design worker did not build, install, refresh the manifest, run tests, or launch the indicator. CODEX_OK remains unverified until the implementer performs and records the authorized launch check.

