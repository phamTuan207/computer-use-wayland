# Dieu khien Zen qua AT-SPI: nghien cuu va prototype

Ngay: 2026-11-21. May chay: clone1, Ubuntu 24.04, khong co san
Firefox hay Zen, khong co desktop session. Ket luan ngan: cay
AT-SPI cua Firefox doc duoc day du, click qua Action chay that va
da kiem chung, go phim qua AT-SPI thi khong dang tin tren Firefox
hien tai. Zen dung chung stack Gecko voi Firefox nen ket qua nay
chuyen sang Zen duoc, nhung phan Zen that van UNVERIFIED.

## 1. Ket qua tom tat

| Kha nang | Ket qua tren Firefox 160.0.1 | Ghi chu |
| --- | --- | --- |
| Doc cay AT-SPI | CHAY, da kiem chung | 71 node, ca chrome UI va noi dung web |
| Click qua Action | CHAY, da kiem chung | Counter 0 thanh 1, doc lai duoc |
| Chuyen tab qua Action | Co action "switch", chua chay | Chi thay action, chua bam |
| Go text qua EditableText | HONG tren 160.0.1 | Tra True nhung gia tri khong doi, Bug 2087495 |
| Go phim qua generateKeyboardEvent | KHONG CHAY dang keysym | Chi dang keycode moi toi duoc field |
| Go phim qua keycode | TOI DUOC nhung sai ky tu | Keymap Xvfb mac dinh lech, can anh xa keysym sang keycode |
| Chuot qua generateMouseEvent | CHAY | Dung de focus field, xdotool type sau do chay |

## 2. AT-SPI la gi, Firefox dung no the nao

AT-SPI (Assistive Technology Service Provider Interface) la API
tiep can cua Linux tren D-Bus. Ung dung dang ky cay doi tuong cua
no voi registry (at-spi2-registryd), client nhu Orca, Accerciser,
Dogtail doc cay qua libatspi hoac pyatspi. Moi node co role (push
button, entry, document web, page tab), name, states, extents tren
man hinh, va cac interface: Action (click, press, activate),
Component (vi tri, grabFocus), Text (doc text), EditableText (sua
text), Value, Selection.

Firefox tren Linux xuat cay tiep can qua ATK bridge sang AT-SPI2.
Day la cung kenh Orca dung de doc trang web, nen cay noi dung web
cua Firefox la that, khong phai mo phong. Chrome UI cua Firefox
(thanh tab, thanh dia chi, hop thoai) cung nam trong cay. Dieu
kieu de cay xuat hien:

- `accessibility.force_disabled` phai la false (mac dinh tren cac
  ban Firefox gan day, nhung dat false trong user.js cho chac).
- Bien `GNOME_ACCESSIBILITY=1` khi khoi dong Firefox, hoac cong tac
  `org.a11y.Status.IsEnabled` dang bat. Firefox theo doi cong tac
  nay luc chay.
- Query dau tien co the tra ve cay rong vi cay duoc tao luoi
  (lazy), can thu lai sau vai giay.

## 3. Moi truong luc bat dau, va da cai gi de chay duoc

Luc bat dau, may nay khong co gi de chay AT-SPI:

- Khong co Firefox, Zen, hay Chromium (chi co Chromium cache cua
  Playwright, khong phai app desktop).
- Chi co at-spi2-common 2.52.0 va libatk-bridge2.0-0t64 (file thu
  vien), khong co at-spi2-core, khong co registry daemon, khong co
  pyatspi, khong co gi (PyGObject), khong co dogtail hay accerciser.
- Khong co DISPLAY, khong co D-Bus session bus, khong co desktop
  session. Khong co xdotool hay ydotool.

Da cai de chay prototype (tat ca bang apt, sau `apt-get update`):

- at-spi2-core 2.52.0, python3-pyatspi 2.46.1, gir1.2-atspi-2.0
  2.52.0, dbus-x11 1.14.10. Xvfb 2:21.1.12 da co san.
