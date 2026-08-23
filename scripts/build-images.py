#!/usr/bin/env python3
"""Turn the raw asset drop into the WebP files the site ships.

Two sources feed the site:

  * `agartha_assets_2026-08-22/web/` — the 35 WebP derivatives of the images
    published on agartha.in. Filenames are the Wix stems and are kept as-is so
    they stay traceable against `assets/asset_manifest.csv`.
  * The loose WhatsApp photos in the same drop — site photography and renders
    that never went up on the Wix site. These get semantic names.

Every entry produces up to three files: the base (native size, capped at
1920px), `-900` (only when the source is wider than 900) and `-480`. The HTML
references them through `srcset` so phones never download a desktop payload.

    python scripts/build-images.py            # write anything missing
    python scripts/build-images.py --force    # rebuild everything
    python scripts/build-images.py --check    # report only, touch nothing

Source images are NOT in the repo (215 MB of originals); point DROP at the
extracted drop if you need to re-run this.
"""

import argparse
import os
import shutil
import sys

from PIL import Image

DROP = os.environ.get("AGARTHA_DROP", r"C:\Users\91779\Downloads\agartha")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WEB_SRC = os.path.join(DROP, "agartha_assets_2026-08-22", "web")
WEB_OUT = os.path.join(ROOT, "assets", "web")
SITE_OUT = os.path.join(ROOT, "assets", "site")

MAX_EDGE = 1920
QUALITY = {"base": 80, "900": 78, "480": 72}

# --- agartha.in assets (Wix stems kept verbatim) -----------------------------
# Only the ones the site actually uses. Deliberately skipped, with reasons:
#   142b26_37794a02...f000  a solid-black 1080x1920 spacer, no visual content
#   142b26_6d940483...      raster yoga icon   ) all three are superseded by the
#   142b26_8d442931...      raster pool icon   ) sharper vector set in
#   142b26_98457ab9...      raster dining icon ) assets/icons.svg
WEB_ASSETS = [
    "142b26_5f7c47258d394edcbf818b25e3b12965~mv2.webp",  # earthen home, oval windows
    "142b26_86e04d7ce83d497997bdac2c29efe900~mv2.webp",  # AGARTHA entrance gate
    "142b26_87ac7f7d92a145b9aa2740c4a6898410~mv2.webp",  # games pavilion
    "142b26_89a3906d085c4518a1ce49864ebda77a~mv2.webp",  # resort aerial
    "142b26_8ddd02a733d04a139fdd19e058e72d94~mv2.webp",  # master plan
    "142b26_a329de8538c44092bb941ee925dbcd7c~mv2.webp",  # clubhouse + spiral gardens
    "142b26_a79caac8357141ef89993d2115817696~mv2.webp",  # play area + canoe canal
    "142b26_a8649ae42bca482cbbafe84794fe8a6e~mv2.webp",  # pavilion villa
    "142b26_acda3bc9aaa84bfc976803cdcbdce73f~mv2.webp",  # home hero panorama
    "142b26_b52923b4599745df825e9d06157b43d3~mv2.webp",  # living-roof home + pool
    "142b26_bdabb7cd17f741ee815019462732e449~mv2.webp",  # thatch villas by the water
]

