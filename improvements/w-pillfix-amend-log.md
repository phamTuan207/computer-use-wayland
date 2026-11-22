# W-PILLFIX-AMEND log: fix R6/C1 (holder-drop scoping) + release holder smoke

Worker doc lap W-PILLFIX-AMEND (khong phai W-PILLFIX, khong phai
COORD-CLICK-9). Nhiem vu tu Muse tong: (0) release holder W-PILLFIX cu
(19:40:45, pid null) qua duong release dung, khong sua tay holders.json,
khong restart daemon, de yen holder S2-flip; (1) sua R6/C1: thu hep
remove_holder, chi xoa dung holder cu the, khong bao gio xoa tat ca
holder cua mot agent khi pid la None; (2) chay full suite dong thoi de
chung minh fix. Khong chay live (ZT-B, G-PILL retry), khong revert fix,
khong dong vao holder S2-flip. Khong tu spawn reviewer.
Moi gio Asia/Ho_Chi_Minh. Khong dau gach ngang dai. Khong ydotool.
Khong thong tin ca nhan. Chuan Lauren Tan: lenh chay + output + commit
hash + log thoi gian.

## 0. Doc review (20:08 +07, T+0m)

Doc 4 review tren todolist-push:
- improvements/w-pillfix-redteam-review.md (verdict AMEND, R6 la lo
  lon nhat, R1/R4/R7 + test gaps)
- improvements/w-pillfix-council-3-review.md (GO VOI DIEU KIEN, C1
  la dieu kien bat buoc truoc live tiep theo)
- improvements/w-pillfix-council-1-review.md (GO VOI DIEU KIEN,
  dieu kien 2: release holder smoke W-PILLFIX)
- improvements/w-pillfix-council-2-review.md (GO VOI DIEU KIEN)

R6/C1 (trung nhau): cmd_acquire that bai voi pid=None goi
remove_holder(agent, None) xoa TAT CA holder cung agent, ke ca run
khac dang song. Repro redteam: holder Muse:999001 bi xoa sach sau 1
acquire that bai, rc=1. Chieu nguoc: remove_holder voi pid int cung
xoa them key tran agent, nen acquire that bai co pid cung xoa holder
tran cua overlay.hold.

## 1. Buoc 0: release holder W-PILLFIX (20:09 +07, T+1m)

Trang thai truoc release (chi doc, ssh-laptop.sh):
- holders.json: S2-flip acquired 2026-11-22T20:02:18+07:00 (method
  CDP, pid null, dang song) va W-PILLFIX acquired
  2026-11-22T19:40:45+07:00 (method smoke, pid null).
- Daemon PID 115582, started 19:40:45, elapsed 28:30, dang chay.

Lenh (duong release dung cua overlay, khong sua tay holders.json,
khong restart daemon):
```
~/workspace/ssh-laptop.sh 'python3 /home/james/computer-use-wayland/scripts/overlay.py release --agent W-PILLFIX'
```
Output 20:09:25.866 +07:
```
[overlay] {"agent":"W-PILLFIX","elapsed_ms":12,"event":"released","wall_time":"2026-11-22T20:09:25.866+07:00"}
{"holders": {"S2-flip": {"acquired": "2026-11-22T20:02:18+07:00", "agent": "S2-flip", "method": "CDP", "pid": null}}, "label": "S2-flip via CDP", "owner": "daemon", "visible": true}
rc=0
```
Verify sau release: holders.json chi con S2-flip (20:02:18, pid null).
W-PILLFIX da het. S2-flip nguyen ven, pill van visible, daemon van
song (owner daemon). Buoc 0 xong.

## 2. Buoc 1: thu hep remove_holder (20:10 +07, T+2m)

File: scripts/overlay.py, ham remove_holder.

Cu: pid int thi xoa ca key agent:pid lan key tran agent; pid None thi
xoa moi key bang agent hoac bat dau bang agent + ':' (xoa het).

