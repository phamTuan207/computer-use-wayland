# GHI CHU CLOSEOUT (W-PILLFIX-CLOSEOUT, 2026-11-22 19:48-19:55 +07)
#
# File nay la log TAI TAO sau su viec, hoan thien tu log goc con thieu.
# Su that ve nguon goc, ghi ro de COORD-CLICK-9 khong hieu lam: W-PILLFIX
# CO viet mot log dong thoi (274 dong, ket o quyet dinh doi restart 19:40),
# nhung file do nam o trang thai untracked, chua bao gio commit/push, va
# khong co bao cao cuoi. Closeout giu nguyen 274 dong do (khong sua mot
# chu nao), chi them phan duoi tu muc "## CLOSEOUT" tro di. Moi claim trong
# phan closeout ghi ro nguon: commit diff 8f600b9, test chay lai tren VM,
# hoac log laptop doc qua ssh-laptop.sh. Khong claim nao chep mu tu message
# commit; tung con so test deu chay lai va doi chieu. Khong tu cham diem,
# khong tuyen bo gate dat. Gate todolist 4.29 KHONG thuoc ve
# W-PILLFIX-CLOSEOUT; W-PILLVERIFY2 verify doc lap sau.
# Khong dung dau gach ngang dai. Khong ydotool. Khong thong tin ca nhan.
#
# W-PILLFIX log: sua loi pill render standalone (native spawn down)

Lane sua loi cua COORD-CLICK-9 phase live. Bao cao cho COORD-CLICK-9, khong nhan
truc tiep cho the owner. Moi gio ghi theo Asia/Ho_Chi_Minh. Khong dung dau
gach ngang dai. Khong ydotool. Khong thong tin ca nhan len GitHub. Khong tu
cham diem. Log lien tuc voi thoi gian (wall-clock + elapsed). Chuan Lauren Tan:
lenh chay + output + commit hash + log thoi gian.

Loi goc (W-PILLVERIFY, log e200d6e): act CDP 19:20:00 tren tab scratch bi tu
choi, `CDP pill unavailable: final liquid-glass profile unavailable; restore
the pinned plugin before computer-use`, completed 0, grim khong co pill.
Gate todolist 4.29 CHUA DAT. Mei chua duoc chay live run cho den khi loi nay
sua xong va verify lai PASS boi worker doc lap khac (W-PILLVERIFY2).

## 2026-11-22 19:23:52 +07, T+0m: nhan viec

Task tu COORD-CLICK-9. May laptop dang ranh (the owner treo may 19:10, ong
KHONG ngoi truoc may). Bo qua moi tin hieu bao ong dang dung may, tat ca la
tin hieu gia, khong gate live work tren idle check. Khong dong/navigate tab
nao cua the owner (mochi A67A718D, fixture 025266AE, Brave cua mei, tab Zen);
can thi mo tab scratch moi ben canh. Pill PHAI hien khi dieu khien may.

## 2026-11-22 19:24:22 +07, T+1m: trang thai ban dau tren laptop

- Laptop repo /home/james/workspace/computer-use-wayland, HEAD e200d6e
  (W-PILLVERIFY log), sach ngoai file untracked co san.
- Daemon overlay PID 76088, started 18:40:32, chay tu
  /home/james/computer-use-wayland/scripts/overlay.py (ban install, khong
  phai workspace repo). holders.json chi con S2-flip (acquired 18:43:50,
  pid null). Khong co session.json nen khong co session indicator nao song.
- Daemon log: native_spawn_failed lap moi 2s, 1345 lan tinh toi 19:24, cung
  loi liquid-glass. Loi dau tien ngay 18:40:32.524, elapsed_ms 19, tuc la
  daemon nay CHUA BAO GIO spawn duoc native trong ca vong doi cua no.
- native/require-liquid TON TAI o ban install /home/james/computer-use-wayland
  (0 byte, 15/11 02:00, do setup tao), nen nhanh `final` trong
  indicator.Native BAT. Trong workspace repo thi file nay khong co (generated
  local config, khong tracked), nhung daemon khong chay tu workspace repo.