# --- Site photography and renders from the WhatsApp drop ---------------------
# name -> source filename. Skipped from the drop: the AGARTHA logo/palette
# files (already vectorised into assets/brand), one phone screenshot with the
# gallery-app chrome in frame, and second crops of shots already covered here —
# the terracotta alcove (interior-terracotta), a fourth dome-frame angle, and a
# second front-on thatch villa (thatch-villa-front).
SITE_PHOTOS = {
    # real photography on site
    "earthen-home-arched-door": "WhatsApp Image 2026-08-23 at 15.52.27.jpeg",
    "site-aerial-farm": "WhatsApp Image 2026-08-23 at 15.53.02.jpeg",
    "dome-frame-wide": "WhatsApp Image 2026-08-23 at 15.54.08.jpeg",
    "dome-frame-under": "WhatsApp Image 2026-08-23 at 15.54.08 (1).jpeg",
    "farm-arches": "WhatsApp Image 2026-08-23 at 15.54.15 (1).jpeg",
    "masons-brickwork": "WhatsApp Image 2026-08-23 at 15.54.18.jpeg",
    "bamboo-raising": "WhatsApp Image 2026-08-23 at 15.54.19.jpeg",
    "mud-brick-handover": "WhatsApp Image 2026-08-23 at 15.54.19 (1).jpeg",
    "thatch-eave-detail": "WhatsApp Image 2026-08-23 at 15.54.19 (2).jpeg",
    "bamboo-ceiling-detail": "WhatsApp Image 2026-08-23 at 15.54.20.jpeg",
    "farm-view-from-eave": "WhatsApp Image 2026-08-23 at 15.54.21 (1).jpeg",
    "site-path-progress": "WhatsApp Image 2026-08-23 at 15.54.21 (2).jpeg",
    "bamboo-roof-detail": "WhatsApp Image 2026-08-23 at 15.54.22.jpeg",
    "woven-dome-shell": "WhatsApp Image 2026-08-23 at 15.54.23.jpeg",
    # design renders
    "terraced-gardens": "WhatsApp Image 2026-08-23 at 15.52.17.jpeg",
    "earthen-home-terraces": "WhatsApp Image 2026-08-23 at 15.52.19.jpeg",
    "modern-villa-pergola": "WhatsApp Image 2026-08-23 at 15.54.10 (3).jpeg",
    "villa-entrance-pergola": "WhatsApp Image 2026-08-23 at 15.54.11 (1).jpeg",
    "thatch-villa-dusk": "WhatsApp Image 2026-08-23 at 15.54.12 (3).jpeg",
    "thatch-villa-drive": "WhatsApp Image 2026-08-23 at 15.54.13 (1).jpeg",
    "thatch-villa-front": "WhatsApp Image 2026-08-23 at 15.54.13 (2).jpeg",
    "villas-aerial-water": "WhatsApp Image 2026-08-23 at 15.54.14 (2).jpeg",
    "veranda-vines": "WhatsApp Image 2026-08-23 at 15.54.14 (3).jpeg",
}


def variants(src_path, out_dir, stem, force, check, log):
    """Write stem.webp / stem-900.webp / stem-480.webp from src_path."""
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        w, h = im.size
        if max(w, h) > MAX_EDGE:
            im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
            w, h = im.size

        targets = [("base", None, os.path.join(out_dir, stem + ".webp"))]
        if w > 900:
            targets.append(("900", 900, os.path.join(out_dir, f"{stem}-900.webp")))
        targets.append(("480", 480, os.path.join(out_dir, f"{stem}-480.webp")))

        for kind, width, dest in targets:
            if os.path.exists(dest) and not force:
                continue
            if check:
                log.append(f"  would write {os.path.relpath(dest, ROOT)}")
                continue
            out = im if width is None else im.resize(
                (width, round(h * width / w)), Image.LANCZOS)
            out.save(dest, "WEBP", quality=QUALITY[kind], method=6)
            log.append(f"  {os.path.relpath(dest, ROOT)}  "
                       f"{out.width}x{out.height}  {os.path.getsize(dest) // 1024}KB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="rebuild existing files")
    ap.add_argument("--check", action="store_true", help="report only")
    args = ap.parse_args()

    if not os.path.isdir(DROP):
        sys.exit(f"asset drop not found: {DROP}\nSet AGARTHA_DROP to its location.")

    os.makedirs(WEB_OUT, exist_ok=True)
    os.makedirs(SITE_OUT, exist_ok=True)
    log = []

    print(f"agartha.in assets -> {os.path.relpath(WEB_OUT, ROOT)}")
    for name in WEB_ASSETS:
        src = os.path.join(WEB_SRC, name)
        if not os.path.exists(src):
            log.append(f"  MISSING SOURCE {name}")
            continue
        stem = name[:-len(".webp")]
        dest = os.path.join(WEB_OUT, name)
        # The drop's WebP is already the 1920px derivative — copy it verbatim so
        # the file stays byte-identical to the manifest, then derive the rest.
        if not os.path.exists(dest) or args.force:
            if not args.check:
                shutil.copy2(src, dest)
            log.append(f"  {os.path.relpath(dest, ROOT)}  (copied)")
        variants(src, WEB_OUT, stem, args.force, args.check, log)

    print(f"site photography -> {os.path.relpath(SITE_OUT, ROOT)}")
    for stem, name in SITE_PHOTOS.items():
        src = os.path.join(DROP, name)
        if not os.path.exists(src):
            log.append(f"  MISSING SOURCE {name}")
            continue
        variants(src, SITE_OUT, stem, args.force, args.check, log)

    print("\n".join(log) if log else "  nothing to do — everything is up to date")


if __name__ == "__main__":
    main()
