# W-GPILL-RETRY log: G-PILL retry, one live send via amend3 pill mechanism

Worker doc lap W-GPILL-RETRY, buoc 2 cua live sequence (G-PILL retry)
cho COORD-CLICK-11. Bao cao ve COORD-CLICK-11, khong bao ong.
Repo ~/workspace/computer-use-wayland, branch todolist-push.
Moi gio Asia/Ho_Chi_Minh. Khong dau gach ngang dai. Khong ydotool.
Khong thong tin ca nhan. Chuan Lauren Tan: lenh chay + output +
commit hash + log thoi gian.

## 0. Muc tieu va lenh chay

- PASS = mot send live qua co che pill da fix amend3
  (scripts/s2_flip_live.py send_browser) voi anh grim chup trong
  luc send chung minh pill hien live, va don sach (holders 0,
  pill tat).
- Lenh chay (run 6 moi, khong trung rung-2 runs 1-5, khong trung
  S2 land runs 0-5):
  python3 scripts/s2_flip_live.py --run 6 --browser chromium
  --activate --chromium-set-value --message-prefix G-PILL-RETRY
  --workdir improvements/gpill-retry-runs
- Co --activate: buoc activate la buoc visible dau tien ma H1
  gate (re-check holder truoc activate); grim "truoc activate"
  trong brief chi co nghia khi co activate.
- Co --chromium-set-value: Chromium fill that bai failed-unverified
  5/5 o s2-flip-runs (run-1..5); Chromium set_value sent 6/6 o
  s2-flip-land-runs (run-0..5). Set_value la program da land cho
  Chromium, va moi co delayed recount 10s.
- Message: G-PILL-RETRY-R6-CHROMIUM-IGNORE-TEST (message_for).
  Target: thread mochi, Chromium 9223, label clone2, tab
  A67A718D5E236F894F9863F48834743C (tab muse.ai duy nhat).
- Nhan viec 21:39:09 +07, T+0m. May yen, ong khong o may, bo qua
  moi tin hieu idle. Single lane.

## 1. Time log

- 21:39:09 +07, T+0m: nhan viec. Doc xong amend3 log, pillverify2
  log, run3 log.
- 21:40 +07, T+1m: laptop HEAD 14cf4dc (amend2), chua co amend3.
  VM HEAD 8b0b32d.
- 21:41 +07, T+2m: laptop fast-forward len 8b0b32d, AMEND3-ANCESTOR-OK.
  sha256 overlay.py va s2_flip_live.py khop VM.
- 21:42 +07, T+3m: pre-check PASS: holders {}, visible false,
  daemon idle-exited, relay idle owner null, Zen/Chromium/Brave
  song, Chromium co dung 1 tab muse.ai (mochi).

## 2. Sync laptop repo len HEAD (buoc 1)

- Laptop truoc sync: HEAD 14cf4dc (amend2), grep pill_holder_alive
  trong scripts/s2_flip_live.py = 0. Fetch: todolist-push
  14cf4dc..8b0b32d.
- Laptop git status truoc ff: chi file untracked (cf26 lessons,
  latency CSVs, live-a2t, live-a4r), khong co tracked file dirty,
  khong chan ff.
- Lenh: git merge --ff-only origin/todolist-push
- Sau ff: HEAD 8b0b32d COORD-CLICK-10: ZT-B run 3 FAIL verified,
  sequence STOPPED at step 1.
- git merge-base --is-ancestor
  e7e973ecb8f3b218b4ac314d0c22f0f9baef0b1b HEAD: AMEND3-ANCESTOR-OK.
- sha256 laptop:
  - scripts/overlay.py
    4cb46f9d1329034a1e0ad9c78e5b904ebd725835ec6de0f14ff2fae78d7059ae
  - scripts/s2_flip_live.py
    1e00cd7792f88436121798ca4a8e16ed9c464dc85979b608f4a65bff61a30e53
- sha256 VM: giong het ca 2 file (xem muc 2, verify bang lenh
  sha256sum tren VM).
- grep tren laptop: def pill_holder_alive o dong 711
  scripts/s2_flip_live.py; pill_release_cmd(pid) dong 631.

## 3. Pre-check (buoc 2)

- Overlay status: holders {}, owner none, visible false. Pill tat
  o dau.
- Daemon: khong co tien trinh overlay.py daemon (idle-exited sau
  run 3, dung nhu log run3). Chi co session_remote serve PID 70985.
  Acquire se spawn daemon moi tu code tren dia (da co amend3).
- Relay: broker running, state idle, owner null, driver idle,
  guardian idle, loaded_code_sha256 d490f369f6b7.
- Cua so (hyprctl clients): Zen 0x56307e2771d0 ws1 (Calendar);
  Chromium 0x56307e202df0 ws2 (Pick 4 fixture); Chromium
  0x56307e7d9bb0 ws2 (Chat mochi); Brave-Origin 0x56307e4c2f90
  ws2 (Muse). Zen 9222 tra HTTP 404 (port song), Chromium 9223
  Chrome/157.0.8103.38, Brave 9224 Chrome/157.0.8103.79.
