// Measure a page's tonal rhythm: how many vertical pixels each background
// colour occupies, rolled up by family. "The page feels heavy" is a claim you
// can put a number on — this is what turned "too beige" into 39% cream / 27%
// sage / 0% white, and what confirmed the fix landed at 63% white family.
//
//   node scripts/check-tone.mjs index.html
//
// Needs playwright and a Chromium at CHROME_PATH (or the pinned path below).

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const ROOT = "/home/user/agartha";
const PAGE = process.argv[2] || "index.html";
const MIME = { ".html":"text/html", ".css":"text/css", ".js":"text/javascript",
  ".webp":"image/webp", ".png":"image/png", ".svg":"image/svg+xml", ".jpg":"image/jpeg" };

const srv = http.createServer((q, r) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split("?")[0]));
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { "Content-Type": MIME[path.extname(f)] || "application/octet-stream" });
  fs.createReadStream(f).pipe(r);
});
await new Promise(r => srv.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${srv.address().port}`;

const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
await p.goto(`${base}/${PAGE}`, { waitUntil: "networkidle" });
await p.evaluate(async () => {
  // slow enough that lazy images actually finish — stepping faster than this
  // leaves them undecoded and fakes collapsed sections
  for (let y = 0; y < document.body.scrollHeight; y += 250) {
    window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120));
  }
});
await p.waitForTimeout(2500);
await p.waitForFunction(() => [...document.images].every(i => i.complete), null, { timeout: 20000 })
  .catch(() => console.log("  (warning: some images never completed)"));
const notLoaded = await p.$$eval("img", els => els.filter(e => e.naturalWidth === 0).map(e => e.src.split("/").pop()));
if (notLoaded.length) console.log("  images with no pixels:", notLoaded.join(", "), "\n");

const bands = await p.evaluate(() => {
  const NAMES = {
    "253, 252, 246": "off-white  #FDFCF6",
    "255, 255, 255": "pure white #FFFFFF",
    "246, 245, 240": "paper      #F6F5F0",
    "191, 188, 163": "sage deep  #BFBCA3",
    "241, 239, 230": "cream      #F1EFE6",
    "206, 203, 180": "sage       #CECBB4",
    "196, 192, 165": "sage deep  #C4C0A5",
    "79, 74, 33":    "olive      #4F4A21",
    "64, 60, 27":    "deep olive #403C1B",
  };
  const out = [];
  // top-level flow children of body are the page's bands
  for (const el of document.body.children) {
    const r = el.getBoundingClientRect();
    const h = Math.round(r.height);
    if (h < 5) continue;
    const cs = getComputedStyle(el);
    let bg = cs.backgroundColor;
    const m = bg.match(/\d+, \d+, \d+/);
    const hasImg = cs.backgroundImage !== "none";
    let label;
    if (el.classList.contains("hero")) label = "PHOTO (hero)";
    else if (m && m[0] in NAMES) label = NAMES[m[0]];
    else if (bg === "rgba(0, 0, 0, 0)" || bg === "transparent") {
      const pm = getComputedStyle(document.body).backgroundColor.match(/\d+, \d+, \d+/);
      label = (pm && NAMES[pm[0]]) || `page (${bg})`;
    } else label = hasImg ? `gradient/${bg}` : bg;
    out.push({ tag: el.tagName.toLowerCase(), cls: el.className.split(" ")[0] || "-", h, label });
  }
  return out;
});

const total = bands.reduce((s, x) => s + x.h, 0);
console.log(`${PAGE} — ${total}px tall\n`);
for (const x of bands)
  console.log(`  ${String(x.h).padStart(5)}px  ${String(Math.round(x.h/total*100)).padStart(3)}%  ${x.cls.padEnd(14)} ${x.label}`);

const roll = {};
for (const x of bands) {
  const k = x.label.startsWith("PHOTO") ? "photograph"
    : /white|paper/.test(x.label) ? "white family"
    : /cream/.test(x.label) ? "cream"
    : /sage/.test(x.label) ? "sage"
    : /olive/.test(x.label) ? "olive (dark)"
    : "other";
  roll[k] = (roll[k] || 0) + x.h;
}
console.log("\n  ── rollup ──");
for (const [k, v] of Object.entries(roll).sort((a,b) => b[1]-a[1]))
  console.log(`  ${String(Math.round(v/total*100)).padStart(3)}%  ${k}`);

await b.close(); srv.close();
