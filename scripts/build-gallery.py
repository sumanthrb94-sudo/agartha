#!/usr/bin/env python3
"""Regenerate the gallery.html image sections from the captioned list below.

The gallery is sixty images in three groups, and each tile needs a `src`, a
two- or three-entry `srcset`, a `sizes` and a `data-full` for the lightbox —
far too much repetition to hand-edit safely. Add, drop or re-caption an image
in GROUPS and re-run; the script rewrites everything between the
`<!-- Gallery grid -->` marker and the offers block, checks that each file it
references actually exists, and picks the right srcset widths per image.

    python scripts/build-gallery.py
"""
import os
import re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZES = "(max-width: 820px) 100vw, (max-width: 1020px) 50vw, 33vw"

W = "assets/web/142b26_"
A = "assets/web/a6cde1_"
S = "assets/site/"

GROUPS = [
    ("The Resort", "Three Acres of It",
     "The clubhouse, the pools and the play — the shared heart of the 25 acres.", [
         (W + "07ba6ec4ef4e49d680a53ab9a3362f25~mv2", "Resort pavilion beside the natural pond"),
         (W + "13ce857bed164143a7d79ce6cef3668e~mv2", "Clubhouse lounge with fire pit and bar"),
         (W + "34c58cd885c64ddebbae12791465bbe3~mv2", "Poolside open-air cinema and dining"),
         (W + "04f61d366de9472cb87db76b28b272fc~mv2", "Open-air gym under the bamboo canopy"),
         (W + "87ac7f7d92a145b9aa2740c4a6898410~mv2", "Games pavilion with pool, table tennis and foosball"),
         (W + "a79caac8357141ef89993d2115817696~mv2", "Canoe on the water channel beside the play area"),
         (W + "0fee06470ac2445c9ff7742be6377273~mv2", "Fire pit and garden swing at dawn"),
         (W + "a329de8538c44092bb941ee925dbcd7c~mv2", "Clubhouse and the spiral herb gardens from above"),
         (W + "89a3906d085c4518a1ce49864ebda77a~mv2", "The resort from above — pools, pavilions and the water channel"),
     ]),
    ("Homes &amp; Gardens", "Where You'll Live",
     "Earthen homes, thatch villas and the food forest they sit inside.", [
         (W + "acda3bc9aaa84bfc976803cdcbdce73f~mv2", "Food forest and flowering beds through the estate"),
         (W + "bdabb7cd17f741ee815019462732e449~mv2", "Two thatch villas along the water channel"),
         (W + "a8649ae42bca482cbbafe84794fe8a6e~mv2", "Pavilion villa under a layered roof"),
         (W + "b52923b4599745df825e9d06157b43d3~mv2", "Living-roof earthen home above the pool"),
         (W + "5f7c47258d394edcbf818b25e3b12965~mv2", "Earthen home with oval windows on a stone plinth"),
         (W + "e9917bb73fc94531948ef638eba5a051~mv2", "Earthen home wrapped by terraced planting beds"),
         (W + "3a60dc75703c4cc2a29c6d44f41b8e21~mv2", "Earthen farmhouse among the trees"),
         (W + "567e195b978947c9b29be195842095af~mv2", "Farmhouses along the walking path"),
         (W + "5a78474b934e4251b54ce25e16770c68~mv2", "Earthen home with an arched door by the water"),
         (W + "bddb7151495f4ff2a9d71a606def46bf~mv2", "Resort huts under thatched roofs"),
         (W + "d9f37ad4d1d74e65a62892327167ed6b~mv2", "Farmhouse behind a bamboo fence"),
         (S + "thatch-villa-front", "Curved thatch villa with a glazed gable"),
         (S + "thatch-villa-dusk", "Thatch villas in the last of the evening light"),
         (S + "thatch-villa-drive", "Stone drive to a thatch villa"),
         (S + "villa-arrival", "Arrival court and stone path to a thatched villa"),
         (S + "villas-aerial-water", "Villas following the water channel, seen from above"),
         (S + "veranda-vines", "Vine-shaded veranda with a curved balcony"),
         (S + "modern-villa-pergola", "Flat-roofed villa opening onto a timber pergola"),
         (S + "villa-entrance-pergola", "Villa entrance under a bamboo pergola"),
         (S + "courtyard-villas", "Courtyard villas with bamboo pergolas"),
         (S + "pergola-detail", "Bamboo pergola casting patterned shade"),
         (S + "earthen-home", "Earthen home with a living roof among the trees"),
         (S + "earthen-home-terraces", "Earthen home behind tiered planting beds"),
         (S + "earthen-home-arched-door", "Finished earthen home with an arched timber door"),
         (S + "terraced-gardens", "Terraced planting beds curving through the lawn"),
         (S + "interior-terracotta", "Sculpted terracotta interior with built-in seating"),
         (A + "0fba9e5e285949f28357eae29494b6a1~mv2", "Panoramic view of the Agartha estate"),
     ]),
    ("On Site", "Being Built, Right Now",
     "Photographs from the estate — bamboo, earth and thatch going up by hand.", [
         (S + "site-aerial-farm", "The estate from above — farm plots and the first structures"),
         (S + "site-path-progress", "The main path with buildings going up either side"),
         (S + "bamboo-dome-frame", "Bamboo dome frame rising on the site"),
         (S + "dome-frame-wide", "The dome frame standing clear of the treeline"),
         (S + "dome-frame-under", "Looking up into the bamboo gridshell"),
         (S + "dome-thatching", "Layering the woven roof of the bamboo dome"),
         (S + "dome-workers", "Craftsmen finishing the dome roof by hand"),
         (S + "woven-dome-shell", "The woven shell closing over the dome"),
         (S + "bamboo-raising", "Raising a bamboo pole into place"),
         (S + "masons-brickwork", "Masons laying an earth block wall"),
         (S + "mud-brick-handover", "Passing an earth block up to the wall"),
         (S + "thatch-villa-site", "A thatch villa taking shape on the 25-acre site"),
         (S + "thatch-villa-shell", "Thatch and bamboo shell before glazing"),
         (S + "thatch-villa-day", "The finished villa — thatch roof and glass gable"),
         (S + "bamboo-tower", "Two-storey mud and bamboo tower"),
         (S + "bamboo-tower-close", "The tower's wrap-around bamboo balcony"),
         (S + "farm-arches", "Arched farm structures along the track"),
         (S + "farm-shelter", "Livestock shelter at the working farm"),
         (S + "farm-view-from-eave", "The farm seen from under a thatch eave"),
         (S + "entrance-canopy", "Bamboo entrance canopy on the estate road"),
         (S + "interior-mudwall", "Mud wall and clay pot in morning light"),
         (S + "bamboo-ceiling-detail", "Woven bamboo lattice forming a ceiling"),
         (S + "bamboo-roof-detail", "Bamboo battens and thatch on a curved roof"),
         (S + "thatch-eave-detail", "Underside of a thatched eave"),
     ]),
]


