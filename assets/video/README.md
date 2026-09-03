# Hero video

`index.html` layers a muted, looping video over the photo hero. Drop two files
here and it appears; leave them out and the hero renders exactly as it does now.

    estate-hero.webm    ← preferred, served first
    estate-hero.mp4     ← fallback for Safari and older browsers

## Making them

One command, from the camera original:

```bash
pip install imageio-ffmpeg          # only if ffmpeg is not already installed
python3 scripts/build-hero-video.py H08A5473.MOV --start 00:00:12 --duration 8
```

It strips the audio, scales to 1920, encodes both formats, and fails loudly if
either lands over the 4MB budget rather than letting a heavy file through. The
pipeline has been run end to end against a synthetic source: both outputs came
back with zero audio streams, and the page played the WebM muted and looping
behind the headline.

## Doing it by hand

The source clips (`H08A5473.MOV` 226MB, `H08A7965.MOV` 93MB) are camera
originals. Never put those on the web — transcode first. Target 6–10 seconds,
no audio, under ~4MB; this plays behind a headline, it is texture, not content.

```bash
# pick the best 8 seconds, drop the audio, scale to 1920 wide
ffmpeg -ss 00:00:12 -t 8 -i H08A5473.MOV \
  -an -vf "scale=1920:-2,fps=25" \
  -c:v libx264 -profile:v high -crf 28 -preset slow -movflags +faststart \
  estate-hero.mp4

ffmpeg -ss 00:00:12 -t 8 -i H08A5473.MOV \
  -an -vf "scale=1920:-2,fps=25" \
  -c:v libvpx-vp9 -crf 36 -b:v 0 -row-mt 1 \
  estate-hero.webm
```

`-an` is what strips the audio track. The markup is also `muted`, which is what
allows a browser to autoplay at all — both matter, for different reasons.

Check the result is under 4MB before committing. If it is not, raise `-crf`
(28 → 32) or shorten the clip rather than reducing resolution.

## What the page does with it

`js/main.js` only fetches the video when the visitor's settings welcome it:
`preload="none"` in the markup means nothing downloads until the script decides,
and it does not decide when `prefers-reduced-motion` is set, when Save-Data is
on, or on a 2G connection. On a metered mobile connection an unrequested hero
video is the most expensive mistake this page could make.

The video only becomes visible on `canplay`, so a half-buffered pop-in never
shows. Any failure leaves the photo hero in place.
