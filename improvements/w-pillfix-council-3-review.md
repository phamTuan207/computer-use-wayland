# Council 3 (rui ro) review: W-PILLFIX commit 8f600b9

Bao cao cho COORD-CLICK-9, khong nhan truc tiep cho Pham Tuan.
Review doc lap, chi review, khong sua code, khong viet log thay W-PILLFIX.
Moi gio ghi theo Asia/Ho_Chi_Minh. Khong dung dau gach ngang dai.
Khong ydotool. Khong thong tin ca nhan len GitHub. Khong tu cham diem.
Chuan Lauren Tan: lenh chay + output + commit hash + log thoi gian.

## Verdict: GO VOI DIEU KIEN

Fix dung huong, dung nguyen nhan that, va da co bang chung live la
standalone spawn chay lai duoc (xem muc 5). Huong fail-closed la dung:
status khong noi doi nua, acquire tu choi thay vi de caller chay mu.
Nhung co 1 rui ro that can sua truoc lan live tiep theo (dieu kien C1),
1 hoi quy nho ve WAYLAND_DISPLAY (C2), va khoang trong bang chung
ve log + holder smoke chua don (C3). Khong co ly do revert commit.

## Dieu kien

- C1 (bat buoc truoc live tiep theo): thu hep viec go holder o duong
  acquire invisible trong `cmd_acquire` chi dung key vua them, khong
  xoa het holder cung agent khi pid la None. Hien tai
  `remove_holder(agent, None)` xoa ca holder co pid cua cung agent
  (da chung minh bang probe R6 o muc 3). Them test 2 holder cung agent
  (1 pid-keyed, 1 pid-less), acquire invisible cua holder pid-less
  khong duoc lam mat holder pid-keyed. Cung ap dung cho duong exception
  D1 neu cham vao do, vi no dung chung `remove_holder(agent, pid)`.
- C2 (sua kem C1): nhanh discovery trong `wayland_env` phai giu
  WAYLAND_DISPLAY do caller truyen (setdefault nhu code cu), khong ghi
  de thanh wayland-1 (probe R2 o muc 1).
- C3 (ho so): commit `improvements/w-pillfix-log.md` kem muc ket luan
  ghi lai restart daemon 19:40:45 + ket qua smoke, vi hien log chi ton
  tai untracked tren VM va dung o quyet dinh restart, khong co ket qua.
  Dong thoi release holder smoke W-PILLFIX con sot tren laptop (xem
  muc 5), khong de pill bi giu boi 1 holder test.
- C4 (verify): W-PILLVERIFY2 doc lap chay lai gate live, kem grim thay
  pill that, truoc khi tuyen bo gate 4.29 dat. Council 3 khong chay
  lai act CDP live (VM khong co compositor; kiem tra laptop chi doc).

## 1. wayland_env moi (scripts/overlay.py, dong 197-235)

### Da kiem tra bang doc code

- Nguyen nhan goc dung: code cu doc signature tu `/run/user/1000/hyprland`,
  thu muc nay khong ton tai; code moi uy thac `hypr_cmd.desktop_env`
  voi `signature_dir=<runtime>/hypr`, dung layout that.
  `desktop_env` (scripts/hypr_cmd.py, dong 191-218) chi raise ValueError
  khi khong list duoc thu muc hoac thu muc rong; ben trong no da doi
  OSError thanh ValueError.
- `wayland_env` bat `(ImportError, ValueError)` roi tra env khong co
  signature, spawn sau do fail loud nhu cu. Dung thiet ke.
- Truong hop tra ve signature SAI thi co, va la hanh vi thua huong tu
  `desktop_env`, khong phai do fix nay tao ra: `desktop_env` lay
  `sorted(os.listdir(signature_dir))[0]`, khong kiem tra instance nao
  con song (khong thu socket, khong chay hyprctl). Nhieu instance hoac
  thu muc instance cu ton tai thi lay sai theo thu tu alphabet.
  Ngay 22/11 tren laptop chi co 1 thu muc instance duy nhat duoi
  `/run/user/1000/hypr/` (kiem tra 19:50:08, xem muc 5), nen rui ro
  nay hien la tiem an, khong phai dang xay ra.
