# Báo cáo recon: port Shayxo Legacy/Chrome cho pill

- **Model:** gpt-6-luna
- **Reasoning effort:** max
- **Bắt đầu (Asia/Ho_Chi_Minh):** 2026-11-18 13:13:19
- **Kết thúc (Asia/Ho_Chi_Minh):** 2026-11-18 13:40:40
- **CODEX_OK:** chưa xác minh. `printenv CODEX_OK CODEX_MODEL CODEX_REASONING_EFFORT` không trả giá trị; `hyprctl -j monitors` cũng không trả JSON trong shell này.
- **Phạm vi:** đã đọc đầy đủ `/tmp/pill-copy-shayxo-report.md` (466 dòng), chỉ đọc source/config/log; không build, không chạy test, không kích hoạt plugin, không đọc shell history. File này là file repo mới duy nhất được tạo.

## 1. Provenance của plugin 69309243

### Source tree khớp artifact

Source tree khớp chính xác với plugin đang cài là:

`~/computer-use-handoff/backend/hyprglass-1.1.1`

Bằng chứng trực tiếp:

- `native/visuals.json:4` trỏ tới `~/.local/share/agent-computer-use/plugins/hyprglass-69309243789bee75616b5d260882db7597ab7da4f928755971f813dd77b89748.so`.
- SHA-256 của file cài và `~/computer-use-handoff/backend/hyprglass-1.1.1/hyprglass.so` đều là `69309243789bee75616b5d260882db7597ab7da4f928755971f813dd77b89748` (đối chiếu trực tiếp bằng `sha256sum`).
- ELF của artifact source có `DW_AT_comp_dir : ~/computer-use-handoff/backend/hyprglass-1.1.1` (`readelf --debug-dump=info`), xác nhận thư mục biên dịch được ghi trong debug info.
- `git rev-parse HEAD` của cây này là `03a57c4451b4abee38feda2ffb725f55ecc0f2fd`, đúng pin trong `scripts/build-glass.py:16` và `scripts/setup.py:336`.

Cây này có đúng ba file tracked đang sửa: `src/GlassLayerSurface.cpp`, `src/GlassRenderer.cpp`, `src/Shaders.hpp` (`git status --short --branch`). Hai patch trong repo đều reverse-check thành công trên cây này:

- `native/hyprglass-local-optics.patch`: chỉnh C++ trong `GlassLayerSurface.cpp` và `GlassRenderer.cpp` (patch: dòng 1–34); phần chính lấy hình chữ nhật optical từ blur region và dùng nó để đặt `glassBoxOffsetPx` / `glassBoxSizePx`.
- `native/hyprglass-cylindrical-bottle.patch`: chỉ sửa `src/Shaders.hpp` (patch: dòng 1–67). Hunk thay exponential falloff bằng profile hình chai trụ; dòng 50–66 ghi khoảng cách tới đường tâm là `PILL_HEIGHT/2 = 19px` tại scale 1, và code dùng `thetaS = asin(sinS)`, `thetaR = asin(sinS / 1.5)`, `lensFalloff ... * 4.33`.

Trong cây khớp artifact, `src/Shaders.hpp` hiện có đúng profile chai trụ này ở dòng 498–530. Như vậy patch cylinder đã hiện diện trong source đã biên dịch; không thể xác minh từ file hiện có ai đã áp dụng patch bằng thao tác nào hoặc vào thời điểm nào.

### Build command và giới hạn tái lập

Lệnh tái dựng source hiện có là:

```sh
python3 scripts/build-glass.py ~/computer-use-handoff/backend/hyprglass-1.1.1 --local-optics --allow-dirty
```

Đây là **lệnh tái dựng suy ra từ cây hiện có**, không phải lệnh lịch sử được tìm thấy trong log. `scripts/build-glass.py:8–9` nêu dạng gọi; dòng 16 pin commit; dòng 19 đặt duy nhất `PATCH = .../native/hyprglass-local-optics.patch`; dòng 42 bắt buộc `--local-optics`; dòng 57–61 từ chối cây dirty nếu thiếu `--allow-dirty`; dòng 71–79 chỉ kiểm tra/áp dụng local-optics patch; dòng 84 gọi `make -j2 -B HYPRGLASS_VERSION=1.1.1-cu.1`.

Trích nguyên văn các câu quyết định từ `scripts/build-glass.py:4–6`:

> “It applies one supplied patch and builds in the source tree. It never resets, cleans, stashes or deletes, and it never installs or loads anything.”

Do script hiện tại **không áp dụng** `hyprglass-cylindrical-bottle.patch`, lệnh trên chỉ tạo cùng nội dung shader nếu source đã chứa patch cylinder từ trước. Nếu chạy script trên checkout sạch của pin 03a57c4, script chỉ thêm local-optics C++; nó **không** tái tạo shader chai trụ. `scripts/setup.py:331–340` tạo clone tạm, checkout pin, rồi gọi `build-glass.py ... --local-optics` mà không có bước patch cylinder. Vì thế build/setup hiện tại không tái tạo đầy đủ source đang gắn với plugin 69309243 từ upstream sạch.