Moi: chi xoa dung 1 key cu the, _holder_key(agent, pid):
- pid int > 0: chi xoa agent:pid.
- pid None: chi xoa key tran agent.
Khong bao gio xoa holder cua run khac. Docstring cap nhat theo.

Kiem tra caller: cmd_acquire (D1 exception + invisible) xoa dung key
vua them; cmd_release / daemon release xoa dung holder duoc giu;
first_action.acquire_overlay xoa dung holder vua them (pid cua tien
trinh goi); first_action.release_overlay xoa dung entry cua run nay
(khop docstring cua no: "Only this run's entry is removed").
Khong caller nao phu thuoc vao hanh vi xoa het.

Khong sua: overlay.hold() va s2_flip pill_acquire_cmd truyen --pid
that (redteam amend 1, phan 2). Day la follow-up rieng, khong thuoc
pham vi R6/C1 cua task nay; ghi lai de Muse tong giao lane sau.

## 3. Test moi (20:10 +07, T+2m)

File: tests/test_overlay.py, 3 test moi sau
test_same_agent_two_pids_are_independent, kem trong khoi __main__:
- test_remove_holder_pid_none_keeps_pid_keyed_holder (R6/C1 truc
  tiep): 2 holder cung agent (1 tran, 1 pid-keyed 999001);
  remove_holder('Muse', None) chi xoa tran, giu Muse:999001.
- test_remove_holder_pid_keeps_bare_holder (chieu nguoc):
  remove_holder('Muse', 999001) chi xoa Muse:999001, giu tran.
- test_cmd_acquire_invisible_keeps_concurrent_holder (C1 end to
  end): holder pid-keyed dong thoi song, acquire that bai invisible
  voi pid=None tra 1, chi xoa key tran vua them, giu Muse:999001.

## 4. Targeted suite + repro R6 (20:10 +07, T+2m)

```
python3 -m unittest discover -s tests -p 'test_overlay.py'
Ran 22 tests in 0.020s, OK
```
22 = 19 cu + 3 moi, deu pass.

Repro R6 cua redteam (holder Muse:999001, acquire that bai pid=None):
```
before failed acquire pid=None: ['Muse:999001']
after  failed acquire pid=None: ['Muse:999001']
R6 FIXED: concurrent holder survives
```

Kiem chung test moi bat duoc loi cu: worktree /tmp/amend-baseline
tai 8f600b9 (code cu), copy file test moi sang, chay:
```
Ran 22 tests, FAILED (failures=3)
```
Dung 3 test moi fail tren code cu, 19 test cu van pass. Worktree da
xoa sau kiem chung. Vay 3 test moi that su bat duoc R6, khong phai
test trang tri.

## 5. Full suite dong thoi (20:10:53-20:14:31 +07, 217.2s)

Lenh: `python3 -m unittest discover -s tests -p 'test_*.py'`
Log: /tmp/w-pillfix-amend-fullsuite.log
Ket qua:
```
Ran 2316 tests in 217.173s
FAILED (failures=1, errors=2, skipped=17)
```
2316 = 2313 baseline + 3 test moi (ca 3 pass). 3 loi giong het
baseline, deu loi moi truong co san, khong cham overlay/indicator:
- ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26)
- ERROR test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_passes_when_fragment_is_visible (tesseract is unavailable)
- FAIL test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_fails_when_fragment_is_absent (tesseract is unavailable)
Ket luan: 2313/2316 pass, 0 regression moi, 0 loi moi do fix.
Muc tieu dat (Ran tang 3 do test moi, failures/errors/skipped
giong het baseline).

## 6. Commit va push

Lenh:
```
git add -- scripts/overlay.py tests/test_overlay.py improvements/w-pillfix-amend-log.md
git commit -m "fix: narrow remove_holder to one holder (R6/C1) + 3 tests"
git push origin todolist-push
git ls-remote origin todolist-push
```
Ket qua: (ghi sau khi push, kem hash commit).
