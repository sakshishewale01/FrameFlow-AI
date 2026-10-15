import asyncio
import math
import os
import subprocess
import tempfile
import uuid
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
import imageio
import imageio_ffmpeg

# Setup storage directory for rendered videos
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated_videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Style color schemes and voice mappings
STYLE_CONFIGS = {
    "Cinematic": {
        "bg_top": (10, 15, 30),
        "bg_bottom": (22, 36, 68),
        "accent": (235, 175, 70),
        "accent_secondary": (147, 197, 253),
        "card_bg": (15, 23, 42, 220),
        "voice": "en-US-GuyNeural",
        "tag": "CINEMATIC MASTER",
    },
    "Cartoon": {
        "bg_top": (38, 18, 74),
        "bg_bottom": (88, 28, 135),
        "accent": (251, 191, 36),
        "accent_secondary": (244, 114, 182),
        "card_bg": (30, 27, 75, 220),
        "voice": "en-US-AnaNeural",
        "tag": "ANIMATED ADVENTURE",
    },
    "Educational": {
        "bg_top": (8, 25, 45),
        "bg_bottom": (15, 52, 85),
        "accent": (56, 189, 248),
        "accent_secondary": (94, 234, 212),
        "card_bg": (12, 34, 56, 220),
        "voice": "en-US-ChristopherNeural",
        "tag": "DISCOVERY SERIES",
    },
    "Story": {
        "bg_top": (28, 16, 28),
        "bg_bottom": (64, 28, 54),
        "accent": (251, 146, 60),
        "accent_secondary": (244, 63, 94),
        "card_bg": (42, 20, 36, 220),
        "voice": "en-US-AriaNeural",
        "tag": "ILLUSTRATED TALE",
    },
    "Nursery Rhyme": {
        "bg_top": (18, 38, 64),
        "bg_bottom": (35, 78, 120),
        "accent": (250, 204, 21),
        "accent_secondary": (74, 222, 128),
        "card_bg": (20, 48, 80, 220),
        "voice": "en-US-JennyNeural",
        "tag": "WHIMSICAL RHYMES",
    },
}

ASPECT_RATIO_RESOLUTIONS = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "1:1": (1080, 1080),
}


def get_font(size: int, bold: bool = False):
    """Load standard Windows Arial or fallback to default."""
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except Exception:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()


