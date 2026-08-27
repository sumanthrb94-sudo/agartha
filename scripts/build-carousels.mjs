// Render Instagram carousels from the Agartha photo library, brand-locked.
//
// Every slide is real HTML rendered by headless Chromium at 1080x1350, using the
// palette in BRAND.md, the vendored Poppins in brand-kit/fonts, and the logo
// artwork in assets/brand. Nothing here is drawn by hand, so re-running after a
// copy change regenerates the whole set identically.
//
// The full pipeline is two steps — render 2x masters, then reduce them to
// Instagram's native width. Pass --out, or the 2x renders land on top of the
// 1080px deliverables:
//
//   node scripts/build-carousels.mjs --out carousels/master
//   python3 scripts/downsample-carousels.py
//   bash scripts/pack-carousels.sh
//
//   node scripts/build-carousels.mjs [--out carousels] [--size 1080x1350]

import { chromium } from "playwright";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import url from "node:url";

const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
const arg = (f, d) => {
  const i = process.argv.indexOf(f);
  return i > -1 ? process.argv[i + 1] : d;
};
const OUT = path.resolve(ROOT, arg("--out", "carousels"));
const [W, H] = arg("--size", "1080x1350").split("x").map(Number);
const SCALE = Number(arg("--scale", "2"));      // render at 2x, downsample later
const GUIDES = process.argv.includes("--guides");

const CHROME =
  process.env.CHROME_PATH ||
  ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "/usr/bin/chromium"].find((p) => fs.existsSync(p));

const spec = JSON.parse(fs.readFileSync(path.join(ROOT, "scripts/carousels.json"), "utf8"));

// Slides are served over loopback HTTP rather than file://: a page created with
// setContent has an about:blank origin that blocks file:// subresources, and
// @font-face is CORS-restricted even file-to-file. One origin, no surprises.
const MIME = { ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".woff2": "font/woff2", ".html": "text/html; charset=utf-8" };
let CURRENT = "";
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split("?")[0]);
  if (u === "/__slide") { res.writeHead(200, { "Content-Type": MIME[".html"] }); return res.end(CURRENT); }
  const f = path.join(ROOT, u);
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end("nope"); }
  res.writeHead(200, { "Content-Type": MIME[path.extname(f)] || "application/octet-stream" });
  fs.createReadStream(f).pipe(res);
});
let ORIGIN = "";
const fileUrl = (p) => `${ORIGIN}/${p.split(path.sep).join("/")}`;

// Brand tokens — mirrored from BRAND.md §3/§4.
const OLIVE = "#4F4A21", OLIVE_DEEP = "#403C1B", SAGE = "#CECBB4", OFFWHITE = "#FDFCF6";
const SCRIM = "linear-gradient(180deg, rgba(30,28,12,0.58) 0%, rgba(38,36,16,0.16) 20%, rgba(38,36,16,0.30) 46%, rgba(38,36,16,0.80) 78%, rgba(30,28,12,0.94) 100%)";

const esc = (s = "") => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const nl = (s = "") => esc(s).replace(/\n/g, "<br>");

