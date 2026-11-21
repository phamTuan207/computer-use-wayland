#!/usr/bin/env python3
"""Test 08, shopping cart checkout, batch 3.

Drives a real offline shop in a real browser: add products, change
quantities, remove an item, try a wrong discount code, apply
SAVE10, verify every money figure by recomputing it in the test
from the known prices and the shipping rule, then run the checkout
form through empty, invalid card, and valid submissions, and
verify the order confirmation and the cleared cart.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import BrowserCase, fixture_uri

PRICES = {"p1": 2450, "p2": 7999, "p3": 999,
          "p4": 4500, "p5": 5995, "p6": 1999}
FREE_SHIP_THRESHOLD = 10000
FLAT_SHIPPING = 500


def expected_totals(cart, code=None):
    subtotal = sum(PRICES[pid] * qty for pid, qty in cart.items())
    discount = (subtotal + 5) // 10 if code == "SAVE10" else 0
    if subtotal == 0 or code == "FREESHIP" \
            or subtotal - discount >= FREE_SHIP_THRESHOLD:
        shipping = 0
    else:
        shipping = FLAT_SHIPPING
    return {"subtotal": subtotal, "discount": discount,
            "shipping": shipping,
            "total": subtotal - discount + shipping}


def cents(text):
    return int(round(float(text) * 100))


def main():
    case = BrowserCase("test08", "shopping cart checkout")
    driver = case.start_browser()
    from selenium.webdriver.common.by import By

    def read_summary():
        lines = {}
        for row in driver.find_elements(By.CSS_SELECTOR, ".cart-line"):
            pid = row.get_attribute("data-id")
            lines[pid] = {
                "qty": int(row.find_element(
                    By.CSS_SELECTOR, ".line-qty").text),
                "total": cents(row.find_element(
                    By.CSS_SELECTOR, ".line-total").text),
            }
        return {"lines": lines,
                "subtotal": cents(driver.find_element(
                    By.ID, "subtotal").text),
                "discount": cents(driver.find_element(
                    By.ID, "discount").text),
                "shipping": cents(driver.find_element(
                    By.ID, "shipping").text),
                "total": cents(driver.find_element(
                    By.ID, "total").text)}

    def totals_match(summary, cart, code=None):
        exp = expected_totals(cart, code)
        return (summary["subtotal"] == exp["subtotal"]
                and summary["discount"] == exp["discount"]
                and summary["shipping"] == exp["shipping"]
                and summary["total"] == exp["total"]), exp

    def click(css):
        driver.find_element(By.CSS_SELECTOR, css).click()

    def fill(element_id, value):
        el = driver.find_element(By.ID, element_id)
        el.clear()
        el.send_keys(value)
        return el.get_attribute("value")

    last_total = {}
    try:
        case.step("load_fixture",
                  lambda: (driver.get(fixture_uri(
                      "test08_shopping_checkout.html")), driver.title)[1])

        def read_products():
            cards = driver.find_elements(By.CSS_SELECTOR, ".product")
            first = cards[0]
            return {"count": len(cards),
                    "first_name": first.find_element(
                        By.CSS_SELECTOR, ".product-name").text,
                    "first_price": cents(first.find_element(
                        By.CSS_SELECTOR, ".product-price").text)}
        products = case.step("read_products", read_products)
        case.check("six_products", products["count"] == 6,
                   f"count={products['count']}")
        case.check("first_product_price",
                   products["first_name"] == "Wireless Mouse"
                   and products["first_price"] == PRICES["p1"],
                   f"first={products}")

        case.step("add_mouse", lambda: click("[data-add='p1']"))
        case.step("add_cable", lambda: click("[data-add='p3']"))
        summary = case.step("read_cart_after_adds", read_summary)
        ok, exp = totals_match(summary, {"p1": 1, "p3": 1})
        case.check("two_lines_after_adds",
                   set(summary["lines"]) == {"p1", "p3"}
                   and summary["lines"]["p1"]["qty"] == 1
                   and summary["lines"]["p3"]["total"] == PRICES["p3"],
                   f"lines={summary['lines']}")
        case.check("totals_after_adds_recomputed", ok,
                   f"got={summary} expected={exp}")

        case.step("increase_qty_mouse",
                  lambda: click("[data-plus='p1']"))
        summary = case.step("read_cart_after_increase", read_summary)
        ok, exp = totals_match(summary, {"p1": 2, "p3": 1})
        case.check("totals_after_qty_increase_recomputed", ok,
                   f"got={summary} expected={exp}")

        case.step("decrease_qty_mouse",
                  lambda: click("[data-minus='p1']"))
        summary = case.step("read_cart_after_decrease", read_summary)
        ok, exp = totals_match(summary, {"p1": 1, "p3": 1})
        case.check("subtotal_back_after_decrease", ok,
                   f"got={summary} expected={exp}")

        case.step("add_stand", lambda: click("[data-add='p4']"))
        summary = case.step("read_cart_after_third", read_summary)
        ok, exp = totals_match(summary, {"p1": 1, "p3": 1, "p4": 1})
        case.check("totals_after_third_product_recomputed", ok,
                   f"got={summary} expected={exp}")
        total_before_code = summary["total"]

        def apply_wrong():
            fill("discount-code", "BOGUS")
            click("#apply-code")
            return driver.find_element(By.ID, "code-message").text
        message = case.step("apply_wrong_code", apply_wrong)
        summary = case.step("read_totals_after_wrong_code", read_summary)
        case.check("wrong_code_error_shown", "Invalid" in message,
                   f"message={message!r}")
        case.check("wrong_code_no_discount_totals_unchanged",
                   summary["discount"] == 0
                   and summary["total"] == total_before_code,
                   f"summary={summary} before={total_before_code}")

        def apply_save10():
            fill("discount-code", "SAVE10")
            click("#apply-code")
            return driver.find_element(By.ID, "code-message").text
        message = case.step("apply_save10", apply_save10)
        summary = case.step("read_totals_after_save10", read_summary)
        ok, exp = totals_match(summary, {"p1": 1, "p3": 1, "p4": 1},
                               code="SAVE10")
        case.check("save10_discount_and_total_recomputed", ok,
                   f"got={summary} expected={exp} message={message!r}")
        case.check("save10_shipping_rule_applied",
                   summary["shipping"] == FLAT_SHIPPING
                   and summary["subtotal"] - summary["discount"]
                   < FREE_SHIP_THRESHOLD,
                   f"shipping={summary['shipping']}")

        case.step("remove_cable", lambda: click("[data-remove='p3']"))
        summary = case.step("read_totals_after_remove", read_summary)
        ok, exp = totals_match(summary, {"p1": 1, "p4": 1},
                               code="SAVE10")
        case.check("totals_after_remove_recomputed", ok,
                   f"got={summary} expected={exp}")
        last_total["value"] = summary["total"]

        case.step("submit_empty_checkout",
                  lambda: click("#place-order"))

        def read_errors():
            return {eid: driver.find_element(By.ID, eid).text
                    for eid in ("err-name", "err-address", "err-card",
                                "err-expiry", "err-cvc")}
        errors = case.step("read_validation_errors", read_errors)
        case.check("empty_submit_shows_field_errors",
                   all(errors[e] for e in
                       ("err-name", "err-address", "err-expiry",
                        "err-cvc")),
                   f"errors={errors}")
        case.check("empty_submit_card_error",
                   "16 digits" in errors["err-card"],
                   f"card_error={errors['err-card']!r}")

        def fill_invalid():
            fill("co-name", "Test Buyer")
            fill("co-address", "1 Example Street")
            fill("co-card", "1234")
            fill("co-expiry", "12/30")
            fill("co-cvc", "123")
            return "filled"
        case.step("fill_form_invalid_card", fill_invalid)
        case.step("submit_invalid_card",
                  lambda: click("#place-order"))

        def invalid_state():
            return {"card_error": driver.find_element(
                        By.ID, "err-card").text,
                    "name_error": driver.find_element(
                        By.ID, "err-name").text,
                    "confirmation_shown": driver.find_element(
                        By.ID, "confirmation").is_displayed()}
        state = case.step("verify_invalid_card_state", invalid_state)
        case.check("invalid_card_error_specific",
                   "16 digits" in state["card_error"]
                   and state["name_error"] == "",
                   f"state={state}")
        case.check("no_confirmation_for_invalid_card",
                   state["confirmation_shown"] is False,
                   f"state={state}")

        case.step("fix_card_number",
                  lambda: fill("co-card", "4111111111111111"))
        case.step("place_order_valid", lambda: click("#place-order"))

        def read_confirmation():
            return {"shown": driver.find_element(
                        By.ID, "confirmation").is_displayed(),
                    "number": driver.find_element(
                        By.ID, "order-number").text,
                    "total": cents(driver.find_element(
                        By.ID, "order-total").text)}
        conf = case.step("read_confirmation", read_confirmation)
        case.check("order_number_format",
                   conf["shown"]
                   and re.match(r"^ORD-\d{6}$", conf["number"])
                   is not None,
                   f"conf={conf}")
        case.check("confirmation_total_matches_last_cart_total",
                   conf["total"] == last_total["value"],
                   f"conf_total={conf['total']} "
                   f"last_cart_total={last_total['value']}")

        summary = case.step("read_cart_after_order", read_summary)
        case.check("cart_cleared_after_order",
                   summary["lines"] == {}
                   and summary["subtotal"] == 0
                   and summary["total"] == 0,
                   f"summary={summary}")
    except Exception as exc:
        print(f"  test aborted: {type(exc).__name__}: {exc}", flush=True)
        case.check("test_completed_without_abort", False,
                   f"aborted: {type(exc).__name__}: {exc}")

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())
