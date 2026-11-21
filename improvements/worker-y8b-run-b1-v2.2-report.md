# E1 B1-v2.2 report, single-arm observation under v2.2 (coordinator fencing header, prepended by Worker Y8b; the executor report below is verbatim)

Single-arm observation under v2.2. No comparison is drawn, now or later, from E1 data. Arm A has no valid observation (A1 FAIL incomplete, A2 FAIL incomplete, arm A BLOCKED under v2.1, judge 7275171). No deliberation win or loss is claimed. No total-speed arithmetic. No accuracy comparison. This B1-v2.2 run must never be paired with any future A run; a future comparison re-runs BOTH arms fresh. PASS/FAIL is read from out.log by the independent judge from the fixed final-read list, never from the executor claim.

Executor wall 20:06:45-20:15:27 +07 (522 s). Coordinator wall T0 20:06:32 to events-file close 20:15:35 (543 s). Driver commands 59. Tokens in 4,602,024 (cached 4,530,688), out 17,283, reasoning 3,754. Post-run audit: 59 report commands, 0 js values with a single quote, 0 JS parse failures, no forbidden reads, out.log B-range 59/59 ok:true.

--- executor report verbatim below ---

# E1 executor B report — test-05 contact book

Start time: 2026-11-21 20:06:45 +07
Files read, in order:
1. `/tmp/e1/plan-test-05.md`
2. `/tmp/e1/worker-y8-driver-reference.md`

