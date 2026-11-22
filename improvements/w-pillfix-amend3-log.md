# W-PILLFIX-AMEND3 log: close remaining review conditions of W-PILLFIX-AMEND2

Worker doc lap W-PILLFIX-AMEND3 (khong phai W-PILLFIX-AMEND2, khong
phai COORD-CLICK-9). Nhiem vu tu Muse tong: dong cac dieu kien con
lai cua amend 2 (14cf4dc + 448fee6 + 4a4fae3, 4 review deu GO hoac GO
WITH CONDITIONS). DAY LA VONG CUOI cho pill, khong mo them vong sau.
Khong chay live proof, khong dong/mo/navigate tab nao trong Zen cua
Pham Tuan, khong tu spawn reviewer, khong release bat ky holder nao.
Moi gio Asia/Ho_Chi_Minh. Khong dau gach ngang dai. Khong ydotool.
Khong thong tin ca nhan. Chuan Lauren Tan: lenh chay + output +
commit hash + log thoi gian.

## 0. Doc review (21:10 +07, T+0m)

Doc improvements/w-pillfix-amend2-log.md va 4 review:
- council-1 c1af8aa: GO, khong dieu kien chan live (G1 stale holder
  la viec cua coordinator, khong phai dieu kien).
- council-2 ec48240: GO WITH CONDITIONS, 2 test-only follow-up:
  C1 pin 2 fragment shell load-bearing trong lenh acquire cua
  s2_flip; C2 test hold() khi acquire fail.
- council-3 c099019: GO WITH CONDITIONS, C1 don holder S2-flip bare
  stale (coordinator action, KHONG phai viec cua amend nay; brief
  cam dong vao holder, xem muc 7).
- redteam ff8c228: GO WITH CONDITIONS, C1 (H1 re-check holder truoc
  activate), C2 (H2 bo fallback release pid-less), C3-C5 tuy chon
  (deferred, muc 6).

## 1. H1 (Redteam C1, MEDIUM): re-check holder truoc activate (21:11 +07, T+1m)

Van de: activate_browser (Target.activateTarget + Page.bringToFront
qua /tmp/c5-activate.mjs, helper tho khong co pill) chi duoc che boi
holder S2-flip sleeper; cdp_pill_hold chi check rc acquire 1 lan roi
yield, khong bao gio xac nhan lai holder truoc activate. Sleeper
chet trong cua so ~1-2s cua activate thi pill rot ma activate van
chay (doi tab + bringToFront, focus steal, khong pill).

Fix, scripts/s2_flip_live.py:
- Moi: pill_holder_alive(sleep_pid) chay `overlay.py status` tren
  laptop (read-only; cmd_status prune dead holders truoc, nen key
  cua sleeper chet da bien mat luc holders duoc bao cao) va check
  key chinh xac S2-flip:<sleep_pid> co trong holders khong. Tra
  False khi key vang, khi khong co pid de check (sleep_pid None:
  khong xac dinh duoc key, nen khong the xac nhan), hoac khi chinh
  check loi. Fail closed.
- cdp_pill_hold giu sleep_pid da parse tren self._pill_sleep_pid
  trong suot hold (khoi tao None trong __init__, xoa trong finally)
  de send_browser dung lai.
- send_browser: sau khi vao hold, neu held va holder khong con
  song thi abort ngay voi outcome aborted-pill-lost, error
  'S2-flip pill holder gone before activate', wall_ms, truoc khi
  goi _send_browser_inner. Khong activate, khong program, khong
  V12. Release trong finally van chay (holder da mat thi release
  chi la no-op, ghi nhan). Acquire that bai (held False) van chay
  body nhu cu (best effort, khong doi): re-check chi ap dung khi
  acquire bao held.
- Re-check chay ca khi self.activate False: luc do buoc visible
  dau tien la program (qua cdp.mjs act gate), cung vi tri gate, cung
  co che, khong them rui ro.
- Outcome aborted-pill-lost mang day du field nhu cac outcome khac
  (browser, label, endpoint, message, target_id, program_variant,
  wall_ms). Voi set_value, delayed_targets van dua no vao recount
  10s sau (co target_id + message); count 0 la bang chung abort
  khong gui gi.