- overlay.py va indicator.py giong het nhau giua 3 ban: workspace repo,
  home checkout /home/james/computer-use-wayland, installed tree
  ~/.local/share/agent-computer-use (diff rong).

## 2026-11-22 19:24-19:28 +07, T+1-5m: nghien cuu, tim nguyen nhan that

Doc docs/overlay.md, docs/liquid-glass.md, scripts/overlay.py (613 dong),
scripts/indicator.py (283 dong), scripts/cdp.mjs gate (dong 1-90),
scripts/chromium_cli.py _pill_hold (dong 630-660), scripts/first_action.py
(acquire_overlay, overlay_visible), scripts/hypr_cmd.py desktop_env,
scripts/s2_flip_live.py cdp_pill_hold, tests/test_overlay.py,
tests/test_indicator.py (NativeStartup).

Phat hien 1, quyet dinh: hyprglass HOAN TOAN KHOE, plugin KHONG can restore.

- `hyprctl -j hyprglass status` (voi SIG dung) tra ve profile hop le day du:
  schema 1, version 1.1.1-cu.1, versionCheck match, active true, shaders
  ready, layers enabled true active true reason null, windows/subsurfaces
  enabled false. `_valid_liquid` tra True voi status nay.
- `hyprctl plugin list`: hyprglass 1.1.1-cu.1 loaded, kem hyprbars 1.0 va
  computer-use-cursor 1.0. Hyprland 0.57.2 dung pin.
- Vay loi 'final liquid-glass profile unavailable' KHONG co nghia plugin
  mat. No chi co nghia `_valid_liquid(status)` la False, ma status co the
  la None khi khong probe duoc.

Phat hien 2, NGUYEN NHAN GOC: daemon khong co HYPRLAND_INSTANCE_SIGNATURE.

- Environ cua daemon PID 76088 chi co XDG_RUNTIME_DIR=/run/user/1000 va
  WAYLAND_DISPLAY=wayland-1, KHONG co HYPRLAND_INSTANCE_SIGNATURE.
- `indicator._status(env)` tra None ngay khi thieu SIG hoac WAYLAND_DISPLAY
  (dong 197-198), nen liquid=False, final=True, Native raise loi tren.
- `overlay.wayland_env()` (dong 194-215) tim sig dir o
  `/run/user/1000/hyprland`, thu muc nay KHONG TON TAI tren may
  (ls bao No such file). Sig dir that nam o `/run/user/1000/hypr/<sig>`.
- Cung repo da biet dieu nay: scripts/hypr_cmd.py dong 12 ghi ro
  "Signature discovery: ls /run/user/1000/hypr/ (NOT hyprland/, which is
  empty)", HYPR_SIGNATURE_DIR = "/run/user/1000/hypr", va
  desktop_env() dung thu muc do. overlay.py la cho DUY NHAT con dung
  duong cu. Bai hoc 21/11 trong AGENTS.md cung ghi /run/user/1000/hyprland
  rong la bug lam SIG blank, nhung overlay.py chua bao gio duoc sua.
- Tai sao duong session van chay tot luc 18:43 (W-F4FIX, 6 phien probe deu
  co pill): session_live() chi probe socket cua session indicator da song,
  khong bao gio spawn Native, khong bao gio goi _status. Chi duong spawn
  standalone bi hong. Dung nhu mo ta trong task.

Phat hien 3, TAI HIEN XAC DINH (clean env, khong SIG):

- `env -i PATH=/usr/bin:/bin HOME=/home/james python3 -c` goi
  overlay.wayland_env() roi indicator.liquid_available(env):
  SIG None, WAYLAND wayland-1, liquid_available False, status None.
- Cung lenh voi SIG dung + WAYLAND_DISPLAY=wayland-1:
  liquid_available True.
