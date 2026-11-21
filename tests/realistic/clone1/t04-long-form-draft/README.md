# t04-long-form-draft: long form, conditional fields, draft save

## Context

A problem setter fills a long creation form, but the work is
interrupted. The form type selector changes which fields exist: the
`interactive` type reveals extra fields for the interactor description
and the query limit, while the `batch` type hides them. A `Save draft`
button stores the in-progress form in local storage, so a reload
restores it instead of losing the work.

## Goal

Show that the conditional fields appear only for the interactive type,
save a draft, reload the page, see the draft restored, then submit
successfully.

## Steps

1. Open the fixture page.
2. Select type `batch` and confirm the interactive fields are hidden.
3. Select type `interactive` and confirm the extra fields appear.
4. Fill the title, the interactor description, and the query limit.
5. Click `Save draft`, then reload the page.
6. Confirm the title and the extra fields still hold the same values.
7. Click `Create problem` and read the success message.

## Pass conditions

- The interactive fields are hidden for `batch` and visible for
  `interactive`.
- After reload, the title, interactor description, and query limit
  match what was typed before the reload.
- The final submit shows a success message containing the title.

## Fail conditions

- The conditional fields show for the wrong type.
- Any drafted value is lost after reload.
- The final submit shows an error instead of success.

## Notes

The fixture uses local storage in the page origin. No data leaves the
machine. The browser run is Playwright Chromium; the same flow on
Firefox or Zen is UNVERIFIED.
