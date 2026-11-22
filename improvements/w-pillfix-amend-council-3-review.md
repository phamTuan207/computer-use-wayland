# Council 3 (risk) review: W-PILLFIX-AMEND (5a272ae + a355002)

Reviewer doc lap Council 3 (lens rui ro), cho Muse tong. Chi review,
khong sua fix, khong chay live, khong tu spawn reviewer. Moi gio
Asia/Ho_Chi_Minh. Khong dau gach ngang dai. Khong ydotool. Khong thong
tin ca nhan. Chuan Lauren Tan: lenh chay + output + commit hash + log
thoi gian.

## Verdict: GO VOI DIEU KIEN

Fix dung pham vi R6/C1, test that, buoc 0 sach. Nhung co 2 lo van mo
phai dong truoc live tiep theo (H1 bare-bare, H2 chua deploy), va 1
tuong tac lam H2 kho hon (R11 chan daemon tu cycle). Cac muc con lai
de hoan duoc.

Dieu kien (truoc live tiep theo):

1. Part 2: overlay.hold() va s2_flip pill_acquire_cmd /
   pill_release_cmd truyen --pid that; sua s2_flip release bo --method
   (R11); sua docstring cdp_pill_hold va docstring remove_holder (H3);
   them test bare-bare (du kien fail cho den khi xong) hoac ghi ro la
   gioi han da biet.
2. Deploy: fast-forward laptop len origin/todolist-push (giai quyet
   file chua commit), verify file overlay.py tren laptop co fix,
   restart daemon PID 115582, verify bang smoke acquire/release.
3. Cung lane follow-up voi dieu kien 1: C2 (WAYLAND_DISPLAY
   setdefault) + R4 (desktop_env is_dir).

De hoan (khong chan live tiep theo): R1, R2/R3, R7 (them log warn),
R8/R9 (docs), R10 dai han.

## 1. Fix R6/C1: dung, da kiem chung doc lap

- Doc diff 5a272ae: remove_holder moi chi pop dung 1 key
  _holder_key(agent, pid). pid int > 0 thi chi xoa agent:pid; pid
  None thi chi xoa key tran. Docstring cap nhat theo.
- Kiem tra caller: khong caller nao phu thuoc vao hanh vi xoa het cu.
  Bang caller (tu doc code): daemon release handler (agent, pid tu
  req); cmd_acquire D1 (532) + invisible (547) xoa dung key vua add;
  cmd_release no-daemon (561) + socket-failure fallback (569) xoa dung
  key duoc yeu cau; first_action acquire (143) + release (181) truyen
  os.getpid(); overlay.hold() acquire/release bare (cap nhat quan);
  prune_dead_holders khong goi remove_holder; cmd_stop xoa het co y.
- Targeted chay lai tren VM: Ran 22 tests, OK (19 cu + 3 moi).
- Baseline chay lai doc lap: worktree /tmp/c3-amend-baseline tai
  8f600b9, copy file test moi sang, Ran 22, FAILED (failures=3), dung
  3 test moi fail, 19 cu pass. Worktree da xoa. Vay 3 test that su bat
  duoc R6.
- Luu y: worktree chi hop le cho targeted suite; full suite trong
  worktree thieu file gitignored (native/keyboard-protocol.c) nen
  khong dung (Council 1 amend da chung minh). Baseline cua toi chi
  chay targeted nen khong anh huong.

## 2. Buoc 0 release: dung duong, an toan, da kiem chung doc lap

- Worker dung `overlay.py release --agent W-PILLFIX` (duong release
  dung, khong sua tay holders.json, khong restart daemon), rc=0,
  20:09:25.
- Verify doc lap cua toi, chi doc qua ssh-laptop.sh, 20:17 +07:
  holders.json chi con S2-flip (acquired 2026-11-22T20:13:27+07:00,
  method CDP, pid null); W-PILLFIX da het; daemon PID 115582 van song
  (started 19:40:45, elapsed 36:43).
- Buoc 0 chay luc 20:09 bang code cu tren laptop (fix commit 20:16).
  Voi code cu, remove_holder('W-PILLFIX', None) xoa het key cua agent
  W-PILLFIX; W-PILLFIX luc do chi co key tran nen ket qua giong code
  moi. S2-flip la agent khac nen khong anh huong du code nao. Buoc 0
  an toan ca 2 phien ban.
- Holder S2-flip doi timestamp 20:02:18 sang 20:13:27 nghia la s2_flip
  da acquire lai sau buoc 0 (harness acquire moi lan send), holder
  dang duoc duy tri, khong phai rac cu. Buoc 0 khong de lai rac.
- Council 1 (goc) dieu kien 2 (release holder smoke W-PILLFIX) coi
  nhu xong.

## 3. Full suite: 0 regression, chenh lech so Ran giai thich duoc

- Chay lai doc lap cua toi, main tree, 20:16-20:22 +07, log
  /tmp/c3-amend-fullsuite.log (330.6s, cham do 3 suite chay song song):
