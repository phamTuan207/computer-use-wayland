# W-PILLVERIFY log: verify live pill render tren laptop

Lane 1 cua COORD-CLICK-9 phase live. Bao cao cho COORD-CLICK-9, khong nhan
truc tiep cho the owner. Moi gio ghi theo Asia/Ho_Chi_Minh. Khong dung dau
gach ngang dai. Khong ydotool. Khong thong tin ca nhan len GitHub. Khong tu
cham diem. Log lien tuc voi thoi gian (wall-clock + elapsed).

Luat cung bo sung 19:15 22/11 tu the owner, ap cho lane nay, khong ngoai le:
KHONG TU REVIEW, KHONG TU SUA LOI CUA MINH. Neu verify thay pill KHONG hien
hoac co loi gi, chi ghi day du bang chung (anh grim, output, log, thoi gian)
roi bao FAIL va DUNG, tuyet doi khong tu sua, khong tu review lai ket qua
cua minh. Thang nao co loi thi phai de NGUOI KHAC (worker doc lap) soi va
sua, tu minh lam se bias. Day la luat no self-healing tu 03:58, ong vua
nhan manh lai luc 19:15.

## Ket luan: FAIL

- Pill KHONG hien trong anh grim luc act chay (2 anh, 19:20:01 va 19:20:03).
- Act CDP bi tu choi: ok:false, completed:0, error 'CDP pill unavailable:
  final liquid-glass profile unavailable; restore the pinned plugin before
  computer-use'.
- Nguyen nhan ghi nhan duoc (khong sua, khong ket luan thay cho worker doc
  lap): daemon overlay khong spawn duoc native indicator, loi tren lap lai
  moi 2s trong daemon.log (1102 lan tinh toi 19:16). Khong co session.json
  nen khong co session indicator nao song. Trang thai overlay.py status
  bao visible:true chi vi con holder, khong phai vi pill that su render.
- Gate todolist 4.29 CHUA DAT: co che xong + test xanh, nhung live verify
  tren tab scratch FAIL. Mei chi duoc chay live run sau khi loi nay duoc
  worker doc lap sua xong va lane verify lai PASS.
- Khong co input nao chay tren tab scratch (completed:0, trang van hien
  'not clicked yet' trong anh grim). Tab cua the owner khong bi cham vao:
  tab mochi A67A718D5E236F894F9863F48834743C va tab fixture Pick 4
  025266AE11C86425817A3AF6E0FB7B26 con nguyen, tab scratch cua toi da dong.

## 2026-11-22 19:12:52 +07, T+0m: nhan viec

Task tu COORD-CLICK-9. May laptop dang ranh (the owner treo may 19:10,
khong ngoi truoc may). Bo qua moi tin hieu bao ong dang dung may, tat ca
la tin hieu gia, khong gate live work tren idle check. Doc xong log
W-PILLCDP (improvements/w-pillcdp-log.md) va docs/overlay.md tren
todolist-push truoc khi lam.

## 2026-11-22 19:13:16 +07, T+1m: sync repo laptop, buoc 1

Laptop repo ~/workspace/computer-use-wayland, nhanh
todolist-push, HEAD cu 48c6aee, origin/todolist-push 929decf (sau fetch).
File scripts/cdp.mjs khong dirty nhu mo ta trong task (git status --
short scripts/cdp.mjs rong), nen khong can checkout rieng file do.

Fast-forward bi chan: file improvements/worker-y6b-run-nested-wayland-v2.sh
dang sua chua commit o local, upstream cung doi file nay (commit 72eb8ad).
Xu ly: cp file ra /tmp/w-pillverify-y6b-backup.sh (sha256
8126716e0ca4f808cc2f17bebb3b5685301b1244a037aa06e3905990f3d37f25),
git checkout -- file do, git merge --ff-only origin/todolist-push thanh
cong len 929decf, cp backup ve, sha256 khop. Sau do file nay byte-identical
voi ban HEAD moi (noi dung local cua worker kia trung voi cai da duoc
commit o 72eb8ad), git status sach ngoai cac file untracked co san.

