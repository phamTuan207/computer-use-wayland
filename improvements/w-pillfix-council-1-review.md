# Council 1 review: W-PILLFIX 8f600b9 (co che + bang chung)

Review doc lap cho COORD-CLICK-9, khong nhan truc tiep cho the owner.
Lens cua Council 1: co che + bang chung. Moi gio Asia/Ho_Chi_Minh.
Khong dung dau gach ngang dai. Khong ydotool. Khong thong tin ca nhan.
Khong tu cham diem. Chuan Lauren Tan: lenh + output + thoi gian.

## Verdict: GO VOI DIEU KIEN

Fix dung nguyen nhan goc, dung co che, so lieu test trong message commit
da duoc chay lai va khop dung. Dieu kien khong chan viec land (fix da
deploy va W-PILLVERIFY2 da PASS doc lap, commit 9ac4dcd tren laptop),
chi la viec hoan thien ho so va don dep:

1. Commit log W-PILLFIX (hien untracked, 425 dong) de ho so commit
   khong chi co code. Phan tai tao cua closeout da ghi ro nguon tung
   claim, Council 1 da kiem chung doc lap cac claim chinh o muc 5.
2. Release holder smoke W-PILLFIX (acquired 19:40:45, pid null) khi
   verify xong, do COORD-CLICK-9 hoac W-PILLVERIFY2 quyet dinh.
   Council 1 khong tu release vi S2-flip đang dùng pill live.
3. Follow-up nit (khong chan): ghi ro `overlay.py status` co side
   effect reconcile (muc 4d) va sua docstring stale cua
   `first_action.overlay_visible` (muc 4e).

## 1. Pham vi review va thoi gian

- Nhan viec: 2026-11-22 19:48:05 +07. Ket thuc viet review: 19:58 +07.
- Repo: ~/workspace/computer-use-wayland, branch todolist-push.
  HEAD luc review: 8f600b9, parent e200d6e (xac nhan bang
  `git log --oneline -8`, 19:48 +07).
- Commit duoc review: 8f600b933728e29c3889948de0da7c80a8c14eb3,
  4 files, 240 insertions, 13 deletions:
  scripts/overlay.py, scripts/indicator.py,
  tests/test_overlay.py, tests/test_indicator.py.
- Council 1 chi review, khong sua code, khong viet log thay W-PILLFIX.
  Laptop chi doc qua ssh-laptop.sh, khong sua gi tren laptop.

## 2. Nguyen nhan goc: DUOC CHUNG MINH

Chuoi bang chung day du, moi mat xich deu co nguon doc lap:

a) Loi goc (W-PILLVERIFY, log e200d6e, commit e200d6e597c71451ad77ba6f178ab554d13a32d3):
act CDP 19:20:00 bi tu choi `CDP pill unavailable: final liquid-glass
profile unavailable; restore the pinned plugin before computer-use`,
completed 0, grim khong co pill, daemon.log lap native_spawn_failed
1102 lan tinh toi 19:16, khong co session.json.

b) Code cu doc sai thu muc (xac nhan truc tiep tu git):
`git show e200d6e:scripts/overlay.py` dong 200-215, wayland_env cu doc
`/run/user/1000/hyprland`. Council 1 kiem tra live tren laptop
19:50:29 +07 qua ssh-laptop.sh:
`ls: cannot access '/run/user/1000/hyprland': No such file or directory`,
trong khi `ls /run/user/1000/hypr/` tra ve dung 1 thu muc signature
`11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795342782_301493614`.

c) Thieu SIG dan toi dung loi do (co che trong code, khong phai suy doan):
`scripts/indicator.py` `_status` tra None ngay khi thieu
HYPRLAND_INSTANCE_SIGNATURE hoac WAYLAND_DISPLAY; `_valid_liquid(None)`
la False; `native/require-liquid` ton tai nen nhanh `final` bat va raise
dung text loi tren. Log W-PILLFIX ghi tai hien clean-env: khong SIG thi
`liquid_available` False, status None; co SIG dung thi True.

