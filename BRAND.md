# Agartha — Brand & Content Kit

Single source of truth for anything carrying the Agartha name: social posts,
decks, ads, print. Values here are lifted from the live site
(`css/styles.css`, `assets/brand/`), so this file and the website cannot drift.

---

## 1. The master prompt

Paste this whole block as the system prompt / project brief wherever posts are
generated. Everything below section 1 is the reference it draws on.

> You are the brand designer and copywriter for **Agartha: Roots of Earth**, a
> 25-acre bespoke farmhouse community by Modcon at Narsapur, near Hyderabad.
> Two of the 25 acres are a resort with clubhouse amenities. Homes are built
> from earth, bamboo, lime and thatch. Every asset you produce must be
> indistinguishable in identity from agartha.in.
>
> **Colour — use only these.** Olive `#4F4A21` and sage `#CECBB4` are the
> designer's two official brand colours. White `#FFFFFF`, paper `#F6F5F0` and
> deep olive `#403C1B` are the approved supporting neutrals. Never introduce a
> colour outside this set — no pure black, no accent hue, no gradient that
> isn't the scrim in §3. Dark layouts are olive or deep olive with sage or
> paper text. **Light layouts lead with white**: it is the trust colour and
> should be the largest share of any light composition, with paper as the
> quieter field beneath it. Sage is an accent — icon chips, a rule, one band —
> never a whole field, which flattens everything sitting on it.
>
> **Type.** Poppins throughout — Light 300, Regular 400, Medium 500, SemiBold
> 600. Headlines Medium, generous size, tight line-height (1.1–1.2), letter
> spacing slightly negative. Eyebrows and buttons are uppercase Medium at
> 0.18–0.28em letter spacing. Body is Regular at 1.65 line-height. Never bold
> above 600, never a second typeface, never italics.
>
> **Logo.** Use the supplied files only; never retype the wordmark, never
> recolour, rotate, outline, add effects to, or place the mark on a busy part of
> a photo. Sage lockups on dark, olive lockups on light. Clear space on all
> sides equal to the height of the spiral mark.
>
> **Photography.** Use only the supplied library — real construction and real
> renders of this project. Never stock photography, never AI-generated imagery,
> never another development's work. Warm, natural daylight; earth, bamboo,
> thatch and greenery; unhurried and unpeopled or lightly peopled. Do not apply
> filters, heavy grading, vignettes or borders. If text sits on a photo, lay the
> scrim from §3 underneath it — never type straight onto a bright sky.
>
> **Voice.** Grounded, calm, unhurried, quietly premium. Short declaratives.
> Nature and craft lead; money follows. Say what the place *is*, not how
> exciting it is. Never use exclamation marks, hype words ("amazing",
> "unbelievable", "luxury living redefined"), emoji in headlines, urgency
> pressure ("hurry", "last chance"), or invented figures. Every number —
> price, area, yield, acreage — must come from the source material, never
> estimated.
>
> **Facts, verbatim.** 25 acres · 2-acre resort · Narsapur, adjacent to the
> upcoming Regional Ring Road, Hyderabad · Moosapet Village, Narsapur Mandalam,
> Hyderabad, Telangana 502313 · +91 95348 69999 · @agartha_by_modcon ·
> agartha.in
>
> Before returning any asset, check it against the Do / Don't list in §9. If a
> requested claim is not in the source material, say so instead of inventing it.

---

## 2. What Agartha is

A 25-acre bespoke farmhouse community by **Modcon**, at Narsapur near
Hyderabad, adjacent to the upcoming Regional Ring Road. Two acres are given to
a resort and clubhouse. Homes are built from natural materials — earth blocks,
bamboo, lime, thatch — with edible landscaped backyards.

Three commercial offers: **Investment**, **Membership**, **Holiday Homes**.

Tagline: **Roots of Earth.**

---

## 3. Colour

**Official — the designer's palette.** Only these two are the brand.

| Token | Hex | Use |
|---|---|---|
| Olive | `#4F4A21` | Primary. Headers, dark panels, body text on light |
| Sage | `#CECBB4` | Secondary. Text on olive, buttons, the logo on dark |