Không thấy log file nào ghi lại chính xác command lịch sử cho artifact này trong các file/log đã kiểm tra. Shell history được để ngoài phạm vi như yêu cầu. Vì vậy command ở trên là command phù hợp để rebuild cây source đã có cả hai patch, không phải khẳng định về command lịch sử hoặc tái lập byte-for-byte.

Các ứng viên khác đã kiểm tra không khớp: `~/computer-use-handoff/backend/hyprglass-local-optics` tạo SHA khác (`dc1567…`); backup `~/backups/omarchy-native-port-20261113/hyprglass-0.57` ở commit khác. Không tìm thấy cây build `Shaders.hpp` khớp trong `/tmp`.

## 2. Pinned upstream `Shaders.hpp`: uniforms, blur và thứ tự lấy mẫu

Nguồn ở đây là **file pristine tại** commit `03a57c4451b4abee38feda2ffb725f55ecc0f2fd`, đọc bằng `git show HEAD:src/Shaders.hpp`. Cây source hiện tại đã có patch cylinder nên các dòng của nó sau đoạn refraction lệch so với `HEAD`. Shader chính là `liquidglass.frag`; blur và contour là các shader pass riêng trong cùng `Shaders.hpp`.

**Lưu ý về “default”:** GLSL uniforms không tự có giá trị mặc định. Các giá trị dưới là host config mặc định trong `src/BuiltInPresets.hpp:23–60`; những biến per-draw được renderer tính/bind, không có Lua default riêng. `blur_strength` và `blur_iterations` là host settings, không phải uniforms của shader chính.

### Uniforms của `liquidglass.frag`

