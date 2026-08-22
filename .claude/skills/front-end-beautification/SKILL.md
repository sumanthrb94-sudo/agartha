---
name: front-end-beautification
description: Elevate a website's front end from "AI-made template" to award-site polish — typography, spacing, imagery art direction, scroll choreography, and micro-interactions, using techniques from GSAP, Lenis, Magic UI, Motion, and anime.js. Use this skill whenever the user says a site looks sloppy, generic, boring, flat, "AI-generated", or unpolished; asks to beautify, redesign, modernize, or "make it look premium/pro"; asks for animations, motion, scroll effects, hover effects, or micro-interactions; or is building/reworking any landing page, marketing page, or portfolio front end — even if they don't use the word "design".
---

# Front-End Beautification

Turn a functional-but-generic front end into something that feels designed.
This skill encodes the patterns used by the most-starred motion/UI repos on
GitHub — [greensock/GSAP](https://github.com/greensock/GSAP) (MIT since the
Webflow acquisition, all pro plugins free),
[darkroomengineering/lenis](https://github.com/darkroomengineering/lenis)
(the smooth-scroll standard),
[magicuidesign/magicui](https://github.com/magicuidesign/magicui) (animated
components for design engineers),
[motiondivision/motion](https://github.com/motiondivision/motion) (formerly
Framer Motion, now vanilla-first), and
[juliangarnier/anime](https://github.com/juliangarnier/anime) (anime.js v4) —
plus the landing-page pattern language popularized by shadcn/ui, Aceternity,
and Awwwards-grade studio sites.

Concrete code recipes (CDN setup, GSAP/Lenis snippets, CSS patterns) live in
`references/motion-recipes.md` — read it before writing any animation code.

## Why sites read as "AI-made" — and what fixes each tell

Work through this table first. Motion added on top of a weak base makes a
site look *worse*; fix the static design before animating it.

| Tell | Why it happens | Fix |
| --- | --- | --- |
| Emoji as icons | Fastest placeholder | Consistent icon set: inline SVG (stroke-based, one weight, one color) or the brand's own icon files |
| Every section = centered heading + 3–4 identical cards | Grid templates are easy | Vary section anatomy: alternate split layouts, bento grids (cells of different spans), full-bleed image bands, editorial big-type sections, sticky side-panels |
| Uniform section heights & padding | One `section { padding }` rule | Compose a rhythm: dense → airy → full-bleed. Let one section be 40vh and the next 100vh. Whitespace is a design element, not leftover space |
| Headings all the same size-jump | Default h1–h3 | Real type scale (1.25–1.333 ratio), plus at least one oversized display moment per page (`clamp(3rem, 8vw, 7rem)`) with tight leading (0.95–1.1) and slight negative tracking |
| Flat #fff / one brand color everywhere | Palette applied, not designed | Layered neutrals (2–3 tints of the background), one saturated accent used sparingly, dark inverted sections for contrast beats |
| Images in identical rounded boxes | One `.img` class | Art direction: vary aspect ratios, allow full-bleed, overlap images across section boundaries, add a subtle inner shadow/gradient scrim, parallax the large ones |
| Hover = instant color swap | Default `:hover` | Micro-interaction: 200–350ms transform + shadow lift, icon nudge, underline draw, or gradient shift — always with an ease-out curve |
| Motion = everything fades up the same way | One reveal class | Choreography: staggered children, split-text headlines, clip-path reveals, scale-from-image, velocity-reactive marquees — chosen per element role |
| Buttons look like `<button>` defaults + border-radius | Unstyled interaction layer | Purposeful CTA design: one primary style, one ghost style, consistent paddings, pressed/tap states, focus-visible rings |
| Lorem ipsum, "placeholder copy", broken image frames | Unfinished content | Flag to the user; never ship placeholder text into a "polished" pass silently |

## Workflow

### 1. Audit before touching code

Open every page and list, per section: layout pattern, type sizes, image
treatment, hover states, motion. Score each against the table above. Present
the audit as a short prioritized list — the user should see *why* the site
reads as generic, not just receive a diff.

### 2. Establish the design system pass (static polish)

Do this entirely in CSS custom properties so later passes stay consistent:

- **Type**: display font for headlines (variable optical sizing if available),
  workhorse sans for UI/body. Define `--step--1 … --step-5` with `clamp()`
  fluid sizes. Body 16–18px, line-height 1.6–1.7; display leading ≤1.1.
- **Spacing**: an 8px-based scale (`--space-1 … --space-9`), section padding
  from the scale, not ad hoc.
- **Color**: background tint layers, one accent, dark section palette,
  borders at 8–12% opacity of the ink color instead of gray hexes.
- **Elevation**: two shadow levels max, tinted with the background hue
  (never pure black), plus a hover level.
- **Radius**: pick ONE radius family (e.g. 4/12/24) and use it everywhere.

### 3. Layout de-templating

Rebuild the 1–2 most template-looking sections per page using patterns from
the researched repos: a bento grid (Magic UI / Aceternity signature), a
sticky split panel (Linear/Stripe style — text scrolls, visual pins), an
editorial full-bleed image band with overlaid oversized type, or an
alternating zig-zag. Keep the rest — total redesign is not the goal;
breaking the grid monotony is.

### 4. Motion pass

Motion has a hierarchy — apply in this order and stop when the page feels
alive, not busy:

1. **Page entrance**: hero headline split-text reveal (words/chars staggered
   30–60ms), hero image scale-settle from 1.08→1, nav fade-down.
2. **Scroll reveals**: sections reveal once, 500–800ms, translateY 24–40px +
   fade, children staggered 60–100ms. Vary the axis occasionally.
3. **Scroll choreography** (only on hero + 1–2 hero-grade sections): parallax
   backgrounds (10–20% depth), pinned/scrubbed sequences, progress-linked
   counters (Magic UI number-ticker pattern).
4. **Ambient motion**: an infinite marquee (logos/keywords), a slow gradient
   drift, a floating shape — max one ambient element visible at a time.
5. **Micro-interactions**: card tilt/lift, magnetic CTA, underline draw,
   image zoom-on-hover inside fixed frame, button shimmer.

Library selection (details + code in `references/motion-recipes.md`):

| Need | Reach for | Why |
| --- | --- | --- |
| Scroll-driven anything, timelines, pinning, split text | GSAP + ScrollTrigger (+ SplitText — free now) | The industry standard; scrub/pin/snap unmatched |
| Smooth scroll feel | Lenis | 3KB, native-scroll-based, pairs with ScrollTrigger, honors reduced-motion by default |
| Small standalone tweens, staggers, springs without GSAP's weight | anime.js v4 or Motion (`motion/mini`, 2.6KB) | Modular, tiny |
| Simple reveal-on-scroll only, no library budget | IntersectionObserver + CSS classes | Zero deps; already sufficient for basic reveals |
| React codebases | Motion + Magic UI / shadcn patterns | Copy-paste animated components |

Static no-build sites load GSAP/Lenis from CDN (jsDelivr) — no bundler needed.

### 5. Accessibility & performance gates

Non-negotiable — this is what separates pro motion from junk motion:

- Wrap ALL non-essential animation behind `prefers-reduced-motion` (CSS
  `@media` + `gsap.matchMedia()`); reveals become instant, marquees stop.
- Animate only `transform`, `opacity`, `clip-path`, `filter` — never
  layout properties (top/left/width/height/margin).
- `will-change` only on elements mid-animation; remove after.
- Keep total added JS under ~90KB gzipped (GSAP core+ScrollTrigger+Lenis
  fits); lazy-init below-the-fold animation.
- Keyboard focus states must survive the redesign (`:focus-visible` rings).
- Test at 375px, 768px, 1280px+; heavy scroll effects get reduced or
  disabled under 768px via `gsap.matchMedia()`.

### 6. Verify like a reviewer

Before declaring done: scroll every page top to bottom slowly, then fast.
Check for reveal-flash (content invisible before JS runs — always author the
hidden state in JS, not CSS, so no-JS users see everything), scroll jank,
overlapping z-index accidents, CLS from late images (set width/height or
aspect-ratio on every img), and the reduced-motion mode actually working
(DevTools → Rendering → emulate prefers-reduced-motion).

## Output expectations

- Keep the site's content, brand palette direction, and information
  architecture intact unless asked otherwise — beautification is not
  rewriting copy or rebranding.
- Prefer editing the existing CSS/JS in place over introducing a framework.
- Commit in logical passes (tokens/type → layout → motion) so each step is
  reviewable and revertible.
- After the pass, summarize what changed per the audit list, and note any
  content-level issues (placeholder copy, missing images) left for the user.
