# t04-kanban-drag: drag cards on a kanban board

## Context

A kanban board with Todo, Doing, and Done columns. Cards move by HTML5
drag and drop, can be reordered inside a column, added, deleted, and
filtered. The board saves to localStorage.

## Goal

Move cards between columns, reorder one, add and delete cards, filter,
and prove the board survives a reload and can be emptied.

## Steps (36)

1. Open the fixture.
2. Clear the saved board and reload.
3. Check Todo starts with 3 cards.
4. Check Doing starts with 2.
5. Check Done starts with 1.
6. Drag the bug card from Todo to Doing.
7. Check Todo is 2 after the drag.
8. Check Doing is 3 after the drag.
9. Check the dragged card is in Doing.
10. Check the status says it moved to Doing.
11. Drag the card above another card to reorder.
12. Check the reordered card is first in Doing.
13. Drag the card to Done.
14. Check Done is 2.
15. Check the card is in Done.
16. Type a new card title.
17. Pick the bug tag.
18. Add the new card.
19. Check Todo is 3 after the add.
20. Check the new card appears.
21. Filter by bug.
22. Check the filter shows 3 of 7 cards.
23. Clear the filter.
24. Check the counts are back.
25. Delete a card.
26. Check Todo is 2 after the delete.
27. Check the status says deleted.
28. Reload the page.
29. Check Todo persists at 2 after reload.
30. Check Doing persists at 2 after reload.
31. Check Done persists at 2 after reload.
32. Check the moved card is still in Done.
33. Drag the last Todo feature card to Done.
34. Drag the new bug card to Done.
35. Check Todo is empty.
36. Check the empty column message.

## Pass

All 36 steps run, every drag lands in the right column and order,
counts match after each move, the filter counts are right, and the board
persists after reload.

## Fail

Any step above fails, a drag does not move the card, a count is wrong,
or the board is lost on reload.
