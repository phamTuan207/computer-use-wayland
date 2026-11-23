# Council 1 review: W-PILLFIX-AMEND (5a272ae + a355002)

Reviewer doc lap Council 1 cho W-PILLFIX-AMEND. Nhiem vu tu Muse tong:
verify doc lap fix thu hep remove_holder (R6/C1). Khong sua fix, khong
chay live, khong tu spawn reviewer. Moi gio Asia/Ho_Chi_Minh. Khong dau
gach ngang dai. Chuan Lauren Tan: lenh chay + output + commit hash +
log thoi gian.

## Verdict: GO VOI DIEU KIEN

Dieu kien (ca 2 thuoc 1 follow-up lane, giao ten cu the truoc khi
live phase nao chay 2 run pid-less cung agent chong len nhau):

1. overlay.hold() va s2_flip pill_acquire_cmd / pill_release_cmd
truyen --pid that cua tien trinh goi (redteam amend 1, phan 2), de moi
run co key rieng va prune_dead_holders heal duoc. Ly do: sau fix,
holder pid-less van chia 1 key tran theo agent; 2 run cung agent
khong pid chong len nhau thi release cua run nay van go holder cua
run kia. Day la han che cu co san, khong phai loi moi do fix sinh ra.
2. Cung follow-up do, sua s2_flip pill_release_cmd: bo co --method CDP
(release parser khong co --method; toi verify tren VM: rc=2,
"unrecognized arguments: --method CDP", holder khong bao gio duoc
xoa). Sua luon docstring cdp_pill_hold (noi daemon prune holder
pid-less khi agent duoc dung lai, sai, prune_dead_holders khong bao
gio cham holder pid-less).
3. Trien khai truoc live tiep theo: dong bo overlay.py moi len
laptop va restart daemon 115582 (chay code cu tu 19:40:45), roi
verify bang docstring moi (muc 8). Neu khong, live chay van dung
code cu va lo R6 van mo.

Khong can AMEND: fix khong can sua; cac muc mo nam o file khac
(s2_flip_live.py, hold) va da co duong follow-up. Log muc 2 da ghi
lai follow-up --pid, khong de mat.

## 1. Doc diff (20:17 +07, T+0m)

- 5a272aeec9996a2febb00063d26c29da93bc9f94: fix + 3 test + log, 3 file,
  223 insertions, 18 deletions. scripts/overlay.py (remove_holder),
  tests/test_overlay.py (3 test moi), improvements/w-pillfix-amend-log.md.
- a355002071457e429a753cae3c0ec65bea0022df: docs, ghi hash 5a272ae
  vao log muc 6, 1 file, 5 insertions, 1 deletion.
- Ca 2 commit: 0 dau gach ngang dai (U+2014: 0, U+2013: 0, kiem
  bang python count tren git show).
- R6/C1 dung nhu review goc: redteam R6 "acquire that bai voi
  pid=None xoa holder cua run khac dang song"
  (improvements/w-pillfix-redteam-review.md dong 97); Council 3 C1
  "thu hep viec go holder" (improvements/w-pillfix-council-3-review.md
  dong 20). Fix nay dong dung pham vi do.

## 2. Ngu nghia remove_holder moi doi voi moi caller (20:17 +07)

Moi: chi xoa dung 1 key `_holder_key(agent, pid)`. pid int > 0 thi
chi xoa agent:pid; pid None thi chi xoa key tran agent. Khong bao
gio xoa holder cua run khac.

| Caller | Args truyen | Key bi xoa | Ket luan |
|---|---|---|---|
| Daemon release handler, overlay.py:412 | (agent, pid tu req) | dung key cua req | Dung. Release pid None khong con xoa het holder pid-keyed cung agent. |
| cmd_acquire D1 exception, overlay.py:532 | (agent, args.pid) | dung key vua add | Dung. add_holder dung cung _holder_key nen cap doi khop. |
| cmd_acquire invisible, overlay.py:547 | (agent, args.pid) | dung key vua add | Dung. Test end-to-end moi bao phu (muc 3). |
| cmd_release no-daemon, overlay.py:561 | (agent, args.pid) | dung key duoc yeu cau | Dung. Buoc 0 dung duong nay, chi xoa W-PILLFIX, giu S2-flip (muc 5). |
| cmd_release socket-failure fallback, overlay.py:569 | (agent, args.pid) | dung key nhu req socket | Dung. |
| first_action.acquire_overlay, first_action.py:143 | (agent, os.getpid()) | dung key vua add | Dung. |
| first_action.release_overlay, first_action.py:181 | (agent, os.getpid()) | dung entry cua run nay | Dung. Docstring "Only this run's entry is removed" nay dung that; truoc day remove_holder pid int con xoa them key tran. |
| overlay.hold(), overlay.py:625 | acquire bare + release bare | bare key | Dung, cap nhat quan. Release bare khong con xoa holder pid-keyed cung agent (truoc day co). |
| cmd_stop | xoa het | tat ca | Len dung co y, khong anh huong. |
| prune_dead_holders | khong goi remove_holder | khong | Chi xoa holder pid int chet; khong anh huong. |

