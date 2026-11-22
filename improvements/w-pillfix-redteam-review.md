# W-PILLFIX redteam review: fix pill commit 8f600b9

Lane redteam doc lap cua COORD-CLICK-9 phase live. Bao cao cho COORD-CLICK-9, khong nhan truc tiep cho Pham Tuan. Moi gio ghi theo Asia/Ho_Chi_Minh. Khong dung dau gach ngang dai. Khong ydotool. Khong thong tin ca nhan len GitHub. Khong tu cham diem. Log lien tuc voi thoi gian (wall-clock + elapsed). Chuan Lauren Tan: lenh chay + output + commit hash + log thoi gian.

Pham vi: chi TAN CONG + REVIEW commit 8f600b9 (`W-PILLFIX: restore standalone pill spawn, fail-closed status and acquire`, tren todolist-push). Khong sua code, khong viet log thay W-PILLFIX. Lam viec tren VM; laptop chi doc qua ssh-laptop.sh, khong sua gi tren laptop.

## Verdict: AMEND

Fix chua dung benh live cua su co 19:20 (daemon moi spawn duoc native tu 19:40:45, 0 loi spawn tu do), nen khong revert. Nhung fix chua duoc chap nhan nguyen ven: co 1 lo hong moi do chinh commit nay sinh ra (R7, muc 2), 2 lo chua nguyen nhan goc (R1, R4, muc 1), va test khong bao phu cac lo do (muc 3). Gate todolist 4.29 da duoc W-PILLVERIFY2 PASS doc lap bang grim (9ac4dcd, 19:53, xem muc 0), nen phan live-render cua gate da xong; AMEND o day nghia la: giu fix dang chay, sua cac amend muc 4 truoc khi coi fix la hoan tat, khong phai chay lai verify render.

Ly do khong phai BLOCK: benh live da khoi. Revert se lam pill chet lai ngay. Ly do khong phai GO: R7 co the lam mat pill giua chung cua mot run dang chay, va R1/R4 co the dua loi cu tro lai ngay sau mot lan Hyprland restart hoac mot entry rac trong thu muc signature.

Ghi chu doc lap: cac repro o muc 1 va 2 do redteam nay chay luc 19:50:25-19:50:37, truoc khi doc cac review Council 1/2/3 (doc luc 19:59:20). Ket qua hoi tu voi Council 3 (cung tim ra R1, R4, R6) va voi dieu kien cua Council 1/2 (GO VOI DIEU KIEN). Hoi tu nay duoc ghi nhan, khong phai sao chep: bang chung cua redteam la lenh chay rieng, co log thoi gian rieng o muc 5.

## 0. Cai gi da duoc kiem chung la DUNG (ghi nhan cong bang)

- Nguyen nhan goc duoc W-PILLFIX neu la co that: `overlay.wayland_env` cu doc `/run/user/1000/hyprland`, thu muc nay khong ton tai tren laptop (ssh 19:50:45: `ls: cannot access '/run/user/1000/hyprland': No such file or directory`), trong khi signature that nam o `/run/user/1000/hypr/11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795342782_301493614`.
- Fix hoat dong live: daemon cu PID 76088 chet, daemon moi PID 115582 start 19:40:45.465, `native_spawned` luc 19:40:45.659 (elapsed 206ms), loi `native_spawn_failed` cuoi cung luc 19:40:29.376 (daemon cu), 0 loi tu khi daemon moi chay. Daemon chay tu `/home/james/computer-use-wayland/scripts/overlay.py`, sha256 `b551cf6b2e1503824c690f46dae5ce88c90dfca6cf0f0761699e808717be59b4` khop log W-PILLFIX; indicator sha256 `4008141bc28ca1b6ba2865ef6a05eb8a4d837c3ca7675f5daa2e06d05e3a43ac` cung khop.
- Targeted suites chay lai tren VM 19:50:19: `test_overlay.py` 19 tests OK, `test_indicator.py` 43 tests OK, `test_hypr_cmd.py` 24 tests OK. Full suite dang chay nen luc viet bao cao, ket qua o muc 5.
- Huong fail-closed la dung: `cmd_acquire` tra 1 khi visible False, `cdp.mjs` `runOverlayCli` reject tren exit non-zero nen act bi tu choi, `chromium_cli._pill_hold` dung `overlay.hold` voi `check=True` nen raise. Huong nay khong bi tan cong do.
- Cap nhat 19:59: W-PILLVERIFY2 (9ac4dcd) PASS doc lap: pill HIEN trong 2 anh grim luc act chay (19:50:31 va 19:50:33), label "Muse via CDP", act ok:true, completed 5, assert #out "clicked" pass, gate 4.29 DAT. Crop phong dai xac nhan pill la lop layer-shell vat qua ranh 2 cua so Chromium, khong phai tab trinh duyet. Day la bang chung pixel ma W-PILLFIX thieu.
- Cap nhat 19:59: closeout 394a989 da hoan thien log W-PILLFIX sau su viec (gi nguyen 274 dong goc, them duoi restart 19:40:45, smoke show ack, test evidence). Tien de "W-PILLFIX ket thuc ma khong viet log" chi dung o thoi diem worker dung viec, khong con dung sau closeout.

