#!/usr/bin/env python3
"""End-to-end check of the built site in a real browser.

Serves the repo on localhost and, for every page at four widths, reports:
  * console errors and page exceptions
  * failed requests / non-2xx responses (a 404 image is a broken page)
  * horizontal overflow (the body must never scroll sideways)
  * images that resolved but decoded to nothing
Then exercises the gallery lightbox, the mobile nav and the lead forms.

    python scripts/verify-site.py            # check, write screenshots
    python scripts/verify-site.py --shots-only
"""

import argparse
import http.server
import functools
import os
import socket
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "scripts", "screenshots")

PAGES = ["index.html", "investment.html", "membership.html", "resort.html",
         "holiday-homes.html", "gallery.html", "contact.html", "admin.html"]
WIDTHS = [("desktop", 1440, 900), ("laptop", 1100, 800),
          ("tablet", 820, 1000), ("mobile", 390, 844), ("narrow", 320, 700)]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    handler = functools.partial(Quiet, directory=ROOT)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{port}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots-only", action="store_true")
    args = ap.parse_args()

    os.makedirs(SHOTS, exist_ok=True)
    httpd, base = serve()
    problems, warnings = [], []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for label, w, h in WIDTHS:
            ctx = browser.new_context(viewport={"width": w, "height": h},
                                      device_scale_factor=1)
            page = ctx.new_page()
            for name in PAGES:
                errors, bad = [], []
                page.on("console", lambda m, e=errors:
                        e.append(m.text) if m.type == "error" else None)
                page.on("pageerror", lambda x, e=errors: e.append(f"exception: {x}"))
                page.on("requestfailed", lambda r, b=bad:
                        b.append(f"{r.url} ({r.failure})"))
                page.on("response", lambda r, b=bad:
                        b.append(f"HTTP {r.status} {r.url}") if r.status >= 400 else None)

                page.goto(f"{base}/{name}", wait_until="networkidle")
                page.wait_for_timeout(700)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1200)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(400)

                overflow = page.evaluate(
                    "() => document.documentElement.scrollWidth - "
                    "document.documentElement.clientWidth")
                # An img with no src yet (the lightbox stub) is not broken.
                broken = page.evaluate("""() => [...document.images]
                    .filter(i => (i.currentSrc || i.getAttribute('src')) &&
                                 i.complete && i.naturalWidth === 0)
                    .map(i => i.currentSrc || i.src)""")

                where = f"{name} @ {label}({w}px)"
                # Third-party CDNs (fonts, GSAP) are outside the site's control
                # and the page degrades gracefully without them — note, not fail.
                third = ("fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net")
                for e in errors:
                    bucket = warnings if "Failed to load resource" in e else problems
                    bucket.append(f"{where}  console: {e}")
                for b in set(bad):
                    bucket = warnings if any(h in b for h in third) else problems
                    bucket.append(f"{where}  request: {b}")
                if overflow > 0:
                    problems.append(f"{where}  horizontal overflow: {overflow}px")
                for b in broken:
                    problems.append(f"{where}  image decoded empty: {b}")

                page.screenshot(
                    path=os.path.join(SHOTS, f"{name.replace('.html','')}-{label}.png"),
                    full_page=(label == "desktop"))
                page.close()
                page = ctx.new_page()  # fresh listeners per page
            ctx.close()

        # ---- interactions (desktop + mobile) ----
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(f"{base}/gallery.html", wait_until="networkidle")
        tiles = page.locator(".gallery-grid img")
        count = tiles.count()
        # Tiles arrive via a scroll-triggered reveal, so scroll it into view
        # first — before that the tile is genuinely hidden, not broken.
        tiles.nth(0).scroll_into_view_if_needed()
        page.wait_for_timeout(1200)
        tiles.nth(0).click()
        page.wait_for_timeout(500)
        if not page.locator(".lightbox.open").is_visible():
            problems.append("gallery: lightbox did not open on click")
        else:
            shown = page.locator(".lightbox img").get_attribute("src")
            expected = tiles.nth(0).get_attribute("data-full")
            if expected and not shown.endswith(expected.split("/")[-1]):
                problems.append(f"gallery: lightbox showed {shown}, expected {expected}")
            page.locator(".lb-next").click()
            page.wait_for_timeout(300)
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            if page.locator(".lightbox.open").is_visible():
                problems.append("gallery: Escape did not close the lightbox")
        print(f"gallery tiles: {count}")
        ctx.close()

        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()
        page.goto(f"{base}/index.html", wait_until="networkidle")
        page.locator("#navToggle").click()
        page.wait_for_timeout(500)
        box = page.locator("#mainNav").bounding_box()
        if not box or box["width"] < 300:
            problems.append(f"mobile nav overlay is {box}, expected full-width")
        page.screenshot(path=os.path.join(SHOTS, "index-mobile-nav.png"))
        ctx.close()

        # Forms: every lead form must have its fields, honeypot and a submit.
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        for name in ["contact.html", "investment.html", "membership.html"]:
            page.goto(f"{base}/{name}", wait_until="domcontentloaded")
            forms = page.locator("form[data-lead]")
            if forms.count() == 0:
                problems.append(f"{name}: no lead form found")
            for i in range(forms.count()):
                f = forms.nth(i)
                kind = f.get_attribute("data-lead")
                if f.locator('input[name="website"]').count() != 1:
                    problems.append(f"{name}/{kind}: honeypot field missing")
                if f.locator('button[type="submit"]').count() != 1:
                    problems.append(f"{name}/{kind}: submit button missing")
                if f.locator(".form-note").count() != 1:
                    problems.append(f"{name}/{kind}: status note element missing")
        ctx.close()
        browser.close()

    httpd.shutdown()

    if warnings:
        print(f"\n{len(warnings)} third-party warning(s) "
              "(site degrades gracefully without these):")
        for w_ in sorted(set(warnings))[:8]:
            print("  " + w_)

    if problems:
        print(f"\n{len(problems)} PROBLEM(S):")
        for p_ in problems:
            print("  " + p_)
        return 1
    print("\nAll pages clean: no console errors, no failed requests, "
          "no horizontal overflow, no broken images.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
