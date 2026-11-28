# Báo cáo D2 — hợp đồng test Shayxo Legacy

## Thông tin lượt làm

- Model theo yêu cầu: `gpt-6-luna`
- Reasoning effort theo yêu cầu: `max`
- Bắt đầu (Asia/Ho_Chi_Minh): `2026-11-18 14:08:25`
- Hoàn tất xác minh test (Asia/Ho_Chi_Minh): `2026-11-18 14:39:03`
- Test mới: `tests/test_glass_shayxo_contract.py`
- Phạm vi D2: test và báo cáo này. Không sửa shader, Lua, patch, build script, manifest, hoặc cấu hình cài đặt.

## Va chạm và cách xử lý

Kiểm tra bắt buộc ban đầu cho thấy `tests/test_glass_shayxo_contract.py` chưa tồn tại. Trong lúc bắt đầu ghi test, file này xuất hiện với nội dung hợp đồng của worker W3. Tôi đã đọc toàn bộ file hiện có rồi mở rộng, giữ nguyên mọi test của file; không ghi đè.

Trong cùng lượt, W3 sửa các file `tests/test_glass_optics_contract.py`, `tests/test_glass_lighting_contract.py`, `tests/test_glass_dome_contract.py`, `tests/test_glass_ripple_contract.py` và `tests/test_glass_build.py`. Tôi đọc lại toàn bộ phiên bản mới nhất trước khi quyết định không sửa chồng các phần đó. Các thay đổi không phải test của W3 vẫn đang hiện diện ở Lua, build script và patch Shayxo.

## Test mới và hợp đồng được thêm

File mới/được mở rộng là `tests/test_glass_shayxo_contract.py`. File này kiểm tra các giá trị task, công thức Snell, phần chuyển tiếp, epsilon rộng, fade ở trục giữa, dome weight cho pill 288×38, lấy mẫu sharp sau offset, blur bằng 0, và danh sách literal GLSL có citation. Nếu patch hoặc build order thiếu, test báo `shayxo port not landed: ...` bằng assertion; không skip hoặc crash khi import.

Danh sách đầy đủ test trong file:

1. `ShayxoNoInventedConstants.test_shader_literals_and_bound_profile_values_are_traced`
2. `ShayxoPortContract.test_axis_fade_tends_to_zero_without_a_direction_flip_seam`
3. `ShayxoPortContract.test_bend_formula_checkpoints_and_non_unit_peak`
4. `ShayxoPortContract.test_blur_zero_uses_sharp_rgb_and_detail_samples`
5. `ShayxoPortContract.test_dispersion_and_blue_sampling_bound`
6. `ShayxoPortContract.test_legacy_pad_is_12_6_pixels`
7. `ShayxoPortContract.test_lighting_constants_and_powers`
8. `ShayxoPortContract.test_outer_inner_fade_is_flat_then_c1_fades_without_midband_peak`
9. `ShayxoPortContract.test_patch_exposes_single_source_snell_law_and_no_capsule_ripple`
10. `ShayxoPortContract.test_patch_translates_glsl_descending_smoothstep_and_omits_wide_copy`
11. `ShayxoPortContract.test_pill_dome_weight_is_zero`
12. `ShayxoPortContract.test_selected_task_values_are_bound`
13. `ShayxoPortContract.test_shader_has_the_rim_snell_normalization_and_both_fades`
14. `ShayxoPortContract.test_snell_values_match_the_verified_checkpoints`
15. `ShayxoPortContract.test_transparent_tint_no_preblur_and_no_mirror`
16. `ShayxoPortContract.test_wide_epsilon_and_axis_fade_are_in_the_shader`
17. `ShayxoPortContract.test_zero_blur_profile_rim_sharp_and_after_push_sample_order`

### Điểm không nhất quán trong yêu cầu về bend

Công thức được yêu cầu mirror là tỉ số Snell chuẩn hóa nhân với inner fade, axis fade và guard 1.5 px. Công thức đó không tạo tổng `bend = 1` xuyên outer band: tại depth=1.5 px giá trị khoảng `0.508922`; dense scan trong test optics hiện có cho đỉnh cục bộ khoảng `0.515` ở 1.3983 px. Chỉ riêng hệ số `1 - smoothstep(0.75, 1.0, e)` bằng 1 khi `e <= 0.75`. Tôi đã hỏi cần ưu tiên cách hiểu nào; chưa nhận được trả lời trước khi hoàn tất. Vì công thức đầy đủ và yêu cầu C1 không thể đồng thời cho tổng bend bằng 1, test theo công thức, kiểm tra riêng hệ số outer fade bằng 1, và ghi rõ khác biệt trong header. Không đưa assertion sai `bend == 1` vào.

