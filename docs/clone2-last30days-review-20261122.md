# Review doc lap source last30days-skill, Critical Risk that hay gia

Ngay review: 22/11/2026. Repo review: github.com/mvanhorn/last30days-skill, commit f5d0e44, version 4.5.0 trong skills/last30days/SKILL.md. Clone read-only vao /tmp/last30days-skill, chi doc nhu plain text, khong chay installer, khong chay bat cu file nao trong repo, khong copy vao home, config, PATH hay tools. Khong click qua xac nhan installer trong bat cu truong hop nao.

## Verdict: PROCEED

Critical Risk la false positive ve y do doc hai. Khong co hanh vi doc hai that trong source: khong exfiltration, khong obfuscation, khong trom credential, khong hardcode secret, khong download-and-execute. Nhung flag khong phai vo can cu: skill co tinh doc va giai ma session cookie cua trinh duyet, dung la hanh vi ma cac scanner sinh ra de bat. Phan biet ro: flag bat dung kha nang, sai ve y do. Kha nang do duoc ghi trong tai lieu, co cong tac dong y, gioi han pham vi, va chi chay khi nguoi dung bat.

Verdict PROCEED khong cho phep tu cai bang -g. Quyet dinh cai la cua Muse tong sau khi doc verdict nay.

## Cach review

Doc SKILL.md, SECURITY.md, cac script last30days.py, store.py, box_chrome_login.py, setup-keychain.sh, setup-pass.sh, thu muc lib/ (130 module Python), thu muc mcp/ (Go server), pyproject.toml o repo root, uv.lock, CHANGELOG.md, tests/hermes/. Chay lai logic replica cua repo (tests/hermes/test_no_critical_scan_findings.py) bang python3 tren ban clone: 0 CRITICAL hit. Grep toan repo cho eval, exec, shell=True, os.system, verify=False, pickle, curl pipe shell, authorized_keys, NOPASSWD, /etc/passwd, rm -rf.

## Nhung gi scanner thay, va su that tung cai

### 1. Doc va giai ma session cookie trinh duyet (nguyen nhan chinh cua flag)

Day la cum code ma ca ba scanner deu bat, vi no khop mau "credential theft / session hijacking":

- skills/last30days/scripts/lib/chrome_cookies.py: doc SQLite Cookies cua Chrome, Brave, Edge, Vivaldi, Opera, Arc, Dia, Chromium tren macOS, lay passphrase tu macOS Keychain bang `security find-generic-password` (_get_chromium_encryption_key, dong khoang 100-130), dao khoa AES bang PBKDF2-HMAC-SHA1, salt "saltysalt", 1003 vong, roi giai ma v10 bang openssl AES-128-CBC (_decrypt_v10_value). Day la dinh dang ma hoa v10 cua chinh Chrome, skill buoc phai theo dung no moi doc duoc, khong phai lua chon cua tac gia.
- skills/last30days/scripts/lib/cookie_extract.py: doc truc tiep bang moz_cookies cua Firefox (dong 285, query co tham so hoa, chi doc 2 ten cookie duoc chi dinh cho domain duoc chi dinh). Firefox khong ma hoa cookie nen khong can giai ma.
- skills/last30days/scripts/lib/safari_cookies.py: parse file Cookies.binarycookies cua Safari (dinh dang binary khong ma hoa), chi doc.
- skills/last30days/scripts/lib/chrome_cdp.py: mo websocket CDP toi Chrome cuc bo roi goi Network.getAllCookies (_get_all_cookies, dong 280-310), sau do loc chi giu x.com va twitter.com (khop chinh xac sau khi bo mot dau cham, _ALLOWED_X_HOSTS).
- skills/last30days/scripts/lib/agentcookie.py: goi binary ngoai `agentcookie cookies --domain .x.com --json` (read_x_cookies), chi nhan du cap auth_token + ct0, mot nua thi bo.
- skills/last30days/scripts/lib/reddit_session.py: gui cookie reddit_session chi toi reddit.com (dong 204-205).

Gioi han da ghi trong code va tai lieu, da kiem tra:

- Chi doc 2 cookie cua X (auth_token, ct0), 1 cookie cua Truth Social (_session_id), 1 cookie cua Reddit (reddit_session). Loc theo domain va ten truoc khi giai ma bat cu thu gi (SECURITY.md, muc Browser cookies).
- Mac dinh TAT: FROM_BROWSER chua set thi khong doc cookie trinh duyet nao (env.py cookie_extraction_browsers, dong 1309-1315). Tu choi ro rang thang: BROWSER_CONSENT=false hoac FROM_BROWSER=off tat ca duong doc cookie, ke ca sidecar (env.py cookie_access_denied, dong 1290-1302; gia tri dong y khong nhan dang thi fail closed).
- Khong bao gio chay tren Grok Bot, hosted, hay scheduled run (SKILL.md, GROK BOT HOST RULE).
- Gia tri cookie khong bao gio ghi log, khong luu vao .env hay file nao, chi o trong bo nho roi truyen qua bien moi truong toi client X (agentcookie.py, docstring; SECURITY.md).
- Ban sao tam cua cookie DB co quyen 0600 va xoa ngay sau khi doc (chrome_cookies.py _lock_temp_cookie_copy, cookie_extract.py finally).
- Cookie chi gui toi dung dich: X cookie chi toi x.com, twitter.com, upload.twitter.com (vendored bird-search, dem duoc 13 x.com, 1 upload.twitter.com, 1 twitter.com); reddit_session chi toi reddit.com; khong co host thu ba nao nhan cookie.

