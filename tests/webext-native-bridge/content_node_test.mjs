#!/usr/bin/env node
// Node harness for extension/content.js. No browser needed.
// Builds a fake DOM and a fake browser.runtime, loads the real
// content.js source in a vm context, then runs every op the content
// script supports and checks the result. Each op prints one JSON
// line with wall-clock time and elapsed ms. Exit 0 when all checks
// pass, 1 otherwise.
//
// Run: node tests/webext-native-bridge/content_node_test.mjs

import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CONTENT = path.join(HERE, "extension", "content.js");

let failures = 0;

function stamp() {
  return new Date().toISOString();
}

function check(name, ok, detail) {
  const line = { wall_clock: stamp(), op: name, ok: !!ok };
  if (detail !== undefined) line.detail = detail;
  console.log(JSON.stringify(line));
  if (!ok) failures += 1;
}

// ---- Fake DOM ----

class FakeEvent {
  constructor(type, opts = {}) {
    this.type = type;
    this.bubbles = !!opts.bubbles;
    this.cancelable = !!opts.cancelable;
    this.clientX = opts.clientX || 0;
    this.clientY = opts.clientY || 0;
  }
}

class FakeElement {
  constructor(tag, fields = {}) {
    this.tagName = tag;
    this.type = fields.type || "";
    this.innerText = fields.innerText || "";
    this.href = fields.href || "";
    this.isContentEditable = !!fields.isContentEditable;
    this.options = fields.options || [];
    this.files = null;
    this.events = [];
    this.scrolledIntoView = false;
    this.focused = false;
    this.clicked = false;
    this._value = fields.value !== undefined ? fields.value : "";
  }

  getAttribute(name) {
    if (name === "type") return this.type;
    if (name === "aria-label") return "";
    return null;
  }

  getBoundingClientRect() {
    return { x: 10, y: 20, width: 100, height: 30 };
  }

  scrollIntoView() {
    this.scrolledIntoView = true;
  }

  focus() {
    this.focused = true;
  }

  click() {
    this.clicked = true;
  }

  dispatchEvent(event) {
    this.events.push(event.type);
    return true;
  }
}

Object.defineProperty(FakeElement.prototype, "value", {
  get() {
    return this._value;
  },
  set(v) {
    this._value = String(v);
  },
  configurable: true,
});

class FakeDataTransfer {
  constructor() {
    this._files = [];
    this.items = {
      add: (file) => {
        this._files.push(file);
      },
    };
  }

  get files() {
    return this._files;
  }
}

const observers = [];
class FakeMutationObserver {
  constructor(callback) {
    this.callback = callback;
    observers.push(this);
  }

  observe() {}
  disconnect() {
    const i = observers.indexOf(this);
    if (i >= 0) observers.splice(i, 1);
  }
}

function fireMutations() {
  for (const obs of [...observers]) obs.callback();
}

const registry = new Map();
function register(selector, el) {
  registry.set(selector, el);
}

const documentStub = {
  title: "Harness Page",
  documentElement: {},
  querySelector(selector) {
    return registry.get(selector) || null;
  },
  querySelectorAll() {
    return [...registry.values()];
  },
};

const windowStub = {
  location: { href: "https://example.test/page" },
  scrollX: 0,
  scrollY: 0,
  scrollTo(opts) {
    this.scrollX = opts.left || 0;
    this.scrollY = opts.top || 0;
  },
  getComputedStyle() {
    return { visibility: "visible", display: "block" };
  },
  atob(base64) {
    return Buffer.from(base64, "base64").toString("binary");
  },
  HTMLInputElement: { prototype: FakeElement.prototype },
  HTMLTextAreaElement: { prototype: FakeElement.prototype },
};

let messageHandler = null;
const browserStub = {
  runtime: {
    onMessage: {
      addListener(fn) {
        messageHandler = fn;
      },
    },
  },
};

const sandbox = {
  window: windowStub,
  document: documentStub,
  browser: browserStub,
  MutationObserver: FakeMutationObserver,
  MouseEvent: FakeEvent,
  Event: FakeEvent,
  File,
  DataTransfer: FakeDataTransfer,
  setTimeout,
  clearTimeout,
  console,
};
sandbox.window.window = windowStub;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(CONTENT, "utf-8"), sandbox, { filename: "content.js" });

if (!messageHandler) {
  console.log(JSON.stringify({ wall_clock: stamp(), op: "load", ok: false, detail: "no onMessage listener registered" }));
  process.exit(1);
}

