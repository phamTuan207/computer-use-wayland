# S2 flip P9 screenshot manifest

- Purpose: committed render evidence for the P9 screenshot check that the CB-8 audit (docs/batch12-task3-cb8-audit-20261122.md on main) found missing. The audit REVOKED two DONE claims, (a) S2 flip reopen PASS and (b) (b1) 5/5 on Chromium, for one reason only: the P9 PNGs were not in the repo. The numbers in both claims were verified correct from the raw JSONs. This manifest lists every P9 PNG committed here, with its sha256, run and browser, privacy disposition, and what the frame actually shows.
- Auditor note: the run JSONs carry p9 as null, so they do not name the PNG paths. The PNGs below sit at exactly the paths the audit lists in its repair list, which is the filename convention the capture step used.
- Privacy method: every PNG below was viewed in full before commit. All 25 are window captures of the clone1 or clone2 test threads in the Muse app. The left rail is collapsed to icons in every shot, so no other chat names appear. The right panel shows the clone's own profile (plush avatar) and its own scheduled tasks or approvals history, which is agent work product already in the repo logs. The clone2 shots also show clone2's own usage limit notice (weekly reset 2:38 AM Wednesday, November 25), which is clone2's own account status already on the record. The clone1 shots show clone1's own status messages about batch 10, batch 11, sweep work, and the S2 flip runs, which are already in the repo docs. No personal photos, no other chats, no owner personal data appear in any shot. Disposition for all 25 is cleared as-is. No file was cropped and none was excluded.
- No em dash or en dash anywhere in this file.

## Focusenter helper

The file improvements/s2-flip-b1-runs/c5-focusenter.mjs is the focus plus Enter helper from the (b1) measurement, copied verbatim from the laptop at /tmp/c5-focusenter.mjs on 2026-11-22 at 14:10 +07, and it is not landed code. It is evidence only, so the Enter mechanism in claim (b) is reviewable from the branch, which closes the audit's secondary gap. It was still present on the laptop when checked, it was not lost. The copy is byte identical to the laptop file: 2478 bytes, sha256 94ee467ed3067e044491ad19153c24b73d574a8106a5367db454c0e47e1a695f, 42 lines. It focuses textarea[aria-label="Message"], asserts it is document.activeElement, then sends Input.dispatchKeyEvent keyDown plus keyUp Enter, with no mouse event, no click, and no typing.

## (b1) runs: improvements/s2-flip-b1-runs, Chromium only

| File | Size (bytes) | sha256 | Run and browser | Privacy disposition | What the frame shows |
|---|---|---|---|---|---|
| p9-run1-chromium.png | 240188 | f6db565115efd225f6d019e483857a8a577935fc1b76473f373a8ca854467240 | (b1) run 1, Chromium | cleared as-is | Bubble C5-B1-R1-CHROMIUM-IGNORE-TEST visible, composer empty |
| p9-run2-chromium.png | 247301 | fabd60f6a1c965b5d3a4e5064aa554f68b57ca5ca2eaea30c7f9c4142ac9f9b9 | (b1) run 2, Chromium | cleared as-is | Bubbles C5-B1-R1 and C5-B1-R2 visible, composer empty |
| p9-run3-chromium.png | 238934 | 6e180ac709bbcb72dbd54ef47d6c0add77580dfa1cad8ce427aa18ef772cbcc5 | (b1) run 3, Chromium | cleared as-is | Bubbles C5-B1-R1, R2, R3 visible, composer empty |
| p9-run4-chromium.png | 241703 | a7277c6726f17d62ce8d5534e05aa34aa9351a571ba421001cc3e1591a677be3 | (b1) run 4, Chromium | cleared as-is | Bubbles C5-B1-R1, R2, R3, R4 visible, composer empty |
| p9-run5-chromium.png | 242479 | ab5498a18ab9a68058d346241795eb82816cd1faf0c36974e7825847588f8209 | (b1) run 5, Chromium | cleared as-is | Bubbles C5-B1-R2, R3, R4, R5 visible, composer empty |

