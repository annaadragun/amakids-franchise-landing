import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "crm-production" / "raw" / "sanitized"
ASSETS = ROOT / "crm-production" / "assets"
WORK = ROOT / "crm-production" / "render-work" / "creative"
OUTPUT = ROOT / "video-output"
LEARNING_MUSIC = ROOT / "video-production" / "assets" / "learning-through-games-instrumental.wav"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1280, 720, 30
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(maximum, value))


def ease_out_cubic(value):
    value = clamp(value)
    return 1 - (1 - value) ** 3


def ease_out_back(value):
    value = clamp(value)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (value - 1) ** 3 + c1 * (value - 1) ** 2


def run(args):
    command = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *map(str, args)]
    print("Rendering", Path(args[-1]).name, flush=True)
    subprocess.run(command, check=True)


def source_slide(name):
    image = Image.open(SOURCE / f"{name}.png").convert("RGBA")
    image = image.crop((0, 0, 1440, 810)).resize((W, H), Image.Resampling.LANCZOS)
    if name == "07-settings":
        draw = ImageDraw.Draw(image, "RGBA")
        draw.rounded_rectangle((398, 159, 628, 188), radius=4, fill=(255, 255, 255, 255), outline=(198, 204, 211, 255), width=1)
        draw.text((411, 166), "contact@demo-center.com", font=font(FONT_REGULAR, 13), fill=(110, 118, 128, 255))
    return image


def camera_frame(image, zoom, focus):
    crop_w = W / zoom
    crop_h = H / zoom
    fx, fy = focus
    left = max(0, min(W - crop_w, fx - crop_w / 2))
    top = max(0, min(H - crop_h, fy - crop_h / 2))
    return image.crop((left, top, left + crop_w, top + crop_h)).resize((W, H), Image.Resampling.LANCZOS)


def rounded_crop(image, rect, target_width):
    crop = image.crop(rect)
    ratio = target_width / crop.width
    crop = crop.resize((target_width, round(crop.height * ratio)), Image.Resampling.LANCZOS)
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, crop.width - 1, crop.height - 1), radius=16, fill=255)
    crop.putalpha(mask)
    return crop


def draw_lower_third(frame, kicker, headline, progress):
    progress = ease_out_cubic(progress)
    x = round(-1180 + 1230 * progress)
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rounded_rectangle((x, 604, x + 1180, 699), radius=26, fill=(7, 25, 49, 230))
    draw.rounded_rectangle((x + 22, 619, x + 238, 646), radius=13, fill=(248, 0, 127, 238))
    draw.text((x + 36, 625), kicker, font=font(FONT_BOLD, 14), fill=(255, 255, 255, 255))
    draw.text((x + 28, 658), headline, font=font(FONT_BOLD, 26), fill=(255, 255, 255, 255))
    frame.alpha_composite(overlay)


def draw_popup(frame, base, rect, t, label, position):
    appear = ease_out_back((t - 1.15) / 0.50)
    disappear = 1 - ease_out_cubic((t - 3.65) / 0.55)
    scale = max(0.0, appear * disappear)
    if scale <= 0.01:
        return
    target_width = round(520 * scale)
    popup = rounded_crop(base, rect, max(4, target_width))
    px, py = position
    px += round((520 - popup.width) / 2)
    py += round((180 - popup.height) / 2)

    shadow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow, "RGBA")
    shadow_draw.rounded_rectangle(
        (px - 12, py - 12, px + popup.width + 12, py + popup.height + 12),
        radius=24, fill=(4, 16, 36, round(130 * scale)),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    frame.alpha_composite(shadow)

    card = Image.new("RGBA", (popup.width + 20, popup.height + 20), (255, 255, 255, 246))
    ImageDraw.Draw(card, "RGBA").rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=20, fill=(255, 255, 255, 246))
    card.alpha_composite(popup, (10, 10))
    frame.alpha_composite(card, (px - 10, py - 10))

    draw = ImageDraw.Draw(frame, "RGBA")
    badge_width = max(116, 24 + len(label) * 8)
    draw.rounded_rectangle((px + 10, py - 42, px + 10 + badge_width, py - 14), radius=14, fill=(248, 0, 127, round(245 * scale)))
    draw.text((px + 22, py - 35), label, font=font(FONT_BOLD, 13), fill=(255, 255, 255, round(255 * scale)))

    click_t = (t - 2.25) / 0.55
    if 0 <= click_t <= 1:
        radius = 9 + 34 * click_t
        alpha = round(210 * (1 - click_t))
        cx = px + popup.width * 0.25
        cy = py + popup.height * 0.52
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(248, 0, 127, alpha), width=4)