d) Hyprglass khoe (kiem chung live 19:50-19:51 +07):
`hyprctl -j hyprglass status` voi SIG dung tra ve schema 1, version
1.1.1-cu.1, versionCheck match, active true, shaders ready, layers
enabled true active true reason null, windows/subsurface disabled.
`hyprctl plugin list`: hyprglass 1.1.1-cu.1 loaded, kem hyprbars 1.0 va
computer-use-cursor 1.0. Vay text loi noi plugin mat la sai huong dan,
dung nhu message commit noi.

e) Daemon cu khong co SIG, daemon moi co SIG (kiem chung live):
log W-PILLFIX ghi environ daemon cu PID 76088 chi co XDG_RUNTIME_DIR va
WAYLAND_DISPLAY, khong co SIG. Council 1 doc `/proc/115582/environ`
19:50 +07: daemon moi co du
HYPRLAND_INSTANCE_SIGNATURE=11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795342782_301493614,
WAYLAND_DISPLAY=wayland-1, XDG_RUNTIME_DIR=/run/user/1000.

Ket luan muc 2: nguyen nhan goc duoc chung minh, khong phai gia thuyet.
Diem tru duy nhat: phan log goc cua W-PILLFIX (19:23-19:40) khong co
trong commit 8f600b9; bang chung restart/smoke chi co trong file
working-tree (xem muc 5).

## 3. Co che fix: DUNG

a) Uy thac cho hypr_cmd.desktop_env la dung source of truth.
`scripts/hypr_cmd.py` dong 12 ghi ro "Signature discovery:
ls /run/user/1000/hypr/ (NOT hyprland/, which is empty)",
HYPR_SIGNATURE_DIR = "/run/user/1000/hypr". desktop_env fail-closed
bang ValueError khi khong list duoc dir hoac dir rong. wayland_env moi
truyen `signature_dir=str(runtime / 'hypr')`, bat (ImportError,
ValueError) va tra env khong SIG nhu cu de spawn fail loud thay vi
crash. Khong co duong nao KeyError duoc: dict tra ve la literal du 3 key,
OSError da duoc desktop_env doi thanh ValueError.

b) SIG do caller truyen duoc giu nguyen (nhanh moi + test). Hanh vi nay
doi so voi code cu (cu ghi de SIG bang sig_dirs[0] neu tim thay), nhung
doi nay dung: SIG cua caller đang chạy khong co ly do gi de bi ghi de.
He qua nho: SIG stale do caller truyen cung duoc tin (khong re-discover).
Thuc te khong anh huong vi caller chinh la daemon (khong co SIG) va test.

c) Fail-closed status: `Daemon.status_reply` goi `apply_holders` roi moi
bao. Cu la `{'visible': bool(holders)}`, noi doi truc tiep va da lac
huong lane verify (W-PILLVERIFY log 19:14:49). Moi tra visible False
kem error khi spawn/show that bai. Xem luu y side effect o muc 4d.

d) Fail-closed acquire: `cmd_acquire` exit 1 + go holder vua them khi
reply visible khong phai True, van in reply JSON de chan doan, log
`acquire_invisible` ra stderr. Tuong thich caller, da kiem tra tung
caller (19:52 +07):
- `overlay.hold` dung `check=True` (scripts/overlay.py dong 625-630),
  nen exit 1 raise CalledProcessError, dung nhu docstring cua
  `chromium_cli._pill_hold` (dong 640-648) von mo ta sai truoc fix.
- `scripts/cdp.mjs` dong 57, 66-67: throw `CDP pill unavailable` ca khi
  exit non-zero lan khi reply.visible !== true.
- `scripts/s2_flip_live.py` `cdp_pill_hold` (dong 607-640): chi check
  rc == 0, that bai thi warn-only, gate that la cdp.mjs. Tuong thich.