| Uniform | Type | Ý nghĩa | Giá trị mặc định / nguồn |
|---|---|---|---|
| `tex` | `sampler2D` | Backdrop đã được host xử lý blur, dùng để lấy màu sau khi tính offset | Texture do renderer bind |
| `fullSize` | `vec2` | Kích thước framebuffer sample | Renderer per-draw |
| `invFullSize` | `vec2` | Nghịch đảo kích thước framebuffer, tránh chia lặp từng pixel | Tính từ `fullSize` |
| `radii` | `vec4` | Bán kính bốn góc theo thứ tự TL, TR, BR, BL | Shape/Hyprland per-draw |
| `uvPadding` | `vec2` | Padding quanh UV để sample không chạm biên texture | Renderer tính theo sample region |
| `refractionStrength` | `float` | Độ lớn refraction; nhánh soft edge đổi thành `refractionStrength * 50px` | `0.6` |
| `noiseStrength` | `float` | Grain/noise | `0.0` |
| `chromaticAberration` | `float` | Độ lệch sample giữa R/G/B | `0.5` |
| `fresnelStrength` | `float` | Cường độ viền Fresnel | `0.6` |
| `specularStrength` | `float` | Cường độ highlight | `0.8` |
| `glassOpacity` | `float` | Alpha của lớp kính | `1.0` |
| `edgeThickness` | `float` | Độ rộng bezel tương đối; khi `edge_thickness_px > 0` host đổi sang tỉ lệ pixel | `0.06`; `edge_thickness_px` mặc định `0.0` |
| `invBezelWidthPx` | `float` | `1 / (edgeThickness * minDim)`, host tính sẵn | Tính per-draw, không có config riêng |
| `tintColor` | `vec3` | Màu tint lấy từ RGB packed color | RGB của `0x8899aa22` |
| `tintAlpha` | `float` | Alpha của tint lấy từ byte thấp của packed color | `0x22 / 255` từ `0x8899aa22` |
| `lensDistortion` | `float` | Cường độ center dome lens; contour variant tắt dome | `0.5` |
| `lensMaxPx` | `float` | Giới hạn displacement dome: `lensDistortion * minDim * 0.006` | Tính per-draw |
| `brightness` | `float` | Nhân độ sáng theo theme | Dark `0.82`; light `1.12` |
| `contrast` | `float` | Contrast quanh midpoint 0.5 | Dark `0.90`; light `0.92` |
| `saturation` | `float` | Mức saturation nền | Dark `0.80`; light `0.85` |
| `vibrancy` | `float` | Tăng saturation có chọn lọc | Dark `0.15`; light `0.12` |
| `vibrancyDarkness` | `float` | Giảm vibrancy theo độ tối | `0.0` ở cả hai theme |
| `adaptiveDim` | `float` | Giảm vùng sáng theo luminance | Dark `0.4`; light `0.0` |
| `adaptiveBoost` | `float` | Nâng vùng tối theo luminance | Dark `0.0`; light `0.4` |
| `roundingPower` | `float` | Power của hình rounded corner lấy từ shape/decoration | Host/Hyprland per-draw, không phải material Lua key |
| `invRoundingPower` | `float` | Nghịch đảo `roundingPower` | Host tính per-draw |
| `refractionFlow` | `float` | Trộn hướng inward với hướng dọc cạnh; contour variant không dùng | `0.0` |
| `refractionSpread` | `float` | Điều khiển cửa sổ falloff rim-only của upstream exponential profile | `1.0` |
| `fresnelTint` | `float` | Trộn màu Fresnel theo màu nền | `0.0` |
| `bevelStrength` | `float` | Cường độ bevel highlight | `0.0` |
| `bevelSize` | `float` | Độ rộng bevel theo logical px, nhân monitor scale | `6.0` |
| `monitorScale` | `float` | Tỉ lệ màn hình dùng đổi logical px sang framebuffer px | Monitor runtime; renderer fallback `1.0` khi không có scale hợp lệ |
| `fresnelColor` | `vec3` | Màu Fresnel | RGB trắng từ `0xffffff00` |
| `fresnelColorAlpha` | `float` | Alpha của Fresnel color | `0` từ byte thấp `0xffffff00` |
| `bevelColor` | `vec3` | Màu bevel | RGB trắng từ `0xffffff00` |
| `bevelColorAlpha` | `float` | Alpha của bevel color | `0` |
| `bevelTint` | `float` | Trộn bevel với hue nền | `0.0` |
| `bevelAngle` | `float` | Hướng sáng bevel, độ theo chiều kim đồng hồ; 0 là từ trên | `315.0` |
| `bevelShadow` | `float` | Mức tối ở phía xa nguồn sáng | `0.0` |
| `specularAngle` | `float` | Hướng gradient specular | `0.0` |
| `maskTex` | `sampler2D` | Bản render bề mặt layer dùng làm alpha mask | Chỉ bind cho layer có mask |
| `useMask` | `int` | Bật đường composite mask | 1 khi layer dùng mask, 0 cho window |
| `maskUVOffset` | `vec2` | Offset UV để đọc mask | Tính per-draw |
| `maskUVScale` | `vec2` | Tỉ lệ UV của mask | Tính per-draw |
| `maskAlphaThreshold` | `float` | Ngưỡng alpha để bật glass ở alpha-mask mode | Host/per-layer; không có material default trong shader |
| `maskCoverage` | `float` | Độ dài alpha ramp sau threshold; 0 nghĩa là mask cứng | `0` nghĩa vụ theo comment shader |
| `maskMode` | `int` | `0` alpha threshold, `1` protocol region | Host chọn theo mask mode |
| `regionRectCount` | `int` | Số hình chữ nhật blur region, tối đa 64 | `0..64`; 0 nếu không có rect |
| `regionRects[64]` | `vec4[64]` | Mỗi rect gồm offset XY và size ZW, tọa độ pixel local | Host bind; không có giá trị material mặc định |
| `glassBoxOffsetPx` | `vec2` | Offset hình kính trong box được vẽ | `(0,0)` nếu cả box là kính |
| `glassBoxSizePx` | `vec2` | Kích thước hình kính thực | `fullSize` nếu cả box là kính |
| `glassUVScale` | `vec2` | Đổi UV box sang UV hình kính | `(1,1)` nếu cả box là kính |
| `glassUVOffset` | `vec2` | Offset UV hình kính | `(0,0)` nếu cả box là kính |
| `sampleUVOffset` | `vec2` | Offset map từ box UV sang texture sample UV | `(0,0)` nếu sample phủ box |
| `sampleUVScale` | `vec2` | Scale map sample UV | `(1,1)` nếu sample phủ box |
| `lensHeightPx`* | `float` | Chiều cao lens edge trong framebuffer px | `edge_height=0` mặc định |
| `lensReflection`* | `float` | Cường độ phản chiếu của rim lens | `fresnel_reflection=0` mặc định |
| `lensReflectionReachPx`* | `float` | Khoảng cách sample phản chiếu | Hằng số host `0.8 * SAMPLE_PADDING_PX` |
| `focusLight`* | `float` | Cường độ focus light sau fade | `0.0` mặc định |
| `focusLightColor`* | `vec3` | Màu focus light | RGB trắng từ `0xffffff00` |
| `focusLightColorAlpha`* | `float` | Alpha màu focus | `0` |
| `frostTex`* | `sampler2D` | Bản backdrop blur thêm, nửa kích thước | Chỉ bind khi frost bật |
| `frostAmount`* | `float` | Mức frost sau easing | `frost=0.0` mặc định |
| `contourTex`* | `highp sampler2D` | Distance field: R là signed distance px (âm bên trong), GB gradient | Field dựng từ render layer |
| `contourUVScale`* | `vec2` | Scale UV layer sang distance field | Tính từ kích thước field |
| `contourReferencePx`* | `float` | Mẫu số để tính bezel trong contour mode | Tính từ kích thước layer/scale |
| `contourReachPx`* | `float` | Tầm của distance field, hiệu ứng fade trước giới hạn | Tính từ plan contour |