1 | {"cmd":"new_session"} | {"ok":true,"result":"3fbba432","ms":4}
2 | {"cmd":"new_tab","url":"http://127.0.0.1:8767/test-05-contact-book.html"} | {"ok":true,"result":"022e068c","ms":1105}
After step 2 (required visibility diagnosis) | {"cmd":"eval","js":"return (function(){var cs=getComputedStyle(document.body);var r=document.body.getBoundingClientRect();var cc=document.querySelector(\"#contacts-count\");return{readyState:document.readyState,htmlClassList:Array.from(document.documentElement.classList),bodyVis:cs.visibility,bodyOpacity:cs.opacity,bodyDisplay:cs.display,rect:{w:r.width,h:r.height},innerLen:document.body.innerText.length,hasFocus:document.hasFocus(),visState:document.visibilityState,countText:cc?cc.textContent.trim():null};})()"} | {"ok":true,"result":{"bodyDisplay":"block","bodyOpacity":"1","bodyVis":"visible","countText":"6","hasFocus":true,"htmlClassList":[],"innerLen":576,"readyState":"complete","rect":{"h":580.5333251953125,"w":1615},"visState":"visible"},"ms":2} | VISIBLE
3 | {"cmd":"eval","js":"localStorage.clear(); return localStorage.length"} | {"ok":true,"result":0,"ms":2}
4 | {"cmd":"eval","js":"return {count:document.querySelector(\"#contacts-count\").textContent.trim(),cardCount:document.querySelectorAll(\"#contacts-list .contact-card\").length,ids:Array.from(document.querySelectorAll(\"#contacts-list .contact-card\")).map(c=>c.id),names:Array.from(document.querySelectorAll(\"#contacts-list .contact-name\")).map(e=>e.lastElementChild.textContent.trim())}"} | {"ok":true,"result":{"cardCount":6,"count":"6","ids":["contact-card-alice-chen","contact-card-bob-martin","contact-card-clara-vance","contact-card-david-kim","contact-card-eva-rostova","contact-card-spam-bot"],"names":["Alice Chen","Bob Martin","Clara Vance","David Kim","Eva Rostova","Spam Bot"]},"ms":2}
5 | {"cmd":"find","css":"#btn-new-contact"} | {"ok":true,"result":"0f816751-c098-444c-9eb2-6aa204c65cdc","ms":2}
6 | {"cmd":"click","el":"0f816751-c098-444c-9eb2-6aa204c65cdc"} | {"ok":true,"result":"clicked","ms":59}
7 | {"cmd":"eval","js":"return {display:document.querySelector(\"#contact-modal\").style.display,title:document.querySelector(\"#modal-title\").textContent.trim()}"} | {"ok":true,"result":{"display":"flex","title":"Add New Contact"},"ms":2}
8 | {"cmd":"find","css":"#input-contact-first"} | {"ok":true,"result":"94b92eb8-64ef-4f7f-9f5f-e79bfbda40a6","ms":2}
9 | {"cmd":"type","el":"94b92eb8-64ef-4f7f-9f5f-e79bfbda40a6","text":"Frank"} | {"ok":true,"result":"typed","ms":6}
10 | {"cmd":"find","css":"#input-contact-last"} | {"ok":true,"result":"01513187-d58a-4ea2-a0ab-1e7d7c99fc53","ms":2}
11 | {"cmd":"type","el":"01513187-d58a-4ea2-a0ab-1e7d7c99fc53","text":"Sinatra"} | {"ok":true,"result":"typed","ms":7}
12 | {"cmd":"find","css":"#input-contact-email"} | {"ok":true,"result":"d233dbea-0574-4a6b-bbef-ade424277272","ms":1}
13 | {"cmd":"type","el":"d233dbea-0574-4a6b-bbef-ade424277272","text":"frank.s@example.com"} | {"ok":true,"result":"typed","ms":4}
14 | {"cmd":"find","css":"#input-contact-phone"} | {"ok":true,"result":"701e61de-807a-4b09-8446-037b7c440fed","ms":1}
15 | {"cmd":"type","el":"701e61de-807a-4b09-8446-037b7c440fed","text":"+1-555-0106"} | {"ok":true,"result":"typed","ms":5}
16 | {"cmd":"eval","js":"const e=document.querySelector(\"#select-contact-group\"); e.value=\"Engineering\"; e.dispatchEvent(new Event(\"change\",{bubbles:true})); return e.value"} | {"ok":true,"result":"Engineering","ms":2}
17 | {"cmd":"find","css":"#input-contact-notes"} | {"ok":true,"result":"8ec4c15b-545e-48ae-a547-ed419b267ac7","ms":1}
18 | {"cmd":"type","el":"8ec4c15b-545e-48ae-a547-ed419b267ac7","text":"Vocal Architect"} | {"ok":true,"result":"typed","ms":5}
19 | {"cmd":"find","css":"#btn-modal-save-contact"} | {"ok":true,"result":"7904b135-8059-4d7b-af53-036f4b176351","ms":3}
20 | {"cmd":"click","el":"7904b135-8059-4d7b-af53-036f4b176351"} | {"ok":true,"result":"clicked","ms":58}
21 | {"cmd":"eval","js":"const c=document.querySelector(\"#contact-card-frank-sinatra\"); return {count:document.querySelector(\"#contacts-count\").textContent.trim(),cardCount:document.querySelectorAll(\"#contacts-list .contact-card\").length,modalDisplay:document.querySelector(\"#contact-modal\").style.display,frankName:c?c.querySelector(\".contact-name\").lastElementChild.textContent.trim():null,frankGroup:c?c.querySelector(\".badge\").textContent.trim():null,frankEmail:c?c.querySelector(\"#email-frank-sinatra\").textContent.trim():null,frankPhone:c?c.querySelector(\"#phone-frank-sinatra\").textContent.trim():null,frankNotes:c?c.querySelector(\".meta-line[style*=\\\"italic\\\"]\").textContent.trim():null}"} | {"ok":true,"result":{"cardCount":7,"count":"7","frankEmail":"frank.s@example.com","frankGroup":"Engineering","frankName":"Frank Sinatra","frankNotes":"Vocal Architect","frankPhone":"+1-555-0106","modalDisplay":"none"},"ms":2}
22 | {"cmd":"find","css":"#btn-edit-contact-bob-martin"} | {"ok":true,"result":"f3b4a6be-9ee4-4e25-8766-cb9c315f61d2","ms":1}
23 | {"cmd":"click","el":"f3b4a6be-9ee4-4e25-8766-cb9c315f61d2"} | {"ok":true,"result":"clicked","ms":54}
24 | {"cmd":"eval","js":"return {title:document.querySelector(\"#modal-title\").textContent.trim(),editId:document.querySelector(\"#edit-contact-id\").value,phone:document.querySelector(\"#input-contact-phone\").value,display:document.querySelector(\"#contact-modal\").style.display}"} | {"ok":true,"result":{"display":"flex","editId":"bob-martin","phone":"+1-555-0102","title":"Edit Contact"},"ms":2}
25 | {"cmd":"find","css":"#input-contact-phone"} | {"ok":true,"result":"701e61de-807a-4b09-8446-037b7c440fed","ms":1}
26 | {"cmd":"clear","el":"701e61de-807a-4b09-8446-037b7c440fed"} | {"ok":true,"result":"cleared","ms":3}
27 | {"cmd":"type","el":"701e61de-807a-4b09-8446-037b7c440fed","text":"+1-555-9999"} | {"ok":true,"result":"typed","ms":8}
28 | {"cmd":"find","css":"#btn-modal-save-contact"} | {"ok":true,"result":"7904b135-8059-4d7b-af53-036f4b176351","ms":2}
29 | {"cmd":"click","el":"7904b135-8059-4d7b-af53-036f4b176351"} | {"ok":true,"result":"clicked","ms":56}
30 | {"cmd":"eval","js":"return {count:document.querySelector(\"#contacts-count\").textContent.trim(),bobPhone:document.querySelector(\"#phone-bob-martin\")?document.querySelector(\"#phone-bob-martin\").textContent.trim():null,modalDisplay:document.querySelector(\"#contact-modal\").style.display}"} | {"ok":true,"result":{"bobPhone":"+1-555-9999","count":"7","modalDisplay":"none"},"ms":2}
31 | {"cmd":"click_js","js":"document.querySelector(\"#btn-fav-contact-david-kim\")"} | {"ok":true,"result":"clicked_js","ms":3}
32 | {"cmd":"eval","js":"const s=document.querySelector(\"#btn-fav-contact-david-kim\"); const c=document.querySelector(\"#contact-card-david-kim\"); return {starActive:s?s.classList.contains(\"active\"):false,cardFavorite:c?c.classList.contains(\"favorite\"):false,favoriteCards:document.querySelectorAll(\"#contacts-list .contact-card.favorite\").length,starClass:s?s.className:\"\"}"} | {"ok":true,"result":{"cardFavorite":true,"favoriteCards":1,"starActive":true,"starClass":"fav-star active is-favorite"},"ms":2}
33 | {"cmd":"find","css":"#btn-del-contact-spam-bot"} | {"ok":true,"result":"16bd2e09-7cb8-42b6-a31c-1a9a180d59bb","ms":2}
34 | {"cmd":"click","el":"16bd2e09-7cb8-42b6-a31c-1a9a180d59bb"} | {"ok":true,"result":"clicked","ms":56}
35 | {"cmd":"eval","js":"return {count:document.querySelector(\"#contacts-count\").textContent.trim(),cardCount:document.querySelectorAll(\"#contacts-list .contact-card\").length,spamCardPresent:document.querySelector(\"#contact-card-spam-bot\")!==null}"} | {"ok":true,"result":{"cardCount":6,"count":"6","spamCardPresent":false},"ms":3}
36 | {"cmd":"find","css":"#contact-search"} | {"ok":true,"result":"fa065146-e16e-4ac9-9bcc-6621c89c6460","ms":3}
37 | {"cmd":"type","el":"fa065146-e16e-4ac9-9bcc-6621c89c6460","text":"Kim"} | {"ok":true,"result":"typed","ms":5}
38 | {"cmd":"eval","js":"return {search:document.querySelector(\"#contact-search\").value,count:document.querySelector(\"#contacts-count\").textContent.trim(),cardCount:document.querySelectorAll(\"#contacts-list .contact-card\").length,names:Array.from(document.querySelectorAll(\"#contacts-list .contact-name\")).map(e=>e.lastElementChild.textContent.trim())}"} | {"ok":true,"result":{"cardCount":1,"count":"1","names":["David Kim"],"search":"Kim"},"ms":2}
39 | {"cmd":"find","css":"#contact-search"} | {"ok":true,"result":"fa065146-e16e-4ac9-9bcc-6621c89c6460","ms":1}
40 | {"cmd":"clear","el":"fa065146-e16e-4ac9-9bcc-6621c89c6460"} | {"ok":true,"result":"cleared","ms":2}
41 | {"cmd":"eval","js":"const e=document.querySelector(\"#contact-search\"); e.dispatchEvent(new Event(\"input\",{bubbles:true})); return {search:e.value,count:document.querySelector(\"#contacts-count\").textContent.trim(),cardCount:document.querySelectorAll(\"#contacts-list .contact-card\").length,names:Array.from(document.querySelectorAll(\"#contacts-list .contact-name\")).map(x=>x.lastElementChild.textContent.trim())}"} | {"ok":true,"result":{"cardCount":6,"count":"6","names":["Alice Chen","Bob Martin","Clara Vance","David Kim","Eva Rostova","Frank Sinatra"],"search":""},"ms":4}
42 | {"cmd":"eval","js":"const e=document.querySelector(\"#filter-contact-group\"); e.value=\"Engineering\"; e.dispatchEvent(new Event(\"change\",{bubbles:true})); return e.value"} | {"ok":true,"result":"Engineering","ms":3}
43 | {"cmd":"eval","js":"return {group:document.querySelector(\"#filter-contact-group\").value,count:document.querySelector(\"#contacts-count\").textContent.trim(),cardCount:document.querySelectorAll(\"#contacts-list .contact-card\").length,names:Array.from(document.querySelectorAll(\"#contacts-list .contact-name\")).map(e=>e.lastElementChild.textContent.trim())}"} | {"ok":true,"result":{"cardCount":3,"count":"3","group":"Engineering","names":["Alice Chen","David Kim","Frank Sinatra"]},"ms":2}
44 | {"cmd":"eval","js":"const e=document.querySelector(\"#filter-contact-group\"); e.value=\"all\"; e.dispatchEvent(new Event(\"change\",{bubbles:true})); return e.value"} | {"ok":true,"result":"all","ms":7}
45 | {"cmd":"eval","js":"return {search:document.querySelector(\"#contact-search\").value,group:document.querySelector(\"#filter-contact-group\").value,count:document.querySelector(\"#contacts-count\").textContent.trim(),cardCount:document.querySelectorAll(\"#contacts-list .contact-card\").length,names:Array.from(document.querySelectorAll(\"#contacts-list .contact-name\")).map(e=>e.lastElementChild.textContent.trim())}"} | {"ok":true,"result":{"cardCount":6,"count":"6","group":"all","names":["Alice Chen","Bob Martin","Clara Vance","David Kim","Eva Rostova","Frank Sinatra"],"search":""},"ms":2}
46 | {"cmd":"find","css":"#btn-save-directory"} | {"ok":true,"result":"f72ad7cf-3e93-4268-9fbb-5b6407a36b0b","ms":2}
47 | {"cmd":"click","el":"f72ad7cf-3e93-4268-9fbb-5b6407a36b0b"} | {"ok":true,"result":"clicked","ms":54}
48 | {"cmd":"text","css":"#contact-status-banner"} | {"ok":true,"result":"Directory saved: 6 contacts (1 favorite)","ms":2}
49 | {"cmd":"text","css":"#contacts-count"} | {"ok":true,"result":"6","ms":2}
50 | {"cmd":"value","css":"#contact-search"} | {"ok":true,"result":"","ms":2}
51 | {"cmd":"value","css":"#filter-contact-group"} | {"ok":true,"result":"all","ms":2}
52 | {"cmd":"text","css":"#phone-bob-martin"} | {"ok":true,"result":"+1-555-9999","ms":2}
53 | {"cmd":"eval","js":"const s=document.querySelector(\"#btn-fav-contact-david-kim\"); const c=document.querySelector(\"#contact-card-david-kim\"); return {starActive:s?s.classList.contains(\"active\"):false,cardFavorite:c?c.classList.contains(\"favorite\"):false}"} | {"ok":true,"result":{"cardFavorite":true,"starActive":true},"ms":2}
54 | {"cmd":"eval","js":"return {cardPresent:document.querySelector(\"#contact-card-spam-bot\")!==null,namePresent:Array.from(document.querySelectorAll(\"#contacts-list .contact-name\")).some(e=>e.lastElementChild.textContent.includes(\"Spam Bot\"))}"} | {"ok":true,"result":{"cardPresent":false,"namePresent":false},"ms":2}
55 | {"cmd":"eval","js":"const c=document.querySelector(\"#contact-card-frank-sinatra\"); return {cardPresent:!!c,name:c?c.querySelector(\".contact-name\").lastElementChild.textContent.trim():null,group:c?c.querySelector(\".badge\").textContent.trim():null,email:c?c.querySelector(\"#email-frank-sinatra\").textContent.trim():null,phone:c?c.querySelector(\"#phone-frank-sinatra\").textContent.trim():null,notes:c?c.querySelector(\".meta-line[style*=\\\"italic\\\"]\").textContent.trim():null}"} | {"ok":true,"result":{"cardPresent":true,"email":"frank.s@example.com","group":"Engineering","name":"Frank Sinatra","notes":"Vocal Architect","phone":"+1-555-0106"},"ms":2}
56 | {"cmd":"eval","js":"return window.__agyVerify()"} | {"ok":true,"result":{"failures":[],"passed":true,"score":1,"state":{"banner":"Directory saved: 6 contacts (1 favorite)","bobPhone":"+1-555-9999","contactCount":6,"favCount":1,"saved":true}},"ms":2} | PASS verifier
57 | {"cmd":"close_tab"} | {"ok":true,"result":"closed","ms":37} | Closed executor tab
58 | {"cmd":"delete_session"} | {"ok":true,"result":"deleted","ms":2}

End time: 2026-11-21 20:15:27 +07
Plan steps run: 58/58, plus required visibility diagnosis after step 2
Total driver commands: 59
Errors: none
Misclicks: none
PLAN DEFECTS: none
Final evidence: banner=Directory saved: 6 contacts (1 favorite); count=6; search=empty; group=all; Bob phone=+1-555-9999; David star active and card favorite=true; Spam Bot absent; Frank present with Engineering, frank.s@example.com, +1-555-0106, notes=Vocal Architect; __agyVerify={passed:true,failures:[],score:1,state:{saved:true,contactCount:6,favCount:1,bobPhone:+1-555-9999,banner:Directory saved: 6 contacts (1 favorite)}}
Result: PASS