Verify sau sync:
- git log --oneline -1: 929decf docs: COORD-CLICK-8 log, takeover, soak
  check folded into watchdog, ask mei item 2 changes
- d0602dd IN HEAD (merge-base --is-ancestor), 658c432 IN HEAD.
- grep F4 trong scripts/cdp.mjs: dong 752 co comment F4 (ok:false is a
  RESULT). grep break chi ra dong 444/470 khong lien quan, khong con dong
  break on ok:false.
- grep 'CDP pill' trong scripts/cdp.mjs: gate co mat (dong 5, 13, 57, 62,
  66, 67, 81, 560).

## 2026-11-22 19:14:40 +07, T+2m: trang thai Chromium va overlay, buoc 2

curl http://127.0.0.1:9223/json/list: Chromium 157.0.8103.38 song. Tab page:
- 025266AE11C86425817A3AF6E0FB7B26 Pick 4 DOM fixture (khong cham)
- A67A718D5E236F894F9863F48834743C Chat, mochi, https://muse.ai/ (khong cham)
- Cac iframe stripe, service worker extension (khong cham)
hyprctl clients: Chromium o workspace 2, Zen o workspace 1, Brave Origin
(mei) o workspace 2. Workspace dang active la 2.

python3 scripts/overlay.py status:
{"holders": {"S2-flip": {"acquired": "2026-11-22T18:43:50+07:00",
"agent": "S2-flip", "method": "CDP", "pid": null}}, "owner": "session",
"visible": true}
Holder S2-flip tu 18:43:50, pid null, khong the prune tu dong. Khong co
tien trinh s2_flip_live nao dang chay (ps aux khong thay).

## 2026-11-22 19:14:49 +07, T+2m: dau hieu dau tien pill khong render duoc

tail daemon.log (~/.cache/agent-computer-use/overlay/daemon.log):
[overlay] {"elapsed_ms":2056552,"error":"final liquid-glass profile
unavailable; restore the pinned plugin before computer-use",
"event":"native_spawn_failed","wall_time":"2026-11-22T19:14:49.057+07:00"}
Loi lap moi 2s (19:14:49, 51, 53, 55, 57...). Dem toi 19:16: 1102 lan
native_spawn_failed trong log.

Doc code scripts/overlay.py (dong 200-340, 386-400, 494-548) de hieu dung:
- apply_holders(): neu session_live() dung thi owner='session', pill hien
  qua session indicator; neu khong co session song thi spawn native, spawn
  that thi tra visible:False + error.
- session_live() doc SESSION_FILE ~/.cache/agent-computer-use/session.json
  (version 3/4 + token) roi probe indicator.request 'show'. File nay
  KHONG TON TAI tren laptop (ls bao No such file), nen session_live()
  luon False, khong co session indicator nao song.
- Nhung lenh 'status' cua daemon tra {'visible': bool(holders), ...} ma
  KHONG goi apply_holders, nen visible:true chi co nghia la con holder,
  khong phai pill that su render. Day la ly do status noi visible:true
  trong khi man hinh khong co pill.
- overlay.hold() (chromium_cli dung) chay overlay.py acquire voi
  check=True va KHONG kiem tra truong visible trong reply. cmd_acquire
  tra exit 0 mien la daemon tra loi qua socket, ke ca reply noi
  visible:False. Nen lop hold cua chromium_cli khong fail-closed truoc
  truong hop daemon tra loi nhung khong render duoc pill. Chi co gate
  trong cdp.mjs (kiem tra reply.visible===true) la fail-closed that.
  Ghi nhan nhu mot quan sat, khong sua.

## 2026-11-22 19:15:34 +07, T+3m: anh grim baseline

