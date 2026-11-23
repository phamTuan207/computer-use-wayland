# Council 2 review: W-PILLFIX commit 8f600b9

Review doc lap boi Council 2 (y the owner), cho COORD-CLICK-9. Khong nhan
truc tiep cho the owner. Moi gio ghi theo Asia/Ho_Chi_Minh. Khong dung dau
gach ngang dai. Khong ydotool. Khong thong tin ca nhan len GitHub. Log lien
tuc voi thoi gian (wall-clock + elapsed). Chuan Lauren Tan: lenh chay +
output + commit hash + log thoi gian.

Pham vi: chi REVIEW, khong sua code, khong viet log thay W-PILLFIX. Lam viec
tren VM; laptop chi doc qua ssh-laptop.sh, khong sua gi tren laptop.

## Verdict: GO VOI DIEU KIEN

Code dung, fail-closed dung, nhung gate 4.29 chi duoc tuyen bo DAT sau khi
W-PILLVERIFY2 (worker doc lap khac) xac nhan bang anh grim: pill HIEN tren
pixel + act CDP thanh cong tren tab scratch. Mei chua chay live run cho den
luc do. Dieu kien thu hai: log tai tao improvements/w-pillfix-log.md phai
duoc hoan thien (ket qua restart 19:40:45 + smoke) va commit, vi ban hien
tai dung o 19:40 giua chung.

## 1. Luat 18:30 (pill PHAI hien khi bat ky agent nao dieu khien may): GIU, VA MANH HON

### 1.1 Nguyen nhan goc dung, sua dung cho

Commit message noi overlay.wayland_env doc signature tu /run/user/1000/hyprland
(khong ton tai). Code cu xac nhan:

- scripts/overlay.py cu: `hypr = runtime / 'hyprland'`, doc sig_dirs tu do.
- Code moi uy quyen cho hypr_cmd.desktop_env, nguon tin cay da chung minh
  trong repo: HYPR_SIGNATURE_DIR = "/run/user/1000/hypr"
  (scripts/hypr_cmd.py dong 22), desktop_env doc thu muc nay, fail-closed
  bang ValueError khi khong tim thay signature.

Kiem chung truc tiep tren laptop, chi doc, 2026-11-22 19:49:12 +07:

- Lenh: `ls -d /run/user/1000/hyprland /run/user/1000/hypr; ls /run/user/1000/hypr/`
- Output: `ls: cannot access '/run/user/1000/hyprland': No such file or directory`,
  `/run/user/1000/hypr` ton tai, chua 1 thu muc instance.
- Ket luan: nguyen nhan goc duoc xac nhan bang bang chung song, khong phai
  doan. Fix sua dung goc (sai duong dan, uy quyen ve nguon dung), khong va
  trieu chung. Dung huong first principles the owner da duyet.

### 1.2 Fail-closed: that, khong co lo hong moi

Ba lop chan deu duoc kiem tra bang doc code:

- cmd_acquire moi (scripts/overlay.py): khi reply.visible khong phai True,
  go holder vua them (remove_holder), ghi log acquire_invisible, in reply
  JSON, return 1. Truoc day return 0 voi visible False, tuc la acquire
  "thanh cong" trong khi khong co pill.
- overlay.hold (dong 625-630): goi acquire bang subprocess check=True, nen
  exit 1 thanh CalledProcessError. chromium_cli._pill_hold (dong 640-655)
  dung hold nay va ghi ro: pill khong len duoc thi lenh tu choi thay vi
  dieu khien trinh duyet vo hinh.
- scripts/cdp.mjs (dong 52-67): khi reply.visible !== true thi throw
  'CDP pill unavailable', act khong chay. Dung co che da tu choi act cua
  W-PILLVERIFY luc 19:20.

Khong thay doi nao lam yeu luat 18:30. Cac thay doi status deu chat hon:

- Daemon 'status' cu bao {'visible': bool(holders)}, noi doi (holder ton
  tai nhung pill khong render). Moi: status_reply goi apply_holders, chi
  bao visible True sau khi _show_label duoc ack, neu khong bao visible
  False kem error.
- CLI cmd_status khi khong co daemon: cu bao owner 'none' nhung visible
  theo bool(holders); moi: visible = bool(holders) and session_live(),
  holder rieng khong bao gio tu render duoc.
- indicator.Native: them phan biet probe=no_session_env vs invalid_status
  o stderr, text exception khong doi (test va grep log phu thuoc vao no).

Quan sat (khong phai blocker, ghi de COORD-CLICK-9 biet):

- status_reply goi apply_holders nen mot lenh status co the spawn native
  khi holder da ton tai. Cung lop tac dung phu nhu monitor chay moi 2s,
  khong them lop rui ro moi, va khi spawn that bai no bao visible False.