## 1. Tan cong nguyen nhan: loi khong chi do duong /run/user/1000/hyprland

Claim cua commit: loi `final liquid-glass profile unavailable` chi vi thieu signature. Sai o muc lop loi: `_status` tra None hoac `_valid_liquid` tra False voi NHIEU nguyen nhan, tat ca deu do vao cung mot dong exception text. Fix chi chua 1 nguyen nhan trong so do.

### R1 (nang, da chung minh live): signature cu do caller truyen duoc giu nguyen, khong bao gio validate lai

Code `scripts/overlay.py`, `wayland_env` dong 207-211: neu env co `HYPRLAND_INSTANCE_SIGNATURE` thi tra ve nguyen, chi setdefault `WAYLAND_DISPLAY`. Test `test_wayland_env_keeps_caller_signature` con ca ngoi hanh vi nay. Nhung signature co the da chet: Hyprland restart doi signature, daemon cu van giu signature cu trong env cua no, moi lan `_spawn_native` goi `wayland_env()` deu di nhanh early-return va that bai mai, monitor retry moi 2s vo ich cho den khi daemon bi restart bang tay.

Chung minh live tren laptop, 19:51:39:

```
$ env -i PATH=/usr/bin:/bin HOME=/home/james XDG_RUNTIME_DIR=/run/user/1000 HYPRLAND_INSTANCE_SIGNATURE=deadbeef-stale WAYLAND_DISPLAY=wayland-1 hyprctl -j hyprglass status
Couldn't connect to /run/user/1000/hypr/deadbeef-stale/.socket.sock. (4)
```

`hyprctl` tra non-zero nen `indicator._status` tra None (dong 197-206 `indicator.py`), `liquid` False, cung loi cu xuat hien. Chung minh tren VM, 19:50:25:

```
R1 stale SIG kept: stale-dead-sig-123
R1 _status(stale env): None | liquid: False
```

Kich ban fix nay van fail: Hyprland restart (crash, update) trong khi daemon song. Luc do khong co cach nao tu phuc hoi, vi duong duy nhat lay signature moi (`desktop_env`) chi chay khi env KHONG co signature.

### R2 (nang, da chung minh): cac nguyen nhan khac cung cho ra cung loi, fix khong chua

`indicator._valid_liquid` doi version dung `1.1.1-cu.1`, `versionCheck` dung `match`, `active` True, `layers.enabled` True, `layers.active` True, `layers.reason` None. Bat ky dieu nao lech deu cho cung exception text `restore the pinned plugin before computer-use`, trong khi plugin khong he mat.

Chung minh tren VM, 19:50:25 (dung status dict hop le roi sua 1 truong):

```
R2 valid(good): True | valid(version bumped): False
R2 valid(layers inactive): False
```

Kich ban fix nay van fail: hyprglass nang cap len 1.1.2 (versionCheck mismatch), hoac layers tam inactive sau mot lan Hyprland reload. Loi tra ve van bao `restore the pinned plugin`, dan duong chan doan sai nhu lan truoc.

### R3 (trung binh, da chung minh live): PATH khong co hyprctl cung cho ra cung loi