Các số dẫn xuất được kiểm tra gồm lens 7.65 px, blue bound 8.1855 px, pad 12.6 px, epsilon 4.2 px, counterPow 9.6, Fresnel `f0=0.04`, `rimSharp=(1-e)^2`, và domeWeight 0. Các tham số task và bảng lệch so với GlassStyle.Chrome thật được ghi ở header file test.

### Bộ dò hằng số

Allowlist trong test ánh xạ từng literal GLSL được thêm vào đúng một nguồn (`report §...`, `design §...`, hoặc task value). Parser bỏ comment và dòng diff bị xóa; nó giữ số dòng gốc của patch để báo literal chưa có nguồn. Các binding Lua được kiểm riêng theo tên để phát hiện `.25` blur, `.04` chroma, `.50` specular từ preset cũ dù cùng literal có thể hợp lệ ở chỗ khác trong shader. Phần `0.25` của legibility vẫn được cho phép vì report §3.10 nêu đúng hệ số này.

Các quyết định biên trong allowlist: `0.25` chỉ được cho phép trong công thức legibility nguồn, trong khi `blur_strength=0.25` bị từ chối theo tên binding; `0.90` cho tint adaptivity là giá trị Chrome thật được ghi trong design §2; `0.70`, `0.34` và Oklab/luma coefficients lấy từ report/design đã nêu cạnh từng literal; `3.0` xuất hiện trong phép tính mean `1/3` của tone helper và đồng thời là bevel 3 dp; các số `0.002`, `0.998`, `1e-4`, `1e-5`, `1e-3` là clamp/denominator floors được source trích dẫn. Không có wildcard allow cho số “trông giống hằng cấu trúc”.

## Các test hiện có

- `tests/test_glass_optics_contract.py` — W3 thay mô hình capsule/Ior 1.45 bằng bevel slope + Snell IOR 1.5, band 14, bend mới, checkpoints và kiểm tra C1; applicability test dùng pin `03a57c4…`. Test ghi rõ total bend không bằng 1.
- `tests/test_glass_lighting_contract.py` — W3 thay model Fresnel/specular cũ bằng Schlick, lobe power 6/9.6, edge line 2 px, inner line và các task gains.
- `tests/test_glass_dome_contract.py` — W3 thay center-dome model bằng dome gate và epsilon/fade cho pill 288×38; xác nhận domeWeight bằng 0.
- `tests/test_glass_ripple_contract.py` — W3 bỏ hợp đồng ripple/exponential cũ, xác nhận một trường Snell và không có capsule ripple.
- `tests/test_glass_build.py` — W3 mở rộng mock build để kiểm tra thứ tự local-optics rồi Shayxo, dừng trước `make` nếu patch thứ hai lỗi. Không đổi pin hay `setup_instance`.
- `tests/test_glass_local_optics.py` — D2 chỉ thêm ghi chú `SUPERSEDED` vào `test_rim_fades_inside`: assertion exponential cũ không còn là luật optics; giữ nguyên code và các kiểm tra scope/geometry còn lại. Hợp đồng mới ở `test_glass_shayxo_contract.py`.
- `tests/glass_optics.py` — đã đọc hết, không đổi vì đây là diagnostic ảnh synthetic cần file capture ngoài repo, không phải mô hình shader hay unittest.

Tổng file test chịu ảnh hưởng: 1 file mới/được mở rộng + 6 file test hiện có. Năm file test optics/build trong danh sách trên đã được W3 sửa trong lúc D2 làm việc; D2 chỉ sửa ghi chú ở local-optics.

## Chạy kiểm tra

### `py_compile`

Lệnh cuối cùng chạy thành công, exit code 0, không có output:

```text
python3 -m py_compile tests/test_glass_shayxo_contract.py tests/test_glass_optics_contract.py tests/test_glass_lighting_contract.py tests/test_glass_dome_contract.py tests/test_glass_ripple_contract.py tests/test_glass_local_optics.py tests/test_glass_build.py
```

### Bộ test kính tập trung