- Caller-provided signature duoc giu nguyen, khong xac thuc. Signature
  cu/chet van duoc giu, spawn se fail loud nhu truoc. Chap nhan duoc
  theo huong fail loud, nhung test `test_wayland_env_keeps_caller_signature`
  dung gia tri gia (`keep-me`) nen chi chung minh giu nguyen, khong
  chung minh signature that dung duoc. Khong phai loi chan.
- `XDG_RUNTIME_DIR` sai dan toi discovery sai: `runtime` lay tu env
  cua caller, `signature_dir` la `<runtime>/hypr`. Neu caller mang
  runtime sai thi discovery that bai am tham, tra env khong signature.
  Dung huong fail loud, nhung kho chan doan vi khong log ly do.
  De xuat nho (khong chan): log 1 dong khi discovery that bai, kem
  runtime da thu.
- Ngoai le chua bat het: `from hypr_cmd import desktop_env` neu
  `hypr_cmd.py` loi import-time khac ImportError (vi du loi cu phap
  phu thuoc) thi `wayland_env` crash thay vi tra env khong signature.
  Xac suat thap, ghi nhan de phong, khong chan.

### Probe tu chay tren VM (19:49:43 +07, /tmp/c3-probe.py)

```
R1 multi-sig picked: aaaaaaaa_stale_1
R2 caller display wayland-9 -> wayland-1 sig: only_sig
R3 stale caller sig kept: stale_dead_sig
R4 wrong runtime dir, sig present: False
R5 missing dir -> ValueError: cannot list Hyprland signature dir /tmp/no-such-c3/hypr: [Errno 2] No such file or directo
R5 empty dir -> ValueError: no Hyprland instance signature under /tmp/tmpzmidkj3q (hyprland/ is empty; use hypr/)
```

- R1: 2 thu muc gia, lay `aaaaaaaa_stale_1` (alphabet dau), khong
  kiem tra song chet. Da chung minh.
- R2: HOI QUY MOI. Caller co `WAYLAND_DISPLAY=wayland-9` nhung chua
  co signature, nhanh discovery ghi de thanh `wayland-1` bang
  `env['WAYLAND_DISPLAY'] = discovered['WAYLAND_DISPLAY']`.
  Code cu dung `setdefault` nen giu display cua caller. Tren may
  nay display that la wayland-1 (hang so trong hypr_cmd.py dong 23)
  nen khong anh huong live hom nay, nhung neu display that khac
  thi spawn sai display. Dieu kien C2.
- R3: signature cu do caller truyen duoc giu nguyen, khong xac thuc.
- R4: runtime sai thi khong co signature, fail loud nhu thiet ke.
- R5: ValueError o ca 2 truong hop, dung nhu `wayland_env` ky vong.

## 2. Thay doi status (reconcile via apply_holders)

### Da kiem tra bang doc code

- `Daemon.status_reply` (overlay.py dong 343-356) goi thang
  `apply_holders`, giong monitor chay moi 2s. Nhan xet "khong them
  side-effect class" la dung o muc loai tac dung: spawn/show chi khi
  co holders. Nhung ban chat cua status doi tu read-only thanh
  mutating: 1 lan hoi status co the spawn native, doi owner
  daemon/session, hide pill cua daemon khi handover sang session.
- Vong lap: khong co vong lap moi. Monitor da goi `apply_holders`
  moi 2s, status chi them 1 lan goi nua. Neu spawn that bai lien tuc,
  moi lan status se log them `native_spawn_failed` va tra error, giong
  monitor. Khong co de quy (apply_holders khong goi lai status).
- Cham tre / timeout: serve loop xu ly tuan tu tung client, status
  co the giu loop trong luc spawn/show. `_ensure_daemon` goi status
  voi timeout 2-3s (overlay.py, ham `_ensure_daemon`), trong khi
  spawn live do duoc 205ms (19:40:45.659, muc 5) nen vua ngan sach
  hom nay. Neu spawn cham hon (hyprctl treo), `_ensure_daemon` se
  coi nhu daemon chua tra loi va thu lai trong vong 15s, khong chet
  ngay, nhung acquire se cham them. `cmd_status` dung
  `_send_socket` timeout mac dinh 10s, co the treo toi 10s khi spawn
  cham. Ghi nhan, khong chan.
- Khoa: `apply_holders` giu `self.lock` trong suot qua trinh spawn
  va show. Monitor va status dung chung lock nen tuan tu hoa, khong
  deadlock (khong co duong goi long nhau vao `apply_holders`).