- Vay: sua wayland_env la du de spawn lai duoc. Khong can dong den plugin,
  khong unload/reload, khong xoa require-liquid, khong doi cdp.mjs gate.

Phat hien 4, daemon log lich su: `grep -c native_spawned` = 313 lan trong
file log (cac daemon doi truoc, vd 21/11 04:56 va 05:01 spawn thanh cong).
Daemon hien tai (18:40:32) spawn 0 lan thanh cong. Dieu nay phu hop voi
gia thuyet: daemon doi truoc duoc khoi dong tu shell co du SIG (hoac
hyprland/ luc do con ton tai), daemon 18:40 duoc khoi dong qua SSH khong
SIG (S2-flip) nen hong tu giay dau tien.

## Council 3 + redteam truoc khi sua (19:28 +07)

Ghi chu pham vi: worker nay chay o depth 2/2, khong spawn duoc subagent
(can_spawn=no), nen council o day la deliberation co cau truc ghi thang vao
log voi 3 vi tri doc lap + redteam, de COORD-CLICK-9 va worker verify doc
lap (W-PILLVERIFY2) soi lai. Khong co claim nao ve council chay rieng ma
khong co bang chung.

- Evidence (co che): dong y nguyen nhan goc la wayland_env doc sai thu muc
  sig. Bang chung: tai hien clean-env, daemon environ thieu SIG, hyprglass
  status hop le voi SIG dung, loi dau tien o elapsed 19ms. Fix: wayland_env
  uy thac cho hypr_cmd.desktop_env() (nguon that duy nhat, da duoc chung
  minh), chi lay SIG + WAYLAND_DISPLAY tu do, giu nguyen env day du cua
  caller. Khong dong plugin, khong doi gate cdp.mjs, khong xoa
  require-liquid (fail-closed giu nguyen).
- Safety (fail-closed): dong y voi dieu kien: (1) cmd_acquire exit 1 khi
  visible False van tuong thich cdp.mjs vi no da throw ca khi reply
  visible!==true lan khi overlay.py exit non-zero, deu thanh
  'CDP pill unavailable'; (2) s2_flip tuong thich vi no chi check rc==0,
  that bai thi warn-only, gate cung van ap dung; (3) status goi
  apply_holders khong them side-effect moi vi monitor thread da goi
  apply_holders moi 2s; (4) restart daemon bang `stop` chi sau khi xac
  minh khong co run nao song (ps, khong session.json, Mei dang bi gate).
- Scope (sua phu): (a) FIX status bao visible theo bool(holders): status
  noi doi truc tiep lam lane verify lac huong, va first_action.py da ghi
  ro status chi noi holders ton tai chu khong phai pill render (no phai
  dung 'sync' de tranh). Sua: daemon 'status' tra apply_holders(), CLI
  khong-daemon thi session-aware. (b) FIX overlay.hold() / cmd_acquire
  khong kiem tra visible: W-PILLVERIFY chung minh live `open` van thanh
  cong khi pill khong render, docstring cua _pill_hold noi hold raise
  CalledProcessError la SAI hien tai. Sua: cmd_acquire exit 1 + go holder
  vua them khi visible False (theo dung mau D1 da co, va mau
  acquire_overlay trong first_action.py). (c) PRUNE holder S2-flip stale
  bang tay luc restart daemon (sau khi xac minh khong run nao song), KHONG
  them code auto-prune theo tuoi cho holder pid-less (khong an toan: holder
  pid-less co the thuoc run dang song khong truyen pid).
