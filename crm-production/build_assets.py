import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "crm-production" / "raw" / "sanitized"
ASSETS = ROOT / "crm-production" / "assets"
LOGO_PATH = Path("/Users/annad./Desktop/Marketing/Symbols - logos/Amakids_logo-01 banner 1.png")
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
W, H = 1280, 720


def font(path, size):
    return ImageFont.truetype(path, size)


def prepare_logo(max_width):
    logo = Image.open(LOGO_PATH).convert("RGBA").crop(Image.open(LOGO_PATH).convert("RGBA").getbbox())
    ratio = max_width / logo.width
    return logo.resize((round(logo.width * ratio), round(logo.height * ratio)), Image.Resampling.LANCZOS)


def gradient(top, bottom):
    image = Image.new("RGB", (W, H), top)
    canvas = np.asarray(image).copy()
    for y in range(H):
        mix = y / max(1, H - 1)
        canvas[y, :, :] = [round(top[i] * (1 - mix) + bottom[i] * mix) for i in range(3)]
    return Image.fromarray(canvas).convert("RGBA")


def centered(draw, text, y, used_font, fill):
    box = draw.textbbox((0, 0), text, font=used_font)
    draw.text(((W - box[2] + box[0]) / 2, y), text, font=used_font, fill=fill)


def title_card():
    image = gradient((10, 28, 55), (28, 69, 112))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((-120, -150, 420, 390), fill=(248, 0, 127, 45))
    draw.ellipse((930, 390, 1430, 890), fill=(0, 166, 225, 45))
    draw.line((90, 590, 1190, 590), fill=(255, 255, 255, 35), width=2)
    logo = prepare_logo(500)
    white_pill = Image.new("RGBA", (600, 150), (255, 255, 255, 245))
    ImageDraw.Draw(white_pill).rounded_rectangle((0, 0, 599, 149), radius=46, fill=(255, 255, 255, 245))
    white_pill.alpha_composite(logo, ((600 - logo.width) // 2, (150 - logo.height) // 2))
    image.alpha_composite(white_pill, ((W - 600) // 2, 92))
    centered(draw, "Run your education business with clarity", 315, font(FONT_BOLD, 48), (255, 255, 255, 255))
    centered(draw, "A quick look at the AMAkids franchise CRM", 392, font(FONT_REGULAR, 29), (207, 225, 242, 255))
    draw.rounded_rectangle((438, 500, 842, 566), radius=33, fill=(248, 0, 127, 245))
    centered(draw, "CONTROL • INSIGHT • GROWTH", 519, font(FONT_BOLD, 21), (255, 255, 255, 255))
    image.save(ASSETS / "title.png")


def end_card():
    image = gradient((242, 248, 255), (239, 229, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((-120, 430, 300, 850), fill=(255, 179, 0, 45))
    draw.ellipse((1010, -120, 1410, 280), fill=(248, 0, 127, 38))
    logo = prepare_logo(510)
    image.alpha_composite(logo, ((W - logo.width) // 2, 120))
    centered(draw, "Less admin. More growth.", 345, font(FONT_BOLD, 58), (13, 39, 70, 255))
    centered(draw, "One CRM for every part of your franchise", 438, font(FONT_REGULAR, 30), (58, 80, 110, 255))
    draw.rounded_rectangle((480, 535, 800, 603), radius=34, fill=(0, 166, 225, 240))
    centered(draw, "AMAkids CRM", 552, font(FONT_BOLD, 27), (255, 255, 255, 255))
    image.save(ASSETS / "end.png")


def base_slide(source_name):
    image = Image.open(SOURCE / f"{source_name}.png").convert("RGBA")
    image = image.crop((0, 0, 1440, 810)).resize((W, H), Image.Resampling.LANCZOS)
    return image


def highlight(image, boxes):
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")
    for box in boxes:
        glow_draw.rounded_rectangle(box, radius=18, outline=(248, 0, 127, 180), width=12)
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    image.alpha_composite(glow)
    draw = ImageDraw.Draw(image, "RGBA")
    for box in boxes:
        draw.rounded_rectangle(box, radius=18, outline=(248, 0, 127, 245), width=4)


def sanitize_settings_email(image):
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((398, 159, 628, 188), radius=4, fill=(255, 255, 255, 255), outline=(198, 204, 211, 255), width=1)
    draw.text((411, 166), "contact@demo-center.com", font=font(FONT_REGULAR, 13), fill=(110, 118, 128, 255))


def build_slides():
    configs = {
        "01-dashboard": [(125, 104, 1155, 574)],
        "02-trainers": [(122, 218, 1160, 705)],
        "03-groups": [(132, 473, 1149, 708), (943, 117, 1138, 164)],
        "04-students": [(132, 403, 1150, 708), (139, 118, 423, 165)],
        "05-leads": [(132, 118, 553, 170), (133, 206, 1153, 704)],
        "06-reports": [(278, 120, 1000, 678)],
        "07-settings": [(130, 208, 1150, 472)],
    }
    for name, boxes in configs.items():
        image = base_slide(name)
        if name == "07-settings":
            sanitize_settings_email(image)
        highlight(image, boxes)
        image.save(ASSETS / f"slide-{name}.png")


def caption(name, kicker, headline):
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((54, 595, 1226, 696), radius=28, fill=(9, 28, 52, 228))
    draw.rounded_rectangle((76, 612, 260, 641), radius=14, fill=(248, 0, 127, 235))
    kicker_font = font(FONT_BOLD, 15)
    headline_font = font(FONT_BOLD, 29)
    kicker_box = draw.textbbox((0, 0), kicker, font=kicker_font)
    draw.text((168 - (kicker_box[2] - kicker_box[0]) / 2, 619), kicker, font=kicker_font, fill=(255, 255, 255, 255))
    draw.text((82, 652), headline, font=headline_font, fill=(255, 255, 255, 255))
    image.save(ASSETS / f"caption-{name}.png")


def captions():
    content = {
        "dashboard": ("ONE CLEAR VIEW", "Your entire franchise — visible at a glance"),
        "trainers": ("TEACHER SUCCESS", "Empower every teacher. Track what drives performance."),
        "groups": ("SMART SCHEDULING", "Build groups, courses and timetables in seconds"),
        "students": ("LEARNER JOURNEYS", "Every student record — organised and actionable"),
        "leads": ("GROWTH PIPELINE", "Turn enquiries into enrolments with a smarter workflow"),
        "reports": ("BUSINESS INTELLIGENCE", "Decisions backed by data — ready when you are"),
        "settings": ("BUILT FOR YOUR MODEL", "Your KPIs, payment rules and operating standards"),
    }
    for name, (kicker, headline) in content.items():
        caption(name, kicker, headline)


def watermark():
    logo = prepare_logo(170)
    image = Image.new("RGBA", (210, 58), (255, 255, 255, 225))
    ImageDraw.Draw(image).rounded_rectangle((0, 0, 209, 57), radius=18, fill=(255, 255, 255, 225))
    image.alpha_composite(logo, ((210 - logo.width) // 2, (58 - logo.height) // 2))
    image.save(ASSETS / "watermark.png")


def music(duration=52.0, sample_rate=44100):
    samples = int(duration * sample_rate)
    audio = np.zeros(samples, dtype=np.float64)
    rng = np.random.default_rng(30102026)
    chords = [
        (220.00, 277.18, 329.63),
        (174.61, 220.00, 261.63),
        (196.00, 246.94, 293.66),
        (164.81, 207.65, 261.63),
    ]
    bar = 2.14
    for bar_index, start in enumerate(np.arange(0, duration, bar)):
        chord = chords[bar_index % len(chords)]
        for beat in range(6):
            note_start = start + beat * (bar / 6)
            i0 = int(note_start * sample_rate)
            length = min(int(0.42 * sample_rate), samples - i0)
            if length <= 0:
                continue
            t = np.arange(length) / sample_rate
            env = np.exp(-5.7 * t) * np.minimum(1.0, t / 0.012)
            note = chord[(beat + bar_index) % 3] * (2 if beat in (1, 4) else 1)
            tone = np.sin(2 * np.pi * note * t) + 0.28 * np.sin(4 * np.pi * note * t)
            audio[i0 : i0 + length] += 0.095 * env * tone
        i0 = int(start * sample_rate)
        length = min(int(1.9 * sample_rate), samples - i0)
        if length > 0:
            t = np.arange(length) / sample_rate
            env = np.exp(-1.1 * t) * np.minimum(1.0, t / 0.05)
            pad = sum(np.sin(2 * np.pi * n * t) for n in chord) / 3
            audio[i0 : i0 + length] += 0.05 * env * pad
        for beat in range(8):
            i0 = int((start + beat * bar / 8) * sample_rate)
            length = min(int(0.035 * sample_rate), samples - i0)
            if length > 0:
                noise = rng.standard_normal(length) * np.exp(-80 * np.arange(length) / sample_rate)
                audio[i0 : i0 + length] += 0.011 * noise
        for beat in (0, 4):
            i0 = int((start + beat * bar / 8) * sample_rate)
            length = min(int(0.15 * sample_rate), samples - i0)
            if length > 0:
                t = np.arange(length) / sample_rate
                kick = np.sin(2 * np.pi * (82 - 28 * t) * t) * np.exp(-20 * t)
                audio[i0 : i0 + length] += 0.08 * kick
    fade = int(1.4 * sample_rate)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)
    audio /= max(1.0, np.max(np.abs(audio)) / 0.82)
    stereo = np.column_stack((audio, np.roll(audio, 360)))
    pcm = (stereo * 32767).astype("<i2")
    with wave.open(str(ASSETS / "music-original.wav"), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(pcm.tobytes())


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    title_card()
    end_card()
    build_slides()
    captions()
    watermark()
    music()
    print("CRM visual assets and original music created")


if __name__ == "__main__":
    main()