Test moi, tests/test_s2_flip_pill.py:
- test_send_aborts_when_holder_lost_before_activate: FakeHarness
  tra pill-status voi holders rong (sleeper chet + prune sau
  acquire), activate/oneshot/v12 deu fake va ghi lai. Assert
  outcome aborted-pill-lost, 0 visible action, commands dung
  ['pill-acquire', 'pill-status', 'pill-release'].
- FakeHarness.ssh mac dinh tra pill-status voi holders chua
  S2-flip:4242 (holder song), nen test happy path cu van chay qua
  re-check; test_send_browser_holds_pill_around_send cap nhat
  commands thanh ['pill-acquire', 'pill-status', 'pill-release']
  va release index 2.

## 2. H2 (Redteam C2, MEDIUM): bo fallback release pid-less (21:11 +07, T+1m)

Van de: acquire ok nhung khong parse duoc PILL_SLEEP_PID thi
cdp_pill_hold fallback ve pill_release_cmd(None), chi xoa bare key:
co the xoa holder tran dang song cua run khac cung agent (dung
hazard bare-bare ma amend nay sinh ra de dong), trong khi holder
pid-keyed that van con va sleeper mo coi chay du 600s; lai tra rc=0.

Fix, scripts/s2_flip_live.py:
- pill_release_cmd(pid) gio bat buoc pid, bo nhanh pid None (khong
  con caller nao truyen None: grep chi con cdp_pill_hold + test).
  Docstring ghi ro: khong con pid-less release.
- cdp_pill_hold finally: chi release khi held va sleep_pid is not
  None. Khi khong parse duoc pid thi khong release gi, chi note
  (khong fallback), de daemon prune holder khi sleeper het han.
  Docstring sua theo.
- Test cu test_release_falls_back_pid_less_without_parsed_pid doi
  ten thanh test_no_release_without_parsed_pid: assert commands
  chi co ['pill-acquire'] (khong co release call nao) va note co
  chua 'no PILL_SLEEP_PID'.

## 3. Council 2 C1 + C2 (21:12 +07, T+2m)

- C1: test_acquire_keys_holder_by_laptop_sleeper_pid them 2 string
  assertion cho fragment load-bearing trong lenh acquire:
  '[ $ACQ_RC -ne 0 ] && kill $SLEEP_PID' (giet sleeper khi acquire
  fail) va 'exit $ACQ_RC' (giu rc acquire, khong de echo che thanh
  held=True khi khong co holder).
- C2: test moi test_hold_acquire_failure_raises_without_release
  trong tests/test_overlay.py (kem trong khoi __main__): fake
  subprocess raise CalledProcessError o acquire, assert hold()
  raise truoc khi yield, dung 1 subprocess call, khong co release
  call. Luu y trung thuc (muc 4): test nay PASS ca tren code cu
  8f600b9, vi hold() luc do da raise truoc yield voi check=True.
  Day la coverage completion theo yeu cau cua Council 2, khong
  phai regression guard cho thay doi cua amend 3.

## 4. Verify tren VM (21:12-21:14 +07, T+2m to T+4m)

Targeted, chay bang discover:
```
python3 -m unittest discover -s tests -p 'test_overlay.py'
Ran 28 tests in 0.024s, OK        (27 cu + 1 moi C2)
python3 -m unittest discover -s tests -p 'test_s2_flip_pill.py'
Ran 6 tests in 0.002s, OK         (5 cu + 1 moi H1; test fallback
                                   da viet lai thanh no-release, C1
                                   assertion them vao test sleeper)
python3 -m unittest discover -s tests -p 'test_hypr_cmd.py'
Ran 25 tests in 0.003s, OK
python3 -m unittest discover -s tests -p 'test_chromium_cli.py'
Ran 23 tests in 1.323s, OK        (hold() doi khong gay hong CLI)
```
py_compile scripts/s2_flip_live.py + scripts/overlay.py OK.
0 dau gach ngang dai o ca 3 file sua (grep count 0).
Grep pill_release_cmd() khong doi so: khong con caller nao.

