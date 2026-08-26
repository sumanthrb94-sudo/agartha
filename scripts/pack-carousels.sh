#!/usr/bin/env bash
# Package each carousel as its own ready-to-post zip.
#
#   bash scripts/pack-carousels.sh [outdir]
#
# One zip per set: the numbered slides in swipe order, the caption and the
# posting sheet. Whoever posts needs nothing else.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/dist/carousels}"
mkdir -p "$OUT"

cd "$ROOT/carousels"
for dir in */; do
  slug="${dir%/}"
  case "$slug" in master|_guides) continue ;; esac
  zip="$OUT/agartha-$slug.zip"
  rm -f "$zip"
  zip -q -j "$zip" "$slug"/*.jpg "$slug"/caption.txt "$slug"/POST.md
  n=$(ls "$slug"/*.jpg | wc -l)
  printf '%-28s %s slides  %s\n' "$slug" "$n" "$(du -h "$zip" | cut -f1)"
done