`*` Các uniform này chỉ tồn tại trong build khi feature tương ứng được compile (`LENS_EDGE`, `FOCUS_LIGHT`, `FROST`, `CONTOUR`); xem pinned `Shaders.hpp:108–149`.

Các giá trị config host có căn cứ tại `src/BuiltInPresets.hpp:23–60`. Hằng số compile-time của feature lens là `LENS_IOR = 1.5`, `LENS_DISPERSION = 0.25`, `LENS_REFERENCE_STRENGTH = 0.6` (`Shaders.hpp:113–117`). Chúng không phải Lua uniform knobs.

### Blur pass và contour-build passes

| Shader/pass | Uniforms (type — ý nghĩa) | Default |
|---|---|---|
| `gaussianblur.frag` | `tex` (`sampler2D`, input); `direction` (`vec2`, trục ngang/dọc theo texel); `blurRadius` (`float`, bán kính kernel px) | Bind từ host. `blurRadius = blur_strength * 12 / downscale`; `blur_iterations` mặc định 3, host clamp 1–5 (`GlassLayerSurface.cpp:436–452`, `BuiltInPresets.hpp:30–31`) |
| `contourseed.frag` | `tex` (`sampler2D`, render layer/alpha); `boxOffsetPx`, `boxSizePx`, `sourceSizePx` (`vec2`, kích thước/vị trí vùng); `divisor` (`float`, 1/2/4/8 px mỗi texel); `threshold` (`float`, alpha threshold) | Input do contour builder bind; không có material defaults (`Shaders.hpp:836–841`) |
| `contouredt.frag` | `tex` (`sampler2D`); `fieldSize` (`vec2`, texel); `direction` (`vec2`, trục EDT); `reachTexels` (`int`); `resolveSigned` (`int`, pass cuối); `texelPx`, `reachPx` (`float`) | Tính từ contour plan (`Shaders.hpp:883–889`) |
| `contoursmooth.frag` | `tex` (`sampler2D`); `fieldSize`, `direction` (`vec2`); `radius` (`int`, taps mỗi phía); `negHalfInvSigmaSq` (`float`, hệ số Gaussian) | Tính từ contour plan (`Shaders.hpp:932–936`) |
| `contourfield.frag` | `tex` (`sampler2D`); `fieldSize` (`vec2`); `texelPx` (`float`) | Tính từ contour plan (`Shaders.hpp:963–965`) |

Blur shader đặt `samples = min(int(ceil(blurRadius)), 8)` (`Shaders.hpp:792`). Nó đọc 1 tap ở tâm, rồi ghép cặp hai offset mỗi bên thành một lần bilinear fetch; tối đa 4 cặp × 2 phía + tâm = **9 texture fetches mỗi pass/trục** (`Shaders.hpp:799–818`). Horizontal/vertical và số pass đến từ host; `blur_iterations` mặc định 3.

### Thứ tự blur/refraction và số lần sample backdrop

Trong Hyprglass, host blur backdrop **trước** khi `applyGlassEffect` chạy: `GlassLayerSurface.cpp:439–452` gọi `sampleBackground`, tính radius, rồi gọi `blurBackground`; shader mới tính offset refraction và đọc texture. Pinned upstream `Shaders.hpp:497–516` tạo `baseOffset`; dòng 551–565 cộng offset vào UV rồi gọi `sampleBlurred`. Nói chính xác: shader chính không blur từng pixel; nó **sample texture đã blur trước** tại UV đã lệch bởi refraction. Đây là khác với Shayxo: report Shayxo mô tả sample sharp tại điểm đã lệch rồi blur sau đó (`/tmp/pill-copy-shayxo-report.md:454`).

`sampleBlurred()` dùng `texture(tex, ...)` một lần cho kênh RGB bình thường (`Shaders.hpp:168–175`). Khi chromatic aberration bật ở vùng edge, nó lấy R/G/B tại ba UV riêng, tức 3 lần sample (`Shaders.hpp:555–565` trong pinned revision). Với frost, mỗi sample còn trộn `tex` và `frostTex`. Lens reflection có thể đọc thêm sample. Không có kernel blur trong `liquidglass.frag`.

Một vài điểm quan trọng của pristine upstream:

- Refraction mặc định dùng `edgeProximity` exponential; `refractionSpread` chỉ window falloff trong nhánh này (`Shaders.hpp:497–505`). Cây đã build hiện thay đoạn này bằng cylinder patch.
- `chromaticAberration` được đổi thành `chromaSpread = chromaticAberration * 0.35` (`Shaders.hpp:522–525` pinned).
- Fresnel thường là `edgeProximity * edgeProximity * fresnelStrength * 0.15` (`Shaders.hpp:676–685` pinned); không phải Schlick theo normal.
- Specular thường lấy `pow(specT, 2.0)` rồi nhân `edgeProximity² * specularStrength * 0.08` (`Shaders.hpp:704–706` pinned); power không phải config.
- Inner shadow bị hard-code `* 0.06` (`Shaders.hpp:720–721` pinned).