`indicator._status` goi `hyprctl` bang ten, khong duong dan tuyet doi. Neu PATH cua caller khong co `/usr/bin`, `subprocess.run` raise `OSError`, `_status` tra None, cung loi cu.

Chung minh live tren laptop, 19:52:06 (`which hyprctl` tra `/usr/bin/hyprctl`):

```
status PATH=/tmp/empty: None
```

Chu y: truong hop PATH thieu hoan toan thi Python dung default path nen van tim duoc hyprctl; chi khi PATH duoc set tuong minh ma khong co `/usr/bin` moi fail. Cron hoac SSH env toi gian la noi hay gap kieu PATH nay. Fix khong dong den PATH.

### R4 (trung binh, da chung minh tren VM): desktop_env chon sai instance khi co nhieu entry, va chon ca file thuong

`scripts/hypr_cmd.py`, `desktop_env` dong 196-204: `names = sorted(os.listdir(signature_dir))`, lay `names[0]`, KHONG loc `is_dir`. Code cu cua `wayland_env` co loc (`[d for d in hypr.iterdir() if d.is_dir()]`); uy thac sang `desktop_env` lam mat bo loc nay. Day la regression nho so voi code cu.

Chung minh tren VM, 19:50:30:

```
R4 desktop_env picks: {'XDG_RUNTIME_DIR': '/run/user/1000', 'WAYLAND_DISPLAY': 'wayland-1', 'HYPRLAND_INSTANCE_SIGNATURE': 'aaa-junk-file'}
R4 old-code filter would pick: ['zzz_real-sig_1_2']
R5 desktop_env picks: aaa_stale-sig_9_9
```

Kich ban fix nay van fail: thu muc `hypr/` co them 1 file rac (lock, socket, log) co ten sort truoc, hoac 1 instance cu con sot lai sau crash co ten sort truoc. Luc do signature tim duoc la rac, `_status` None, cung loi cu. Hien tai tren laptop chi co 1 entry (kiem tra 19:50:45) nen lo nay dang latent, chua live. Council truoc khi sua cua W-PILLFIX da neu diem nay (redteam 1) va chap nhan bo qua; redteam nay khong dong y bo qua, vi chi can 1 entry rac la benh tai phat ma khong co ai bao truoc.

### R5 (nhe, da kiem tra va LOAI TRU): nhanh early-return thieu XDG_RUNTIME_DIR

`wayland_env` nhanh 1 (ca SIG va WAYLAND deu co) tra env nguyen, khong setdefault `XDG_RUNTIME_DIR` nhu code cu van lam. Da kiem tra live tren laptop 19:51:39: `hyprctl -j hyprglass status` voi SIG dung van tra status hop le ca khi khong co `XDG_RUNTIME_DIR` (hyprctl tu fallback ve `/run/user/1000`). Lo nay KHONG tai hien, ghi nhan la da kiem tra chu khong phai lo hong.

### Ket luan muc 1

Nguyen nhan goc cua su co 19:20 la dung, nhung fix chi chua truong hop `khong co signature`. No khong chua signature cu, signature rac, PATH thieu hyprctl, version lech, layers inactive. Moi truong hop do deu hien cung mot loi, va log W-PILLFIX khong co co che nao phan biet chung sau khi fix, ngoai metric probe o muc 2.

## 2. Tan cong fail-closed moi: van co duong act chay ma khong co pill

### R6 (nang, lo moi do chinh commit nay sinh ra): acquire that bai voi pid=None xoa holder cua run khac dang song

`cmd_acquire` khi reply visible False se goi `remove_holder(args.agent, args.pid)` (dong 553-556 `overlay.py`). Khi `args.pid` la None, `remove_holder` xoa TAT CA entry cua agent do (dong 130-138: nhanh `else` xoa moi key bang agent hoac bat dau bang `agent + ':'`). Vay mot acquire that bai se xoa holder cua mot run cung agent khac dang song, lam mat pill giua chung cua run do, va run do khong he biet.

Chung minh tren VM bang ham that, 19:50:37 (mock chi o lop socket, giong test cua chinh fix):

```
R7 cmd_acquire rc: 1 | holders after: {}
```

Truoc lenh do holders co `Muse:999001` (mot run khac, pid 999001). Sau lenh acquire that bai voi pid=None, holders rong. Chi rieng dong xoa nay da xoa holder cua run khac.