Subtotal: 5 PNGs, 1210605 bytes. JSON outcome for all 5 is sent, which matches the visible bubbles.

## Reopen runs: improvements/s2-flip-reopen-runs, Brave and Chromium

| File | Size (bytes) | sha256 | Run and browser | Privacy disposition | What the frame shows |
|---|---|---|---|---|---|
| p9-run1-brave.png | 238402 | eb779f2c25432acf395bb65d8d6f898c3143d37a5541194828e73fae41ea43ff | reopen run 1, Brave | cleared as-is | Bubble S2-REOPEN-R1-BRAVE-IGNORE-TEST visible, composer empty |
| p9-run1-chromium.png | 239767 | bd0691daa4b58b2cb8459e265d2a3bd1adc76324cf1552aed31c759e40093beb | reopen run 1, Chromium | cleared as-is | Bubble S2-REOPEN-R1-CHROMIUM-IGNORE-TEST visible, composer empty |
| p9-run2-brave.png | 238926 | c143bbc2fcd6851903b62a8e64866eccd5c9a32947ac74fab4cb3f4425de02ca | reopen run 2, Brave | cleared as-is | Bubbles S2-REOPEN-R1 and R2 Brave visible, composer empty |
| p9-run2-chromium.png | 238771 | c204fac53b8e49fd2ebc58d839ef23cbd87167d61968188137c66d48a999fb2c | reopen run 2, Chromium | cleared as-is | Bubbles S2-REOPEN-R1 and R2 Chromium visible, composer empty |
| p9-run3-brave.png | 240074 | 495955cb99ea152be343b9964db75cbc72d2736883c758d3fb4b010b084b7b05 | reopen run 3, Brave | cleared as-is | Bubbles S2-REOPEN-R1, R2, R3 Brave visible, composer empty |
| p9-run3-chromium.png | 239223 | 4afc257126d57414c19344f028a4725619fe1abe23ea1060dbbc9a6fa6725ad2 | reopen run 3, Chromium | cleared as-is | Bubbles S2-REOPEN-R1, R2, R3 Chromium visible, composer empty |
| p9-run4-brave.png | 223638 | cc10717a62e756e98efc28af3cbeb41c7d90bac2c60843b6cfc026a92a5655fc | reopen run 4, Brave | cleared as-is | Bubbles S2-REOPEN-R1, R2, R3, R4 Brave visible, composer empty |
| p9-run4-chromium.png | 240380 | aa514581e3540f5c1dcfb70517c69af047088b70287b0d28f6796aaa9f4401eb | reopen run 4, Chromium | cleared as-is | Bubbles S2-REOPEN-R2, R3, R4 Chromium visible, composer empty |
| p9-run5-brave.png | 215341 | 0230307c6df5a3dfe364e2b3b2602e38baf734941654c45348057008096c6096 | reopen run 5, Brave | cleared as-is | Bubbles S2-REOPEN-R1, R2, R3, R4, R5 Brave visible, composer empty |
| p9-run5-chromium.png | 240415 | 68efc47d78d44e1021900b2c787f7911f23a2ed35d756f9e0a89ca29b2ab64da | reopen run 5, Chromium | cleared as-is | Bubbles S2-REOPEN-R2, R3, R4, R5 Chromium visible, composer empty |

Subtotal: 10 PNGs, 2354937 bytes. JSON outcome for all 10 is sent, which matches the visible bubbles.

## Original flip runs: improvements/s2-flip-runs, Brave and Chromium