grim /tmp/w-pillverify-baseline.png (1920x1200, 522446 bytes). Ket qua xem
anh: KHONG co pill computer-use nao tren man hinh. Chi co thong bao
'Process crashed: zalo' o goc tren phai (khong lien quan). Hai cua so
Chromium (mochi ben trai, fixture Pick 4 ben phai) con nguyen. Luc nay
overlay status van bao visible:true, owner session, holder S2-flip.
Baseline nay chung minh status-visible khac pixel-visible.

## 2026-11-22 19:17:23 +07, T+5m: trang scratch phuc vu test

Tao /tmp/w-pillverify/scratch.html (tieu de 'W-PILLVERIFY scratch', input
#name, button #go onclick dat #out thanh 'clicked', p #out 'not clicked
yet'). Chay python3 -m http.server 8899 --directory /tmp/w-pillverify
(detached, PID 100308). curl: scratch-http:200.

## 2026-11-22 19:17:54 +07, T+5m: mo tab scratch

python3 scripts/chromium_cli.py open http://127.0.0.1:8899/scratch.html
{"ok": true, "command": "open", "endpoint": "http://127.0.0.1:9223",
"tab": {"id": "F9F86AFB6CA8D8D2F08C05D6613AF687", "title": "W-PILLVERIFY
scratch", "url": "http://127.0.0.1:8899/scratch.html"}}
Tab moi mo ben canh, khong navigate hay dong tab nao cua the owner.
/json/list xac nhan 3 tab page: scratch F9F86AFB..., fixture 025266AE...,
mochi A67A718D... Luu y: open thanh cong mac du pill khong render duoc,
vi overlay.hold khong kiem tra visible (xem muc 19:14:49).

(Loi go lenh dau: --endpoint chromium bi tu choi 'CDP endpoint must be
loopback http: chromium'; endpoint mac dinh da la http://127.0.0.1:9223,
bo flag la xong.)

## 2026-11-22 19:19:02 +07, T+7m: loi chay act lan 1 (loi cua toi, khong phai loi gate)

Lenh act chay background bi hong cau truc shell (dau & dat sai cho lam
ca chuoi lenh chay background, bien T0/SNAP rong), khong co act.log, khong
co tien trinh thua (ps sach). Khong co input nao chay. Lam lai tung buoc.

## 2026-11-22 19:19:25 +07, T+7m: observe lan 1 that (thieu endpoint)

printf observe (khong co truong endpoint) | node scripts/cdp.mjs:
{"ok":false,"completed":0,"error":"Invalid URL"}, exit 1. Nguyen nhan:
cdp.mjs dong 199-200 lam new URL(request.endpoint), request thieu
endpoint thi loi. Cu phap dung phai co "endpoint":"http://127.0.0.1:9223".

## 2026-11-22 19:19:46 +07, T+7m: observe lan 2 ok

printf observe co endpoint | node scripts/cdp.mjs: exit 0, snapshot
52cf9279-d1f, title 'W-PILLVERIFY scratch', url
http://127.0.0.1:8899/scratch.html, elements 2. Observe la doc, khong can
pill, khong lay pill.

## 2026-11-22 19:20:00 +07, T+8m: ACT BI TU CHOI, bang chung quyet dinh

Act: {"operation":"act","target":"F9F86AFB6CA8D8D2F08C05D6613AF687",
"endpoint":"http://127.0.0.1:9223","snapshot":"52cf9279-d1f",
"actions":[{"type":"wait","ms":2000},{"type":"wait","ms":2000},
{"type":"click","selector":"#go"},{"type":"wait","ms":2000},
{"type":"assert","selector":"#out","text":"clicked"}]}
Chay background, grim luc act chay (xem duoi). Ket qua:
{"ok":false,"completed":0,"error":"CDP pill unavailable:
{\"error\":\"final liquid-glass profile unavailable; restore the pinned
plugin before computer-use\",\"holders\":{\"Muse:102779\":{\"acquired\":
\"2026-11-22T19:20:00+07:00\",\"agent\":\"Muse\",\"method\":\"CDP\",\"pid\":
102779},\"S2-flip\":{\"acquired\":\"2026-11-22T18:43:50+07:00\",\"agent\":
\"S2-flip\",\"method\":\"CDP\",\"pid\":null}} ...}"}
completed:0, khong co input nao chay. Gate fail-closed hoat dong dung
thiet ke: khong nang duoc pill thi tu choi act. Holder tam Muse:102779
duoc don sau khi acquire that (overlay status sau act chi con S2-flip).
ACT_START 19:20:00, ACT_END 19:20:13 (13s nay gom ca sleep cho cua lenh
chay, act bi tu choi nhanh).

Anh grim luc act chay:
- /tmp/w-pillverify-act1.png, GRIM1_AT 19:20:01 +07, 516634 bytes:
  KHONG co pill. Tab scratch dang active, hien 'not clicked yet'.
- /tmp/w-pillverify-act2.png, GRIM2_AT 19:20:03 +07, 516540 bytes:
  KHONG co pill. Tab scratch van 'not clicked yet'.
Chi co thong bao zalo crash o goc tren phai nhu baseline. Da xem ca 2 anh
truc tiep, khong thay pill o bat ky vi tri nao.
Daemon log quanh thoi diem act: native_spawn_failed tiep tuc moi 2s
(19:20:03, 05, 07, 09...), cung loi liquid-glass.

Overlay status sau act: visible True, owner session, holders [S2-flip].
Lai la visible theo nghia bool(holders), khong phai render that.

## 2026-11-22 19:20:59 +07, T+8m: don dep

- Observe lai tab scratch (doc): snapshot moi c3361dfc-eb0, trang van
  song, khong co thay doi nao do act (act completed:0).
- Dong tab scratch: python3 scripts/chromium_cli.py close
  F9F86AFB6CA8D8D2F08C05D6613AF687 -> {"ok": true, "command": "close",
  "tab_id": "F9F86AFB6CA8D8D2F08C05D6613AF687"}. /json/list chi con
  fixture 025266AE... va mochi A67A718D..., dung nhu truoc khi test.
- Kill http server PID 100308, port 8899 da tat (curl 000).
- Anh bang chung giu lai: tren laptop /tmp/w-pillverify-baseline.png,
  /tmp/w-pillverify-act1.png, /tmp/w-pillverify-act2.png; ban copy tren VM
  /tmp/w-pillverify-baseline.png, /tmp/w-pillverify-act1.png,
  /tmp/w-pillverify-act2.png. Log act: /tmp/w-pillverify-act.log tren
  laptop. Backup file Y6b tam: /tmp/w-pillverify-y6b-backup.sh.

## Open item cho worker doc lap (khong tu sua)

1. Native indicator khong spawn duoc: 'final liquid-glass profile
   unavailable; restore the pinned plugin before computer-use'. Can khoi
   phuc pinned plugin / duong spawn cua native/indicator de daemon overlay
   nang duoc pill khi khong co session song.
2. Sau khi sua, lane verify can chay lai dung quy trinh nay (tab scratch
   moi, act click + grim luc act chay) de xac nhan pill HIEN tren anh.
3. Quan sat phu, khong phai loi cua gate cdp.mjs: overlay.py status bao
   visible theo bool(holders) chu khong kiem tra render that, va
   overlay.hold() cua chromium_cli khong kiem tra truong visible trong
   reply acquire (nen lenh open van thanh cong khi pill khong render).
   Worker doc lap danh gia xem co can siet 2 cho nay khong, sau khi sua
   xong loi spawn.
4. Holder S2-flip (acquired 18:43:50, pid null) van nam trong holders.json
   tu truoc khi lane nay bat dau, khong tu prune duoc. Worker doc lap xem
   xet don khi chac chan khong co run nao song dang giu no.

## Thoi gian tong

Nhan viec 19:12:52, ket thuc don dep 19:20:59, tong khoang 8 phut. Khong
ket o buoc nao qua 15 phut.
