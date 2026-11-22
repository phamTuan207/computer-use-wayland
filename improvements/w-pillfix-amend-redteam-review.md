# Redteam review: W-PILLFIX-AMEND (5a272ae + a355002)

Reviewer doc lap (redteam, khong phai W-PILLFIX-AMEND, khong phai
COORD-CLICK-9). Nhiem vu tu Muse tong: tan cong fix thu hep
remove_holder, tim cho gay. Khong sua fix, khong chay live, khong tu
spawn reviewer. Moi gio Asia/Ho_Chi_Minh. Khong dau gach ngang dai.
Khong ydotool. Khong thong tin ca nhan. Chuan Lauren Tan: lenh chay +
output + commit hash + log thoi gian.

## 0. Verdict: GO VOI DIEU KIEN

Fix dung cho pham vi no nhan (R6/C1): remove_holder moi chi xoa dung
1 key, holder pid-keyed cua run khac song sot sau acquire that bai
voi pid None. 3 test moi that su bat duoc R6 (fail dung 3 tren code
cu, pass tren code moi). Full suite khong regression moi. Buoc 0
release sach, S2-flip nguyen ven.

Nhung co 2 dieu kien bat buoc truoc live tiep theo, vi fix chua bao
het duong xoa nham holder va chua co mat tren may live:

- C1: land follow-up truyen --pid that cho cac caller pid-less
  (overlay.hold() va s2_flip pill_acquire_cmd), de lo H1 khong con
  duong di tren live; them test cho truong hop bare-bare (du kien
  fail cho den khi C1 xong) hoac ghi ro la gioi han da biet; sua
  docstring noi qua (H3).
- C2: sync fix len laptop VA restart daemon, verify ca hai, truoc
  live tiep theo. Hien tai file laptop van code cu va daemon PID
  115582 van chay code cu trong bo nho, nen R6 chua duoc sua tren
  may live (H2).
- C3 (khuyen nghi): sua R11 (parser release khong co --method) de
  s2_flip release that su chay duoc va daemon tu cycle lay code moi;
  neu khong, daemon giu code cu mai trong khi holder S2-flip pid-less
  ton tai. R11 co san truoc fix, khong tinh vao verdict, chi ghi de
  lane W-PILLCDP sua.

## 1. Pham vi da doc

- improvements/w-pillfix-amend-log.md (toan bo, 6 muc).
- Diff 5a272ae (scripts/overlay.py 31 dong, tests/test_overlay.py 67
  dong, log 143 dong) va a355002 (log 6 dong, chi ghi hash).
- scripts/overlay.py toan bo (doc hien tai, sau fix), dac biet
  _holder_key (102), add_holder (111), remove_holder (127),
  prune_dead_holders (149), Daemon.serve acquire/release (409-413),
  cmd_acquire (505-553), cmd_release (556-569), hold() (620).
- scripts/first_action.py acquire_overlay/release_overlay (120-183):
  truyen pid that (os.getpid()), an toan voi fix moi.
- scripts/s2_flip_live.py pill_acquire_cmd (596), pill_release_cmd
  (601), cdp_pill_hold (607): KHONG truyen --pid, holder pid-less.
- scripts/chromium_cli.py _pill_hold (640-654): dung overlay.hold
  ("Muse", "CDP"), KHONG truyen --pid, holder pid-less.
- scripts/cdp.mjs releaseCdpPill (70-88): goi release voi --agent,
  --method, --pid; parser release chi co --agent va --pid (R11).
- improvements/w-pillfix-redteam-review.md muc R6/R7/R11 va muc 4
  (amend list): amend 1 phan 2 (truyen --pid that cho hold() va
  s2_flip) da duoc amend log ghi la follow-up rieng, khong thuoc
  pham vi task nay.

## 2. Tan cong: ket qua (11 truong hop tu chay + 1 race tien trinh)