Duong chay that bi anh huong, khong phai ly thuyet:

- `overlay.hold()` (dong 642-649) goi `acquire --agent --method` KHONG truyen `--pid`. `chromium_cli._pill_hold` dung `hold("Muse", "CDP")`, nen moi lenh `open`/`activate`/`close` cua chromium_cli deu di duong pid=None.
- `s2_flip_live.py`, `pill_acquire_cmd` (dong 596-600) cung goi `acquire --agent --method` KHONG truyen `--pid`.
- Chi `cdp.mjs` truyen `--pid` (dong 65). Vay 2 trong 3 caller chinh di duong pid=None.

Hau qua cu the: mot lenh `chromium_cli open` that bai pill (vi ly do gi cung duoc) se xoa holder cua mot act CDP dang chay cua cung agent Muse, pill tat giua chung, act do chay tiep khong pill. Day la dung loai loi ma luat 18:30 cam. Test cua fix (`test_cmd_acquire_refuses_when_pill_invisible`) khong bat duoc vi no chi co 1 holder duy nhat trong tmp dir trong, khong co holder dong thoi nao de mat.

Cung lo o chieu nguoc: `cmd_acquire` duong exception (dong 531-546) cung goi `remove_holder(args.agent, args.pid)` voi pid=None, cung xoa het. Va `remove_holder` voi pid int cung xoa them key tran `agent` (dong 128-133), nen mot acquire that bai co pid cung xoa holder tran cua `overlay.hold`.

### R7 (trung binh, co san truoc fix, fix khong dong den): CU_CDP_PILL=0 tat ca 2 gate bang 1 bien moi truong

- `scripts/cdp.mjs` dong 25: `pillEnabled()` tra False khi `CU_CDP_PILL=='0'`; dong 52: `acquireCdpPill` tra False ngay, act chay tiep voi `pillHeld=false`, khong tu choi.
- `scripts/chromium_cli.py` dong 650: `_pill_hold` yield ngay khi `CU_CDP_PILL == "0"`.

Khong co log, khong co canh bao, khong co phan biet fixture voi live. Bat ky caller nao ke thua env co bien nay (SSH env, cron env, shell rc) deu lai xe ma khong co pill, trong khi commit message cua fix noi `fail-closed`. Day la lo co san, khong phai do fix sinh ra, nhung fix tu nhan fail-closed ma khong bit no thi claim do khong tron.

### R8 (trung binh): status_reply bao visible theo ack, khong phai theo pixel

`status_reply` goi `apply_holders`, `_show_label` tra True khi `native.command('show')` tra ack `visible` (dong 292-305 `overlay.py`, dong 118-130 `indicator.py`). Khong co buoc nao kiem tra pixel that su duoc ve. Grep `grim|pixel|screenshot` trong `scripts/overlay.py` va `scripts/indicator.py` chi ra 1 dong docstring trong `indicator.py` dong 258 tu thua nhan: `liquid_available` khong phai bang chung pixel nao duoc ve.

Bang chung live: daemon.log luc 19:50:53-19:50:59 cho thay `show` ack deu moi 2s (monitor loop), nhung cac cua so metric kem theo ghi `paint_callbacks: 0, surface_commits: 0`. Redteam KHONG ket luan pill khong ve tu 2 so nay (show lap lai la duplicate, khong can ve lai), chi ket luan: ack khong chung minh duoc pixel. Vi vay `status` moi van co the noi visible True trong khi man hinh khong co pill (vi du indicator window o workspace khac, output tat, layer bi che). Chi grim moi la ground truth, va W-PILLFIX khong co anh grim nao trong log cua no. Cap nhat 19:59: W-PILLVERIFY2 da bu dap dung cho nay bang 2 anh grim PASS (muc 0), nen R8 con lai o muc tinh chat cua `status`, khong con la thieu bang chung render cua su co nay.

### R9 (nhe): status gio la thao tac co side-effect va co the cham

