import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "crm-production" / "assets"
WORK = ROOT / "crm-production" / "render-work"
OUTPUT = ROOT / "video-output"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1280, 720, 30
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def run(args):
    command = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *map(str, args)]
    print("Rendering", Path(args[-1]).name, flush=True)
    subprocess.run(command, check=True)


def still_segment(source, duration, destination):
    run(
        [
            "-loop", "1", "-i", source, "-t", str(duration),
            "-vf", "fps=30,format=yuv420p", "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-movflags", "+faststart", destination,
        ]
    )


def zoom_segment(source, caption, watermark, duration, focus, destination):
    frames = round(duration * FPS)
    fx, fy = focus
    zoom = (
        "zoompan="
        "z='min(zoom+0.00045,1.075)':"
        f"x='min(max({fx}-iw/zoom/2,0),iw-iw/zoom)':"
        f"y='min(max({fy}-ih/zoom/2,0),ih-ih/zoom)':"
        "d=1:s=1280x720:fps=30"
    )
    filters = (
        f"[0:v]{zoom}[base];"
        "[base][1:v]overlay=0:0:format=auto[captioned];"
        "[captioned][2:v]overlay=1048:16:format=auto,format=yuv420p[out]"
    )
    run(
        [
            "-loop", "1", "-i", source,
            "-loop", "1", "-i", caption,
            "-loop", "1", "-i", watermark,
            "-filter_complex", filters,
            "-map", "[out]", "-frames:v", str(frames), "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-movflags", "+faststart", destination,
        ]
    )


def dashboard_segment(duration, destination):
    base = Image.open(ASSETS / "slide-01-dashboard.png").convert("RGBA")
    caption = Image.open(ASSETS / "caption-dashboard.png").convert("RGBA")
    watermark = Image.open(ASSETS / "watermark.png").convert("RGBA")
    font_label = ImageFont.truetype(FONT_REGULAR, 17)
    font_number = ImageFont.truetype(FONT_BOLD, 31)
    font_badge = ImageFont.truetype(FONT_BOLD, 13)
    frames = round(duration * FPS)
    process = subprocess.Popen(
        [
            FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(destination),
        ],
        stdin=subprocess.PIPE,
    )
    finals = (128, 64, 42, 48620)
    labels = ("NEW LEADS", "TRIAL LESSONS", "NEW STUDENTS", "MONTHLY REVENUE")
    colors = ((248, 0, 127), (0, 166, 225), (255, 179, 0), (99, 75, 200))
    for frame_index in range(frames):
        t = frame_index / max(1, frames - 1)
        zoom = 1.0 + 0.045 * t
        zw, zh = round(W * zoom), round(H * zoom)
        scaled = base.resize((zw, zh), Image.Resampling.LANCZOS)
        x0, y0 = (zw - W) // 2, (zh - H) // 2
        frame = scaled.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA")

        shadow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow, "RGBA").rounded_rectangle((53, 421, 1227, 586), radius=28, fill=(5, 20, 40, 135))
        shadow = shadow.filter(ImageFilter.GaussianBlur(13))
        frame.alpha_composite(shadow)
        draw = ImageDraw.Draw(frame, "RGBA")
        draw.rounded_rectangle((56, 414, 1224, 578), radius=26, fill=(250, 252, 255, 248), outline=(220, 226, 234, 255), width=2)
        draw.rounded_rectangle((1085, 79, 1208, 108), radius=14, fill=(13, 39, 70, 230))
        draw.text((1101, 86), "DEMO DATA", font=font_badge, fill=(255, 255, 255, 255))

        tile_w = 270
        for index in range(4):
            tx = 74 + index * 285
            if index:
                draw.line((tx - 15, 443, tx - 15, 552), fill=(218, 224, 232, 255), width=2)
            draw.ellipse((tx, 443, tx + 14, 457), fill=(*colors[index], 255))
            draw.text((tx + 24, 440), labels[index], font=font_label, fill=(76, 91, 110, 255))
            delay = index * 0.08
            progress = min(1.0, max(0.0, (t - delay) / 0.48))
            eased = 1 - (1 - progress) ** 3
            value = round(finals[index] * eased)
            display = f"${value:,}" if index == 3 else f"{value:,}"
            draw.text((tx, 480), display, font=font_number, fill=(13, 39, 70, 255))
            trend = ("+18%", "+12%", "+24%", "+16%")[index]
            draw.text((tx, 530), trend + " this month", font=font_label, fill=(35, 148, 86, 255))

        frame.alpha_composite(caption)
        frame.alpha_composite(watermark, (1048, 16))
        process.stdin.write(frame.convert("RGB").tobytes())
    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("Dashboard animation render failed")
    print("Rendering", destination.name, flush=True)


