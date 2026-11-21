# t01-upload-single: upload one file to a web form

## Context

A problem setter uploads a statement file for a new problem on a
judge site, similar to creating a problem on Polygon. The form has a
problem title and one file input. The upload shows progress and, when
done, a confirmation with the file name, size, and a checksum so the
setter can confirm the right file arrived.

## Goal

Upload one statement file through the form and confirm the page reports
the correct file name, size, and checksum for the given title.

## Steps

1. Open the fixture page.
2. Type the title `Sample Problem` in the title field.
3. Choose a statement file from disk.
4. Click `Upload`.
5. Wait for the progress bar to finish and the confirmation to appear.

## Pass conditions

- The confirmation text contains the uploaded file name.
- The confirmation text contains the exact byte size of the file.
- The confirmation text contains the checksum computed from the file
  bytes (simple sum, `h = (h * 31 + b) >>> 0`, printed as 8 hex digits).
- The confirmation text contains the title `Sample Problem`.

## Fail conditions

- No confirmation appears within 10 seconds.
- The confirmation shows a wrong name, size, or checksum.
- The page reports an error instead of a confirmation.

## Notes

The fixture simulates the server in the page. No file leaves the
machine. The browser run is Playwright Chromium; the same flow on
Firefox or Zen is UNVERIFIED.
