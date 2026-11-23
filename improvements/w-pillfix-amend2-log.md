# W-PILLFIX-AMEND2 log: close all review conditions of W-PILLFIX-AMEND

Worker doc lap W-PILLFIX-AMEND2 (khong phai W-PILLFIX-AMEND, khong
phai COORD-CLICK-9). Nhiem vu tu Muse tong: dong cac dieu kien review
cua amend 1 (5a272ae + a355002, 4 review deu GO WITH CONDITIONS).
Khong chay live proof, khong dong/mo/navigate tab nao trong Zen cua
the owner, khong tu spawn reviewer. Moi gio Asia/Ho_Chi_Minh. Khong
dau gach ngang dai. Khong ydotool. Khong thong tin ca nhan. Chuan
Lauren Tan: lenh chay + output + commit hash + log thoi gian.

## 0. Doc review (20:38 +07, T+0m)

Doc improvements/w-pillfix-amend-log.md va 4 review:
- council-1 e2ed4e8: dieu kien 1+2+3 (truyen --pid that; sua release
  --method + docstring; sync laptop + restart daemon).
- council-2 1f28b3f: E1 (test cmd_release pid=None + help text --pid),
  E2 (test end-to-end duong D1 exception).
- council-3 f294661: dieu kien 1+2 nhu tren, + gom C2 (WAYLAND_DISPLAY
  setdefault) + R4 (desktop_env is_dir) vao cung lane.
- redteam 5d5111f: H1 bare-bare (C1), H2 chua deploy (C2), R11 (C3),
  H3 docstring noi qua.

## 1. Quyet dinh ky thuat: pid nao cho s2_flip (20:38-20:40 +07, T+2m)

Brief noi "truyen --pid that cho s2_flip pill_acquire_cmd". Pid cua
harness tren VM KHONG phai pid that dung duoc: holder song tren
laptop, daemon prune holder co pid khong ton tai tren laptop. Kiem
chung thuc nghiem truoc khi quyet:
```
# VM, thu muc tam rieng: holder pid 999999 (khong ton tai) bi prune ngay
before prune: ['S2-flip:999999']
pruned: ['S2-flip:999999']
after prune: []
# VM pid khong ton tai tren laptop (ssh-laptop.sh, chi doc)
laptop lacks pid 93722   (pid shell VM)
laptop lacks pid 999999
laptop lacks pid 12345
```
Ket luan: truyen pid VM thi daemon prune holder trong ~2s (monitor
tick), pill roi giua send. Do la regression, khong phai fix. Thay
the: pid cua mot `sleep 600` detached tren laptop (nohup, stdin/
stdout/stderr redirect, song 600s, du 1 send step). Pid that tren
laptop, song trong luc hold, khac nhau moi run, prune heal duoc neu
harness chet (sleeper het han sau 600s). Ghi ro ly do nay trong
docstring pill_acquire_cmd de lane sau khong "sua" lai thanh pid VM.
Thu nghiem live muc 7 chung minh construct chay dung tren laptop.

## 2. H1 bare-bare: moi live caller truyen --pid that (20:41 +07, T+3m)

- scripts/overlay.py hold(agent, method, pid=None): mac dinh pid =
  os.getpid() cua tien trinh goi. Acquire va release deu truyen
  --pid do. Tien trinh goi song trong ca `with` block theo dinh
  nghia, nen pid song trong luc hold va prune heal duoc neu caller
  chet giua block. Chi caller duy nhat cua hold() la
  chromium_cli._pill_hold (chay tren laptop, pid that, khac nhau moi
  lenh dong thoi). first_action dung os.getpid() truc tiep tu truoc,
  khong doi. session_cleanup chi dung prune_dead_holders, khong anh
  huong.
- scripts/s2_flip_live.py: pill_acquire_cmd() khoi dong sleeper tren
  laptop, acquire voi --pid $SLEEP_PID, echo PILL_SLEEP_PID= de
  release dung, kill sleeper inline neu acquire that bai, giu nguyen
  rc cua acquire lam rc cua call (echo o cuoi khong duoc che rc).
  pill_release_cmd(pid=None) truyen --pid do + kill sleeper sau
  release. cdp_pill_hold parse PILL_SLEEP_PID tu output acquire;
  neu khong parse duoc thi release fallback pid-less (khong xoa duoc
  holder pid-keyed, note lai, holder heal qua prune khi sleeper het
  han). Docstring cdp_pill_hold sua theo: holder nay pid-keyed
  (sleeper pid), khong con pid-less.