Khong caller nao phu thuoc vao hanh vi xoa het cu. `_holder_key`
voi pid <= 0 hoac khong phai int tra ve key tran, nhat quan ca 2
chieu add/remove. Voi agent rong (daemon req mac dinh '') key moi
chi la '', hep hon code cu (cu con match key bat dau bang ':').

Han che con lai (cu co san, khong do fix sinh ra): 2 run pid-less
cung agent chia 1 key tran; add_holder ghi de, release cua run nay
go holder cua run kia. Day la ly do dieu kien 1 ton tai.

## 3. Test moi: pass tren code moi, fail tren code cu (20:18 +07)

Targeted tren HEAD hien tai (4dafe17, da fast-forward):
```
python3 -m unittest discover -s tests -p 'test_overlay.py'
Ran 22 tests in 0.074s
OK
```
22 = 19 cu + 3 moi, deu pass.

Baseline doc lap: worktree /tmp/amend-review-baseline tai 8f600b9
(code cu), copy file test moi sang, chay cung lenh:
```
Ran 22 tests in 0.017s
FAILED (failures=3)
```
Dung 3 test moi fail, ten day du:
- test_remove_holder_pid_none_keeps_pid_keyed_holder
- test_remove_holder_pid_keeps_bare_holder
- test_cmd_acquire_invisible_keeps_concurrent_holder
19 test cu van pass. Vay 3 test that su bat duoc R6, khong phai
test trang tri. Day cung la repro R6 doc lap: tren code cu, acquire
that bai pid=None xoa holder Muse:999001; tren code moi, holder
song.

## 4. Full suite dong thoi

Log cua worker, /tmp/w-pillfix-amend-fullsuite.log (da doc truc
tiep, khong tin loi noi):
```
Ran 2316 tests in 217.173s
FAILED (failures=1, errors=2, skipped=17)
```
3 loi, dung nhu log mo ta, deu loi moi truong co san, khong cham
overlay/indicator:
- ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26)
- ERROR test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_passes_when_fragment_is_visible (tesseract is unavailable)
- FAIL test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_fails_when_fragment_is_absent (tesseract is unavailable)
2316 = 2313 baseline + 3 test moi (ca 3 pass).

Chay lai doc lap cua toi, lan 1 (KHONG HOP LE, ghi lai de tranh
hieu lam): worktree sach /tmp/amend-review-clean tai a355002,
`python3 -m unittest discover -s tests -p 'test_*.py'`,
20:17-20:22 +07, log /tmp/amend-review-fullsuite.log:
```
Ran 2293 tests in 328.908s
FAILED (failures=4, errors=259, skipped=17)
```
Con so nay KHONG phan anh fix. Nguyen nhan da tim ra: worktree
khong mang file gitignored ma suite can. Cu the,
native/keyboard-protocol.c (va .h) la file ignored, chi co trong
main tree, khong co trong worktree nen setUpClass test_wtype_native
loi bien dich, 23 test wtype khong chay (2316-23=2293, khop), va
cac module phu thuoc duong dan/file local khac (keyboard_preflight,
type_verification, click2_redteam, session_driver) loi theo.
Bang chung doi chieu, chay truc tiep trong main tree 20:23 +07:
test_keyboard_preflight Ran 32 OK, test_wtype_native Ran 23 OK,
test_type_verification Ran 61 OK. Cung module, chi khac cho chay.
Vay worktree khong phai moi truong chay suite hop le o repo nay.

Chay lai doc lap cua toi, lan 2 (hop le): truc tiep trong main
tree tai 4dafe17 (gom amend + W-ZENPROOF2-FIX), cung lenh,
20:24-20:28 +07, log /tmp/amend-review-fullsuite-main.log:
```
Ran 2332 tests in 257.972s
FAILED (failures=1, errors=2, skipped=17)
```
Dung 3 loi tren, khong loi moi, khong fail moi:
- ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26)
- ERROR test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_passes_when_fragment_is_visible (tesseract is unavailable)
- FAIL test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_fails_when_fragment_is_absent (tesseract is unavailable)
2332 = 2316 (worker, tai a355002) + 16 test moi cua W-ZENPROOF2-FIX
(commit 014938b, lenh sau a355002), khop so hoc. Ket luan: 0
regression moi do fix, xac nhan doc lap.