const cssFor = () => `
@font-face{font-family:Poppins;font-weight:300;src:url('${fileUrl("brand-kit/fonts/poppins-latin-300-normal.woff2")}') format('woff2')}
@font-face{font-family:Poppins;font-weight:400;src:url('${fileUrl("brand-kit/fonts/poppins-latin-400-normal.woff2")}') format('woff2')}
@font-face{font-family:Poppins;font-weight:500;src:url('${fileUrl("brand-kit/fonts/poppins-latin-500-normal.woff2")}') format('woff2')}
@font-face{font-family:Poppins;font-weight:600;src:url('${fileUrl("brand-kit/fonts/poppins-latin-600-normal.woff2")}') format('woff2')}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px}
body{font-family:Poppins,sans-serif;background:${OLIVE};overflow:hidden}
.slide{position:relative;width:${W}px;height:${H}px;overflow:hidden;display:flex;flex-direction:column;justify-content:flex-end}
.photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.scrim{position:absolute;inset:0;background:${SCRIM}}
.field{position:absolute;inset:0;background:${OLIVE}}
.field.deep{background:${OLIVE_DEEP}}
.mark{position:absolute;top:172px;left:80px;height:34px;width:auto;opacity:.95}
.body-wrap{position:relative;padding:0 80px 152px}
.eyebrow{font-size:21px;font-weight:500;letter-spacing:.28em;text-transform:uppercase;color:${SAGE};margin-bottom:26px}
.kicker{font-size:20px;font-weight:500;letter-spacing:.28em;color:${SAGE};opacity:.75;margin-bottom:22px}
h1{font-size:82px;font-weight:500;line-height:1.08;letter-spacing:-.015em;color:${OFFWHITE};text-shadow:0 2px 24px rgba(20,19,8,.35)}
h1.sm{font-size:64px}
p{margin-top:26px;font-size:31px;font-weight:300;line-height:1.5;color:rgba(253,252,246,.86);max-width:760px}
/* statement slides: type on a flat field, no photo */
.centered{justify-content:center;text-align:left}
.centered h1{font-size:74px;color:${SAGE}}
.centered p{color:rgba(206,203,180,.8)}
.rule{width:96px;height:3px;background:${SAGE};opacity:.6;margin-bottom:40px}
/* cta */
.cta{justify-content:center;align-items:center;text-align:center}
.cta .lockup{position:relative;height:210px;width:auto;margin-bottom:56px}
/* position:relative — the scrim is absolutely positioned, so it paints above
   any static sibling. Without this the CTA copy vanishes behind it. */
.cta h1,.cta .pill,.cta .handle{position:relative}
.cta h1{font-size:66px}
.cta .pill{margin-top:48px;display:inline-block;background:${SAGE};color:${OLIVE_DEEP};font-size:30px;font-weight:500;letter-spacing:.1em;padding:24px 52px;border-radius:999px}
.cta .handle{margin-top:34px;font-size:26px;font-weight:400;letter-spacing:.16em;color:rgba(206,203,180,.85)}
/* --guides only: Instagram crop boxes, so placement can be eyeballed */
.guide{position:absolute;pointer-events:none}
.guide.square{left:0;right:0;top:${(H-W)/2}px;height:${W}px;border:3px dashed rgba(255,120,120,.9)}
.guide.sides{top:0;bottom:0;left:${Math.round((W-H*0.75)/2)}px;right:${Math.round((W-H*0.75)/2)}px;border-left:3px dashed rgba(120,180,255,.9);border-right:3px dashed rgba(120,180,255,.9)}
.guide.safe{inset:80px;border:2px dotted rgba(255,255,255,.5)}
.guide-key{position:absolute;bottom:${(H-W)/2 + 14}px;left:16px;font-size:19px;font-weight:500;color:#fff;background:rgba(0,0,0,.6);padding:6px 12px;border-radius:6px}
.pager{position:absolute;bottom:52px;right:80px;font-size:20px;font-weight:400;letter-spacing:.22em;color:rgba(253,252,246,.6)}
.swipe{position:absolute;bottom:52px;left:80px;font-size:20px;font-weight:500;letter-spacing:.24em;text-transform:uppercase;color:rgba(253,252,246,.75)}
`;

const photo = (name) => `<img class="photo" src="${fileUrl(`assets/site/${name}.webp`)}">`;
const markSage = fileUrl("assets/brand/wordmark-sage.png");
const lockup = fileUrl("assets/brand/lockup-vert-sage.png");

