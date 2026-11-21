# Quyet dinh 2.2.3: test animated backdrop (hyprglass) hay khong

Ngay: 21/11/2026. Nguoi viet: Worker X (danh gia doc lap).
Trang thai hien tai (da kiem chung lai 21/11 17:52):
- hyprglass KHONG duoc load (chi co hyprbars), KHONG co trong hyprland.conf.
- File .so chi con trong backup: /home/james/.local/share/agent-computer-use/backups/full-1791544423/native/hyprglass.so va backups/sync-20261116-230254-783160-a9a24690/trees/native/hyprglass.so (kem cac ban hash khac).
- Indicator da duoc chung minh KHONG ve lai khi idle 3 lan doc lap: 122 cua so 1 giay 0 callback, 3 phut 0 commit, ban binary da deploy 3 cua so 0. E1 logging (ghi log theo tung su kien) da san sang de bat bat ky lan tai phat nao.
- Chua co cach nao tai hien che do LIQUID + backdrop dong ma khong dong vao compositor dang chay.

## Chon 1 trong 4 phuong an (ong chi can noi chu cai)

### A. Cua so handover, load plugin vao compositor dang chay
- Lam gi: ong giao may ~30 phut, khong de app nao co viec chua luu. Muse load file hyprglass.so tu backup vao Hyprland dang chay (hyprctl plugin load), bat backdrop dong che do LIQUID, lai Zen do pill ve lai (grim + dem callback).
- Duoc gi: biet chac chan backdrop dong co phai nguyen nhan nhap nhay hay khong.
- Rui ro: load plugin co the lam Hyprland crash giua phien (chet Zen, Zalo, Teams, nhac, toan bo GUI). Khoi phuc bang cach dang nhap lai, viec chua luu se mat.
- Giam rui ro: chi lam khi khong co gi chua luu.

### B. Cau hinh load o luc dang nhap (them vao hyprland.conf roi reboot)
- Lam gi: them hyprglass vao danh sach plugin trong hyprland.conf, reboot/dang nhap lai voi plugin da load, chay test trong phien moi, xong thi xoa dong do.
- Duoc gi: cung ket qua nhu A, trong phien sach.
- Rui ro: neu plugin crash Hyprland ngay luc dang nhap, phien do hoa khong mo len duoc, ong phai sua hyprland.conf tu TTY (Ctrl+Alt+F2) moi dang nhap lai duoc. Can viet san lenh khoi phuc ra giay/dien thoai truoc.
- Danh gia: rui ro/lợi ích te nhat trong 4 phuong an (khoa dang nhap de lay cung thong tin nhu A).

### C. Compositor long nhau, cach ly (khong dong vao phien dang chay)
- Lam gi: chay mot Hyprland long nhau (nested) ben trong phien hien tai, hoac tren TTY rieng, voi hyprglass da load, test trong do.
- Duoc gi: tai hien ma KHONG co rui ro gi cho phien lam viec cua ong.
- Rui ro/kha thi: CHUA KIEM CHUNG duoc nested Hyprland + GPU + plugin co chay duoc khong. Neu khong chay thi mat thoi gian ma khong co ket qua. Can chay thu do kha thi truoc (~15 phut, khong rui ro).
- Danh gia: thu C truoc, neu khong duoc thi chon A hoac D.

### D. Bo qua tai hien, giam sat bang log (khong can ong lam gi)
- Lam gi: chap nhan bang chung hien co (indicator khong ve lai khi idle, 3 lan do doc lap deu 0; log E1 ghi lai bat ky lan tai phat nao kem thoi gian chinh xac). Dong I11 dang "khong tai hien duoc neu khong co plugin".
- Duoc gi: 0 rui ro, 0 thoi gian cua ong. Neu nhap nhay tai phat, log E1 cho biet chinh xac luc nao, dieu kien nao, de sua dung cho.
- Mat gi: khong co ket luan chac chan ve nguyen nhan vu 20/11. Neu nguyen nhan dung la backdrop, no van chua biet cho den khi tai phat.

## De xuat cua Worker X (khuyen nghi, ong quyet)
Thu C truoc (re, khong rui ro). Neu C khong chay duoc: chon A neu ong muon biet chac chan va chiu duoc rui ro crash phien, chon D neu ong khong muon mo may. Khong khuyen B.
