# Image assets

Images are being migrated from Wix CDN hotlinks to self-hosted files as the
originals are provided:

- `web/` — self-hosted 1920px WebP derivatives (21 of 35 so far). Pages
  reference these directly where available.
- Everything else still loads from the original Wix CDN
  (`static.wixstatic.com`) using the URLs in `asset_manifest.csv` — the
  manifest of all 35 image assets from agartha.in, including source URLs,
  page usage (home/gallery), dimensions, hashes, and responsive variants.

To finish the migration, add the remaining `web/` files here with their
original filenames and swap the leftover `static.wixstatic.com` URLs in the
HTML (match by the 8-hex filename stem).

## Self-hosting the images later

Hotlinking works, but the images will break if the Wix site is ever taken
down. To move them into the repo:

1. Run `bash scripts/download-assets.sh` on a machine with normal internet
   access — it downloads every manifest entry into `assets/originals/`
   (~215 MB at full resolution).
2. Optionally resize/compress (e.g. 1920px WebP) before committing.
3. Find-and-replace the `https://static.wixstatic.com/media/...` URLs in the
   HTML files with the local paths.

`logo.png` — drop a brand logo here if you want to replace the CSS monogram
in the header.