function slideHTML(s, i, total) {
  const pager = `<div class="pager">${String(i + 1).padStart(2, "0")} / ${String(total).padStart(2, "0")}</div>`;
  const mark = `<img class="mark" src="${markSage}">`;

  if (s.type === "cover") {
    return `<div class="slide">${photo(s.photo)}<div class="scrim"></div>${mark}
      <div class="body-wrap">
        ${s.eyebrow ? `<div class="eyebrow">${esc(s.eyebrow)}</div>` : ""}
        <h1>${nl(s.headline)}</h1>
      </div>
      <div class="swipe">Swipe →</div>${pager}</div>`;
  }
  if (s.type === "statement") {
    return `<div class="slide centered"><div class="field deep"></div>${mark}
      <div class="body-wrap" style="padding-bottom:0">
        <div class="rule"></div>
        <h1>${nl(s.headline)}</h1>
        ${s.body ? `<p>${nl(s.body)}</p>` : ""}
      </div>${pager}</div>`;
  }
  if (s.type === "cta") {
    return `<div class="slide cta">${s.photo ? photo(s.photo) : `<div class="field"></div>`}<div class="scrim" style="background:linear-gradient(180deg,rgba(38,36,16,.72),rgba(30,28,12,.9))"></div>
      <img class="lockup" src="${lockup}">
      <h1>${nl(s.headline)}</h1>
      <div class="pill">+91 95348 69999</div>
      <div class="handle">@agartha_by_modcon</div>${pager}</div>`;
  }
  // beat
  return `<div class="slide">${photo(s.photo)}<div class="scrim"></div>${mark}
    <div class="body-wrap">
      ${s.kicker ? `<div class="kicker">${esc(s.kicker)}</div>` : ""}
      <h1 class="sm">${nl(s.headline)}</h1>
      ${s.body ? `<p>${nl(s.body)}</p>` : ""}
    </div>${pager}</div>`;
}

(async () => {
  if (!CHROME) throw new Error("No Chromium found — set CHROME_PATH");
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  ORIGIN = `http://127.0.0.1:${server.address().port}`;
  const css = cssFor();
  // Clear stale slides only. Wiping OUT wholesale also takes the sidecars that
  // live beside them — caption.txt, POST.md, README.md — and the master/ tree
  // when OUT is carousels/ itself. Renumbering a carousel shorter still needs
  // the old tail gone, so delete the JPEGs and leave everything else alone.
  for (const c of spec.carousels) {
    const dir = path.join(OUT, c.slug);
    if (!fs.existsSync(dir)) continue;
    for (const f of fs.readdirSync(dir)) {
      if (/^\d+\.jpg$/.test(f)) fs.rmSync(path.join(dir, f));
    }
  }
  const browser = await chromium.launch({ executablePath: CHROME });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: SCALE });
  let n = 0;

  for (const c of spec.carousels) {
    const dir = path.join(OUT, c.slug);
    fs.mkdirSync(dir, { recursive: true });
    for (let i = 0; i < c.slides.length; i++) {
      const overlay = GUIDES
        ? `<div class="guide square"></div><div class="guide sides"></div><div class="guide safe"></div>` +
          `<div class="guide-key">— — 1:1 grid crop · | | 3:4 grid · ⋯ text-safe</div>`
        : "";
      const html = `<!doctype html><meta charset="utf-8"><style>${css}</style>${slideHTML(c.slides[i], i, c.slides.length).replace("</div>", overlay + "</div>")}`;
      CURRENT = html;
      await page.goto(`${ORIGIN}/__slide`, { waitUntil: "load" });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(120);
      const problems = await page.evaluate(() => {
        const out = [];
        for (const im of document.images)
          if (!im.complete || im.naturalWidth === 0) out.push("unloaded image: " + im.src);
        // Every piece of copy must actually be the topmost thing at its own
        // centre. The scrim is absolutely positioned and will paint over any
        // static sibling, which silently swallowed the whole CTA once.
        for (const el of document.querySelectorAll("h1, p, .eyebrow, .kicker, .pill, .handle, .swipe, .pager")) {
          const r = el.getBoundingClientRect();
          if (r.width === 0 || r.height === 0) { out.push("zero-size: " + el.className); continue; }
          const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
          if (hit !== el && !el.contains(hit)) {
            out.push(`covered: <${el.tagName.toLowerCase()} class="${el.className}"> hidden behind .${hit ? hit.className : "?"}`);
          }
        }
        return out;
      });
      if (problems.length) throw new Error(`slide ${c.slug}/${i + 1}:\n  ${problems.join("\n  ")}`);
      await page.screenshot({ path: path.join(dir, `${String(i + 1).padStart(2, "0")}.jpg`), type: "jpeg", quality: 92 });
      n++;
    }
    console.log(`${c.slug.padEnd(16)} ${c.slides.length} slides`);
  }
  await browser.close();
  server.close();
  console.log(`\n${n} slides written to ${path.relative(ROOT, OUT)}/ at ${W * SCALE}x${H * SCALE}` + (GUIDES ? " (with guides)" : ""));
})();
