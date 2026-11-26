# R3-035 scorer 2 grade (Pair A, R3-L3)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-035
verdict: PASS
timestamp: 2026-11-26 13:21 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: all 3 xe.com conversion screenshots show exactly the rates and results recorded in ket-qua.txt and in the saved online document, the arithmetic checks out (the GBP row differs by 1 VND from the product of the 2-decimal displayed rate, inside the key's 1 VND tolerance, and equals xe.com's own displayed result), and the total is the exact sum of the 3 results.

## Key section used

docs/rung3-answer-keys.md, "## R3-035 (Tier B)", lines 363-370: convert 100 USD, 50 EUR and 200 GBP to VND on xe.com, recording the live rate and result for each; total is the sum of the 3 results; rounding tolerance 1 VND. Rates and results are live at run time and the timestamped screenshots are the ground truth. Grading evidence: the rate and result screenshots plus the online document (table of 4 rows: 3 conversions and 1 total row); the grader compares rates, results and total against the screenshots.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-035-L3/
- Manifest hash (manifest_sha256 field in manifest.json): 976ef57d5d7a5dd9c0d1d79ca6b8bbee28522aa511607632494f90a48100c134 (matches the dispatch notice)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 61 evidence files OK, no mismatches, no files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-26T12:54:46+07:00, end_time.txt 2026-11-26T13:15:42+07:00, inside the 30 minute task limit. All 3 conversion screenshots show the xe.com mid-market rate timestamp 05:58 UTC (12:58 +07), inside the window.