- Redteam phan bien: (1) Nhieu sig dir thi sorted()[0] co the chon sai
  instance cu? Chap nhan: cung luat voi desktop_env, va spawn path tu
  validate bang _status, SIG sai chi dan toi cung loi cu, khong pill sai.
  (2) status goi apply_holders co the block toi 30s khi shader compiling?
  Chi lan spawn dau tien, monitor da lam dieu do; sau spawn thi apply
  nhanh (label+show). Chap nhan. (3) cmd_acquire exit 1 co caller nao
  phu thuoc exit 0 khi invisible khong? Da grep: cdp.mjs (tuong thich),
  s2_flip (rc check, tuong thich), overlay.hold check=True (day la muc
  tieu: phai raise), first_action dung socket truc tiep (khong anh huong).
  (4) Go holder khi invisible co lam mat co hoi retry cua monitor khong?
  Co, nhung holder pid-less le ra se ket vinh vien (dung benh S2-flip);
  caller muon retry thi acquire lai. Fail-closed + khong leak thang.
  (5) Co nen doi text loi 'final liquid-glass...' khong? KHONG doi text
  exception (test test_indicator.py dong 118 pin dung text do). Chi them
  mot dong metric stderr phan biet probe='no_session_env' vs
  'invalid_status' de lan sau chan doan nhanh. Khong doi hanh vi.
- Verdict council: FIX (a) + (b) + root cause cung lan nay, (c) don tay
  luc restart. Khong sua plugin, khong sua gate cdp.mjs, khong xoa
  require-liquid.

## Ke hoach trien khai

1. Sua scripts/overlay.py: wayland_env uy thac desktop_env; Daemon.status
   tra apply_holders (tach thanh status_reply de test duoc); cmd_acquire
   exit 1 + go holder khi visible False; cmd_status khong-daemon thi
   session-aware.
2. Sua scripts/indicator.py: Native log metric phan biet no_session_env
   vs invalid_status truoc khi raise (text exception giu nguyen).
3. Them test vao tests/test_overlay.py va tests/test_indicator.py.
4. Chay test cuc bo tren VM: test_overlay, test_indicator, test_hypr_cmd,
   test_s2_flip_pill, test_indicator_native, roi full discover.
5. Commit nho (git add -- paths tuong minh, git commit -m, KHONG commit
   tran, KHONG add -A, KHONG amend), push, verify ls-remote.
6. Deploy len laptop: pull workspace repo (ff-only); cap nhat home checkout
   /home/james/computer-use-wayland (no bi chan boi cdp.mjs dirty: chi copy
   file da sua, khong dong cdp.mjs); thu sync-installed.py cho installed
   tree neu chay sach (relay dang idle).
7. Restart daemon (stop roi acquire moi) sau khi xac minh khong run song;
   smoke check cuc bo: acquire + grim thay pill + release. KHONG tu tuyen
   bo gate dat; W-PILLVERIFY2 verify doc lap sau.

## 2026-11-22 19:29-19:32 +07, T+6-9m: sua code

File sua (VM repo, branch todolist-push):
- scripts/overlay.py (+75/-? dong, xem diff): wayland_env uy thac
  hypr_cmd.desktop_env (sig dir /run/user/1000/hypr/); giu nguyen SIG do
  caller truyen; khong tim duoc instance thi tra env khong SIG nhu cu.
  Daemon.status_reply() moi tra apply_holders(); handler 'status' dung no.
  cmd_acquire exit 1 + go holder vua them khi reply visible False, log
  acquire_invisible ra stderr, van in reply JSON. cmd_status khong-daemon
  thi session-aware (visible chi True khi session_live()).
- scripts/indicator.py (+12 dong): Native log metric
  liquid_unavailable probe=no_session_env|invalid_status ra stderr truoc
  khi raise; text exception giu nguyen y het (test pin).
- tests/test_overlay.py (+145 dong): 7 test moi (wayland_env tim sig tu
  hypr/, giu SIG caller, khong instance thi khong SIG, status_reply that,
  cmd_status session-aware, cmd_acquire tu choi khi invisible + khong leak
  holder, cmd_acquire visible van thanh cong).
- tests/test_indicator.py (+21 dong): 1 test moi, 2 case (env rong thi
  no_session_env, env co SIG thi invalid_status), exception text khong doi.

Khong sua: plugin hyprglass, require-liquid, gate cdp.mjs, chromium_cli.py,
s2_flip_live.py, first_action.py. Khong them auto-prune theo tuoi.