| File | Size (bytes) | sha256 | Run and browser | Privacy disposition | What the frame shows |
|---|---|---|---|---|---|
| p9-run1-brave.png | 259014 | 1465d28013fed9c33130910f9388cb9a93ab203769481bb6e3fd2d195cb3e8fe | flip run 1, Brave | cleared as-is | Bubble S2-FLIP-R1-BRAVE-IGNORE-TEST visible, composer empty |
| p9-run1-chromium.png | 306802 | 224351c2e6348691a4cc9ed3832c1b070f408ff87e3231672880fe27057988d8 | flip run 1, Chromium | cleared as-is | NO test bubble visible. Frame shows the clone2 thread at an earlier scroll position (batch 9 messages, 5:47 AM approval). Consistent with the JSON: Chromium outcome failed-unverified, so no bubble was ever rendered |
| p9-run2-brave.png | 231189 | d87d5140d3de80b99c221c2a3f937911159cc5421a4259d87a862601b9cea14c | flip run 2, Brave | cleared as-is | Bubbles S2-FLIP-R1 and R2 Brave visible, composer empty |
| p9-run2-chromium.png | 306774 | 4ca497ea3dd9f6bfea41f23d2764687c8fc8a08400af233eac1fe4ff455cd921 | flip run 2, Chromium | cleared as-is | NO test bubble visible. Same earlier scroll position as run 1 Chromium. Consistent with the JSON: Chromium outcome failed-unverified |
| p9-run3-brave.png | 233318 | e7f1d7e59ad78a0734f3381ae71cf34d7cfa6a22ada98bd4b9989756e431910c | flip run 3, Brave | cleared as-is | Bubbles S2-FLIP-R2 and R3 Brave visible, composer empty |
| p9-run3-chromium.png | 306781 | 958de889edf17cfc5b4663cd18d53fb80ccda58b7d481808cb58be84fe9991a6 | flip run 3, Chromium | cleared as-is | NO test bubble visible. Same earlier scroll position as run 1 Chromium. Consistent with the JSON: Chromium outcome failed-unverified |
| p9-run4-brave.png | 234423 | 037d9204d3c3ff4f898841a74a0ab3397fcbfbb6e56f197c2d1c90f744524493 | flip run 4, Brave | cleared as-is | Bubbles S2-FLIP-R2, R3, R4 Brave visible, composer empty |
| p9-run4-chromium.png | 307207 | 38d7836eb4761731e70b995bfbea5368dd0305b3eb8cc975ab19d407e377b256 | flip run 4, Chromium | cleared as-is | NO test bubble visible. Same earlier scroll position as run 1 Chromium. Consistent with the JSON: Chromium outcome failed-unverified |
| p9-run5-brave.png | 247898 | 587f1c8aa1761f416df9b096ac709719ac6b47acf2b6b2eedffaface3491dae7 | flip run 5, Brave | cleared as-is | Bubbles S2-FLIP-R3, R4, R5 Brave visible, composer empty |
| p9-run5-chromium.png | 307082 | 651a7db0b58443e1313e9a0190a556662f043cd2590203b12d8a472045618d67 | flip run 5, Chromium | cleared as-is | NO test bubble visible. Same earlier scroll position as run 1 Chromium. Consistent with the JSON: Chromium outcome failed-unverified |

Subtotal: 10 PNGs, 2740488 bytes. The Chromium half of the original flip failed in all 5 runs (JSON outcome failed-unverified; clone1's own messages in the Brave frames say Input.dispatchMouseEvent timed out at 5003 ms in run 1 and 5002 ms in run 2, and the same failure repeated in runs 3 to 5). The 5 Chromium PNGs are committed as the true capture files, not as proof of a Chromium send. They are evidence that no Chromium bubble was rendered, which agrees with the JSONs. The 5 Brave PNGs show the sent bubbles and match their JSON outcome sent.

## Totals

- Mandated 15 PNGs (5 (b1) plus 10 reopen): 3565542 bytes, about 3.6 MB, as briefed.
- Original flip 10 PNGs: 2740488 bytes, about 2.7 MB.
- All 25 PNGs: 6306030 bytes, about 6.3 MB.
- Focusenter helper: 2478 bytes.
- Excluded: none. Cropped: none.
