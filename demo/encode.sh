#!/usr/bin/env bash
# Encode demo-raw.mov into the GIF + MP4 the README and social posts reference.
# See demo/script.md for the recording shot list.

set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
raw="${here}/demo-raw.mov"
gif="${here}/demo.gif"
mp4="${here}/demo.mp4"
palette="${here}/palette.png"

if [[ ! -f "$raw" ]]; then
    echo "Missing $raw — record the demo first (see demo/script.md)" >&2
    exit 1
fi

echo "→ Generating GIF palette"
ffmpeg -y -i "$raw" \
    -vf "fps=15,scale=900:-1:flags=lanczos,palettegen=stats_mode=diff" \
    "$palette"

echo "→ Encoding GIF (target ~5 MB)"
ffmpeg -y -i "$raw" -i "$palette" \
    -lavfi "fps=15,scale=900:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
    "$gif"

echo "→ Encoding MP4 (1080p, CRF 22)"
ffmpeg -y -i "$raw" \
    -vf "scale='min(1920,iw)':-2:flags=lanczos,fps=30" \
    -c:v libx264 -preset slow -crf 22 \
    -movflags +faststart \
    -an \
    "$mp4"

echo "→ Done"
echo "  GIF: $(ls -lh "$gif" | awk '{print $5}') — $gif"
echo "  MP4: $(ls -lh "$mp4" | awk '{print $5}') — $mp4"
echo
echo "If the GIF is over 5 MB, edit demo/script.md guidance to drop fps to 12 or scale to 800."
