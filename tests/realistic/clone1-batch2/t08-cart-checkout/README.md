# t08-cart-checkout: shop and pay

## Context

A small shop with 8 products, search and category filter, a cart with
quantities, coupons SAVE10 and FREESHIP, $5 shipping free over $150,
a checkout form with validation, an order number, and order history.
The cart saves to localStorage.

## Goal

Build a cart, use coupons, fail checkout validation, place an order,
and prove the cart survives a reload.

## Steps (40)

1. Open the fixture.
2. Clear the saved cart and reload.
3. Check 8 products are shown.
4. Search for lamp.
5. Check the search leaves 1 product.
6. Clear the search.
7. Filter electronics.
8. Check 3 electronics products.
9. Clear the category filter and check 8 products again.
10. Add the Desk Lamp twice and the Headphones once.
11. Check the cart count is 3 and the subtotal is 109.97.
12. Increase the Lamp quantity.
13. Check the subtotal is 134.96.
14. Decrease the Lamp quantity.
15. Check the subtotal is back to 109.97.
16. Apply an invalid coupon.
17. Check the invalid coupon is rejected.
18. Apply SAVE10.
19. Check the discount is 11.00 and the total is 103.97.
20. Remove the Headphones.
21. Check the subtotal and total are both 49.98.
22. Open the checkout form.
23. Check the checkout form is shown.
24. Submit the empty checkout.
25. Check the empty form errors.
26. Fill name, address, city, and postcode.
27. Fill a 15-digit card, expiry, and CVC.
28. Submit with the bad card.
29. Check the card error is shown.
30. Fix the card to 16 digits and place the order.
31. Check the confirmation, order number ORD-104998, and $49.98 charged.
32. Check the cart is empty and the history has 1 order.
33. Add the Monitor to a new cart.
34. Check the subtotal is 129.99.
35. Apply FREESHIP.
36. Check shipping is 0 and the total is 129.99.
37. Reload the page.
38. Check the cart and subtotal persist after reload.
39. Clear the cart.
40. Check the cart is empty after clear.

## Pass

All 40 steps run, every money figure matches to the cent, both coupons
behave, both validation errors appear, the order number is exact, and
the cart persists after reload.

## Fail

Any step above fails, a money figure is off, a coupon is wrongly
accepted or rejected, or the order is lost.
