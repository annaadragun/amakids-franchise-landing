#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
FFMPEG="$ROOT/.video-edit-venv/lib/python3.9/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1"
SOURCE="/Users/annad./Desktop/Диана.Двухзначные. Режим Double power..mp4"
LOGO="$ROOT/video-production/assets/watermark.png"
OUTPUT="$ROOT/video-output/diana-double-power-amakids.mp4"

mkdir -p "$ROOT/video-output"

"$FFMPEG" -y -i "$SOURCE" -loop 1 -i "$LOGO" -filter_complex "
  [0:v]trim=start=28.7:end=43.15,setpts=PTS-STARTPTS,fps=25[v1];
  [0:v]trim=start=48.75:end=52.75,setpts=PTS-STARTPTS,fps=25[v2];
  [v1][v2]xfade=transition=fade:duration=0.30:offset=14.15,
    hqdn3d=1.2:1.0:2.2:1.8,
    eq=contrast=1.035:saturation=1.055:brightness=0.006,
    unsharp=5:5:0.48:3:3:0.18,
    crop=1048:590:160:130,
    scale=1920:1080:flags=lanczos[clean];
  [1:v]scale=352:96:flags=lanczos,colorkey=0xFFFFFF:0.22:0.10[logo];
  [clean][logo]overlay=x=28:y=18:shortest=1[vout];
  [0:a]atrim=start=28.7:end=43.15,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.15[a1];
  [0:a]atrim=start=48.75:end=52.75,asetpts=PTS-STARTPTS,afade=t=out:st=3.78:d=0.20[a2];
  [a1][a2]acrossfade=d=0.30:c1=tri:c2=tri,highpass=f=75,lowpass=f=15000,loudnorm=I=-16:TP=-1.5:LRA=9[aout]
" -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset slow -crf 16 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart -metadata title="AMAkids — Double Power" \
  "$OUTPUT"

echo "$OUTPUT"