```
Ran 2332 tests in 330.646s
FAILED (failures=1, errors=2, skipped=17)
```
- 3 loi, giong het baseline, deu loi moi truong, khong cham
  overlay/indicator:
  - ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26)
  - ERROR test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_passes_when_fragment_is_visible (tesseract is unavailable)
  - FAIL test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_fails_when_fragment_is_absent (tesseract is unavailable)
- Kiem chung: grep `import overlay` trong 2 file loi tra rong (rc=1),
  nen fix (chi dong overlay.py + test_overlay.py) khong the gay ra
  3 loi do.
- Chenh lech Ran: worker bao 2316, redteam chay lai 2316, toi chay
  2332 (+16). Giai thich: checkout dung chung dang duoc sua boi nhieu
  lane song song trong cung cua so (HEAD doi a355002 sang 5d5111f luc
  toi review; loader dem 2340 test case luc 20:26; worktree cua
  Council 1, Council 2, redteam cung ton tai). So Ran troi theo test
  duoc them/bot boi lane khac, khong phai do fix (fix chi them dung 3
  test, da chung minh o muc 1). Bat bien quan trong giong het o ca 3
  lan chay: failures=1, errors=2, skipped=17, cung 3 loi ten. Vay 0
  regression moi, 0 loi moi do fix.
- Luu y: loader 2340 tru Ran 2332 = 8, dung bang so test cua lop
  CursorFileTests (8 test, khong chay rieng do setUpClass loi). Khop.

## 4. H1 (trung binh): va cham bare-bare van mo

- Sau fix, 2 run pid-less cung agent van chia 1 key tran duy nhat.
  add_holder ghi de len nhau; remove_holder pid-less xoa key chung.
  Mot acquire that bai pid-less xoa holder tran cua run pid-less khac
  dang song, pill roi giua chung cho run do.
- Caller live con pid-less: overlay.hold() (overlay.py 620, dung boi
  chromium_cli._pill_hold dong 654, agent Muse) va s2_flip
  pill_acquire_cmd (s2_flip_live.py 596, agent S2-flip). cdp.mjs
  truyen --pid (dong 65, 79). first_action truyen os.getpid().
- Kich ban live that: 2 lane song song dung chromium_cli
  (mo/activate/close) cung luc; 1 lane acquire that bai invisible
  trong luc outage thi lane kia mat pill giua chung. Huong van
  fail-closed (act ke tiep cua lane kia bi tu choi, khong chay mu),
  nen day la mat pill oan + retry, khong phai chay mu. Nhung live
  phase chay nhieu lane dong thoi nen xac suat va cham la that, va
  pill roi se lam nhieu ket qua do.
- Day chinh la phan 2 cua amend 1 (redteam goc), ma amend log muc 2
  da ghi la follow-up rieng. Dieu kien 1 dong lo nay.
- H3 (nhe): docstring moi viet "No call ever removes another run's
  entry" la sai theo nghia den o truong hop bare-bare. Thu hep thanh
  "No call ever removes another run's PID-KEYED entry" hoac dong H1
  bang dieu kien 1 roi moi giu cau nay. Chi la van ban, nhung
  docstring sai dan nguoi doc sau danh gia sai do an toan.

## 5. H2 (trung binh): fix chua co mat tren laptop, daemon van chay code cu

- Kiem tra chi doc tren laptop (ssh-laptop.sh, 20:17 +07):
  - File /home/james/computer-use-wayland/scripts/overlay.py van
    remove_holder CU: docstring "Without a pid, all of the agent's
    entries are removed", sha256
    b551cf6b2e1503824c690f46dae5ce88c90dfca6cf0f0761699e808717be59b4
    khop dung 8f600b9.
  - Daemon PID 115582, started 19:40:45, van chay; daemon nap
    overlay.py luc start (truoc fix 20:16), nen code trong bo nho la
    code cu.
  - Ket luan: R6 CHUA duoc sua tren may live, ca duong CLI (file cu)
    lan duong daemon socket (bo nho cu). Live tiep theo van dinh R6
    cho den khi dieu kien 2 xong.
- Duong di deploy: laptop HEAD 331523f la ancestor cua
  origin/todolist-push, nen fast-forward duoc; nhung laptop co file
  chua commit (M scripts/cdp.mjs, scripts/indicator.py,
  scripts/overlay.py, tests/test_indicator.py,
  tests/test_overlay.py) can giai quyet truoc khi pull. Sau sync,
  verify file co fix, roi restart daemon de duong socket release
  (overlay.py:413) cung lay code moi.
- Tuong tac voi R11 (lam H2 kho hon): daemon chi thoat khi holders
  ve 0, nhung holder S2-flip pid-less khong bao gio duoc release dung
  (s2_flip release cmd chua --method bi parser tu choi, rc=2, Council
  1 amend da verify tren VM), nen daemon khong tu cycle lay code moi.
  Can restart daemon thu cong (hoac release S2-flip dung bang lenh
  khong --method de holders ve 0), roi verify. Dieu kien 1 sua R11
  cung giai quyet goc cua tuong tac nay.