## 3. Mapping Lua → shader, và các tham số Shayxo

`native/hyprglass-local-optics.lua:4–16` đặt material hiện hành; `src/PluginConfig.cpp:413–445` nhận diện Lua keys; `src/GlassRenderer.cpp:573–593,629–635` bind values sang uniforms. `scripts/activate-glass.py` chỉ kiểm tra hash, ABI, plugin inventory rồi load/reload (`:16–66`); nó **không** ánh xạ tham số shader.

| Key hiện có trong Lua | Uniform/control phía plugin | Ghi chú |
|---|---|---|
| `refraction_strength` | `refractionStrength` | Scale displacement; hiện tại `0.55`, shader cylinder cũng dùng `*50px` để đổi độ lớn |
| `refraction_flow` | `refractionFlow` | Trộn hướng; bị bỏ qua trong contour variant; Lua hiện `1.0` |
| `refraction_spread` | `refractionSpread` | Upstream điều khiển rim window; cylinder patch hiện làm giá trị này inert |
| `edge_thickness` | `edgeThickness`, `invBezelWidthPx` | Tỉ lệ theo reference px; hiện `.05` |
| `lens_distortion` | `lensDistortion`, `lensMaxPx` | Center dome bị `#ifndef HYPRGLASS_FEATURE_CONTOUR` tắt trong contour mode; Lua `.6` |
| `blur_strength` | Host blur trước shader; **không có uniform material** | Radius `strength * 12 / downscale`; hiện Lua `.25`, tức 3px khi downscale=1, chứ không phải 0 |
| `chromatic_aberration` | `chromaticAberration` | Có knob nhưng scaling/formula khác Shayxo; Lua `.04` |
| `fresnel_strength` | `fresnelStrength` | Có knob nhưng công thức Hyprglass khác; Lua `.10` |
| `specular_strength` | `specularStrength` | Có knob về gain; Lua `.50` |
| `bevel_strength` | `bevelStrength` | Cường độ viền bevel; Lua `.45` |
| `bevel_size` | `bevelSize` | logical px, host nhân scale; Lua `3.0` |
| `bevel_tint` | `bevelTint` | Lua `0.0` |
| `bevel_shadow` | `bevelShadow` | Lua `0.0` |
| `bevel_angle` | `bevelAngle` | Lua `315.0` |
| `noise_strength` | `noiseStrength` | Lua `0.0` |
| `glass_opacity` | `glassOpacity` | Lua `1.0` |
| `tint_color` | `tintColor` + `tintAlpha` | Packed `0xRRGGBBAA`; Lua `0xffffff00` trong suốt |
| `brightness` | `brightness` | Lua `1.0`, áp dụng cả dark/light override |
| `contrast` | `contrast` | Lua `1.0` |
| `saturation` | `saturation` | Lua `1.0` |
| `vibrancy` | `vibrancy` | Lua `0.0` |
| `vibrancy_darkness` | `vibrancyDarkness` | Lua `0.0` |
| `adaptive_dim` | `adaptiveDim` | Lua `0.0` |
| `adaptive_boost` | `adaptiveBoost` | Lua `0.0` |

Các config `enabled`, `manage_window_blur`, `subsurfaces`, `layers.enabled`, `preset`, `mask_mode` chọn phạm vi/tuyến xử lý; chúng không phải material optics uniform. `mask_mode = "contour"` được gán riêng cho `computer-use-indicator` tại `native/hyprglass-local-optics.lua:26–33`.

### Đối chiếu Chrome Legacy của Shayxo

Preset target và Legacy-vs-Measured được ghi trong `/tmp/pill-copy-shayxo-report.md:23–32,410–457`. Đây là danh sách target người dùng yêu cầu:

| Shayxo Chrome parameter | Khả năng biểu đạt trong Hyprglass hiện có | Phân loại |
|---|---|---|
| band `14 dp` | `edge_thickness_px = 14` là control tương đương về độ rộng bezel, được nhân monitor scale. Key được host nhận diện (`PluginConfig.cpp:422`) nhưng hiện không có trong Lua profile. `edge_thickness = .05` hiện chỉ cho khoảng 3.3px khi reference=66, scale=1. | Có control trực tiếp, cần đặt pixel key |
| depth `9 dp` | Không có tham số depth quang học tách biệt. `refraction_strength` chỉ tăng/giảm biên độ; không tái tạo `uRefractDepth`. | **NONE** |
| blur `0` | `blur_strength = 0` là knob trực tiếp ở host; shader không có uniform blur strength. | Có control trực tiếp; **profile hiện tại sai target** (`.25`) |
| IOR `1.5` | Không có knob Lua/uniform IOR. Có literal `1.5` trong cylinder patch và hằng số lens feature, nhưng không thể đổi bằng Lua. | **NONE** dạng chỉnh được; hằng số hiện tại tình cờ bằng 1.5 |
| `bevelPower = 2` | Không có `bevelPower`. `roundingPower` là power hình outline từ Hyprland, không điều khiển Shayxo bevel profile. | **NONE** |
| `cornerPower = 2` | `roundingPower` uniform có cùng số khả dĩ nhưng đến từ Hyprland shape, không phải local Lua material; contour mode đo silhouette raster thay vì áp power này. | Không có knob Lua tương đương thực sự |
| dispersion `0.07` | `chromatic_aberration` có gain knob; Hyprglass áp hệ số riêng (`*0.35` ở shader thường, hoặc dispersion constant khác ở lens-edge). | Có knob tương tự, **không cùng công thức** |
| specular `0.55` | `specular_strength` điều khiển gain trực tiếp; Lua hiện `.50`. | Có |
| specularPower `6` | Hyprglass hard-code `pow(specT, 2.0)` ở upstream. | **NONE** |
| counterLight `0.35` | Không có counter-light lobe/uniform. | **NONE** |
| edgeLight `1` | Không có outer edge line riêng tương đương trong material keys. | **NONE** |
| bevelPeak `0` | Không có tham số đỉnh bevel riêng. | **NONE** |
| innerShadow `0.07` | Có inner shadow nhưng hard-code hệ số `.06`, không phải knob; profile không đổi được bằng Lua. | **NONE** |
| legibility `0.6` | Không có material control tương ứng. `brightness`/`contrast`/`saturation` là tone controls khác nghĩa. | **NONE** |
| Fresnel `0.10` | `fresnel_strength` là gain knob trực tiếp; công thức Hyprglass dùng edge exponential², không dùng đúng Schlick/normal của Shayxo Legacy. | Có gain knob, **không cùng công thức** |
| bevel `3 dp` | `bevel_size = 3` điều khiển độ rộng đường bevel; Lua hiện đã đặt `3.0`. | Có |

Vậy Lua-only có thể đặt band, blur, strength knobs, bevel width và tone controls. Nó không thể biểu đạt Snell bevel/IOR có thể chỉnh, depth 9dp, Legacy normal/dome/dispersion chính xác, specular power 6, counter light, edge line, bevel peak, inner shadow gain hay legibility. Ngoài ra, order blur-after-refraction của Shayxo trái với pipeline hiện tại blur-before-refraction. Các phần này cần GLSL/C++ shader change.

## 4. Manifest: refresh, guard, và lệnh tiếp theo

Đã đọc toàn bộ `scripts/refresh-visuals-manifest.py` và `scripts/check-visuals-manifest.py`.

### `refresh-visuals-manifest.py`

- Mặc định đọc/ghi **repo** `native/visuals.json` (`:41–44`), và dùng `native/hyprglass-local-optics.lua` làm optics profile.
- Xác minh plugin mới đã cài trong `<installed-root>/plugins`, tên chứa SHA-256 và bytes khớp hash (`:55–73`). Mặc định installed root là `~/.local/share/agent-computer-use`.
- Tính SHA-256 của plugin .so và Lua profile (`:71–72`, `:146–148`), đọc runtime ABI, kiểm tra cursor-guard .so, cursor profile và cursor tree nếu theme trỏ tới thư mục được quản lý (`:149–153`).
- Chỉ ghi đúng hai field: `library` và `profile_sha256`; các field còn lại được kiểm tra rồi giữ nguyên (`:121–125`, `:163–166`). Nó không hash `Shaders.hpp`/patch riêng; shader được nhận dạng qua SHA của `.so`.
- Không build/cài/load/unload/reload plugin (`docstring :11–17`).

### `check-visuals-manifest.py`

Guard này chỉ so SHA-256 của Lua profile với `profile_sha256` trong manifest (`:14–15`, `:47–56`). Nó không kiểm tra artifact bytes hoặc source shader. Khi mismatch, nó in remediation chính xác (`:62–67`): refresh, check, sync, sync `--check`, rồi mới commit.

Manifest repo hiện là `native/visuals.json`; file này bị `.gitignore:47` ignore. `sync-installed.py:22–32` vẫn đưa nó vào generated managed files. `_validate_manifest(root, installed)` đọc `root/native/visuals.json` và xác minh cả library hashes lẫn Lua hash (`sync-installed.py:446–472`); sync còn yêu cầu manifest repo và installed giống hệt (`:807–811`). Installed copy nằm tại `~/.local/share/agent-computer-use/native/visuals.json`. **Không sửa `native/visuals.json` bằng tay**; để refresh cập nhật repo bản local, sau đó guarded sync cập nhật/kiểm tra installed tree.

### Lệnh sau khi build và install

Từ repo root, sau khi có artifact mới:

