# t07-download-check: download a file, check its contents

## Context

A problem setter downloads the generated test data for a problem from
the judge site and must confirm the file is complete before using it.
The file is a CSV with a header row and five data rows. The page shows
the expected row count and a checksum of the file bytes.

## Goal

Download the generated CSV and verify its header, row count, and
checksum against what the page promised.

## Steps

1. Open the fixture page.
2. Read the expected row count and checksum shown on the page.
3. Click `Download test data`.
4. Open the downloaded file and read its contents.
5. Compare the header, the row count, and the checksum with the page.

## Pass conditions

- The downloaded file exists and is not empty.
- The first line is exactly `id,input,expected`.
- The file has 6 lines: 1 header plus 5 data rows.
- The checksum computed from the downloaded bytes matches the
  checksum shown on the page.

## Fail conditions

- No download happens within 10 seconds.
- The header is wrong, or the row count is not 6 lines.
- The checksum does not match.

## Notes

The fixture generates the CSV in the page with a Blob. No data leaves
the machine. The browser run is Playwright Chromium; the same flow
on Firefox or Zen is UNVERIFIED.
