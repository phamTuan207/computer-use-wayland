Báo cáo sửa session startup — đo trực tiếp trên Hyprland v0.56.2

BLOCKER

`scripts/cursor_session.py:118` chụp mọi màn hình đang bật, thu ảnh RGB về tối đa
1280 pixel ngang, yêu cầu ba cặp ảnh liên tiếp giống nhau trước khi báo ready.
`scripts/cursor_session.py:194` gọi bước này sau hotkey và sau đổi zoom.
Không có sleep khởi động. Giới hạn 120 vòng và deadline 6 giây; mỗi lệnh chụp
bị giới hạn bởi thời gian còn lại (`scripts/cursor_session.py:130`).
6 giây là chính sách giới hạn khởi động, không phải độ trễ đo được; nó cho phép
nhiều vòng sau khoảng ổn định đo được bên dưới. Nếu không ổn định hoặc chụp lỗi,
phiên báo lỗi, không chạy driver, rồi khôi phục zoom (`scripts/cursor_session.py:169`,
`scripts/cursor_session.py:204`). Không nới ngưỡng guard tại `scripts/cu.py:261`.

MEASURED

Môi trường desktop lấy từ `/proc` của quickshell bằng `cu.environment()`
(`scripts/cu.py:81`), gồm WAYLAND_DISPLAY và HYPRLAND_INSTANCE_SIGNATURE.
Cache riêng trong /tmp. Không chạy bản cài đặt, không di chuyển con trỏ, click,
gõ phím; action là wait:0. Build pointer bằng `python3 scripts/build.py`:
output đầy đủ: `pointer built`.

Trước sửa: driver chạy dưới `python3 scripts/cu.py session -- python3
/tmp/cu-session-evidence/driver.py before`, observe eDP-2, observe lại sau
2 giây, rồi act dùng observation đầu. Mean tính bằng trung bình ba kênh RGB của
ImageChops.difference, đúng công thức `scripts/cu.py:261`. Khi act bị từ chối,
`after.image` chính là ảnh guard đã so sánh (`scripts/cu.py:390`), nên đo mean
trên cặp observation đầu và after.image cho mean guard thật.

Mean trước sửa: 18.481884440104; capture 0→1: 18.481884440104; bbox [0, 0, 1280, 800]; capture_ms [40, 38].
Output JSON đầy đủ của driver trước sửa:

```json
{
  "label": "before",
  "capture_0_to_1_mean": 18.481884440104167,
  "bbox": [
    0,
    0,
    1280,
    800
  ],
  "capture_ms": [
    40,
    38
  ],
  "guard_mean": 18.481884440104167,
  "act_exit": 1,
  "act": {
    "ok": false,
    "completed": 0,
    "error": "screen changed since observation; inspect after.image",
    "after": {
      "image": "/tmp/cu-session-evidence/cache/agent-computer-use/eae3da03c2bb.png",
      "observation": "/tmp/cu-session-evidence/cache/agent-computer-use/eae3da03c2bb.json",
      "image_size": [
        1280,
        800
      ],
      "capture_ms": 33,
      "region": [
        0,
        0,
        1920,
        1200
      ],
      "crop": null,
      "scale": 0.666667
    }
  },
  "zoom_during": "float: 5.000000\nset: true"
}
```

Session trước sửa thoát 1; getoption sau phiên trả `float: 1.000000`, `set: true`.

Sau sửa: `python3 tests/session_quiet_live.py` chạy `cu.py session -- DRIVER`;
driver observe rồi act ngay, không có sleep giữa chúng. Bộ đo chỉ bọc
`screen_changed` để ghi mean của hai ảnh mà guard thật nhận, rồi gọi guard gốc
(`tests/session_quiet_live.py:19`). Mọi xử lý CLI, lock, token và action vẫn đi
qua `cu.main()` (`tests/session_quiet_live.py:27`). Driver dùng wait:0 tại
`tests/session_quiet_live.py:35`; đo zoom sau phiên tại dòng 51.

Lệnh và output đầy đủ của lần chạy trên bản cuối:

```sh
python3 tests/session_quiet_live.py
```

```text
zoom_before: float: 1.000000
set: true
desktop quiet after 25 captures; global mean=0.000000
{"guard_mean": 0.0, "act_exit": 0, "act": {"ok": true, "completed": 1, "execution_ms": 113, "after": {"image": "/tmp/cu-quiet-live-_0qhov21/agent-computer-use/c410443739ca.png", "observation": "/tmp/cu-quiet-live-_0qhov21/agent-computer-use/c410443739ca.json", "image_size": [1280, 800], "capture_ms": 29, "region": [0, 0, 1920, 1200], "crop": null, "scale": 0.666667}, "changed": false}, "zoom_during": "float: 5.000000\nset: true"}
session_exit: 0
zoom_after: float: 1.000000
set: true
```

