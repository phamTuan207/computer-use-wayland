# t03-keyboard-nav: use the page without a mouse

## Context

A demo page built for keyboard users: a skip link, a dropdown menu,
a listbox, a contact form, a focus-trapped dialog, and a Ctrl+K search
overlay. Every interaction must work from the keyboard alone.

## Goal

Walk the whole page by Tab, operate the menu, listbox, form, dialog,
and search with keys only, and prove focus always lands where it should.

## Steps (35)

1. Open the fixture.
2. Walk the Tab order through 8 stops.
3. Check the Tab order is skip, menu button, listbox, name, email,
   country, Send, dialog button.
4. Shift+Tab back to the menu button.
5. Open the menu with Enter.
6. Check the menu opened.
7. Arrow down to the second menu item.
8. Check the arrow focused Reference.
9. Pick the item with Enter.
10. Check the result says Reference and focus returned to the button.
11. Tab to the listbox and check it is focused.
12. Arrow down twice in the listbox.
13. Pick the item with Enter.
14. Check the listbox picked Forms.
15. Tab to the name field and type a name.
16. Tab to the email field and type an email.
17. Tab to the country select.
18. Arrow down to the first country.
19. Check the country is vn.
20. Tab to Send.
21. Submit with Space.
22. Check the form result.
23. Tab to the dialog button and check it is focused.
24. Open the dialog with Enter.
25. Check the dialog opened with its input focused.
26. Type feedback.
27. Tab inside the dialog to test the trap.
28. Check the focus trap moved to Close.
29. Close with Escape.
30. Check the dialog closed, focus returned, and feedback kept.
31. Open search with Ctrl+K and check it opened with input focused.
32. Type the search query apple.
33. Pick the first match with Enter.
34. Check the pick is apple pie and the overlay closed.
35. Open search again and close it with Escape.

## Pass

All 35 steps run, the Tab order matches, every arrow and Enter works,
the dialog traps focus and closes on Escape, and the search picks and
closes correctly.

## Fail

Any step above fails, the Tab order is wrong, focus is lost, the trap
lets focus escape, or a key does nothing.
