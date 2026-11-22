# W-PILLCDP log: pill cho moi hanh dong CDP

Worker doc lap cua COORD-CLICK-6. Nhiem vu: co che hien pill cho duong ghi CDP tho.
Moi gio ghi theo Asia/Ho_Chi_Minh. Khong dung dau gach ngang dai.

## 2026-11-22 18:33 +07, T+1m: nhan viec, bat dau nghien cuu

Repo: ~/workspace/computer-use-wayland, nhanh todolist-push, HEAD 5b6dbef.
Luat 18:30: pill phai hien khi agent dieu khien may bang BAT KY phuong phap nao.
Nguyen nhan: tin nhan cho mochi gui bang CDP tho (Runtime.evaluate) nen khong co pill.

## 2026-11-22 18:36 +07, T+4m: pill hien nay chay the nao

Doc: scripts/indicator.py, scripts/overlay.py, scripts/first_action.py,
docs/overlay.md, scripts/cu.py (ham browser), scripts/cdp.mjs,
scripts/s2_flip_live.py, scripts/chromium_cli.py, scripts/browser_worker.py.

Ket luan nghien cuu:

1. Session indicator (scripts/indicator.py): moi session sinh mot tien trinh
native `native/indicator`, noi show/hide/label/move qua stdin, token trong
`~/.cache/agent-computer-use/session.json`. `request(state, cmd)` noi qua
unix socket co token. `capture_clean()` an pill luc chup man hinh.
Ai hien: session driver khi session song. Cai gi giu: tien trinh native song.
Cai gi go: lenh hide, hoac session chet. Pill gan voi session (token).

2. Overlay trung tam (scripts/overlay.py, docs/overlay.md): DA CO SAN.
Holders dem tham chieu trong `~/.cache/agent-computer-use/overlay/holders.json`
(khoa file, key theo agent:pid, prune pid chet). Daemon khoi dong tach roi
o lan acquire dau, poll moi 2s. Neu session song thi chuyen show/label cho
session indicator, khong sinh pill thu hai; neu session chet trong khi holders
con thi daemon tu sinh native indicator va tiep quan. Pill chi an khi TAT CA
holders release. Label = acquirer moi nhat "agent via method", toi da 40 ky tu.
CLI: acquire/release/status/stop/daemon. Python: `overlay.hold(agent, method)`.
Day la co che dung san de CDP dung, khong can viet daemon moi.

3. Cua bao act-now (scripts/first_action.py): acquire_overlay /
overlay_visible / release_overlay. Fail-closed (D1): khong hien duoc pill
thi tu choi hanh dong, khong bao gio hanh dong vo hinh. Overlay duoc acquire
TRUOC moi thu khac. Day la tien le thiet ke cho hook CDP.

4. LO HONG: duong ghi CDP tho khong cham vao overlay lan nao.
`cu.browser()` (cu.py:2465) chay `node scripts/cdp.mjs`, handle() co 4
operation: tabs (doc), observe (doc), act (GHI: click/fill/set_value/focus/
key/scroll...), harvest (doc). Khong co lenh overlay nao trong cdp.mjs.
`scripts/browser_worker.py` spawn cdp.mjs --worker nen se duoc bao neu
gate dat trong cdp.mjs. `scripts/s2_flip_live.py` gui qua oneshot code-exec
-> session-driver -> dom_act -> cu.browser -> cdp.mjs, nen cung duoc bao;
chi buoc activate rieng (Target.activateTarget, /tmp/c5-activate.mjs)
nam ngoai cdp.mjs. `scripts/chromium_cli.py` co client CDP truc tiep rieng
(open/activate/close, Page.navigate qua WebSocket) cung khong co pill.

## Thiet ke (2026-11-22 18:37 +07)