Ket luan muc 1: hanh vi la that, nhung la tinh nang co ghi trong tai lieu, co cong tac dong y, co pham vi hep, khong co exfiltration. Scanner khong phan biet duoc "doc cookie co dong y de search X" voi "trom session", nen flag Critical la false positive ve y do, dung ve kha nang.

### 2. Doc credential tu Keychain va pass (nguyen nhan phu)

- skills/last30days/scripts/lib/env.py _load_keychain (dong 369-460): chay `security find-generic-password -a <user> -s last30days-<KEY> -w` cho khoang 24 key, chi tren Darwin, la nguon uu tien thap nhat. Co cong tac tat LAST30DAYS_SKIP_KEYCHAIN.
- skills/last30days/scripts/lib/env.py _load_pass: chay `pass show last30days/<KEY>`, chi doc dong dau, khong ghi ra dia, khong log.
- skills/last30days/scripts/setup-keychain.sh va setup-pass.sh: chi ghi key do nguoi dung go tay vao (doc tu stdin, khong ghi log), luu bang `security add-generic-password` hoac `pass insert`, quyen 0600.

Day la cach luu key chuan cua he dieu hanh, khong phai trom key. Scanner thay "read secrets from credential store" thi flag.

### 3. Chuoi curl pipe shell con sot trong CHANGELOG.md (trigger that cho scanner regex)

Skill dir hien tai SACH chuoi nay: grep toan bo skills/ va mcp/ khong con dong nao. Fix #1502 da doi hint cai Grok CLI thanh `npm install -g @xai-official/grok` (references/setup-wizard.md:193, lib/health.py:225-226, 246-247, lib/prescriptions.py:137-140, lib/backends.py:307; rieng lib/grok_x.py:8 dung dang viet tat `npm i -g`).

Nhung chuoi cu van con o 3 cho NGOAI skill dir, ma installer quet ca repo se thay:

- CHANGELOG.md:819, dong changelog lich su mo ta cach cai cu (curl tai installer roi pipe sang bash).
- tests/hermes/baseline_findings.md:33, ghi lai finding cu de lam tai lieu.
- tests/hermes/test_no_critical_scan_findings.py:127, chinh test replica dung chuoi mau de khang dinh rule bat duoc no.

Day la tai lieu lich su va test, khong phai lenh chay. Nhung scanner regex don gian khong phan biet duoc, day la trigger false positive that su ma tac gia bo sot. De nghi bao upstream xoa hoac che chuoi nay trong CHANGELOG.md:819 neu muon sach flag.

### 4. Cai remote code luc setup (supply chain, muc thap)

- skills/last30days/scripts/lib/setup_wizard.py _run_npx_install (dong 285-325): chay `npx -y @mvanhorn/printing-press-library install <slug> --cli-only` de cai cac CLI Digg, arXiv, Techmeme, Yahoo Finance, Trustpilot. Chi chay luc setup, chi cai package co scope cua chinh tac gia, co kiem tra sau cai.
- SECURITY.md ghi setup cai yt-dlp bang Homebrew tren macOS khi thieu.

Khong co lenh tai ve roi chay kieu pipe-to-shell trong skill. Rui ro chi la supply chain cua mot package npm cua tac gia, muc thap, va nguoi dung co the bo qua.

### 5. Nhung gi da kiem tra la KHONG co