Script: /tmp/redteam_attack_overlay.py (scratch, khong trong repo),
chay tren VM copy cua scripts/overlay.py, thu muc tam rieng, khong
live, khong laptop. Len:
`python3 /tmp/redteam_attack_overlay.py`
Ket qua: 10 PASS, 1 HOLE. Targeted suite rieng:
`python3 -m unittest discover -s tests -p 'test_overlay.py'`
Ran 22 tests, OK (20:22 +07, chay lai doc lap).

| Case | Mo ta | Ket qua |
| A1 | pid None giu holder pid-keyed | PASS, after=['Muse:999001'] |
| A2 | pid int giu holder tran | PASS, after=['Muse'] |
| A3 | pid -1 chi xoa tran | PASS, key='Muse', after=['Muse:999001'] |
| A4 | pid 0 chi xoa tran | PASS, key='Muse', after=['Muse:999001'] |
| A5 | pid True map 'Muse:1', khong cham gi khac | PASS, key='Muse:1', present=False |
| A6 | pid khong ton tai giu tat ca | PASS, present=False |
| A7 | 2 holder pid-keyed cung agent, xoa 1 giu 1 | PASS, after=['Muse:222'] |
| A8 | bare-bare: acquire that bai pid-less xoa holder tran cua run khac | HOLE, rc=1, after=[] (H1) |
| A9 | 2 lan acquire that bai lien tiep giu holder pid-keyed | PASS, rcs=[1, 1] |
| A10 | race 9 thread (8 worker + 1 failed-acquire loop) | PASS, final={'Muse:999001'} |
| A11 | add pid -1 va 0 deu map ve key tran, nhat quan voi remove | PASS |
| A12 | race 4 tien trinh rieng biet, chung thu muc tam | PASS, final=['Muse:999001'] |

A12 chay bang /tmp/redteam_race_worker.py, 4 subprocess Popen chung
mot thu muc tam, moi tien trinh add/remove 10 holder pid-keyed
rieng; holder giu 'Muse:999001' song sot, trang thai cuoi chinh
xac. File lock (fcntl.flock) giu load-modify-save nguyen tu ca
xuyen thread lan xuyen tien trinh.

## 3. Lo tim duoc

### H1 (trung binh): va cham bare-bare, acquire that bai pid-less van xoa holder tran cua run khac dang song

Repro (A8, chay lai duoc bang script tren):
- Run A: overlay.add_holder('Muse', 'CDP') (pid-less, live).
- Run B (cung agent, pid-less): cmd_acquire voi _send_socket mock
  tra visible False; B ghi de key tran 'Muse' bang timestamp cua B,
  that bai invisible, goi remove_holder('Muse', None).
- Ket qua: rc=1, holders sau = [] (run A mat holder, pill roi giua
  chung cho run A du run A khong loi gi).

Nguyen nhan goc: 2 run pid-less cung agent chia 1 key tran duy nhat
('Muse'). add_holder ghi de len nhau, remove_holder xoa key chung.
Fix R6 chi bao ve holder pid-keyed, khong bao ve holder tran khoi
mot run pid-less khac. Docstring moi noi "No call ever removes
another run's entry" la sai theo nghia den o truong hop nay (xem H3).

Caller live con pid-less (duong di that, khong phai ly thuyet):
- overlay.hold() (overlay.py 620): acquire/release khong --pid.
  Dung boi chromium_cli._pill_hold (chromium_cli.py 654, agent
  Muse). Hai lenh chromium_cli dong thoi (2 lane song song) se va
  nhau dung kieu A8.
- s2_flip pill_acquire_cmd (s2_flip_live.py 596): acquire khong
  --pid, agent S2-flip. Chi co 1 harness s2_flip chay tai mot thoi
  diem nen va cham noi bo thap, nhung holder pid-less cua no van
  bi xoa neu mot acquire pid-less nao khac cung agent that bai.
- CLI mac dinh --pid None: bat ky lenh acquire thu cong nao khong
  --pid cung la holder tran.

Day chinh la phan 2 cua amend 1 trong review redteam goc (truyen
--pid that cho hold() va s2_flip), ma amend log muc 2 da ghi la
follow-up rieng. Redteam nay xac nhan: phan do chua lam, lo van mo.
Dieu kien C1 dong lo nay.

