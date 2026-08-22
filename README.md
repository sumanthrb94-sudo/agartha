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

## Backend (leads + admin)

The backend is Supabase (project `modcon-progress`, Mumbai region), used
directly from the browser — no servers to run:

- **Lead capture** — every form (`data-lead` attribute: contact / visit /
  investment / membership) POSTs to the `agartha_leads` table via Supabase
  REST (`js/main.js`, config in `js/config.js`). The key in `config.js` is a
  *publishable* key, safe to commit: row-level security only lets it INSERT.
  It cannot read, change, or delete anything. A hidden honeypot field
  silently swallows bot submissions.
- **Admin panel** — `/admin` (admin.html): email/password login via Supabase
  Auth. Signed-in admins whose email is in the `agartha_admins` allowlist
  can view, filter, search, status-track (new → contacted → visit scheduled
  → closed / spam), annotate, delete, and CSV-export leads.
- **Adding an admin**: insert their email into `agartha_admins` (Supabase
  dashboard → Table Editor), then have them use "Create the admin account"
  on `/admin`. Sign-ups from emails not in the allowlist can log in but see
  no data.

Tables and policies live in Supabase migrations `agartha_leads_backend` and
`agartha_admin_delete_policy`.

## Odds and ends

- The map is a Google Maps embed pointed at Moosapet Village, Narsapur
  Mandal — swap the `src` for your exact plus-code/place link if desired.
- The Instagram button on the membership page points at instagram.com —
  update it with the real profile URL.
