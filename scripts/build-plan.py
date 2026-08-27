#!/usr/bin/env python3
"""Build the master-plan derivatives from the client's artwork.

The plan is kept out of build-images.py because it is not a photograph and does
not want that script's settings:

  * The client supplies it as a **CMYK** JPEG (print artwork). Pillow's
    ``convert("RGB")`` handles Adobe's inverted CMYK correctly; running the
    embedded ICC profile through ``profileToProfile`` instead desaturates the
    greens badly, so the plain convert is deliberate.
  * It is line art with numerals a few pixels tall, not a photo. The photo
    pipeline's quality ladder (80/78/72) rings around the plot outlines at the
    smaller sizes, so the two reductions here get more quality than the base.

Quality was chosen by measurement, not by eye: on the densest numbering the
base at q80 differs from q88 by an RMS of 4.4/255 (worst pixel 26) and saves
300 KB. Anything below that starts to soften the numerals.

    python3 scripts/build-plan.py path/to/master-plan.jpg
"""
import argparse
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "site"

# (filename, width, webp quality)
VARIANTS = [
    ("master-plan.webp", 1920, 80),
    ("master-plan-900.webp", 900, 86),
    ("master-plan-480.webp", 480, 84),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="the client's master-plan artwork (JPEG/PNG/TIFF)")
    a = ap.parse_args()

    src = pathlib.Path(a.source)
    if not src.is_file():
        print(f"not found: {src}", file=sys.stderr)
        return 1

    im = Image.open(src)
    print(f"{src.name}: {im.width}x{im.height} {im.mode}")
    rgb = im.convert("RGB")

    if rgb.width < VARIANTS[0][1]:
        print(f"  warning: source is only {rgb.width}px wide — the base variant "
              f"would be an upscale", file=sys.stderr)

    OUT.mkdir(parents=True, exist_ok=True)
    for name, width, q in VARIANTS:
        w = min(width, rgb.width)
        out = rgb.resize((w, round(rgb.height * w / rgb.width)), Image.LANCZOS)
        dest = OUT / name
        out.save(dest, "WEBP", quality=q, method=6)
        print(f"  {dest.relative_to(ROOT)}  {out.width}x{out.height}  "
              f"{dest.stat().st_size // 1024}KB  q{q}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
