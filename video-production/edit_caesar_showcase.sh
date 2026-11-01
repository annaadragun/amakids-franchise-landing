#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
FFMPEG="$ROOT/.video-edit-venv/lib/python3.9/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1"
SOURCE="/Users/annad./Desktop/СМАРТУМ ЦЕЗАРЬ КИЕВ 2019.mp4"
LOGO="$ROOT/video-production/assets/watermark.png"
MUSIC="$ROOT/video-production/assets/learning-through-games-instrumental.wav"
FONT="$ROOT/amakids-local/amakids.com/fonts/ClearSans-Bold.ttf"
OUTPUT="$ROOT/video-output/caesar-mental-arithmetic-amakids.mp4"

mkdir -p "$ROOT/video-output"

"$FFMPEG" -y -i "$SOURCE" -i "$MUSIC" -loop 1 -i "$LOGO" -filter_complex "
  [0:v]trim=start=30.0:end=32.8,setpts=PTS-STARTPTS,fps=25[v0];
  [0:v]trim=start=19.2:end=20.5,setpts=PTS-STARTPTS,fps=25[v1];
  [0:v]trim=start=22.2:end=23.5,setpts=PTS-STARTPTS,fps=25[v2];
  [0:v]trim=start=27.1:end=28.6,setpts=PTS-STARTPTS,fps=25[v3];
  [0:v]trim=start=32.2:end=34.6,setpts=PTS-STARTPTS,fps=25[v4];
  [0:v]trim=start=37.3:end=43.2,setpts=PTS-STARTPTS,fps=25[v5];
  [0:v]trim=start=48.2:end=51.0,setpts=PTS-STARTPTS,fps=25[v6];
  [0:v]trim=start=65.0:end=68.2,setpts=PTS-STARTPTS,fps=25[v7];

  [v0][v1]xfade=transition=fade:duration=0.25:offset=2.55[x1];
  [x1][v2]xfade=transition=fade:duration=0.25:offset=3.60[x2];
  [x2][v3]xfade=transition=fade:duration=0.25:offset=4.65[x3];
  [x3][v4]xfade=transition=fade:duration=0.25:offset=5.90[x4];
  [x4][v5]xfade=transition=fade:duration=0.25:offset=8.05[x5];
  [x5][v6]xfade=transition=fade:duration=0.25:offset=13.70[x6];
  [x6][v7]xfade=transition=fade:duration=0.25:offset=16.25,
    crop=1184:666:48:20,
    deblock=filter=weak:block=8:alpha=0.055:beta=0.04:gamma=0.03:delta=0.03,
    hqdn3d=0.70:0.55:1.20:1.00,
    eq=contrast=1.045:saturation=1.085:brightness=0.006:gamma=0.99,
    scale=1920:1080:flags=lanczos,
    setsar=1,
    cas=strength=0.30,
    drawbox=x=(iw-1140)/2:y=ih-176:w=1140:h=92:color=0x0D2746@0.88:t=fill:enable='between(t,0.25,4.15)',
    drawbox=x=(iw-1140)/2:y=ih-176:w=12:h=92:color=0xF8007F@0.98:t=fill:enable='between(t,0.25,4.15)',
    drawtext=fontfile='$FONT':text='MENTAL MATH — EVEN IN MOTION':fontcolor=white:fontsize=47:x=(w-text_w)/2:y=h-153:enable='between(t,0.25,4.15)',
    drawbox=x=(iw-1050)/2:y=ih-168:w=1050:h=84:color=0x0D2746@0.86:t=fill:enable='between(t,4.35,8.10)',
    drawbox=x=(iw-1050)/2:y=ih-168:w=12:h=84:color=0x00A6E1@0.98:t=fill:enable='between(t,4.35,8.10)',
    drawtext=fontfile='$FONT':text='FOCUS  •  SPEED  •  COORDINATION':fontcolor=white:fontsize=39:x=(w-text_w)/2:y=h-147:enable='between(t,4.35,8.10)'[base];

  [2:v]scale=300:82:flags=lanczos,colorkey=0xFFFFFF:0.22:0.10[logo];
  [base][logo]overlay=x=42:y=34:shortest=1[vout];

  [1:a]atrim=start=17.0:end=36.45,asetpts=PTS-STARTPTS,
    afade=t=in:st=0:d=0.28,afade=t=out:st=18.45:d=0.95,
    highpass=f=35,lowpass=f=18000,
    loudnorm=I=-16:TP=-1.2:LRA=7[aout]
" -map "[vout]" -map "[aout]" -t 19.45 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart \
  -metadata title="AMAkids — Mental Math in Motion" \
  "$OUTPUT"

echo "$OUTPUT"