- `scripts/first_action.py` `acquire_overlay` (dong 116-150) dung socket
  truc tiep va tu check visible, khong anh huong.

e) Fail-closed status khong-daemon: `cmd_status` chi bao visible True
khi `session_live()` (doc SESSION_FILE + probe indicator.request).
Dung: holders mot minh khong render duoc pill khi khong co daemon.

f) Indicator metric: chi them 1 dong stderr `_metric`
('liquid_unavailable', probe=no_session_env|invalid_status), text
exception giu nguyen y het (test pin). Phan biet duoc probe khong chay
(thieu SIG/WAYLAND) voi probe chay ra status khong hop le. Dung muc
dich chan doan.

g) Session path khong anh huong: `apply_holders` chi spawn native khi
`session_live()` False; khi session song thi owner='session', khong
spawn. Dung nhu message commit noi.

## 4. Quan sat nho (khong chan)

a) `desktop_env` chon sorted()[0] trong hypr/, ke ca file lac va instance
cu neu co nhieu dir. Cung luat voi moi cho khac dung desktop_env; spawn
tu validate bang `_status`, SIG sai chi dan toi loi cu, khong pill sai.
Chap nhan duoc, log W-PILLFIX da ghi redteam nay.

b) Full suite chay cham hon khi chay song song (294s o lan chay cua
Council 1, 268s cua closeout, 216-220s cua W-PILLFIX luc chay mot minh).
Chi la nhieu CPU, khong phai regression.

c) `test_phase3_cleanup` FAIL khi co lane khac chay song song (closeout
gap failures=2, Council 1 khong gap). Test nay kiem tra desktop sach
nen guardian cua lane khac lam no FAIL; chay rieng thi OK (5 tests).
Khong lien quan fix.

d) `overlay.py status` khong con la pure read. `status_reply` chay
`apply_holders`, tuc la lenh status co the spawn native (lan dau cho
shader toi da LIQUID_READY_TIMEOUT 30s + ready 3s) va ghi label/show.
Council 1 quan sat truc tiep: lenh `overlay.py status` luc 19:50:29
+07 sinh cac dong label "Muse via CDP" + show trong daemon.log, va
`_ensure_daemon` probe status voi timeout 2s se timeout lan dau roi
retry. Monitor von chay apply_holders moi 2s nen day khong phai class
side effect moi, nhung can ghi ro trong docstring/docs de lane sau
khong ngac nhien khi status cham hoac status tu nang pill.

e) Docstring stale: `first_action.overlay_visible` van ghi "a 'status'
reply only says holders exist, not that the pill rendered". Sau fix nay
cau do sai. Sua o follow-up, khong chan.

f) Holder pid-less van khong tu prune duoc (S2-flip re-acquire 19:36:53
roi 19:53:37, actor khong xac dinh; holder smoke W-PILLFIX con sot).
Fix log da quyet dinh co chu y la KHONG them auto-prune theo tuoi.
Council 1 dong y quyet dinh nay, chi ghi nhan ve sinh holder van la
viec tay.

## 5. So lieu test: CHAY LAI VA KHOP DUNG

Tat ca so duoi day la do Council 1 tu chay tren VM, khong chep tu
message commit. Repo tai 8f600b9, tru phi ghi khac.

### 5a. Targeted suites, 19:49:44-19:49:45 +07

Lenh: `python3 -m unittest discover -s tests -p '<file>.py'` tung file.

| Suite | Ket qua cua Council 1 | Message commit |
|---|---|---|
| test_overlay.py | Ran 19 tests, OK | 19 |
| test_indicator.py | Ran 43 tests, OK | 43 |
| test_hypr_cmd.py | Ran 24 tests, OK | 24 |
| test_s2_flip_pill.py | Ran 3 tests, OK | 3 |
| test_indicator_ink.py | Ran 6 tests, OK | 6 |
| test_indicator_material.py | Ran 3 tests, OK | 3 |
| test_indicator_native.py | Ran 1 test, OK | 1 |

Khop dung ca 7 con so.