**Approved neutrals.** Derived for the website; safe to use, but they are
supporting tones, not brand colours.

| Token | Hex | Use |
|---|---|---|
| White | `#FFFFFF` | Surfaces — cards, panels, the wide light bands |
| Paper | `#F6F5F0` | Page field beneath the white surfaces |
| Deep olive | `#403C1B` | Footer, table headers, deepest panels |
| Moss | `#8A8768` | Muted rules, icon fills — large text only |
| Clay | `#8A8455` | Eyebrows, captions — large text only |

A white card on a white band needs an edge the shadow alone will not give it:
one olive hairline at 7%, `0 0 0 1px rgba(79, 74, 33, 0.07)`. Faint enough not
to read as a border.

**Photo scrim.** Any text over a photograph sits on this, never bare:

```css
linear-gradient(180deg, rgba(58,55,26,0.64) 0%, rgba(72,67,32,0.36) 45%, rgba(48,45,20,0.78) 100%)
```

**Measured contrast** (WCAG, computed — not estimated):

| Combination | Ratio | Verdict |
|---|---|---|
| White on deep olive | 11.17 | AAA — safest dark layout |
| Paper on deep olive | 10.23 | AAA |
| Olive on white | 9.00 | AAA |
| Olive on paper | 8.24 | AAA |
| Sage on deep olive | 6.82 | AA body |
| Olive on sage | 5.50 | AA body |
| Clay on white | 3.81 | **Large text only** |
| Moss on white | 3.65 | **Large text only** |

Moss and clay fail for body copy. Use them at 24px+ or for non-text elements.

---

## 4. Typography

**Poppins** — everything. `https://fonts.google.com/specimen/Poppins`
Weights: 300, 400, 500, 600. Never heavier, never a second family.

| Role | Weight | Treatment |
|---|---|---|
| Headline | 500 | line-height 1.1–1.2, letter-spacing −0.01em |
| Eyebrow | 500 | UPPERCASE, letter-spacing 0.28em |
| Body | 400 | line-height 1.65 |
| Button | 500 | UPPERCASE, letter-spacing 0.12em |

> The website also declares Julius Sans One as a brand font. It is **unused** —
> the wordmark is supplied as artwork. Do not set type in it.

---

## 5. Logo kit — `assets/brand/`

| File | What it is | Use on |
|---|---|---|
| `mark-sage.png` | Spiral mark alone | Dark |
| `mark-olive.png` | Spiral mark alone | Light |
| `wordmark-sage.png` | AGARTHA wordmark | Dark |
| `wordmark-olive.png` | AGARTHA wordmark | Light |
| `lockup-line-sage.png` | Horizontal, AGARTHA + ROOTS OF EARTH | Dark, wide |
| `lockup-vert-sage.png` | Stacked full lockup | Dark, square |
| `lockup-vert-olive.png` | Stacked full lockup | Light, square |
| `favicon.png` | Rounded-square app icon | Avatars, favicons |

Transparent PNGs — place directly on any approved background.

**Rules.** Clear space on every side ≥ the spiral mark's height. Minimum
wordmark width 120px on screen. Sage on dark, olive on light — never olive on
olive or sage on sage. Never: recolour, stretch, rotate, outline, add shadow or
glow, re-typeset the wordmark, box it, or lay it over a busy area of a photo.

---

## 5b. Icons — `assets/icons.svg`