Lệnh cuối cùng chạy:

```text
python3 -m unittest discover -s tests -p 'test_glass_*.py' -v
```

Output nguyên văn:

```text
test_allow_dirty_bypasses_initial_dirt_reaches_make (test_glass_build.GlassBuild.test_allow_dirty_bypasses_initial_dirt_reaches_make) ... ok
test_apply_failure_stops_before_make (test_glass_build.GlassBuild.test_apply_failure_stops_before_make) ... build-glass: commit=03a57c4451b4abee38feda2ffb725f55ecc0f2fd initial_dirty=False allow_dirty=False
build-glass: local-optics patch application failed: patch application failed
ok
test_clean_fresh_apply_stamps_build_dirty_true (test_glass_build.GlassBuild.test_clean_fresh_apply_stamps_build_dirty_true) ... ok
test_dirty_tracked_initial_refuses_by_default (test_glass_build.GlassBuild.test_dirty_tracked_initial_refuses_by_default) ... ok
test_local_optics_is_required_before_source_access (test_glass_build.GlassBuild.test_local_optics_is_required_before_source_access) ... ok
test_prepatched_dirty_rerun_needs_flag (test_glass_build.GlassBuild.test_prepatched_dirty_rerun_needs_flag) ... ok
test_real_git_untracked_visible_despite_show_untracked_no (test_glass_build.GlassBuild.test_real_git_untracked_visible_despite_show_untracked_no) ... ok
test_second_patch_failure_stops_before_make (test_glass_build.GlassBuild.test_second_patch_failure_stops_before_make) ... ok
test_second_status_failure_fails_before_make (test_glass_build.GlassBuild.test_second_status_failure_fails_before_make) ... ok
test_stamps_include_pinned_commit_value (test_glass_build.GlassBuild.test_stamps_include_pinned_commit_value) ... ok
test_status_failure_fails_before_make (test_glass_build.GlassBuild.test_status_failure_fails_before_make) ... ok
test_stdout_stamps_contain_all_fields (test_glass_build.GlassBuild.test_stdout_stamps_contain_all_fields) ... ok
test_successful_apply_then_make (test_glass_build.GlassBuild.test_successful_apply_then_make) ... ok
test_untracked_only_initial_refuses_by_default (test_glass_build.GlassBuild.test_untracked_only_initial_refuses_by_default) ... ok
test_actual_pill_band_stops_below_dome_threshold (test_glass_dome_contract.ShayxoLegacyDomeContract.test_actual_pill_band_stops_below_dome_threshold) ... ok
test_long_pill_aspect_alone_does_not_enable_dome (test_glass_dome_contract.ShayxoLegacyDomeContract.test_long_pill_aspect_alone_does_not_enable_dome) ... ok
test_refraction_uses_sdf_depth_and_wide_epsilon_normal (test_glass_dome_contract.ShayxoLegacyDomeContract.test_refraction_uses_sdf_depth_and_wide_epsilon_normal) ... ok
test_upstream_center_dome_is_removed_from_the_new_path (test_glass_dome_contract.ShayxoLegacyDomeContract.test_upstream_center_dome_is_removed_from_the_new_path) ... ok
test_wide_epsilon_axis_fade_handles_the_medial_axis (test_glass_dome_contract.ShayxoLegacyDomeContract.test_wide_epsilon_axis_fade_handles_the_medial_axis) ... ok
test_counter_lobe_power_is_9_6_for_task_values (test_glass_lighting_contract.ShayxoLegacyLighting.test_counter_lobe_power_is_9_6_for_task_values) ... ok
test_highlight_uses_the_source_oklab_helper (test_glass_lighting_contract.ShayxoLegacyLighting.test_highlight_uses_the_source_oklab_helper) ... ok
test_inner_line_uses_three_pixel_bevel_and_0_07_gain (test_glass_lighting_contract.ShayxoLegacyLighting.test_inner_line_uses_three_pixel_bevel_and_0_07_gain) ... ok
test_key_counter_and_edge_lobes_have_expected_endpoints (test_glass_lighting_contract.ShayxoLegacyLighting.test_key_counter_and_edge_lobes_have_expected_endpoints) ... ok
test_new_lighting_is_directional_and_has_no_dark_outline_constant (test_glass_lighting_contract.ShayxoLegacyLighting.test_new_lighting_is_directional_and_has_no_dark_outline_constant) ... ok
test_old_capsule_lighting_formula_is_replaced (test_glass_lighting_contract.ShayxoLegacyLighting.test_old_capsule_lighting_formula_is_replaced) ... ok
test_schlick_fresnel_matches_ior_1_5_formula (test_glass_lighting_contract.ShayxoLegacyLighting.test_schlick_fresnel_matches_ior_1_5_formula) ... ok
test_source_light_vector_and_lobe_powers_are_selected (test_glass_lighting_contract.ShayxoLegacyLighting.test_source_light_vector_and_lobe_powers_are_selected) ... ok
test_task_light_gains_are_in_the_active_lua_profile (test_glass_lighting_contract.ShayxoLegacyLighting.test_task_light_gains_are_in_the_active_lua_profile) ... ok
test_full_box_sentinel_equivalence (test_glass_local_optics.LocalOptics.test_full_box_sentinel_equivalence) ... ok
test_material_has_no_plate_or_noise (test_glass_local_optics.LocalOptics.test_material_has_no_plate_or_noise) ... ok
test_patch_scoped_to_indicator (test_glass_local_optics.LocalOptics.test_patch_scoped_to_indicator) ... ok
test_profile_scopes_region_mask_to_the_indicator (test_glass_local_optics.LocalOptics.test_profile_scopes_region_mask_to_the_indicator) ... ok
test_rim_fades_inside (test_glass_local_optics.LocalOptics.test_rim_fades_inside)
SUPERSEDED by test_glass_shayxo_contract: the old exponential fade ... ok
test_formula_bend_at_depth_checkpoints (test_glass_optics_contract.ShayxoLegacyOptics.test_formula_bend_at_depth_checkpoints) ... ok
test_formula_bend_at_e_checkpoints (test_glass_optics_contract.ShayxoLegacyOptics.test_formula_bend_at_e_checkpoints) ... ok
test_full_strength_plateau_claim_is_not_the_formula (test_glass_optics_contract.ShayxoLegacyOptics.test_full_strength_plateau_claim_is_not_the_formula) ... ok
test_patch_applies_to_fresh_pinned_upstream_when_source_is_supplied (test_glass_optics_contract.ShayxoLegacyOptics.test_patch_applies_to_fresh_pinned_upstream_when_source_is_supplied) ... skipped 'set CU_HYPRGLASS_SOURCE to a pinned hyprglass git repo to run this'
test_profile_is_finite_bounded_and_fades_to_flat_interior (test_glass_optics_contract.ShayxoLegacyOptics.test_profile_is_finite_bounded_and_fades_to_flat_interior) ... ok
test_profile_joins_are_c1 (test_glass_optics_contract.ShayxoLegacyOptics.test_profile_joins_are_c1) ... ok
test_snell_slope_and_shift_checkpoints (test_glass_optics_contract.ShayxoLegacyOptics.test_snell_slope_and_shift_checkpoints) ... ok
test_old_capsule_ripple_patch_is_not_the_active_contract (test_glass_ripple_contract.ShayxoLegacyNoRippleContract.test_old_capsule_ripple_patch_is_not_the_active_contract) ... ok
test_patch_does_not_add_a_ripple_field (test_glass_ripple_contract.ShayxoLegacyNoRippleContract.test_patch_does_not_add_a_ripple_field) ... ok
test_patch_uses_the_single_snell_displacement (test_glass_ripple_contract.ShayxoLegacyNoRippleContract.test_patch_uses_the_single_snell_displacement) ... ok
test_shader_literals_and_bound_profile_values_are_traced (test_glass_shayxo_contract.ShayxoNoInventedConstants.test_shader_literals_and_bound_profile_values_are_traced) ... ok
test_axis_fade_tends_to_zero_without_a_direction_flip_seam (test_glass_shayxo_contract.ShayxoPortContract.test_axis_fade_tends_to_zero_without_a_direction_flip_seam) ... ok
test_bend_formula_checkpoints_and_non_unit_peak (test_glass_shayxo_contract.ShayxoPortContract.test_bend_formula_checkpoints_and_non_unit_peak) ... ok
test_blur_zero_uses_sharp_rgb_and_detail_samples (test_glass_shayxo_contract.ShayxoPortContract.test_blur_zero_uses_sharp_rgb_and_detail_samples) ... ok
test_dispersion_and_blue_sampling_bound (test_glass_shayxo_contract.ShayxoPortContract.test_dispersion_and_blue_sampling_bound) ... ok
test_legacy_pad_is_12_6_pixels (test_glass_shayxo_contract.ShayxoPortContract.test_legacy_pad_is_12_6_pixels) ... ok
test_lighting_constants_and_powers (test_glass_shayxo_contract.ShayxoPortContract.test_lighting_constants_and_powers) ... ok
test_outer_inner_fade_is_flat_then_c1_fades_without_midband_peak (test_glass_shayxo_contract.ShayxoPortContract.test_outer_inner_fade_is_flat_then_c1_fades_without_midband_peak) ... ok
test_patch_exposes_single_source_snell_law_and_no_capsule_ripple (test_glass_shayxo_contract.ShayxoPortContract.test_patch_exposes_single_source_snell_law_and_no_capsule_ripple) ... ok
test_patch_translates_glsl_descending_smoothstep_and_omits_wide_copy (test_glass_shayxo_contract.ShayxoPortContract.test_patch_translates_glsl_descending_smoothstep_and_omits_wide_copy) ... ok
test_pill_dome_weight_is_zero (test_glass_shayxo_contract.ShayxoPortContract.test_pill_dome_weight_is_zero) ... ok
test_selected_task_values_are_bound (test_glass_shayxo_contract.ShayxoPortContract.test_selected_task_values_are_bound) ... ok
test_shader_has_the_rim_snell_normalization_and_both_fades (test_glass_shayxo_contract.ShayxoPortContract.test_shader_has_the_rim_snell_normalization_and_both_fades) ... ok
test_snell_values_match_the_verified_checkpoints (test_glass_shayxo_contract.ShayxoPortContract.test_snell_values_match_the_verified_checkpoints) ... ok
test_transparent_tint_no_preblur_and_no_mirror (test_glass_shayxo_contract.ShayxoPortContract.test_transparent_tint_no_preblur_and_no_mirror) ... ok
test_wide_epsilon_and_axis_fade_are_in_the_shader (test_glass_shayxo_contract.ShayxoPortContract.test_wide_epsilon_and_axis_fade_are_in_the_shader) ... ok
test_zero_blur_profile_rim_sharp_and_after_push_sample_order (test_glass_shayxo_contract.ShayxoPortContract.test_zero_blur_profile_rim_sharp_and_after_push_sample_order) ... ok

----------------------------------------------------------------------
Ran 60 tests in 0.222s

OK (skipped=1)
```

