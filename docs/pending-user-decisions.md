# Quyet dinh con no cua ong

Ngay: 21/11/2026. Danh sach nay chi gom nhung viec chi ong moi quyet duoc, khong agent nao
tu quyet thay duoc. Moi muc ghi ro can ong lam gi.

## 1. Reboot laptop (mo khoa nhieu viec nhat)

Ong da noi mai day reboot sau. Sau khi reboot, chay duoc ngay:
- Test lai click Puppeteer BiDi (1.1.1), test firefox-mcp (1.1.2), Selenium tren Zen that (1.1.3)
- Test lai tren task that, do tong wall time truoc/sau (1.3.2)
- Verify co .desktop Zen + Chromium da co hieu luc tren fresh launch (1.3.3)
- Deploy pill blur tang len 0.15 va overlay luon bat vao ban cai dat (relay can khoi dong lai, chay sync-installed.py)
- Test nhap nhay overlay voi backdrop dong trong che do LIQUID (E2 phase B)

## 2. Bat lai computer-use + test animated backdrop (2.2.3)

Ong tat computer-use luc 19:13 ngay 20/11 vi overlay nhap nhay ngua mat. Ket qua do that
ngay 21/11: indicator da sua khong ve lai khi idle (0 lan ve trong 122 cua so 1 giay, 32/32
khung hinh pill giong het nhau). Can ong bat lai khi ong san sang. Luu y: nguyen nhan nhap
nhay ngay 20/11 o che do LIQUID van chua xac minh chac chan, chi moi loai tru duoc phia
indicator. Neu no tai phat, log E1 moi them se ghi lai duoc.

Rieng viec test backdrop dong (hyprglass): chi tiet 4 phuong an A/B/C/D kem rui ro tung
phuong an o docs/decision-2-2-3-hyprglass-test-20261121.md (Worker X, 21/11). Tom tat:
A = giao may 30 phut, load plugin vao compositor dang chay (biet chac chan, rui ro crash
phien); B = them vao hyprland.conf roi reboot (te nhat, co the khoa dang nhap); C = chay
Hyprland long nhau cach ly (0 rui ro, chua biet co chay duoc khong); D = bo qua tai hien,
giam sat bang log (0 rui ro, khong co ket luan chac chan). De xuat: thu C truoc, neu khong
duoc thi chon A hoac D. Ong chi can noi chu cai.

## 3. Chon pill candidate (4.5)

Candidate 2 (chai hinh tru) dang la default tam. Candidate 1 (ban Shayxo fix) van giu lai.
Ong la nguoi cham mui vi. Ben trong pill can co refraction, nhe hon o vien, khong thi trong
nhu kinh trong suot. Can ong tu test them roi chon.

## 4. H1-BASE recovery method

Phuong phap khoi phuc H1-BASE van chua co quyet dinh. Ghi trong todo list tu truoc, can ong
quyet chon cach nao.

## 5. Step 3 go/no-go

Thiet ke Step 3 stream da co (branch step3-stream-prep, commit 700144a) nhung e2e van
loanh quanh 10 giay, chua dat muc 8 giay exec / 10 giay e2e. Quyet dinh di tiep hay dung
van dang treo tu 18/11.

## 6. Save-dialog fix Part B

Phan B cua fix save-dialog van chua co quyet dinh.

## 7. Xoa ~/backups ~99 GiB

Thu muc backup tren laptop chiem khoang 99 GiB. Can ong xac nhan xoa truoc khi agent nao
dong vao.

## 8. Omarchy restore steps

Cac buoc khoi phuc Omarchy van chua co quyet dinh cuoi.

## 9. 3 tab Calibration Grid E2 tren Zen cua ong

Worker A2 de lai 3 tab test mo tren Zen cua ong (clean grid, broken-JS truth grid,
fixed-JS truth grid). Cac tab khac khong bi cham. Ong muon dong hay giu lai de xem?