[Lucide](https://lucide.dev), ISC licensed, re-weighted to **stroke 1.6** on a
24×24 box with round caps so it sits with Poppins Light rather than shouting
over it. One sprite, referenced by symbol id.

Use these and only these. Do not mix in a second icon family, do not use filled
or duotone glyphs, and do not draw a one-off — if a symbol is missing, add it to
the mapping in `scripts/build-icons.py` and rebuild, so the whole set stays one
family at one weight. Icons take `currentColor`: olive on light, sage on dark.

The Instagram mark is the exception — Lucide carries no brand marks, so that one
glyph is hand-drawn and must not be replaced with a lookalike.

---

## 6. Photography — `assets/site/` and `assets/web/`

Real photography and real renders of **this** project. Never substitute stock.

**`assets/site/` — 16 masters** (client-supplied):

Built work · `thatch-villa-day` `thatch-villa-shell` `thatch-villa-site`
`bamboo-tower` `bamboo-tower-close` `farm-shelter`
Craft in progress · `bamboo-dome-frame` `dome-thatching` `dome-workers`
`entrance-canopy`
Interiors · `interior-terracotta` `interior-mudwall`
Renders · `earthen-home` `villa-arrival` `courtyard-villas` `pergola-detail`
Plan · `master-plan` — the client's 37-plot layout drawing

**`assets/web/`** — the original site library: aerials, pools, clubhouse,
pathways.

Each master ships with `-480` and `-900` variants. **Use the master for print
and full-bleed; use `-900` for social.** A 1080×1080 post needs ~1080px — the
900 variant is close enough; the 480 is not.

**Art direction.** Warm natural daylight. Earth, bamboo, thatch, greenery.
Unhurried, generous negative space, horizon level. Craft-in-progress shots are
on-brand and distinctive — use them. No filters, no heavy grading, no vignettes,
no drop shadows, no borders.

**Known gap:** nothing in the library shows edible planting or a food forest,
despite it being a headline proposition. Commission that shoot.

---

## 7. Voice

Grounded, calm, unhurried, quietly premium. Nature and craft lead; money
follows.

**Proven lines** (live on the site — reuse freely):

- "Agartha is not just a farmhouse project — it's a way of life."
- "25-Acre Bespoke Farmhouse Community Near Hyderabad"
- "Own a Holiday. Earn a Future. Live in Peace."
- "Your holiday home isn't just a retreat — it's a living, breathing investment."
- "A Living Canvas of Nature & Design"
- "Step beyond the noise — discover your roots at Agartha."

**Vocabulary.** Earthen · bamboo · lime · thatch · food forest · farm to table ·
natural swimming pool · clubhouse · retreat · stillness · roots.

**Propositions.** Farmhouses built with natural materials · Edible landscaped
backyards · Premium resort & clubhouse · Strategic location.

**Amenities.** Earthen Retreats · Tulum-style Gym · Yoga & Wellness Centre ·
Natural Swimming Pool · Banquet Hall for Celebrations · Farm to Table Restaurant
· Sustainable Living Spaces.

Never: exclamation marks, emoji in headlines, hype adjectives, false urgency, or
any figure not in the source material.

---

## 8. Facts

| | |
|---|---|
| Full name | Agartha: Roots of Earth |
| By | Modcon |
| Site | 25 acres, 2-acre resort |
| Location | Narsapur, adjacent to the upcoming Regional Ring Road, Hyderabad |
| Address | Moosapet Village, Narsapur Mandalam, Hyderabad, Telangana 502313 |
| Phone / WhatsApp | +91 95348 69999 |
| Instagram | [@agartha_by_modcon](https://www.instagram.com/agartha_by_modcon) |
| Maps | https://share.google/gh30pBzVmntxDpqDk |
| Website | agartha.in |

---

## 9. Do / Don't

**Do** — white as the dominant light · olive and sage as the frame · Poppins
only · the supplied logo files · real project photography · the scrim under any
text on a photo · sentences that describe rather than sell · numbers traced to
source.

**Don't** — introduce a colour outside §3 · pure black · sage as a full-section
field · a second typeface · retype or recolour the logo · stock or AI-generated
imagery · filters, vignettes or borders on photos · text on a bright sky without
the scrim · exclamation marks or hype · invented prices, yields or areas.

---

## 10. Social formats

| Format | Size | Notes |
|---|---|---|
| Instagram square | 1080×1080 | Use a `-900` variant or larger |
| Portrait / Reel cover | 1080×1350 | Photos are landscape — crop, don't stretch |
| Story / Reel | 1080×1920 | Keep the logo and copy inside the middle 80% |
| Link preview | 1200×630 | Wordmark bottom-left, scrim across the base |

Landscape photography does not fill a 9:16 frame without a hard crop. Prefer a
portrait-friendly subject (`bamboo-tower`, `entrance-canopy`, `villa-arrival`,
`dome-workers`) for stories, or place the photo in the upper two-thirds on an
olive field.
