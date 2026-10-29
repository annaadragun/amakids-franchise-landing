import math
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "video-production" / "assets"
LOGO_PATH = Path("/Users/annad./Desktop/Marketing/Symbols - logos/Amakids_logo-01 banner 1.png")
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
W, H = 1280, 720


def font(path, size):
    return ImageFont.truetype(path, size)


def gradient(top, bottom):
    image = Image.new("RGB", (W, H), top)
    pixels = image.load()
    for y in range(H):
        ratio = y / (H - 1)
        color = tuple(round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        for x in range(W):
            pixels[x, y] = color
    return image


def centered(draw, text, y, used_font, fill):
    box = draw.textbbox((0, 0), text, font=used_font)
    draw.text(((W - (box[2] - box[0])) / 2, y), text, font=used_font, fill=fill)


def prepare_logo(max_width):
    logo = Image.open(LOGO_PATH).convert("RGBA")
    bbox = logo.getbbox()
    logo = logo.crop(bbox)
    ratio = max_width / logo.width
    return logo.resize((round(logo.width * ratio), round(logo.height * ratio)), Image.Resampling.LANCZOS)


def title_card():
    image = gradient((240, 248, 255), (231, 224, 255)).convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    for x, y, r, color in (
        (90, 100, 85, (248, 0, 127, 35)),
        (1150, 120, 120, (0, 166, 225, 35)),
        (110, 650, 160, (255, 179, 0, 30)),
        (1180, 650, 180, (248, 0, 127, 28)),
    ):
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
    logo = prepare_logo(620)
    image.alpha_composite(logo, ((W - logo.width) // 2, 115))
    centered(draw, "Learning that feels like play", 355, font(FONT_BOLD, 54), (13, 39, 70, 255))
    centered(draw, "A quick tour of the AMAkids student platform", 435, font(FONT_REGULAR, 28), (58, 80, 110, 255))
    draw.rounded_rectangle((440, 520, 840, 582), radius=31, fill=(248, 0, 127, 235))
    centered(draw, "ENGLISH • SKILLS • MOTIVATION", 535, font(FONT_BOLD, 22), (255, 255, 255, 255))
    image.save(ASSETS / "title-16x9.png")


def end_card():
    image = gradient((255, 239, 247), (237, 246, 255)).convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    logo = prepare_logo(540)
    image.alpha_composite(logo, ((W - logo.width) // 2, 135))
    centered(draw, "Learn. Play. Grow.", 360, font(FONT_BOLD, 62), (13, 39, 70, 255))
    centered(draw, "Skills children want to practise every day", 455, font(FONT_REGULAR, 30), (58, 80, 110, 255))
    draw.rounded_rectangle((490, 535, 790, 599), radius=32, fill=(0, 166, 225, 235))
    centered(draw, "AMAkids", 550, font(FONT_BOLD, 28), (255, 255, 255, 255))
    image.save(ASSETS / "end-16x9.png")


def caption(name, text):
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    text_font = font(FONT_BOLD, 32)
    box = draw.textbbox((0, 0), text, font=text_font)
    text_width = box[2] - box[0]
    pill_width = min(1160, max(620, text_width + 100))
    x0 = (W - pill_width) // 2
    draw.rounded_rectangle((x0, 625, x0 + pill_width, 691), radius=28, fill=(13, 39, 70, 220))
    draw.ellipse((x0 + 20, 643, x0 + 34, 657), fill=(248, 0, 127, 255))
    centered(draw, text, 642, text_font, (255, 255, 255, 255))
    image.save(ASSETS / f"caption-{name}.png")


def watermark():
    logo = prepare_logo(180)
    image = Image.new("RGBA", (220, 60), (255, 255, 255, 225))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((0, 0, 219, 59), radius=20, fill=(255, 255, 255, 225))
    image.alpha_composite(logo, ((220 - logo.width) // 2, (60 - logo.height) // 2))
    image.save(ASSETS / "watermark.png")


def music(duration=60.0, sample_rate=44100):
    samples = int(duration * sample_rate)
    audio = np.zeros(samples, dtype=np.float64)
    rng = np.random.default_rng(20261029)
    chords = [
        (261.63, 329.63, 392.00),
        (196.00, 246.94, 392.00),
        (220.00, 261.63, 329.63),
        (174.61, 220.00, 349.23),
    ]
    bar = 2.0
    for bar_index, start in enumerate(np.arange(0, duration, bar)):
        chord = chords[bar_index % len(chords)]
        bass = chord[0] / 2
        for beat in range(4):
            note_start = start + beat * 0.5
            i0 = int(note_start * sample_rate)
            length = min(int(0.48 * sample_rate), samples - i0)
            if length <= 0:
                continue
            t = np.arange(length) / sample_rate
            env = np.exp(-5.2 * t) * np.minimum(1.0, t / 0.012)
            note = chord[(beat + bar_index) % 3]
            pluck = np.sin(2 * np.pi * note * t) + 0.35 * np.sin(4 * np.pi * note * t)
            audio[i0 : i0 + length] += 0.11 * env * pluck
        i0 = int(start * sample_rate)
        length = min(int(1.65 * sample_rate), samples - i0)
        if length > 0:
            t = np.arange(length) / sample_rate
            env = np.exp(-1.5 * t) * np.minimum(1.0, t / 0.03)
            pad = sum(np.sin(2 * np.pi * note * t) for note in chord) / 3
            audio[i0 : i0 + length] += 0.055 * env * pad
        for beat in (0, 2):
            kick_start = start + beat * 0.5
            i0 = int(kick_start * sample_rate)
            length = min(int(0.13 * sample_rate), samples - i0)
            if length > 0:
                t = np.arange(length) / sample_rate
                kick = np.sin(2 * np.pi * (bass * 1.2 - 35 * t) * t) * np.exp(-22 * t)
                audio[i0 : i0 + length] += 0.09 * kick
        for beat in range(8):
            hat_start = start + beat * 0.25
            i0 = int(hat_start * sample_rate)
            length = min(int(0.035 * sample_rate), samples - i0)
            if length > 0:
                noise = rng.standard_normal(length) * np.exp(-75 * np.arange(length) / sample_rate)
                audio[i0 : i0 + length] += 0.012 * noise
    fade = int(1.5 * sample_rate)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)
    audio /= max(1.0, np.max(np.abs(audio)) / 0.82)
    stereo = np.column_stack((audio, np.roll(audio, 420)))
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
    watermark()
    captions = {
        "login": "One platform. A world of learning.",
        "dashboard": "Everything a learner needs — in one place",
        "learning": "English lessons + an interactive Web Book",
        "homework": "Challenges turn homework into a game",
        "motivation": "XP, streaks, leagues and 233 medals",
        "arena": "Compete in Mental Arithmetic and English",
    }
    for name, text in captions.items():
        caption(name, text)
    music()
    print("Created visual assets and original music")


if __name__ == "__main__":
    main()