def width_of(rel):
    with Image.open(os.path.join(ROOT, rel.replace("/", os.sep))) as im:
        return im.width


def tile(stem, alt):
    base = stem + ".webp"
    small = stem + "-480.webp"
    mid = stem + "-900.webp"
    for p in (base, small):
        assert os.path.exists(os.path.join(ROOT, p.replace("/", os.sep))), p

    if os.path.exists(os.path.join(ROOT, mid.replace("/", os.sep))):
        src, srcset = mid, f"{small} 480w, {mid} 900w"
    else:
        src, srcset = base, f"{small} 480w, {base} {width_of(base)}w"

    return (
        f'        <img class="img-frame reveal" loading="lazy" decoding="async" alt="{alt}"\n'
        f'          src="{src}" srcset="{srcset}"\n'
        f'          sizes="{SIZES}" data-full="{base}" />\n'
    )


def main():
    # Re-emit the marker so this stays re-runnable against its own output.
    out = ["  <!-- Gallery grid -->\n"]
    for i, (eyebrow, title, sub, items) in enumerate(GROUPS):
        pad = ' style="padding-top: 0;"' if i else ""
        out.append(f'  <!-- {title} -->\n  <section{pad}>\n    <div class="container">\n')
        out.append('      <div class="center reveal">\n')
        out.append(f'        <span class="eyebrow">{eyebrow}</span>\n')
        out.append(f'        <h2 class="section-title">{title}</h2>\n')
        out.append(f'        <p class="section-sub">{sub}</p>\n')
        out.append('      </div>\n      <div class="gallery-grid">\n')
        out.extend(tile(stem, alt) for stem, alt in items)
        out.append('      </div>\n    </div>\n  </section>\n\n')

    path = os.path.join(ROOT, "gallery.html")
    html = open(path, encoding="utf-8").read()
    new, hits = re.subn(
        r"  <!-- Gallery grid -->.*?\n  <!-- Offers -->",
        lambda _: "".join(out) + "  <!-- Offers -->",
        html,
        flags=re.S,
    )
    assert hits == 1, "gallery block markers not found in gallery.html"
    open(path, "w", encoding="utf-8", newline="\n").write(new)
    counts = [len(g[3]) for g in GROUPS]
    print(f"gallery.html rewritten: {sum(counts)} images in {len(GROUPS)} sections "
          f"({', '.join(map(str, counts))})")
    # Three columns above 1020px: a group that isn't a multiple of three ends on
    # a part-empty row, which reads as a hole rather than a deliberate stop.
    for (_, title, _, items) in GROUPS:
        if len(items) % 3:
            print(f"  note: '{title}' has {len(items)} images — "
                  f"{3 - len(items) % 3} empty cell(s) in its last row at 3 columns")


if __name__ == "__main__":
    main()
