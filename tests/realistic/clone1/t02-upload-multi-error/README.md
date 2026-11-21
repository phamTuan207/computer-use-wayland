# t02-upload-multi-error: upload several files, one fails midway

## Context

A problem setter uploads three test data files for a problem. The
judge accepts files up to 64 KB. One file is 100 KB, so the simulated
server rejects it midway while the other two succeed. The setter must
notice the failure, remove the bad file, and retry the rest without
re-uploading the files that already succeeded.

## Goal

Upload three files, see exactly one failure, remove the failed file,
retry, and end with the two good files confirmed as uploaded.

## Steps

1. Open the fixture page.
2. Choose three files: two small files and one 100 KB file.
3. Click `Upload all`.
4. Note the failed row for the large file.
5. Click `Remove failed files`.
6. Click `Upload remaining`.
7. Wait for the final confirmation.

## Pass conditions

- After the first upload, the large file row shows an error mentioning
  the 64 KB limit, and the two small files show `ok`.
- After removing the failed file and retrying, the confirmation lists
  exactly the two small file names and no mention of the large file.
- The failed file is never reported as uploaded.

## Fail conditions

- The large file is reported as uploaded.
- A small file is reported as failed.
- The retry confirmation is missing or lists the wrong files.

## Notes

The fixture simulates the server in the page. No file leaves the
machine. The browser run is Playwright Chromium; the same flow on
Firefox or Zen is UNVERIFIED.
