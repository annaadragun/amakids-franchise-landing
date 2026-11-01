#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
FFMPEG="$ROOT/.video-edit-venv/lib/python3.9/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1"
SOURCE="/Users/annad./Desktop/Learning Through Games – The AMAkids Way! 🎮🧠.mp4"
OUTPUT="$ROOT/video-output/learning-through-games-no-footer.mp4"

mkdir -p "$ROOT/video-output"

"$FFMPEG" -y -i "$SOURCE" \
  -vf "crop=1636:920:142:0,scale=1920:1080:flags=lanczos,setsar=1" \
  -map 0:v:0 -map 0:a:0 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -level 4.2 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -ar 48000 -movflags +faststart \
  -metadata title="Learning Through Games — AMAkids" \
  "$OUTPUT"

echo "$OUTPUT"
