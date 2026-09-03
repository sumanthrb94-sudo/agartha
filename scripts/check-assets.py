#!/usr/bin/env python3
"""Cross-check the asset folders against what the HTML actually references.

Reports four things:
  * broken      — a path referenced in HTML/CSS/JS with no file behind it
  * external    — any remaining off-site image URL (the site self-hosts)
  * unaccounted — a shipped image nothing references and nothing explains
  * intentional — shipped but unreferenced on purpose, listed below

    python scripts/check-assets.py
Exits non-zero if anything is broken, hotlinked, or unaccounted for.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_EXT = (".html", ".css", ".js")
IMAGE_EXT = (".webp", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".gif")

REF = re.compile(
    r"""(?:src|href|srcset|url|data-full)\s*[=(]\s*["']?([^"')\s>]+)""", re.I)
SRCSET = re.compile(r"""srcset\s*=\s*["']([^"']+)["']""", re.I)
# Only images the browser actually fetches — og:image and twitter:image are
# absolute by spec and must stay that way, so `content=` is deliberately excluded.
EXTERNAL = re.compile(
    r"""(?:src|srcset|url)\s*[=(]\s*["']?\s*(https?://[^"')\s]+\.(?:webp|png|jpe?g|gif|svg))""",
    re.I)
# ...but they still *use* the file, so the same absolute URLs have to count as a
# reference or the OG image reads as dead weight. Only the path after the host
# matters; whichever domain the site is on, it resolves to the same repo file.
META_REF = re.compile(
    r"""content\s*=\s*["']https?://[^"'/]+/([^"'\s]+\.(?:webp|png|jpe?g|gif|svg))["']""", re.I)

# Shipped on purpose even though no page links them.
INTENTIONAL = {
    "assets/favicon.svg": "vector favicon kept beside the PNG the pages use",
    "assets/brand/lockup-line-sage.png": "brand kit: horizontal lockup",
    "assets/brand/lockup-vert-olive.png": "brand kit: olive-on-light lockup",
    "assets/brand/mark-olive.png": "brand kit: olive-on-light mark",
    "assets/brand/wordmark-olive.png": "brand kit: olive-on-light wordmark",
    # Heroes are CSS backgrounds and switch at 900px, so they use the base and
    # -900 files only. The 480 variants fall out of the uniform build.
    "assets/web/142b26_5a1d622ef5d5437aa5da964188a3266e~mv2-480.webp": "hero variant",
    "assets/web/142b26_86e04d7ce83d497997bdac2c29efe900~mv2-480.webp": "hero variant",
    "assets/web/142b26_e952e8d04d6546b5866e374206744e87~mv2-480.webp": "hero variant",
}


def source_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "scripts", ".claude")]
        for f in files:
            if f.endswith(SOURCE_EXT):
                yield os.path.join(base, f)


def shipped_images():
    for base, dirs, files in os.walk(os.path.join(ROOT, "assets")):
        for f in files:
            if f.endswith(IMAGE_EXT):
                yield os.path.relpath(os.path.join(base, f), ROOT).replace("\\", "/")


def main():
    referenced, broken, external = set(), [], []

    for path in source_files():
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        text = open(path, encoding="utf-8").read()

        for url in EXTERNAL.findall(text):
            external.append((rel, url))

        candidates = set(REF.findall(text))
        candidates.update(META_REF.findall(text))
        for block in SRCSET.findall(text):
            for part in block.split(","):
                candidates.add(part.strip().split()[0] if part.strip() else "")

        for ref in candidates:
            ref = ref.split("#")[0].split("?")[0].strip()
            if not ref or ref.startswith(("http", "//", "data:", "mailto:", "tel:")):
                continue
            if not ref.lower().endswith(IMAGE_EXT):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), ref))
            key = os.path.relpath(target, ROOT).replace("\\", "/")
            referenced.add(key)
            if not os.path.exists(target):
                broken.append((rel, ref))

    shipped = set(shipped_images())
    unused = sorted(shipped - referenced)

    print(f"referenced image paths: {len(referenced)}")
    print(f"shipped image files:    {len(shipped)}")

    if broken:
        print(f"\nBROKEN ({len(broken)}):")
        for where, ref in sorted(set(broken)):
            print(f"  {where} -> {ref}")
    else:
        print("\nBROKEN: none — every referenced image resolves")

    if external:
        print(f"\nEXTERNAL image URLs ({len(external)}):")
        for where, url in sorted(set(external)):
            print(f"  {where} -> {url}")
    else:
        print("EXTERNAL: none — all imagery is self-hosted")

    accounted = [u for u in unused if u in INTENTIONAL]
    unaccounted = [u for u in unused if u not in INTENTIONAL]
    stale = sorted(set(INTENTIONAL) - shipped)

    if accounted:
        print(f"\nINTENTIONAL ({len(accounted)}):")
        for u in accounted:
            print(f"  {u}  — {INTENTIONAL[u]}")
    for u in stale:
        print(f"  note: {u} is on the intentional list but is not shipped")

    if unaccounted:
        total = sum(os.path.getsize(os.path.join(ROOT, u)) for u in unaccounted)
        print(f"\nUNACCOUNTED ({len(unaccounted)}, {total // 1024}KB dead weight):")
        for u in unaccounted:
            print(f"  {u}")
    else:
        print("UNACCOUNTED: none — every shipped image is used or explained")

    return 1 if broken or external or unaccounted else 0


if __name__ == "__main__":
    sys.exit(main())