- Firefox 160.0.1, tai tu download.mozilla.org, file
  firefox.tar.xz 90,943,956 byte, giai nen ra /tmp/firefox.
- xdotool 3.20160805.1, chi dung lam doi chung cho viec go phim,
  khong nam trong prototype chinh.

Phien chay that: Xvfb :99 (1280x1024), dbus-launch lay session bus,
at-spi-bus-launcher, Firefox voi profile moi co user.js dat
accessibility.force_disabled=false va tat cac man hinh chao dau
(phai xoa profile va tao lai moi lan chay vi hop thoai onboarding
van hien, xem muc 5).

## 4. Prototype

File: tests/atspi_probe.py (stdlib cong pyatspi, khong phu thuoc
ngoai). Cac mode: dump (in cay dang JSON), click, type, full.
Moi buoc log 1 dong JSON co wall_clock va elapsed_ms. Thoat 0 khi
moi op yeu cau duoc xac minh, 2 khi co op that bai.

Cac buoc trong mode full:

1. Tim app Firefox tren desktop.
2. Tat hop thoai onboarding neu co (tim push button "Continue",
   "Not now", "Skip", bam qua Action).
3. Tim push button "Increment", bam qua Action, doc lai doan van
   "Counter: 1" de xac minh.
4. Tim entry "Name", go text qua EditableText, doc lai de xac minh.
5. Neu EditableText that bai, thu go phim qua generateKeyboardEvent
   sau khi click chuot vao giua field de focus.

## 5. Ket qua chay that

Fixture: tests/bidi_fixture.html (nut Increment, input Name,
counter). Moi so duoi day do that tren may nay, ngay 2026-11-21.

### 5.1 Doc cay: chay

- find_app: 11.0 den 31.9 ms tuy lan chay.
- Walk toan cay sau khi tat onboarding: 71 node, 15.4 den 29.9 ms.
- Cay gom: application Firefox, frame "BiDi fixture - Mozilla
  Firefox", 4 tool bar (Menu Bar, Browser tabs, Navigation, 1
  trong), page tab list voi page tab "BiDi fixture" co action
  "switch", nut Close tab, Back, Forward, Reload, combo box dia
  chi "Search with Google or enter address" co action "activate",
  Bookmark, Account, Extensions, va noi dung web: document web,
  heading "BiDi fixture", paragraph "Counter: 0", push button
  "Increment" (extents [8, 212, 77, 25], action "press"), entry
  "Name" (extents [138, 212, 180, 25], action "activate").

### 5.2 Tat onboarding bang AT-SPI: chay

Lan chay dau, cay chi co 37 node va noi dung web khong xuat hien,
vi hop thoai "Welcome to Firefox" (chrome://browser/content/
spotlight.html) dang mo va che tab. Cac pref tat welcome trong
user.js (aboutwelcome.enabled=false, showSpotlight=false,
homepage_override.mstone=ignore) khong tat duoc hop thoai nay
tren 160.0.1. Cach xu ly: bam nut "Continue" hoac "Not now" qua
Action "press", 0.2 den 0.3 ms, doi 2 s, cay day du xuat hien.
Day cung la bang chung AT-SPI dieu khien duoc ca chrome UI, khong
chi noi dung web.

### 5.3 Click qua Action: chay, da xac minh

- Tim nut "Increment": ok.
- Click qua Action "press": 0.2 den 0.3 ms, tra True.
- Doc lai paragraph qua Text interface: "Counter: 1",
  counter_seen true. Click that su lam counter tang, khong chi
  tra OK.

### 5.4 Go text qua EditableText: hong tren 160.0.1

- setTextContents("hello atspi") tra True, doc lai bang Text
  interface duoc chuoi rong. Goi that bai am tham, khong nem loi.
- Day la Bug 2087495 tren Bugzilla Mozilla, mo 10 ngay truoc
  (Firefox 152.0), da RESOLVED FIXED, thuoc nhanh 161. Nguyen
  nhan: trong accessible/atk/nsMaiInterfaceEditableText.cpp moi
  callback bat dau bang `if (acc->IsTextRole()) return;`, dieu
  kien bi dao nguoc tu Bug 1832353 Part 3, nen moi lenh
  set/insert/delete deu return som va khong lam gi. Firefox
  160.0.1 van co loi nay, ban sua nam o nhanh 161.