- Docstring remove_holder (H3): "No call ever removes another run's
  entry" sai theo nghia den o bare-bare, thu hep thanh "No call ever
  removes another run's PID-KEYED entry" + ghi ro ngoai le bare key
  va yeu cau moi live caller truyen pid that.

## 3. R11: release parser chap nhan --method (20:41 +07, T+3m)

scripts/overlay.py release subparser them --method (default None).
Holder key la (agent, pid), method khong nam trong key nen gia tri
duoc chap nhan va bo qua cho viec xoa. Sua 1 cho nay chua ca 2 caller
truyen --method: s2_flip pill_release_cmd va cdp.mjs releaseCdpPill
(dong 79). Khong sua cdp.mjs (fail-closed gate, tranh dong vao).
Verify tren VM sau sua: `release --agent X --method CDP --pid 1`
rc=0 (truoc sua rc=2 "unrecognized arguments").

## 4. Council 2 E1 + E2, C2 + R4 (20:41-20:42 +07, T+4m)

- E1: test_cmd_release_pid_none_keeps_pid_keyed_holder: release
  pid-less giu holder pid-keyed + output van liet ke no; release
  sau voi --pid do thi xoa het. Help text --pid cho ca acquire va
  release: acquire noi key la agent:pid; release noi pid-less chi
  xoa bare entry, holder pid-keyed can --pid cua no.
- E2: test_cmd_acquire_daemon_failure_keeps_concurrent_holder:
  duong D1 exception (daemon ensure failure) giu holder pid-keyed
  dong thoi, mirror test 3 (duong invisible).
- C2: wayland_env discovery branch dung setdefault cho
  WAYLAND_DISPLAY (khong ghi de display caller dua). Test moi
  test_wayland_env_keeps_caller_display.
- R4: hypr_cmd.desktop_env chi chon thu muc (is_dir) lam signature.
  Test moi test_from_dir_listing_skips_files.

## 5. Test moi (20:42 +07, T+4m)

tests/test_overlay.py, 5 test moi (sau test_cmd_acquire_invisible_
keeps_concurrent_holder, kem trong khoi __main__):
- test_cmd_acquire_invisible_pid_keyed_keeps_bare_holder (H1):
  holder tran song sot sau acquire that bai co pid.
- test_cmd_release_pid_none_keeps_pid_keyed_holder (E1).
- test_cmd_acquire_daemon_failure_keeps_concurrent_holder (E2).
- test_hold_passes_calling_pid (H1): capture argv subprocess, acquire
  va release cung --pid = os.getpid() cua tien trinh goi.
- test_wayland_env_keeps_caller_display (C2).
tests/test_s2_flip_pill.py, 2 test moi:
- test_acquire_keys_holder_by_laptop_sleeper_pid (H1): acquire chua
  nohup sleep 600 + --pid $SLEEP_PID + PILL_SLEEP_PID=; release
  chua --pid 4242 + kill 4242 (FakeHarness tra PILL_SLEEP_PID=4242).
- test_release_falls_back_pid_less_without_parsed_pid: khong co pid
  trong output thi release fallback pid-less, khong crash.
tests/test_hypr_cmd.py, 1 test moi:
- test_from_dir_listing_skips_files (R4).

## 6. Verify tren VM (20:44-20:49 +07, T+6m to T+11m)

Targeted, chay bang discover (load_tests can _function_test_support
chi chay duoc qua discover):
```
python3 -m unittest discover -s tests -p 'test_overlay.py'
Ran 27 tests in 0.024s, OK        (22 cu + 5 moi)
python3 -m unittest discover -s tests -p 'test_s2_flip_pill.py'
Ran 5 tests in 0.002s, OK         (3 cu + 2 moi)
python3 -m unittest discover -s tests -p 'test_hypr_cmd.py'
Ran 25 tests in 0.003s, OK        (24 cu + 1 moi)
python3 -m unittest discover -s tests -p 'test_chromium_cli.py'
Ran 23 tests in 1.273s, OK        (hold() doi khong gay hong CLI)
```
Kiem chung test moi bat duoc loi cu: worktree /tmp/amend2-baseline
tai 8f600b9 (code cu), copy 3 file test moi sang:
- test_overlay: Ran 27, FAILED (failures=8) = 5 test moi + 3 test
  amend-1, dung nhu ky vong.
- test_s2_flip_pill: test sleeper FAIL (code cu khong co sleeper),
  test_send_browser ERROR vi pill_release_cmd() cu khong nhan pid
  (chung minh code cu thieu tham so pid).