Per-file results (name, recomputed sha256, result):
  - 20261126-1300-conv1-usd-vnd.png b0cf2844481656a2dcc26d406c4fa3a7f7a94067d52f64d17fc4cb36585fcd5a OK
  - 20261126-1301-conv2-eur-vnd.png df7c5407a3e879bd890415fe9435527c73ecf7f279efeb4bbe0097c875f7ab2b OK
  - 20261126-1303-conv3-gbp-vnd.png 6bf8bbd083a747d93d92fe51fdba5a3721700a91aa887bcfbc3a49a79f878107 OK
  - 20261126-1316-doc-reopened.png ac6d9c3ad84400fd23deb4f7e2bc42c26344fc756d59d49965a35429fd27c8f4 OK
  - 20261126-1316-pill-gone.png e9c7dbc3e7a9e14a6be498d729e62112d59c582fe9016acf35f39ac8c498cb95 OK
  - act1.json 51ad1545f42c4f947c75a3974e267e95a2a3eb9199d326e8b615aff118853d39 OK
  - act10.json 263a0db9fe680aa5507e6f67fe82ef011c97c3190678d8d54100a47fc60c8195 OK
  - act11.json 01e042d1e618aa94bbab027c191e68dc7fd0dbf437b485d1a62d7baff1f9dea2 OK
  - act12.json 263a0db9fe680aa5507e6f67fe82ef011c97c3190678d8d54100a47fc60c8195 OK
  - act13.json a278f25d3e43387816524111c3031d6aa1643e78d4d358fc4750c47b3272504f OK
  - act14.json 0aa17ee988879257844d6d005c495dcaa4ebc80e4f4488695eeffc338416de3e OK
  - act15.json 82d37966e1b0bbf7e5bf453d6e0ed0d8cf5861d1f2e3685a75fa1d6bdac7ab08 OK
  - act16.json f4e5995d58707da28a9ce4002d6a32c34b5ed08cce984a5c47078dfaaaf3341a OK
  - act17.json e86402ffa7798b6f0dd574d87074e61a543605466245a540b303030608a6481d OK
  - act18.json 1800d09a6dd5e4f8c2b375cdeda2313cb00daaed721b7340dc711bb036d7c0f3 OK
  - act19.json 0ca0c8ff8e674040d973560189a802cf2731616a4ef92544a2605cf81515a848 OK
  - act2.json 466d8f6d64b1705fca59e15223c82d825922c4fdce95169e8c26ee624239f6c7 OK
  - act20.json 5d7d08180836a3c2506efea24ae50e953e0779cb672e728591a3f74ad398e866 OK
  - act21.json 8dd675602a914d42e677e5c34bbe727e89a8c366b528893264e44bacaf2f094d OK
  - act22.json b82501234db8575383ef7f9fe5d162869f091999fe2dbcfdb043f88bf4ebe68f OK
  - act23.json 2c793850b69049249a1a63050607f90a7edd5291c0b732fbcbf06dbccf390760 OK
  - act24.json e696c510f9518bd6d1e9baa1ddf6c4dd4476e14b877de0f95f8109b17483eb7b OK
  - act25.json 83983fdbd254ed48df7f605cd10b0c4a84934c63424a7177f60f4e933d1b4af4 OK
  - act26.json 38a7c0eae912cf59646de8d407c1e31f125cfe7411545f1db45b4e9dabde1c09 OK
  - act27.json b45e7198cfc33cd711d31c8da57bb8b9ac5e292e6964ff9b956e0b38d252018d OK
  - act28.json ca3e19b79c6acee7856432979e805c2580c1ec58931059575530f90adea7e733 OK
  - act29.json 5b25b363d897bf885b824f4bc3104cf79242d046f19698f3002bc16fa1fc9153 OK
  - act3.json a5b94fc5d7ef1301189a7ec00eceb5c9de54e1fe3298e35016bd3285557ccb92 OK
  - act30.json b030df0333bbabbb03b7d1237a8e91c4364893cd2cb93996e1cee203268bdfa6 OK
  - act31.json 39128db9a54ae4ba6113e1e5dd39bafdabad8ffb617cb9bbff8107622370c87d OK
  - act32.json ca9f72a146eaa6b98319eff30f86fe1b84b7c313273e38066c201a9ccd68e892 OK
  - act33.json 94006637c67b6485eac9886891d99857451c8aac45984d2a86ae4e56d6373bed OK
  - act34.json 80a5cca5428dc579527f34aa466e8f3998a6be140484e541109b53e52df66269 OK
  - act35.json f756765b42dfba670b558bee2da9382d6eb86489cf0ab320d6672dde58b764f2 OK
  - act36.json fd0b481f2baa9426a03666ed3ae46b10fc9c208a7e6aaa1af6cf0933000bb81e OK
  - act37.json c663832946ab8e8e099d3bba1f8b0807eed4147163995418406b407729f20bf4 OK
  - act38.json 4f28eee813bd1522dfea95d43c248b416942453b47dd29c592c075ab87628458 OK
  - act39.json 5d7b95ca8f84f548211318fdf990647bb4a29714725a85cfb3108fcedf555758 OK
  - act4.json baef310ec5b87ec445bc3c57ab54b098e361e6f24d4c20b2b1076d9c06c0dab0 OK
  - act40.json e74e98c3770cd0f8a8f14e41b3df7da4ee86fd34298c3efd69998ace57fb7797 OK
  - act41.json f756765b42dfba670b558bee2da9382d6eb86489cf0ab320d6672dde58b764f2 OK
  - act42.json eee8582dd001ae09b922d451e56062135af645070f6faf43be5c5903de4dbea4 OK
  - act43.json 451d1edae074b03b99c4ce2a4c8f4a2c3c5ed43e27120ae18e252a1bceb4c737 OK
  - act44.json 1690b7aca95cc0b48f278fe6e71253b914345abe10b33ed81187c9ae21bfb9c4 OK
  - act5.json 725e4d85d1359a83559c8164fe199e7893924be7fc49d4733a145493c0ac7e48 OK
  - act6.json 7ecf6396b1c7884c18f8911ca00f21f30fcc9aba76f6d8a590ccd123fd495acc OK
  - act7.json 263a0db9fe680aa5507e6f67fe82ef011c97c3190678d8d54100a47fc60c8195 OK
  - act8.json 7ecf6396b1c7884c18f8911ca00f21f30fcc9aba76f6d8a590ccd123fd495acc OK
  - act9.json 025131668c9da6ec7039d87b6672181c41e5459d4b6be16deaf6d50fd3d3cf5d OK
  - drive-log.txt a55b3386b3fbca9f9afcb4f83bca22870bd8f9d23873dc350c9e754515ff3dfe OK
  - end_time.txt fa008f536724461872dc1dec276a67590f36aba2bc4a7209f0b9c6068463ab94 OK
  - holder-pid.txt 832026cea53673c10bfe12e341a47d01df6128a0376e9d278119abe263465860 OK
  - holder-task.log 580578f35e68e8d5988422cdfd29c9095b9b1af837c17359e1a1e063a7f04b7a OK
  - ket-qua.txt 405e5e710cf8ab4beb5def5c7e0a11671ab06da27e2d2141774e59999b78ebc0 OK
  - probe-ready.json 23527a6aa9734243461422321cb99e2f82ab84e054ead8d69b94633252db83c7 OK
  - start_time.txt 77c147968e2a1b56e4e4fb8176ea5a040d58eb1e8c7db6eca32b72d2324224e5 OK
  - step00-probe.png ba827f80d70c860c1ece2c8db4332be28c152ec4c6491be2a24c12134a107fac OK
  - step01-serp.png 4d23eacc9dec07ff05f6a623a201ead77ceed0c7ec353a8c35c62c9b346f141d OK
  - step02-xe.png 725e392ca512fa4ec8a891a69c068a895b2cab5a3c5961c4743d7e8c1ba4cde7 OK
  - step03-amt100.png 39ee1c89814651af96f871ae986007bb4a68bfff055ea7c93de090291c36dd58 OK
  - step04-dropdown.png 9a3e7f0c68d9eae7fc3c91ba777a650b68c0ce6ff8eef048e571646a7b0107fb OK