### H2 (trung binh): fix chua co mat tren laptop, daemon van chay code cu

Kiem tra chi doc tren laptop (ssh-laptop.sh, 20:20 +07):
- File /home/james/computer-use-wayland/scripts/overlay.py van
  remove_holder CU: docstring "Without a pid, all of the agent's
  entries are removed", code xoa het key cua agent khi pid None.
- Daemon PID 115582, started 19:40:45, elapsed 37:00, van chay;
  daemon.json xac nhan pid 115582, started 19:40:45. Daemon nap
  overlay.py luc start (truoc fix 20:16), nen code trong bo nho la
  code cu, ke ca khi file duoc sync sau.
- Ket luan: R6 CHUA duoc sua tren may live, ca duong CLI (file cu)
  lan duong daemon socket (bo nho cu). Live tiep theo van dinh R6
  cho den khi C2 xong.

Tuong tac lam C2 kho tu dong: daemon chi thoat khi holders ve 0,
nhung holder S2-flip pid-less khong bao gio duoc release dung
(R11: s2_flip release cmd chua --method bi parser tu choi), nen
daemon khong tu cycle lay code moi. Can sync file roi restart
daemon thu cong (hoac release S2-flip dung bang lenh khong --method
de holders ve 0), roi verify.

### H3 (nhe): docstring moi noi qua

remove_holder (overlay.py 127-136) viet: "No call ever removes
another run's entry". H1 chung minh cau nay sai: mot lan remove
pid-less xoa holder tran cua run pid-less khac cung agent. Nen thu
hep thanh "No call ever removes another run's PID-KEYED entry" hoac
dong H1 bang C1 roi moi giu cau nay. Chi la van ban, khong phai loi
code, nhung docstring sai dan nguoi doc sau danh gia sai do an toan.

## 4. Ghi nhan them (khong phai lo cua fix nay, khong tinh vao verdict)

- Pid am / 0 / bool (A3/A4/A5/A11): _holder_key dua tat ca ve key
  tran (tru True map 'Muse:1'). Add va remove dung chung mot ham
  nen nhat quan, khong xoa nham. Chi ghi nhan hanh vi; khong caller
  nao truyen pid am/0/bool hien nay. Daemon khong validate kieu pid
  trong request socket (JSON true se tao holder 'Muse:1'), thap.
- prune_dead_holders (overlay.py 149): coi PermissionError (pid ton
  tai nhung thuoc user khac) la chet va prune. Co san truoc fix, fix
  khong dong den. Tren may live daemon chay cung user james nen
  khong kich hoat thuc te.
- R11 (redteam goc muc 4, item 6): release parser khong co --method
  trong khi cdp.mjs releaseCdpPill (dong 81) va s2_flip
  pill_release_cmd deu truyen --method. Moi lan release deu loi
  argparse "unrecognized arguments: --method CDP". Co san truoc
  8f600b9, fix nay khong dong den. Chi anh huong C2/C3 (xem muc 0).
- Test 3 mock daemon: test_cmd_acquire_invisible_keeps_concurrent_holder
  mock _ensure_daemon va _send_socket, khong chay qua daemon that.
  Du cho claim hep R6 (duong failure cua cmd_acquire goi
  remove_holder), vi code duoc test la duong do. Khong phai lo.

## 5. 3 test moi co bao phu khong

Co, cho pham vi R6/C1 da claim. Kiem chung doc lap: worktree
/tmp/amend-baseline2 tai 8f600b9 (code cu), copy file test moi sang,
chay suite overlay: Ran 22, FAILED (failures=3), dung 3 test moi
fail, 19 test cu pass. Worktree da xoa. Vay 3 test that su bat duoc
R6, khong phai test trang tri. Redteam tu chay lai targeted suite
tren code moi: Ran 22, OK.

