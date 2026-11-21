# E1 merged plan, test-05 contact book (DELIBERATED condition)

Executor runs each JSON object below as one call to `/tmp/e1/step.sh '<json>'`. The driver and fixture server are already running when the executor works. Use only the new tab opened in step 2; do not switch to or close any other tab. After a `find`, substitute the returned element id wherever a later step says `<element id from step N>`.

## How this plan was made (merge note)

Three deliberators worked in parallel from the same brief and produced three drafts: draft-1 (68 steps, Vietnamese), draft-2 (62 steps, Vietnamese), draft-3 (58 steps, English). All three reported zero UNVERIFIED selectors. This file is the merge, done by the coordinator from the drafts only, with every contested point resolved against the fixture HTML:

- Base skeleton: draft-3 (58 steps), the most complete check sequence.
- Name reads use `.contact-name` lastElementChild (draft-1 method). The render template puts the star span first and the name span last inside `.contact-name`, so lastElementChild is the name text exactly, with no string surgery on the star character.
- Frank card checks also verify notes "Vocal Architect" (draft-1), read through `.meta-line[style*="italic"]`.
- Star checks use classList.contains plus the exact class string (draft-1 exact string "fav-star active is-favorite" combined with draft-2/3 contains checks).
- After clearing the search input, the plan explicitly dispatches an `input` event (draft-3). Draft-1 and draft-2 assumed Marionette `clear` fires the input event; the explicit dispatch works whether or not it does, so it wins.
- Draft-1 extra step (clear search before typing Kim) dropped: the search starts empty in a fresh tab, and draft-2/3 do not have it. Majority 2-1 plus redundancy.
- Re-find of the phone input after `clear` (draft-2 step 28) dropped: `clear` does not re-render the modal, so the element id stays valid. Draft-1/3 reuse it. Majority 2-1.
- Modal-still-open policy: record the failure and continue (draft-3, as the brief specified). Draft-1 (skip to final verification) and draft-2 (skip to cleanup) lose information; the brief rule is continue-through.
- Bob preloaded phone check kept (draft-3): the edit modal preloads "+1-555-0102", verified in the fixture contacts array. Modal title checks kept (draft-3): "Add New Contact" and "Edit Contact", verified in openNewModal/openEditModal.
- All three drafts agree: star is a span, use click_js directly; delete has no confirmation; select set by JS value plus change event; search filters live on input, group filter on change, "all" resets; banner exact text; final __agyVerify check; cleanup closes only the executor tab.

## Fixture facts used by this plan (all verified in the fixture HTML)

- The fixture script initializes six contacts and calls renderGrid() on load. That render replaces the static count placeholder (5) with the real initial count, 6.
- Rendered ids use each contact id: Alice alice-chen, Bob bob-martin, Clara clara-vance, David david-kim, Eva eva-rostova, Spam Bot spam-bot. New "Frank Sinatra" is slugified to frank-sinatra.
- Card markup: id contact-card-{id}; `.contact-name` holds the star span then the name span; `.badge` holds the group; `#email-{id}` and `#phone-{id}` hold email and phone; notes render as `.meta-line` with style containing "font-style: italic".
- Bob original phone is +1-555-0102, group Design. David original phone +1-555-0104, group Engineering. Alice is Engineering, so the Engineering filter yields Alice, David, Frank.
- Add opens #contact-modal with display flex and title "Add New Contact"; the modal Save button writes the record, hides the modal (display none), and re-renders. Modal fields: #input-contact-first, #input-contact-last, #input-contact-email, #input-contact-phone, #select-contact-group, #input-contact-notes. The department field is a select; its option values are Engineering, Design, Product, Operations. The new-contact flow defaults to Engineering, but step 16 sets it explicitly.
- Bob Edit opens the same modal with title "Edit Contact", edit-contact-id "bob-martin", and all fields preloaded. Saving also hides the modal and re-renders, so all later contact selectors are freshly found.
- The favorite is a small span.fav-star, not a button. Its click listener toggles favorite and re-renders. Use click_js directly for this tiny target; static HTML cannot establish whether a real Marionette click will be interactable at runtime.
- Delete immediately removes the contact and re-renders. There is no confirmation dialog or confirm button.
- Search filters live on the input event by full name or email, case-insensitive. The group filter re-renders on change; "all" means all groups. The count indicator shows the FILTERED count, so a search for Kim shows count 1.
- Saving sets the banner to exactly "Directory saved: 6 contacts (1 favorite)" for the required final state.

