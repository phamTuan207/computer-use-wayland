// t08-cart-checkout check. Searches and filters the catalog, builds a
// cart, changes quantities, applies coupons, fails checkout validation
// twice, places an order, and proves the cart persists after reload.
// Prints one JSON result line. Exit 0 on pass, 1 on fail.
// Usage: node check.mjs  (FIXTURE_BASE_URL optional, see README)
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { launchBrowser, nowIso } from '../lib/browser.mjs';
import { serveDir } from '../lib/server.mjs';

const testDir = path.dirname(fileURLToPath(import.meta.url));
const testName = path.basename(testDir);
const startedAt = nowIso();
const started = Date.now();
const failures = [];
const steps = [];
let details = {};
let stepCount = 0;
function step(name) { stepCount += 1; steps.push(stepCount + '. ' + name); }
function check(cond, msg) { if (!cond) failures.push(msg); }

let browser = null;
let closeServer = null;
try {
  let fixtureUrl;
  if (process.env.FIXTURE_BASE_URL) {
    fixtureUrl = process.env.FIXTURE_BASE_URL.replace(/\/$/, '') + '/' + testName + '/fixture.html';
  } else {
    const server = await serveDir(testDir);
    fixtureUrl = server.url + '/fixture.html';
    closeServer = server.close;
  }
  browser = await launchBrowser();
  const page = await browser.newPage();
  await page.goto(fixtureUrl); step('open fixture');
  await page.evaluate(() => { localStorage.removeItem('cart'); localStorage.removeItem('coupon'); localStorage.removeItem('orders'); });
  await page.reload(); step('clear saved cart and reload');
  const prodCount = () => page.evaluate(() => document.querySelectorAll('#products .product').length);
  const num = (sel) => page.evaluate((s) => Number(document.getElementById(s).textContent), sel);
  check((await prodCount()) === 8, 'catalog should show 8 products'); step('check 8 products shown');
  await page.fill('#search', 'lamp'); step('search for lamp');
  check((await prodCount()) === 1, 'search should leave 1 product'); step('check search leaves 1 product');
  await page.fill('#search', ''); step('clear search');
  await page.selectOption('#category', 'electronics'); step('filter electronics');
  check((await prodCount()) === 3, 'electronics should show 3 products'); step('check 3 electronics products');
  await page.selectOption('#category', '');
  check((await prodCount()) === 8, 'catalog should show 8 again'); step('clear category filter, check 8 products');
  const addBtn = (id) => page.locator('.product[data-id="' + id + '"] .addBtn');
  await addBtn('p1').click();
  await addBtn('p1').click();
  await addBtn('p2').click(); step('add Desk Lamp twice and Headphones once');
  check((await num('cartCount')) === 3, 'cart count should be 3');
  check((await num('subtotal')) === 109.97, 'subtotal should be 109.97, got ' + (await num('subtotal'))); step('check cart count is 3, subtotal is 109.97');
  await page.locator('#cartItems li[data-id="p1"] .plusBtn').click(); step('increase Lamp quantity');
  check((await num('subtotal')) === 134.96, 'subtotal should be 134.96 after plus'); step('check subtotal is 134.96');
  await page.locator('#cartItems li[data-id="p1"] .minusBtn').click(); step('decrease Lamp quantity');
  check((await num('subtotal')) === 109.97, 'subtotal should be back to 109.97'); step('check subtotal back to 109.97');
  await page.fill('#coupon', 'NOPE');
  await page.click('#applyCoupon'); step('apply invalid coupon');
  const couponMsg1 = (await page.textContent('#couponMsg')) || '';
  check(couponMsg1.includes('Invalid coupon'), 'expected invalid coupon message, got: ' + couponMsg1); step('check invalid coupon rejected');
  await page.fill('#coupon', 'SAVE10');
  await page.click('#applyCoupon'); step('apply SAVE10');
  check((await num('discount')) === 11.00, 'discount should be 11.00, got ' + (await num('discount')));
  check((await num('total')) === 103.97, 'total should be 103.97, got ' + (await num('total'))); step('check discount is 11.00, total is 103.97');
  await page.locator('#cartItems li[data-id="p2"] .removeBtn').click(); step('remove Headphones');
  check((await num('subtotal')) === 49.98, 'subtotal should be 49.98 after remove');
  check((await num('total')) === 49.98, 'total should be 49.98 after remove'); step('check subtotal and total are 49.98');
  await page.click('#checkoutBtn'); step('open checkout form');
  check(await page.isVisible('#checkoutForm'), 'checkout form should show'); step('check checkout form shown');
  await page.click('#placeOrderBtn'); step('submit empty checkout');
  const err1 = (await page.textContent('#formErrors')) || '';
  check(err1.includes('name is required'), 'expected name error, got: ' + err1); step('check empty form errors');
  await page.fill('#coName', 'Ada Lovelace');
  await page.fill('#coAddress', '12 Analytical Way');
  await page.fill('#coCity', 'London');
  await page.fill('#coPostcode', 'E1 6AN'); step('fill name, address, city, postcode');
  await page.fill('#coCard', '424242424242424');
  await page.fill('#coExpiry', '12/28');
  await page.fill('#coCvc', '123'); step('fill 15-digit card, expiry, CVC');
  await page.click('#placeOrderBtn'); step('submit with bad card');
  const err2 = (await page.textContent('#formErrors')) || '';
  check(err2.includes('card number must be 16 digits'), 'expected card error, got: ' + err2); step('check card error shown');
  await page.fill('#coCard', '4242424242424242');
  await page.click('#placeOrderBtn'); step('fix card to 16 digits, place the order');
  check(await page.isVisible('#confirmation'), 'confirmation should show');
  const orderNum = (await page.textContent('#orderNumber')) || '';
  check(/ORD-\d{6}/.test(orderNum), 'order number format wrong: ' + orderNum);
  check(orderNum.includes('ORD-104998'), 'order number should be ORD-104998, got: ' + orderNum);
  const charged = (await page.textContent('#orderTotal')) || '';
  check(charged.includes('49.98'), 'charged amount should be 49.98, got: ' + charged); step('check confirmation, order ORD-104998, $49.98 charged');
  details = { orderNum: orderNum.trim() };
  check((await num('cartCount')) === 0, 'cart should be empty after order');
  check((await page.evaluate(() => document.querySelectorAll('#orders li').length)) === 1, 'order history should have 1 order'); step('check cart empty, history has 1 order');
  await addBtn('p6').click(); step('add Monitor to new cart');
  check((await num('subtotal')) === 129.99, 'subtotal should be 129.99'); step('check Monitor subtotal is 129.99');
  await page.fill('#coupon', 'FREESHIP');
  await page.click('#applyCoupon'); step('apply FREESHIP');
  check((await num('shipping')) === 0, 'shipping should be 0 with FREESHIP');
  check((await num('total')) === 129.99, 'total should be 129.99 with free shipping'); step('check shipping 0, total 129.99');
  await page.reload(); step('reload page');
  check((await num('cartCount')) === 1, 'cart should persist after reload');
  check((await num('subtotal')) === 129.99, 'subtotal should persist after reload'); step('check cart and subtotal persist after reload');
  await page.click('#clearCartBtn'); step('clear the cart');
  check((await num('cartCount')) === 0, 'cart should be empty after clear'); step('check cart empty after clear');
  check(stepCount >= 15 && stepCount <= 40, 'step count ' + stepCount + ' outside 15-40');
} catch (err) {
  failures.push(String(err && err.message ? err.message : err));
} finally {
  if (browser) await browser.close();
  if (closeServer) await closeServer();
}

const result = {
  test: testName,
  pass: failures.length === 0,
  failures,
  details,
  steps,
  started_at: startedAt,
  finished_at: nowIso(),
  elapsed_ms: Date.now() - started,
};
console.log(JSON.stringify(result));
process.exit(result.pass ? 0 : 1);
