# Báo cáo triển khai A1

## Mốc thời gian

Các mốc dưới đây dùng giờ Asia/Ho_Chi_Minh, UTC+07.

- Commit design và template: 2026-11-19 13:35:01 +07.
- Commit interpreter và backend: 2026-11-19 13:44:26 +07.
- Bộ test cuối hoàn tất: 2026-11-19 13:52:06 +07, chạy 31.099 giây.
- Commit tests: 2026-11-19 13:52:21 +07.
- Kiểm tra repo và remote cuối: 2026-11-19 13:52:54 +07.

## HEAD và repo

- HEAD được xác minh trước khi sửa: `9a257c55635b4a7a5f6dfbd41d967ec44247a354`, đúng branch `speed-swarm`.
- HEAD cuối: `03795bc73479ea7ce03da2d1efbcd3985643cb3e`, branch `speed-swarm`.
- Repo sạch sau commit. Không checkout hoặc sửa `main`.

## File đã thay đổi

- `improvements/a1-code-exec-dom-design.md`: bản sao design đã cung cấp.
- `improvements/a1-dom-program-template.md`: chương trình D1 và sketch nhiều bước từ design.
- `scripts/code_exec.py`: thêm năm API DOM, preflight action, binding snapshot, hết hạn 90 giây và lưu binding trong state file hiện có.
- `scripts/cu.py`: thêm DOM methods vào `CodeExecBackend`, dùng `browser()` và `browser_start()`, áp dụng session policy cho DOM act.
- `tests/test_code_exec.py`: thêm 15 test DOM, gồm snapshot binding và hết hạn, validation, assert, trace budget, runaway loop, lưu state qua nhiều lần chạy, và chương trình desktop plus DOM.

Đã so sánh hai code block trong template với code block tương ứng trong design; cả hai khớp chính xác. Escape của `printf` giữ `\\n` giữa phần output và một `\n` cuối lệnh trong mã Python. Không sửa `scripts/cdp.mjs`, broker, driver, desktop act path, `MAX_PROGRAM_CHARS`, flag của pick khác, hoặc template Pick 1.

## Tuân thủ design và khác biệt

Không có khác biệt với design. Interpreter còn so sánh snapshot đầy đủ với binding để từ chối dict bị sửa dù vẫn giữ snapshot id. Điều này thực thi yêu cầu chỉ nhận dict snapshot được trả về trong session.

## Test

Lệnh suite trước và sau giống nhau:

```text
PYTHONPATH=tests:scripts python3 -m unittest test_session_remote test_session_driver test_act_diagnostics test_code_exec test_cdp_snapshot test_browser_worker
```

- Trước, tại HEAD `9a257c5`: 151 tests, 5 failures đã có từ trước. SHA256 danh sách lỗi đã sắp xếp: `9d2bf0e6a73b02020e951f5789e689efb7b37ee6242e4b64029b18460d44d0dd`.
- Sau: 166 tests, 5 failures, không có lỗi mới. Tất cả 15 test DOM mới pass. Riêng `test_code_exec`: 47 tests, OK.
- Log suite cuối: `/tmp/speed-a1-20261119/after-suites.log`.

Diff của danh sách FAIL/ERROR đã sắp xếp:

- Bị xóa: không có.
- Được thêm: không có.
- SHA256 danh sách sau: `9d2bf0e6a73b02020e951f5789e689efb7b37ee6242e4b64029b18460d44d0dd`, trùng hash trước.

Danh sách lỗi sau, giữ nguyên từ baseline:

```text
FAIL: test_base_exception_from_probe_is_not_converted_to_ime_error (test_session_driver.DoctorCliTests)
FAIL: test_first_failure_skips_second_probe (test_session_driver.DoctorCliTests)
FAIL: test_long_crlf_probe_error_is_single_line_bounded (test_session_driver.DoctorCliTests)
FAIL: test_remote_success_keeps_schema (test_session_driver.DoctorCliTests)
FAIL: test_second_probe_failure_after_first_success (test_session_driver.DoctorCliTests)
```

## Commits và xác minh push

| Commit | Thời gian +07 | Hash | Kết quả `git ls-remote origin speed-swarm` sau push |
| --- | --- | --- | --- |
| Design và template | 13:35:01 | `d955d745e07ad47a883ddd5c2c6bb097f67cbbe6` | `d955d745e07ad47a883ddd5c2c6bb097f67cbbe6 refs/heads/speed-swarm` |
| Interpreter và backend | 13:44:26 | `83f42244b3ff2f2322431c8167490b2e479c0502` | `83f42244b3ff2f2322431c8167490b2e479c0502 refs/heads/speed-swarm` |
| Tests | 13:52:21 | `03795bc73479ea7ce03da2d1efbcd3985643cb3e` | `03795bc73479ea7ce03da2d1efbcd3985643cb3e refs/heads/speed-swarm` |

Kiểm tra remote cuối:

```text
03795bc73479ea7ce03da2d1efbcd3985643cb3e	refs/heads/speed-swarm
```

## Verdict và việc còn mở

Verdict: PROVISIONAL, non-Astra. Cài đặt A1 và test đã hoàn tất; kết quả suite không làm tăng tập lỗi baseline.

Relay restart và live measurement còn mở cho coordinator. Không restart relay, không mở broker session, không khởi chạy browser, và không thao tác desktop.