## 2026-11-22 19:30-19:32 +07, T+7-9m: test cuc bo tren VM (targeted)

Lenh: `python3 -m unittest discover -s tests -p 'test_overlay.py'` etc.
- test_overlay.py: 19 tests, OK (12 cu + 7 moi).
- test_indicator.py: 43 tests, OK (42 cu + 1 moi).
- test_indicator_native.py: 1 test, OK.
- test_hypr_cmd.py: 24 tests, OK.
- test_s2_flip_pill.py: 3 tests, OK.
- test_indicator_ink.py: 6 tests, OK.
- test_indicator_material.py: 3 tests, OK.
- Luu y: chay bang `python3 -m unittest tests.test_overlay` se loi
  ModuleNotFoundError _function_test_support (do cach chay sai, khong phai
  do code); dung discover nhu docs/testing.md moi dung.
- Full suite `python3 -m unittest discover -s tests -p 'test_*.py'` dang
  chay background (timeout 280s), ket qua cho o muc sau truoc khi commit.

## 2026-11-22 19:34-19:38 +07, T+11-15m: full suite + chung minh 3 loi la co san

- Full suite lan 1 (220s): Ran 2313 tests, FAILED (failures=1, errors=2,
  skipped=17). 3 loi deu o test_tc02_controller / test_cursor_file.
- Full suite lan 2 (ghi /tmp/w-pillfix-fullsuite.log, 216s): Ran 2313
  tests, FAILED (failures=1, errors=2, skipped=17), cung 3 loi:
  ERROR setUpClass test_cursor_file.CursorFileTests (g++ -std=c++26
  compile loi tren VM), ERROR + FAIL test_tc02_controller.Tc02MenuBarTests
  (tesseract is unavailable; VM khong co tesseract, `which tesseract`
  rong). Khong loi nao cham overlay/indicator.
- Chung minh co san bang worktree sach /tmp/w-pillfix-baseline o e200d6e
  (khong co fix): test_cursor_file FAILED errors=1, test_tc02_controller
  FAILED failures=1 errors=1, giong het. Worktree da xoa sau khi check.
- Ket luan: fix nay gay 0 regression. 2310/2313 pass, 3 loi moi truong co
  san tu truoc.
- Fast-forward VM repo len origin/todolist-push e200d6e truoc khi commit
  (local truoc do o 929decf, behind 1; merge --ff-only thanh cong vi
  e200d6e chi them w-pillverify-log.md).
- Commit code 8f600b9 (4 files, 240 insertions, 13 deletions), push
  todolist-push, ls-remote xac nhan 8f600b933728e29c3889948de0da7c80a8c14eb3.

## 2026-11-22 19:38-19:40 +07, T+15-17m: deploy len laptop

- Laptop workspace repo: fetch + merge --ff-only origin/todolist-push,
  len 8f600b9 (merge output 4 files, 240 insertions).
- Home checkout /home/james/computer-use-wayland: git pull bi chan nhu du
  doan (cdp.mjs dirty, upstream doi file nay tu 331523f). Xu ly: chi copy
  4 file da sua (scripts/overlay.py, scripts/indicator.py,
  tests/test_overlay.py, tests/test_indicator.py) tu workspace repo sang,
  sha256 khop ca 2 file scripts (overlay b551cf6b..., indicator
  4008141b...). cdp.mjs KHONG dong vao (diff van dung 13 dong nhu cu).
  Home checkout hien M 5 file (cdp.mjs cua nguoi khac + 4 file cua fix);
  noi dung 4 file fix bang dung commit 8f600b9 da push.
- Tai hien clean-env voi code MOI (home checkout): SIG duoc tim thay
  '11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795342782_301493614',
  liquid_available True. Fix dung o muc ham truoc khi restart daemon.
- Precheck truoc restart: relay idle, khong session.json, khong tien
  trinh s2_flip/soak nao tren laptop hay VM, PID 27441 (soak master) khong
  ton tai tren laptop, tab mochi + fixture con nguyen.

