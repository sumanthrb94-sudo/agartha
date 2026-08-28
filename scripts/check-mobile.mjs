// Mobile pass: load every public page on five phone/tablet viewports and report
// anything that would look wrong on a handset — horizontal overflow (naming the
// elements that cause it), images that never decoded, and tap targets too small
// to hit. Writes stitched frames for two representative devices.
//
//   node scripts/check-mobile.mjs [outdir]
//
// Needs playwright and a Chromium at CHROME_PATH (or the pinned path below).
//
// Scroll pacing matters: stepping faster than ~250px/110ms outruns the lazy
// images and reports collapsed sections that are perfectly fine in a browser.
import { chromium, devices } from "playwright";
import http from "http"; import fs from "fs"; import path from "path";

const ROOT = "/home/user/agartha";
const OUT = process.argv[2] || "/tmp/mobile";
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });

const MIME = { ".html":"text/html",".css":"text/css",".js":"text/javascript",
  ".webp":"image/webp",".png":"image/png",".svg":"image/svg+xml",".jpg":"image/jpeg",
  ".xml":"application/xml",".txt":"text/plain" };
const srv = http.createServer((q, r) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split("?")[0]));
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { "Content-Type": MIME[path.extname(f)] || "application/octet-stream" });
  fs.createReadStream(f).pipe(r);
});
await new Promise(r => srv.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${srv.address().port}`;

const PHONES = [
  { name: "iphone-se",  w: 375, h: 667, dpr: 2 },
  { name: "iphone-14",  w: 390, h: 844, dpr: 3 },
  { name: "pixel-7",    w: 412, h: 915, dpr: 2.6 },
  { name: "galaxy-fold",w: 320, h: 653, dpr: 2 },
  { name: "ipad-mini",  w: 768, h: 1024, dpr: 2 },
];
const PAGES = ["index.html","investment.html","membership.html",
               "holiday-homes.html","gallery.html","contact.html"];

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });

let problems = 0;
for (const d of PHONES) {
  const ctx = await browser.newContext({
    viewport: { width: d.w, height: d.h }, deviceScaleFactor: d.dpr,
    isMobile: true, hasTouch: true,
    userAgent: devices["iPhone 13"].userAgent,
  });
  for (const pg of PAGES) {
    const p = await ctx.newPage();
    await p.goto(`${base}/${pg}`, { waitUntil: "networkidle" });
    await p.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 250) {
        window.scrollTo(0, y); await new Promise(r => setTimeout(r, 110));
      }
      window.scrollTo(0, 0);
    });
    // Wait on the actual condition, not a guess. Scrolling back to the top
    // deprioritises the last lazy image, so a fixed sleep kept reporting the
    // footer panorama as broken when it loads fine.
    await p.waitForFunction(() => [...document.images].every(i => i.complete),
      null, { timeout: 15000 }).catch(() => {});
    await p.waitForTimeout(400);

    const issues = await p.evaluate(() => {
      const out = [];
      const de = document.documentElement;
      const over = de.scrollWidth - de.clientWidth;
      if (over > 1) {
        // name the widest offenders so the fix has an address
        const wide = [...document.querySelectorAll("body *")]
          .map(e => ({ e, r: e.getBoundingClientRect() }))
          .filter(x => x.r.right > de.clientWidth + 1 && x.r.width > 0)
          .sort((a, b) => b.r.right - a.r.right).slice(0, 3)
          .map(x => `<${x.e.tagName.toLowerCase()} class="${x.e.className}"> to ${Math.round(x.r.right)}px`);
        out.push(`overflow ${over}px — ${wide.join(" | ")}`);
      }
      for (const img of document.images)
        if (img.naturalWidth === 0 && img.getAttribute("src")) out.push(`image no pixels: ${img.src.split("/").pop()}`);
      // tap targets: links/buttons that are visible and too small to hit
      // Only judge what a user can actually reach. The mobile menu is parked
      // at translateX(100%) rather than display:none, so its links are laid
      // out but off-screen — measuring them there reported 17px for links that
      // are 50px once the menu opens.
      for (const el of document.querySelectorAll("a, button")) {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        if (getComputedStyle(el).display === "none" || el.offsetParent === null) continue;
        if (r.left >= de.clientWidth || r.right <= 0) continue;   // parked off-screen
        if (!el.textContent.trim()) continue;
        if (r.height < 44)
          out.push(`tap target ${Math.round(r.width)}x${Math.round(r.height)}: "${el.textContent.trim().slice(0,28)}"`);
      }
      return out;
    });

    if (issues.length) {
      problems += issues.length;
      console.log(`  ${d.name} / ${pg}`);
      for (const i of [...new Set(issues)].slice(0, 5)) console.log(`      ${i}`);
    }

    // stitched frames only for the two most representative phones
    if (d.name === "iphone-14" || d.name === "galaxy-fold") {
      const total = await p.evaluate(() => document.body.scrollHeight);
      const stem = `${d.name}-${pg.replace(".html","")}`;
      let y = 0, i = 0;
      while (y < total && i < 12) {
        await p.evaluate(v => window.scrollTo(0, v), y);
        await p.waitForTimeout(260);
        await p.screenshot({ path: `${OUT}/${stem}-${String(++i).padStart(2,"0")}.png` });
        y += d.h;
      }
    }
    await p.close();
  }
  console.log(`${d.name} (${d.w}x${d.h} @${d.dpr}x) done`);
  await ctx.close();
}
await browser.close(); srv.close();
console.log(problems ? `\n${problems} issue(s) found` : "\nno overflow, no dead images, no undersized tap targets");