Khoang trong bao phu (redteam tu kiem chung bang script A1-A12,
khong co trong test file):
- Pid khong ton tai (A6): PASS, khong co test.
- 2 holder pid-keyed cung agent (A7): PASS, khong co test.
- Acquire that bai lien tiep (A9): PASS, khong co test.
- Pid am / 0 / bool (A3/A4/A5): hanh vi nhat quan, khong co test.
- Bare-bare (A8): HOLE, khong co test nao bat duoc, nen suite xanh
  trong khi lo van mo. Day la khoang trong quan trong nhat: them
  test cho A8 (du kien fail cho den khi C1 xong) hoac ghi ro la
  gioi han da biet.

## 6. Buoc 0 release: sach, S2-flip nguyen ven

Log muc 1 noi release W-PILLFIX bang `overlay.py release --agent
W-PILLFIX` (khong --method, khong --pid), rc=0, sau release chi
con S2-flip. Redteam kiem chung bang trang thai live tren laptop
(chi doc, 20:20 +07): holders.json chi con S2-flip, acquired
2026-11-22T20:13:27+07:00, pid null; W-PILLFIX da het; daemon PID
115582 van song. Timestamp S2-flip doi tu 20:02:18 (luc buoc 0)
sang 20:13:27 nghia la s2_flip da acquire lai sau buoc 0 (harness
acquire moi lan send), holder dang duoc duy tri chu khong phai rac
cu. Buoc 0 khong de lai rac, khong anh huong S2-flip.

Luu y: buoc 0 chay luc 20:09 bang code cu tren laptop (fix commit
20:16). Voi code cu, remove_holder('W-PILLFIX', None) xoa het key
cua agent W-PILLFIX; W-PILLFIX luc do chi co key tran nen ket qua
giong code moi. S2-flip la agent khac nen khong anh huong du code
nao. Buoc 0 an toan ca 2 phien ban.

## 7. Full suite

Worker bao: Ran 2316 tests in 217.173s, FAILED (failures=1, errors=2,
skipped=17); 2316 = 2313 baseline + 3 test moi; 3 loi giong het
baseline (g++ C++26 setUpClass, 2 test tesseract unavailable).
Redteam kiem chung doc lap:
- `grep -l "import overlay" tests/test_cursor_file.py tests/test_tc02_controller.py`
  tra ve rong (exit 1): ca 2 file loi deu khong import overlay,
  nen fix (chi dong overlay.py + test_overlay.py) khong the gay ra
  3 loi do. Chung la loi moi truong co san, khong phai regression.
- Targeted suite chay lai doc lap: Ran 22, OK.
- Redteam chay lai full suite doc lap (20:24-20:29 +07, 321s):
  FAILED (failures=1, errors=2, skipped=17), giong het worker.
  Loader dem 2340 test case, Ran 2316; chenh 24 do setUpClass error
  cua CursorFileTests (ca class khong chay rieng) + skip, khong phai
  test mat. 3 loi giong het baseline, file loi khong import overlay.
  Ket luan: 0 regression moi, 0 loi moi do fix.

## 8. Log thoi gian (Asia/Ho_Chi_Minh)

- 20:15:45: nhan task redteam tu Muse tong.
- 20:16: doc amend log + diff 5a272ae/a355002 + overlay.py toan bo.
- 20:18: doc first_action.py caller + review redteam goc (R6/R7/R11)
  + grep caller hold() / chromium_cli / s2_flip / cdp.mjs.
- 20:20: kiem tra laptop chi doc (holders.json, daemon PID 115582,
  file overlay.py cu) qua ssh-laptop.sh.
- 20:21: viet /tmp/redteam_attack_overlay.py, chay: 10 PASS, 1 HOLE
  (A8); targeted suite Ran 22 OK.
- 20:22: race tien trinh A12 PASS; baseline worktree 8f600b9: dung
  3 test moi fail; grep xac nhan 2 file loi full suite khong import
  overlay; worktree da xoa.
- 20:24: chay lai full suite doc lap (321s, xong 20:29, giong het
  worker: failures=1, errors=2, skipped=17).
- 20:30: viet review, commit + push len todolist-push, verify
  ls-remote.
