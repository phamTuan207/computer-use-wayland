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

  function scrollToTarget(selector, x, y, behavior) {
    const mode = behavior === "smooth" ? "smooth" : "auto";
    if (selector) {
      const el = find(selector);
      el.scrollIntoView({ block: "center", behavior: mode });
      const rect = el.getBoundingClientRect();
      return {
        scrolled: true,
        target: "element",
        scrollX: Math.round(window.scrollX),
        scrollY: Math.round(window.scrollY),
        rect: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height),
        },
      };
    }
    window.scrollTo({
      left: Number(x) || 0,
      top: Number(y) || 0,
      behavior: mode,
    });
    return {
      scrolled: true,
      target: "window",
      scrollX: Math.round(window.scrollX),
      scrollY: Math.round(window.scrollY),
    };
  }

  function hover(selector) {
    const el = find(selector);
    const rect = el.getBoundingClientRect();
    const cx = rect.x + rect.width / 2;
    const cy = rect.y + rect.height / 2;
    const opts = {
      bubbles: true,
      cancelable: true,
      clientX: cx,
      clientY: cy,
      view: window,
    };
    el.dispatchEvent(new MouseEvent("mouseover", opts));
    el.dispatchEvent(new MouseEvent("mouseenter", { bubbles: false, cancelable: true, clientX: cx, clientY: cy, view: window }));
    el.dispatchEvent(new MouseEvent("mousemove", opts));
    return {
      hovered: true,
      tag: el.tagName.toLowerCase(),
      text: trunc(el.innerText || el.value || ""),
      rect: {
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      },
    };
  }

  function selectOption(selector, value) {
    const el = find(selector);
    if (el.tagName !== "SELECT") {
      throw new Error("element is not a select: " + selector);
    }
    const wanted = String(value);
    const option = Array.from(el.options).find(
      (opt) => opt.value === wanted || opt.text === wanted
    );
    if (!option) {
      throw new Error("no option matches value: " + wanted);
    }
    el.value = option.value;
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    return {
      selected: true,
      tag: "select",
      value: el.value,
      text: option.text,
    };
  }

  function base64ToBytes(base64) {
    const binary = window.atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }

  function upload(selector, filename, mime, dataBase64) {
    const el = find(selector);
    if (el.tagName !== "INPUT" || el.type !== "file") {
      throw new Error("element is not a file input: " + selector);
    }
    if (!dataBase64 || typeof dataBase64 !== "string") {
      throw new Error("upload needs base64 file data in field data");
    }
    // Content scripts cannot read a path from disk, so the agent sends
    // the file bytes as base64 and the file is rebuilt here. The file
    // input then holds a real File object, so forms and change handlers
    // see a normal user-style selection, except the event is synthetic.
    const bytes = base64ToBytes(dataBase64);
    const file = new File([bytes], filename || "upload.bin", {
      type: mime || "application/octet-stream",
    });
    const transfer = new DataTransfer();
    transfer.items.add(file);
    el.files = transfer.files;
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    return {
      uploaded: true,
      tag: "input",
      filename: file.name,
      size: file.size,
      type: file.type,
    };
  }

  function waitFor(selector, timeoutMs) {
    const timeout = Math.max(0, Math.min(timeoutMs || 5000, 120000));
    const started = Date.now();
    return new Promise((resolve, reject) => {
      const check = () => {
        const el = document.querySelector(selector);
        if (el && isVisible(el)) {
          const rect = el.getBoundingClientRect();
          resolve({
            found: true,
            tag: el.tagName.toLowerCase(),
            text: trunc(el.innerText || el.value || ""),
            waited_ms: Date.now() - started,
            rect: {
              x: Math.round(rect.x),
              y: Math.round(rect.y),
              width: Math.round(rect.width),
              height: Math.round(rect.height),
            },
          });
          return true;
        }
        return false;
      };
      if (check()) {
        return;
      }
      const timer = setTimeout(() => {
        observer.disconnect();
        reject(
          new Error(
            "waitFor timed out after " + timeout + " ms: " + selector
          )
        );
      }, timeout);
      const observer = new MutationObserver(() => {
        if (check()) {
          clearTimeout(timer);
          observer.disconnect();
        }
      });
      observer.observe(document.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
      });
    });
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
        case "scroll":
          return Promise.resolve(
            scrollToTarget(message.selector, message.x, message.y, message.behavior)
          );
        case "hover":
          return Promise.resolve(hover(message.selector));
        case "select":
          return Promise.resolve(selectOption(message.selector, message.value));
        case "upload":
          return Promise.resolve(
            upload(message.selector, message.filename, message.mime, message.data)
          );
        case "waitFor":
          return waitFor(message.selector, message.timeoutMs);
        default:
          return Promise.reject(new Error("unknown op: " + String(message.op)));
      }
    } catch (error) {
      return Promise.reject(error);
    }
  });
}