- 0 hardcoded secret: chay replica Hermes (50 rule CRITICAL cua skills-guard-v16) tren skills/last30days cho 0 hit. Grep sk-, ghp_, github_pat_, AKIA, BEGIN PRIVATE KEY: 0 secret that, chi 1 duong dan gia tu chu "disk-" trong comment "on-disk-but-off-PATH" (lib/health.py:268).
- 0 eval, exec, __import__ chay code dong. Grep eval( chi gap 2 lan ten ham verify_eval (verify_v3.py:138, 187), khong phai lenh eval. Ve compile: ngoai re.compile con co helper ten _compile (lib/x_api.py:336) chi ghep chuoi query X, khong phai lenh compile() chay code.
- 0 shell=True, os.system, os.popen trong scripts/.
- 0 verify=False, CERT_NONE, unverified context trong scripts/. http.py co guard SSRF: redirect toi dia chi private bi tu choi (dong 121-130).
- 0 pickle, marshal, shelve, yaml.load khong an toan.
- SQL co tham so hoa: store.py dung f-string chi de ghep ten cot da kiem tra qua allowlist _UPDATABLE_RUN_COLUMNS / _UPDATABLE_FINDING_COLUMNS (dong 541, 943), gia tri luon la placeholder ?.
- Runtime dependencies bang 0 (pyproject.toml o repo root, dependencies = []), chi dung stdlib. Dev deps trong uv.lock chi co pytest, pyyaml, towncrier va phu thuoc cua chung, khong co CVE runtime de quet.
- MCP Go server (mcp/internal/engine/run.go): chi goi exec.Command(pythonPath, ...) voi env thua ke tu parent cong ExtraEnv, khong truyen secret rieng, khong co lenh shell.
- Vendored bird-search package.json: private, khong co install script, khong co dependencies.
- box_chrome_login.py: chi in lenh khoi dong Chrome de nguoi dung tu dang nhap, docstring ghi ro "Reads NO cookies and prints NO cookie values", khong doc cookie nao.

### 6. Ghi chu ve quy mo va lich su scanner cua repo

- Repo tu co test bao ve tests/hermes/test_no_critical_scan_findings.py (replica 50 rule CRITICAL cua Hermes skills-guard-v16) va file tests/hermes/baseline_findings.md ghi lai lich su: thang 07/2026 Hermes tung danh dangerous voi 14 CRITICAL (7 python_environ_get_secret, 4 ruby_env_secret, 2 env_exfil_httpx, 1 deception_hide), khong co curl_pipe_shell trong so do. 6 curl_pipe_shell thuoc lan do lai thang 11/2026 (7 CRITICAL truoc fix #1502). Sau fix #1502, Hermes ve caution, 0 CRITICAL. Nghia la repo da tung bi flag va da sua dung huong, nhung Gen/Socket/Snyk co rule khac Hermes, nhat la rule doc cookie trinh duyet, nen van flag.
- Skill dir hien 19M (scripts 4.2M). Hermes tung danh HIGH oversized_skill (1615KB luc do), khong phai CRITICAL, khong anh huong verdict nay.

## Luu y bo sung (sau council + redteam)

- Luong du lieu rerank: resolve_runtime (lib/providers.py:476-493) tu chon provider theo key co san theo thu tu Gemini, OpenAI, xAI, OpenRouter, nen key dat cho mot muc dich (vi du XAI_API_KEY cho search X) cung duoc dung de gui topic + tieu de, doan trich, comment duoc chon loc toi provider do de rerank (lib/rerank.py:304-310; lib/planner.py:536-537 cung goi provider.generate_json). Da ghi trong SECURITY.md muc Hosted reasoning models, opt-in bang key co san, key chi toi dung provider cua no, khong co key thi cham diem cuc bo. Khong phai exfiltration, khong doc hai, nhung lam ro khung "du lieu chi toi dung host": du lieu co the toi them provider rerank.
- Luat Grok Bot la dieu kien mem: x_policy (lib/env.py:1820-1838) chi kich hoat khi host khai LAST30DAYS_HOST=grok-bot; neu chuoi khong bao gio duoc set thi x_policy khong ap dung. Dong y doc cookie van bat buoc trong moi truong hop, day la gia dinh trien khai, khong phai lo hong code.

## Dieu kien kem theo verdict PROCEED

1. Cai skill thi cai, nhung mac dinh KHONG bat cookie trinh duyet: de FROM_BROWSER off va BROWSER_CONSENT false. Dung duong X API chinh thuc (X_BEARER_TOKEN) hoac Grok CLI thay vi cookie. Chi bat cookie khi that su can search X bang session, va tat lai sau do.
2. Khong bao gio chay skill tren host share, scheduled run, hay Grok Bot voi cookie bat (skill tu tat, nhung dung dua vao do).
3. Bao upstream (issue) xoa chuoi curl pipe shell o CHANGELOG.md:819 de sach flag cho lan quet sau. Day la viec cua upstream, khong chan cai dat.
4. Verdict nay chi ap dung cho commit f5d0e44, version 4.5.0. Ban moi can review lai neu them code doc credential.

## Gioi han cua review

- Chi doc source dang plain text, khong chay code nao trong repo, khong cai skill, khong chay installer. Khong the chay lai chinh xac ba scanner Gen/Socket/Snyk cua installer vi khong co quyen truy cap chung; ket luan dua tren rule da biet cua cac loai scanner nay va tren code thuc te.
- Khong kiem tra dich vu ben thu ba (api.scrapecreators.com, api.x.com, api.x.ai, hn.algolia.com, gamma-api.polymarket.com): chi xac nhan code gui dung loai du lieu da ghi trong SKILL.md toi dung host do, khong gui key hay cookie sang host khac.
- Khong danh gia tinh bao mat cua cac dich vu ben thu ba hay cua npm package printing-press-library.