Truoc fix, `status` chi doc holders. Sau fix, `status_reply` goi `apply_holders` duoi lock, co the spawn Native. `Native.__init__` co the block toi `ready_timeout` 3s + `LIQUID_READY_TIMEOUT` 30s (`indicator.py` dong 97-105) neu shader dang compile. Trong luc do vong serve cua daemon (don tuyen) bi chan, va `_ensure_daemon` poll `status` voi timeout 2s (dong 503-510 `overlay.py`) se timeout lien tuc. Council cua W-PILLFIX da neu diem nay (redteam 2) va chap nhan; redteam nay ghi nhan lai o muc nhe vi hanh vi that da do duoc live: spawn 19:40:45 chi mat 206ms, nen truong hop cham chi xay ra khi shader pending hoac spawn that. Van la thay doi ngu nghia cua mot lenh doc: `overlay.py status` gio co the nang pill, khong con la read-only.

### R10 (nhe, bang chung live): holder pid-null rac van ton tai sau deploy, fix khong don

Luc 19:50:52 tren laptop, `holders.json` co 2 entry, ca 2 deu pid null:

- `S2-flip`, acquired 2026-11-22T19:36:53+07:00 (holder ma W-PILLVERIFY thay luc 19:14 la 18:43:50, da duoc acquire lai 19:36:53 boi mot lane khong xac dinh).
- `W-PILLFIX`, method `smoke`, acquired 2026-11-22T19:40:45+07:00, pid null.

`prune_dead_holders` chi xoa pid int (dong 141-160 `overlay.py`), nen holder pid null khong bao gio tu het. Daemon PID 115582 van chay, pill van duoc giu boi 2 holder cua cac run da chet, ke ca holder smoke cua chinh W-PILLFIX. Day la benh S2-flip ma W-PILLFIX da mo ta, va chinh lan deploy cua no da de lai them 1 holder benh nhu vay. Khong phai lo bao mat, nhung no lam `status` noi visible True mai mai du khong con run nao song, va daemon khong bao gio idle-exit.

## 3. Tan cong test: test moi co bao phu loi goc khong

Ket luan: test moi bao phu dung truong hop don gian nhat cua loi goc (1 instance dir, khong signature), nhung khong bao phu cac lo o muc 1 va 2. Mot so test chi test mock, khong test day dan that.

### T1: test_wayland_env chi co 1 dir, khong co truong hop nhieu dir / file rac / signature cu

- `test_wayland_env_discovers_signature_from_hypr_dir`: tmp dir chi co 1 dir `deadbeef_1_2`. Khong test 2 dir (R4/R5), khong test file thuong trong `hypr/` (R4), khong test signature cu (R1).
- `test_wayland_env_keeps_caller_signature`: dung `keep-me` lam signature hop le gia dinh. Khong co test nao truyen signature cu va doi hoi re-discovery hoac that bai ro rang. Test nay that ra khoa chat hanh vi gay loi R1.
- `test_wayland_env_without_instance_returns_no_signature`: tmp dir khong co thu muc `hypr/` nao. Khong test `hypr/` rong (cung nhanh ValueError, nhung khong co test nao chung minh).

### T2: test_cmd_acquire mock socket nen khong test day dan that

`test_cmd_acquire_refuses_when_pill_invisible` va `test_cmd_acquire_visible_still_succeeds` deu mock `overlay._send_socket` tra ve dict viet tay. Chung khong chay qua daemon that, khong chay qua `status_reply`/`apply_holders` that, khong chay qua `_spawn_native` that. Neu daemon that tra reply thieu key `visible`, hoac `apply_holders` tra kieu khac, test van xanh. Dac biet, test invisible dung tmp dir trong, khong co holder dong thoi, nen khong the bat R6.

### T3: test_status_reply dung FakeNative khong giong Native that

`_FakeNative.command` tra `ok` ngay khi process song, `_FakeNativeFailing.command` raise ngay. Native that thi `command('show')` doi ack `visible` qua stdout pipe voi timeout 3s, va `__init__` co the raise `RuntimeError` tu `wait_for_profile` sau 30s. Fake khong mo phong duong raise luc spawn (duong gay loi 19:20), chi mo phong duong raise luc show. Vay test khong bao phu chinh xac loi goc: spawn that bai.

### T4: test probe cua indicator mock _status nen khong phan biet duoc 2 nhan

