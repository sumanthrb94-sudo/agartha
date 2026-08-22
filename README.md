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

## Running locally

No build step — it's plain HTML/CSS/JS. Open `index.html` directly, or serve
the folder:

```bash
python3 -m http.server 8080
# then visit http://localhost:8080
```

## Replacing image placeholders

Photography could not be pulled from the live site in this environment, so
image slots are rendered as styled placeholder frames. To use real photos:

1. Drop images into `assets/` (see `assets/README.md` for the expected names).
2. Replace the corresponding `<div class="img-frame">…</div>` block with
   `<img class="img-frame" src="assets/<name>.jpg" alt="…" />`, or set the
   image as a CSS background on the frame.

## Wiring up functionality later

- All forms are marked with `data-demo` and currently just show a thank-you
  note client-side (`js/main.js`). Point them at your backend or a form
  service by removing `data-demo` and adding `action`/`method`, or replace the
  submit handler with a `fetch()` call.
- The map is a Google Maps embed pointed at Moosapet Village, Narsapur
  Mandal — swap the `src` for your exact plus-code/place link if desired.
- The Instagram button on the membership page points at instagram.com —
  update it with the real profile URL.