## 2026-11-22 19:39-19:40 +07, T+16-17m: PHAT HIEN MOI, doi ke hoach restart

- holders.json luc 19:38: S2-flip acquired 2026-11-22T19:36:53+07:00, pid
  null. KHONG phai 18:43:50 nhu W-PILLVERIFY thay luc 19:14. Holder da
  duoc acquire LAI luc 19:36:53, sau khi W-PILLVERIFY ket thuc va sau khi
  task nay bat dau. Chung co: holders.json mtime 19:36:53.604, trung voi
  mot dong native_spawn_failed ngoai chu ky monitor (19:36:53.604, cach
  tick truoc 272ms), tuc la co mot request acquire den daemon luc do.
- Nguoi acquire khong xac dinh duoc: khong co tien trinh s2_flip/soak nao
  tren laptop hay VM, relay idle. Co the la lenh SSH ngan tu mot lane
  khac da thoat truoc khi kiem tra. Khong the ket luan S2-flip da chet.
- QUYET DINH (doi so voi ke hoach cu): KHONG dung `overlay.py stop` (no
  xoa HET holder, neu S2-flip dang co run song thi mat pill giua chung va
  holder mat). Thay vao do kill daemon PID 76088 bang SIGTERM (daemon tu
  don socket/daemon.json), GIU NGUYEN holders.json. Acquire ke tiep se
  spawn daemon moi tu code da sua, apply_holders dau tien se nang pill
  cho holder S2-flip con lai. Rui ro: neu co act nao dang chay qua gate
  cdp.mjs, no chi mat pill vai giay (hien tai von khong co pill nao) va
  release cuoi act van chay duoc (cmd_release khong-daemon chi go holder).

## CLOSEOUT (W-PILLFIX-CLOSEOUT, 2026-11-22 19:48-19:55 +07)
#
# Tu day tro xuong la phan TAI TAO sau su viec, viet boi W-PILLFIX-CLOSEOUT.
# Moi claim ghi nguon trong ngoac. Khong sua phan log goc phia tren.

## 2026-11-22 19:48:36 +07, T+0m: nhan viec, trang thai repo
(Nguon: VM repo, git log/status/ls-remote.)
- VM repo ~/workspace/computer-use-wayland, branch todolist-push, HEAD
  8f600b9, bang dung origin/todolist-push (ls-remote xac nhan
  8f600b933728e29c3889948de0da7c80a8c14eb3).
- improvements/w-pillfix-log.md ton tai tren dia, 274 dong, untracked,
  chua commit. Phan log goc ket o quyet dinh doi restart 19:40, khong ghi
  ket qua restart, khong co bao cao cuoi. Day la phan con thieu ma closeout
  nay viet lai.
- Luu y: git status con thay 1 file modified khong lien quan
  (tests/realistic/clone1-batch3/results.json) va vai file untracked khac;
  closeout KHONG dong vao chung, chi add rieng improvements/w-pillfix-log.md.

## 2026-11-22 19:40:45 +07: KET QUA RESTART (Council 2 yeu cau bo sung)
(Nguon: laptop, doc qua ssh-laptop.sh, kiem tra lai 19:48-19:54.)
- Daemon cu PID 76088 (started 18:40:32) da chet theo dung ke hoach SIGTERM
  giu holders.json. Daemon moi PID 115582, started 19:40:45.465, chay tu
  /home/james/computer-use-wayland/scripts/overlay.py daemon.
  daemon.log: `[overlay] {"elapsed_ms":12,"event":"daemon_started",
  "pid":115582,"wall_time":"2026-11-22T19:40:45.465+07:00"}`.
  daemon.json: `{"pid": 115582, "started": "2026-11-22T19:40:45+07:00"}`.
- holders.json GIU NGUYEN nhu ke hoach: S2-flip (acquired 19:36:53, pid
  null) con lai; them holder W-PILLFIX (acquired 19:40:45, method smoke,
  pid null) tu lenh acquire smoke cua W-PILLFIX.