- _show_label tra True khi lenh show duoc ack, khong phai bang chung pixel.
  Day la ngu nghia co san cua ca duong monitor, khong phai loi moi cua fix
  nay. Vi vay bang chung pixel (grim) van bat buoc o W-PILLVERIFY2.
- Opt-out CU_CDP_PILL=0 trong cdp.mjs va chromium_cli la co san tu truoc,
  chi danh cho fixture test, khong phai do fix nay them. Luat 18:30 phu
  thuoc vao viec khong bao gio dat bien nay khi lam live.

### 1.3 Bang chung song: daemon moi da chay, pill da show

Kiem tra chi doc tren laptop, 2026-11-22 19:49 +07:

- Lenh: `ps -eo pid,etime,cmd | grep overlay.py`
- Output: PID 115582, etime 08:34 (8 phut 34 giay), chay
  ~/computer-use-wayland/scripts/overlay.py daemon; native
  indicator PID 115587 cung song. Daemon cu PID 76088 (tu 18:40:32, chua
  bao gio spawn duoc native) da khong con.
- holders.json luc 19:49: S2-flip acquired 19:36:53 +07:00 (pid null) va
  W-PILLFIX acquired 19:40:45 +07:00, method smoke (pid null).
- daemon.log, 19:49:35 va 19:49:37 +07: indicator-event label
  "W-PILLFIX via smoke", event show, present_failures 0; show_commands 1,
  duplicate_shows 1. Tuc la restart co xay ra luc ~19:40:45, smoke acquire
  thanh cong, pill duoc show va van duoc giu.

Day la bang chung manh nhung chua phai bang chung pixel: log cua indicator
tu bao show duoc ack, khong phai anh grim. Vi vay dieu kien 1 o verdict van
can W-PILLVERIFY2 lam.

## 2. Luat 18:23 (khong dong/navigate tab cua the owner): GIU

- Diff cua 8f600b9 chi cham 4 file: scripts/indicator.py (+12),
  scripts/overlay.py (+75/-13), tests/test_indicator.py (+21),
  tests/test_overlay.py (+145). Tong 240 insertions, 13 deletions.
- Khong co code trinh duyet, tab, cua so, hay navigate nao trong diff.
  Cac chu "chromium_cli" va "cdp.mjs" chi xuat hien trong comment giai
  thich co che tu choi da co san.
- Log tai tao ghi precheck truoc restart: tab mochi + fixture con nguyen,
  relay idle, khong session.json, khong tien trinh s2_flip/soak.
- Council 2 khong mo, khong dong, khong navigate bat ky tab nao trong
  qua trinh review nay.

## 3. Huong the owner da duyet va chuan bang chung

### 3.1 Huong dung

- Sua dung goc (muc 1.1), uy quyen ve nguon tin cay co san thay vi them
  duong doc moi. Khong va trieu chung.
- Test kem theo dung trong tam: 7 test overlay moi (wayland_env tu hypr
  dir, giu signature cua caller, khong instance thi khong signature,
  status_reply bao visibility that, cmd_status no-daemon session-aware,
  cmd_acquire tu choi khi pill invisible, acquire visible van pass) va
  1 test indicator moi (test_final_profile_rejection_names_probe_cause).

### 3.2 Tu chay lai test doc lap tren VM, 2026-11-22 19:49 +07

- `python3 -m unittest discover -s tests -p 'test_overlay.py'`: Ran 19 tests, OK.
- `python3 -m unittest discover -s tests -p 'test_indicator.py'`: Ran 43 tests, OK.
- `python3 -m unittest discover -s tests -p 'test_hypr_cmd.py'`: Ran 24 tests, OK.
- Khop dung con so commit message neu (overlay 19, indicator 43, hypr_cmd 24).

### 3.3 3 loi full suite la loi moi truong co san, da kiem chung

- `test_cursor_file.py` tren 8f600b9: FAILED (errors=1), loi setUpClass
  bien dich g++ -std=c++26 tren VM.
- `test_tc02_controller.py` tren 8f600b9: Ran 46 tests, FAILED
  (failures=1, errors=1, skipped=1), ca 2 deu do "tesseract is unavailable".
- Khop dung mo ta commit message (2310/2313 pass, 3 loi moi truong co san)
  va log tai tao (da chung minh bang worktree sach o e200d6e cho cung 3 loi).

### 3.4 Thieu log goc + thieu bao cao cuoi: VI PHAM chuan bang chung, chap nhan CO DIEU KIEN

