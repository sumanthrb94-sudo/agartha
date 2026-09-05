/**
 * Lead-capture audit: which contact routes actually reach the admin, and how
 * many taps each one costs.
 *
 * The site offers several ways to make contact, and they are not equal. A form
 * writes a row to agartha_leads, which is what /admin reads. A tel: link or a
 * WhatsApp link hands the visitor to another app and, unless something records
 * the intent first, leaves nothing behind — the enquiry arrives on somebody's
 * phone with no idea which page sent it.
 *
 * This walks every public page at desktop and phone width, finds every contact
 * route, exercises it, and reports whether a lead row was written and how many
 * interactions it took. Every Supabase write is intercepted, so running this
 * never touches the real table.
 *
 *     node scripts/check-leads.mjs
 *
 * Needs: npm install playwright
 */
import { chromium } from 'playwright';

const BASE = 'http://localhost:8099';
const PAGES = ['index', 'investment', 'membership', 'holiday-homes', 'resort', 'gallery', 'contact'];
const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900, mobile: false },
  { name: 'phone', width: 390, height: 844, mobile: true },
];

const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',
  args: ['--disable-background-networking'],
});

// Every route the site offers for making contact, and what it costs.
const rows = [];

async function newPage(vp) {
  const page = await browser.newPage({
    viewport: { width: vp.width, height: vp.height },
    isMobile: vp.mobile, hasTouch: vp.mobile,
    deviceScaleFactor: vp.mobile ? 3 : 1,
  });
  const captured = { leads: [], events: [] };
  await page.route('**/*', route => {
    const url = route.request().url();
    if (url.startsWith(BASE + '/')) return route.continue();
    if (url.includes('/rest/v1/agartha_leads')) {
      try { captured.leads.push(JSON.parse(route.request().postData() || '{}')); } catch { captured.leads.push({}); }
      return route.fulfill({ status: 201, body: '' });
    }
    if (url.includes('/rest/v1/agartha_events')) {
      try { captured.events.push(JSON.parse(route.request().postData() || '{}')); } catch { captured.events.push({}); }
      return route.fulfill({ status: 201, body: '' });
    }
    return route.abort();
  });
  // tel: and whatsapp leave the page. Keep the tab so the handler's own
  // fetch can be observed, exactly as keepalive would deliver it in the wild.
  await page.addInitScript(() => {
    document.addEventListener('click', e => {
      const a = e.target.closest && e.target.closest('a[href^="tel:"], a[href*="wa.me"]');
      if (a) e.preventDefault();
    }, false);
  });
  return { page, captured };
}