## 5. Buoc 0: release holder W-PILLFIX, S2-flip yen (20:18 +07)

Log cua worker: release 20:09:25 rc=0 qua
`overlay.py release --agent W-PILLFIX`, sau do holders.json chi
con S2-flip, daemon van song.

Verify doc lap cua toi, chi doc qua ssh-laptop.sh, 20:18 +07:
- holders.json tren laptop chi con 1 key S2-flip (acquired
  2026-11-22T20:13:27+07:00, method CDP, pid null). Khong con
  W-PILLFIX. Holder S2-flip hien tai la run moi acquire lai sau
  buoc 0 (20:13:27 sau 20:09), chung to duong acquire van chay
  binh thuong sau fix.
- Daemon PID 115582 van song (started 19:40:45, elapsed 36:46),
  daemon.json khop PID. Buoc 0 khong restart daemon, khong dong
  vao S2-flip. S2-flip yen, daemon yen.

Luu y: holder S2-flip hien tai la bare key (pid null) vi
pill_acquire_cmd khong truyen --pid; release cua chinh no lai hong
do --method (muc 6). Nen holder nay ton tai nho ca 2 loi do, khong
phai nho co che dung. Day la ly do dieu kien 1+2 can lam.

## 6. Phat hien moi (ngoai pham vi diff, thuoc follow-up)

s2_flip pill_release_cmd (scripts/s2_flip_live.py:600) tra ve:
`python3 <overlay> release --agent S2-flip --method CDP`
Release parser chi co --agent va --pid, khong co --method. Toi
verify tren VM voi XDG_CACHE_HOME rieng:
```
$ python3 scripts/overlay.py release --agent S2-flip --method CDP
usage: overlay.py [-h] {acquire,release,status,stop,daemon} ...
overlay.py: error: unrecognized arguments: --method CDP
rc=2
```
Ket qua: release cua S2-flip khong bao gio chay, holder S2-flip
khong bao gio duoc tu xoa. Huong an toan (pill van hien, khong mat
pill), nhung holder rac ton tai va daemon khong bao gio tu thoat.
PILL_AGENT='S2-flip', PILL_METHOD='CDP' da xac minh
(s2_flip_live.py dong 85-86). Sua trong follow-up dieu kien 1+2
(bo --method, them --pid that).

Docstring cdp_pill_hold (s2_flip_live.py:607) noi "the daemon
prunes it only when the agent name is reused", sai:
prune_dead_holders chi xoa holder co pid int chet, khong bao gio
cham holder pid-less. Sua docstring trong follow-up.

## 7. Ket luan

- Fix dung, thu hep dung pham vi R6/C1, test that (pass moi,
  fail cu), khong regression (chay lai doc lap trong main tree:
  Ran 2332, chi 3 loi moi truong cu, 0 loi moi).
- Buoc 0 xong, W-PILLFIX het, S2-flip yen, daemon 115582 yen.
- Verdict: GO VOI DIEU KIEN (dieu kien 1+2+3 o dau). Khong can
  AMEND vi fix khong can sua.

## 8. Hoi tu voi redteam + luu y trien khai (20:29 +07)

- Redteam review 5d5111f (GO VOI DIEU KIEN) H1 bare-bare: trung
  voi dieu kien 1 cua toi (2 run pid-less cung agent chia key
  tran; acquire that bai van xoa holder tran cua run khac dang
  song). Hoi tu doc lap, khong sao chep: bang chung cua toi la
  doc code caller + test baseline, cua redteam la repro A8.
- H2 cua redteam: fix chua co mat tren laptop. Toi verify doc lap
  (chi doc, ssh-laptop.sh, 20:29 +07):
  ~/computer-use-wayland/scripts/overlay.py van la
  remove_holder CU (docstring "Without a pid, all of the agent's
  entries are removed"); repo laptop tai 331523f, scripts/overlay.py
  dang M (sua local); daemon 115582 chay code cu tu 19:40:45.
  Nghia la lo R6 van mo tren laptop cho den khi sync repo +
  restart daemon. Day khong phai loi cua fix, nhung la dieu kien
  trien khai (dieu kien 3): dong bo overlay.py moi len laptop,
  restart daemon (holder S2-flip hien tai khong tu het vi release
  cua no hong, muc 6, nen daemon se khong tu thoat khi holders
  ve 0), roi verify bang docstring moi truoc live tiep theo.