Baseline check: worktree /tmp/amend3-baseline tai 8f600b9 (code cu),
copy 2 file test moi sang, chay, xoa worktree:
- test_s2_flip_pill: Ran 6, FAILED (failures=4) = dung 4 test lien
  quan amend 3: sleeper test (C1, code cu khong co sleeper),
  no-release test (H2, code cu chay fallback pid-less), H1 abort
  test (code cu khong co re-check, activate van chay), happy-path
  test (code cu khong co pill-status call). 2 test cu con lai pass.
- test_overlay: Ran 28, FAILED (failures=8) = dung 5 test moi amend2
  + 3 test amend-1, giong het baseline amend2. Test C2 moi PASS
  tren code cu (ly do muc 3), khong nam trong 8 failure.
Vay 3 test hanh vi moi that su bat duoc code cu; test C2 pin hanh vi
da co tu truoc.

## 5. Full suite (21:18 +07, T+8m)

Detached, log /tmp/w-pillfix-amend3-fullsuite.log:
```
Ran 2370 tests in 223.008s
FAILED (failures=1, errors=2, skipped=17)
```
3 loi giong het baseline, deu loi moi truong co san, khong cham
overlay/s2_flip/hypr_cmd:
- ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26)
- ERROR test_typed_text_check_passes_when_fragment_is_visible
  (test_tc02_controller, tesseract)
- FAIL test_typed_text_check_fails_when_fragment_is_absent
  (test_tc02_controller, tesseract)
Ran 2370 (cao hon 2360 cua worker amend2 do lane khac them test
trong checkout dung chung + 2 test moi cua amend nay; bat bien quan
trong giong het: failures=1, errors=2, skipped=17, cung 3 loi ten).
Ket luan: 0 regression moi.

## 6. Deferred (Redteam C3-C5 tuy chon, khong lam trong vong nay)

- C3 (H3): verify /proc/<pid>/cmdline la sleep truoc khi kill
  trong pill_release_cmd va pill_acquire_cmd. Deferred: kha nang
  pid tai su dung trong cua so vai giay la khong dang ke
  (pid_max 4194304), redteam tu danh LOW.
- C4 (H5): cmd_release log warning khi was_present False ma co pid.
  Deferred: observability only, hanh vi co san tu truoc, khong
  phai dieu kien.
- C5 (H6): thu tuc restart daemon co wait-for-death poll + retry
  khi bind fail. Deferred: procedural, lan restart amend2 chay tot,
  _ensure_daemon tu hoi phuc; viet thu tuc la viec doc, khong phai
  code gate.
- Ghi them: G1-G4 cua Council 1 amend2 (sleeper bound 600s, `|| true`
  che rc release, hold() check=True trong finally co the che
  exception) van la note, khong phai dieu kien, khong doi.

## 7. Khong dong vao (theo brief)

- Holder S2-flip bare STALE (acquired 20:34:45, pid null) tren laptop:
  KHONG don, KHONG release bat ky holder nao. Council 3 C1 ghi day
  la coordinator action truoc live run, khong phai viec cua amend
  nay. Amend 3 khong chay lenh nao tren laptop ngoai doc (khong co
  ssh-laptop.sh nao trong vong nay); moi verify la tren VM.
- File dirty tests/realistic/clone1-batch3/results.json (cua worker
  khac) khong dong vao, khong commit.

## 8. Commit va push (log nay)

Lenh:
```
git add -- scripts/s2_flip_live.py tests/test_s2_flip_pill.py tests/test_overlay.py
git commit -m "fix: pill holder re-check before activate (H1), no pid-less fallback release (H2), C1/C2 tests"
git push origin todolist-push
git ls-remote origin todolist-push
```
Ket qua: code + test commit e7e973ecb8f3b218b4ac314d0c22f0f9baef0b1b
tren todolist-push, 3 files, 175 insertions, 28 deletions.
ls-remote verify khop HEAD local. Khong commit
tests/realistic/clone1-batch3/results.json (cua worker khac) va
khong dong vao file untracked.
```
git add -- improvements/w-pillfix-amend3-log.md
git commit -m "docs: W-PILLFIX-AMEND3 log (H1/H2/C1/C2 closed)"
git push origin todolist-push
git ls-remote origin todolist-push
```
Ket qua: [GHI SAU KHI CHAY]
