"""G14 held-out validation: 5 realistic tasks on a real third-party
web app (Swag Labs demo shop, https://www.saucedemo.com/), executed
by a fresh agent with DOM-semantics location only.

Run:  ~/workspace/tools/venv/bin/python tests/heldout_g14/run_tasks.py
Writes results.json next to this file and prints a summary.
"""

import datetime
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selenium.webdriver.common.by import By

import app_page as P
from driver_lib import Metrics, TaskFail, make_driver, wait_for

HERE = os.path.dirname(os.path.abspath(__file__))


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def login(m, d, user="standard_user", password="secret_sauce"):
    P.type_text(m, d, "type username", P.username_input, user)
    P.type_text(m, d, "type password", P.password_input, password)
    P.click(m, d, "click Login", P.login_button,
            lambda drv: drv.current_url.endswith("/inventory.html")
            and len(P.inventory_items(drv)) > 0)


# --------------------------------------------------------------- task 1
def task1_checkout_happy_path(m, d):
    """Multi-field workflow: login, add two products, complete the
    checkout form, verify the money on the overview from prices read
    live in the inventory, finish the order."""
    d.get(P.BASE)
    login(m, d)
    prices = {}
    for name, badge in (("Sauce Labs Backpack", "1"),
                        ("Sauce Labs Bike Light", "2")):
        prices[name] = P.item_price(P.find_item(d, name))
        P.click(m, d, f"add '{name}' to cart",
                lambda drv, n=name: P.item_button(P.find_item(drv, n)),
                lambda drv, n=name, b=badge:
                    P.item_button(P.find_item(drv, n)).text == "Remove"
                    and P.cart_badge_text(drv) == b)
    P.click(m, d, "open cart", P.cart_link,
            lambda drv: drv.current_url.endswith("/cart.html")
            and len(P.cart_items(drv)) == 2)
    P.click(m, d, "click Checkout",
            lambda drv: P.button_by_text(drv, "Checkout"),
            lambda drv: "checkout-step-one" in drv.current_url)
    P.type_text(m, d, "type first name",
                lambda drv: P.form_input(drv, "First Name"), "Ada")
    P.type_text(m, d, "type last name",
                lambda drv: P.form_input(drv, "Last Name"), "Lovelace")
    P.type_text(m, d, "type postal code",
                lambda drv: P.form_input(drv, "Zip/Postal Code"), "12345")
    P.click(m, d, "click Continue",
            lambda drv: P.button_by_text(drv, "Continue"),
            lambda drv: "checkout-step-two" in drv.current_url)
    subtotal = P.summary_value(d, ".summary_subtotal_label")
    tax = P.summary_value(d, ".summary_tax_label")
    total = P.summary_value(d, ".summary_total_label")
    exp_sub = round(sum(prices.values()), 2)
    exp_tax = round(exp_sub * 0.08, 2)
    if not (abs(subtotal - exp_sub) < 0.005 and abs(tax - exp_tax) < 0.005
            and abs(total - round(exp_sub + exp_tax, 2)) < 0.005):
        raise TaskFail(
            f"overview money mismatch: page subtotal {subtotal}, tax "
            f"{tax}, total {total}; expected from live inventory "
            f"prices {exp_sub}, {exp_tax}, {round(exp_sub + exp_tax, 2)}")
    P.click(m, d, "click Finish",
            lambda drv: P.button_by_text(drv, "Finish"),
            lambda drv: "checkout-complete" in drv.current_url)
    header = d.find_element(By.CSS_SELECTOR, ".complete-header").text
    if "Thank you" not in header:
        raise TaskFail(f"unexpected completion header: {header!r}")
    return {"prices_read_live": prices, "subtotal": subtotal,
            "tax": tax, "total": total, "header": header}


