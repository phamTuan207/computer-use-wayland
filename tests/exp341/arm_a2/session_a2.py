#!/usr/bin/env python3
"""Arm A-prime session: same Session harness as arms A and B, but the
observation is the full DOM picture a real DOM-reading agent gets.

The original arm A observe() returned only title, body text, and
input id/value/checked. It never returned button attributes, so arm
A could not see the task 5 trap button's data-action before
clicking, no matter how competently it reasoned. This override
returns, per observation:

- title and visible body text
- inputs: id, tag, type, name, value, checked, associated label
  text, and for selects the full option list (value, text, selected)
- buttons: id, label text, data-action attribute, CSS class, and
  the text of the containing element (product context for the
  cart Add buttons)
- errors: text of error or alert elements, by id

Counting is unchanged: one observe() call is one observation, the
final checker read is not counted, actions and retries count
exactly as in common.Session.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common import Session

OBSERVE_JS = """
function lab(e) {
  if (e.id) {
    var l = document.querySelector('label[for="' + e.id + '"]');
    if (l) return l.textContent.trim();
  }
  var p = e.closest ? e.closest('label') : null;
  return p ? p.textContent.trim() : '';
}
function ctx(e) {
  var p = e.parentElement;
  return p ? (p.textContent || '').trim().slice(0, 160) : '';
}
return {
  title: document.title,
  text: document.body ? document.body.innerText.slice(0, 3000) : '',
  inputs: Array.prototype.map.call(
    document.querySelectorAll('input,select,textarea'), function (e) {
      var o = {id: e.id, tag: e.tagName.toLowerCase(),
               type: e.type || '', name: e.name || '',
               value: e.value, checked: !!e.checked, label: lab(e)};
      if (e.tagName === 'SELECT') {
        o.options = Array.prototype.map.call(e.options, function (op) {
          return {value: op.value, text: op.textContent.trim(),
                  selected: op.selected};
        });
      }
      return o;
    }),
  buttons: Array.prototype.map.call(
    document.querySelectorAll('button, input[type=button], input[type=submit]'),
    function (e) {
      return {id: e.id, label: (e.textContent || e.value || '').trim(),
              dataAction: e.getAttribute('data-action'),
              cls: e.className || '', context: ctx(e)};
    }),
  errors: Array.prototype.map.call(
    document.querySelectorAll('[id^="err"], .error, [role="alert"]'),
    function (e) { return {id: e.id, text: (e.textContent || '').trim()}; })
};
"""


class A2Session(Session):
    """Session whose observe() returns the rich payload above."""

    def observe(self):
        self.observations += 1
        return self.driver.execute_script(OBSERVE_JS)


# --- lookups over one observation payload -------------------------
# Every decision in the driver is computed from these helpers over
# the latest payload, never from page facts baked into the script.

def input_by_label(obs, needle, types=None):
    for inp in obs["inputs"]:
        if needle.lower() in inp["label"].lower():
            if types is None or inp["type"] in types:
                return inp
    return None


def input_by_id(obs, element_id):
    for inp in obs["inputs"]:
        if inp["id"] == element_id:
            return inp
    return None


def button_by_label(obs, needle):
    for btn in obs["buttons"]:
        if needle.lower() in btn["label"].lower():
            return btn
    return None


def button_by_context(obs, needle, label_needle=None):
    for btn in obs["buttons"]:
        if needle.lower() in btn["context"].lower():
            if label_needle is None or label_needle.lower() in btn["label"].lower():
                return btn
    return None


def active_errors(obs):
    return [e for e in obs["errors"] if e["text"]]
