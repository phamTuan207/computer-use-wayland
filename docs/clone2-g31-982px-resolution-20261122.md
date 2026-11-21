# G31 982 px vs 2 px resolution, 2026-11-22

Status: RESOLVED. This report resolves the open inconsistency 1 in docs/g31-nearmiss-draft-20261122.md (fix pass e7b4713) independently from the raw data: the region origins, image sizes, and normalized grounding readings recorded in the CL2-MSG timeline. The coordinator's analysis was not taken as the answer; every conversion below was recomputed from those raw numbers, and the recomputation reproduces the timeline's converted point exactly.

## Conclusion

2 px is correct. 982 px is an artifact of comparing two coordinates that live in two different coordinate spaces without converting them to a common space.

The click point (306,1130) is in the WINDOW observation image space (901x1176). The cursor after click (1288,1144) is in the SCREEN after-image space (1920x1200). Subtracting them raw gives 982.1 px, which is meaningless. Converted to the same space, the click point is (1290,1142) in screen space, and the cursor is (1288,1144): dx 2, dy 2, Euclidean 2.83 px. The assignment's "2px from the click point" is correct, read as 2 px per axis.

## Source gap, stated honestly

The direct log ~/workspace/cl2msg-direct-log.md does not exist on this machine. A full filesystem search finds no file of that name and no copy of it in the repo. It presumably lives on the laptop. This resolution is derived instead from the CL2-MSG timeline in improvements/worker-coord-click2-log.md on origin/todolist-push (line 196), which records the same incident with the region origins, image sizes, and both normalized grounding readings, plus improvements/worker-cl1sweep-fail-invest-log.md (commit 5f5a2fd) for the after-image scope. The timeline is a primary record of the run, not an analysis, and every number in it is re-derived below rather than quoted on trust.

## The exact coordinate chain, step by step

All times 2026-11-22, Asia/Saigon. All coordinates in px.

### Step 1: the window observation, 03:49:57

Fresh observe of the clone2 Chrome window (0x5570538ed160), observation id 76e9b0732824.