- Spawn dau tien cua daemon moi THANH CONG: `[overlay]
  {"elapsed_ms":206,"event":"native_spawned","owner":"daemon",
  "wall_time":"2026-11-22T19:40:45.659+07:00"}`. Native indicator PID
  115587, started 19:40:45.
- Environ cua daemon 115582 VA native 115587 deu co
  HYPRLAND_INSTANCE_SIGNATURE=11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795342782_301493614
  va WAYLAND_DISPLAY=wayland-1 (doc /proc/<pid>/environ). Cung SIG ma log
  goc tim thay bang tai hien clean-env. Fix chay dung o muc live, khong chi
  o muc ham.
- Code dang chay la code fix: scripts/overlay.py tren home checkout co 3
  lan nhac desktop_env, import o dong 222; sha256 overlay
  b551cf6b2e1503824c690f46dae5ce88c90dfca6cf0f0761699e808717be59b4 va
  indicator 4008141bc28ca1b6ba2865ef6a05eb8a4d837c3ca7675f5daa2e06d05e3a43ac,
  khop dung VM repo tai 8f600b9. Laptop workspace repo HEAD 8f600b9.
- Loi liquid-glass DUNG HAN: dong native_spawn_failed CUOI CUNG trong toan
  bo daemon.log la 19:40:29.377 (tick cuoi cua daemon cu, elapsed_ms
  3596872). Dem chinh xac bang grep theo wall_time: 0 loi tu 19:40:30 tro
  di (kiem tra lai 19:54:33). Tong native_spawn_failed 1839 (toan bo lich
  su file log), tong native_spawned 314 (313 truoc + 1 luc 19:40:45.659).
- Chi co 1 dong daemon_started cho PID 115582; khong co daemon nao khac
  khoi dong sau do. Daemon 115582 va native 115587 van song o lan kiem tra
  cuoi 19:54:33.

## 2026-11-22 19:40:45-19:49:37 +07: SMOKE TEST VA SHOW ACK
(Nguon: laptop daemon.log, cac dong [indicator-event] / [indicator-metrics].)
- 19:40:45, ngay sau spawn: label "W-PILLFIX via smoke", show "stdin show
  command", framed "buffer presented", present_failures 0 (elapsed_ms 37
  den 58). Pill da hien voi label smoke.
- Show ack Council 2 yeu cau, da xac minh truc tiep trong daemon.log:
  - 19:49:35+0700, elapsed_ms 529953: label "W-PILLFIX via smoke",
    present_failures 0; show "stdin show command", present_failures 0.
  - 19:49:37+0700, elapsed_ms 531953: label "W-PILLFIX via smoke",
    present_failures 0; show "stdin show command", present_failures 0.
  - Cung khung gio: 19:49:13 label + show, present_failures 0; metrics
    19:49:11-13 ghi show_commands 1, label_commands 1, present_retries 0.
- Gioi han bang chung, ghi ro: log goc khong co anh chup grim nao, closeout
  cung khong tim thay bang chung grim. Bang chung o day la muc process
  (spawn thanh cong, framed, show ack, present_failures 0), KHONG phai anh
  chup man hinh. Xac nhan bang mat thuoc ve W-PILLVERIFY2, khong tuyen bo o
  day.

## 2026-11-22 19:48:43 +07: TEST CHAY LAI TREN VM, TARGETED
(Nguon: chay lai bang `python3 -m unittest discover -s tests -p ...`,
log /tmp/w-pillfix-closeout/targeted.log.)
- test_overlay.py: Ran 19 tests, OK.
- test_indicator.py: Ran 43 tests, OK.
- test_hypr_cmd.py: Ran 24 tests, OK.
- test_s2_flip_pill.py: Ran 3 tests, OK.
- test_indicator_ink.py: Ran 6 tests, OK.
- test_indicator_material.py: Ran 3 tests, OK.
- test_indicator_native.py: Ran 1 test, OK.
- Ket luan phan nay: khop dung tung con so trong message commit 8f600b9.