- He qua: khong dung EditableText de go text vao Firefox cho toi
  khi ban 161 tro len. Can kiem tra lai tren Zen (xem Zen base
  tren Firefox bao nhieu) truoc khi tin duong nay.

### 5.5 Go phim qua generateKeyboardEvent: 4 bien the da thu

Tat ca thu tren cung field "Name", sau khi field da co focus
(STATE_FOCUSED True, kiem tra truc tiep):

- A: KEY_SYM tung ky tu ("hi"): doc lai rong. That bai.
- B: KEY_STRING ca chuoi ("yo"): doc lai rong. That bai.
- C: KEY_PRESS roi KEY_RELEASE tung ky tu, dung keystring:
  doc lai rong. That bai.
- D: Action "activate" tren field roi KEY_SYM: focus True
  nhung doc lai van rong. That bai.
- E: KEY_PRESS/KEY_RELEASE dung keycode evdev (a=30, b=48):
  toi duoc field, nhung doc lai la "u'" thay vi "ab". Keycode
  toi duoc, nhung anh xa keycode sang ky tu lech theo keymap
  mac dinh cua Xvfb. Can bang anh xa keysym sang keycode theo
  keymap dang dung thi moi go dung.
- Doi chung bang xdotool type "yo": doc lai "yo", chay. Dieu
  nay chung to X focus va XTest van tot, loi nam o dang
  keystring cua generateKeyboardEvent trong stack nay
  (at-spi2 2.52.0, pyatspi 2.46.1), khong phai o focus.

### 5.6 Log day du lan chay cuoi (mode full)

- find_app ok, 22.0 ms.
- dismiss_onboarding ok, nut "Continue", action press, 0.3 ms.
- find_button ok, 2048.9 ms (gom 2 s doi sau khi tat dialog).
- click ok, action press, 0.3 ms.
- find_field ok, ten "Name".
- type_editabletext FAIL, "EditableText returned True, read back
  ''", 5.5 ms.
- type_keysyms_fallback FAIL, "keysym typing, read back ''",
  821.1 ms.
- final_readback ok, paragraph "Counter: 1", entry "", counter
  true. Probe exit 2 vi phan go text that bai.

## 6. Dieu nay co nghia gi cho Zen

Zen la fork cua Firefox tren Gecko, nen cay AT-SPI cua no co cung
hinh dang: chrome UI (sidebar, workspace cua Zen cung la tai lieu
chrome dang XUL/HTML) va noi dung web deu xuat hien qua AT-SPI
nhu Firefox. Nhung diem can kiem tra tren laptop, chua do duoc
o day:

- Zen base tren Firefox bao nhieu, va ban do co loi EditableText
  cua Bug 2087495 khong. Neu Zen base duoi 161, go text qua
  AT-SPI se am tham that bai nhu o day.
- Sidebar va workspace cua Zen co xuat hien day du trong cay
  khong, ten va role cua chung la gi.
- Tren Wayland, AT-SPI chay qua D-Bus nen doc cay va Action click
  van chay (khong can X). Nhung generateKeyboardEvent va
  generateMouseEvent dung XTest, khong chay tren Wayland, va
  xdotool cung chi chay tren X11. Tren Wayland, go phim chi con
  2 duong dang tin: EditableText (khi Firefox/Zen da sua loi)
  hoac BiDi Input (duong chinh cua repo nay).
- Vi vay, khuyen dung AT-SPI cho doc cay va click, dung BiDi
  cho go phim, cho toi khi loi EditableText duoc sua tren ban
  Zen dang dung.

## 7. Quy trinh chay tren laptop (de kiem tra Zen that)

Cac buoc nay chay tren may co desktop session that, khong phai
tren may clone1.

1. Cai goi can thiet:
   `sudo apt install at-spi2-core python3-pyatspi gir1.2-atspi-2.0`