## Check and error rules

- Each check step below gives its exact expected result. If a successful read differs, find the checked element again with the selector in that read, then repeat the same read once (for an eval, repeat its fresh querySelector read once). If it still differs, record the step number and actual result as a failure and continue with the next listed step. Do not claim success from an attempted action.
- On any {"ok": false}: record the step and error. Retry that same command once; for clear, type, or click, first run find again with that step exact selector and use the newly returned element id. If a real click still fails, try click_js with the exact selector given at that step. If that fallback fails, record it and continue. For a failed find, retry the same find; for eval, text, or value, retry the same command (the selectors in eval are freshly queried). Do not invent a success.
- If a check remains wrong after its one read retry, record the failure and continue through the plan so final verification and cleanup still happen. A PASS requires all final reads and window.__agyVerify() to match the expected values.

## Exact step order

1. Start the driver session: `{"cmd":"new_session"}`
2. Open only the fixture in a new tab: `{"cmd":"new_tab","url":"http://127.0.0.1:8767/test-05-contact-book.html"}`
3. Clear local storage as a precaution; expected result: `0`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"localStorage.clear(); return localStorage.length"}`
4. Check initial render; expected result: `{"count":"6","cardCount":6,"ids":["contact-card-alice-chen","contact-card-bob-martin","contact-card-clara-vance","contact-card-david-kim","contact-card-eva-rostova","contact-card-spam-bot"],"names":["Alice Chen","Bob Martin","Clara Vance","David Kim","Eva Rostova","Spam Bot"]}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"return {count:document.querySelector('#contacts-count').textContent.trim(),cardCount:document.querySelectorAll('#contacts-list .contact-card').length,ids:Array.from(document.querySelectorAll('#contacts-list .contact-card')).map(c=>c.id),names:Array.from(document.querySelectorAll('#contacts-list .contact-name')).map(e=>e.lastElementChild.textContent.trim())}"}`
5. Find Add Contact: `{"cmd":"find","css":"#btn-new-contact"}`
6. Open the modal: `{"cmd":"click","el":"<element id from step 5>"}`. If the click retry fails, fallback: `{"cmd":"click_js","js":"document.querySelector('#btn-new-contact')"}`
7. Check modal opened; expected result: `{"display":"flex","title":"Add New Contact"}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"return {display:document.querySelector('#contact-modal').style.display,title:document.querySelector('#modal-title').textContent.trim()}"}`
8. Find first-name input: `{"cmd":"find","css":"#input-contact-first"}`
9. Type `Frank`: `{"cmd":"type","el":"<element id from step 8>","text":"Frank"}`
10. Find last-name input: `{"cmd":"find","css":"#input-contact-last"}`
11. Type `Sinatra`: `{"cmd":"type","el":"<element id from step 10>","text":"Sinatra"}`
12. Find email input: `{"cmd":"find","css":"#input-contact-email"}`
13. Type `frank.s@example.com`: `{"cmd":"type","el":"<element id from step 12>","text":"frank.s@example.com"}`
14. Find phone input: `{"cmd":"find","css":"#input-contact-phone"}`
15. Type `+1-555-0106`: `{"cmd":"type","el":"<element id from step 14>","text":"+1-555-0106"}`
16. Set the modal department select by value and dispatch `change`; expected result: `Engineering`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"const e=document.querySelector('#select-contact-group'); e.value='Engineering'; e.dispatchEvent(new Event('change',{bubbles:true})); return e.value"}`
17. Find notes input: `{"cmd":"find","css":"#input-contact-notes"}`
18. Type `Vocal Architect`: `{"cmd":"type","el":"<element id from step 17>","text":"Vocal Architect"}`
19. Find modal Save Contact button: `{"cmd":"find","css":"#btn-modal-save-contact"}`
20. Save Frank: `{"cmd":"click","el":"<element id from step 19>"}`. If the click retry fails, fallback: `{"cmd":"click_js","js":"document.querySelector('#btn-modal-save-contact')"}`
21. Check add/save and the new card; expected result: `{"count":"7","cardCount":7,"modalDisplay":"none","frankName":"Frank Sinatra","frankGroup":"Engineering","frankEmail":"frank.s@example.com","frankPhone":"+1-555-0106","frankNotes":"Vocal Architect"}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"const c=document.querySelector('#contact-card-frank-sinatra'); return {count:document.querySelector('#contacts-count').textContent.trim(),cardCount:document.querySelectorAll('#contacts-list .contact-card').length,modalDisplay:document.querySelector('#contact-modal').style.display,frankName:c?c.querySelector('.contact-name').lastElementChild.textContent.trim():null,frankGroup:c?c.querySelector('.badge').textContent.trim():null,frankEmail:c?c.querySelector('#email-frank-sinatra').textContent.trim():null,frankPhone:c?c.querySelector('#phone-frank-sinatra').textContent.trim():null,frankNotes:c?c.querySelector('.meta-line[style*=\"italic\"]').textContent.trim():null}"}`
22. Find Bob Edit button: `{"cmd":"find","css":"#btn-edit-contact-bob-martin"}`
23. Open Bob edit modal: `{"cmd":"click","el":"<element id from step 22>"}`. If the click retry fails, fallback: `{"cmd":"click_js","js":"document.querySelector('#btn-edit-contact-bob-martin')"}`
24. Check Bob modal and preloaded phone; expected result: `{"title":"Edit Contact","editId":"bob-martin","phone":"+1-555-0102","display":"flex"}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"return {title:document.querySelector('#modal-title').textContent.trim(),editId:document.querySelector('#edit-contact-id').value,phone:document.querySelector('#input-contact-phone').value,display:document.querySelector('#contact-modal').style.display}"}`
25. Find the phone input again inside Bob modal: `{"cmd":"find","css":"#input-contact-phone"}`
26. Clear Bob current phone: `{"cmd":"clear","el":"<element id from step 25>"}`
27. Type `+1-555-9999` into the same still-open input: `{"cmd":"type","el":"<element id from step 25>","text":"+1-555-9999"}`
28. Find modal Save Contact button again: `{"cmd":"find","css":"#btn-modal-save-contact"}`
29. Save Bob: `{"cmd":"click","el":"<element id from step 28>"}`. If the click retry fails, fallback: `{"cmd":"click_js","js":"document.querySelector('#btn-modal-save-contact')"}`
30. Check Bob saved phone and modal close; expected result: `{"count":"7","bobPhone":"+1-555-9999","modalDisplay":"none"}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"return {count:document.querySelector('#contacts-count').textContent.trim(),bobPhone:document.querySelector('#phone-bob-martin')?document.querySelector('#phone-bob-martin').textContent.trim():null,modalDisplay:document.querySelector('#contact-modal').style.display}"}`
31. Toggle David small star using the safer JS click: `{"cmd":"click_js","js":"document.querySelector('#btn-fav-contact-david-kim')"}`
32. Check star and card favorite state; expected result: `{"starActive":true,"cardFavorite":true,"favoriteCards":1,"starClass":"fav-star active is-favorite"}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"const s=document.querySelector('#btn-fav-contact-david-kim'); const c=document.querySelector('#contact-card-david-kim'); return {starActive:s?s.classList.contains('active'):false,cardFavorite:c?c.classList.contains('favorite'):false,favoriteCards:document.querySelectorAll('#contacts-list .contact-card.favorite').length,starClass:s?s.className:''}"}`
33. Find Spam Bot Delete button: `{"cmd":"find","css":"#btn-del-contact-spam-bot"}`
34. Delete Spam Bot (the fixture has no confirmation): `{"cmd":"click","el":"<element id from step 33>"}`. If the click retry fails, fallback: `{"cmd":"click_js","js":"document.querySelector('#btn-del-contact-spam-bot')"}`
35. Check delete and re-render; expected result: `{"count":"6","cardCount":6,"spamCardPresent":false}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"return {count:document.querySelector('#contacts-count').textContent.trim(),cardCount:document.querySelectorAll('#contacts-list .contact-card').length,spamCardPresent:document.querySelector('#contact-card-spam-bot')!==null}"}`
36. Find search input: `{"cmd":"find","css":"#contact-search"}`
37. Type `Kim` (the input listener filters live): `{"cmd":"type","el":"<element id from step 36>","text":"Kim"}`
38. Check live search; expected result: `{"search":"Kim","count":"1","cardCount":1,"names":["David Kim"]}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"return {search:document.querySelector('#contact-search').value,count:document.querySelector('#contacts-count').textContent.trim(),cardCount:document.querySelectorAll('#contacts-list .contact-card').length,names:Array.from(document.querySelectorAll('#contacts-list .contact-name')).map(e=>e.lastElementChild.textContent.trim())}"}`
39. Find search input again: `{"cmd":"find","css":"#contact-search"}`
40. Clear the search string: `{"cmd":"clear","el":"<element id from step 39>"}`
41. Dispatch the live-search event after clear and check that all remaining contacts show; expected result: `{"search":"","count":"6","cardCount":6,"names":["Alice Chen","Bob Martin","Clara Vance","David Kim","Eva Rostova","Frank Sinatra"]}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"const e=document.querySelector('#contact-search'); e.dispatchEvent(new Event('input',{bubbles:true})); return {search:e.value,count:document.querySelector('#contacts-count').textContent.trim(),cardCount:document.querySelectorAll('#contacts-list .contact-card').length,names:Array.from(document.querySelectorAll('#contacts-list .contact-name')).map(x=>x.lastElementChild.textContent.trim())}"}`
42. Set the group filter to Engineering and dispatch `change`; expected result: `Engineering`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"const e=document.querySelector('#filter-contact-group'); e.value='Engineering'; e.dispatchEvent(new Event('change',{bubbles:true})); return e.value"}`
43. Check Engineering filter; expected result: `{"group":"Engineering","count":"3","cardCount":3,"names":["Alice Chen","David Kim","Frank Sinatra"]}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"return {group:document.querySelector('#filter-contact-group').value,count:document.querySelector('#contacts-count').textContent.trim(),cardCount:document.querySelectorAll('#contacts-list .contact-card').length,names:Array.from(document.querySelectorAll('#contacts-list .contact-name')).map(e=>e.lastElementChild.textContent.trim())}"}`
44. Reset the group filter to `all` and dispatch `change`; expected result: `all`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"const e=document.querySelector('#filter-contact-group'); e.value='all'; e.dispatchEvent(new Event('change',{bubbles:true})); return e.value"}`
45. Check filters reset and all six remaining contacts show; expected result: `{"search":"","group":"all","count":"6","cardCount":6,"names":["Alice Chen","Bob Martin","Clara Vance","David Kim","Eva Rostova","Frank Sinatra"]}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"return {search:document.querySelector('#contact-search').value,group:document.querySelector('#filter-contact-group').value,count:document.querySelector('#contacts-count').textContent.trim(),cardCount:document.querySelectorAll('#contacts-list .contact-card').length,names:Array.from(document.querySelectorAll('#contacts-list .contact-name')).map(e=>e.lastElementChild.textContent.trim())}"}`
46. Find Save Directory: `{"cmd":"find","css":"#btn-save-directory"}`
47. Save the directory: `{"cmd":"click","el":"<element id from step 46>"}`. If the click retry fails, fallback: `{"cmd":"click_js","js":"document.querySelector('#btn-save-directory')"}`
48. Final banner read; expected exact text: `Directory saved: 6 contacts (1 favorite)`. If different, apply the check retry rule, then record and continue: `{"cmd":"text","css":"#contact-status-banner"}`
49. Final visible count read; expected exact text: `6`. If different, apply the check retry rule, then record and continue: `{"cmd":"text","css":"#contacts-count"}`
50. Final search value read; expected exact value: empty string `""`. If different, apply the check retry rule, then record and continue: `{"cmd":"value","css":"#contact-search"}`
51. Final group value read; expected exact value: `all`. If different, apply the check retry rule, then record and continue: `{"cmd":"value","css":"#filter-contact-group"}`
52. Final Bob phone read; expected exact text: `+1-555-9999`. If different, apply the check retry rule, then record and continue: `{"cmd":"text","css":"#phone-bob-martin"}`
53. Final David favorite DOM read; expected result: `{"starActive":true,"cardFavorite":true}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"const s=document.querySelector('#btn-fav-contact-david-kim'); const c=document.querySelector('#contact-card-david-kim'); return {starActive:s?s.classList.contains('active'):false,cardFavorite:c?c.classList.contains('favorite'):false}"}`
54. Final Spam Bot absence read; expected result: `{"cardPresent":false,"namePresent":false}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"return {cardPresent:document.querySelector('#contact-card-spam-bot')!==null,namePresent:Array.from(document.querySelectorAll('#contacts-list .contact-name')).some(e=>e.lastElementChild.textContent.includes('Spam Bot'))}"}`
55. Final Frank DOM read; expected result: `{"cardPresent":true,"name":"Frank Sinatra","group":"Engineering","email":"frank.s@example.com","phone":"+1-555-0106","notes":"Vocal Architect"}`. If different, apply the check retry rule, then record and continue: `{"cmd":"eval","js":"const c=document.querySelector('#contact-card-frank-sinatra'); return {cardPresent:!!c,name:c?c.querySelector('.contact-name').lastElementChild.textContent.trim():null,group:c?c.querySelector('.badge').textContent.trim():null,email:c?c.querySelector('#email-frank-sinatra').textContent.trim():null,phone:c?c.querySelector('#phone-frank-sinatra').textContent.trim():null,notes:c?c.querySelector('.meta-line[style*=\"italic\"]').textContent.trim():null}"}`
56. Run the fixture final verifier; exact command: `{"cmd":"eval","js":"return window.__agyVerify()"}`. Read the returned JSON under the driver `result` field. PASS requires `passed: true`, `failures: []`, `score: 1`, and `state` equal to `{"saved":true,"contactCount":6,"favCount":1,"bobPhone":"+1-555-9999","banner":"Directory saved: 6 contacts (1 favorite)"}`. If any field differs, apply the check retry rule once, record the returned JSON, and continue to cleanup.
57. Close ONLY the current tab opened in step 2: `{"cmd":"close_tab"}`
58. Delete the WebDriver session: `{"cmd":"delete_session"}`