- test_hypr_cmd: Ran 25, FAILED (failures=1) = dung test R4 moi.
Worktree da xoa. Vay test moi that su bat duoc hanh vi cu.

Full suite dong thoi (20:45-20:49 +07, 214.5s),
log /tmp/w-pillfix-amend2-fullsuite.log:
```
Ran 2360 tests in 214.538s
FAILED (failures=1, errors=2, skipped=17)
```
3 loi giong het baseline, deu loi moi truong co san, khong cham
overlay/s2_flip/hypr_cmd:
- ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26)
- ERROR test_tc02_controller test_typed_text_check_passes... (tesseract)
- FAIL test_tc02_controller test_typed_text_check_fails... (tesseract)
Ran 2360 (cao hon 2332 cua Council 1 do lane khac them test trong
checkout dung chung; bat bien quan trong giong het: failures=1,
errors=2, skipped=17, cung 3 loi ten). Ket luan: 0 regression moi.
0 dau gach ngang dai o ca 6 file sua (grep count 0).

Commit + push (20:49 +07):
```
git add -- scripts/overlay.py scripts/s2_flip_live.py scripts/hypr_cmd.py tests/test_overlay.py tests/test_s2_flip_pill.py tests/test_hypr_cmd.py
git commit -m "fix: pid-keyed pill holders (H1 bare-bare), release --method (R11), E1/E2 tests, C2+R4"
git push origin todolist-push
git ls-remote origin todolist-push
```
Ket qua: commit 14cf4dc93aa18d6e03bdb8c29ec514289a464d3b tren
todolist-push, 6 files, 305 insertions, 26 deletions. Khong commit
tests/realistic/clone1-batch3/results.json (cua worker khac) va
khong dong vao file untracked.

## 7. H2: sync laptop + restart daemon (20:49-20:51 +07, T+11m to T+13m)

Trang thai truoc sync (chi doc, ssh-laptop.sh):
- Laptop HEAD 331523f, branch todolist-push; dirty: M scripts/cdp.mjs,
  scripts/indicator.py, scripts/overlay.py, tests/test_indicator.py,
  tests/test_overlay.py (toan bo la W-PILLFIX/F4 da land tren VM).
- holders.json chi con S2-flip (acquired 2026-11-22T20:34:45+07:00,
  method CDP, pid null); daemon PID 115582, started 19:40:45, elapsed
  01:08:34; khong co s2_flip hay node cdp nao dang chay (khong co send
  nao giua chung). Holder 15 phut tuoi, stale do release hong vi R11
  (xem muc 8).
- Kiem tra truoc sync: `git diff origin/todolist-push` chi co 4 dong
  `+` tren toan bo 5 file, dung la code remove_holder CU (wipe-all)
  ma amend-1 da thay the, khong phai viec local chua land. Khong co
  incoming commit nao cham results.json (git log 331523f..
  origin/todolist-push -- tests/realistic/clone1-batch3/results.json
  rong). Phat hien them: cdp.mjs tren laptop DANG THIEU pill gate
  (code gate co tren origin nhung khong co trong working tree) vi
  laptop chua sync tu khi gate land; sync nay khoi phuc lai gate.

