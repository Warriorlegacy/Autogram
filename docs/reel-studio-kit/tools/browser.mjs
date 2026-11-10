// Shared: pick a browser for Remotion. Set BROWSER_EXECUTABLE to force one.
// If Remotion's own headless Chrome cannot start, fall back to installed Google Chrome / Chromium.
import fs from "node:fs";

export const MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
export const WIN_CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
export const LINUX_CHROME_CANDIDATES = [
  "/usr/bin/google-chrome",
  "/usr/bin/chromium-browser",
  "/usr/bin/chromium",
  "/snap/bin/chromium",
  "/opt/google/chrome/chrome"
];

export const browserFlag = () => {
  const forced = process.env.BROWSER_EXECUTABLE;
  if (forced) return forced;
  return null;
};

export const fallbackBrowser = () => {
  if (fs.existsSync(WIN_CHROME)) return WIN_CHROME;
  if (fs.existsSync(MAC_CHROME)) return MAC_CHROME;
  for (const c of LINUX_CHROME_CANDIDATES) {
    if (fs.existsSync(c)) return c;
  }
  return null;
};