## 6. Cac muc de ngoai pham vi: danh gia rui ro tung muc

- C2 (WAYLAND_DISPLAY bi ghi de): chua sua, wayland_env van
  `env['WAYLAND_DISPLAY'] = discovered['WAYLAND_DISPLAY']`. Tren may
  nay display that la wayland-1 (hang so trong hypr_cmd.py) nen khong
  anh huong live hom nay. De hoan duoc, nhung chi la sua 1 dong
  (setdefault nhu code cu), nen gom vao cung lane follow-up voi dieu
  kien 1 (dieu kien 3).
- R4 (desktop_env chon sai instance): chua sua,
  `sorted(os.listdir)[0]`, khong loc is_dir. Tren laptop chi co 1
  entry duoi /run/user/1000/hypr/ nen latent, chua kich hoat. De hoan
  duoc, gom vao lane follow-up (dieu kien 3).
- R1 (signature cu khong validate): chua sua. Can probe hyprctl +
  re-discovery, thay doi lon hon, can lane rieng. Hien 1 instance
  dir, signature song, khong kich hoat. De hoan, khong chan live tiep
  theo.
- R2/R3 (nhan loi theo nguyen nhan / PATH): chan doan, khong phai loi
  live. De hoan.
- R7 (CU_CDP_PILL=0 tat gate): chua sua. Kiem chung: bien khong duoc
  set trong ssh env, khong noi nao trong repo set no (grep chi thay
  doc + 2 cho doc code, deu ghi "fixture tests only, never live"). De
  hoan, nhung nen them log warn moi lan no tat gate (re, de lane sau).
- R8 (status ack vs pixel): tinh chat cua status, khong phai thieu
  bang chung render nua (W-PILLVERIFY2 da PASS bang grim, 9ac4dcd).
  Chi can ghi ro trong docs. De hoan.
- R9 (status co side-effect / cham): latent, spawn live do 205ms. De
  hoan.
- R10 dai han (holder pid-null khong het han): Council 1 (goc) dong y
  khong auto-prune theo tuoi. Phan cap bach da xong nho buoc 0
  (W-PILLFIX het); phan con lai (S2-flip) se het khi R11 duoc sua
  (dieu kien 1) vi release cua no se chay duoc. De hoan.

## 7. Hoi tu voi Council 1 va redteam (amend)

- Council 1 amend: GO VOI DIEU KIEN, dieu kien 1+2 (truyen --pid that
  + sua release --method / docstring) trong 1 follow-up lane. Redteam
  amend: GO VOI DIEU KIEN, C1 (part 2 + test bare-bare + docstring),
  C2 (sync + restart daemon), C3 (khuyen nghi R11).
- Review nay doc lap, nhung hoi tu: cung H1, cung H2, cung R11. Bang
  chung cua toi la lenh chay rieng (targeted 22 OK, baseline 3 fail,
  full suite 2332, laptop chi doc 20:17), khong sao chep.
- Khac biet nho: toi them dieu kien 3 (gom C2+R4 vao lane follow-up)
  va phan tich tuong tac R11/H2. Toi khong lap lai attack A1-A12 cua
  redteam (da du); toi kiem chung bang code read + chay lai suite +
  baseline.

## 8. Log thoi gian (Asia/Ho_Chi_Minh)

- 20:15:45, T+0m: nhan task Council 3 tu Muse tong.
- 20:16, T+0m: doc amend log + diff 5a272ae/a355002 + redteam/council
  3 review goc; bat dau full suite nen (PID 51446, log
  /tmp/c3-amend-fullsuite.log).
- 20:16-20:17, T+1m: doc Council 1/2 review goc; kiem tra laptop chi
  doc (holders.json, daemon PID 115582, file overlay.py cu, sha256
  b551cf6b).
- 20:18, T+2m: doc overlay.py (holder, daemon serve, cmd_acquire /
  release, hold, wayland_env); targeted suite Ran 22 OK; baseline
  worktree 8f600b9: 3 test moi fail.
- 20:20, T+4m: doc caller first_action / s2_flip / chromium_cli /
  cdp.mjs; grep CU_CDP_PILL (khong noi nao set).
- 20:21-20:23, T+5m: doc s2_flip pill_acquire/release cmd (thieu
  --pid, release chua --method); cho full suite.
- 20:25, T+9m: full suite xong: Ran 2332, failures=1 errors=2
  skipped=17; loader dem 2340; doc redteam amend review 5d5111f.
- 20:27, T+11m: doc Council 1 amend review; verify 2 file loi full
  suite khong import overlay; xoa worktree baseline.
- 20:28, T+12m: viet review nay, commit + push, verify ls-remote.

## 9. Commit va push (review nay)

- Lenh: git add -- improvements/w-pillfix-amend-council-3-review.md
- Lenh: git commit -m "docs: Council 3 review of W-PILLFIX-AMEND (GO VOI DIEU KIEN)"
- Lenh: git push origin todolist-push
- Verify: git ls-remote origin todolist-push (ket qua bao ve Muse tong).