DEFECTS

1. `scripts/cursor_session.py:294`: wrapper thử recover khi snapshot còn tồn tại,
   kể cả guardian thoát 1; token và lock vẫn được recover kiểm tra ở dòng 97.
   Guardian lỗi vẫn khiến phiên trả lỗi tại dòng 298. Test ba lần restore lỗi rồi
   wrapper khôi phục, và sáu lần lỗi giữ snapshot: `tests/test_cursor_session.py:259`.
2. `scripts/cursor_session.py:188`: lỗi Escape chỉ in warning. Bộ lọc tên keyboard
   không phân biệt hoa thường (`scripts/cancel_hotkey.py:25`). Test hotkey lỗi và
   Keychron: `tests/test_cursor_session.py:200`, `tests/test_cursor_session.py:207`.
   Lệnh Escape cũng mang cache phiên và đường dẫn Python hiện tại, với shell quoting
   (`scripts/cancel_hotkey.py:32`), để latch hủy đúng phiên khi cache được đổi.
3. `scripts/cursor_session.py:204`: từng thao tác cleanup được xử lý lỗi độc lập;
   finally vẫn gọi restore ở dòng 213. Test chèn lỗi vào cả ba thao tác:
   `tests/test_cursor_session.py:215`.

TESTS

Lệnh và output đầy đủ:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

```text
test_bad_key_and_non_bmp_rejected_before_execution (test_core.Coordinates.test_bad_key_and_non_bmp_rejected_before_execution) ... ok
test_cancel_interrupts_running_adapter_and_latches (test_core.Coordinates.test_cancel_interrupts_running_adapter_and_latches) ... ok
test_clipped_window (test_core.Coordinates.test_clipped_window) ... ok
test_compact_observation_retains_paths_not_internal_geometry (test_core.Coordinates.test_compact_observation_retains_paths_not_internal_geometry) ... ok
test_delay_reset_starts_another_wtype_process (test_core.Coordinates.test_delay_reset_starts_another_wtype_process) ... ok
test_focus_and_composition_boundaries (test_core.Coordinates.test_focus_and_composition_boundaries) ... ok
test_fractional_scale_and_rotated_monitor (test_core.Coordinates.test_fractional_scale_and_rotated_monitor) ... ok
test_key_aliases (test_core.Coordinates.test_key_aliases) ... ok
test_outside_monitor (test_core.Coordinates.test_outside_monitor) ... ok
test_reject_invalid_points (test_core.Coordinates.test_reject_invalid_points) ... ok
test_reject_invalid_window_before_dispatch (test_core.Coordinates.test_reject_invalid_window_before_dispatch) ... ok
test_resized_crop_with_negative_monitor_origin (test_core.Coordinates.test_resized_crop_with_negative_monitor_origin) ... ok
test_restore_ime_on_typing_failure (test_core.Coordinates.test_restore_ime_on_typing_failure) ... ok
test_screen_crop_maps_negative_monitor_origin_and_rejects_overflow (test_core.Coordinates.test_screen_crop_maps_negative_monitor_origin_and_rejects_overflow) ... ok
test_screen_observation_rejects_keyboard_before_input (test_core.Coordinates.test_screen_observation_rejects_keyboard_before_input) ... ok
test_small_target_change_detected_without_global_change (test_core.Coordinates.test_small_target_change_detected_without_global_change) ... ok
test_validate_bad_batches (test_core.Coordinates.test_validate_bad_batches) ... ok
test_capture_failure_aborts_startup_and_restores (test_cursor_session.Lifecycle.test_capture_failure_aborts_startup_and_restores) ... ok
test_cleanup_exceptions_cannot_skip_restore (test_cursor_session.Lifecycle.test_cleanup_exceptions_cannot_skip_restore) ... ready
registered
session cleanup failed: cleanup injected
ready
registered
session cleanup failed: cleanup injected
ready
registered
session cleanup failed: cleanup injected
ok
test_concurrent_session_cannot_overwrite_original (test_cursor_session.Lifecycle.test_concurrent_session_cannot_overwrite_original) ... ok
test_escape_cancel_restores_even_when_unbind_fails (test_cursor_session.Lifecycle.test_escape_cancel_restores_even_when_unbind_fails) ... ok
test_gate_eof_never_starts_driver (test_cursor_session.Lifecycle.test_gate_eof_never_starts_driver) ... ok
test_guardian_death_has_wrapper_fallback (test_cursor_session.Lifecycle.test_guardian_death_has_wrapper_fallback) ... ok
test_guardian_death_reaps_whole_driver_group (test_cursor_session.Lifecycle.test_guardian_death_reaps_whole_driver_group) ... ok
test_hotkey_failure_warns_but_driver_runs (test_cursor_session.Lifecycle.test_hotkey_failure_warns_but_driver_runs) ... ok
test_input_requires_explicit_session (test_cursor_session.Lifecycle.test_input_requires_explicit_session) ... ok
test_keeps_zoom_between_commands_and_finish_restores (test_cursor_session.Lifecycle.test_keeps_zoom_between_commands_and_finish_restores) ... ok
test_mixed_case_physical_keyboard (test_cursor_session.Lifecycle.test_mixed_case_physical_keyboard) ... ok
test_old_command_cannot_stop_new_session (test_cursor_session.Lifecycle.test_old_command_cannot_stop_new_session) ... ok
test_quiet_capture_is_bounded_and_cancelable (test_cursor_session.Lifecycle.test_quiet_capture_is_bounded_and_cancelable) ... desktop quiet after 5 captures; global mean=0.000000
ok
test_refusal_and_exception_end_session (test_cursor_session.Lifecycle.test_refusal_and_exception_end_session) ... ok
test_restore_timeout_preserves_snapshot_and_does_not_raise (test_cursor_session.Lifecycle.test_restore_timeout_preserves_snapshot_and_does_not_raise) ... cursor restore failed; snapshot retained; run computer-use recover
ok
test_retry_and_persistent_recovery_after_failed_restore (test_cursor_session.Lifecycle.test_retry_and_persistent_recovery_after_failed_restore) ... ok
test_startup_failures_restore_if_write_may_have_applied (test_cursor_session.Lifecycle.test_startup_failures_restore_if_write_may_have_applied) ... ok
test_success_and_driver_error_restore_nondefault (test_cursor_session.Lifecycle.test_success_and_driver_error_restore_nondefault) ... ok
test_unknown_value_never_changes_cursor (test_cursor_session.Lifecycle.test_unknown_value_never_changes_cursor) ... ok
test_wrapper_signals_and_abrupt_death (test_cursor_session.Lifecycle.test_wrapper_signals_and_abrupt_death) ... ok

----------------------------------------------------------------------
Ran 37 tests in 17.000s

OK
```