- Chromium /json/list: dung 2 tab page: Pick 4 fixture
  025266AE11C86425817A3AF6E0FB7B26 va mochi
  A67A718D5E236F894F9863F48834743C (https://muse.ai/). Dung 1 tab
  muse.ai, route_browser se tim dung target. Khong co tab scratch.
- Ket luan pre-check: PASS, du dieu kien chay send.

## 4. Test acquire: pill hien voi code amend3 (21:41 +07, T+2m)

- Lenh (mau pill_acquire_cmd, sleep 120): acquire --agent S2-flip
  --method CDP --pid 192378.
- Ket qua: holder S2-flip:192378 acquired 21:41:06 +07, label
  "S2-flip via CDP", owner daemon, visible true.
- Daemon PID 192380, spawn 21:41:06.282 +07 tu code tren dia (da
  co amend3), event daemon_spawned trong stderr.
- Grim /tmp/gpill-retry-test-acquire.png, 894478 bytes, sha256
  35ac8ea498ae41b7bae1700018e271bb9a4b9a39596eecce14d506f9156a4203.
  Xem truc tiep: pill HIEN top center, label "S2-flip via CDP",
  cham xanh la, vat qua ranh Zen/OmaCal. Test acquire PASS.
- Release pid-keyed: release --agent S2-flip --method CDP --pid
  192378, event released 21:41:31.783 +07, kill sleeper 192378.
  Status sau release: holders {}, owner none, visible false.
  Daemon tu thoat khi het holder (daemon_exiting true), dung
  hanh vi idle-exit da thay o run 3.

## 5. Khoi phuc helper /tmp tren laptop (21:42 +07, T+3m)

- Phat hien: /tmp/c5-activate.mjs, /tmp/c5-count.mjs,
  /tmp/s2-v12.mjs, /tmp/s2-p9.mjs KHONG con tren laptop (tmp
  bi don tu lan land run truoc). Khong co cac file nay thi
  activate tra ok False, count tra -1, V12 that bai, P9 that
  bai, send khong the PASS. Dung lai de khoi phuc truoc khi
  chay, khong chay send thieu helper.
- Khoi phuc tu ban persistent tren laptop (khong download moi):
  cp ~/c5-rung2-run/c5-count.mjs, s2-v12.mjs, s2-p9.mjs va
  ~/c5-step9-run/c5-activate.mjs sang /tmp/.
- sha256 sau khoi phuc, khop ban VM:
  - c5-activate.mjs
    74af25d2f9b8bae1f7f5154ac9d974e1bc5316247a564768cd44d6571dff1d70
    (khop ~/workspace/c5-step9-run/c5-activate.mjs)
  - c5-count.mjs
    d0f4e25464395544504200bff9d0edf79c73e221f7fdbc4297c61c168606d80d
  - s2-v12.mjs
    dd588e8417a35a6a33dda01cd315eaf83f395fdb61a9f8fc5ebdebb278b1a473
  - s2-p9.mjs
    b39829e12b139d6fe4c2f803a356f6789bf90b4515e92c0f69184aa586580f4b
    (3 file sau khop ~/workspace/c5-rung2-run/)
- Watcher grim: ~/gpill-retry/watch.sh tren laptop, poll overlay
  status 0.5s, grim ngay khi holders khac 0 (during1), grim lai
  sau 3s (during2), log vao ~/gpill-retry/watch.log. bash -n OK.

## 6. Live send run 6 (21:43 +07, T+4m)

- Lenh chay detached (VM PID 147951, launch 21:43:23 +07):
  python3 scripts/s2_flip_live.py --run 6 --browser chromium
  --activate --chromium-set-value --message-prefix G-PILL-RETRY
  --workdir improvements/gpill-retry-runs
- Ket qua stdout: {"run": 6, "wall_ms": 16827.3, "outcomes":
  {"chromium": "sent"}, "json":
  "improvements/gpill-retry-runs/run-6.json"}
- Run JSON (improvements/gpill-retry-runs/run-6.json):
  - target_id A67A718D5E236F894F9863F48834743C (mochi),
    tab_title Muse, label clone2, endpoint 127.0.0.1:9223
  - message G-PILL-RETRY-R6-CHROMIUM-IGNORE-TEST
  - routing dom-chromium, 55 elements, truncated false,
    composer_present true
  - activation ok true, hasFocus false truoc, true sau, rc 0,
    ms 1016.9
  - pre_count 0 (items 44), program ok true completed 4,
    elapsed_ms 319.4, error null
  - cb1 input_sent true, target_received true, verified true
  - v12 found true, role user, side user, attempts 1
  - outcome sent, wall_ms 4980.5 (send), 16827.3 (run)
  - delayed_count chromium count 1 (items 42), khong double-send
  - p9 chromium ok true, p9-run6-chromium.png
  - model_calls 0
- P9 xem truc tiep: bubble xanh user
  "G-PILL-RETRY-R6-CHROMIUM-IGNORE-TEST" o day thread mochi,
  composer trong, dung 1 bubble. DOM-vs-render khop (V12 found,
  delayed count 1, P9 hien dung 1 bubble).
- Chi 1 send nay vao thread mochi trong task nay, khong send nao
  khac.

## 7. Grim trong luc send: pill hien live (21:43:34-37 +07)

- Pre grim (truoc launch): ~/gpill-retry/
  gpill-retry-pre.png, 886956 bytes, sha256
  5fadab479db43eb798b90be5fc5b211597583adf77906af302b26734bb8924ce.
  Xem truc tiep: KHONG co pill top center. Pill tat truoc send.
- Watcher log (~/gpill-retry/watch.log, copy o
  improvements/gpill-retry-runs/watch.log):
  21:43:16 START watch; 21:43:34 HOLDERS=1 grim1; 21:43:34 grim1
  done; 21:43:37 grim2 done; status luc grim2: holder
  S2-flip:194257 acquired 21:43:34, label "S2-flip via CDP",
  visible true.
- During1 (21:43:34, ngay luc acquire, truoc activate):
  gpill-retry-during1.png, 892966 bytes, sha256
  3bbfc811dea0312d9caf36fc4b731142a44649118192cc197ccac7d51adffbe3.
  Xem truc tiep: pill HIEN top center, label "S2-flip via CDP",
  cham xanh la, vat qua ranh Zen/OmaCal.
- During2 (21:43:37, trong luc program chay):
  gpill-retry-during2.png, 893043 bytes, sha256
  81f3e289406e35e8293a85a9117c1280cab16b30e4ee2da8267cf050550a74c5.
  Xem truc tiep: pill HIEN, cung label, cung vi tri.
- Post grim (ngay sau send xong): gpill-retry-post.png,
  886907 bytes, sha256
  5102d3c9618db954fc640f280ab517f64fdb771a9ad109cd8fb2967be9ab2633.
  Xem truc tiep: KHONG co pill. Pill tat sau send.
- Ca 4 anh grim da fetch ve VM (improvements/gpill-retry-runs/),
  sha256 khop ban laptop.
- Luu y: man hinh trong ca 4 anh la ws1 Zen Calendar (thong bao
  lich "SLEEP (Daily) se bat dau luc 9:45PM" co san tu truoc,
  khong phai cua toi; cung dialog nay co o grim run 3). Send chay
  tren Chromium ws2 qua CDP, khong doi workspace; pill la
  layer-shell top center nen van thay ro tren ws1. Khong co tab
  nao cua ong bi dong hay navigate: /json/list sau run van dung
  2 tab (fixture 025266AE, mochi A67A718D).

## 8. Verify hanh vi amend3 tu log run (buoc 4)

- Thu tu ssh_calls trong run-6.json (tat ca rc=0):
  mux-probe, mux-probe, lease-cleanup, broker-start,
  broker-request-1, broker-result-1, broker-request-2,
  broker-result-2, broker-finish, pill-acquire (950.7ms),
  pill-status (792.0ms), activate (1016.9ms), count-check,
  oneshot-code-exec, v12-check, pill-release (1266.7ms),
  count-check (delayed), p9-capture.
- H1: pill-status chay ngay sau pill-acquire va ngay truoc
  activate; send khong abort (holder song, khong co outcome
  aborted-pill-lost, khong co note pill lost). Re-check chay
  dung vi tri gate truoc buoc visible dau tien.
- H2: release chay sau V12 qua pill_release_cmd(pid) (code chi
  con duong pid-keyed, khong con fallback pid-less); holder
  S2-flip:194257 bien mat khoi status sau send, holders ve {}.
- Don sach: status sau run holders {}, owner none, visible
  false; khong co tien trinh overlay.py daemon (tu thoat);
  khong co sleeper sot (ps sleep 120/600 trong); relay state
  finished, owner s2-flip-run6 (driver dung, broker ra idle);
  Chromium van dung 2 tab page nhu truoc run.
- Daemon run 6: spawn tu acquire (holder S2-flip:194257,
  acquired 21:43:34), code amend3 tren dia (da verify sha256
  muc 2).

## 9. Verdict: PASS

- G-PILL retry PASS: mot send live qua send_browser amend3,
  outcome sent, V12 found attempts 1, delayed count 1, P9 hien
  dung 1 bubble; pill sight-verify HIEN trong 2 anh grim luc
  send (during1 21:43:34, during2 21:43:37, label "S2-flip via
  CDP", top center); pill tat truoc va sau (pre/post grim +
  status holders {}); H1 re-check chay truoc activate, release
  pid-keyed, holders ve 0.
- Thoi gian: nhan viec 21:39:09, send xong 21:43:5x, don dep
  xong 21:45:40, tong khoang 6 phut. Khong ket o buoc nao qua
  15 phut. Khong co stop condition nao kich hoat (pill hien,
  send khong bi tu choi, khong loi).
- File bang chung: improvements/gpill-retry-runs/run-6.json,
  run-6.stdout.log, p9-run6-chromium.png,
  gpill-retry-pre.png, gpill-retry-during1.png,
  gpill-retry-during2.png, gpill-retry-post.png,
  gpill-retry-test-acquire.png, watch.log.
