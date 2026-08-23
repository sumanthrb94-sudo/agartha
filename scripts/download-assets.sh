#!/usr/bin/env bash
# Re-fetch the full-resolution originals listed in assets/asset_manifest.csv
# from the Wix CDN into assets/originals/ (~215 MB, git-ignored).
#
# The site no longer needs this: every image it serves is already self-hosted
# under assets/web/ and assets/site/. Reach for it only when you need a
# print-quality source that the 1920px WebP derivative can't give you.
#
#   bash scripts/download-assets.sh
#
set -euo pipefail

manifest="assets/asset_manifest.csv"
outdir="assets/originals"
mkdir -p "$outdir"

# Column 2 of the manifest is the original source URL; skip the header row.
tail -n +2 "$manifest" | while IFS=, read -r filename source_url _rest; do
  [ -z "$filename" ] && continue
  dest="$outdir/$filename"
  if [ -f "$dest" ]; then
    echo "skip  $filename (exists)"
  else
    echo "fetch $filename"
    curl -fsSL --retry 3 -o "$dest" "$source_url"
  fi
done

echo "Done. Files are in $outdir/ (git-ignored — they are sources, not shipped)."