- `cmd_status` khong daemon (overlay.py dong 581-600):
  `visible = bool(holders) and session_live()`. Dung huong, chat hon
  code cu. Nhung `session_live` tu no probe bang
  `indicator.request(BASE, 'show')`, tuc la status cung goi show
  vao session indicator (docstring noi idempotent, khong ve lai).
  Rui ro nho: neu session indicator song nhung thuoc run khac,
  status van bao visible True cho holder hien tai. Chi la bao cao
  sai nhe, khong gay hanh dong sai.
- Truong hop daemon song nhung status socket timeout: `cmd_status`
  bat `(OSError, ValueError)` roi de `info['owner'] = 'unknown'`
  nhung giu `visible = bool(holders)` cu, tuc la van co the bao
  visible True trong khi that ra chua biet. Loi cu con sot, khong
  phai do fix nay tao ra, ghi nhan de sua sau.

### Test lai cua Council 3

Targeted suites chay lai tren VM 19:49:34 +07, deu OK (xem muc 6).
Test `test_status_reply_reports_real_visibility` dung fake native,
chi chung minh logic reconcile, khong chung minh spawn that.

## 3. cmd_acquire exit 1 va drop holder (rui ro lon nhat)

### Da kiem tra bang doc code + probe

- Tat ca caller CLI deu xu ly duoc exit 1:
  - `scripts/cdp.mjs` dong 52-68: `runOverlayCli` reject khi
    execFile bao loi (exit != 0), `acquireCdpPill` doi thanh
    `CDP pill unavailable`, act bi tu choi. Dung, fail-closed.
    Timeout acquire 60000ms (dong 23), du cho spawn cham.
  - `scripts/chromium_cli.py` dong 640-660 (`_pill_hold`): dung
    `overlay.hold`, subprocess `check=True` nen exit 1 thanh
    CalledProcessError, main bao loi envelope, khong chay lenh
    trinh duyet mu. Dung.
  - `scripts/first_action.py` dong 116-145 (`acquire_overlay`):
    khong dung CLI `cmd_acquire`, no goi thang `_ensure_daemon` +
    `_send_socket` va tu raise RuntimeError khi visible khong True,
    kem go holder. Khong bi anh huong truc tiep boi exit 1 moi.
  - `scripts/s2_flip_live.py` dong 607-640 (`cdp_pill_hold`):
    best-effort, `held = rc == 0`, exit 1 thi yield False, bo qua
    release, ghi note. Send sau do van bi gate cdp.mjs chan.
    Khong treo. Dung, va tot hon truoc (truoc day rc 0 kem
    invisible se yield True sai).
- Khong co duong goi acquire nao bi treo boi exit 1. Khong tim thay
  caller nao goi CLI acquire ma khong kiem tra exit code: grep toan
  repo chi thay cdp.mjs, chromium_cli qua hold, first_action qua
  socket, s2_flip qua rc, va docs vi du chay tay.
- NHUNG: viec go holder qua rong (R6). `cmd_acquire` duong invisible
  goi `remove_holder(args.agent, args.pid)`. Khi pid la None,
  `remove_holder` (overlay.py dong 127-151) xoa TAT CA key cua agent
  do, gom ca holder co pid dang song. Probe 19:49:43 +07:

```
R6 before remove(None): {'Muse': {... 'pid': None}, 'Muse:12345': {... 'pid': 12345}}
R6 after remove_holder(Muse, None): {}
```

- Ai dung pid None: `overlay.hold` (dong 625-636) khong truyen
  `--pid`, nen moi acquire tu `chromium_cli._pill_hold` deu pid None.
  Docs vi du (`docs/overlay.md`, `docs/brief-template.md`) cung
  acquire khong pid. Chi cdp.mjs truyen `--pid` (pid cua tien trinh
  node), nen duong cdp duoc bao ve nho scoping theo pid.
- Kich ban vo: pill dang invisible (native chet hoac show that bai)
  trong luc 1 run `first_action` cua Muse (holder pid-keyed) hoac
  1 run chromium_cli khac dang giu pill. 1 acquire moi tu
  chromium_cli that bai invisible se xoa luon holder cua run dang
  song, monitor sau do thay het holders (neu chi con holder do)
  thi hide/close pill, run dang song mat pill giua chung va act
  ke tiep cua no cung fail-closed. Huong van an toan (khong chay mu),
  nhung mat pill oan va co the gay hieu ung domino trong luc outage,
  dung luc nhieu lane cung acquire that bai. Day la rui ro that
  nhat cua fix, va la dieu kien C1.