## Files read

- rung3-run-log/briefs/R3-035-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 363-370 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- rung3-run-log/rung3-snapshots/R3-035-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-035-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-035-L3/20261126-1300-conv1-usd-vnd.png
- rung3-run-log/rung3-snapshots/R3-035-L3/20261126-1301-conv2-eur-vnd.png
- rung3-run-log/rung3-snapshots/R3-035-L3/20261126-1303-conv3-gbp-vnd.png
- rung3-run-log/rung3-snapshots/R3-035-L3/20261126-1316-doc-reopened.png
- rung3-run-log/rung3-snapshots/R3-035-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-035-L3/end_time.txt

The remaining snapshot files (act1.json to act43.json, drive-log.txt, holder-task.log, holder-pid.txt, probe-ready.json, the step00 to step04 screenshots and 20261126-1316-pill-gone.png) were hash-verified against the manifest but not read for grading: the brief directs grading from the 3 conversion screenshots, the saved document screenshot and ket-qua.txt, not from report or log text.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.

## Reasons

- Conversion 1 (100 USD to VND): 20261126-1300-conv1-usd-vnd.png shows the xe.com converter with 1.00 USD = 25,842.15 VND, mid-market rate at 05:58 UTC, amount $100.00, result 2,584,215 VND. ket-qua.txt records rate 25,842.15 and result 2,584,215, an exact match, and 100 x 25,842.15 = 2,584,215.
- Conversion 2 (50 EUR to VND): 20261126-1301-conv2-eur-vnd.png shows 1.00 EUR = 28,320.08 VND, mid-market rate at 05:58 UTC, amount 50.00 EUR, result 1,416,004 VND. ket-qua.txt records rate 28,320.08 and result 1,416,004, an exact match, and 50 x 28,320.08 = 1,416,004.
- Conversion 3 (200 GBP to VND): 20261126-1303-conv3-gbp-vnd.png shows 1.00 GBP = 33,855.23 VND, mid-market rate at 05:58 UTC, amount 200.00 GBP, result 6,771,047 VND. ket-qua.txt records rate 33,855.23 and result 6,771,047, an exact match with the screenshot. The product of the displayed 2-decimal rate is 200 x 33,855.23 = 6,771,046, so the recorded result differs by 1 VND from that product; xe.com computes its displayed result from the full-precision rate, the key's rounding tolerance is 1 VND, and the key makes the screenshot the ground truth, so this row passes.
- Saved online document: 20261126-1316-doc-reopened.png shows the reopened Google Docs document (same document ID as the URL in ket-qua.txt) holding the 4 required rows: the 3 conversions with the same rates and results as the screenshots, and the total row 10,771,266 VND.
- Total: 2,584,215 + 1,416,004 + 6,771,047 = 10,771,266 VND, exactly the total recorded in ket-qua.txt and in the document.
- No block or error state appears in any graded screenshot; xe.com and Google Docs render normally throughout, so the list section 1 invalid case does not arise.