Exit code là `0`: 60 test chạy, 59 pass, 1 skip có điều kiện vì `CU_HYPRGLASS_SOURCE` chưa đặt.

### Negative control với cây cũ

Vì patch Shayxo và build order của W3 đã có mặt trong worktree, test tập trung hiện pass trên source hiện tại. Để xác minh bộ dò hằng số phân biệt được cây cũ, tôi chạy riêng cùng test scanner với patch Shayxo được mô phỏng là chưa có, patch cylindrical cũ và Lua baseline từ `HEAD`. Đây là output nguyên văn; test thất bại assertion và liệt kê literal cũ chưa có nguồn, gồm `19.0`, `4.33`, `refraction_strength=0.55`, `blur_strength=0.25`, `chromatic_aberration=0.04`, `specular_strength=0.50`:

```text
test_shader_literals_and_bound_profile_values_are_traced (shayxo_contract_negative_control.ShayxoNoInventedConstants.test_shader_literals_and_bound_profile_values_are_traced) ... FAIL

======================================================================
FAIL: test_shader_literals_and_bound_profile_values_are_traced (shayxo_contract_negative_control.ShayxoNoInventedConstants.test_shader_literals_and_bound_profile_values_are_traced)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "~/computer-use-wayland/tests/test_glass_shayxo_contract.py", line 518, in test_shader_literals_and_bound_profile_values_are_traced
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        findings,
        ^^^^^^^^^
        [],
        ^^^
        'uncited constants or old optical parameter values:\n' + '\n'.join(findings),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: Lists differ: ['line 56: 19.0 has no source citation', '[458 chars] px'] != []

First list contains 6 additional elements.
First extra element 0:
'line 56: 19.0 has no source citation'

+ []
- ['line 56: 19.0 has no source citation',
-  'line 66: 4.33 has no source citation',
-  'Lua line 9: blur_strength=0.25 is untraced; task value 0.0 (task value list: '
-  'no fine blur or pre-blur)',
-  'Lua line 10: chromatic_aberration=0.04 is untraced; task value 0.07 (task '
-  'value list: dispersion 0.07)',
-  'Lua line 11: specular_strength=0.50 is untraced; task value 0.55 (task value '
-  'list: specular 0.55)',
-  'Lua line 5: refraction_strength=0.55 is an untraced old gain; the active '
-  'shader still multiplies it by 50 px'] : uncited constants or old optical parameter values:
line 56: 19.0 has no source citation
line 66: 4.33 has no source citation
Lua line 9: blur_strength=0.25 is untraced; task value 0.0 (task value list: no fine blur or pre-blur)
Lua line 10: chromatic_aberration=0.04 is untraced; task value 0.07 (task value list: dispersion 0.07)
Lua line 11: specular_strength=0.50 is untraced; task value 0.55 (task value list: specular 0.55)
Lua line 5: refraction_strength=0.55 is an untraced old gain; the active shader still multiplies it by 50 px

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
negative_control_exit_code=1
```

