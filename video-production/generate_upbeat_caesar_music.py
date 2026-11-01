#!/usr/bin/env python3
import wave
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "video-production" / "assets" / "music-upbeat-caesar.wav"
SAMPLE_RATE = 48_000
DURATION = 20.0
BPM = 128
BEAT = 60.0 / BPM


def add_tone(track, start, duration, frequency, volume, decay=5.0, harmonics=(1.0,)):
    first = int(start * SAMPLE_RATE)
    length = min(int(duration * SAMPLE_RATE), len(track) - first)
    if first < 0 or length <= 0:
        return
    t = np.arange(length) / SAMPLE_RATE
    attack = np.minimum(1.0, t / 0.008)
    release = np.minimum(1.0, (duration - t) / 0.06)
    envelope = attack * np.maximum(0.0, release) * np.exp(-decay * t)
    tone = np.zeros(length)
    for harmonic, weight in enumerate(harmonics, start=1):
        tone += weight * np.sin(2 * np.pi * frequency * harmonic * t)
    track[first : first + length] += volume * envelope * tone


def main():
    samples = int(DURATION * SAMPLE_RATE)
    left = np.zeros(samples, dtype=np.float64)
    right = np.zeros(samples, dtype=np.float64)
    rng = np.random.default_rng(20261030)

    # C major, G major, A minor, F major: bright and energetic.
    progressions = [
        (130.81, (261.63, 329.63, 392.00)),
        (98.00, (196.00, 246.94, 392.00)),
        (110.00, (220.00, 261.63, 329.63)),
        (87.31, (174.61, 220.00, 349.23)),
    ]
    melody_steps = (0, 1, 2, 1, 2, 1, 0, 2)

    total_beats = int(np.ceil(DURATION / BEAT))
    for beat_index in range(total_beats):
        start = beat_index * BEAT
        root, chord = progressions[(beat_index // 4) % len(progressions)]

        # Punchy bass on every beat.
        add_tone(left, start, 0.34, root, 0.10, decay=4.4, harmonics=(1.0, 0.22))
        add_tone(right, start + 0.006, 0.34, root, 0.10, decay=4.4, harmonics=(1.0, 0.22))

        # Bright marimba-like eighth notes.
        for half in range(2):
            note_start = start + half * BEAT / 2
            note = chord[melody_steps[(beat_index * 2 + half) % len(melody_steps)]] * 2
            pan_left = 0.085 if (beat_index + half) % 2 == 0 else 0.055
            pan_right = 0.055 if (beat_index + half) % 2 == 0 else 0.085
            add_tone(left, note_start, 0.25, note, pan_left, decay=8.5, harmonics=(1.0, 0.34, 0.10))
            add_tone(right, note_start + 0.009, 0.25, note, pan_right, decay=8.5, harmonics=(1.0, 0.34, 0.10))

        # Kick on every beat with extra weight on 1 and 3.
        kick_length = min(int(0.16 * SAMPLE_RATE), samples - int(start * SAMPLE_RATE))
        if kick_length > 0:
            t = np.arange(kick_length) / SAMPLE_RATE
            kick = np.sin(2 * np.pi * (78 - 42 * t) * t) * np.exp(-24 * t)
            gain = 0.15 if beat_index % 4 in (0, 2) else 0.10
            i0 = int(start * SAMPLE_RATE)
            left[i0 : i0 + kick_length] += gain * kick
            right[i0 : i0 + kick_length] += gain * kick

        # Hand clap on beats 2 and 4.
        if beat_index % 4 in (1, 3):
            clap_start = start + 0.01
            i0 = int(clap_start * SAMPLE_RATE)
            length = min(int(0.11 * SAMPLE_RATE), samples - i0)
            if length > 0:
                t = np.arange(length) / SAMPLE_RATE
                noise = rng.standard_normal(length)
                clap = noise * np.exp(-28 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 38 * t) ** 2)
                left[i0 : i0 + length] += 0.055 * clap
                right[i0 : i0 + length] += 0.055 * np.roll(clap, 75)

        # Crisp hi-hats on sixteenth notes.
        for step in range(4):
            hat_start = start + step * BEAT / 4
            i0 = int(hat_start * SAMPLE_RATE)
            length = min(int(0.035 * SAMPLE_RATE), samples - i0)
            if length > 0:
                t = np.arange(length) / SAMPLE_RATE
                hat = rng.standard_normal(length) * np.exp(-90 * t)
                pan = 0.018 if step % 2 == 0 else 0.012
                left[i0 : i0 + length] += pan * hat
                right[i0 : i0 + length] += (0.030 - pan) * hat

    # Add a short rising sparkle every four bars.
    for start in (0.0, 7.5, 15.0):
        for step, frequency in enumerate((523.25, 659.25, 783.99, 1046.50)):
            add_tone(left, start + step * 0.11, 0.30, frequency, 0.040, decay=7.0, harmonics=(1.0, 0.25))
            add_tone(right, start + step * 0.11 + 0.012, 0.30, frequency, 0.052, decay=7.0, harmonics=(1.0, 0.25))

    fade_in = int(0.18 * SAMPLE_RATE)
    fade_out = int(0.85 * SAMPLE_RATE)
    left[:fade_in] *= np.linspace(0, 1, fade_in)
    right[:fade_in] *= np.linspace(0, 1, fade_in)
    left[-fade_out:] *= np.linspace(1, 0, fade_out)
    right[-fade_out:] *= np.linspace(1, 0, fade_out)

    stereo = np.column_stack((left, right))
    peak = np.max(np.abs(stereo))
    stereo *= 0.90 / max(peak, 0.90)
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUTPUT), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(pcm.tobytes())
    print(OUTPUT)


if __name__ == "__main__":
    main()