def create_gradient_backdrop(width: int, height: int, color_top: Tuple[int, int, int], color_bottom: Tuple[int, int, int]) -> Image.Image:
    """Create a vertical gradient image."""
    base = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        factor = y / max(1, height - 1)
        r = int(color_top[0] * (1 - factor) + color_bottom[0] * factor)
        g = int(color_top[1] * (1 - factor) + color_bottom[1] * factor)
        b = int(color_top[2] * (1 - factor) + color_bottom[2] * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return base


def wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Wrap text to fit within a given pixel width."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def render_scene_frame(
    width: int,
    height: int,
    style: str,
    scene_number: int,
    total_scenes: int,
    title: str,
    description: str,
    narration: str,
    frame_index: int,
    total_frames_in_scene: int,
    overall_progress: float,
) -> Image.Image:
    """Render a single high-definition video frame with dynamic motion elements."""
    config = STYLE_CONFIGS.get(style, STYLE_CONFIGS["Cinematic"])
    img = create_gradient_backdrop(width, height, config["bg_top"], config["bg_bottom"])
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Subtle ambient animated glowing circles
    motion_t = frame_index / max(1, total_frames_in_scene)
    pulse = math.sin(motion_t * math.pi * 2) * 15
    drift_x = math.cos(motion_t * math.pi) * 30
    drift_y = math.sin(motion_t * math.pi) * 20

    glow_color = (*config["accent"], 30)
    center_glow = (int(width * 0.5 + drift_x), int(height * 0.4 + drift_y))
    radius = int(min(width, height) * 0.35 + pulse)
    draw.ellipse(
        [
            center_glow[0] - radius,
            center_glow[1] - radius,
            center_glow[0] + radius,
            center_glow[1] + radius,
        ],
        fill=glow_color,
    )

    # Top Header Banner
    header_font = get_font(max(14, int(height * 0.024)), bold=True)
    header_text = f"FRAMEFLOW AI  •  {config['tag']}  •  SCENE {scene_number:02d}/{total_scenes:02d}"
    draw.text((int(width * 0.06), int(height * 0.05)), header_text, font=header_font, fill=config["accent"])

    # Outer decorative canvas border
    border_margin = int(min(width, height) * 0.035)
    draw.rounded_rectangle(
        [border_margin, border_margin, width - border_margin, height - border_margin],
        radius=18,
        outline=(*config["accent_secondary"], 80),
        width=2,
    )

    # Central Narrative Display Card
    card_margin_x = int(width * 0.07)
    card_top = int(height * 0.12)
    card_bottom = int(height * 0.88)
    card_rect = [card_margin_x, card_top, width - card_margin_x, card_bottom]
    draw.rounded_rectangle(card_rect, radius=20, fill=config["card_bg"], outline=(*config["accent"], 140), width=2)

    # Scene Number Badge inside card
    badge_x = card_margin_x + int(width * 0.04)
    badge_y = card_top + int(height * 0.04)
    badge_w = int(width * 0.22)
    badge_h = max(28, int(height * 0.048))
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=14, fill=(*config["accent"], 50))
    badge_font = get_font(max(13, int(height * 0.022)), bold=True)
    draw.text((badge_x + 12, badge_y + (badge_h - int(height * 0.022)) // 2 - 2), f"BEAT #{scene_number}", font=badge_font, fill=config["accent"])

    # Scene Title
    title_font = get_font(max(24, int(height * 0.048)), bold=True)
    title_y = badge_y + badge_h + int(height * 0.03)
    max_text_width = (width - card_margin_x * 2) - int(width * 0.08)
    title_lines = wrap_text(title, title_font, max_text_width, draw)
    curr_y = title_y
    for tline in title_lines[:2]:
        draw.text((badge_x, curr_y), tline, font=title_font, fill=(255, 255, 255, 255))
        curr_y += int(height * 0.055)

    # Visual Cue / Staging Description
    desc_label_font = get_font(max(12, int(height * 0.02)), bold=True)
    curr_y += int(height * 0.02)
    draw.text((badge_x, curr_y), "VISUAL STAGING & DIRECTION", font=desc_label_font, fill=config["accent_secondary"])
    curr_y += int(height * 0.03)

    desc_font = get_font(max(16, int(height * 0.028)))
    desc_lines = wrap_text(description, desc_font, max_text_width, draw)
    for dline in desc_lines[:3]:
        draw.text((badge_x, curr_y), dline, font=desc_font, fill=(203, 213, 225, 240))
        curr_y += int(height * 0.036)

    # Bottom Narration / Voiceover Subtitle Bar inside card
    narration_box_h = max(70, int(height * 0.16))
    narration_box_y = card_bottom - narration_box_h - int(height * 0.03)
    narration_box = [badge_x, narration_box_y, width - card_margin_x - int(width * 0.04), narration_box_y + narration_box_h]
    draw.rounded_rectangle(narration_box, radius=12, fill=(0, 0, 0, 160), outline=(*config["accent"], 100), width=1)

    narr_label_font = get_font(max(11, int(height * 0.018)), bold=True)
    draw.text((badge_x + 14, narration_box_y + 8), "VOICEOVER NARRATION", font=narr_label_font, fill=config["accent"])

    narr_font = get_font(max(14, int(height * 0.025)), bold=True)
    narr_lines = wrap_text(narration, narr_font, max_text_width - 28, draw)
    narr_y = narration_box_y + int(height * 0.04)
    for nline in narr_lines[:2]:
        draw.text((badge_x + 14, narr_y), nline, font=narr_font, fill=(254, 240, 138, 255))
        narr_y += int(height * 0.032)

    # Bottom Progress Bar across scenes
    bar_y = height - int(height * 0.04)
    bar_h = max(4, int(height * 0.01))
    draw.rectangle([border_margin, bar_y, width - border_margin, bar_y + bar_h], fill=(30, 41, 59, 200))

    progress_w = int((width - border_margin * 2) * max(0.0, min(1.0, overall_progress)))
    if progress_w > 0:
        draw.rectangle([border_margin, bar_y, border_margin + progress_w, bar_y + bar_h], fill=config["accent"])

    # Composite alpha overlay onto base
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


async def generate_speech_audio(text: str, voice: str, output_path: str) -> float:
    """Generate speech audio file with edge-tts and return its duration in seconds."""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
    except Exception as e:
        print(f"TTS warning, falling back to silent track: {e}")
        # Generate 3 seconds of silence using ffmpeg as fallback
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run(
            [ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "3", output_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # Measure exact audio duration with ffmpeg
    try:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        result = subprocess.run(
            [ffmpeg, "-i", output_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        for line in result.stderr.splitlines():
            if "Duration:" in line:
                # Format: Duration: 00:00:04.25, start: ...
                time_str = line.split("Duration:")[1].split(",")[0].strip()
                parts = time_str.split(":")
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    except Exception:
        pass
    return 4.0


async def render_video_job(
    job_id: str,
    prompt: str,
    style: str,
    aspect_ratio: str,
    duration: int,
    scenes: list,
    progress_callback=None,
) -> str:
    """
    Renders the complete video:
    1. Generates speech audio for all scenes
    2. Renders animated frames for each scene matching speech length
    3. Merges video frames and audio track into a single MP4 with FFmpeg
    """
    width, height = ASPECT_RATIO_RESOLUTIONS.get(aspect_ratio, (1280, 720))
    config = STYLE_CONFIGS.get(style, STYLE_CONFIGS["Cinematic"])
    voice = config["voice"]
    fps = 12

    output_video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")

    with tempfile.TemporaryDirectory() as temp_dir:
        scene_video_files = []
        total_scenes = len(scenes)

        if progress_callback:
            await progress_callback(10, "Synthesizing voiceover narration for scenes...")

        # Step 1: Synthesize audio and calculate scene lengths
        scene_audios = []
        scene_durations = []
        for idx, scene in enumerate(scenes):
            audio_path = os.path.join(temp_dir, f"audio_{idx}.mp3")
            narration_text = getattr(scene, "narration", None) or scene.get("narration") if isinstance(scene, dict) else None
            if not narration_text:
                narration_text = (
                    scene.description if hasattr(scene, "description") else scene.get("description", "")
                )
            actual_audio_dur = await generate_speech_audio(narration_text, voice, audio_path)
            # Ensure minimum duration so scene doesn't flash too fast
            target_scene_dur = max(actual_audio_dur + 0.8, 3.0)
            scene_audios.append(audio_path)
            scene_durations.append(target_scene_dur)

        total_video_duration = sum(scene_durations)

        # Step 2: Render video frames for each scene
        elapsed_video_time = 0.0
        for idx, scene in enumerate(scenes):
            scene_title = scene.title if hasattr(scene, "title") else scene.get("title", f"Scene {idx+1}")
            scene_desc = scene.description if hasattr(scene, "description") else scene.get("description", "")
            narration_text = getattr(scene, "narration", None) or (scene.get("narration") if isinstance(scene, dict) else scene_desc)
            scene_dur = scene_durations[idx]
            total_frames = int(scene_dur * fps)

            temp_scene_video = os.path.join(temp_dir, f"scene_{idx}_raw.mp4")
            writer = imageio.get_writer(temp_scene_video, fps=fps, codec="libx264", pixelformat="yuv420p")

            for f in range(total_frames):
                current_time = elapsed_video_time + (f / fps)
                overall_progress = current_time / max(1.0, total_video_duration)
                frame_img = render_scene_frame(
                    width=width,
                    height=height,
                    style=style,
                    scene_number=idx + 1,
                    total_scenes=total_scenes,
                    title=scene_title,
                    description=scene_desc,
                    narration=narration_text,
                    frame_index=f,
                    total_frames_in_scene=total_frames,
                    overall_progress=overall_progress,
                )
                import numpy as np
                writer.append_data(np.array(frame_img))

            writer.close()
            elapsed_video_time += scene_dur

            # Remux scene raw video with its audio track
            scene_with_audio = os.path.join(temp_dir, f"scene_{idx}_final.mp4")
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            cmd = [
                ffmpeg, "-y",
                "-i", temp_scene_video,
                "-i", scene_audios[idx],
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                "-movflags", "+faststart",
                scene_with_audio,
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            scene_video_files.append(scene_with_audio)

            if progress_callback:
                pct = int(25 + ((idx + 1) / total_scenes) * 55)
                await progress_callback(pct, f"Rendered Scene {idx+1} of {total_scenes} with synchronized audio...")

        # Step 3: Concatenate all scene clips into the final video
        if progress_callback:
            await progress_callback(85, "Stitching scene clips and compiling final MP4...")

        concat_list_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for sf in scene_video_files:
                escaped_path = sf.replace("\\", "/")
                f.write(f"file '{escaped_path}'\n")

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        concat_cmd = [
            ffmpeg, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_file,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-movflags", "+faststart",
            output_video_path,
        ]
        subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if progress_callback:
            await progress_callback(100, "Video rendering complete!")

    return output_video_path
