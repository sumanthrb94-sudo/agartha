# Agartha : Roots of Earth — Front End

Static front-end rebuild of [agartha.in](https://agartha.in) — a 25-acre bespoke
farmhouse community and eco resort near Hyderabad. This is the presentation
layer only; backend functionality (form handling, booking, etc.) is to be
wired up later.

## Pages

| File | Page |
| --- | --- |
| `index.html` | Home — hero, Why Agartha, earthen homes, location, contact |
| `investment.html` | Investment plots — opportunity, master plan, 3-year ROI projection, who it's for, consultation form |
| `membership.html` | Membership tiers — Standard / Premium / Founder perks and pricing |
| `holiday-homes.html` | Holiday homes — 1 & 2 BHK price breakdowns, rental program, permaculture principles |
| `resort.html` | The Resort — the shared two acres: amenities, and how they're built by hand |
| `gallery.html` | Gallery — 60 images in three groups (the resort, homes & gardens, the build on site) with a full-size lightbox |
| `contact.html` | Contact info, message form, visit invitation, location and map |

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

Every image is self-hosted — heroes, the master plan, the gallery, the cards,
the footer panorama. Nothing is hotlinked, so nothing breaks if the original
Wix site goes away. Each one ships at up to three widths and pages pick
between them with `srcset`.

`scripts/build-images.py` regenerates the whole set from the raw asset drop and
holds the source-to-name mapping; see `assets/README.md` for the layout, the
naming convention, and what was deliberately left out. The master plan is
client-supplied CMYK print artwork on a different quality ladder, so it has its
own one-off: `scripts/build-plan.py`.

## Icons

One inline vector sprite, `assets/icons.svg`, drawn from
[Lucide](https://lucide.dev) (ISC — `assets/icons.LICENSE`) and re-weighted to
stroke 1.6 to sit with Poppins Light. Pages reference symbols by id
(`<use href="assets/icons.svg#home">`).

`scripts/build-icons.py` holds the id-to-Lucide mapping and rebuilds the sprite;
edit the mapping there rather than the generated file. Adding an icon means
adding a line to `ICONS` and re-running it. The Instagram glyph stays
hand-drawn — Lucide dropped brand marks, so there is nothing to map it to.

## Backend (leads + admin)

The backend is Supabase (project `modcon-progress`, Mumbai region), used
directly from the browser — no servers to run:

- **Lead capture** — every form (`data-lead` attribute: contact / visit /
  investment / membership) POSTs to the `agartha_leads` table via Supabase
  REST (`js/main.js`, config in `js/config.js`). The key in `config.js` is a
  *publishable* key, safe to commit: row-level security only lets it INSERT.
  It cannot read, change, or delete anything. A hidden honeypot field
  silently swallows bot submissions.
- **Booking overlay** — every "Book a Visit" button on every page opens a
  panel with the visit form in it rather than navigating to `/contact` and
  making the visitor scroll past the message form to find it. The markup is
  injected by `js/main.js`, so it exists on all eight pages without being
  pasted into any of them, and each trigger keeps its `href` — without JS the
  links still go to the contact page. The form posts as `form_type` `visit`
  and carries the page it was opened from, so the admin can see which page
  sold the visit.
- **One-tap intent** — a tap on the WhatsApp button or on any `tel:` link also
  writes a row, as `form_type` `whatsapp` or `call`, with no name and the page
  it came from. Those are the fastest routes on the site and they exist on
  every page, but they hand the visitor to another app, so without this the
  enquiry arrived with no idea what prompted it. The POST uses
  `keepalive: true` — the click is navigating away, and an ordinary fetch
  would be cancelled. One row per intent per page view, so repeated taps do
  not flood the list. `scripts/check-leads.mjs` asserts every route still
  reaches the table.
- **Admin panel** — `/admin` (admin.html): email/password login via Supabase
  Auth. Signed-in admins whose email is in the `agartha_admins` allowlist
  can view, filter, search, status-track (new → contacted → visit scheduled
  → closed / spam), annotate, delete, and CSV-export leads.
- **Analytics Console** — `/analytics` (analytics.html), linked from the admin
  top bar. Same login and allowlist as the lead manager. Four tabs:
  *Overview* and *Visitors* (pageviews, unique visitors, sessions, time on
  page, bounce, top pages, referrers, devices, browsers), *Leads &
  Conversion* (visitor→lead funnel and rate, leads by form / page / status),
  and a live *SEO Audit* that fetches each page in the browser and scores ~14
  on-page ranking factors plus robots.txt / sitemap.xml. Charts are
  self-contained inline SVG — no third-party analytics, no external chart libs.
- **Visitor tracking** — `js/analytics.js` (loaded on every public page) logs
  cookieless, anonymous pageview + engagement events to the `agartha_events`
  table via the same insert-only publishable key. It honours Do-Not-Track /
  Global Privacy Control, skips bots and the admin pages, keeps only a random
  first-party id in `localStorage` (no cookies, no PII), and never blocks the
  page. Only allowlisted admins can read the data back, in the console.
- **Adding an admin**: insert their email into `agartha_admins` (Supabase
  dashboard → Table Editor), then have them use "Create the admin account"
  on `/admin`. Sign-ups from emails not in the allowlist can log in but see
  no data. The same account also unlocks `/analytics`.

Tables and policies live in Supabase migrations `agartha_leads_backend`,
`agartha_admin_delete_policy` and `agartha_analytics_events` (the
`agartha_events` table: anon insert-only, admin read).

## SEO

`sitemap.xml` and `robots.txt` sit at the repo root (Vercel serves them at the
domain root). Each public page carries a canonical URL, Open Graph + Twitter
card tags, and a `RealEstateAgent` JSON-LD block (a LocalBusiness subtype — address, phone and award, ready for `geo` once coordinates arrive). The Analytics Console's SEO
Audit tab re-checks all of this live and flags regressions — run it after any
content change. Update `sitemap.xml` when you add or remove a page.

## Going live

Ordered by dependency — the domain gates everything below it.

**1. Point agartha.in at Vercel.** Every absolute URL on the site currently says
`agartha-zeta.vercel.app`: 43 of them across canonicals, og:url, twitter:image,
the JSON-LD, sitemap.xml and robots.txt. Until that changes, the canonical tags
are telling Google the vercel.app address is the real one, so the two compete.
Add the domain in Vercel, then run a find-and-replace across those 43 and push.

**2. Google Search Console.** Verify the real domain, submit
`https://agartha.in/sitemap.xml`. Do it after step 1 — Search Console is
per-domain, and verifying vercel.app first means doing it twice and losing the
indexing history. Verification is a meta tag in each page's head.

**3. Google Business Profile.** For a 25-acre site people physically visit this
drives more enquiries than search ranking will. A Maps listing already exists
(the footer links to it); claiming it and adding photos, hours and the phone
number is the highest-return hour available.

**4. Conversion tracking, before any ad spend.** Without a conversion event an
ad platform optimises for clicks rather than enquiries, so the spend buys
traffic blind. The wiring is in place and waiting for a tag: `reportConversion`
in `js/main.js` fires once the lead row comes back written, and calls `gtag`,
`dataLayer.push` and `fbq` if any of them exist. None is loaded by the site, so
each call is a no-op until you install one — paste in the GA4 / Google Ads tag
or the Meta Pixel and conversions start flowing with no change to the JS.

Two things to know when you install one. The tag's host has to be added to
`script-src` and `connect-src` in the `vercel.json` CSP — it is Report-Only
today, so a missing entry shows up as a console report rather than a block, but
it will bite whenever the policy is enforced. And the event deliberately fires
on the written row, not on the submit: firing on submit counts failed posts and
every bot the honeypot swallowed, which is a number no bidding algorithm should
be handed.

**Still outstanding for want of information:**

- Real geo coordinates. The JSON-LD is `RealEstateAgent` with a full postal
  address but no `geo` block, because inventing a lat/long puts a map pin in the
  wrong field. The long Google Maps URL containing `@17.xxxx,78.xxxx` supplies it.
- A food-forest photograph. `BRAND.md` §6 flags it: nothing in the library shows
  edible planting, despite it being a headline proposition.
- The hero video files — see `assets/video/README.md`.

**Known limitation.** The lead forms carry a honeypot, which stops drive-by
bots. It does not stop anything posting straight at the Supabase REST endpoint,
since the publishable key is public by design. If spam appears, the fix is a
captcha (Turnstile or hCaptcha) or an edge function in front of the insert.

## Checks

Three scripts, no build step. Run them from the repo root; each exits non-zero
on a real problem.

```bash
python scripts/check-assets.py     # every image resolves, nothing hotlinked, nothing dead
python scripts/check-backend.py    # leads: Supabase reachable, schema matches, RLS insert-only
python scripts/check-analytics.py  # events: schema matches, tracker can write, reads still blocked
python scripts/verify-site.py      # loads every page in Chromium at 5 widths
node scripts/check-tone.mjs index.html   # tonal rhythm: % of the page per colour
node scripts/check-mobile.mjs            # 7 pages on 5 phone viewports
node scripts/check-spacing.mjs           # desktop vertical rhythm and dead space
node scripts/check-leads.mjs             # every contact route, and whether it reaches /admin
```

`check-leads.mjs` walks every public page at desktop and phone width, finds
every contact route — `tel:` links, WhatsApp links and lead forms — exercises
each one, and reports whether a row reaches `agartha_leads` and how many
interactions it cost. Every Supabase write is intercepted, so running it never
touches the real table. It exits non-zero if any route is silent. It needs
`npm install playwright`.

`check-spacing.mjs` looks for the two ways vertical rhythm goes wrong: runs of
flat single-colour pixels longer than two stacked section paddings, and
side-by-side columns whose heights differ by more than 260px — a short column
next to a tall one is dead space the pixel scan cannot tell apart from ordinary
padding. Pass a width to test a wider desk (`node scripts/check-spacing.mjs 1920`).
It needs `npm install playwright pngjs @fontsource/poppins`: the pages pull
Poppins from Google Fonts, and measuring heights against a fallback face
measures the wrong typography, so the font request is answered locally.

`verify-site.py` needs `pip install playwright && playwright install chromium`.
It reports console errors, failed requests, broken images and horizontal
overflow per page, then exercises the lightbox, the mobile nav and the lead
forms, and drops screenshots in `scripts/screenshots/` (git-ignored).

`scripts/build-gallery.py` regenerates the gallery page's markup from a
captioned list — edit that list rather than the 60 `<img>` tags.

## Odds and ends

- The map is a Google Maps embed pointed at Moosapet Village, Narsapur
  Mandal — swap the `src` for your exact plus-code/place link if desired.