# --------------------------------------------------------------- task 2
def task2_sort_find_detail(m, d):
    """Sort the catalogue by price, find the cheapest record, open its
    detail view, check the record is consistent across views, and add
    it to the cart from the detail view."""
    d.get(P.BASE)
    login(m, d)
    P.choose(m, d, "sort by Price (low to high)", P.sort_select,
             "Price (low to high)")

    def prices_ascending(drv):
        ps = [P.item_price(it) for it in P.inventory_items(drv)]
        return ps == sorted(ps) and len(ps) >= 6

    if not wait_for(d, prices_ascending, 5):
        raise TaskFail("inventory did not settle into ascending prices")
    first = P.inventory_items(d)[0]
    name, price = P.item_name(first), P.item_price(first)
    P.click(m, d, f"open detail of '{name}'",
            lambda drv: P.find_item(drv, name).find_element(
                By.CSS_SELECTOR, ".inventory_item_name"),
            lambda drv: "inventory-item.html" in drv.current_url)
    det_name = d.find_element(
        By.CSS_SELECTOR, ".inventory_details_name").text
    det_price = float(d.find_element(
        By.CSS_SELECTOR, ".inventory_details_price").text
        .replace("$", "").strip())
    if det_name != name or abs(det_price - price) > 0.005:
        raise TaskFail(
            f"detail record mismatch: inventory ({name}, {price}) vs "
            f"detail ({det_name}, {det_price})")
    P.click(m, d, "add to cart from detail",
            lambda drv: P.button_by_text(drv, "Add to cart"),
            lambda drv: P.button_by_text(drv, "Remove") is not None
            and P.cart_badge_text(drv) == "1")
    P.click(m, d, "back to products",
            lambda drv: P.button_by_text(drv, "Back to products"),
            lambda drv: drv.current_url.endswith("/inventory.html"))
    if P.cart_badge_text(d) != "1":
        raise TaskFail("cart badge lost after returning to inventory")
    return {"cheapest_item": name, "price": price,
            "detail_price": det_price}


# --------------------------------------------------------------- task 3
def task3_sort_subset_cart_edit(m, d):
    """Sort by name Z to A, take the first two records of that subset
    ordering, add both, verify the cart holds exactly those records,
    then remove one and verify what remains."""
    d.get(P.BASE)
    login(m, d)
    P.choose(m, d, "sort by Name (Z to A)", P.sort_select, "Name (Z to A)")

    def names_descending(drv):
        ns = [P.item_name(it) for it in P.inventory_items(drv)]
        return ns == sorted(ns, reverse=True) and len(ns) >= 6

    if not wait_for(d, names_descending, 5):
        raise TaskFail("inventory did not settle into Z to A order")
    names = [P.item_name(it) for it in P.inventory_items(d)]
    n1, n2 = names[0], names[1]
    for name, badge in ((n1, "1"), (n2, "2")):
        P.click(m, d, f"add '{name}' to cart",
                lambda drv, n=name: P.item_button(P.find_item(drv, n)),
                lambda drv, n=name, b=badge:
                    P.item_button(P.find_item(drv, n)).text == "Remove"
                    and P.cart_badge_text(drv) == b)
    P.click(m, d, "open cart", P.cart_link,
            lambda drv: drv.current_url.endswith("/cart.html"))
    in_cart = P.cart_item_names(d)
    if sorted(in_cart) != sorted([n1, n2]):
        raise TaskFail(f"cart contents {in_cart} != expected {[n1, n2]}")

    def remove_btn(drv):
        for it in P.cart_items(drv):
            nm = it.find_element(
                By.CSS_SELECTOR, ".inventory_item_name").text
            if nm == n1:
                return it.find_element(By.CSS_SELECTOR, "button")
        raise LookupError("cart item not found")

    P.click(m, d, f"remove '{n1}' from cart", remove_btn,
            lambda drv: P.cart_item_names(drv) == [n2]
            and P.cart_badge_text(drv) == "1")
    return {"sorted_first_two": [n1, n2], "cart_after_remove": [n2]}


# --------------------------------------------------------------- task 4
def task4_login_error_recovery(m, d):
    """Error state: the locked-out account is rejected with an error
    banner. Recover by switching to a working account and logging in
    for real."""
    d.get(P.BASE)
    P.type_text(m, d, "type username", P.username_input, "locked_out_user")
    P.type_text(m, d, "type password", P.password_input, "secret_sauce")
    P.click(m, d, "click Login with locked-out user", P.login_button,
            lambda drv: (P.error_box(drv) is not None
                         and "locked out" in P.error_box(drv).text
                         and len(P.inventory_items(drv)) == 0))
    err = P.error_box(d).text
    P.type_text(m, d, "replace username with standard_user",
                P.username_input, "standard_user", clear_first=True)
    if P.password_input(d).get_attribute("value") != "secret_sauce":
        P.type_text(m, d, "retype password", P.password_input,
                    "secret_sauce", clear_first=True)
    P.click(m, d, "click Login with standard_user", P.login_button,
            lambda drv: drv.current_url.endswith("/inventory.html")
            and len(P.inventory_items(drv)) == 6)
    return {"locked_out_error": err, "items_after_recovery":
            len(P.inventory_items(d))}


