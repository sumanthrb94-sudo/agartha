# Image assets

Every image the site serves is self-hosted from this folder — there are no CDN
hotlinks left. `scripts/check-assets.py` enforces that.

| Folder | What's in it |
| --- | --- |
| `web/` | The imagery published on agartha.in. Filenames keep the original Wix stems so each one stays traceable against `asset_manifest.csv`. |
| `site/` | Photography and renders supplied directly by the client — the build in progress, interiors, villa studies. Semantic names. |
| `brand/` | The official identity: mark, wordmark, lockups, favicon, in sage and olive. |

`asset_manifest.csv` is the record of all 35 image assets captured from
agartha.in: source URL, page usage (home / gallery), dimensions, byte sizes,
hashes and responsive variants.

## Sizes

Each image ships as up to three WebP files:

    name.webp        native size, capped at 1920px on the long edge
    name-900.webp    only when the source is wider than 900px
    name-480.webp    phones

Pages reference them through `srcset`, so a phone never downloads a desktop
payload. Hero backgrounds are CSS, not `<img>`, so they switch between the base
and `-900` file at a 900px media query instead (`.hero-photo` in `css/styles.css`).
Gallery tiles carry `data-full` pointing at the base file — that's what the
lightbox opens, so a click gives you the full-size image rather than an upscaled
thumbnail.

## Rebuilding

`scripts/build-images.py` produces everything here from the raw asset drop. The
sources are not in the repo (the originals alone are ~215 MB); point it at the
extracted drop and run it:

    AGARTHA_DROP=/path/to/agartha python scripts/build-images.py
    python scripts/build-images.py --check     # report only
    python scripts/build-images.py --force     # rebuild existing files

The mapping from source file to shipped name lives in that script, which is
also where to add a new photograph.

### Deliberately not shipped

Some of the drop is in the repo's history but not in the deploy, on purpose:

- **Raster icons** for yoga, pool, dining, gym, celebration and sunrise — the
  vector set in `icons.svg` is sharper at every size and themeable.
- **A solid-black 1080×1920 file** from the source site, which has no content.
- **Second crops** of shots already here: another angle on the terracotta
  alcove, a fourth bamboo-dome frame, a second front-on thatch villa.
- **The AGARTHA logo and palette images** from the client drop — already
  vectorised into `brand/`.
- **One phone screenshot** with the gallery app's own UI in frame.

## Checking

    python scripts/check-assets.py

Fails if any referenced image is missing, if any off-site image URL creeps back
in, or if a file ships that nothing references. A handful of files are
unreferenced on purpose (spare brand lockups, the vector favicon); they are
listed with their reason inside the script.
