"use strict";

// Background script for the computer-use bridge extension (Manifest V2).
// Holds one persistent native messaging port to the host named
// "computer_use_bridge" and routes JSON commands from the agent to tabs.
// Manifest V2 is used on purpose: the background page is persistent, so
// the native port stays open. Firefox MV3 uses a non-persistent event
// page, which would drop the port whenever the page is unloaded, and
// Firefox has no MV2 deprecation timeline. See README.md in this folder.
//
// Message flow (one listener, two kinds of traffic):
// - A message whose id is in the pending map is a reply to a request
//   this script sent to the host (for example host.ping). Resolve it.
// - Any other message with an id is a command from the agent, relayed
//   by the host. Run it and post the reply back on the same port.

const HOST_NAME = "computer_use_bridge";
const RECONNECT_DELAYS_MS = [1000, 2000, 5000, 10000, 30000];
const REQUEST_TIMEOUT_MS = 20000;
const TAB_TIMEOUT_MS = 25000;

let nativePort = null;
let reconnectAttempt = 0;
let reconnectTimer = null;
let nativeDeaths = 0;
const pending = new Map();

function log(...args) {
  console.log("[cu-bridge]", new Date().toISOString(), ...args);
}

function connectNative() {
  if (nativePort) {
    return;
  }
  try {
    nativePort = browser.runtime.connectNative(HOST_NAME);
  } catch (error) {
    log("connectNative failed:", error);
    scheduleReconnect();
    return;
  }
  reconnectAttempt = 0;
  nativePort.onMessage.addListener(onNativeMessage);
  nativePort.onDisconnect.addListener(onNativeDisconnect);
  log("connected to native host", HOST_NAME);
  // Smoke check: the host answers host.ping itself, no tab needed.
  // Negative id, so it can never collide with agent request ids.
  sendToHost({ id: -1, op: "host.ping" }).catch((error) => {
    log("host.ping failed:", error);
  });
}

function onNativeDisconnect() {
  const error = browser.runtime.lastError;
  nativeDeaths += 1;
  log(
    "native port disconnected, death count:",
    nativeDeaths,
    error ? error.message : "no error"
  );
  nativePort = null;
  for (const [id, entry] of pending) {
    entry.reject(new Error("native port disconnected"));
    pending.delete(id);
  }
  scheduleReconnect();
}

function scheduleReconnect() {
  if (reconnectTimer) {
    return;
  }
  const delay = RECONNECT_DELAYS_MS[
    Math.min(reconnectAttempt, RECONNECT_DELAYS_MS.length - 1)
  ];
  reconnectAttempt += 1;
  log("reconnecting to native host in", delay, "ms");
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connectNative();
  }, delay);
}

function onNativeMessage(message) {
  if (!message || typeof message !== "object") {
    log("ignoring non-object native message");
    return;
  }
  const entry = pending.get(message.id);
  if (entry) {
    pending.delete(message.id);
    clearTimeout(entry.timer);
    entry.resolve(message);
    return;
  }
  if (message.id === undefined) {
    log("ignoring native message without id:", message);
    return;
  }
  // A command from the agent, relayed by the host.
  handleCommand(message)
    .then((reply) => {
      if (nativePort) {
        nativePort.postMessage(reply);
      }
    })
    .catch((error) => {
      log("handleCommand failed:", error);
      if (nativePort) {
        nativePort.postMessage({
          id: message.id,
          ok: false,
          error: String(error && error.message ? error.message : error),
        });
      }
    });
}

function sendToHost(message) {
  if (!nativePort) {
    return Promise.reject(new Error("not connected to native host"));
  }
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      pending.delete(message.id);
      reject(new Error("native host timed out"));
    }, REQUEST_TIMEOUT_MS);
    pending.set(message.id, { resolve, reject, timer });
    try {
      nativePort.postMessage(message);
    } catch (error) {
      clearTimeout(timer);
      pending.delete(message.id);
      reject(error);
    }
  });
}

async function ensureContentScript(tabId) {
  try {
    await browser.tabs.executeScript(tabId, { file: "content.js" });
  } catch (error) {
    // The content script may already be present, or the tab may not
    // accept injection (for example, an internal about: page). The
    // sendMessage below reports the real failure in that case.
    log("executeScript note for tab", tabId, ":", error.message);
  }
}

async function runInTab(tabId, message) {
  await ensureContentScript(tabId);
  // A content script that never replies must not hang the agent: the
  // host gives up after its own timeout, but this shorter timeout lets
  // the extension report the failure with the tab id attached.
  return Promise.race([
    browser.tabs.sendMessage(tabId, message),
    new Promise((_resolve, reject) =>
      setTimeout(
        () =>
          reject(
            new Error(
              "tab reply timed out after " + TAB_TIMEOUT_MS + " ms, op: " + message.op
            )
          ),
        TAB_TIMEOUT_MS
      )
    ),
  ]);
}

async function handleCommand(message) {
  const started = Date.now();
  const finish = (result) => ({
    id: message.id,
    ok: true,
    result,
    elapsed_ms: Date.now() - started,
  });
  try {
    switch (message.op) {
      case "ping": {
        return finish({ pong: true, native_deaths: nativeDeaths });
      }
      case "listTabs": {
        const tabs = await browser.tabs.query({});
        return finish(
          tabs.map((tab) => ({
            id: tab.id,
            index: tab.index,
            url: tab.url,
            title: tab.title,
            active: tab.active,
          }))
        );
      }
      case "activate": {
        await browser.tabs.update(message.tabId, { active: true });
        return finish({ activated: message.tabId });
      }
      case "navigate": {
        await browser.tabs.update(message.tabId, { url: message.url });
        return finish({ navigated: message.url });
      }
      case "snapshot":
      case "click":
      case "type":
      case "evaluate":
      case "scroll":
      case "hover":
      case "select":
      case "upload":
      case "waitFor": {
        const result = await runInTab(message.tabId, message);
        return finish(result);
      }
      default: {
        return {
          id: message.id,
          ok: false,
          error: "unknown op: " + String(message.op),
          elapsed_ms: Date.now() - started,
        };
      }
    }
  } catch (error) {
    return {
      id: message.id,
      ok: false,
      error: String(error && error.message ? error.message : error),
      elapsed_ms: Date.now() - started,
    };
  }
}

connectNative();