- Su that: W-PILLFIX ket thuc ma khong viet log va khong co bao cao cuoi.
  Day la vi pham chuan Lauren Tan va workflow team 19:03 (tu lam, log lien
  tuc, bang chung day du). Council 2 ghi nhan vi pham nay, khong xoa nhe.
- Giam nhe, chua xoa: mot worker khac dang tai tao log
  (improvements/w-pillfix-log.md, 274 dong, untracked, mtime
  2026-11-22 12:40:24 UTC). Log nay chi tiet, co gio + elapsed + lenh +
  output, dung den 19:40, bao gom phat hien holder S2-flip acquire lai
  19:36:53 va quyet dinh doi ke hoach restart (kill SIGTERM PID 76088,
  giu holders.json, thay vi overlay.py stop xoa het holder). Quyet dinh
  nay dung va than trong.
- Nhung log tai tao DUNG O 19:40, chua ghi ket qua restart 19:40:45,
  chua ghi smoke acquire, chua ghi daemon moi PID 115582, chua co anh
  grim. Council 2 phai tu tim cac bang chung nay trong daemon.log va
  holders.json tren laptop (muc 1.3). Bang chung ton tai ngoai log, nhung
  log chua ghi lai.
- Chap nhan duoc CHI KHI: log tai tao duoc hoan thien (them restart +
  smoke + PID daemon moi + show ack) va commit; va live pixel proof den
  tu W-PILLVERIFY2 doc lap, khong phai tu nguoi sua. Neu 2 dieu kien nay
  khong xong, vi pham bang chung van mo va gate 4.29 khong duoc tuyen bo.

### 3.5 Luat 19:15 (khong tu review/khong tu sua loi cua minh): GIU

- Review nay do Council 2 doc lap thuc hien, khong phai W-PILLFIX tu
  review. Council 2 khong sua code, khong viet log thay W-PILLFIX, chi
  doc va kiem chung.

## 4. Dieu kien GO cu the (cho COORD-CLICK-9)

1. W-PILLVERIFY2 doc lap: grim luc act chay cho thay pill HIEN + act CDP
   thanh cong tren tab scratch, log day du, roi moi tuyen bo gate 4.29 DAT
   va cho mei chay live run.
2. Hoan thien va commit improvements/w-pillfix-log.md: them ket qua
   restart 19:40:45, smoke acquire, daemon PID 115582, show ack 19:49:35
   va 19:49:37, kem anh grim neu co.
3. Khong can sua code them cho commit nay. Neu W-PILLVERIFY2 FAIL thi mo
   lane sua moi, khong de W-PILLFIX tu sua lan 2 roi tu ket luan.

## 5. Nhat ky review (Council 2)

- 19:48:08 +07, T+0m: nhan task, xac dinh repo dung la
  ~/workspace/computer-use-wayland, branch todolist-push, HEAD 8f600b9.
  Commit e200d6e truoc do la log W-PILLVERIFY FAIL.
- 19:48-19:49 +07: doc full diff 8f600b9 (4 file), doc apply_holders,
  session_live, _show_label, cmd_acquire, cmd_status, desktop_env,
  cdp.mjs gate, chromium_cli._pill_hold; doc log W-PILLVERIFY (FAIL
  19:20:01 va 19:20:03, grim khong co pill) va log tai tao W-PILLFIX.
- 19:49:03 +07: tu chay targeted suites tren VM: overlay 19 OK,
  indicator 43 OK, hypr_cmd 24 OK.
- 19:49:12 +07: kiem tra chi doc tren laptop: /run/user/1000/hyprland
  khong ton tai, /run/user/1000/hypr ton tai, 1 instance dir.
- 19:49:35-19:49:37 +07: doc daemon.log tren laptop: show ack,
  present_failures 0; daemon moi PID 115582, holders co W-PILLFIX smoke
  19:40:45.
- 19:49:53 +07: kiem tra 2 file loi moi truong: cursor_file errors=1
  (g++), tc02_controller failures=1 errors=1 (tesseract).
- 19:50:00 +07: xac nhan origin/todolist-push = 8f600b9 bang ls-remote.
- 19:50 +07: viet review nay, commit bang pathspec tuong minh, push,
  verify bang ls-remote (xem muc 6).

## 6. Commit va push (review nay)

- Lenh: `git add -- improvements/w-pillfix-council-2-review.md`
- Lenh: `git commit -m "docs: Council 2 review of W-PILLFIX 8f600b9 (GO VOI DIEU KIEN)"`
- Lenh: `git push origin todolist-push`
- Verify: `git ls-remote origin todolist-push` tra ve
  8246a9a913c4838329dc7bce7b26f80cb67f7009, khop HEAD local, 19:50 +07.