### 5b. Full suite, bat dau 19:49:57 +07

Lenh: `python3 -m unittest discover -s tests -p 'test_*.py'`
(log /tmp/c1-fullsuite.log).
Ket qua: `Ran 2313 tests in 294.450s, FAILED (failures=1, errors=2,
skipped=17)`, tuc 2310/2313 pass, khop dung message commit.
3 loi, ten lay tu log:
- ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26).
- ERROR test_tc02_controller.Tc02MenuBarTests
  .test_typed_text_check_passes_when_fragment_is_visible
  (`tesseract is unavailable; refusing to assume text presence`).
- FAIL test_tc02_controller.Tc02MenuBarTests
  .test_typed_text_check_fails_when_fragment_is_absent
  (`'20:30' not found in 'tesseract is unavailable...'`).

### 5c. 3 loi la co san, chung minh tren baseline e200d6e

Worktree sach /tmp/c1-baseline tai e200d6e (khong co fix), chay
19:52:01-19:52:02 +07:
- test_cursor_file.py: Ran 0 tests, FAILED (errors=1).
- test_tc02_controller.py: Ran 46 tests, FAILED (failures=1, errors=1).
- `which tesseract` rong; `g++ --version` 13.3.0 (khong ho tro C++26).
Giong het 3 loi tren code fix. Fix gay 0 regression.
Closeout chay song song gap them 1 FAIL test_phase3_cleanup (muc 4c);
lan chay cua Council 1 khong gap, nen day la nhieu dong thoi, khong
phai regression.

### 5d. Test moi co bao phu dung loi goc khong: CO

Chay 8 test moi (7 overlay + 1 indicator) tren code CU o worktree
baseline e200d6e, 19:50:14-19:50:18 +07, bang cach copy file test moi
tu 8f600b9 sang worktree:
- test_overlay.py: FAILED (failures=2, errors=2).
- test_indicator.py: FAILED (failures=2).
Cac test that bai tren code cu:
- test_wayland_env_discovers_signature_from_hypr_dir: ERROR
  (KeyError, code cu khong tim duoc SIG). Day la test tai hien TRUC
  TIEP loi goc.
- test_status_reply_reports_real_visibility: ERROR (khong co ham).
- test_cmd_acquire_refuses_when_pill_invisible: FAIL (code cu tra 0).
- test_cmd_status_no_daemon_is_session_aware: FAIL (owner sai).
- test_final_profile_rejection_names_probe_cause: FAIL ca 2 sub-case
  (stderr khong co probe).
3 test moi con lai pass ca tren code cu, la guard test (giu SIG caller,
khong instance thi khong SIG, acquire visible van thanh cong), khong
phai test tai hien. Ho so bao phu tot: 5/8 test moi that su bat duoc
hanh vi cu, trong do co dung test tai hien loi goc.

### 5e. Kiem chung live tren laptop (chi doc, 19:50-19:51 +07)

- Daemon moi PID 115582, started 19:40, chay tu
  ~/computer-use-wayland/scripts/overlay.py daemon.
  Environ co SIG dung (muc 2e). Native indicator song.
- Dong native_spawn_failed CUOI CUNG trong daemon.log:
  19:40:29.377 +07; tong 1839 lan trong lich su file log, 0 lan tu
  19:40:30 tro di (kiem tra 19:50:29). Khop log closeout (kiem tra
  19:54:33 cung ket luan).
- `overlay.py status` luc 19:51: visible True, owner daemon, label
  'W-PILLFIX via smoke', holders [S2-flip, W-PILLFIX].
- Grim /tmp/c1-pill-check.png (laptop, 19:51, 523619 bytes, md5
  ff0297586ec951d8d22b130f8f1689ca): pill HIEN o giua tren man hinh,
  ghi 'W-PILLFIX via smoke'. Ban nho tren VM /tmp/c1-pill-small.jpg.
  Day la bang chung pixel do Council 1 tu chup va xem, khong lay tu
  log khac.
