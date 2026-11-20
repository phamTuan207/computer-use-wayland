"use strict";

// Content script for the computer-use bridge extension.
// Runs in page tabs and performs DOM actions requested by the background
// script. All actions here are DOM-level: element.click() and dispatched
// input events are synthetic, so pages that check event.isTrusted will
// see them as untrusted. Real trusted input needs the OS-level keyboard
// and pointer path (see README.md), not this script.

if (!window.__cuBridgeLoaded) {
  window.__cuBridgeLoaded = true;

  const TEXT_LIMIT = 80;
  const INTERACTIVE_SELECTOR =
    "a, button, input, select, textarea, [role=button], [role=link], [onclick]";

  function trunc(text) {
    const clean = String(text || "").replace(/\s+/g, " ").trim();
    return clean.length > TEXT_LIMIT ? clean.slice(0, TEXT_LIMIT) : clean;
  }

  function isVisible(el) {
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
      return false;
    }
    const style = window.getComputedStyle(el);
    return style.visibility !== "hidden" && style.display !== "none";
  }

  function snapshot(maxNodes) {
    const limit = Math.max(1, Math.min(maxNodes || 200, 1000));
    const nodes = [];
    const elements = document.querySelectorAll(INTERACTIVE_SELECTOR);
    for (const el of elements) {
      if (nodes.length >= limit) {
        break;
      }
      if (!isVisible(el)) {
        continue;
      }
      const rect = el.getBoundingClientRect();
      nodes.push({
        ref: nodes.length,
        tag: el.tagName.toLowerCase(),
        type: el.getAttribute("type") || "",
        text: trunc(el.innerText || el.value || el.getAttribute("aria-label") || ""),
        value: el.value !== undefined ? String(el.value).slice(0, TEXT_LIMIT) : "",
        href: el.href ? String(el.href).slice(0, 200) : "",
        rect: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height),
        },
      });
    }
    return {
      title: document.title,
      url: window.location.href,
      nodes,
      truncated: elements.length > nodes.length,
    };
  }

  function find(selector) {
    const el = document.querySelector(selector);
    if (!el) {
      throw new Error("no element matches selector: " + selector);
    }
    return el;
  }

  function click(selector) {
    const el = find(selector);
    el.scrollIntoView({ block: "nearest" });
    el.focus();
    el.click();
    return {
      clicked: true,
      tag: el.tagName.toLowerCase(),
      text: trunc(el.innerText || el.value || ""),
    };
  }

  function setValue(el, text) {
    const proto = el.tagName === "TEXTAREA"
      ? window.HTMLTextAreaElement.prototype
      : window.HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
    setter.call(el, text);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function type(selector, text) {
    const el = find(selector);
    el.scrollIntoView({ block: "nearest" });
    el.focus();
    if (el.isContentEditable) {
      el.textContent = text;
      el.dispatchEvent(new Event("input", { bubbles: true }));
    } else if ("value" in el) {
      setValue(el, text);
    } else {
      throw new Error("element is not editable: " + selector);
    }
    return { typed: true, tag: el.tagName.toLowerCase(), length: text.length };
  }

  function evaluate(expression) {
    // Runs in the content script isolated world, not in page context.
    // Deliberately no eval of remote code: the expression comes from
    // the local agent only, over the loopback native host.
    const fn = new Function("return (" + expression + ")");
    const value = fn();
    if (value === undefined) {
      return { value: null, type: "undefined" };
    }
    return { value, type: typeof value };
  }

  browser.runtime.onMessage.addListener((message) => {
    try {
      switch (message.op) {
        case "snapshot":
          return Promise.resolve(snapshot(message.maxNodes));
        case "click":
          return Promise.resolve(click(message.selector));
        case "type":
          return Promise.resolve(type(message.selector, message.text || ""));
        case "evaluate":
          return Promise.resolve(evaluate(message.expression || "document.title"));
        default:
          return Promise.reject(new Error("unknown op: " + String(message.op)));
      }
    } catch (error) {
      return Promise.reject(error);
    }
  });
}
