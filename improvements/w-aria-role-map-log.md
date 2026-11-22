# W-ARIA role map log (COORD-CLICK-6, muc 3 hang doi resume)

Worker: W-ARIA. Repo: computer-use-wayland, nhanh todolist-push, HEAD 05140c1
luc bat dau. Bat dau 2026-11-22 17:49 +07 (Asia/Ho_Chi_Minh).
Moi claim co lenh da chay, output, commit hash, thoi gian chay (wall-clock
+07 voi elapsed). Khong tu cham minh pass.

## 0. Trang thai repo luc bat dau

- `git fetch origin` loi lock ref `refs/remotes/origin/main` (loose ref
  d49dbe2 vs packed-refs b8cfe92, pre-existing). Da sua bang
  `git fetch origin main:refs/remotes/origin/main`, sau do origin/main =
  d49dbe23760e7a1856fbe82902b528163e00d387. `origin/todolist-push` =
  05140c10d180ce7d26548df0f5b6f9c4d431e316 = HEAD local, nhanh hien tai
  todolist-push. Khong can pull them.
- Working tree luc bat dau co file cua worker khac, KHONG dung toi:
  modified `tests/realistic/clone1-batch3/results.json`, untracked
  `improvements/codex-discuss-prompt.md`, `fcc-discuss-prompt-run2.md`,
  `fcc-discuss-prompt.md`, `multi-agent-deliberation-idea-20261121.md`,
  `muse-coordinate-accuracy-20261120.md`, `worker-y14b-fix6-redteam.md`.

## 1. Audit: harvest sinh role nao, grounding chap nhan role nao

### 1.1 Harvest 1: DOM snapshot (scripts/cdp.mjs, ham snapshot)

- Candidate: selector INTERACTIVE (dong 178):
  `button,a[href],input,textarea,select,summary,[role="button"],[role="checkbox"],[role="tab"],[role="menuitem"],[contenteditable="true"]`
- Role (dong 211): `e.getAttribute('role') || (tagName==='A' ? 'link' : tagName.toLowerCase())`,
  KHONG lowercase, KHONG chuan hoa contenteditable.
- Role co the sinh (tu code, da doc het ham):
  tag: button, link (a[href]), input, textarea, select, summary, bat ky tag
  nao co contenteditable="true" (div, span, p, ...); cong bat ky gia tri
  role attr nao dat tren cac candidate tren (vi du textbox, searchbox,
  combobox, switch, slider, spinbutton, radio, menuitemcheckbox,
  treeitem, ...).
- Hop dong hien tai: tests/cdp_snapshot.mjs:424 khang dinh
  `[['e1','input'],['e2','button']]`, tuc `<input>` harvest thanh "input".

### 1.2 Harvest 2: AX tree (scripts/cdp.mjs, ham harvest)

- Role loc boi whitelist (dong 257):
  button|link|textbox|checkbox|radio|combobox|searchbox|spinbutton|slider|
  menuitem|menuitemcheckbox|menuitemradio|tab|switch|treeitem (case-insensitive).
- Chi tests/cdp_validation.mjs:123-126 doc ax_tree (role textbox). Khong
  consumer nao khac dung ax_tree de ground target. Khong gap o day.

### 1.3 Harvest 3: tests/two_vision_bench.py HARVEST_JS

- Tu chuan hoa role: input (tru button/submit) -> "textbox", textarea ->
  "textbox", contenteditable -> "textbox", explicit role attr thang.
  Selector co ca `[role="textbox"]`.
- find_input chi chap nhan role == "textbox", nhung harvest cua chinh no
  da chuan hoa ve "textbox" nen tu nhat quan. Da kiem tra: KHONG gap.
  (Ghi chu: day la bang chung trong repo rang contenteditable duoc coi
  la textbox o noi khac, trong khi cdp.mjs thi map thanh ten tag.)

### 1.4 Grounding (cac noi tieu thu role)