## Risks and countermeasures in the step order

- Modal left open or wrong modal: steps 7, 21, 24, and 30 read its display/title/edit id; add/edit fields are completed before the matching Save click. Save should hide it. Record any mismatch and continue.
- Stale element ids after re-render: after add, Bob save, favorite toggle, delete, and filter changes, later interactive controls are obtained by fresh `find` calls. No old card/button element id is reused after a re-render.
- Tiny favorite target / click miss: step 31 uses `click_js` on the verified span selector and step 32 checks both active star and favorite card classes.
- Delete behavior: no confirmation exists in the fixture; step 34 clicks the exact Spam Bot delete button once, and step 35 verifies the card is absent and count is six.
- Search or group filter left active: step 40 clears search and step 41 dispatches `input`; step 44 sets group to `all` and dispatches `change`; step 45 and final steps 50-51 verify both controls are reset before saving.
- Wrong element or unexpected count: all selectors below were checked against fixture markup or its render template. Contact action ids resolve from the explicit fixture contact ids listed above. Count/name checks after each state change catch a wrong match before final verification.
- Save state not persisted: step 48 checks the exact success banner, and step 56 checks the fixture `saved` state, final totals, favorite, Bob phone, Frank, and Spam Bot removal.

## Selector verification

All selectors and generated ids used above are present in the fixture markup or are produced by its renderGrid() template using the confirmed contact ids. No selector is unverified. (All three deliberators independently reported zero UNVERIFIED selectors.)