```sh
NEW_SO="$(python3 scripts/install-glass.py ~/computer-use-handoff/backend/hyprglass-1.1.1/hyprglass.so ~/.local/share/agent-computer-use/plugins)"
python3 scripts/refresh-visuals-manifest.py "$NEW_SO"
python3 scripts/check-visuals-manifest.py
python3 scripts/sync-installed.py
python3 scripts/sync-installed.py --check
```

`install-glass.py:10–20,28–42` tạo file cài hash-immutable và không ghi đè file đã có khác bytes. Refresh chỉ chạy **sau** install vì nó yêu cầu .so immutable đã nằm trong thư mục plugins.

## 5. Regression suite và các test kính

### Chạy suite / baseline

`docs/testing.md:5–7` ghi suite là Python `unittest` với lệnh chính xác:

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
```

Baseline có sẵn trong `/tmp/hyprglass-fix-f3-codex.log:8028`: `Ran 111 tests in 15.325s` và `OK`. Các lần baseline lặp ở dòng 8104, 8194, 8381 chạy 15.293–15.490 giây. Đây là log cũ, **không phải test chạy trong recon này**. `docs/testing.md:17–31` nói suite trộn native C thật, fake Wayland, Node thật/fake CDP và mock; test patch applicability cần `CU_HYPRGLASS_SOURCE` mới không skip.

### Test optics/build

| File | Hợp đồng hiện tại | Cần cập nhật? |
|---|---|---|
| `tests/test_glass_optics_contract.py:1–10,21–26,53–75,87–149` | Mô hình capsule cũ; IOR `1.45`, depth `edge_thickness * min(pill)`, bound giải tích, zero giữa/lùi sâu, mirror symmetry, continuity. Test patch applicability `:152–178` đòi pin cũ `84c1a5…` và tìm `capsuleNormal` / `1.0 / 1.45`. | Có. Chuyển contract sang Legacy Snell của Shayxo: IOR1.5, depth9, band14 và vị trí sample/blur mới. Patch-application test phải pin 03a57c4 và kiểm tra patch mới. |
| `tests/test_glass_lighting_contract.py:1–10,17–22,51–67,149–185` | Numeric model cho capsule cũ: IOR1.45, Schlick `pow(...,5)`, specular `pow(...,24)` và scale `.32`, cùng kiểm tra shader patch strings. | Có. Target có specular power6, counter light, edge light và Fresnel/formula khác. |
| `tests/test_glass_dome_contract.py:1–10,18–21,36–53,65–97` | Mô hình center-dome Hyprglass từ `lens_distortion`, trên trục pill; không kiểm tra GPU pixels/blur/visual fidelity. | Có nếu Shayxo dome field thay dome Hyprglass; viết assertion cho dome field Legacy và scale/aspect behavior. |
| `tests/test_glass_ripple_contract.py:1–38` | Assert exponential capsule rim + ripple constants, bound, axis fade trong `hyprglass-capsule.patch`. Shayxo Legacy static Chrome không có law ripple này. | Có: bỏ/đổi contract cũ hoặc ghi rõ model ripple không nằm trong port; không để test cũ đại diện cho optics mới. |
| `tests/test_glass_build.py:1–2,67–94,108–189` | Mock subprocess; xác nhận pin, dirty guards, patch apply trước `make`, version stamp và `--allow-dirty`; không build thật. | Có. Thêm assertion cho thứ tự áp dụng patch GLSL riêng; giữ nguyên pin/dirty/failure-before-make. |
| `tests/test_glass_local_optics.py:9–42` | C++ patch chỉ scope indicator, geometry/finite checks, sentinel; Lua mask scope; no plate/noise. Dòng 19 bắt buộc local-optics patch không chứa `src/Shaders.hpp`. | Giữ nếu shader nằm trong patch file riêng và C++ patch giữ scope; cập nhật các giá trị Lua nếu assertion cụ thể đổi. |
| `tests/glass_optics.py:1–17,25–31,76–120` | Diagnostic tùy chọn, không tự chạy như unittest; cần PIL/numpy và 3 ảnh capture. Đo lag ở fixture 1280×720 cho offset cưỡng bức 8/16px; không xác nhận Shayxo visual fidelity. | Giữ nếu protocol/capture fixture không đổi; không dùng thay shader contract. |

Các test plumbing cần tiếp tục pass sau đổi optics/manifest: `tests/test_install_glass.py` (immutable SHA install), `tests/test_activate_glass.py` (ABI/hash/plugin inventory; RPC mocked), `tests/test_refresh_visuals_manifest.py` (refresh checks/hash/field preservation), `tests/test_check_visuals_manifest.py` (Lua pin/pre-commit guard), `tests/test_sync_installed.py` (source/installed manifest, hashes và ledger). Đổi formula không phải lý do sửa các hợp đồng này.

## 6. Pill geometry, monitor scale và contour distance

`native/indicator.c:18–24` khai báo `PILL_WIDTH=288`, `PILL_HEIGHT=38`, `SURFACE_WIDTH=320`, `SURFACE_HEIGHT=66`; pill local position là left=16, top=16 (`:20–24`). Rounded region lấy radius `min(PILL_HEIGHT/2, pw/2)` (`:118`) và chỉ scan 38 pill rows (`:119–124`). Surface luôn có chiều cao 66 (`:391–395`).

Contour mode không lấy cạnh của layer rectangle làm mép kính. `src/Contour.hpp:15–18` mô tả signed-distance field dựng từ render của layer; `Shaders.hpp:142–149` định nghĩa R là signed distance đến outline (âm phía trong), GB là gradient. Shader đọc `contourSample.r` thành `cornerSdf` (`:382–385`); trong contour branch `bevelSdf = cornerSdf` và `edgeProximity` suy từ signed distance (`:434–440` pinned source). Cylinder patch đặt `depth = -bevelSdf` (`native/hyprglass-cylindrical-bottle.patch:60–66`). Do đó distance đo từ đường viền pill đã render; phần giữa pill cách outline xấp xỉ 19 logical px theo chiều cao 38.

`GlassRenderer.cpp:561–566` lấy scale từ `monitor->m_scale` (fallback 1.0 nếu không có scale dương). `native/hyprglass-cylindrical-bottle.patch:50–58` ghi rõ phép tính 19px dựa trên pill38/layer66, monitor scale1, và shader dùng `19.0 * monitorScale`. Không xác minh được scale đang chạy trên máy: `hyprctl -j monitors` trong shell này không trả JSON. Vì vậy quy đổi chính xác là theo scale ký hiệu `s`:

| Đại lượng | logical px | framebuffer px |
|---|---:|---:|
| pill height | 38 | `38*s` |
| nửa chiều cao/rim → center line | 19 | `19*s` |
| layer height | 66 | `66*s` |
| Shayxo band | 14 dp | `14*s` |
| Shayxo optical depth | 9 dp | `9*s` |

Ở scale1 band14 vừa nằm trong bán kính pill19. Current profile `edge_thickness=.05` trên contour reference66 cho bezel ~3.3px ở scale1; nó không phải band14. Dùng `edge_thickness_px=14` để diễn đạt độ rộng band, còn depth9 vẫn cần shader uniform/code mới.

## KHUYẾN NGHỊ

Tạo patch shader riêng, ví dụ `native/hyprglass-shayxo-legacy.patch`, và sửa `scripts/build-glass.py` để áp patch đó **sau** `hyprglass-local-optics.patch`. Giữ patch local-optics riêng cho C++: `tests/test_glass_local_optics.py:19` khóa ranh giới này, build script hiện chỉ biết áp một patch, và Lua không biểu đạt được Legacy Snell, depth, blur-after-refraction, các lobe chiếu sáng/power còn thiếu. Cập nhật Lua cho các knob có thật (band14, blur0, chroma.07, specular.55, Fresnel.10, bevel size3) nhưng không giả vờ các knob đó thay thế công thức GLSL.

Thứ tự triển khai và xác minh sau khi implementer đã sửa patch/script/profile/test:

1. Build pinned tree có cả hai patch:
   ```sh
   python3 scripts/build-glass.py ~/computer-use-handoff/backend/hyprglass-1.1.1 --local-optics --allow-dirty
   ```
2. Install artifact hash-immutable:
   ```sh
   NEW_SO="$(python3 scripts/install-glass.py ~/computer-use-handoff/backend/hyprglass-1.1.1/hyprglass.so ~/.local/share/agent-computer-use/plugins)"
   ```
3. Refresh và kiểm tra manifest; không chỉnh JSON bằng tay:
   ```sh
   python3 scripts/refresh-visuals-manifest.py "$NEW_SO"
   python3 scripts/check-visuals-manifest.py
   ```
4. Chạy test tập trung, rồi toàn suite:
   ```sh
   python3 -m unittest discover -s tests -p 'test_glass_*.py'
   python3 -m unittest discover -s tests -p 'test_*visuals_manifest.py'
   python3 -m unittest discover -s tests -p 'test_*.py'
   ```
5. Đồng bộ installed tree và kiểm lại:
   ```sh
   python3 scripts/sync-installed.py
   python3 scripts/sync-installed.py --check
   ```
6. Stage source/test đã sửa, commit, push (không stage `native/visuals.json`, file này local/generated/ignored):
   ```sh
   git add native/hyprglass-shayxo-legacy.patch native/hyprglass-local-optics.lua scripts/build-glass.py tests/test_glass_build.py tests/test_glass_optics_contract.py tests/test_glass_lighting_contract.py tests/test_glass_dome_contract.py tests/test_glass_ripple_contract.py tests/test_glass_shayxo_contract.py
   git commit -m "fix: port shayxo legacy glass optics"
   git push origin main
   ```

Không có bước nào ở trên được chạy trong recon này.
