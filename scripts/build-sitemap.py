#!/usr/bin/env python3
"""Regenerate sitemap.xml from the pages that actually ship.

Two things go stale in a hand-written sitemap, and both mislead Google:

  * a page is added or removed and nobody edits the XML — the new one never
    gets crawled, the dead one gets crawled until it 404s enough times;
  * `lastmod` keeps saying a date the page has long since moved past, so a
    rewritten page is treated as unchanged and stays out of the index.

So the list of pages is checked against the repo, and `lastmod` is taken
from the file's last commit rather than typed. Priority and changefreq are
editorial and stay declared here.

    python scripts/build-sitemap.py          # rewrite sitemap.xml
    python scripts/build-sitemap.py --check  # verify it is current, write nothing

Exits non-zero if a public page is missing from the list, or (under --check)
if the file on disk is out of date.
"""

import datetime
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# path, url, changefreq, priority. Order is the order they appear in the file.
PAGES = [
    ("index.html", "/", "weekly", "1.0"),
    ("membership.html", "/membership", "monthly", "0.8"),
    ("holiday-homes.html", "/holiday-homes", "monthly", "0.8"),
    ("resort.html", "/resort", "monthly", "0.8"),
    ("gallery.html", "/gallery", "monthly", "0.7"),
    ("contact.html", "/contact", "monthly", "0.7"),
]

# Shipped but deliberately absent from the sitemap: the error page has no
# content of its own, and the two consoles are behind a login and are
# already Disallowed in robots.txt.
NOT_PUBLIC = {"404.html", "admin.html", "analytics.html"}


def base_url():
    """The site's own address, taken from the home page's canonical.

    Reading it rather than hardcoding it means the domain move is still the
    single find-and-replace the README describes: change the canonicals and
    the sitemap follows.
    """
    head = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read(4000)
    m = re.search(r'<link rel="canonical" href="(https?://[^"]+?)/?"', head)
    if not m:
        sys.exit("index.html has no canonical URL to take the domain from")
    return m.group(1)


def last_modified(path):
    """Commit date of the file, falling back to its mtime when uncommitted."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", path],
            cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", path],
            cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        if out and not dirty:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    ts = os.path.getmtime(os.path.join(ROOT, path))
    return datetime.date.fromtimestamp(ts).isoformat()


def main():
    check = "--check" in sys.argv
    listed = {p for p, _, _, _ in PAGES}

    shipped = {f for f in os.listdir(ROOT) if f.endswith(".html")}
    missing = sorted(listed - shipped)
    unlisted = sorted(shipped - listed - NOT_PUBLIC)
    if missing:
        sys.exit(f"sitemap lists pages that do not exist: {', '.join(missing)}")
    if unlisted:
        sys.exit(f"public pages missing from the sitemap: {', '.join(unlisted)}\n"
                 f"add them to PAGES in {os.path.relpath(__file__, ROOT)}")

    base = base_url()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, url, freq, priority in PAGES:
        lines += ["  <url>",
                  f"    <loc>{base}{url}</loc>",
                  f"    <lastmod>{last_modified(path)}</lastmod>",
                  f"    <changefreq>{freq}</changefreq>",
                  f"    <priority>{priority}</priority>",
                  "  </url>"]
    lines.append("</urlset>")
    body = "\n".join(lines) + "\n"

    target = os.path.join(ROOT, "sitemap.xml")
    current = open(target, encoding="utf-8").read() if os.path.exists(target) else ""

    if check:
        if body != current:
            print("sitemap.xml is out of date — run scripts/build-sitemap.py")
            return 1
        print(f"sitemap.xml is current — {len(PAGES)} URLs at {base}")
        return 0

    open(target, "w", encoding="utf-8").write(body)
    print(f"wrote sitemap.xml — {len(PAGES)} URLs at {base}")
    for path, url, _, _ in PAGES:
        print(f"  {base}{url}  lastmod {last_modified(path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
