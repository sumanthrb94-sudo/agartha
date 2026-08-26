# Agartha carousels — ready to post

Three finished Instagram carousel sets, each a folder you can hand straight to
whoever posts.

| Set | Folder | Slides | Story |
|---|---|---|---|
| 1 | `why-agartha/` | 7 | What the place is — 25 acres, the four propositions, come and walk it |
| 2 | `how-its-built/` | 7 | The craft — earth blocks, bamboo, thatch, then it becomes a home |
| 3 | `holiday-homes/` | 5 | The commercial offer — own it, earn from it, let's talk numbers |

Each folder holds:

- `01.jpg` … `NN.jpg` — the slides, **1080×1350**, in swipe order
- `caption.txt` — copy-paste caption, hashtags included
- `POST.md` — slide-by-slide sheet, alt text, posting notes

## How they were made

Rendered at 2× (2160×2700) by `scripts/build-carousels.mjs` from
`scripts/carousels.json`, then reduced to Instagram's native 1080px with Lanczos
resampling at quality 94 and 4:4:4 chroma (`scripts/downsample-carousels.py`).
Supersampling is why the type edges are clean. The 2× masters are kept in
`master/` for print, ads and other platforms.

Every colour, typeface and photograph is drawn from `BRAND.md`. No figure
appears on a slide that is not already published on agartha.in.

## Changing the copy

Edit `scripts/carousels.json`, then:

```
node scripts/build-carousels.mjs          # 2x masters
python3 scripts/downsample-carousels.py   # 1080px deliverables
```

Add `--guides` to the build to write `_guides/` — the same slides overlaid with
Instagram's 1:1 grid crop, 3:4 crop and the text-safe box, for checking that
nothing important sits near an edge.
