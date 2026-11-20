# EVENT-WAIT-SEQ METHOD arm

## Trạng thái

**BLOCKED tại setup bước 3.** Chưa chạy arm đo METHOD vì không thể chuyển checkout sang HEAD yêu cầu mà vẫn giữ nguyên file log đang được đồng bộ. HEAD tại thời điểm dừng là `56f5af4`, không phải `3113fb1`.

## Setup và bằng chứng

- Broker ở lần kiểm tra đầu tiên đang bận: `state=running`, `owner=h3land2-d1`, `driver=ready`, `guardian=active`, `started_git_head=6bca53a66d7ab937b027d8f9b64ffce9194386ba`. Không khởi chạy session và chờ đến lần kiểm tra tiếp theo.
- Lần kiểm tra tiếp theo cho thấy broker rảnh theo quy tắc: `state=finished`, `owner=h3land2-check`, `driver=stopped`, `guardian=clean`, `stop_reason=explicit_finish`; `started_git_head=56f5af4e521e1c20b26b56dc31d662e34f1c2668`.
- `git status --short` đúng với danh sách đã biết: `M improvements/live-test-log.md`, cùng bốn thư mục hoặc tệp untracked đã nêu trong brief. Không có mục mới.
- Bản sao bảo vệ tại `/tmp/live-test-log-main-backup-ewmethod.md` có MD5 `0fee1435cfb43d554404caf487ed80f2`.
- `git checkout --detach 3113fb1` bị Git từ chối vì thay đổi cục bộ trong `improvements/live-test-log.md` sẽ bị ghi đè. Thử giữ nguyên file bằng cờ `skip-worktree` cũng không cho checkout. Đã gỡ cờ ngay sau đó. MD5 file trong checkout vẫn là `0fee1435cfb43d554404caf487ed80f2`, HEAD vẫn `56f5af4`, và `git status --short` vẫn đúng danh sách ban đầu.
- Vì không đạt HEAD yêu cầu, không restart relay, không chạy suite gate, và không grep `wait_for` trong code được phục vụ. Không sửa nội dung các tệp dirty/untracked.

## Kết quả tác vụ

Không có session, lease, timed.py request, quan sát màn hình, hoặc probe nào được chạy. Vì vậy không có số đo để so với baseline.

| Tác vụ | wall | think | service | calls | observes | re-observes | wait_for | timeouts | missed events | waits absorbed | OCR / ground truth |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| P1 C-03 | N/A | N/A | N/A | 0 | 0 | 0 | Chưa chạy | 0 | 0 | 0 | Chưa có ảnh; ground truth chưa thu thập |
| P2 E-04 | N/A | N/A | N/A | 0 | 0 | 0 | Chưa chạy | 0 | 0 | 0 | Chưa có ảnh; ground truth là 96.0 |
| P3 B-01 | N/A | N/A | N/A | 0 | 0 | 0 | Chưa chạy | 0 | 0 | 0 | Chưa có ảnh; chưa kiểm tra 4 thư mục |
| P4 A-01 | N/A | N/A | N/A | 0 | 0 | 0 | Chưa chạy | 0 | 0 | 0 | Chưa có ảnh; chưa kiểm tra 3 dòng byte-exact |
| Probe | N/A | N/A | N/A | 0 | 0 | 0 | openwindow và activewindow chưa chạy | 0 | 0 | 0 | Chưa có ảnh |

## Relay, desktop, và teardown

- Không restart relay, vì HEAD chưa khớp. Trạng thái broker cuối cùng đã quan sát được vẫn là `finished`, driver `stopped`, guardian `clean`; không có session do arm này tạo.
- Không mở terminal kiểm thử hoặc cửa sổ probe. Không chạy lệnh dọn `/tmp/hoc-ky-2` hay `/tmp/y-tuong.txt`, vì arm chưa kiểm tra trạng thái dirt và không tạo các tệp đó.
- Không chạy lệnh xác nhận cửa sổ desktop; desktop chưa bị arm này tác động.
- Không thực hiện teardown vì chưa rời `56f5af4` và chưa tạo session. Sau khi bị chặn, MD5 của log chính khớp bản sao: `0fee1435cfb43d554404caf487ed80f2`.

## Verdict và việc còn lại

Không thể đánh giá success bar về tốc độ, timeout, hoặc missed event. Việc còn lại là giải quyết cách giữ nguyên `improvements/live-test-log.md` trong lúc chuyển checkout sang `3113fb1`, sau đó chạy lại từ setup bước 3. Không có kết luận về hiệu năng METHOD từ lần chạy bị chặn này.
