# Agartha : Roots of Earth — Front End

Static front-end rebuild of [agartha.in](https://agartha.in) — a 25-acre bespoke
farmhouse community and eco resort near Hyderabad. This is the presentation
layer only; backend functionality (form handling, booking, etc.) is to be
wired up later.

## Pages

| File | Page |
| --- | --- |
| `index.html` | Home — hero, Why Agartha, master plan, resort amenities, earthen homes, location, contact |
| `investment.html` | Investment plots — opportunity, 3-year ROI projection, who it's for, consultation form |
| `membership.html` | Membership tiers — Standard / Premium / Founder perks and pricing |
| `holiday-homes.html` | Holiday homes — 1 & 2 BHK price breakdowns, rental program, permaculture principles |
| `gallery.html` | Gallery grid (placeholder frames) |
| `contact.html` | Contact info, message form, schedule-a-visit form, map |

Shared assets: `css/styles.css` (design system + all components) and
`js/main.js` (sticky header, mobile nav, scroll-reveal, demo form handling).

## Deploying to Vercel

The site is zero-build static hosting — `vercel.json` provides the config
(clean URLs, so `/contact` serves `contact.html`, plus security headers).
Deploy either way:

- **Dashboard**: [vercel.com/new](https://vercel.com/new) → import this
  GitHub repo → framework preset "Other", no build command, output directory
  left as the root → Deploy.
- **CLI**: `npx vercel` from the repo root (add `--prod` for production).

Internal links use `.html` paths so the site also works when served locally;
on Vercel, `cleanUrls` redirects them to the extensionless URLs.

## Running locally

No build step — it's plain HTML/CSS/JS. Open `index.html` directly, or serve
the folder:

```bash
python3 -m http.server 8080
# then visit http://localhost:8080
```

## Images

All photography and icons load directly from the original Wix CDN
(`static.wixstatic.com`), using the URLs recorded in
`assets/asset_manifest.csv` — hero backgrounds, the master plan, amenity
icons, the gallery grid, holiday-home cards, and the footer panorama are all
the real site assets. To self-host them instead of hotlinking, run
`bash scripts/download-assets.sh` on a machine with normal internet access
and swap the URLs (details in `assets/README.md`).

## Wiring up functionality later

- All forms are marked with `data-demo` and currently just show a thank-you
  note client-side (`js/main.js`). Point them at your backend or a form
  service by removing `data-demo` and adding `action`/`method`, or replace the
  submit handler with a `fetch()` call.
- The map is a Google Maps embed pointed at Moosapet Village, Narsapur
  Mandal — swap the `src` for your exact plus-code/place link if desired.
- The Instagram button on the membership page points at instagram.com —
  update it with the real profile URL.
