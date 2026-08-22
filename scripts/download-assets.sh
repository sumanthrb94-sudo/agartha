#!/usr/bin/env bash
# Download all image assets listed in assets/asset_manifest.csv from the Wix CDN
# into assets/originals/, so the site can be switched from CDN hotlinks to
# self-hosted files later. Run from the repo root on a machine with normal
# internet access:
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

echo "Done. Files are in $outdir/."
echo "To self-host, replace https://static.wixstatic.com/media/<name>[/v1/...] URLs"
echo "in the HTML with assets/originals/<name> (or resized copies)."
