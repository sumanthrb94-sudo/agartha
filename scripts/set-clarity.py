#!/usr/bin/env python3
"""Install, replace or remove the Microsoft Clarity tag across the site.

Clarity is a session recorder, not just a counter: it replays what visitors
did, which is why two things about this install are deliberate.

  * `/admin` and `/analytics` are excluded. Those pages render the lead table
    — real names, phone numbers and email addresses — and the login form.
    Recording them would ship customer PII and an admin typing credentials
    into a third party, for no analytical gain. They are also Disallowed in
    robots.txt, so nothing is lost.
  * `404.html` IS included. Which URLs people land on and fail to find is
    worth seeing, and the page holds no data.

    python scripts/set-clarity.py <project-id>   # install or replace
    python scripts/set-clarity.py --show         # what is installed
    python scripts/set-clarity.py --remove       # take it back out

Re-running with a different id replaces the block rather than stacking a
second tag. Remember the CSP in vercel.json also has to allow clarity.ms —
it already does.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = ["index.html", "membership.html", "holiday-homes.html", "resort.html",
         "gallery.html", "contact.html", "404.html"]
EXCLUDED = {"admin.html": "renders the lead table (customer PII)",
            "analytics.html": "renders lead and visitor data"}

OPEN, CLOSE = "<!-- Microsoft Clarity -->", "<!-- /Microsoft Clarity -->"
# Matched as a whole block so replacing is exact and removal leaves no crumbs.
# The leading indentation belongs to the block: without it, every install
# left two orphaned spaces welded to </head>, and they accumulated on each
# replace.
BLOCK = re.compile(
    r"[ \t]*" + re.escape(OPEN) + r".*?" + re.escape(CLOSE) + r"[ \t]*\n?", re.S)
ID_IN_BLOCK = re.compile(r'"clarity",\s*"script",\s*"([^"]+)"')


def snippet(pid):
    return (
        f'  {OPEN}\n'
        '  <script>\n'
        '    (function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};\n'
        '    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;\n'
        '    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);\n'
        f'    }})(window, document, "clarity", "script", "{pid}");\n'
        '  </script>\n'
        f'  {CLOSE}\n')


def check_id(raw):
    pid = raw.strip().strip('"\'')
    # Clarity ids are short lowercase alphanumeric strings. Catching a pasted
    # URL or a whole snippet here beats deploying a tag that silently 404s.
    m = re.search(r'clarity\.ms/tag/([a-z0-9]+)', pid)
    if m:
        pid = m.group(1)
    if not re.fullmatch(r"[a-z0-9]{6,20}", pid):
        sys.exit(f"that does not look like a Clarity project id: {pid!r}\n"
                 "it is a short lowercase alphanumeric string, e.g. 'q4k8n2xw1p' — "
                 "find it in Clarity under Settings → Overview, or in the install "
                 "snippet after 'clarity.ms/tag/'.")
    return pid


def main():
    args = [a for a in sys.argv[1:] if a.strip()]
    if not args:
        sys.exit(__doc__)

    if args[0] == "--show":
        for page in PAGES:
            text = open(os.path.join(ROOT, page), encoding="utf-8").read()
            m = BLOCK.search(text)
            found = ID_IN_BLOCK.search(m.group(0)) if m else None
            print(f"  {page:<20} {found.group(1) if found else '— not installed'}")
        for page, why in EXCLUDED.items():
            print(f"  {page:<20} — excluded on purpose: {why}")
        return 0

    removing = args[0] == "--remove"
    pid = None if removing else check_id(args[0])

    changed = []
    for page in PAGES:
        path = os.path.join(ROOT, page)
        text = open(path, encoding="utf-8").read()
        stripped = BLOCK.sub("", text)

        if removing:
            new = stripped
        elif "</head>" not in stripped:
            sys.exit(f"{page}: no </head> to anchor the tag to")
        else:
            # Last thing in the head: the tag is async either way, and this
            # keeps it from sitting between the page and its stylesheet.
            new = stripped.replace("</head>", snippet(pid) + "</head>", 1)

        if new != text:
            open(path, "w", encoding="utf-8").write(new)
            changed.append(page)

    verb = "removed from" if removing else "installed on"
    print(f"Clarity {verb} {len(changed)} page(s): {', '.join(changed) or 'none'}")
    for page, why in EXCLUDED.items():
        print(f"  skipped {page} — {why}")
    if not removing:
        print("\nCommit and push, wait for Vercel, then confirm in Clarity:\n"
              "Settings → Setup should flip to 'Tracking code detected'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