def write_video_frames(destination, duration, frame_generator):
    frames = round(duration * FPS)
    process = subprocess.Popen(
        [
            FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(destination),
        ], stdin=subprocess.PIPE,
    )
    for index in range(frames):
        t = index / FPS
        frame = frame_generator(t, duration).convert("RGB")
        process.stdin.write(frame.tobytes())
    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"Rendering failed: {destination}")
    print("Rendering", destination.name, flush=True)


def render_title(source, duration, destination, end=False):
    base = Image.open(source).convert("RGBA")
    def make_frame(t, total):
        progress = t / total
        zoom = (1.045 - 0.045 * ease_out_cubic(progress)) if not end else (1.0 + 0.035 * progress)
        frame = camera_frame(base, zoom, (W / 2, H / 2))
        fade = clamp(t / 0.35) * clamp((total - t) / 0.35)
        if fade < 1:
            black = Image.new("RGBA", frame.size, (5, 18, 36, round(255 * (1 - fade))))
            frame.alpha_composite(black)
        return frame
    write_video_frames(destination, duration, make_frame)


def render_dashboard(duration, destination, watermark):
    base = source_slide("01-dashboard")
    finals = (128, 64, 42, 48620)
    labels = ("NEW LEADS", "TRIAL LESSONS", "NEW STUDENTS", "MONTHLY REVENUE")
    colors = ((248, 0, 127), (0, 166, 225), (255, 179, 0), (99, 75, 200))
    def make_frame(t, total):
        frame = camera_frame(base, 1.0 + 0.055 * t / total, (640, 340)).convert("RGBA")
        panel_progress = ease_out_back((t - 0.75) / 0.55)
        if panel_progress > 0:
            panel_y = round(412 + (1 - panel_progress) * 110)
            shadow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            ImageDraw.Draw(shadow, "RGBA").rounded_rectangle((53, panel_y + 8, 1227, panel_y + 164), radius=28, fill=(5, 20, 40, 135))
            shadow = shadow.filter(ImageFilter.GaussianBlur(13))
            frame.alpha_composite(shadow)
            draw = ImageDraw.Draw(frame, "RGBA")
            draw.rounded_rectangle((56, panel_y, 1224, panel_y + 156), radius=26, fill=(250, 252, 255, 248), outline=(220, 226, 234, 255), width=2)
            draw.rounded_rectangle((1080, 76, 1208, 106), radius=14, fill=(13, 39, 70, 235))
            draw.text((1097, 84), "DEMO DATA", font=font(FONT_BOLD, 13), fill=(255, 255, 255, 255))
            for idx in range(4):
                tx = 74 + idx * 285
                if idx:
                    draw.line((tx - 15, panel_y + 27, tx - 15, panel_y + 132), fill=(218, 224, 232, 255), width=2)
                draw.ellipse((tx, panel_y + 27, tx + 14, panel_y + 41), fill=(*colors[idx], 255))
                draw.text((tx + 24, panel_y + 23), labels[idx], font=font(FONT_REGULAR, 17), fill=(76, 91, 110, 255))
                count_progress = ease_out_cubic((t - 1.0 - idx * 0.10) / 1.55)
                value = round(finals[idx] * count_progress)
                shown = f"${value:,}" if idx == 3 else f"{value:,}"
                draw.text((tx, panel_y + 62), shown, font=font(FONT_BOLD, 31), fill=(13, 39, 70, 255))
                draw.text((tx, panel_y + 111), ("+18%", "+12%", "+24%", "+16%")[idx] + " this month", font=font(FONT_REGULAR, 16), fill=(35, 148, 86, 255))
        draw_lower_third(frame, "ONE COMMAND CENTRE", "See the whole business move — in real time", (t - 0.20) / 0.55)
        frame.alpha_composite(watermark, (1048, 16))
        return frame
    write_video_frames(destination, duration, make_frame)


def render_feature_scene(config, duration, destination, watermark):
    base = source_slide(config["source"])
    def make_frame(t, total):
        zoom = 1.015 + 0.07 * ease_out_cubic(t / total)
        frame = camera_frame(base, zoom, config["focus"]).convert("RGBA")
        draw_lower_third(frame, config["kicker"], config["headline"], (t - 0.18) / 0.52)
        draw_popup(frame, base, config["popup"], t, config["popup_label"], config["popup_position"])
        frame.alpha_composite(watermark, (1048, 16))
        return frame
    write_video_frames(destination, duration, make_frame)


