# Scorer 1 grade, R3-L3, R3-008

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-008 (Tier B, position 8, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-25 22:12:47 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-008-L3/ at todolist-push commit 1f2adfad, manifest_sha256 54b2a3f9da0c9e7251a1a3788bf501d79b5c5945fc6bc65774440d8145dc8f78, all 6 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-008-L3/manifest.json (snapshot R3-008-L3, commit 1f2adfad)
- rung3-run-log/rung3-snapshots/R3-008-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-008-L3/20261125-220227-tts.png
- rung3-run-log/rung3-snapshots/R3-008-L3/am-thanh-1.mp3
- rung3-run-log/rung3-snapshots/R3-008-L3/am-thanh-2.mp3
- rung3-run-log/rung3-snapshots/R3-008-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-008-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-008 section only (lines 185-197)
- docs/rung3-answer-keys.json, R3-008 entry only (para1_words 80, para2_words 120, voices Joanna/Matthew)
- docs/rung3-list-100-tasks.md, section 6, R3-008 task text only

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I did not re-run any text-to-speech generation.

## Key (R3-008, Tier B)

Voices: paragraph 1 Joanna, paragraph 2 Matthew, both Regular US English voices on ttsmp3.com. Free limit 3000 characters/day, not used at the prep step. Paragraph 1 is 80 words, paragraph 2 is 120 words, both exact word-for-word. File 1: am-thanh-1.mp3 (paragraph 1, Joanna). File 2: am-thanh-2.mp3 (paragraph 2, Matthew). Each file must play, duration over 10 seconds. File 2 has more words than file 1 (120 vs 80). If the free 3000-character daily limit was exhausted before the run, the task is declared invalid before the run with a backup applied. The scorer opens the 2 MP3 files and checks the durations.

Task text Pass: both MP3 files exist, play, each duration over 10 seconds, file 2 has more words than file 1 (120 vs 80), result file has all items, screenshot shows the audio creation page.

## Evidence

- ket-qua.txt (1443B) records: "Remaining free characters at start: 3000" (full limit available, not exhausted, so no invalid); Voice Joanna, am-thanh-1.mp3, 174284 bytes, 29.04 s; Voice Matthew, am-thanh-2.mp3, 238076 bytes, 39.672 s; both paragraphs in full.
- Paragraphs: I compared the 2 paragraphs in ket-qua.txt against the key word-for-word with a script. Both are EXACT MATCHES: paragraph 1 is 80 words / 494 chars, paragraph 2 is 120 words / 691 chars. (An earlier extraction pass that counted 91 words for paragraph 1 was my own parsing error: it had included the "Voice: Matthew" header lines that follow paragraph 1 in the file. Re-extracting only the paragraph block gives 80 words and an exact match. I corrected this before deciding.)
- Total text is 1185 characters, well within the 3000/day free limit.
- MP3 files (independent check with ffprobe, as the key requires the scorer to open the files and check durations): am-thanh-1.mp3 is valid MPEG Audio Layer III, 48 kbps, 24 kHz, mono, duration 29.040 s, size 174284 bytes; am-thanh-2.mp3 is valid MPEG Audio Layer III, 48 kbps, 24 kHz, mono, duration 39.672 s, size 238076 bytes. Both match ket-qua.txt exactly, both play, both durations are over 10 s. File 2 (120 words, 39.672 s) is longer than file 1 (80 words, 29.04 s), consistent with the word counts; the implied speaking rates (about 165 and 182 words per minute) are plausible for text-to-speech.
- Screenshot 20261125-220227-tts.png shows ttsmp3.com ("Free Text-To-Speech and Text-to-MP3 for US English", "type or paste up to 3,000 characters a day"), the "Regular Voices" tab selected, and paragraph 1 in the text box. The required site and voice category are confirmed. A popup ad covers the lower part of the page, so the voice selector is not visible in the screenshot, but the voice names are recorded in ket-qua.txt and the key does not require the scorer to verify the voice from the screenshot.
- Timing: start 2026-11-25T22:02:14+07:00, end 2026-11-25T22:02:45+07:00 (31 s). Fast for 2 generations plus 2 downloads, but the evidence is independently verified (valid MP3s with durations and sizes matching ket-qua.txt exactly, paragraphs matching the key exactly, screenshot of the site with paragraph 1 in the box), so timing alone is not a fail.

## Reason

Both MP3 files exist, play, and are over 10 seconds (29.04 s and 39.672 s, verified with ffprobe); both paragraphs match the key word-for-word (80 and 120 words); file 2 has more words than file 1; ket-qua.txt has all items; and the screenshot shows the ttsmp3.com audio creation page with Regular Voices.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
