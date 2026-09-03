#!/usr/bin/env python3
"""Turn a camera original into the two files the hero video needs.

The Drive clips are 93MB and 226MB QuickTime camera files. Those must never
reach the web: they would blow the deploy budget and punish every mobile
visitor. What the hero wants is a few seconds of texture behind a headline —
silent, short, and small enough that nobody notices it arriving.

    python3 scripts/build-hero-video.py path/to/H08A5473.MOV
    python3 scripts/build-hero-video.py clip.MOV --start 00:00:12 --duration 8

Writes assets/video/estate-hero.mp4 and .webm. ffmpeg comes from the
imageio-ffmpeg wheel if it is not already on PATH:

    pip install imageio-ffmpeg
"""
import argparse
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "video"

# A hero loop is texture, not content. Past ~4MB it stops being free and starts
# being a tax on the visitor, so the encoder settings aim under that and the
# script says so loudly when they miss.
BUDGET_MB = 4.0
WIDTH = 1920

# Quality presets. The default is tuned for a background loop, where the scrim
# and the motion hide a lot. --hq keeps the native resolution and spends the
# bytes; use it when the footage is the point rather than the texture.
PRESETS = {
    "web":  {"width": 1920, "crf": 28, "vp9": 36, "budget": 4.0},
    "hq":   {"width": None, "crf": 20, "vp9": 28, "budget": 12.0},
}


def ffmpeg_bin() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("ffmpeg not found. pip install imageio-ffmpeg")


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{p.stderr[-1500:]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="camera original (.MOV/.mp4)")
    ap.add_argument("--start", default="00:00:00", help="in-point, e.g. 00:00:12")
    ap.add_argument("--duration", type=float, default=8.0, help="seconds to keep")
    ap.add_argument("--preset", choices=sorted(PRESETS), default="web",
                    help="web: 1920px, tuned for a background loop. "
                         "hq: native resolution, visually lossless, bigger files")
    ap.add_argument("--crf", type=int, help="H.264 quality; higher is smaller. Overrides the preset")
    ap.add_argument("--vp9-crf", type=int, help="VP9 quality; higher is smaller. Overrides the preset")
    a = ap.parse_args()

    pre = PRESETS[a.preset]
    crf = a.crf if a.crf is not None else pre["crf"]
    vp9 = a.vp9_crf if a.vp9_crf is not None else pre["vp9"]
    width, budget = pre["width"], pre["budget"]

    src = pathlib.Path(a.source)
    if not src.is_file():
        sys.exit(f"not found: {src}")
    ff = ffmpeg_bin()
    OUT.mkdir(parents=True, exist_ok=True)

    # -an drops the audio track outright. The markup is muted as well, and both
    # matter for different reasons: muted is what permits autoplay, -an is what
    # stops shipping bytes nobody will ever hear.
    # width None means keep the source resolution untouched — only the audio
    # and the duration are dropped.
    vf = "fps=25" if width is None else f"scale={width}:-2,fps=25"
    common = ["-ss", a.start, "-t", str(a.duration), "-i", str(src), "-an", "-vf", vf]

    mp4 = OUT / "estate-hero.mp4"
    webm = OUT / "estate-hero.webm"

    print(f"source: {src.name}  ({src.stat().st_size / 1e6:.0f}MB)")
    size = "native resolution" if width is None else f"{width}px wide"
    print(f"  preset {a.preset}: taking {a.duration:g}s from {a.start}, silent, {size}\n")

    run([ff, "-y", *common, "-c:v", "libx264", "-profile:v", "high",
         "-crf", str(crf), "-preset", "slow", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(mp4)])
    run([ff, "-y", *common, "-c:v", "libvpx-vp9", "-crf", str(vp9),
         "-b:v", "0", "-row-mt", "1", "-pix_fmt", "yuv420p", str(webm)])

    over = False
    for f in (webm, mp4):
        mb = f.stat().st_size / 1e6
        flag = "" if mb <= budget else f"  OVER BUDGET (>{budget}MB)"
        over |= mb > budget
        print(f"  {f.relative_to(ROOT)}  {mb:.2f}MB{flag}")

    if over:
        print("\nRaise --crf / --vp9-crf or shorten --duration rather than dropping "
              "resolution: a soft hero reads as a mistake, a shorter loop does not.",
              file=sys.stderr)
        return 1
    print("\nBoth under budget. Commit them and the hero picks them up.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
