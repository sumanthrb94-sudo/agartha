#!/usr/bin/env python3
"""Stamp the Google Search Console verification tag into every public page.

Search Console verifies a URL-prefix property by fetching the address you
claimed and looking for its token in the `<head>`. Only the home page is
actually checked, but the tag goes on all six: Google re-checks periodically,
and a property silently loses verification if the tag disappears from
wherever it happens to look.

Paste either the bare token or the whole tag Search Console shows you —
both work, because copying the whole line is what people actually do.

    python scripts/set-verification.py "<meta name=... content=... />"
    python scripts/set-verification.py hHmR8w...        # the token alone
    python scripts/set-verification.py --show           # what is installed
    python scripts/set-verification.py --remove         # take it back out

Re-running with a different token replaces the old one rather than stacking
a second tag, so re-verifying after a domain move is the same one command.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The consoles are behind a login and Disallowed in robots.txt, and 404.html
# is not a page Google verifies against. Public pages only.
PAGES = ["index.html", "membership.html", "holiday-homes.html",
         "resort.html", "gallery.html", "contact.html"]

TAG = re.compile(
    r'[ \t]*<meta\s+name=(["\'])google-site-verification\1\s+content=(["\'])(?P<token>[^"\']*)\2\s*/?>\n?',
    re.I)
# The tag sits directly under the viewport meta — the top of the head, above
# the title, which is where Search Console's own instructions put it.
ANCHOR = re.compile(r'(^[ \t]*<meta name="viewport"[^>]*>\n)', re.M)


def extract(argument):
    """Accept a pasted <meta> tag, a bare token, or content="..." on its own."""
    m = re.search(r'content\s*=\s*["\']([^"\']+)["\']', argument)
    token = (m.group(1) if m else argument).strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{20,}", token):
        sys.exit(f"that does not look like a verification token: {token!r}\n"
                 "paste the whole <meta> tag from Search Console, or just the "
                 "content= value (letters, digits, _ and -).")
    return token


def main():
    args = [a for a in sys.argv[1:] if a.strip()]
    if not args:
        sys.exit(__doc__)

    if args[0] == "--show":
        for page in PAGES:
            text = open(os.path.join(ROOT, page), encoding="utf-8").read()
            m = TAG.search(text)
            print(f"  {page:<20} {m.group('token') if m else '— not verified'}")
        return 0

    removing = args[0] == "--remove"
    token = None if removing else extract(args[0])

    changed = []
    for page in PAGES:
        path = os.path.join(ROOT, page)
        text = open(path, encoding="utf-8").read()
        stripped = TAG.sub("", text)

        if removing:
            new = stripped
        else:
            tag = f'  <meta name="google-site-verification" content="{token}" />\n'
            if not ANCHOR.search(stripped):
                sys.exit(f"{page}: no viewport meta to anchor the tag to")
            new = ANCHOR.sub(lambda m: m.group(1) + tag, stripped, count=1)

        if new != text:
            open(path, "w", encoding="utf-8").write(new)
            changed.append(page)

    verb = "removed from" if removing else "written to"
    if changed:
        print(f"verification tag {verb} {len(changed)} page(s): {', '.join(changed)}")
    else:
        print("no change — every page already says exactly this")
    if not removing:
        print("\nNow: commit and push, wait for Vercel to redeploy, then press\n"
              "Verify in Search Console. Submit sitemap.xml once it goes green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