def montage(segments, durations, music, destination):
    inputs = []
    for segment in segments:
        inputs += ["-i", segment]
    inputs += ["-i", music]
    fade = 0.40
    transitions = ["fade", "smoothleft", "fade", "smoothup", "fade", "smoothleft", "fade", "fade"]
    filters = []
    previous = "0:v"
    elapsed = durations[0]
    for index in range(1, len(segments)):
        offset = elapsed - fade * index
        label = f"v{index}"
        transition = transitions[index - 1]
        filters.append(
            f"[{previous}][{index}:v]xfade=transition={transition}:duration={fade}:offset={offset:.3f}[{label}]"
        )
        previous = label
        elapsed += durations[index]
    final_duration = sum(durations) - fade * (len(durations) - 1)
    audio_index = len(segments)
    filters.append(
        f"[{audio_index}:a]volume=2.00,afade=t=in:st=0:d=1.1,"
        f"afade=t=out:st={final_duration - 2.0:.3f}:d=2.0[audio]"
    )
    run(
        [
            *inputs, "-filter_complex", ";".join(filters),
            "-map", f"[{previous}]", "-map", "[audio]", "-t", f"{final_duration:.3f}",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-c:a", "aac", "-b:a", "160k", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", destination,
        ]
    )
    return final_duration


def vertical_version(source, watermark, duration, destination):
    filters = (
        "[0:v]split=2[fgsrc][bgsrc];"
        "[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "gblur=sigma=38,eq=brightness=-0.11:saturation=1.14[bg];"
        "[fgsrc]scale=1080:608:flags=lanczos[fg];"
        "[bg][fg]overlay=0:656[composed];"
        "[1:v]scale=330:91[wm];"
        "[composed][wm]overlay=375:218:format=auto,format=yuv420p[out]"
    )
    run(
        [
            "-i", source, "-loop", "1", "-i", watermark,
            "-filter_complex", filters,
            "-map", "[out]", "-map", "0:a", "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "slow", "-crf", "19",
            "-c:a", "aac", "-b:a", "160k", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", destination,
        ]
    )


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    watermark = ASSETS / "watermark.png"
    segments = [
        WORK / "01-title.mp4",
        WORK / "02-dashboard.mp4",
        WORK / "03-trainers.mp4",
        WORK / "04-groups.mp4",
        WORK / "05-students.mp4",
        WORK / "06-leads.mp4",
        WORK / "07-reports.mp4",
        WORK / "08-settings.mp4",
        WORK / "09-end.mp4",
    ]
    durations = [2.7, 6.4, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 2.7]
    still_segment(ASSETS / "title.png", durations[0], segments[0])
    dashboard_segment(durations[1], segments[1])
    slides = [
        ("02-trainers", "trainers", (560, 420)),
        ("03-groups", "groups", (690, 505)),
        ("04-students", "students", (690, 500)),
        ("05-leads", "leads", (665, 405)),
        ("06-reports", "reports", (650, 390)),
        ("07-settings", "settings", (650, 320)),
    ]
    for index, (slide, caption, focus) in enumerate(slides, start=2):
        zoom_segment(
            ASSETS / f"slide-{slide}.png",
            ASSETS / f"caption-{caption}.png",
            watermark,
            durations[index],
            focus,
            segments[index],
        )
    still_segment(ASSETS / "end.png", durations[-1], segments[-1])
    wide = OUTPUT / "amakids-crm-overview-16x9.mp4"
    final_duration = montage(segments, durations, ASSETS / "music-original.wav", wide)
    vertical_version(wide, watermark, final_duration, OUTPUT / "amakids-crm-overview-9x16.mp4")
    print(f"Finished CRM videos at {final_duration:.2f} seconds", flush=True)


if __name__ == "__main__":
    main()