### Hành vi khi thiếu patch

Mô phỏng thiếu `native/hyprglass-shayxo-legacy.patch` cho thấy test báo lỗi assertion rõ ràng, không skip/error khi import:

```text
test_selected_task_values_are_bound (shayxo_missing_artifact_control.ShayxoPortContract.test_selected_task_values_are_bound) ... FAIL

======================================================================
FAIL: test_selected_task_values_are_bound (shayxo_missing_artifact_control.ShayxoPortContract.test_selected_task_values_are_bound)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "~/computer-use-wayland/tests/test_glass_shayxo_contract.py", line 153, in setUp
    self.assertTrue(
    ~~~~~~~~~~~~~~~^
        PATCH.is_file(),
        ^^^^^^^^^^^^^^^^
        'shayxo port not landed: native/hyprglass-shayxo-legacy.patch missing',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^^
AssertionError: False is not true : shayxo port not landed: native/hyprglass-shayxo-legacy.patch missing

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
missing_artifact_exit_code=1
```

### Lỗi phát triển đã sửa

Lần `py_compile` đầu phát hiện escape thừa ở hai string build-order. Tôi sửa code rồi `py_compile` toàn bộ file test yêu cầu chạy thành công. Output lỗi đầu tiên:

```text
  File "tests/test_glass_shayxo_contract.py", line 153
    local_entry = \"('local-optics', PATCH)\"
                   ^
SyntaxError: unexpected character after line continuation character
exit_code=1
```