Dat hook o noi thap nhat ma moi duong ghi CDP deu di qua: `handle()` trong
scripts/cdp.mjs, chi cho operation 'act' (tabs/observe/harvest la doc,
khong can pill, dung luat tam thoi). Acquire SAU moi validation cua act
(validation fail thi khong co hanh dong nao, khong can pill, va cac test
spawn that hien tai gui act loi validation van giu nguyen error), TRUOC
evaluate/input dau tien. Release trong finally ngoai cua handle() (bao ca
thanh cong, that bai, after-snapshot, screenshot).

Backend: mac dinh dung `node:child_process` execFile chay
`python3 <cung thu muc>/overlay.py acquire/release --agent X --method Y
--pid <pid>`, kiem tra reply JSON visible===true. Fail-closed: acquire
that (hoac khong tim duoc overlay.py) thi act bi tu choi voi error
'CDP pill unavailable: ...', khong bao gio ghi vo hinh.
Env `CU_CDP_PILL=0` tat gate (chi cho test fixture, ghi ro trong code).
Env `CU_OVERLAY_PY` ghi de duong dan overlay.py.
Request co the mang `agent`/`method` (validate charset nhu
first_action._broker_owner, mac dinh Muse/CDP).
Hook tiem `globalThis.__cdpPill` de test (vm harness cua cac test .mjs
hien tai strip dong import nen khong co execFile; khi khong co backend
nao thi gate bat hoat theo cau truc, chi test chuyen biet tiem hook gia).

Them 2 lop nua, cung dung overlay.py san co:
- scripts/chromium_cli.py: cac lenh ghi (open/activate/close) giu pill
qua `overlay.hold('Muse', 'CDP')`, fail-closed; lenh doc khong giu.
- scripts/s2_flip_live.py: giu pill best-effort quanh send_browser
(activate + send + V12) qua SSH toi laptop, agent rieng 'S2-flip' de
release khong cham vao holder cua agent khac; cua cung van la cdp.mjs
(fail-closed), lop nay chi lap khoang trong cua buoc activate.

Khong pha hanh vi pill cua act-now: khong sua overlay.py, indicator.py,
first_action.py; chi them caller moi cua overlay.py.

## 2026-11-22 18:38 +07, T+6m: lam xong hook cdp.mjs

File: scripts/cdp.mjs (them import execFile + ham pill, 3 diem moc).
- Acquire trong handle(), nhom act, SAU moi validation, TRUOC evaluate/input
dau tien; release trong finally ngoai (bao ca after-snapshot, screenshot,
that bai). Chi operation 'act'; tabs/observe/harvest khong acquire.
- Backend mac dinh: execFile chay `python3 <cung thu muc>/overlay.py
acquire/release --agent X --method Y --pid <pid>`, kiem tra reply JSON
visible===true. Fail-closed: acquire that thi act bi tu choi, error
'CDP pill unavailable: ...', khong input nao chay.
- Request co the mang agent/method (validate charset nhu first_action,
mac dinh Muse/CDP). CU_OVERLAY_PY ghi de duong dan. CU_CDP_PILL=0 tat
gate (chi test fixture). Hook tiem globalThis.__cdpPill cho test vm
(harness strip dong import nen khong co execFile; khong co backend thi
gate bat hoat theo cau truc, chi trong sandbox vm).
- Dat ham pill TRUOC assertAction de khong roi vao slice source cua
tests/cdp_errors.mjs (slice tu assertAction toi nhom act).

Test moi: tests/cdp_pill.mjs, 7 case, chay xanh 0.12s:
1. act acquire truoc moi evaluate/input, release sau cung, holder mac dinh.
2. validation fail thi khong acquire, giu nguyen error.
3. observe/harvest khong acquire.
4. acquire that thi tu choi act, 0 evaluate, 0 input.
5. CU_CDP_PILL=0 opt-out.
6. agent/method tu request; ten sai thi fallback mac dinh.
7. release that khong doi ket qua act.
Loi gap khi viet test: no_after doi action cuoi la assert (bo no_after);
harvest can window + shape tra ve cua DOM.getDocument/AXTree trong fake.
Ca 3 loi deu o test, khong phai o code gate.

