#!/usr/bin/env node
/**
 * cdp_client.mjs - minimal Chrome DevTools Protocol client for the Discord
 * desktop client (Electron). Uses Node's built-in global WebSocket (Node >= 22)
 * and fetch. No npm dependencies.
 *
 * Usage:
 *   node cdp_client.mjs targets [port]            # GET /json/list
 *   node cdp_client.mjs version [port]            # GET /json/version
 *   node cdp_client.mjs eval <wsUrl>              # Runtime.evaluate, JS read from stdin
 *   node cdp_client.mjs navigate <wsUrl> <url>    # Page.navigate
 *   node cdp_client.mjs send <wsUrl> <text>       # focus composer, insert text, press Enter
 *   node cdp_client.mjs sendfile <wsUrl> <path> [text]
 *                                                 # DOM.setFileInputFiles + optional caption + Enter
 *
 * Every command prints one JSON object on stdout and exits 0 on success,
 * non-zero with {"ok": false, "error": ...} on failure.
 */
import { readFileSync } from "node:fs";

const CDP_PORT = process.env.DISCORD_CDP_PORT || "9229";

function fail(msg) {
  console.log(JSON.stringify({ ok: false, error: String(msg) }));
  process.exit(1);
}

function out(obj) {
  console.log(JSON.stringify(obj));
  process.exit(0);
}

async function httpJson(path, port = CDP_PORT) {
  const res = await fetch(`http://127.0.0.1:${port}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status} on ${path}`);
  return res.json();
}

class CdpSession {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.ws.addEventListener("message", (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch { return; }
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message || JSON.stringify(msg.error)));
        else resolve(msg.result);
      }
    });
    this.ws.addEventListener("error", (e) => {
      for (const { reject } of this.pending.values()) reject(new Error("WebSocket error"));
      this.pending.clear();
    });
  }
  ready() {
    return new Promise((resolve, reject) => {
      if (this.ws.readyState === WebSocket.OPEN) return resolve();
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
      setTimeout(() => reject(new Error("WebSocket connect timeout")), 10000);
    });
  }
  call(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`CDP timeout on ${method}`));
        }
      }, 30000);
    });
  }
  async evaluate(expression) {
    const r = await this.call("Runtime.evaluate", {
      expression, awaitPromise: true, returnByValue: true,
    });
    if (r.exceptionDetails) {
      throw new Error("JS exception: " + JSON.stringify(r.exceptionDetails).exception?.description
        || JSON.stringify(r.exceptionDetails));
    }
    return r.result ? r.result.value : undefined;
  }
  close() { try { this.ws.close(); } catch { /* ignore */ } }
}

async function connect(wsUrl) {
  const s = new CdpSession(wsUrl);
  await s.ready();
  await s.call("Runtime.enable");
  await s.call("Page.enable");
  return s;
}

async function main() {
  const [cmd, ...args] = process.argv.slice(2);
  try {
    if (cmd === "targets") {
      out({ ok: true, targets: await httpJson("/json/list", args[0]) });
    } else if (cmd === "version") {
      out({ ok: true, ...(await httpJson("/json/version", args[0])) });
    } else if (cmd === "eval") {
      const [wsUrl] = args;
      const expr = readFileSync(0, "utf8");
      const s = await connect(wsUrl);
      try { out({ ok: true, value: await s.evaluate(expr) }); }
      finally { s.close(); }
    } else if (cmd === "navigate") {
      const [wsUrl, url] = args;
      if (!url) fail("navigate needs a url");
      const s = await connect(wsUrl);
      try {
        await s.call("Page.navigate", { url });
        out({ ok: true, url });
      } finally { s.close(); }
    } else if (cmd === "send") {
      const [wsUrl, ...textParts] = args;
      const text = textParts.join(" ");
      if (!text) fail("send needs text");
      const s = await connect(wsUrl);
      try {
        const focus = await s.evaluate(`(() => {
          const ed = document.querySelector('div[role="textbox"][contenteditable="true"]');
          if (!ed) return { ok: false, error: "composer not found" };
          ed.focus();
          return { ok: true, label: ed.getAttribute("aria-label") || "" };
        })()`);
        if (!focus || !focus.ok) fail(focus?.error || "composer not found");
        await s.call("Input.insertText", { text });
        // Enter: rawKeyDown + keyUp (Slate listens for keydown Enter to send).
        const keyParams = {
          type: "rawKeyDown", key: "Enter", code: "Enter",
          windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13,
        };
        await s.call("Input.dispatchKeyEvent", keyParams);
        await s.call("Input.dispatchKeyEvent", { ...keyParams, type: "keyUp" });
        out({ ok: true, sent: text, composer_label: focus.label || "" });
      } finally { s.close(); }
    } else if (cmd === "sendfile") {
      const [wsUrl, filePath, ...textParts] = args;
      const text = textParts.join(" ");
      if (!filePath) fail("sendfile needs a file path");
      const s = await connect(wsUrl);
      try {
        const doc = await s.call("DOM.getDocument", { depth: -1, pierce: true });
        const q = await s.call("DOM.querySelector", {
          nodeId: doc.root.nodeId, selector: "input[type=file]",
        });
        if (!q.nodeId) fail("file input not found in DOM");
        await s.call("DOM.setFileInputFiles", { nodeId: q.nodeId, files: [filePath] });
        // Give Discord a moment to render the upload UI, then send.
        await new Promise((r) => setTimeout(r, 800));
        if (text) {
          await s.evaluate(`(() => {
            const ed = document.querySelector('div[role="textbox"][contenteditable="true"]');
            if (ed) ed.focus();
            return !!ed;
          })()`);
          await s.call("Input.insertText", { text });
        }
        const keyParams = {
          type: "rawKeyDown", key: "Enter", code: "Enter",
          windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13,
        };
        await s.call("Input.dispatchKeyEvent", keyParams);
        await s.call("Input.dispatchKeyEvent", { ...keyParams, type: "keyUp" });
        out({ ok: true, file: filePath, caption: text || "" });
      } finally { s.close(); }
    } else {
      fail(`unknown command: ${cmd}`);
    }
  } catch (e) {
    fail(e.message || String(e));
  }
}

main();