- Code đang chạy khop commit: sha256 tren home checkout laptop khop
  dung `git show 8f600b9` cho ca 4 file (overlay
  b551cf6b2e1503824c690f46dae5ce88c90dfca6cf0f0761699e808717be59b4,
  indicator
  4008141bc28ca1b6ba2865ef6a05eb8a4d837c3ca7675f5daa2e06d05e3a43ac,
  test_overlay e0464d4e498ecc0884a0feecc3e0a09349a2b098e9001e762918a1fb529555d5,
  test_indicator 635858ee74f4728940b69c075e9814a4875f65d737e2a8e0a882c58045afab0d).
- W-PILLVERIFY2 da PASS doc lap sau fix (commit 9ac4dcd tren laptop,
  "live pill render PASS after 8f600b9, CDP act ok, gate 4.29 met").
  Council 1 ghi nhan nhu bang chung phu, khong dung lam co so verdict
  chinh; verdict dung tren muc 2, 3, 5a-5d.
- Luu y dong thoi: luc 19:50:29 status thay holder tam Muse:122139
  (acquired cung giay), toi luc 19:51 da bien mat; nhieu lane live đang
  chay song song, holder S2-flip re-acquire 19:53:37. Council 1 khong
  cham vao holder nao.

## 6. Lo hong bang chung

- Ho so commit 8f600b9 KHONG co log: commit chi co 4 file code/test.
  File improvements/w-pillfix-log.md tren working tree luc review bat
  dau chi co 274 dong, ket o quyet dinh doi restart 19:40, khong co
  ket qua restart, khong co bao cao cuoi. Phan closeout (19:48-19:55,
  425 dong luc 19:56:53) tai tao phan thieu va ghi ro nguon tung claim;
  Council 1 da kiem chung doc lap cac claim chinh (daemon moi + SIG,
  spawn thanh cong, loi cuoi 19:40:29, hash code, so test targeted).
  Lo hong nay da thu hep nhung chua dong: file van untracked luc
  review, can commit (dieu kien 1).
- Log goc khong co anh grim; bang chung pixel chi co tu W-PILLVERIFY2
  va grim cua Council 1 (muc 5e). Du cho verdict, nhung lan sau log
  fix nen kem grim.
- Actor re-acquire S2-flip (19:36:53, 19:53:37) chua xac dinh. Khong
  anh huong verdict.

## 7. Ket luan

Nguyen nhan goc duoc chung minh bang ca code, tai hien clean-env va
kiem chung live. Fix dung co che (desktop_env la source of truth),
fail-closed dung cho, tuong thich het caller. Test moi bao phu dung
loi goc (5/8 test bat duoc hanh vi cu). So lieu commit khop dung khi
chay lai (targeted 7/7, full suite 2310/2313, 3 loi env co san da
chung minh tren baseline). Live: daemon moi co SIG, khong loi spawn
tu 19:40:30, pill hien tren anh grim 19:51, W-PILLVERIFY2 PASS doc lap.
Verdict: GO VOI DIEU KIEN (3 dieu kien o dau file, khong chan land).

## 8. Cap nhat luc khoa review, 19:59 +07

- Dieu kien 1 da duoc dap ung trong luc review: W-PILLFIX-CLOSEOUT da
  commit log o 394a989 (2026-11-22 19:55:29 +07, "complete
  w-pillfix-log.md with restart 19:40:45, smoke show ack and re-run
  test evidence"). Ho so commit cua 8f600b9 nay co log day du tren
  origin/todolist-push. Con lai dieu kien 2 (release holder smoke) va
  dieu kien 3 (nit ve status side effect + docstring stale).
- Ghi nhan them tu git log origin (chi doc tieu de commit, khong dung
  lam co so verdict): Council 2 cung review 8f600b9 voi verdict
  GO VOI DIEU KIEN (commit 8246a9a), va W-PILLVERIFY2 PASS
  (commit 9ac4dcd).
