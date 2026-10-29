import subprocess
from pathlib import Path

import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw"
TAKES = RAW / "final-takes"
ASSETS = ROOT / "video-production" / "assets"
WORK = ROOT / "video-production" / "render-work"
OUTPUT = ROOT / "video-output"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def run(args):
    command = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *map(str, args)]
    print("Rendering", Path(args[-1]).name, flush=True)
    subprocess.run(command, check=True)


def still_segment(source, duration, destination):
    run(
        [
            "-loop", "1", "-i", source,
            "-t", str(duration),
            "-vf", "fps=30,format=yuv420p",
            "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-movflags", "+faststart", destination,
        ]
    )


def visual_segment(source, caption, watermark, crop, speed, duration, destination, still=False):
    input_args = ["-loop", "1"] if still else []
    filter_chain = (
        f"[0:v]{crop},scale=1280:720:flags=lanczos,setpts=(PTS-STARTPTS)*{1/speed:.8f},fps=30[base];"
        "[base][1:v]overlay=0:0:format=auto[captioned];"
        "[captioned][2:v]overlay=1040:18:format=auto,format=yuv420p[out]"
    )
    run(
        [
            *input_args, "-i", source,
            "-loop", "1", "-i", caption,
            "-loop", "1", "-i", watermark,
            "-filter_complex", filter_chain,
            "-map", "[out]", "-t", str(duration), "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-movflags", "+faststart", destination,
        ]
    )


def montage(segments, durations, music, destination):
    inputs = []
    for segment in segments:
        inputs += ["-i", segment]
    inputs += ["-i", music]
    fade = 0.35
    filters = []
    previous = "0:v"
    elapsed = durations[0]
    for index in range(1, len(segments)):
        offset = elapsed - fade * index
        label = f"v{index}"
        filters.append(
            f"[{previous}][{index}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}[{label}]"
        )
        previous = label
        elapsed += durations[index]
    final_duration = sum(durations) - fade * (len(durations) - 1)
    music_index = len(segments)
    filters.append(
        f"[{music_index}:a]volume=1.80,afade=t=in:st=0:d=1.2,"
        f"afade=t=out:st={final_duration - 2.2:.3f}:d=2.2[audio]"
    )
    run(
        [
            *inputs,
            "-filter_complex", ";".join(filters),
            "-map", f"[{previous}]", "-map", "[audio]",
            "-t", f"{final_duration:.3f}",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-c:a", "aac", "-b:a", "160k", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", destination,
        ]
    )
    return final_duration


def vertical_version(source, watermark, duration, destination):
    filters = (
        "[0:v]split=2[fgsrc][bgsrc];"
        "[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,gblur=sigma=38,eq=brightness=-0.10:saturation=1.15[bg];"
        "[fgsrc]scale=1080:608:flags=lanczos[fg];"
        "[bg][fg]overlay=0:656[composed];"
        "[1:v]scale=330:90[wm];"
        "[composed][wm]overlay=375:220:format=auto,format=yuv420p[out]"
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
    watermark_path = ASSETS / "watermark.png"

    segments = [
        WORK / "01-title.mp4",
        WORK / "02-login.mp4",
        WORK / "03-dashboard.mp4",
        WORK / "04-learning.mp4",
        WORK / "05-homework.mp4",
        WORK / "06-motivation.mp4",
        WORK / "07-arena.mp4",
        WORK / "08-end.mp4",
    ]
    durations = [2.6, 2.0, 6.0, 8.8, 11.0, 8.7, 15.1, 2.8]

    still_segment(ASSETS / "title-16x9.png", durations[0], segments[0])
    visual_segment(
        RAW / "01-login.png", ASSETS / "caption-login.png", watermark_path,
        "crop=1440:810:0:0", 1.0, durations[1], segments[1], still=True,
    )
    visual_segment(
        TAKES / "02-dashboard.webm", ASSETS / "caption-dashboard.png", watermark_path,
        "trim=start=0.5,crop=1152:648:0:0", 1.0, durations[2], segments[2],
    )
    visual_segment(
        TAKES / "03-learning.webm", ASSETS / "caption-learning.png", watermark_path,
        "trim=start=0.8,crop=1440:810:0:0", 1.6, durations[3], segments[3],
    )
    visual_segment(
        TAKES / "04-homework.webm", ASSETS / "caption-homework.png", watermark_path,
        "trim=start=3.0,crop=1440:810:0:0", 2.2, durations[4], segments[4],
    )
    visual_segment(
        TAKES / "05-motivation.webm", ASSETS / "caption-motivation.png", watermark_path,
        "trim=start=0.5,crop=1152:648:0:0", 1.8, durations[5], segments[5],
    )
    visual_segment(
        TAKES / "06-arena.webm", ASSETS / "caption-arena.png", watermark_path,
        "trim=start=0.5,crop=1440:810:0:0", 2.3, durations[6], segments[6],
    )
    still_segment(ASSETS / "end-16x9.png", durations[7], segments[7])

    wide_output = OUTPUT / "amakids-platform-overview-16x9.mp4"
    final_duration = montage(segments, durations, ASSETS / "music-original.wav", wide_output)
    vertical_version(
        wide_output,
        watermark_path,
        final_duration,
        OUTPUT / "amakids-platform-overview-9x16.mp4",
    )
    print(f"Finished both videos at {final_duration:.2f} seconds", flush=True)


if __name__ == "__main__":
    main()
