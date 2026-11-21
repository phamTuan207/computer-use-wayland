# t09-upload-metadata: upload plus metadata form

## Context

A problem setter creates a problem by filling metadata (title and
difficulty) and uploading the statement file in the same form. The
server side, simulated in the page, requires all three: a title, a
statement file, and the file must be a `.txt` file. On success it
assigns a problem ID.

## Goal

See the form reject an empty submit and a wrong file type, then submit
a valid title with a `.txt` statement file and receive a problem ID.

## Steps

1. Open the fixture page.
2. Click `Create problem` with the form empty and read the errors.
3. Fill the title, choose a `.png` file, submit, and read the error.
4. Choose a `.txt` statement file instead, submit again.
5. Read the success message with the problem ID.

## Pass conditions

- The empty submit reports a missing title and a missing file.
- The `.png` submit reports that only `.txt` files are accepted.
- The valid submit reports success and a problem ID starting with
  `P-`.

## Fail conditions

- The empty submit succeeds, or the `.png` file is accepted.
- The valid submit shows an error instead of a problem ID.
- The success message has no problem ID.

## Notes

The fixture simulates the server in the page. No file leaves the
machine. The browser run is Playwright Chromium; the same flow on
Firefox or Zen is UNVERIFIED.