Lần chạy test đầu phát hiện bộ tách branch đòi `#endif` trong dòng diff được thêm, trong khi `#endif` là dòng context. Tôi đổi điểm kết thúc sang marker `float bevelPx =`; test chạy lại pass. Output lỗi đầu tiên:

```text
FAIL: test_zero_blur_profile_rim_sharp_and_after_push_sample_order (test_glass_shayxo_contract.ShayxoPortContract.test_zero_blur_profile_rim_sharp_and_after_push_sample_order)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "~/computer-use-wayland/tests/test_glass_shayxo_contract.py", line 352, in test_zero_blur_profile_rim_sharp_and_after_push_sample_order
    self.assertGreater(branch_end, marker_at, 'Legacy sharp sample branch is unterminated')
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: -1 not greater than 6198 : Legacy sharp sample branch is unterminated
```

## Full suite

Không chạy full suite theo điều kiện của task: `git status --short` lúc quyết định vẫn hiện thay đổi ngoài tests của W3:

```text
 M native/hyprglass-local-optics.lua
 M scripts/build-glass.py
?? native/hyprglass-shayxo-legacy.patch
```

Cũng có các test đang được W3 chỉnh cùng lúc. Vì vậy không thể báo tổng full-suite hoặc khẳng định không có failure mới ngoài các file kính. Khi hoàn tất báo cáo, `git status --short` vẫn hiện `M improvements/pill-shayxo-port-design.md` (tài liệu W3) cùng các file D2; do đó vẫn còn thay đổi ngoài tests. Baseline được cung cấp là 1109 test với 5 lỗi `DoctorCliTests`; lượt này chỉ xác minh bộ glass 60 test.

Không stage, commit, push, load plugin, chạy `visuals.py`, hoặc tác động tới phiên máy.