`test_final_profile_rejection_names_probe_cause` patch `indicator._status` tra None ca 2 case, roi assert nhan dua tren env. No khong kiem tra `_status` co that su duoc goi hay khong. Nhap nhang: voi env rong, `_status` that tra None ngay ma khong goi hyprctl; voi env du, `_status` that goi hyprctl roi moi tra None. Test mock lam 2 case giong het nhau o lop duoi, nen no chi test cong thuc nhan, khong test phan biet `probe never ran` vs `probe ran and failed` nhu docstring hua.

Them nua, nhan probe chi ghi ra stderr metric. Tren laptop, `grep -a -c "liquid_unavailable" ~/.cache/agent-computer-use/overlay/daemon.log` luc 19:51:55 tra 0. Metric moi chua bao gio chay live (vi tu khi deploy chua co lan spawn that bai nao). Vay phan diagnostic moi nay chi duoc chung minh bang unit test mock, chua co bang chung live nao.

### T5: claim full suite chua duoc redteam chay lai day du luc viet

W-PILLFIX bao full suite 2310/2313, 3 loi co san. Redteam chay lai targeted suites 19:50:19 (muc 0, deu OK). Full suite duoc chay lai nen luc 19:52:35, log o `/tmp/w-pillfix-redteam-fullsuite.log`, ket qua o muc 5 duoi day.

## 4. Amend bat buoc truoc khi chap nhan (thu tu uu tien)

1. R6 truoc tien: `cmd_acquire` khi that bai chi duoc xoa dung key vua them (`_holder_key(agent, pid)`), khong duoc goi `remove_holder(agent, None)` dang xoa het. Cung sua `overlay.hold()` va `s2_flip pill_acquire_cmd` truyen `--pid` that (pid cua tien trinh goi), de holder co key rieng va prune duoc. Them test: 1 holder dong thoi cua cung agent con song, acquire that bai voi pid=None thi holder kia van con.
2. R1: `wayland_env` phai validate signature: neu `_status` (hoac mot probe hyprctl nhe) that bai voi signature hien co thi bo signature va chay lai `desktop_env` de tim signature moi, thay vi giu signature chet. Them test: signature cu + 1 dir that thi tra ve signature that.
3. R4: `desktop_env` chi chon entry la dir (`is_dir`), va khi co nhieu dir thi uu tien instance dang song (probe duoc bang hyprctl hoac moi nhat theo mtime) thay vi `sorted()[0]`. Them test: file rac + 2 dir thi chon dir song.
4. R2/R3: tach nhan loi theo nguyen nhan that (thieu signature, hyprctl khong chay, version lech, layers inactive) thay vi dung chung 1 text `restore the pinned plugin`. It nhat, sua text hoac them truong `reason` vao log `native_spawn_failed` de lan sau khong chan doan sai. Them test `_valid_liquid` voi version bump va layers inactive (da co san R2 de dung lam test).
5. R7: hoac bo opt-out `CU_CDP_PILL=0` tren duong live (chi cho phep khi co them co bao fixture), hoac log warn ro rang moi lan no tat gate. Khong de 1 bien moi truong am tham tat luat 18:30.
6. R10: don holder smoke `W-PILLFIX` (pid null, 19:40:45) va xac minh lai `S2-flip` (19:36:53) bang tay truoc khi giao cho verify lane; ve lau dai, them co che het han hoac danh dau tuoi cho holder pid-null thay vi de song mai.
7. R8/R9: ghi ro trong docs rang `status`/`visible` la ack-truth, khong phai pixel-truth; gate 4.29 chi dat khi co anh grim. Ghi ro `status` gio co side-effect spawn.
8. W-PILLFIX chua co bao cao cuoi va chua co anh grim smoke: lane verify doc lap phai chay lai act CDP tren tab scratch va chup grim, khong dung ack lam bang chung dat gate. (Cap nhat 19:59: dieu nay da xay ra, W-PILLVERIFY2 PASS, xem muc 0. Amend 8 coi nhu xong nho verify2, khong can lam lai.)

## Open item ngoai pham vi fix (khong tinh vao verdict, ghi de lane chu so huu xu ly)