- Luu y: duong exception D1 cu da co chung pattern
  `remove_holder(agent, pid)` voi pid None, nen van de scoping co
  tu truoc, nhung duong invisible moi lam tan suat kich hoat tang
  manh (truoc day invisible tra 0 va GIU holder; nay moi invisible
  deu go het). Vi vay C1 gan voi fix nay, khong phai viec de sau vo
  thoi han.
- Duong session khong bi anh huong boi fix o muc spawn:
  `apply_holders` khi `session_live()` thi handover sang session,
  `_show_label` nhanh session chi goi `session_label` +
  `session_live`, khong bao gio spawn Native. Da doc code xac nhan.
  Nhung duong session VAN co the bi anh huong gian tiep boi R6:
  neu session live nhung `session_label` that bai thi `_show_label`
  tra False, acquire invisible, holder session bi go theo (neu pid
  None). Cung duoc bao boi C1.
- `cmd_acquire` van in reply JSON ra stdout truoc khi tra 1, tot
  cho chan doan. `_log('acquire_invisible', ...)` ghi ra stderr
  (overlay.py dong 48-59), khong lam ban stdout JSON ma cdp.mjs
  parse. Dung.

## 4. Indicator probe log (scripts/indicator.py)

- `_metric('liquid_unavailable', probe=...)` ghi stderr truoc khi
  raise, text exception giu nguyen (test pin). Phan biet
  `no_session_env` vs `invalid_status` giup chan doan nhanh, dung
  van de W-PILLVERIFY gap.
- Han che nho: `invalid_status` gom ca 2 truong hop khac nhau, hyprctl
  that bai (khong lay duoc status) va status lay duoc nhung khong
  hop le. Chan doan sau nay van phai mo log them. Khong chan.
- Truong hop env co signature nhung thieu WAYLAND_DISPLAY thi bi
  xep vao `no_session_env`. Hop ly (probe chua chay duoc).

## 5. Bang chung live (chi doc tren laptop, khong sua gi)

Laptop kiem tra chi doc qua ssh-laptop.sh, 19:50:08-19:51 +07.

- Laptop workspace repo HEAD 8f600b9, khop commit duoc review.
- `/run/user/1000/hypr/` chi co 1 thu muc instance (19:50:08),
  nen rui ro R1 hien khong kich hoat.
- Daemon hien tai PID 115582, started 19:40:45+07:00 (daemon.json),
  tuc la daemon da duoc restart SAU khi fix deploy, khong phai
  daemon cu 76088 tu 18:40. `native_spawned` luc 19:40:45.659,
  elapsed 205ms, tuc la standalone spawn chay duoc voi code moi.
- Holders luc 19:50: `S2-flip` acquired 19:36:53+07:00 (pid null)
  va `W-PILLFIX` acquired 19:40:45+07:00, method smoke (pid null).
  Holder smoke nay chung minh W-PILLFIX da restart daemon va smoke
  acquire sau 19:40, du log cua ho dung o quyet dinh restart
  (19:39-19:40) va khong ghi ket qua.
- Daemon log luc 19:49:57-19:49:59: show command, present_failures 0,
  label `W-PILLFIX via smoke`, duplicate show do monitor goi lai
  moi 2s. Pill dang duoc show lai lien tuc, khong loi present.
- Ton tai: tong 1839 dong `native_spawn_failed` trong daemon.log
  (tich luy tu truoc fix, khong phai chi so moi). Holder smoke
  W-PILLFIX van chua release luc 19:50, pill van bi giu boi holder
  test. Can don theo C3. Khong tu don trong review nay vi ranh gioi
  chi doc tren laptop.
- Khoang trong ho so: `improvements/w-pillfix-log.md` ton tai tren
  VM o trang thai untracked (274 dong), dung o muc 19:39-19:40
  (quyet dinh kill daemon bang SIGTERM, giu holders.json), khong
  co muc nao ghi restart 19:40:45, smoke acquire, hay ket qua cuoi.
  Commit 8f600b9 chi gom 4 file code + test, khong gom log. Vi vay
  bang chung live o muc nay chi co duoc nho doc truc tiep laptop,
  khong co trong repo. Task giao noi W-PILLFIX ket thuc ma khong
  viet log la khong chinh xac hoan toan: log co viet, nhung chua
  commit va chua ket luan.