## 2026-11-22 19:48:50-19:53:41 +07: TEST CHAY LAI, FULL SUITE, CO LECH
(Nguon: chay lai full suite tren VM, log
/tmp/w-pillfix-closeout/fullsuite.log. KHONG chep so tu message commit.)
- Full suite: Ran 2313 tests in 268.390s, FAILED (failures=2, errors=2,
  skipped=17). Tuc la 2309/2313 pass, KHAC voi message commit ghi
  2310/2313 (failures=1, errors=2). Lech dung 1 FAIL, phan tich duoi day.
- 3 loi giong het claim co san trong message commit va log goc:
  - ERROR setUpClass test_cursor_file.CursorFileTests: g++ bao
    `unrecognized command-line option '-std=c++26'` (VM khong ho tro C++26).
  - ERROR test_tc02_controller.Tc02MenuBarTests
    .test_typed_text_check_passes_when_fragment_is_visible: `tesseract is
    unavailable; refusing to assume text presence`.
  - FAIL test_tc02_controller.Tc02MenuBarTests
    .test_typed_text_check_fails_when_fragment_is_absent: `'20:30' not
    found in 'tesseract is unavailable; refusing to assume text presence'`.
- 1 FAIL THEM, khong co trong message commit:
  - FAIL test_phase3_cleanup.py test_cli_exit_codes: `desktop NOT clean:
    2 leftover(s) in /tmp/tmpqfqgrt2x/state: session guardian still
    running: pid 19139, pid 19164`.
  - Chung minh day la nhieu tu lane khac chay song song, khong phai
    regression cua fix: chay rieng `test_phase3_cleanup.py` luc 19:53:41
    cho Ran 5 tests, OK; 2 PID guardian do khong con ton tai luc kiem tra
    lai. Cung thoi diem full suite cua closeout chay, ps tren VM thay 2
    full suite khac dang chay (c1-fullsuite, w-pillfix-redteam-fullsuite),
    thuoc council/redteam dang review song song. Test nay kiem tra desktop
    sach, nen guardian cua lane khac lam no FAIL.
  - Ket luan phan nay: fix gay 0 regression trong cac suite lien quan va
    full suite; 3 loi moi truong co san + 1 loi nhieu dong thoi, da chung
    minh bang chay rieng.

## 2026-11-22 19:54:33 +07: TRANG THAI LIVE LUC KHOA LOG
(Nguon: laptop, doc qua ssh-laptop.sh.)
- Daemon 115582 + native 115587 van song tu 19:40:45, khong loi spawn nao
  tu 19:40:30.
- S2-flip acquire LAI luc 19:53:37 (holders.json doi acquired tu 19:36:53
  sang 19:53:37, method CDP, pid null), boi mot lane khac khong xac dinh
  duoc, trong luc closeout dang chay. Pill hien dang phuc vu holder nay:
  19:54:31 label "S2-flip via CDP", show "stdin show command",
  present_failures 0.
- Holder smoke W-PILLFIX (acquired 19:40:45, method smoke, pid null) VAN
  CON trong holders.json luc khoa log. Closeout chi doc, khong release
  gi, theo dung brief.

## MO CON, KHONG TUYEN BO
- Holder smoke W-PILLFIX con sot: COORD-CLICK-9 hoac W-PILLVERIFY2 quyet
  dinh release khi xong verify. Closeout khong tu y release vi co the co
  run S2-flip dang dung pill (re-acquire 19:53:37).
- Khong restart daemon khi chua kiem tra: pill dang phuc vu S2-flip live.
- Khong co bang chung grim trong log nay; gate 4.29 chi duoc tuyen bo boi
  lane verify doc lap W-PILLVERIFY2.
- Le cho full suite giua message commit (failures=1) va chay lai cua
  closeout (failures=2) da giai thich o tren: them 1 FAIL nhieu dong thoi,
  chay rieng thi OK. Council/redteam soi lai neu can.
