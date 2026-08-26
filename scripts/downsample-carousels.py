#!/usr/bin/env python3
"""Downsample the 2x carousel masters to Instagram's native 1080x1350.

Instagram serves feed images at 1080px wide, so the upload is resampled by Meta
whatever we send. Supersampling — rendering at 2x and reducing with Lanczos —
gives markedly cleaner type edges than rendering at 1x directly, and leaves a
2160px master for print, ads and other platforms.

    python3 scripts/downsample-carousels.py [--src carousels/master] [--out carousels] [--width 1080]
"""
import argparse
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="carousels/master")
    ap.add_argument("--out", default="carousels")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--quality", type=int, default=94)
    a = ap.parse_args()

    src, out = ROOT / a.src, ROOT / a.out
    masters = sorted(src.rglob("*.jpg"))
    if not masters:
        print(f"no masters under {src} — run build-carousels.mjs first", file=sys.stderr)
        return 1

    done = 0
    for m in masters:
        im = Image.open(m).convert("RGB")
        if im.width <= a.width:
            print(f"  skip {m.name}: already {im.width}px", file=sys.stderr)
            continue
        h = round(im.height * a.width / im.width)
        dst = out / m.relative_to(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.resize((a.width, h), Image.LANCZOS).save(
            dst, "JPEG", quality=a.quality, subsampling=0, optimize=True
        )
        done += 1

    sample = Image.open(next(iter(sorted(out.rglob("*.jpg")))))
    print(f"{done} slides downsampled to {sample.width}x{sample.height} "
          f"(Lanczos, q{a.quality}, 4:4:4 chroma)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
