/* Agartha — shared front-end behavior.
   Motion stack: GSAP + ScrollTrigger + SplitText + Lenis, loaded from CDN
   with defer before this file. Everything degrades gracefully: without JS or
   the CDN, all content is fully visible (no CSS-hidden states). */

(function () {
  "use strict";

  // ----- Baseline behavior (no library needed) -----

  var header = document.getElementById("siteHeader");
  var onScroll = function () {
    if (window.scrollY > 40) header.classList.add("scrolled");
    else header.classList.remove("scrolled");
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var toggle = document.getElementById("navToggle");
  var nav = document.getElementById("mainNav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      nav.classList.toggle("open");
      document.body.classList.toggle("nav-open");
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("open");
        document.body.classList.remove("nav-open");
      });
    });
  }

  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  // Forms are front-end only for now — functionality to be wired later.
  document.querySelectorAll("form[data-demo]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var note = form.querySelector(".form-note");
      if (note) {
        note.textContent =
          "Thank you! Form submission will be connected to the backend soon.";
        note.style.display = "block";
      }
      form.reset();
    });
  });

  // ----- Motion system (GSAP required beyond this point) -----

  if (typeof window.gsap === "undefined") return;

  var hasScrollTrigger = typeof window.ScrollTrigger !== "undefined";
  var hasSplitText = typeof window.SplitText !== "undefined";
  if (hasScrollTrigger) gsap.registerPlugin(ScrollTrigger);
  if (hasSplitText) gsap.registerPlugin(SplitText);

  var motionOK = window.matchMedia(
    "(prefers-reduced-motion: no-preference)"
  ).matches;

  // Smooth scroll — Lenis honors prefers-reduced-motion on its own, but we
  // skip it entirely under reduced motion to keep behavior predictable.
  var lenis = null;
  if (typeof window.Lenis !== "undefined" && motionOK) {
    lenis = new Lenis({ lerp: 0.12 });
    if (hasScrollTrigger) lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add(function (t) {
      lenis.raf(t * 1000);
    });
    gsap.ticker.lagSmoothing(0);

    // Keep in-page anchors working through Lenis.
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
      link.addEventListener("click", function (e) {
        var target = document.querySelector(link.getAttribute("href"));
        if (target) {
          e.preventDefault();
          lenis.scrollTo(target, { offset: -70 });
        }
      });
    });
  }

  if (!motionOK || !hasScrollTrigger) return;

  // SplitText measures line breaks at init — splitting before the webfonts
  // arrive leaves masked lines sized for the fallback font, so the real font
  // reflows into overlapping, clipped text. Wait for fonts (2s cap).
  var startMotion = function () {
  var mm = gsap.matchMedia();

  mm.add(
    {
      motionOK: "(prefers-reduced-motion: no-preference)",
      desktop: "(min-width: 768px)",
      finePointer: "(pointer: fine)",
    },
    function (ctx) {
      if (!ctx.conditions.motionOK) return;

      // --- Hero entrance (light hero on home, overlay hero on inner pages) ---
      var heroTitle = document.querySelector(".hero-lite h1, .hero h1");
      var intro = gsap.timeline({ defaults: { ease: "expo.out" } });

      if (heroTitle && hasSplitText) {
        var split = SplitText.create(heroTitle, {
          type: "lines,words",
          mask: "lines",
        });
        intro.from(split.words, {
          yPercent: 110,
          duration: 0.9,
          stagger: 0.05,
          delay: 0.1,
        });
      } else if (heroTitle) {
        intro.from(heroTitle, { y: 40, autoAlpha: 0, duration: 0.9, delay: 0.1 });
      }

      intro.from(
        [".hero .hero-kicker", ".hero p.lead", ".hero .hero-actions"],
        { y: 26, autoAlpha: 0, duration: 0.7, stagger: 0.12 },
        heroTitle ? "-=0.55" : 0
      );
      // clearProps: a leftover inline transform would make the fixed header
      // the containing block for the fixed mobile-nav overlay, shrinking it
      // to the header's box.
      intro.from(
        ".site-header",
        { y: -24, autoAlpha: 0, duration: 0.6, clearProps: "all" },
        "-=0.6"
      );

      // Hero background settles + gently parallaxes on scroll (desktop only —
      // background-position animation is cheap but pointless on small screens).
      var hero = document.querySelector(".hero");
      if (hero && ctx.conditions.desktop) {
        gsap.to(hero, {
          backgroundPosition: "50% 78%",
          ease: "none",
          scrollTrigger: {
            trigger: hero,
            start: "top top",
            end: "bottom top",
            scrub: true,
          },
        });
      }

      // --- Scroll reveals ---
      // Grids get staggered children; every other .reveal animates alone.
      var handled = new Set();
      var groupSelectors =
        ".card-grid, .amenity-grid, .gallery-grid, .stat-row";

      document.querySelectorAll(groupSelectors).forEach(function (group) {
        var children = Array.prototype.slice.call(group.children);
        if (!children.length) return;
        children.forEach(function (c) {
          handled.add(c);
        });
        gsap.from(children, {
          y: 30,
          autoAlpha: 0,
          duration: 0.7,
          ease: "power3.out",
          stagger: 0.08,
          clearProps: "transform",
          scrollTrigger: { trigger: group, start: "top 82%", once: true },
        });
      });

      var alt = 0;
      document.querySelectorAll(".reveal").forEach(function (el) {
        if (handled.has(el)) return;
        // Vary the entrance axis so the page isn't uniformly bottom-up.
        var fromVars =
          el.closest(".split") && alt++ % 2
            ? { x: -36, autoAlpha: 0 }
            : { y: 32, autoAlpha: 0 };
        fromVars.duration = 0.8;
        fromVars.ease = "power3.out";
        fromVars.clearProps = "transform";
        fromVars.scrollTrigger = { trigger: el, start: "top 84%", once: true };
        gsap.from(el, fromVars);
      });

      // Section titles rise with a slight settle.
      document.querySelectorAll(".section-title").forEach(function (t) {
        gsap.from(t, {
          y: 24,
          autoAlpha: 0,
          duration: 0.8,
          ease: "power3.out",
          clearProps: "transform",
          scrollTrigger: { trigger: t, start: "top 88%", once: true },
        });
      });

      // Footer panorama drifts as it passes (desktop).
      var band = document.querySelector(".photo-band img");
      if (band && ctx.conditions.desktop) {
        gsap.fromTo(
          band,
          { yPercent: -8, scale: 1.12 },
          {
            yPercent: 8,
            scale: 1.12,
            ease: "none",
            scrollTrigger: {
              trigger: band,
              start: "top bottom",
              end: "bottom top",
              scrub: true,
            },
          }
        );
      }

      // --- Micro-interaction: pointer tilt on offer cards ---
      if (ctx.conditions.desktop && ctx.conditions.finePointer) {
        document.querySelectorAll(".offer-card").forEach(function (card) {
          card.addEventListener("pointermove", function (e) {
            var r = card.getBoundingClientRect();
            var rx = ((e.clientY - r.top) / r.height - 0.5) * -6;
            var ry = ((e.clientX - r.left) / r.width - 0.5) * 6;
            gsap.to(card, {
              rotateX: rx,
              rotateY: ry,
              transformPerspective: 800,
              duration: 0.4,
              ease: "power2.out",
            });
          });
          card.addEventListener("pointerleave", function () {
            gsap.to(card, {
              rotateX: 0,
              rotateY: 0,
              duration: 0.5,
              ease: "power3.out",
            });
          });
        });
      }

      return function () {};
    }
  );

  // Triggers can misalign once webfonts/CDN images finish loading.
  window.addEventListener("load", function () {
    ScrollTrigger.refresh();
  });
  };

  if (document.fonts && document.fonts.ready) {
    Promise.race([
      document.fonts.ready,
      new Promise(function (resolve) { setTimeout(resolve, 2000); }),
    ]).then(startMotion);
  } else {
    startMotion();
  }
})();
