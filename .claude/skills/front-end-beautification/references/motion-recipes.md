# Motion recipes

Concrete, copy-adaptable patterns for the beautification pass. All vanilla
JS/CSS unless noted — they work on static no-build sites. Adapt names and
values to the project; don't paste blindly.

## Contents

1. [CDN setup](#cdn-setup)
2. [Lenis smooth scroll](#lenis-smooth-scroll)
3. [GSAP reveals & staggers](#gsap-reveals--staggers)
4. [Split-text headline](#split-text-headline)
5. [Parallax & pinned sections](#parallax--pinned-sections)
6. [Number ticker](#number-ticker)
7. [Infinite marquee](#infinite-marquee)
8. [Micro-interactions](#micro-interactions)
9. [CSS-only fallbacks](#css-only-fallbacks)
10. [Reduced motion & responsive gating](#reduced-motion--responsive-gating)

## CDN setup

Load once, before the site's own script, with `defer`:

```html
<script defer src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/gsap@3/dist/SplitText.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/lenis@1/dist/lenis.min.js"></script>
```

SplitText, ScrollSmoother, MorphSVG etc. are MIT-free since GSAP 3.13.
Register plugins first thing: `gsap.registerPlugin(ScrollTrigger, SplitText)`.

## Lenis smooth scroll

```js
const lenis = new Lenis({ lerp: 0.12 });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((t) => lenis.raf(t * 1000));
gsap.ticker.lagSmoothing(0);
```

Lenis honors `prefers-reduced-motion` automatically. Keep anchor links
working by letting Lenis handle them: `lenis.scrollTo(target)` in the click
handler. Don't stack Lenis with GSAP's ScrollSmoother — pick one.

## GSAP reveals & staggers

Author hidden states IN JS (via `gsap.from`) so content is visible when JS
fails — never `opacity: 0` in the stylesheet.

```js
// One-off section reveal
gsap.utils.toArray('[data-reveal]').forEach((el) => {
  gsap.from(el, {
    y: 32, autoAlpha: 0, duration: 0.8, ease: 'power3.out',
    scrollTrigger: { trigger: el, start: 'top 82%', once: true },
  });
});

// Staggered children (cards, list items, nav links)
gsap.utils.toArray('[data-stagger]').forEach((group) => {
  gsap.from(group.children, {
    y: 28, autoAlpha: 0, duration: 0.7, ease: 'power3.out',
    stagger: 0.08,
    scrollTrigger: { trigger: group, start: 'top 80%', once: true },
  });
});
```

Rules of thumb: entrances 500–800ms `power3.out`/`expo.out`; exits faster
than entrances; stagger 60–100ms; never `ease: 'linear'` for UI movement;
vary direction occasionally (`x: -32`) so the page isn't uniformly bottom-up.

## Split-text headline

The single highest-impact hero upgrade (Magic UI "blur-in", studio-site
standard):

```js
const split = SplitText.create('.hero h1', { type: 'words,chars' });
gsap.from(split.chars, {
  yPercent: 110, autoAlpha: 0, filter: 'blur(6px)',
  duration: 0.9, ease: 'expo.out', stagger: 0.02, delay: 0.15,
});
```

Wrap the heading in `overflow: hidden` line containers (`type:'lines'`,
`mask:'lines'`) for the classic rise-from-baseline look. Word-level stagger
(0.05–0.08) reads calmer than per-char; use chars only on short headlines.

## Parallax & pinned sections

```js
// Background image drifts slower than scroll (10–20% depth)
gsap.to('.hero-bg', {
  yPercent: 18, ease: 'none',
  scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
});

// Sticky split panel (Linear/Stripe pattern): pin visual, scroll text
ScrollTrigger.create({
  trigger: '.split-section', start: 'top top',
  end: () => '+=' + document.querySelector('.split-steps').offsetHeight,
  pin: '.split-visual', pinSpacing: false,
});
```

Give parallaxed images extra bleed (`height: 120%; top: -10%`) so edges
never show. Scrubbed/pinned choreography belongs on 1–2 sections max.

## Number ticker

Magic UI / stats-band pattern — count up when visible:

```js
gsap.utils.toArray('[data-count]').forEach((el) => {
  const end = parseFloat(el.dataset.count);
  const obj = { v: 0 };
  gsap.to(obj, {
    v: end, duration: 1.6, ease: 'power2.out',
    snap: { v: end % 1 ? 0.01 : 1 },
    onUpdate: () => (el.textContent = obj.v.toLocaleString('en-IN')),
    scrollTrigger: { trigger: el, start: 'top 85%', once: true },
  });
});
```

## Infinite marquee

CSS-only, GPU-friendly, pausable. Duplicate the track content once in HTML
(`aria-hidden="true"` on the copy):

```css
.marquee { overflow: hidden; display: flex; }
.marquee-track {
  display: flex; gap: 3rem; flex-shrink: 0; min-width: 100%;
  animation: marquee 28s linear infinite;
}
.marquee:hover .marquee-track { animation-play-state: paused; }
@keyframes marquee { to { transform: translateX(-100%); } }
```

## Micro-interactions

```css
/* Card lift — transform + shadow, ease-out, 250ms */
.card { transition: transform .25s cubic-bezier(.22,.61,.36,1), box-shadow .25s; }
.card:hover { transform: translateY(-6px); box-shadow: var(--shadow-hover); }

/* Image zoom inside a fixed frame */
.frame { overflow: hidden; }
.frame img { transition: transform .6s cubic-bezier(.22,.61,.36,1); }
.frame:hover img { transform: scale(1.05); }

/* Underline draw for links */
.link { background: linear-gradient(currentColor, currentColor) 0 100% / 0 1px no-repeat; transition: background-size .3s; }
.link:hover { background-size: 100% 1px; }

/* Button press */
.btn:active { transform: scale(.97); }
```

Tilt card (boldpiq/Aceternity pattern) — pointer-driven, spring-free vanilla:

```js
card.addEventListener('pointermove', (e) => {
  const r = card.getBoundingClientRect();
  const rx = ((e.clientY - r.top) / r.height - 0.5) * -8;
  const ry = ((e.clientX - r.left) / r.width - 0.5) * 8;
  card.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg)`;
});
card.addEventListener('pointerleave', () => (card.style.transform = ''));
```

Magnetic CTA: translate the button toward the cursor by ~20% of the offset
within a 100px radius; reset with a 300ms ease-out on leave. Skip on touch.

## CSS-only fallbacks

When a library isn't warranted, IntersectionObserver + classes covers basic
reveals (add `.visible`, transition `opacity`/`transform`). CSS
scroll-driven animations (`animation-timeline: view()`) now work in all
evergreen browsers for simple reveal/parallax — use `@supports
(animation-timeline: view())` and keep the JS path as fallback.

## Reduced motion & responsive gating

Gate everything through one matchMedia block — this is the pro/junk divider:

```js
const mm = gsap.matchMedia();
mm.add(
  {
    motionOK: '(prefers-reduced-motion: no-preference)',
    desktop: '(min-width: 768px)',
  },
  (ctx) => {
    if (!ctx.conditions.motionOK) return; // no tweens at all
    initReveals();
    if (ctx.conditions.desktop) initParallaxAndPins(); // heavy stuff desktop-only
  }
);
```

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }
}
```

Performance checklist: animate transform/opacity/clip-path/filter only; no
`will-change` at rest; images get explicit `width`/`height` or
`aspect-ratio` (kills CLS); `ScrollTrigger.refresh()` after fonts/images
load if triggers misalign (`window.addEventListener('load', ...)`).