- Image size: 901 wide, 1176 tall.
- Region (global screen coordinates of the image's top-left corner, then width and height): [3448, 914, 901, 1176].
- Monitor box: [2464, 902, 1920, 1200]. The window sits inside it: 3448 + 901 = 4349, inside 2464 to 4384; 914 + 1176 = 2090, inside 902 to 2102.

### Step 2: the grounding tool point, 03:51

visual_grounding on the input field, normalized reading (340, 961) on the 901x1176 window image.

- x: 0.340 x 901 = 306.34, rounds to 306.
- y: 0.961 x 1176 = 1130.14, rounds to 1130.
- Tool point: (306, 1130), in WINDOW image space. Bounds check: 0 <= 306 < 901 and 0 <= 1130 < 1176, inside the image.

The eye guess (307, 1085) is in the same window image space, so the eye-error comparison is valid in that space: dx 1, dy 45. The 45 px eye error stands as recorded.

### Step 3: the click, 03:51:22

Click act-now at (306, 1130). Result ok true, completed 1, total 1667 ms. After-image id f2bdb0d34ead.

The click coordinates are window image coordinates, because the click was issued against the window observation. The act-now call takes the point in the observation's own image space.

### Step 4: the after-image is screen-scoped

The invest log (commit 5f5a2fd) proves from the laptop JSON that f2bdb0d34ead is scope = screen, image_size [1920, 1200]. This is the structural trap that log documents: act-now always returns a screen-scoped after-image, whatever the input observation's scope. For this resolution, what matters is the coordinate space it defines: the after-image is a full-monitor image, region [2464, 902, 1920, 1200], the same as the monitor box.

### Step 5: the cursor read, 03:51:5x

Caret verified: visual_grounding found the I-beam at normalized (671, 953) on the 1920x1200 after-image.

- x: 0.671 x 1920 = 1288.32, rounds to 1288.
- y: 0.953 x 1200 = 1143.6, rounds to 1144.
- Cursor point: (1288, 1144), in SCREEN image space. Bounds check: 0 <= 1288 < 1920 and 0 <= 1144 < 1200, inside the image.

This is the read the invest log's scope finding governs: the cursor was read off a screen-scoped image, so its coordinates are screen image coordinates, not window image coordinates.

### Step 6: convert the click point to screen space

Window image origin in global coordinates is (3448, 914). Screen image origin in global coordinates is (2464, 902).

- Click point in global coordinates: (306 + 3448, 1130 + 914) = (3754, 2044). Bounds check: inside the monitor box, 2464 <= 3754 <= 4384 and 902 <= 2044 <= 2102.
- Click point in screen image coordinates: (3754 - 2464, 2044 - 902) = (1290, 1142).

This reproduces the timeline's converted point (1290, 1142) exactly. The conversion was computed here from the region origins, not copied from the timeline.

### Step 7: the distance, in one common space

Both points in screen image space:

- Click point: (1290, 1142).
- Cursor after click: (1288, 1144).
- dx = 1290 - 1288 = 2. dy = 1144 - 1142 = 2. Euclidean distance = sqrt(2^2 + 2^2) = sqrt(8) = 2.83 px.

The assignment's "2px from the click point" is the per-axis difference, 2 px in each axis. Stated precisely, the distance is 2 px per axis, 2.83 px Euclidean.

### Where 982 px comes from

sqrt((1288 - 306)^2 + (1144 - 1130)^2) = sqrt(982^2 + 14^2) = 982.1 px. That subtraction mixes window image coordinates (306, 1130) with screen image coordinates (1288, 1144). The x difference is dominated by the two image origins: the window image starts at global x 3448, the screen image at global x 2464, a difference of 984 px. Subtracting unconverted coordinates mostly measures the offset between the two image origins, not the distance between the two points. The draft's section 1 computed this number correctly and then, correctly, refused to reconcile it; the reconciliation it withheld was the coordinate-space conversion, which it explicitly said it would not guess. The conversion is now supplied from the recorded region origins, so the number is explained, not guessed.

## What this means for the CL2-MSG click-precision claim

The claim stands, and it is now verified rather than merely asserted.

1. The click landed where the tool said it would. The tool point (306, 1130) in window space converts to (1290, 1142) in screen space, and the caret was found at (1288, 1144), 2 px per axis away. The click was precise to about 3 px.
2. The draft's open inconsistency 1 is resolved. Its consequence no longer holds: the click-landing claim is verified by the cross-space conversion, so the "tool was right" story does not collapse. The 982 px warning in the draft was a false alarm caused by cross-space comparison, and the draft needs a dated correction note saying so, not a rewrite.
3. The 45 px eye error is real and was caught before clicking. The eye guess and the tool point are both in window image space, so that comparison needs no conversion and is unaffected by this resolution.
4. The downstream effects corroborate the click independently of the coordinate arithmetic: the caret was verified in the input at 03:51:5x, the typed text was verified in clone2's input at 03:52:5x (clone1's input still empty), Enter was pressed once at 03:53:29, and the blue bubble with the full text appeared in the thread at 03:53:30.
5. The draft's conclusion stays a hypothesis, not a rule. This resolution upgrades the evidence from one uncorroborated near-miss with contradictory coordinates to one verified near-miss with consistent coordinates, but it is still n = 1. A universal "must replace the eye guess before every click" rule is still not earned. The draft hypothesis wording needs no change.
6. The draft's section 2 is unaffected. The CL1-MSG comparison remains contradicted by the real CL1-MSG logs (the about 50 px offset was a JPEG-reading artifact, the failures had a different cause). This resolution says nothing about CL1-MSG, and the comparison stays recorded as contradicted.
7. "1/1" remains undefined. The timeline gives the total (4 min 3 s, 03:49:27 to 03:53:30) and the message in thread, but no source defines what "1/1" counts. The draft's flag stands.

## What the draft needs

A dated correction appended to docs/g31-nearmiss-draft-20261122.md, stating: inconsistency 1 is resolved, 2 px is correct (2 px per axis, 2.83 px Euclidean), 982 px was a cross-space artifact, the click-landing claim is verified, and the conclusion remains a hypothesis. No other change to the draft follows from this resolution. That correction is a follow-up edit for the coordinator, not part of this report.