for (const vp of VIEWPORTS) {
  for (const name of PAGES) {
    const { page, captured } = await newPage(vp);
    await page.goto(`${BASE}/${name}.html`, { waitUntil: 'load' });
    await page.waitForTimeout(400);

    // Only routes a visitor can actually reach without opening a menu count as
    // one tap; anything inside the closed overlay nav costs the toggle first.
    const routes = await page.evaluate(() => {
      const seen = [];
      // offsetParent is null for position:fixed by spec, which would write off
      // the WhatsApp float and the sticky call bar — the two fastest routes on
      // the site. checkVisibility answers the question actually being asked.
      const visible = el => {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) return false;
        if (el.checkVisibility && !el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) return false;
        // The overlay nav is laid out but parked off-screen at translateX(100%).
        return r.right > 0 && r.left < window.innerWidth;
      };
      document.querySelectorAll('a[href^="tel:"], a[href*="wa.me"]').forEach(a => {
        seen.push({
          kind: a.href.startsWith('tel:') ? 'call' : 'whatsapp',
          where: a.className || a.closest('[class]')?.className.split(' ')[0] || 'inline',
          reachable: visible(a),
        });
      });
      document.querySelectorAll('form[data-lead]').forEach(f => {
        seen.push({
          kind: 'form:' + f.getAttribute('data-lead'),
          where: 'form',
          reachable: true,
          fields: f.querySelectorAll('[required]').length,
        });
      });
      return seen;
    });

    // Exercise one reachable tel: and one WhatsApp link, and every form.
    const tryClick = async (sel, label) => {
      const el = await page.$(sel);
      if (!el) return null;
      const before = captured.leads.length;
      await el.evaluate(n => n.scrollIntoView({ block: 'center' }));
      await el.click({ force: true }).catch(() => {});
      await page.waitForTimeout(500);
      return { label, lead: captured.leads.length > before };
    };

    const results = [];
    const wa = await tryClick('a.wa-float', 'WhatsApp float (1 tap)');
    if (wa) results.push(wa);

    // Only a link the visitor can actually see counts. .mobile-cta is
    // display:none on desktop and the overlay nav is parked off-screen, and
    // clicking either proves nothing about the site — it just tests a hidden
    // node. Mark the first genuinely visible phone link and click that one.
    const tagged = await page.evaluate(() => {
      const links = [...document.querySelectorAll('a[href^="tel:"]')];
      const hit = links.find(a => {
        const r = a.getBoundingClientRect();
        if (!r.width || !r.height) return false;
        if (a.checkVisibility && !a.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) return false;
        return r.right > 0 && r.left < window.innerWidth;
      });
      if (hit) hit.setAttribute('data-audit-target', '1');
      return !!hit;
    });
    if (tagged) {
      const tel = await tryClick('a[data-audit-target]', 'Phone link (1 tap)');
      if (tel) results.push(tel);
    }

    // The booking overlay is the primary route now — every "Book a Visit"
    // button on every page opens it instead of navigating. It is built on
    // first open, so it has to be opened before it can be tested.
    // Pick a visible trigger: .mobile-cta carries one too and is display:none
    // on desktop, and clicking a hidden node tests nothing.
    const trigger = await page.evaluate(() => {
      const hit = [...document.querySelectorAll('a[data-visit]')].find(a => {
        const r = a.getBoundingClientRect();
        if (!r.width || !r.height) return false;
        if (a.checkVisibility && !a.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) return false;
        return r.right > 0 && r.left < window.innerWidth;
      });
      if (hit) hit.setAttribute('data-audit-visit', '1');
      return !!hit;
    });
    if (trigger) {
      const before = captured.leads.length;
      await page.click('a[data-audit-visit]');
      await page.waitForTimeout(500);
      const opened = await page.evaluate(() =>
        !!document.querySelector('#visitModal.open'));
      if (opened) {
        await page.fill('#m-first-name', 'Test');
        await page.fill('#m-phone', '9999999999');
        await page.fill('#m-date', '2026-12-01');
        await page.click('#visitModal button[type="submit"]');
        await page.waitForTimeout(700);
      }
      results.push({ label: 'Booking overlay (1 tap + 3 fields)',
                     lead: opened && captured.leads.length > before });
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    }

    for (const f of await page.$$('form[data-lead]:not(#visitModal form)')) {
      const type = await f.getAttribute('data-lead');
      const before = captured.leads.length;
      await f.evaluate(form => {
        form.querySelectorAll('[required]').forEach(el => {
          if (el.type === 'email') el.value = 'test@example.com';
          else if (el.type === 'tel') el.value = '9999999999';
          else if (el.type === 'date') el.value = '2026-12-01';
          else el.value = 'Test';
        });
      });
      await f.evaluate(form => form.querySelector('button[type="submit"]').click());
      await page.waitForTimeout(700);
      const n = await f.evaluate(form => form.querySelectorAll('[required]').length);
      results.push({ label: `Form "${type}" (${n} fields + submit)`, lead: captured.leads.length > before });
    }

    rows.push({ vp: vp.name, page: name, routes, results });
    await page.close();
  }
}
await browser.close();

// ---- report ----
let capturedCount = 0, silentCount = 0;
for (const vp of VIEWPORTS) {
  console.log(`\n=== ${vp.name} ===`);
  for (const r of rows.filter(r => r.vp === vp.name)) {
    const calls = r.routes.filter(x => x.kind === 'call');
    const was = r.routes.filter(x => x.kind === 'whatsapp');
    const forms = r.routes.filter(x => x.kind.startsWith('form'));
    console.log(`\n${r.page}.html — ${calls.length} phone link${calls.length === 1 ? '' : 's'} ` +
      `(${calls.filter(c => c.reachable).length} reachable without opening the menu), ` +
      `${was.length} WhatsApp, ${forms.length} form${forms.length === 1 ? '' : 's'}`);
    for (const x of r.results) {
      const mark = x.lead ? 'captured in admin' : 'NOT captured — nothing reaches the lead table';
      console.log(`   ${x.lead ? '✓' : '✗'} ${x.label.padEnd(34)} ${mark}`);
      x.lead ? capturedCount++ : silentCount++;
    }
  }
}
console.log(`\n${capturedCount} route(s) captured, ${silentCount} silent.`);
process.exit(silentCount ? 1 : 0);
