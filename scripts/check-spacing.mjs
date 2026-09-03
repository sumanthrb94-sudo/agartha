/**
 * Desktop spacing audit: where does the page go quiet for too long?
 *
 * Two passes, because vertical rhythm fails in two different ways and a
 * single measurement only ever catches one of them.
 *
 *   bands   — renders the page and scans it row by row for runs of flat,
 *             single-colour pixels. This is what a visitor actually
 *             perceives as "a big empty gap", regardless of which box
 *             model produced it.
 *   columns — measures what a height difference between the halves of a
 *             side-by-side layout actually costs. Unequal columns are not a
 *             fault in themselves. What hurts is a *centred* row: the shorter
 *             column is pushed down by half the difference, so its heading
 *             ends up floating in the middle of an empty field, and the pixel
 *             scan cannot tell that void apart from ordinary section padding.
 *             The same difference under `align-items: start` costs nothing —
 *             the headings line up and the slack trails off at the bottom,
 *             beside whatever made the other column tall. So what is reported
 *             is the displacement, and the raw gap is only ever a note.
 *
 *     node scripts/check-spacing.mjs            # 1440px
 *     node scripts/check-spacing.mjs 1920       # a wider desk
 *
 * Iframe regions are skipped: an embed that has not loaded is a flat
 * rectangle and would otherwise dominate every report.
 */
import { chromium } from 'playwright';
import { PNG } from 'pngjs';
import fs from 'node:fs';

// Poppins is the whole reason the type sits the way it does, and the page
// pulls it from Google Fonts. Anywhere that host is unreachable the browser
// silently falls back to a wider, taller face and every height measured
// below is measured against the wrong typography. So the request is
// answered locally from the npm copy of the same font, and the run aborts
// rather than quietly reporting fiction if that copy is missing.
const FONT_DIR = 'node_modules/@fontsource/poppins/files';
const WEIGHTS = [300, 400, 500, 600];
if (!WEIGHTS.every(w => fs.existsSync(`${FONT_DIR}/poppins-latin-${w}-normal.woff2`))) {
  console.error('Poppins is missing. npm install @fontsource/poppins --no-save');
  process.exit(2);
}
const FONT_CSS = WEIGHTS.map(w => `@font-face{font-family:Poppins;font-style:normal;` +
  `font-weight:${w};font-display:swap;src:url(/__font/${w}.woff2) format("woff2");}`).join('');

const WIDTH = Number(process.argv[2]) || 1440;
const HEIGHT = 1000;
const BASE = 'http://localhost:8099';
const PAGES = ['index', 'investment', 'membership', 'holiday-homes', 'gallery', 'contact'];

// A gap only reads as a mistake once it clears the largest deliberate one.
// Section padding tops out near 152px, so two stacked paddings — the honest
// maximum between two sections — is a shade over 300.
const BAND_FLOOR = 320;
// How far a column may be pushed off the top of its row before its heading
// stops reading as the start of the section. Half of a stacked-padding gap.
const DISPLACEMENT_FLOOR = 130;
// A trailing gap this large is worth seeing even though it displaces nothing.
const TRAILING_NOTE = 240;

const flatRow = (png, y, x0, x1) => {
  let min = [255, 255, 255], max = [0, 0, 0];
  for (let x = x0; x < x1; x += 6) {
    const i = (png.width * y + x) << 2;
    for (let c = 0; c < 3; c++) {
      const v = png.data[i + c];
      if (v < min[c]) min[c] = v;
      if (v > max[c]) max[c] = v;
    }
  }
  return max[0] - min[0] <= 6 && max[1] - min[1] <= 6 && max[2] - min[2] <= 6;
};