| # | Consumer | Predicate | Nhan xet |
|---|----------|-----------|----------|
| G1 | scripts/s2_flip_live.py COMPOSER_ROLES (3 cho: dong 114, 156, 429) | role in ('textarea','textbox','input') va name == 'Message' | Gap A, B (muc 2) |
| G2 | tests/browser_task_benchmark.py pick_ref | role == role truyen vao ('input', 'button') | Fixture dung `<input>`/`<button>` that, khop harvest. Khong gap. |
| G3 | tests/two_vision_bench.py find_input | role == 'textbox' | Harvest cua no tu chuan hoa. Khong gap. |
| G4 | cdp.mjs confirm_click (dong 298) | role tinh lai giong snapshot, so voi expected_role cua caller | Caller copy tu snapshot nen khop theo cau truc; nhung cong thuc tinh lai KHONG giong snapshot o 2 diem: co .toLowerCase() (snapshot khong co) va cung khong chuan hoa contenteditable. Gap D (case) anh huong ca 2 cho neu sua 1 cho. |
| G5 | scripts/a11y.py query / scripts/fastpath.py matches_query | substring, casefold | Namespace AT-SPI rieng, khong phai ARIA/CDP. Khong gap. |
| G6 | scripts/element_ref.py | chi mang role theo, khong so sanh voi tap co dinh | Khong gap. |
| G7 | scripts/live_metrics.py clickable_on_path (dong 123-128) | tag a/button/input/select/textarea/label hoac role button/link | Thieu checkbox/tab/menuitem so voi HIT_USABLE cua cdp.mjs (5 role). Chi la diagnostic, khong ground target nen KHONG sua trong task nay, ghi nhan de follow-up. |
| G8 | skill/references/browser.md:15 | doc: anchor -> link, button -> button tru khi page co explicit role | Doc nhat quan voi harvest. Khong gap. |

## 2. Gap tim duoc (moi cai co bang chung failing-first + live)

- GAP A: `<div contenteditable="true" aria-label="Message">` harvest thanh
  role "div", COMPOSER_ROLES tu choi -> "composer not found in snapshot".
  Cung lop voi run 90. Chuan ARIA: contenteditable co implicit role
  textbox; hai_vision_bench va AX tree deu coi la textbox.
- GAP B: `<input role="searchbox">` / `<input role="combobox">` harvest
  thanh "searchbox"/"combobox", COMPOSER_ROLES tu choi. Day la ARIA
  text-entry role, cung lop voi run 90.
- GAP C: `<div role="textbox">` (khong contenteditable, khong tag native)
  KHONG co trong snapshot vi INTERACTIVE thieu `[role="textbox"]`
  (tuong tu searchbox/combobox). COMPOSER_ROLES chap nhan "textbox"
  nhung harvest khong bao gio sinh ra no cho dang nay -> nhanh chet.
  two_vision_bench HARVEST_JS co `[role="textbox"]`, cdp.mjs khong co.
- GAP D: role attr viet hoa, vi du role="TextBox", harvest giu nguyen
  "TextBox", COMPOSER_ROLES (case-sensitive) tu choi; trong khi
  confirm_click da .toLowerCase(), AX filter la /i, a11y/fastpath dung
  casefold. Snapshot la cho duy nhat case-sensitive.

An toan khi sua (lap lai lap luan run 91): set_value/fill van fail lon
tren field khong phai text (set_value chi chap nhan INPUT|TEXTAREA voi
type text|search|tel|url|email; fill doi editable), nen ground nham
khong the send lang le.

## 3. Fix (da landing, xem muc 6 lay hash)

- F1 (GAP A + GAP D): cdp.mjs snapshot role: contenteditable khong co
  explicit role -> "textbox"; lowercase role. Ap dung cung chuan hoa o
  confirm_click (dong 298, truoc day da lowercase nhung thieu
  contenteditable).
- F2 (GAP B): COMPOSER_ROLES them 'searchbox', 'combobox'.
- F3 (GAP C): INTERACTIVE them `[role="textbox"],[role="searchbox"],[role="combobox"]`;
  mirror vao fake-DOM ROLES regex trong tests/cdp_snapshot.mjs.

## 4. Test failing-first

### 4.1 Truoc fix, 2026-11-22 17:54:08-17:54:10 +07, elapsed 2s

Lenh: `python3 -m unittest tests.test_s2_flip_wiring` + `node tests/cdp_snapshot.mjs`
- test_s2_flip_wiring: 21 tests, FAILED (failures=1):
  `test_composer_grounding_accepts_aria_text_entry_roles` ->
  `AssertionError: composer not found in snapshot` (role searchbox).
- cdp_snapshot.mjs: assertion fail tai dong 446:
  actual `[['e1','div'],['e2','searchbox'],['e3','TextBox']]`,
  expected `[['e1','textbox'],['e2','textbox'],['e3','searchbox'],['e4','textbox']]`.
  Chung minh GAP A (div), GAP C (div role=textbox vang mat), GAP D (TextBox).

### 4.2 Sau fix, 2026-11-22 17:55:08-17:55:09 +07, elapsed 1s

- test_s2_flip_wiring: 21 tests, OK.
- cdp_snapshot.mjs: rc=0, `all cdp snapshot, redaction, fill, payload,
  no_after and scope regressions pass`.

### 4.3 Khong regression, 2026-11-22 17:55:13-17:55:26 +07, elapsed 13s

- `node tests/cdp_validation.mjs`: rc=0.
- `python3 -m unittest tests.test_code_exec tests.test_dom_act`:
  Ran 79 tests, OK.