# --------------------------------------------------------------- task 5
def task5_checkout_error_and_cross_view_value(m, d):
    """Read a price in the inventory view, carry it into checkout.
    First hit the form validation error (missing postal code),
    recover, then verify the overview money against the price read
    earlier in the other view."""
    d.get(P.BASE)
    login(m, d)
    name = "Sauce Labs Fleece Jacket"
    price = P.item_price(P.find_item(d, name))
    P.click(m, d, f"add '{name}' to cart",
            lambda drv: P.item_button(P.find_item(drv, name)),
            lambda drv: P.cart_badge_text(drv) == "1")
    P.click(m, d, "open cart", P.cart_link,
            lambda drv: drv.current_url.endswith("/cart.html"))
    P.click(m, d, "click Checkout",
            lambda drv: P.button_by_text(drv, "Checkout"),
            lambda drv: "checkout-step-one" in drv.current_url)
    P.type_text(m, d, "type first name",
                lambda drv: P.form_input(drv, "First Name"), "Grace")
    P.type_text(m, d, "type last name",
                lambda drv: P.form_input(drv, "Last Name"), "Hopper")
    P.click(m, d, "click Continue with postal code missing",
            lambda drv: P.button_by_text(drv, "Continue"),
            lambda drv: (P.error_box(drv) is not None
                         and "Postal Code is required"
                         in P.error_box(drv).text
                         and "checkout-step-one" in drv.current_url))
    err = P.error_box(d).text
    P.type_text(m, d, "type postal code after error",
                lambda drv: P.form_input(drv, "Zip/Postal Code"), "98765")
    P.click(m, d, "click Continue after fixing form",
            lambda drv: P.button_by_text(drv, "Continue"),
            lambda drv: "checkout-step-two" in drv.current_url)
    subtotal = P.summary_value(d, ".summary_subtotal_label")
    tax = P.summary_value(d, ".summary_tax_label")
    total = P.summary_value(d, ".summary_total_label")
    exp_tax = round(price * 0.08, 2)
    if not (abs(subtotal - price) < 0.005 and abs(tax - exp_tax) < 0.005
            and abs(total - round(price + exp_tax, 2)) < 0.005):
        raise TaskFail(
            f"overview money mismatch: page subtotal {subtotal}, tax "
            f"{tax}, total {total}; expected from inventory price "
            f"{price}: tax {exp_tax}, total {round(price + exp_tax, 2)}")
    return {"inventory_price": price, "validation_error": err,
            "subtotal": subtotal, "tax": tax, "total": total}


TASKS = [
    ("task1_checkout_happy_path", task1_checkout_happy_path),
    ("task2_sort_find_detail", task2_sort_find_detail),
    ("task3_sort_subset_cart_edit", task3_sort_subset_cart_edit),
    ("task4_login_error_recovery", task4_login_error_recovery),
    ("task5_checkout_error_and_cross_view_value",
     task5_checkout_error_and_cross_view_value),
]


def main():
    results = []
    for task_id, fn in TASKS:
        m = Metrics()
        wall_start = utcnow()
        t0 = time.perf_counter()
        status, detail, failure = "PASS", {}, None
        driver = make_driver()
        try:
            detail = fn(m, driver) or {}
        except Exception as exc:
            status = "FAIL"
            failure = f"{type(exc).__name__}: {exc}"
        finally:
            try:
                driver.quit()
            except Exception:
                pass
        elapsed = round(time.perf_counter() - t0, 3)
        rec = {"task": task_id, "status": status,
               "wall_start": wall_start, "wall_end": utcnow(),
               "elapsed_s": elapsed,
               "actions_attempted": m.attempts, "misses": m.misses,
               "retries": m.retries, "miss_log": m.log,
               "detail": detail, "failure": failure}
        results.append(rec)
        print(f"{task_id}: {status} attempts={m.attempts} "
              f"misses={m.misses} retries={m.retries} "
              f"elapsed={elapsed}s", flush=True)
        if failure:
            print(f"  failure: {failure}", flush=True)
    tot_a = sum(r["actions_attempted"] for r in results)
    tot_m = sum(r["misses"] for r in results)
    summary = {"app": "Swag Labs (saucedemo.com)",
               "tasks": results,
               "total_actions_attempted": tot_a, "total_misses": tot_m,
               "hit_rate": round((tot_a - tot_m) / tot_a, 4) if tot_a
               else None,
               "tasks_passed": sum(1 for r in results
                                   if r["status"] == "PASS")}
    with open(os.path.join(HERE, "results.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps({k: summary[k] for k in
                      ("total_actions_attempted", "total_misses",
                       "hit_rate", "tasks_passed")}, indent=2))
    return 0 if summary["tasks_passed"] == len(TASKS) else 1


if __name__ == "__main__":
    sys.exit(main())
