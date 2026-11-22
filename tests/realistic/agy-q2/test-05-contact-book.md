# test-05-contact-book.md

## Test ID
test-05-contact-book

## Topic
Contact book directory: add new contact via modal, edit existing contact phone, star favorite contact, delete invalid contact, search and filter, and save directory state.

## Context
the owner manages the company internal directory.
The workstation runs an offline browser directory (fixtures/test-05-contact-book.html).
There are 6 initial contacts (Alice Chen, Bob Martin, Clara Vance, David Kim, Eva Rostova, and an unverified entry "Spam Bot").
The user must add a new teammate "Frank Sinatra" (Engineering, frank.s@example.com, +1-555-0106), update Bob Martin's phone to "+1-555-9999", star David Kim as a favorite contact, delete the "Spam Bot" entry, test search and department filtering, and save the directory.

## Timing
- Baseline start time: 2026-11-21 17:05:00 Asia/Ho_Chi_Minh
- Expected duration: 150 seconds elapsed
- Maximum allowable latency: 260 seconds elapsed

## Goal
Add Frank Sinatra, update Bob Martin phone to +1-555-9999, star David Kim, delete Spam Bot, verify 6 contacts with 1 favorite, and save directory.

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-05-contact-book.html in the browser.
2. Confirm 6 initial contacts are listed and count indicator (id "contacts-count") displays "6".
3. Click "+ Add Contact" button (id "btn-new-contact").
4. In modal, type "Frank" into first name input (id "input-contact-first").
5. Type "Sinatra" into last name input (id "input-contact-last").
6. Type "frank.s@example.com" into email input (id "input-contact-email").
7. Type "+1-555-0106" into phone input (id "input-contact-phone").
8. Ensure department dropdown (id "select-contact-group") is set to "Engineering".
9. Type "Vocal Architect" into notes input (id "input-contact-notes").
10. Click "Save Contact" modal button (id "btn-modal-save-contact").
11. Verify contacts count indicator (id "contacts-count") updates to "7".
12. Locate Bob Martin's card and click "Edit" (id "btn-edit-contact-bob-martin").
13. In modal, clear phone input (id "input-contact-phone") and type "+1-555-9999".
14. Click "Save Contact" modal button (id "btn-modal-save-contact").
15. Verify Bob Martin's phone field (id "phone-bob-martin") displays "+1-555-9999".
16. Locate David Kim's card and click favorite star icon (id "btn-fav-contact-david-kim").
17. Verify star icon gains the "active" class and card highlights.
18. Locate Spam Bot's card and click "Delete" (id "btn-del-contact-spam-bot").
19. Verify contacts count indicator (id "contacts-count") updates to "6".
20. In search input (id "contact-search"), type "Kim".
21. Verify only 1 contact card (David Kim) remains visible.
22. Clear search input (id "contact-search").
23. In group dropdown (id "filter-contact-group"), select "Engineering".
24. Verify exactly 3 contact cards are visible (Alice Chen, David Kim, Frank Sinatra).
25. Reset group dropdown (id "filter-contact-group") to "all".
26. Verify all 6 contact cards are visible.
27. Click "Save Directory" button (id "btn-save-directory").
28. Read status banner (id "contact-status-banner") and confirm text contains "Directory saved: 6 contacts (1 favorite)".

## Pass/fail criteria
- Pass: Exactly 6 contacts exist, Frank Sinatra added in Engineering, Bob Martin phone is +1-555-9999, David Kim is favorite, Spam Bot removed, directory saved banner confirmed.
- Fail: Spam Bot still present, Frank Sinatra missing, wrong phone number, wrong favorite count, or unsaved directory.

## Errors designed to expose
- click miss: Star icon or edit/delete buttons inside densely packed contact cards.
- modal unhandled: Forgetting to close or submit modal before attempting card interactions.
- stale selector: Using old card element references after DOM grid re-render.
- filter trap: Leaving search string or group dropdown active when attempting to inspect all contacts.
- fabrication: Claiming contact was updated without checking card phone text.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-05-contact-book.html --test 05
```