const run = async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    args: ['--disable-background-networking', '--disable-component-update', '--no-first-run'],
  });
  let findings = 0;

  for (const name of PAGES) {
    // Half-scale: the scan is looking for runs hundreds of pixels long, and
    // a quarter of the pixels finds them just as well in a quarter of the time.
    const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT }, deviceScaleFactor: 0.5 });
    await page.route('**/*', route => {
      const url = route.request().url();
      if (url.startsWith(`${BASE}/`)) return route.continue();
      if (url.includes('fonts.googleapis.com')) {
        return route.fulfill({ contentType: 'text/css', body: FONT_CSS });
      }
      const font = url.match(/\/__font\/(\d+)\.woff2$/);
      if (font) {
        return route.fulfill({ contentType: 'font/woff2',
          body: fs.readFileSync(`${FONT_DIR}/poppins-latin-${font[1]}-normal.woff2`) });
      }
      // Everything else off-site (the CDN scripts, the map embed) is left to
      // fail fast instead of holding `load` open for its full timeout.
      return route.abort();
    });
    await page.goto(`${BASE}/${name}.html`, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    // Walk the whole page so every lazy image has been asked for, then give
    // the decoders a beat — an image mid-decode is a flat grey box, and this
    // scan is looking for exactly those. Waiting on decode() instead would
    // hang: an image that never entered the viewport never starts loading,
    // and its promise never settles.
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 500) {
        window.scrollTo(0, y);
        await new Promise(r => setTimeout(r, 60));
      }
      window.scrollTo(0, 0);
    });
    await page.waitForTimeout(2500);

    const meta = await page.evaluate(() => {
      const sections = [...document.querySelectorAll('body > main > section, body > section')]
        .map(s => {
          const r = s.getBoundingClientRect();
          const cs = getComputedStyle(s);
          return {
            id: s.id || s.className.split(' ')[0] || 'section',
            top: r.top + scrollY, bottom: r.bottom + scrollY,
            padTop: parseFloat(cs.paddingTop), padBottom: parseFloat(cs.paddingBottom),
          };
        });
      const skip = [...document.querySelectorAll('iframe')].map(f => {
        const r = f.getBoundingClientRect();
        return { top: r.top + scrollY - 8, bottom: r.bottom + scrollY + 8 };
      });
      const splits = [...document.querySelectorAll('.split')].map(s => {
        const hs = [...s.children].map(k => k.getBoundingClientRect().height);
        const sect = s.closest('section');
        const align = getComputedStyle(s).alignItems;
        const gap = Math.round(Math.max(...hs) - Math.min(...hs));
        // How far the short column is shifted off the top of the row.
        const share = { center: 0.5, end: 1, 'flex-end': 1 }[align] ?? 0;
        return {
          where: sect?.id || sect?.className.split(' ')[0] || 'section',
          heights: hs.map(Math.round), gap, align,
          displaced: Math.round(gap * share),
          top: Math.round(s.getBoundingClientRect().top + scrollY),
        };
      });
      return { sections, skip, splits, height: document.body.scrollHeight };
    });

    const buf = await page.screenshot({ fullPage: true });
    const png = PNG.sync.read(buf);
    const x0 = Math.round(png.width * 0.06), x1 = Math.round(png.width * 0.94);

    const bands = [];
    let start = null;
    for (let y = 0; y < png.height; y++) {
      if (flatRow(png, y, x0, x1)) { if (start === null) start = y; }
      else { if (start !== null) bands.push([start, y]); start = null; }
    }
    if (start !== null) bands.push([start, png.height]);

    // The screenshot is half-scale, so runs are measured back into CSS pixels
    // before the floor is applied — the floor is a design threshold, not a
    // property of whatever resolution the scan happened to run at.
    const scale = meta.height / png.height;
    const report = bands
      .map(([a, b]) => ({ top: Math.round(a * scale), bottom: Math.round(b * scale), h: Math.round((b - a) * scale) }))
      .filter(band => band.h >= BAND_FLOOR)
      .filter(band => !meta.skip.some(s => band.top < s.bottom && band.bottom > s.top))
      // The run below the last section is the footer's own business.
      .filter(band => band.top < meta.height - 200)
      .map(band => {
        const at = meta.sections.filter(s => band.top < s.bottom && band.bottom > s.top).map(s => s.id);
        const between = at.length > 1 ? `between ${at.join(' / ')}` : `inside ${at[0] || 'page'}`;
        return { ...band, between };
      });

    const pushed = meta.splits.filter(s => s.displaced >= DISPLACEMENT_FLOOR);
    const trailing = meta.splits.filter(s => s.displaced < DISPLACEMENT_FLOOR && s.gap >= TRAILING_NOTE);

    console.log(`\n${name}.html  (${meta.height}px tall @ ${WIDTH})`);
    if (!report.length && !pushed.length) console.log('  spacing reads even');
    for (const b of report) {
      console.log(`  BAND  ${b.h}px of flat colour at y=${b.top}–${b.bottom}  ${b.between}`);
      findings++;
    }
    for (const s of pushed) {
      console.log(`  SPLIT ${s.where} at y=${s.top}: short column pushed ${s.displaced}px down ` +
        `by align:${s.align} over a ${s.gap}px gap  [${s.heights.join(' vs ')}]`);
      findings++;
    }
    for (const s of trailing) {
      console.log(`  note  ${s.where} columns differ by ${s.gap}px [${s.heights.join(' vs ')}], ` +
        `but align:${s.align} keeps it at the bottom — trailing space, nothing displaced`);
    }
    await page.close();
  }

  await browser.close();
  console.log(`\n${findings} spacing finding${findings === 1 ? '' : 's'}`);
  return findings ? 1 : 0;
};

run().then(c => process.exit(c));
