// Shared Playwright loading and Chromium launch for the realistic tests.
// No browser binary is bundled here. playwright-core is loaded from the
// normal node resolution first, then from PLAYWRIGHT_CORE_PATH, then from
// the scratch install used during development. The Chromium binary is the
// Playwright cache build, or CHROMIUM_PATH when set.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

export async function loadPlaywright() {
  try {
    return await import('playwright-core');
  } catch {
    // Fall through to the explicit paths below.
  }
  const candidates = [];
  if (process.env.PLAYWRIGHT_CORE_PATH) {
    candidates.push(process.env.PLAYWRIGHT_CORE_PATH);
  }
  candidates.push('/tmp/realistic-b2-scratch/node_modules/playwright-core');
  const req = createRequire(import.meta.url);
  for (const candidate of candidates) {
    try {
      return req(candidate);
    } catch {
      // Try the next candidate.
    }
  }
  throw new Error(
    'playwright-core not found. Install it once with: npm install playwright-core ' +
    '(in a scratch folder) and set PLAYWRIGHT_CORE_PATH to that package dir.'
  );
}

export function chromiumPath() {
  if (process.env.CHROMIUM_PATH && fs.existsSync(process.env.CHROMIUM_PATH)) {
    return process.env.CHROMIUM_PATH;
  }
  const home = process.env.HOME || '';
  const cached = path.join(
    home,
    '.cache/ms-playwright/chromium-1254/chrome-linux64/chrome'
  );
  if (fs.existsSync(cached)) {
    return cached;
  }
  return undefined;
}

export async function launchBrowser() {
  const { chromium } = await loadPlaywright();
  const executablePath = chromiumPath();
  return chromium.launch({ executablePath, args: ['--no-sandbox'] });
}

export function nowIso() {
  return new Date().toISOString();
}
