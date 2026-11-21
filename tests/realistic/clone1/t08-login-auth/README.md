# t08-login-auth: login, then authenticated work

## Context

A problem setter logs in to the judge site with an access code, then
works on a protected page: marking a problem as reviewed. The session
must survive a reload, and logging out must hide the protected page
again. A short or empty access code must be rejected with an error.

## Goal

Log in with a valid access code, do the protected review action,
confirm the session survives a reload, log out, and confirm the
protected page is hidden again.

## Steps

1. Open the fixture page.
2. Try an access code that is too short and read the error.
3. Log in with the access code `CODE-2026-ABCD`.
4. On the protected page, click `Mark problem 42 as reviewed`.
5. Reload the page and confirm the session is still active.
6. Click `Log out` and confirm the login form is back and the
   protected page is hidden.

## Pass conditions

- The short code shows an error and does not log in.
- The valid code shows the protected page with a welcome message.
- The review action reports `Problem 42 marked reviewed`.
- After reload, the protected page is still shown.
- After logout, the login form is shown and the protected page is
  hidden.

## Fail conditions

- The short code logs in, or the valid code is rejected.
- The review action does not report the problem number.
- The session is lost on reload, or the protected page stays visible
  after logout.

## Notes

The access code here is a demo value typed by the check script, not a
real account credential. The fixture keeps the session in session
storage. No data leaves the machine. The browser run is Playwright
Chromium; the same flow on Firefox or Zen is UNVERIFIED.
