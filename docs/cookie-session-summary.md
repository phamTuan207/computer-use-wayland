# Giu phien Gmail song lau tren may VM: tom tat cho ong

Ngay trinh bay: 21/11/2026. Nguon day du: vm-gmail-sessions-research.md (nghien cuu 20/11/2026, 19 nguon).
Da kiem chung lai ngay 21/11: trang ho tro Google ve dang nhap nhieu tai khoan van con hieu luc, noi dung khop voi nghien cuu.
Cac quan sat tren VM la tu ngay 20/11.

## Ket luan ngan

Khong co cach nao giu phien Gmail "vinh vien" that su. Google co the thu hoi phien tu phia
server bat cu luc nao, du cookie tren may ong van con han. Nhung phien co the song hang thang
neu dung deu, va khi chet thi dang nhap lai bang 1 click qua account chooser, khong can go mat khau.

## Vi sao phien chet

- Cookie phien `SID` ghi han toi da 24 thang, nhung do chi la han cua cai cookie. Google van
  thu hoi duoc tu server ma khong can doi cookie het han.
- Refresh token chet khi: khong dung trong 6 thang lien tiep, doi mat khau, vuot 100 token
  cho moi tai khoan, hoac ong tu thu hoi quyen.
- Phien chet som khi: doi IP hoac thiet bi (IP datacenter/VPN hay bi Google danh dau la),
  khong hoat dong lau, trinh duyet xoa cookie, hoac dang xuat o noi khac.
- Account switcher chi nho danh sach tai khoan, khong giu phien song. Moi tai khoan co phien
  rieng va chet doc lap. Dung chuyen hom nay: [email redacted] chet, the other account van song.

## Cach tot nhat: ket hop 3 thu

1. Moi Gmail mot named profile rieng tren cloud browser. Tach bach tuyet doi, mot phien chet
   khong anh huong cac phien khac, khong bao gio mo nham tai khoan. Dang nhap mot lan qua
   Google account chooser, mat khau lay tu Secure Vault, ong duyet 1 lan.
2. Doc mail va lay link xac nhan/OTP bang Gmail connector (API), khong dung trinh duyet.
   Duong nay khong phu thuoc cookie trinh duyet, khong bao gio "het phien" kieu browser.
   Day la duong chinh nen dung.
3. Cron heartbeat nhe moi 3-4 ngay cham vao tung tai khoan, de phien khong chet vi khong hoat dong.

Ky vong dung: phien song nhieu tuan den nhieu thang neu dung deu va khong doi mat khau.
Khi mot phien chet, dang nhap lai bang account chooser (mat khau da luu trong Vault).

## Khong nen lam

Copy cookie tu laptop (Zen) sang VM. Vua phuc tap, vua hay bi Google bat xac minh lai do khac
thiet bi/IP, vua tang rui ro lo phien. Profile cloud browser tren VM cung khong truy cap truc
tiep duoc tu filesystem nen khong copy file tho duoc.

## Bao mat

Giao mat khau la giao ca mailbox: ai co phien Gmail thi doc duoc moi mail va reset duoc mat khau
nhieu dich vu khac qua "quen mat khau". Mat khau chi giu trong Secure Vault, khong ghi vao chat,
file hay memory. Google se gui canh bao "sign-in moi" khi dang nhap tu IP VM, do la binh thuong,
khong phai bi hack. Thu hoi khi can: myaccount.google.com, Security, Your devices.
