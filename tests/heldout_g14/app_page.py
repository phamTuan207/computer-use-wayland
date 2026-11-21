"""Semantic locators for the Swag Labs demo shop (saucedemo.com).

Everything here is discovered from the application's own live DOM at
runtime: input placeholders, visible button text, and the app's own
class names. Nothing was invented for this test, no element id or
coordinate is baked in from outside the running page.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

BASE = "https://www.saucedemo.com/"


# ---------------------------------------------------------------- login
def username_input(d):
    return d.find_element(By.CSS_SELECTOR, "input[placeholder='Username']")


def password_input(d):
    return d.find_element(By.CSS_SELECTOR, "input[placeholder='Password']")


def login_button(d):
    return d.find_element(By.CSS_SELECTOR, "input[type='submit']")


def error_box(d):
    els = d.find_elements(By.CSS_SELECTOR, "[data-test='error']")
    return els[0] if els else None


# ------------------------------------------------------------ inventory
def inventory_items(d):
    return d.find_elements(By.CSS_SELECTOR, ".inventory_item")


def item_name(item):
    return item.find_element(By.CSS_SELECTOR, ".inventory_item_name").text


def item_price(item):
    txt = item.find_element(By.CSS_SELECTOR, ".inventory_item_price").text
    return float(txt.replace("$", "").strip())


def find_item(d, name):
    for item in inventory_items(d):
        if item_name(item) == name:
            return item
    raise LookupError(f"inventory item not found: {name}")


def item_button(item):
    return item.find_element(By.CSS_SELECTOR, "button")


def sort_select(d):
    return d.find_element(By.CSS_SELECTOR, "select.product_sort_container")


def cart_link(d):
    return d.find_element(By.CSS_SELECTOR, ".shopping_cart_link")


def cart_badge_text(d):
    els = d.find_elements(By.CSS_SELECTOR, ".shopping_cart_badge")
    return els[0].text if els else ""


# ----------------------------------------------------------------- cart
def cart_items(d):
    return d.find_elements(By.CSS_SELECTOR, ".cart_item")


def cart_item_names(d):
    return [el.text for el in
            d.find_elements(By.CSS_SELECTOR, ".cart_item .inventory_item_name")]


def button_by_text(d, text):
    """Find a clickable control by its human-visible label, whether
    the app renders it as a <button> (label = text) or as an
    <input type=submit|button> (label = value attribute)."""
    for b in d.find_elements(By.CSS_SELECTOR, "button"):
        if b.text.strip() == text:
            return b
    for b in d.find_elements(
            By.CSS_SELECTOR, "input[type='submit'], input[type='button']"):
        if (b.get_attribute("value") or "").strip() == text:
            return b
    raise LookupError(f"button not found: {text}")


# ------------------------------------------------------------- checkout
def form_input(d, placeholder):
    return d.find_element(
        By.CSS_SELECTOR, f"input[placeholder='{placeholder}']")


def summary_value(d, css):
    txt = d.find_element(By.CSS_SELECTOR, css).text
    return float(txt.split("$")[-1].strip())


# ------------------------------------------------------- action helpers
def click(m, d, desc, find, verify, **kw):
    m.act(d, "click", desc, find, lambda el: el.click(), verify, **kw)


def type_text(m, d, desc, find, text, clear_first=False):
    def do(el):
        if clear_first:
            el.click()
            el.send_keys(Keys.CONTROL, "a")
            el.send_keys(Keys.DELETE)
        el.send_keys(text)

    def verify(drv):
        return find(drv).get_attribute("value") == text

    m.act(d, "type", desc, find, do, verify)


def choose(m, d, desc, find, visible_text):
    def do(el):
        Select(el).select_by_visible_text(visible_text)

    def verify(drv):
        sel = Select(find(drv))
        return sel.first_selected_option.text == visible_text

    m.act(d, "select", desc, find, do, verify)