Sync (backup truoc, de phong):
```
mkdir -p /tmp/amend2-laptop-backup && cp <5 file> /tmp/amend2-laptop-backup/
git fetch origin
git checkout origin/todolist-push -- scripts/overlay.py scripts/cdp.mjs scripts/indicator.py tests/test_indicator.py tests/test_overlay.py
git merge --ff-only origin/todolist-push
```
Ket qua: HEAD 14cf4dc (chinh commit amend2). results.json con nguyen
(4113 bytes, 17:50), git status chi con file untracked improvements/*
(cua worker khac). Backup du 5 file tai /tmp/amend2-laptop-backup/.

Verify file co fix (ssh-laptop.sh):
```
sha256sum scripts/overlay.py
4cb46f9d1329034a1e0ad9c78e5b904ebd725835ec6de0f14ff2fae78d7059ae  (khop VM)
grep -c "PID-KEYED" scripts/overlay.py -> 1 (docstring moi)
release parser co --method (dong 674); cdp.mjs co lai pill gate (5 match)
```

Restart daemon (giu holders.json, KHONG release S2-flip):
```
kill -INT 115582   (SIGINT -> KeyboardInterrupt -> finally chay sach:
                    hide pill, close native, unlink socket/daemon.json)
```
Verify sau kill: daemon 115582 gone, daemon.json unlinked,
holders.json van chi con S2-flip (20:34:45). Daemon log co
KeyboardInterrupt (finally da chay).

Start daemon moi (detached, GUI env nhu _ensure_daemon):
```
SIG=$(ls /run/user/1000/hypr/ | head -n1)
HYPRLAND_INSTANCE_SIGNATURE=$SIG WAYLAND_DISPLAY=wayland-1 \
XDG_RUNTIME_DIR=/run/user/1000 setsid nohup python3 \
~/computer-use-wayland/scripts/overlay.py daemon \
>> /tmp/amend2-daemon.log 2>&1 < /dev/null & disown
```
Verify sau start (20:50:47 +07):
```
daemon.json: {"pid": 160727, "started": "2026-11-22T20:50:47+07:00"}
overlay.py status: holders chi S2-flip (20:34:45), label
"S2-flip via CDP", owner daemon, visible true
```
Daemon moi chay code da fix, pill hien lai cho holder S2-flip duoc
bao toan. Khoang pill tat chi vai giay giua kill va start.

Smoke test tren daemon moi (20:51:01 +07):
```
# sleeper pid that + acquire/release pid-keyed + --method (R11)
setsid nohup sleep 120 ... & SPID=$!
acquire --agent AMEND2-SMOKE --method smoke --pid $SPID
  -> holder 'AMEND2-SMOKE:160869', holders 2 (smoke + S2-flip), visible true
release --agent AMEND2-SMOKE --method smoke --pid $SPID   (rc=0, R11 xong)
  -> holders chi con S2-flip, visible true
```
Smoke test construct sleeper cua s2_flip (20:51:13 +07, dung cau
lenh shell nhu pill_acquire_cmd, agent tam AMEND2-SLEEPER):
```
nohup sleep 600 ... & SLEEP_PID=$!; acquire ... --pid $SLEEP_PID;
ACQ_RC=$?; echo PILL_SLEEP_PID=$SLEEP_PID; [ $ACQ_RC -ne 0 ] && kill ...; exit $ACQ_RC
  -> PILL_SLEEP_PID=160976, holder 'AMEND2-SLEEPER:160976', S2-flip yen
release --agent AMEND2-SLEEPER --method CDP --pid 160976; kill 160976
  -> holders chi con S2-flip, visible true; sleeper gone; khong con
     sleep thua nao; daemon 160727 van song.
```
H2 xong: file da fix, daemon da restart voi code moi, smoke
acquire/release pass, S2-flip bao toan.

## 8. Con no / luu y cho Muse tong (khong phai dieu kien chan live)

- Holder S2-flip bare STALE (acquired 20:34:45, tu send truoc khi
  R11 duoc sua; release cua no luon fail rc=2 nen khong bao gio tu
  xoa). Release pid-keyed moi cua s2_flip se khong xoa bare key nay
  (dung thiet ke E1), va prune khong bao gio cham bare key. Can 1
  lenh don thu cong de don: `overlay.py release --agent S2-flip`
  (khong --pid) tren laptop, sau khi chac khong co send nao dang
  chay. Toi KHONG lam vi brief cam release S2-flip; de Muse tong
  quyet. Den luc do pill se tat (holders ve 0, daemon tu thoat),
  lan send s2_flip sau se acquire lai binh thuong voi key pid-keyed.
- cdp.mjs tren laptop da thieu pill gate truoc sync nay (laptop
  chua sync tu khi gate land d0602dd). Sync da khoi phuc. Lane nao
  quan ly laptop repo nen biet: laptop lag VM kha xa (331523f).
- /tmp/amend2-laptop-backup/ tren laptop giu ban sao 5 file truoc
  sync; /tmp/amend2-daemon.log la log daemon moi. /tmp/w-pillfix-
  amend2-fullsuite.log la log full suite VM.

## 9. Commit va push (log nay)

Lenh:
```
git add -- improvements/w-pillfix-amend2-log.md
git commit -m "docs: W-PILLFIX-AMEND2 log (H1/R11/E1/E2/H2/C2/R4 closed)"
git push origin todolist-push
git ls-remote origin todolist-push
```
Ket qua: code + test commit 14cf4dc93aa18d6e03bdb8c29ec514289a464d3b;
log commit 448fee69925e94eb340de4e3179458e31cccedc4, ca hai tren
todolist-push, ls-remote verify khop HEAD local.