## 5. Kiem chung live (Chromium agent 9223, KHONG dong vao Zen)

Fixture: /tmp/w-aria-fixture.html tren laptop (10 element tuong tac,
tat ca aria-label "Message" tru nut Send/select/summary). Scratch tab
mo bang /json/new tren 9223, dong ngay sau moi lan observe. Chi con
tab goc 1154C84F (muse.ai) sau moi lan chay, da kiem tra.

### 5.1 Truoc fix, 2026-11-22 17:54:36-17:54:42 +07

Observe bang cdp.mjs truoc fix (observe 75ms, rc=0), 9 element:
e1 input, e2 textarea, e3 div, e4 searchbox, e5 combobox, e6 TextBox,
e7 button, e8 select, e9 summary. GAP A/B/D hien live. GAP C chua ket
luan duoc o lan nay: div role=textbox trong fixture ban dau rong nen
cao 0, bi loc boi dieu kien visibility cua snapshot chu khong phai do
selector. Ghi nhan confound nay, khong dung lan chay nay lam bang
chung GAP C.

### 5.2 Lam lai GAP C dung, 2026-11-22 17:56:09 +07, ca 2 observe 268ms

Fixture sua: div role=textbox co noi dung "aria" (cao > 0). Cung 1 tab,
observe lan luot bang cdp.mjs CU (old) va MOI (new), rc=0 ca 2:
- OLD (9 element): e1 input, e2 textarea, e3 div, e4 searchbox,
  e5 combobox, e6 TextBox, e7 button, e8 select, e9 summary.
  Div role=textbox VANG MAT.
- NEW (10 element): e1 input, e2 textarea, e3 textbox, e4 searchbox,
  e5 combobox, e6 textbox, e7 textbox, e8 button, e9 select,
  e10 summary. e3 textbox (contenteditable, GAP A), e6 textbox
  (TextBox lowercase, GAP D), e7 textbox (div role=textbox, GAP C).
- Snapshot JSON goc da luu: improvements/w-aria-role-map/live-before.json
  (OLD) va live-after.json (NEW).

### 5.3 Grounding tren snapshot live, 2026-11-22 17:56:23 +07, elapsed 0s

COMPOSER_ROLES moi = ('textarea', 'textbox', 'input', 'searchbox', 'combobox').
- Full page: OLD ground e1, NEW ground e1 (input van duoc uu tien).
- Gia lap page chi co composer la contenteditable (bo e1, e2):
  BEFORE + OLD roles -> None (gap live); BEFORE + NEW roles -> e4
  (searchbox, tuc fix grounding mot minh van chua thay duoc div vi
  harvest van bao 'div'); AFTER + NEW roles -> e3 (ca 2 fix thay duoc).
- Gia lap page chi co div role=textbox: AFTER + NEW roles -> e7.
- Dau program that cua s2 (build_program va build_program_set_value)
  chay tren snapshot live AFTER: ca 2 ground e1.

### 5.4 Ghi chu khac

- Trong luc lam, MEMORY.md thay doi tu ben ngoai (17:46 goal moi,
  17:55 giao may + doi nhan su mei/mochi). Khong lien quan task nay,
  khong hanh dong gi them.

## 6. Commit / push

- Commit fix + test + bang chung live:
  f209b3a1733b790dff32e90cb98988e0659cc8cc (2026-11-22, todolist-push).
  6 file: scripts/cdp.mjs, scripts/s2_flip_live.py,
  tests/cdp_snapshot.mjs, tests/test_s2_flip_wiring.py,
  improvements/w-aria-role-map/live-before.json,
  improvements/w-aria-role-map/live-after.json.
  Chi stage bang pathspec tung file; khong dung git add -A hay
  git commit tran; khong commit tests/realistic/clone1-batch3/results.json
  hay file cua worker khac.
- Commit log nay: commit rieng sau commit fix, cung nhanh todolist-push,
  push cung luc; hash trong bao cao ban giao cho COORD-CLICK-6.
- Su co day (2026-11-22 17:57 +07): checkout dung chung, W-EVID commit
  8d5eb3b da quet edit cuoi cua log nay vao commit cua ho (broad add),
  trong khi ban cung noi dung do da duoc push tu cho khac thanh 7267e51
  (van giu dong placeholder). Diff 8d5eb3b..7267e51 chi khac dung 2 dong
  cuoi cua file log nay, khong mat noi dung cua ai. Giai quyet: reset
  --soft ve origin/todolist-push (7267e51), commit lai dung 2 dong nay
  thanh 1 commit rieng, push fast-forward. Khong force-push, khong
  rebase commit cua worker khac.