async function run(message) {
  const started = Date.now();
  const startedWall = stamp();
  const result = await messageHandler(message);
  return { result, elapsed_ms: Date.now() - started, startedWall };
}

async function main() {
  // Fixture elements.
  const button = new FakeElement("BUTTON", { innerText: "Save" });
  const input = new FakeElement("INPUT", { type: "text", value: "" });
  const area = new FakeElement("TEXTAREA", { value: "" });
  const select = new FakeElement("SELECT", {
    options: [
      { value: "a", text: "Alpha" },
      { value: "b", text: "Beta" },
    ],
  });
  select.value = "a";
  const fileInput = new FakeElement("INPUT", { type: "file" });
  const box = new FakeElement("DIV", { innerText: "Panel" });
  register("#save", button);
  register("#name", input);
  register("#notes", area);
  register("#choice", select);
  register("#file", fileInput);
  register("#panel", box);

  let r = await run({ op: "snapshot", maxNodes: 10 });
  check("snapshot", r.result.nodes.length === 6 && r.result.title === "Harness Page", { nodes: r.result.nodes.length, elapsed_ms: r.elapsed_ms });

  r = await run({ op: "click", selector: "#save" });
  check("click", r.result.clicked === true && button.clicked && button.scrolledIntoView, r.result);

  r = await run({ op: "type", selector: "#name", text: "hello" });
  check("type-input", r.result.typed === true && input.value === "hello" && input.events.includes("input") && input.events.includes("change"), { value: input.value });

  r = await run({ op: "type", selector: "#notes", text: "note text" });
  check("type-textarea", area.value === "note text", { value: area.value });

  r = await run({ op: "scroll", selector: "#panel", behavior: "auto" });
  check("scroll-element", r.result.scrolled === true && box.scrolledIntoView, r.result);

  r = await run({ op: "scroll", x: 0, y: 400 });
  check("scroll-window", r.result.scrolled === true && r.result.scrollY === 400, r.result);

  r = await run({ op: "hover", selector: "#save" });
  check("hover", r.result.hovered === true && button.events.includes("mouseover") && button.events.includes("mousemove"), { events: button.events });

  r = await run({ op: "select", selector: "#choice", value: "b" });
  check("select", r.result.selected === true && select.value === "b" && select.events.includes("change"), r.result);

  const data = Buffer.from("hello file").toString("base64");
  r = await run({ op: "upload", selector: "#file", filename: "hello.txt", mime: "text/plain", data });
  check("upload", r.result.uploaded === true && r.result.size === 10 && r.result.filename === "hello.txt" && fileInput.files && fileInput.files.length === 1, r.result);

  r = await run({ op: "waitFor", selector: "#save", timeoutMs: 1000 });
  check("waitFor-immediate", r.result.found === true && r.result.waited_ms < 1000, r.result);

  const late = new FakeElement("BUTTON", { innerText: "Late" });
  const waitPromise = run({ op: "waitFor", selector: "#late", timeoutMs: 5000 });
  register("#late", late);
  fireMutations();
  r = await waitPromise;
  check("waitFor-mutation", r.result.found === true && r.result.tag === "button", r.result);

  let timedOut = false;
  try {
    await run({ op: "waitFor", selector: "#never", timeoutMs: 50 });
  } catch (error) {
    timedOut = String(error.message).includes("timed out");
  }
  check("waitFor-timeout", timedOut);

  r = await run({ op: "evaluate", expression: "document.title" });
  check("evaluate", r.result.value === "Harness Page", r.result);

  let missing = false;
  try {
    await run({ op: "click", selector: "#missing" });
  } catch (error) {
    missing = String(error.message).includes("no element matches");
  }
  check("click-missing-errors", missing);

  let badSelect = false;
  try {
    await run({ op: "select", selector: "#choice", value: "zzz" });
  } catch (error) {
    badSelect = String(error.message).includes("no option matches");
  }
  check("select-bad-value-errors", badSelect);

  console.log(JSON.stringify({ wall_clock: stamp(), op: "summary", ok: failures === 0, failures }));
  process.exit(failures === 0 ? 0 : 1);
}

main().catch((error) => {
  console.log(JSON.stringify({ wall_clock: stamp(), op: "harness", ok: false, detail: String(error && error.message ? error.message : error) }));
  process.exit(1);
});