## 2026-11-22 18:40 +07, T+8m: gate chromium_cli.py

File: scripts/chromium_cli.py. Them _pill_hold() (overlay.hold Muse/CDP,
fail-closed qua CalledProcessError) va WRITE_COMMANDS = open/activate/close.
Lenh doc khong giu. CU_CDP_PILL=0 tat cho test.
Test: tests/test_chromium_cli.py, setUp dat CU_CDP_PILL=0 cho stub test,
them 2 test moi (write giu pill, read khong giu; pill that thi tu choi
open truoc khi tao tab). Tong 23 test, xanh 1.2s.

## 2026-11-22 18:41 +07, T+9m: hold s2_flip_live.py

File: scripts/s2_flip_live.py. Them LAPTOP_OVERLAY/PILL_AGENT='S2-flip'/
PILL_METHOD='CDP', cdp_pill_hold() (best-effort: acquire that chi canh bao,
vi cua cung la cdp.mjs), send_browser thanh wrapper quanh
_send_browser_inner, seed/close scratch tab cung giu pill.
Test moi: tests/test_s2_flip_pill.py, 3 case voi SSH gia, xanh 0.001s.
test_s2_flip_wiring cu van qua.

## 2026-11-22 18:42 +07, T+10m: docs

docs/overlay.md: them muc "CDP writes" + quy trinh cho lane + cach xu ly
khi act bi tu choi 'CDP pill unavailable'.

## 2026-11-22 18:44 +07, T+12m: VA CHAM voi W-F4FIX (khong phai loi cua gate)

Chay lai battery day du, 3 suite node do + 2 test python do:
- tests/cdp_snapshot.mjs: worker status 0 thay vi 1 (dong 404).
- tests/cdp_worker.mjs: output.length 2 thay vi 1 (dong 162).
- tests/cdp_errors.mjs: exitCode 0 thay vi 1 (dong 153).
- tests/test_cdp_snapshot.py: 2 fail theo.
Nguyen nhan: git diff scripts/cdp.mjs cho thay worktree co them mot hunk
F4 cua W-F4FIX (chua commit, khong phai cua toi): vong lap --worker
khong break sau ok:false nua, reset process.exitCode = 0 o EOF. Ca 3
assert do deu do dung hanh vi cu ma F4 doi co tinh. File cdp.mjs luc
18:32 toi nhan viec con sach; battery xanh luc 18:47 (sau moi sua cua
toi); hunk F4 xuat hien sau do, trong luc W-F4FIX lam viec song song.
Coord log xac nhan W-F4FIX dang lam F4 va doi pill (muc 192-194), va
laptop dang o commit 331523f cua W-F4FIX.
Chung minh gate vo can: build ban pill-only (/tmp/pillcheck: HEAD + 4
hunk cua toi, bo hunk F4) roi chay lai: 7/7 suite node xanh
(cdp_snapshot, cdp_worker, cdp_errors, cdp_validation, cdp_keys,
cdp_list_diagnostics, cdp_pill) + python 108 test xanh
(test_cdp_snapshot, test_overlay, test_first_action). Worktree python
220 test xanh (tru test_cdp_snapshot do F4).
Ket luan: KHONG sua code F4, KHONG commit file cua ho. Khi commit
scripts/cdp.mjs, chi stage 4 hunk cua toi (loc diff, verify staged
chi co hunk cua toi, unstaged chi con hunk F4), de cong viec cua
W-F4FIX nguyen ven trong worktree.

## 2026-11-22 18:45 +07, T+13m: live-path tren VM (khong trinh duyet, khong laptop)