def montage(segments, durations, music, destination):
    inputs = []
    for segment in segments:
        inputs += ["-i", segment]
    inputs += ["-i", music]
    fade = 0.25
    transitions = [
        "fade", "smoothleft", "smoothup", "smoothleft", "wipeleft",
        "smoothup", "smoothleft", "wipeleft", "fade",
    ]
    filters = []
    previous = "0:v"
    elapsed = durations[0]
    for idx in range(1, len(segments)):
        offset = elapsed - fade * idx
        label = f"v{idx}"
        filters.append(
            f"[{previous}][{idx}:v]xfade=transition={transitions[idx - 1]}:duration={fade}:offset={offset:.3f}[{label}]"
        )
        previous = label
        elapsed += durations[idx]
    final_duration = sum(durations) - fade * (len(durations) - 1)
    music_index = len(segments)
    filters.append(
        f"[{music_index}:a]volume=0.92,afade=t=in:st=0:d=0.8,"
        f"afade=t=out:st={final_duration - 1.6:.3f}:d=1.6[audio]"
    )
    run(
        [
            *inputs, "-filter_complex", ";".join(filters),
            "-map", f"[{previous}]", "-map", "[audio]", "-t", f"{final_duration:.3f}",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-c:a", "aac", "-b:a", "176k", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", destination,
        ]
    )
    return final_duration


def vertical_version(source, watermark, duration, destination):
    filters = (
        "[0:v]split=2[fgsrc][bgsrc];"
        "[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "gblur=sigma=38,eq=brightness=-0.11:saturation=1.18[bg];"
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
            "-c:a", "aac", "-b:a", "176k", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", destination,
        ]
    )


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    watermark = Image.open(ASSETS / "watermark.png").convert("RGBA")
    segment_paths = [
        WORK / "01-title.mp4",
        WORK / "02-dashboard.mp4",
        WORK / "03-trainers.mp4",
        WORK / "04-groups.mp4",
        WORK / "05-students.mp4",
        WORK / "06-leads.mp4",
        WORK / "07-settings.mp4",
        WORK / "08-group-schedule.mp4",
        WORK / "09-settings-packages.mp4",
        WORK / "10-end.mp4",
    ]
    durations = [2.0, 4.8, 4.2, 4.2, 4.2, 4.2, 4.3, 4.4, 4.5, 2.2]
    render_title(ASSETS / "title.png", durations[0], segment_paths[0])
    render_dashboard(durations[1], segment_paths[1], watermark)
    scenes = [
        {
            "source": "02-trainers", "index": 2, "focus": (650, 400),
            "kicker": "TEACHER SUCCESS", "headline": "Lead stronger teams with performance at your fingertips",
            "popup": (120, 120, 510, 198), "popup_label": "QUICK ACTIONS", "popup_position": (350, 130),
        },
        {
            "source": "03-groups", "index": 3, "focus": (710, 465),
            "kicker": "SMART SCHEDULING", "headline": "Create groups. Set schedules. Stay flexible.",
            "popup": (925, 112, 1150, 185), "popup_label": "CREATE & EXPORT", "popup_position": (600, 125),
        },
        {
            "source": "04-students", "index": 4, "focus": (690, 455),
            "kicker": "LEARNER JOURNEYS", "headline": "Every learner story, organised in one place",
            "popup": (128, 112, 455, 188), "popup_label": "STUDENT TOOLS", "popup_position": (365, 130),
        },
        {
            "source": "05-leads", "index": 5, "focus": (660, 390),
            "kicker": "GROWTH PIPELINE", "headline": "Move from first enquiry to first lesson — faster",
            "popup": (125, 108, 585, 194), "popup_label": "LEAD WORKFLOW", "popup_position": (340, 125),
        },
        {
            "source": "07-settings", "index": 6, "focus": (640, 315),
            "kicker": "BUILT FOR YOUR MODEL", "headline": "Adapt KPIs and payment rules to your business",
            "popup": (355, 280, 720, 475), "popup_label": "FLEXIBLE RULES", "popup_position": (690, 110),
        },
        {
            "source": "08-group-schedule", "index": 7, "focus": (710, 390),
            "kicker": "EVERY CLASS IN SYNC", "headline": "Plan lessons and keep every group on schedule",
            "popup": (128, 315, 1055, 515), "popup_label": "LIVE SCHEDULE", "popup_position": (365, 135),
        },
        {
            "source": "09-settings-packages", "index": 8, "focus": (720, 390),
            "kicker": "OFFERS THAT CONVERT", "headline": "Build flexible packages and reward longer commitments",
            "popup": (145, 105, 1275, 590), "popup_label": "PACKAGES & DISCOUNTS", "popup_position": (375, 90),
        },
    ]
    for idx, config in enumerate(scenes, start=2):
        render_feature_scene(config, durations[idx], segment_paths[idx], watermark)
    render_title(ASSETS / "end.png", durations[-1], segment_paths[-1], end=True)

    wide = OUTPUT / "amakids-crm-overview-creative-16x9.mp4"
    final_duration = montage(segment_paths, durations, LEARNING_MUSIC, wide)
    vertical_version(
        wide, ASSETS / "watermark.png", final_duration,
        OUTPUT / "amakids-crm-overview-creative-9x16.mp4",
    )
    print(f"Finished creative CRM videos at {final_duration:.2f} seconds", flush=True)


if __name__ == "__main__":
    main()