R11: `cdp.mjs` `releaseCdpPill` (dong 81) goi `overlay.py release --agent ... --method ... --pid ...`, nhung parser `release` cua `overlay.py` (dong 648-649) chi co `--agent` va `--pid`, khong co `--method`. Moi lan release deu loi `unrecognized arguments: --method CDP` (W-PILLVERIFY2 quan sat luc 19:50:37, stderr cua act). Holder chi het nho `prune_dead_holders` xoa pid da chet sau khi tien trinh cdp.mjs thoat, nen hau qua hien tai la nhe, nhung day la loi that o duong release, co san truoc 8f600b9 va 8f600b9 khong dong den. De lane W-PILLCDP sua, khong tinh vao verdict cua fix nay.

## 5. Log thoi gian (Asia/Ho_Chi_Minh)

- 19:48:19, T+0m: nhan viec, doc commit 8f600b9, diff 4 file, log W-PILLVERIFY (e200d6e) va log W-PILLFIX.
- 19:49:02, T+1m: doc `overlay.py`, `indicator.py`, `hypr_cmd.py` day du; grep caller `cdp.mjs`, `chromium_cli.py`, `first_action.py`, `s2_flip_live.py`.
- 19:50:19, T+2m: chay lai targeted suites tren VM: overlay 19 OK, indicator 43 OK, hypr_cmd 24 OK.
- 19:50:25, T+2m: repro R1/R2/R3 tren VM (stale SIG, version bump, layers inactive, PATH thieu hyprctl).
- 19:50:30, T+2m: repro R4/R5/R6 tren VM (file rac thang dir that, stale dir thang live dir, `remove_holder` pid=None xoa het).
- 19:50:37, T+2m: repro R7 tren VM (`cmd_acquire` that bai pid=None xoa holder `Muse:999001` cua run khac).
- 19:50:45, T+2m: ssh laptop (chi doc): `/run/user/1000/hypr/` chi co 1 dir `11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795342782_301493614`, `/run/user/1000/hyprland` khong ton tai.
- 19:50:52, T+2m: ssh laptop (chi doc): daemon cu PID 76088 da chet, daemon moi PID 115582 start 19:40:45, holders co `S2-flip` 19:36:53 va `W-PILLFIX` smoke 19:40:45, ca 2 pid null, khong co session.json.
- 19:50:59, T+2m: ssh laptop (chi doc): daemon.log `show` ack moi 2s, `native_spawn_failed` 1839 lan tong, `native_spawned` 314 lan tong, `liquid_unavailable` 0 lan.
- 19:51:11, T+3m: ssh laptop (chi doc): `native_spawn_failed` cuoi 19:40:29.376, `native_spawned` 19:40:45.659, daemon PID 115582 chay tu home checkout, sha256 overlay `b551cf6b...`, indicator `4008141b...` khop log W-PILLFIX.
- 19:51:39, T+3m: ssh laptop (chi doc): hyprctl voi SIG gia tra loi ket noi that bai; hyprctl voi SIG dung tra status hop le ca khi khong co `XDG_RUNTIME_DIR` (R5 bi loai tru).
- 19:51:55, T+3m: ssh laptop (chi doc): `_status` voi PATH khong co hyprctl tra None (xac nhan R3 live); `liquid_unavailable` trong daemon.log van 0.
- 19:52:06, T+4m: ssh laptop (chi doc): `which hyprctl` tra `/usr/bin/hyprctl`, `_status` voi PATH `/tmp/empty` tra None.
- 19:52:35, T+4m: bat dau chay lai full suite tren VM, log `/tmp/w-pillfix-redteam-fullsuite.log` (nen, PID 22422).

## 6. Full suite chay lai (bo sung sau khi chay xong)

- Chay lai tren VM 19:52:35-19:58:37 (272.8s), log `/tmp/w-pillfix-redteam-fullsuite.log`: `Ran 2313 tests, FAILED (failures=1, errors=2, skipped=17)`.
- 3 loi giong het claim cua W-PILLFIX va giong het baseline truoc fix: `ERROR setUpClass test_cursor_file.CursorFileTests` (g++ C++26), `ERROR + FAIL test_tc02_controller.Tc02MenuBarTests` (tesseract missing). Khong loi nao cham overlay/indicator.
- Ket luan: 2310/2313 pass, fix gay 0 regression o full suite. Phan nay cua claim W-PILLFIX la dung.
