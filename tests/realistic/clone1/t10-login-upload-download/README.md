# t10-login-upload-download: login, upload, download result

## Context

A problem setter logs in with an access code, uploads a test data
file, and the judge runs it: the simulated judge counts the cases in
the file and reports the verdict. The setter then downloads the result
report and checks that it names the uploaded file, the case count, and
the verdict.

## Goal

Log in, upload a 4-case test data file, see the judge verdict, download
the result report, and verify the report contents.

## Steps

1. Open the fixture page.
2. Log in with the access code `CODE-2026-ABCD`.
3. Upload a test data file with 4 non-empty lines.
4. Read the judge verdict.
5. Click `Download report`.
6. Open the downloaded report and check its contents.

## Pass conditions

- Login shows the upload section.
- The verdict reports 4 cases and `PASS`.
- The downloaded report names the uploaded file.
- The report states 4 cases and `Verdict: PASS`.

## Fail conditions

- The upload section never appears after login.
- The verdict reports the wrong case count or a fail.
- The report is missing, names the wrong file, or states the wrong
  verdict.

## Notes

The access code here is a demo value typed by the check script, not a
real account credential. The judge and the report are simulated in the
page. No data leaves the machine. The browser run is Playwright
Chromium; the same flow on Firefox or Zen is UNVERIFIED.
