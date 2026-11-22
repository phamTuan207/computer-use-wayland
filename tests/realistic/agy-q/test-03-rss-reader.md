# test-03-rss-reader.md

## Test ID
test-03-rss-reader

## Topic
RSS and news reader: subscribe to new feed, category filing, mark read/unread toggles, star/save articles, and export starred reading list.

## Context
the owner manages engineering newsletters and feed aggregations inside an offline desktop
reader fixture (`fixtures/test-03-rss-reader.html`). The reader initially contains two subscriptions
("Linux Weekly" and "Rust Digest") totaling 6 unread articles. The user needs to add a new custom feed
("Wayland Gazette" under category "Display Servers"), read and triage incoming dispatches, star an
important architecture article, mark another article unread for later review, batch mark the
remaining items as read, verify unread counts in the navigation tree, and export the starred reading list.

## Goal
Subscribe to "Wayland Gazette" with category "Display Servers", star article 201 ("Explicit Sync Lands
in Mainline"), execute "Mark All Read" across the aggregator, confirm total unread badge drops to 0,
and export the Starred Articles list verifying article 201 is included.

## Exact steps
1. Open fixture `tests/realistic/agy-q/fixtures/test-03-rss-reader.html` in the browser via file URL.
2. Verify initial state: 2 feeds loaded in sidebar, total unread badge shows "6".
3. In the left sidebar, click the "+ Subscribe" button (id `btn-add-feed`).
4. In the feed title input (id `input-feed-title`), type `Wayland Gazette`.
5. In the feed URL input (id `input-feed-url`), type `https://wayland.local/feed.xml`.
6. In the feed category dropdown (id `select-feed-category`), select `Display Servers`.
7. Click the "Add Subscription" button (id `btn-confirm-feed`).
8. Confirm modal closes and sidebar displays category "Display Servers" with child feed "Wayland Gazette (3)".
9. Verify the global unread badge at the top updates from 6 to 9.
10. Click the feed entry "Wayland Gazette" in the sidebar to filter the article list to this feed.
11. Observe that 3 articles appear in the middle column list (IDs 201, 202, 203), all in bold unread state.
12. Click article 201 ("Explicit Sync Lands in Mainline") in the list.
13. Observe the article content displays in the right reading pane.
14. Observe that article 201 transitions from unread to read, and feed unread count decrements to 2.
15. In the article reading pane toolbar, click the Star bookmark button (id `btn-star-article`).
16. Verify the star icon highlights yellow and status shows "Starred".
17. In the middle article list, click article 202 ("Fractional Scaling Best Practices").
18. Observe article 202 opens and automatically marks as read (feed unread count becomes 1).
19. Click the read toggle button (id `btn-toggle-read`) to mark article 202 back to "Unread".
20. Confirm article 202 row regains bold styling and feed unread count increments back to 2.
21. Click "All Articles" (id `nav-all-articles`) in the sidebar to view all 9 articles across all feeds.
22. Click the "Mark All As Read" button (id `btn-mark-all-read`) in the header.
23. Confirm the global unread badge updates to "0" and all article rows in the list lose their unread indicator.
24. In the sidebar, click the "Starred" navigation item (id `nav-starred-articles`).
25. Verify the article list filters to display exactly 1 item: "Explicit Sync Lands in Mainline".
26. Click the "Export Starred" button (id `btn-export-starred`).
27. Inspect the export output modal (id `modal-export-starred`) and confirm the text includes `- [Explicit Sync Lands in Mainline](https://wayland.local/art-201)`.
28. Click the "Close" button (id `btn-close-export-modal`) on the export dialog.

## Pass/fail criteria
- Pass: Feed "Wayland Gazette" subscribed under category "Display Servers", article 201 starred, global unread badge equals 0 after mark all read, starred view displays exactly article 201, and export dialog contains the markdown link for article 201.
- Fail: Feed not added, wrong unread count, article 201 not starred, mark all read fails to clear unread states, or exported markdown missing expected title/link.

## What to time
- Per-step wall time for modal inputs, navigation clicks, star toggles, and view switches.
- Total wall time from opening the fixture to completing step 28.
- Latency between clicking "Mark All As Read" and verifying the badge updates to 0.

## Errors designed to expose
- click miss: Star button (22x22 px) and Mark Unread button in reading header are prone to bounding box misalignments.
- slow think: Reading long article body text in the reader pane before proceeding with next step.
- stale observation: Reading old unread badge count before DOM re-renders after marking items read.
- wrong diagnosis: Concluding articles were deleted when switching to Starred view.
- fabrication: Asserting that total unread is 0 without reading the badge value.

## Checker / expected end state
Checker command:
```bash
node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-03-rss-reader.html --test 03
```
Expected end state:
- Subscribed feeds: 3 ("Linux Weekly", "Rust Digest", "Wayland Gazette")
- Category "Display Servers" exists with "Wayland Gazette"
- Article 201 starred: true, read: true
- Total unread count: 0
- Starred articles count: 1 (ID 201)
- Export status verified: true
