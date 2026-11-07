#!/usr/bin/env bash
# Render every project, then write the compressed MP4 and a poster into videos/.
# Usage: ./render_all.sh [slug ...]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/.."
mkdir -p "$OUT/posters"
slugs=("$@")
[ ${#slugs[@]} -eq 0 ] && slugs=($(ls "$HERE/projects"))
for slug in "${slugs[@]}"; do
  p="$HERE/projects/$slug"
  echo "== $slug"
  (cd "$p" && npx --yes hyperframes@0.8.114 render --quality high --output renders/video.mp4 > render.log 2>&1)
  ffmpeg -y -loglevel error -i "$p/renders/video.mp4" -c:v libx264 -preset slow -crf 24 -tune animation \
    -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "$OUT/$slug.mp4"
  t=$(python3 -c "import json;s=json.load(open('$p/timeline.json'))['scenes'][1];print(round(s['start']+s['dur']-0.6,2))")
  ffmpeg -y -loglevel error -ss "$t" -i "$OUT/$slug.mp4" -frames:v 1 -vf scale=960:-2 -q:v 3 "$OUT/posters/${slug:0:2}.jpg"
  ls -la "$OUT/$slug.mp4"
done