Khong verify live tren trinh duyet: laptop chua co code cua toi (repo
laptop o commit 331523f cua W-F4FIX, dang chay probe live), dong bo
code cua toi sang se de len cong viec cua ho; Chromium 9223 co tab mochi
dang mo, khong co slot scratch rong. Lam thay bang stub CDP tren VM
(/tmp/pill-live/stub_cdp.py, /tmp/pill-live/fake_overlay.py) + adapter
that chay one-shot:
- A, 18:45 +07: CU_OVERLAY_PY=fake overlay, act wait 100ms: ok:true,
completed:1, 103ms; log fake overlay ghi acquire (t=...923.138) truoc
release (t=...923.281), cung pid 23998, agent Muse, method CDP.
Pill giu xuyen suot act tren duong chay that (execFile that).
- B, 18:45 +07: overlay.py that tren VM (khong Wayland, thieu
native/indicator): act bi tu choi ok:false, completed:0, error
'CDP pill unavailable: {...visible:false...}', rc=1. Fail-closed tren
duong that. Holders.json sau do la {} (holder loi da duoc don), status
visible:false. VM sach.
- C, 18:45 +07: CU_CDP_PILL=0: act ok:true, 0 cuoc goi overlay.
Con no: verify pill hien that tren man hinh laptop (can repo laptop
dong bo code moi + tab scratch, sau khi F4 xong, co dieu phoi).

## 2026-11-22 18:46 +07, T+14m: nhanh doi duoi chan, F4 CLOSED

Luc fetch truoc khi commit, origin/todolist-push da co 3 commit moi cua
W-F4FIX: 331523f (probe driver mo tab moi), 9c9fea9 (log part 1-2, pill
check YES theo code path: probe driver chay trong session that, guardian
fail neu pill khong hien), 9799741 (F4 CLOSED, probe 5 PASS live
18:44:14). Nhanh local cung da duoc fast-forward len 9799741 trong luc
toi lam (shared checkout). Commit 9c9fea9 va 9799741 ghi ro: "cdp.mjs
hunks uncommitted on VM pending W-PILLCDP landing, patched directly on
the laptop" va "Open item: VM cdp.mjs fix uncommitted pending
W-PILLCDP landing". Thu tu dinh san: toi land pill truoc, W-F4FIX land
hunk cdp.mjs cua ho sau. Vi vay commit scripts/cdp.mjs cua toi CHI stage
4 hunk pill (loc diff, verify staged khong co hunk F4, unstaged chi con
hunk F4), de cong viec cua W-F4FIX nguyen ven trong worktree.

## 2026-11-22 18:47 +07, T+15m: LOI COMMIT (pathspec --only) VA CACH SUA

d0602dd (push 18:47) le ra chi chua pill, nhung thuc te chua ca hunk F4:
`git commit -- <paths> -m` (pathspec lam doi so) kich hoat hanh vi
--only: git bo qua index da stage, ghi lai NOI DUNG WORKTREE cua cac
file do. Worktree cdp.mjs luc do co ca hunk F4 nen hunk do lot vao commit
va message commit noi sai su that. Phat hien khi kiem tra sau push:
git show d0602dd -- scripts/cdp.mjs = 100 insertions (pill 88 + F4 11).
Sua ngay, khong amend (commit da push): d28cad0 (push 18:48) chi go
dung hunk F4 (1 file, 1 insertion, 12 deletions), message giai thich
ro loi. Sau do khoi phuc lai hunk F4 vao worktree (uncommitted) de
W-F4FIX land sau nhu ke hoach. Verify: git show d28cad0:scripts/cdp.mjs
byte-identical voi ban pill-only trong /tmp/pillcheck (ban da chay xanh
7/7 suite node + 108 test python), nen HEAD hien tai xanh. Bai hoc:
KHONG BAO GIO dung pathspec lam doi so cho git commit khi worktree co
thay doi cua worker khac; chi `git add -- <paths>` roi `git commit -m`
khong pathspec. Commit log nay cung dung cach do.