```sh
git diff --check
```

Output: rỗng, exit 0. Không chạy git add, commit hoặc push.

RISK / OPEN

Chưa thử nhấn Escape thật, move/click/type (tuân thủ yêu cầu không phát input).
Chưa đo live trên nhiều màn hình, máy chậm hoặc desktop phát video liên tục.
Desktop luôn biến động sẽ bị từ chối sau giới hạn, theo chính sách được mô tả
ở `README.md:72`; unit test kiểm tra ảnh luôn đổi, deadline và hủy
(`tests/test_cursor_session.py:223`), startup thất bại không chạy driver và vẫn
restore (`tests/test_cursor_session.py:244`). Ba cặp ảnh ổn định là quan sát đã
đo, không đảm bảo desktop không đổi sau khi driver được mở gate.

DISAGREE

Phép đo tách riêng không ủng hộ giả thuyết hl.bind gây reload ở máy này.
hotkey_on: 46 mẫu trong 2.547 giây, mọi mean bằng 0. Đổi zoom 1→5: mean mẫu đầu 19.170889, mean liên tiếp bắt đầu bằng 0 tại 1.143 giây.

Mã nguồn upstream đúng phiên bản: hl.bind gọi addKeybind tại
[LuaBindingsToplevel.cpp:253](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/lua/bindings/LuaBindingsToplevel.cpp#L253);
[KeybindManager.cpp:187](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/managers/KeybindManager.cpp#L187)
chỉ thêm bind. eval gọi bộ thực thi Lua tại
[HyprCtl.cpp:1119](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/debug/HyprCtl.cpp#L1119),
[ConfigManager.cpp:880](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/lua/ConfigManager.cpp#L880)
không gọi reload. Vì vậy giữ cơ chế bind hiện có, không tìm cách thay thế một reload
mà mã nguồn và phép đo này không cho thấy. Bằng chứng live chỉ ra thay đổi zoom
khi khởi động là trigger; chưa truy vết sâu renderer để kết luận cơ chế nội bộ.

Ngoài ra, bản repo nhận được đã có gate báo exit 1 khi guardian lỗi; phần
“session exits 0” không đúng với bản này (`scripts/cursor_session.py:298`).
Lỗi bỏ qua fallback khi guardian thoát 1 vẫn có và đã sửa.

Dữ liệu đầy đủ phép đo tách riêng (thời gian từ lúc thao tác trả về, mean so với
ảnh ngay trước; không sleep giữa các ảnh):

```json
[
  {
    "operation": "hotkey_on",
    "samples": [
      [
        0.06,
        0.0
      ],
      [
        0.108,
        0.0
      ],
      [
        0.169,
        0.0
      ],
      [
        0.231,
        0.0
      ],
      [
        0.293,
        0.0
      ],
      [
        0.343,
        0.0
      ],
      [
        0.401,
        0.0
      ],
      [
        0.45,
        0.0
      ],
      [
        0.499,
        0.0
      ],
      [
        0.56,
        0.0
      ],
      [
        0.62,
        0.0
      ],
      [
        0.669,
        0.0
      ],
      [
        0.728,
        0.0
      ],
      [
        0.777,
        0.0
      ],
      [
        0.837,
        0.0
      ],
      [
        0.885,
        0.0
      ],
      [
        0.934,
        0.0
      ],
      [
        0.996,
        0.0
      ],
      [
        1.044,
        0.0
      ],
      [
        1.102,
        0.0
      ],
      [
        1.154,
        0.0
      ],
      [
        1.212,
        0.0
      ],
      [
        1.273,
        0.0
      ],
      [
        1.333,
        0.0
      ],
      [
        1.394,
        0.0
      ],
      [
        1.455,
        0.0
      ],
      [
        1.506,
        0.0
      ],
      [
        1.565,
        0.0
      ],
      [
        1.616,
        0.0
      ],
      [
        1.675,
        0.0
      ],
      [
        1.725,
        0.0
      ],
      [
        1.785,
        0.0
      ],
      [
        1.834,
        0.0
      ],
      [
        1.894,
        0.0
      ],
      [
        1.943,
        0.0
      ],
      [
        2.003,
        0.0
      ],
      [
        2.056,
        0.0
      ],
      [
        2.114,
        0.0
      ],
      [
        2.161,
        0.0
      ],
      [
        2.22,
        0.0
      ],
      [
        2.269,
        0.0
      ],
      [
        2.316,
        0.0
      ],
      [
        2.374,
        0.0
      ],
      [
        2.434,
        0.0
      ],
      [
        2.486,
        0.0
      ],
      [
        2.547,
        0.0
      ]
    ]
  },
  {
    "operation": "zoom_5",
    "samples": [
      [
        0.051,
        19.170889
      ],
      [
        0.106,
        14.532015
      ],
      [
        0.161,
        14.330691
      ],
      [
        0.216,
        15.117307
      ],
      [
        0.27,
        13.825999
      ],
      [
        0.328,
        12.658655
      ],
      [
        0.38,
        11.428882
      ],
      [
        0.439,
        10.418658
      ],
      [
        0.49,
        9.548844
      ],
      [
        0.546,
        7.849813
      ],
      [
        0.598,
        7.586719
      ],
      [
        0.652,
        6.449273
      ],
      [
        0.707,
        5.315577
      ],
      [
        0.765,
        4.103549
      ],
      [
        0.822,
        3.156933
      ],
      [
        0.874,
        2.232106
      ],
      [
        0.929,
        1.46942
      ],
      [
        0.987,
        0.866804
      ],
      [
        1.043,
        0.283678
      ],
      [
        1.092,
        0.004682
      ],
      [
        1.143,
        0.0
      ],
      [
        1.192,
        0.0
      ],
      [
        1.239,
        0.0
      ],
      [
        1.287,
        0.0
      ],
      [
        1.334,
        0.0
      ],
      [
        1.382,
        0.0
      ],
      [
        1.435,
        0.0
      ],
      [
        1.486,
        0.0
      ],
      [
        1.538,
        0.0
      ],
      [
        1.591,
        0.0
      ],
      [
        1.64,
        0.0
      ],
      [
        1.689,
        0.0
      ],
      [
        1.739,
        0.0
      ],
      [
        1.792,
        0.0
      ],
      [
        1.84,
        0.0
      ],
      [
        1.891,
        0.0
      ],
      [
        1.941,
        0.0
      ],
      [
        1.996,
        0.0
      ],
      [
        2.047,
        0.0
      ],
      [
        2.101,
        0.0
      ],
      [
        2.154,
        0.0
      ],
      [
        2.208,
        0.0
      ],
      [
        2.259,
        0.0
      ],
      [
        2.311,
        0.0
      ],
      [
        2.366,
        0.0
      ],
      [
        2.421,
        0.0
      ],
      [
        2.478,
        0.0
      ],
      [
        2.533,
        0.0
      ]
    ]
  }
]
```