2. Bat accessibility trong desktop (GNOME: Settings, Accessibility,
   bat Screen Reader; hoac dat `gsettings set org.gnome.desktop.interface toolkit-accessibility true`).
3. Khoi dong Zen voi `GNOME_ACCESSIBILITY=1`, mo trang fixture
   cua repo: `GNOME_ACCESSIBILITY=1 zen tests/bidi_fixture.html`
   (duong dan tuy theo cach cai Zen).
4. Chay probe: `python3 tests/atspi_probe.py --mode dump` roi
   `--mode full`. Kiem tra: cay co node Zen khong, nut Increment
   co bam duoc khong, counter co len 1 khong, EditableText co go
   duoc text khong.
5. Neu muon xem cay truc quan: cai accerciser, mo len, chon app
   Zen, duyet cay.
6. Ghi lai: phien ban Zen, phien ban Firefox base (zen://about
   hoac about:support), ket qua tung op, thoi gian tung op.

## 8. Du an tham khao

- Microsoft Hybrid Computer Use: provider Linux dung AT-SPI2,
  X11, XTest (xem docs/research/2026-11-21-microsoft-hybrid-computer-use.md
  trong repo nay).
- CUA (trycua/cua): test AT-SPI tren Linux, dung at-spi-bus-launcher
  dung session bus rieng, bat accessibility cho Firefox bang
  GNOME_ACCESSIBILITY=1, doc lai text da go qua AT-SPI Text.
- kwin-mcp va linux-desktop-mcp: MCP server doc cay AT-SPI qua
  gi.repository.Atspi, dung pyatspi, can at-spi2-core va
  gir1.2-atspi-2.0. Ca hai deu luu y Firefox chi xuat cay khi
  cong tac org.a11y.Status.IsEnabled dang bat.
- Orca: screen reader chuan cua GNOME, bang chung lau doi nhat
  rang cay AT-SPI cua Firefox doc duoc trang web.

## 9. UNVERIFIED

- Moi thu tren Zen that: Zen chua co tren may nay, chua tung chay.
  Cay cua Zen, sidebar, workspace, phien ban Firefox base, loi
  EditableText tren Zen, tat ca chua kiem chung.
- Hanh vi tren Wayland: moi test o day chay tren Xvfb (X11). Doc
  cay va Action click du kien chay tren Wayland vi chung la D-Bus,
  nhung chua do. Go phim qua XTest chac chan khong chay tren
  Wayland.
- Cay cua trang lon: fixture chi co vai node. Trang lon co the
  cham vi walk cay bang D-Bus goi tung node; can do tren trang
  that voi gioi han node va do sau.
- Chuyen tab qua action "switch": chi thay action ton tai, chua
  chay that.

## 10. Nguon

- Tai lieu AT-SPI2, GNOME: gnome.pages.gitlab.gnome.org/at-spi2-core,
  giao dien org.a11y.atspi.EditableText. Truy cap 2026-11-21.
- Bug 2087495, Bugzilla Mozilla: ATK EditableText methods are
  always no-ops due to inverted IsTextRole() check, RESOLVED
  FIXED, nhanh 161. Truy cap 2026-11-21.
- Orca va Firefox tren Linux: copyprogramming.com/howto/
  how-to-have-orca-read-webpage-in-firefox-on-ubuntu,
  accessible-data-interfaces.com, phan Orca and Firefox on Linux
  with Data Grids. Truy cap 2026-11-21.
- Watson issue 66, Browser tab switching on Linux via AT-SPI:
  github.com/william-long-ii/watson/issues/66. Truy cap 2026-11-21.
- CUA PR 1832, AT-SPI tren Linux: github.com/trycua/cua/pull/1832.
  Truy cap 2026-11-21.
- kwin-mcp va linux-desktop-mcp, pypi.org. Truy cap 2026-11-21.
- Vectree, AT-SPI overview: vectree.io/pdf/c/assistive-technology-service-provider-interface. Truy cap 2026-11-21.
