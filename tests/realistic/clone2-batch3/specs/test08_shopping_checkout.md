# Test 08, shopping cart checkout

## Goal

Prove an agent can run a complete small shop flow in a real
browser: build a cart from a product grid, change quantities,
remove an item, handle a wrong discount code and a valid one, and
complete a validated checkout, with every money figure verified by
recomputing it in the test from the known prices and the stated
money rules, never by trusting the page arithmetic.

Fixture: fixtures/test08_shopping_checkout.html, fully offline,
inline CSS and JS. Six products: Wireless Mouse 24.50, Mechanical
Keyboard 79.99, USB Cable 9.99, Laptop Stand 45.00, Webcam 59.95,
Desk Lamp 19.99. All money is rendered with 2 decimals.

Money rules: subtotal is the sum of price times quantity over the
cart lines. SAVE10 takes 10 percent off the subtotal, rounded to
the nearest cent. FREESHIP removes the shipping fee. Shipping is
a flat 5.00 when the subtotal after discount is under 100.00, and
free at or above 100.00 after discount. Total is subtotal minus
discount plus shipping. An empty cart totals 0.00.

## Steps

1. Start the browser and load the fixture.
2. Read the product grid, expect 6 products, first product
   Wireless Mouse at 24.50.
3. Add the Wireless Mouse to the cart.
4. Add the USB Cable to the cart.
5. Read the cart, expect lines for both products, and verify
   subtotal 34.49, shipping 5.00, total 39.49 by recomputation.
6. Increase the mouse quantity to 2 with the plus control.
7. Verify the subtotal is now 58.99 and the total 63.99 by
   recomputation.
8. Decrease the mouse quantity back to 1 with the minus control.
9. Verify the subtotal is back to 34.49.
10. Add the Laptop Stand as a third product.
11. Verify subtotal 79.49 and total 84.49 by recomputation.
12. Apply the wrong code BOGUS.
13. Verify an invalid code error message, discount still 0.00,
    and the total unchanged.
14. Apply the code SAVE10.
15. Verify the discount is 7.95, the discounted subtotal is
    71.54, shipping stays 5.00 because that is under 100.00, and
    the total is 76.54, all by recomputation.
16. Remove the USB Cable line.
17. Verify subtotal 69.50, discount 6.95, shipping 5.00, total
    67.55 by recomputation, and remember this total.
18. Click place order with an empty checkout form.
19. Verify validation errors on the fields, including the card
    error saying the number must be 16 digits.
20. Fill the form with name, address, expiry 12/30 and CVC 123,
    but the invalid card number 1234.
21. Click place order again.
22. Verify the card specific error, no error on the valid name
    field, and no confirmation shown.
23. Correct the card number to 4111111111111111.
24. Click place order.
25. Verify the confirmation is shown, the order number matches
    ORD- plus 6 digits, and the confirmation total equals the
    last cart total, 67.55.
26. Verify the cart is cleared, no lines, subtotal 0.00, total
    0.00.

## Expected results

Every step ok, every check ok. Cart totals follow the recomputed
sequence 39.49, 63.99 after the quantity increase, back to 39.49,
84.49 after the third product, 76.54 after SAVE10, and 67.55
after the removal. The wrong code changes nothing. The empty
submit and the invalid card submit are both rejected with field
errors and no order. The valid submit produces an order number
in the ORD-000000 format and a confirmation total equal to the
final cart total, and the cart is empty afterwards.

## Timing

Filled after the verification runs on this machine, headless
Firefox 160.0.1, geckodriver 0.37.1, Selenium venv:

- RESULT ok: true, two consecutive full passes, final run wall
  clock 2026-11-21T11:30:56Z to 2026-11-21T11:31:20Z
- Step count: 27, including browser_start
- Checks: 19 of 19 ok, 6 of them recompute the full money
  summary in the test from prices and the shipping rule
- Total elapsed: 23.8208 s on the final run, 25.3997 s on the
  pass before it, most of both totals is cold browser start,
  11.4929 s on the first run
- Totals verified along the way, in cents as read from the page
  and recomputed in the test: 3949 after the two adds, 6399
  after the quantity increase, back to 3949 after the decrease,
  8449 after the third product, unchanged after the wrong code,
  7654 after SAVE10 with a 795 discount and 500 shipping, and
  6755 after the removal, which is also the confirmation total
  on the placed order, ORD-750351 on the first run
