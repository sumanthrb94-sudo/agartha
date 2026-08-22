# Image assets

The site currently loads all photography and icons directly from the original
Wix CDN (`static.wixstatic.com`) using the URLs recorded in
`asset_manifest.csv` — the manifest of the 35 image assets from agartha.in,
including source URLs, page usage (home/gallery), dimensions, hashes, and
responsive variant URLs.

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