## 6. Test chay lai boi Council 3 (VM, 19:49:34 +07)

```
python3 -m unittest discover -s tests -p 'test_overlay.py'
Ran 19 tests in 0.052s, OK
python3 -m unittest discover -s tests -p 'test_indicator.py'
Ran 43 tests in 0.133s, OK
python3 -m unittest discover -s tests -p 'test_hypr_cmd.py'
Ran 24 tests in 0.002s, OK
python3 -m unittest discover -s tests -p 'test_s2_flip_pill.py'
Ran 3 tests in 0.001s, OK
```

Full suite chay 3 lan boi Council 3 tren VM, o commit 8f600b9:

- Lan 1, 19:50:37-19:55:37 +07 (300s): Ran 2313 tests,
  FAILED (failures=2, errors=2, skipped=17). CAO HON claim cua
  W-PILLFIX 1 failure + 1 error. Output chi giu tail -6 nen
  khong xac dinh duoc test thua them la test nao. Day la diem tru
  ve cach ghi nhan cua lan 1, khong phai ket luan ve fix.
- Lan 2, 19:55:46-19:59:35 +07 (228s, log day du
  /tmp/c3-fullsuite2.log): Ran 2313 tests,
  FAILED (failures=1, errors=2, skipped=17), khop claim:
  ERROR setUpClass test_cursor_file.CursorFileTests (g++ khong co
  -std=c++26), ERROR + FAIL test_tc02_controller.Tc02MenuBarTests
  (tesseract is unavailable; VM khong co tesseract). Ca 3 deu
  loi moi truong, khong cham overlay/indicator.
- Lan 3, 19:59:45-20:03:24 +07 (218s, log day du
  /tmp/c3-fullsuite3.log): Ran 2313 tests,
  FAILED (failures=1, errors=2, skipped=17), cung 3 loi tren.
- Ket luan: 2/3 lan chay khop claim 2310/2313, 0 regression do
  fix. Lan 1 lech 1 failure + 1 error khong lap lai duoc o 2 lan
  sau, kha nang la flake trong suite (khong xac dinh duoc ten test
  vi log bi cat). Ghi nhan de theo doi, khong quy cho fix khi
  chua co bang chung lap lai.

## 7. Thu da xem

- Diff e200d6e..8f600b9: scripts/overlay.py, scripts/indicator.py,
  tests/test_overlay.py, tests/test_indicator.py (4 files,
  240 insertions, 13 deletions).
- `git log --oneline -1` tren VM: 8f600b9, branch todolist-push.
  `git ls-remote origin todolist-push`:
  8f600b933728e29c3889948de0da7c80a8c14eb3.
- Doc code: scripts/overlay.py (wayland_env, Daemon.apply_holders,
  status_reply, _monitor, _ensure_daemon, cmd_acquire, cmd_status,
  cmd_release, hold, remove_holder, session_live),
  scripts/hypr_cmd.py (desktop_env), scripts/indicator.py (_metric,
  Native), scripts/cdp.mjs (acquireCdpPill, runOverlayCli),
  scripts/chromium_cli.py (_pill_hold), scripts/first_action.py
  (acquire_overlay, overlay_visible), scripts/s2_flip_live.py
  (cdp_pill_hold), scripts/codemode.py (overlay.status chi la stub
  requires_laptop, khong goi CLI).
- Test moi trong fix: 7 test overlay + 1 test indicator, deu co
  trong suite chay lai o muc 6. Test bao phu duong chinh, nhung
  khong co test cho truong hop nhieu signature, WAYLAND_DISPLAY
  cua caller, hay 2 holder cung agent (la 3 lo hong o muc 1 va 3).

## 8. Ket luan

- Fix dung nguyen nhan, dung huong fail-closed, co bang chung live
  spawn chay lai (19:40:45, 205ms, present_failures 0).
- Rui ro lon nhat la go holder qua rong khi pid None (C1), ke den
  la ghi de WAYLAND_DISPLAY (C2). Ca hai deu sua nho, khong can
  revert.
- Khong chan live vinh vien, nhung khong cho phep tuyen bo gate
  4.29 dat chi dua tren review nay: can C1 + C2 + C3, roi
  W-PILLVERIFY2 verify doc lap kem grim (C4).
