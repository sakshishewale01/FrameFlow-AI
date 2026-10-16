"""
FrameFlow AI - Video Generation Orchestrator.
Orchestrates:
- Text-to-speech audio synthesis (edge-tts with silent audio fallback)
- Sequential multi-scene rendering via VideoProviderManager
- Memory-efficient streaming of frames to disk
- Remuxing and FFmpeg concatenation with H.264 / AAC / faststart
- Cancellation checks and progress polling
"""

import asyncio
import math
import os
import subprocess
import tempfile
from typing import Any, Callable, Dict, List, Optional, Tuple

import imageio_ffmpeg
from backend.prompt_interpreter import detect_entity, detect_environment
from backend.video_providers.manager import VideoProviderManager

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated_videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Voice mappings by creative style
VOICE_MAP = {
    "Cinematic": "en-US-GuyNeural",
    "Cartoon": "en-US-AnaNeural",
    "Educational": "en-US-ChristopherNeural",
    "Story": "en-US-AriaNeural",
    "Nursery Rhyme": "en-US-JennyNeural",
}


async def generate_speech_audio(text: str, voice: str, output_path: str) -> float:
    """
    Synthesize narration audio using edge-tts.
    If network or TTS fails, generates a silent track so video rendering never fails.
    Returns the exact audio duration in seconds.
    """
    text_clean = text.strip() if text else ""
    tts_succeeded = False

    if text_clean:
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text_clean, voice)
            await asyncio.wait_for(communicate.save(output_path), timeout=15.0)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                tts_succeeded = True
        except Exception as e:
            # TTS is optional; log warning and create silent audio track
            pass

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    if not tts_succeeded:
        # Generate 3.5 seconds of clean silence using ffmpeg lavfi
        subprocess.run(
            [ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "3.5", output_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return 3.5

    # Measure exact audio duration with ffmpeg
    try:
        result = subprocess.run(
            [ffmpeg, "-i", output_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        for line in result.stderr.splitlines():
            if "Duration:" in line:
                time_str = line.split("Duration:")[1].split(",")[0].strip()
                parts = time_str.split(":")
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    except Exception:
        pass

    return 3.5


async def render_video_job(
    job_id: str,
    prompt: str,
    style: str,
    aspect_ratio: str,
    duration: int,
    scenes: list,
    engine_mode: str = "auto",
    fps: int = 15,
    progress_callback: Optional[Callable] = None,
    is_cancelled_func: Optional[Callable[[], bool]] = None,
) -> Dict[str, Any]:
    """
    Renders the complete video sequence across arbitrary duration (up to 300s):
    1. Synthesizes voiceover narration for all scenes
    2. Sequentially renders visual scene clips to disk
    3. Merges audio and video streams
    4. Stitches all scene clips into a single MP4 with FFmpeg
    """
    output_video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    voice = VOICE_MAP.get(style, "en-US-GuyNeural")
    provider_manager = VideoProviderManager()

    entity = detect_entity(prompt)
    env = detect_environment(prompt)

    total_scenes = len(scenes)
    overall_provider_used = "procedural"
    overall_provider_name = "FrameFlow Procedural 2D Engine"
    overall_fallback_reason: Optional[str] = None

    with tempfile.TemporaryDirectory() as temp_dir:
        scene_video_files: List[str] = []

        # Step 1: Synthesize voiceover audio for each scene
        if progress_callback:
            await progress_callback(5, f"Synthesizing voiceover audio for {total_scenes} scenes...")

        scene_audios: List[str] = []
        scene_durations: List[float] = []

        for idx, scene in enumerate(scenes):
            if is_cancelled_func and is_cancelled_func():
                raise asyncio.CancelledError("Render job cancelled by user")

            audio_path = os.path.join(temp_dir, f"audio_{idx}.mp3")
            narr_text = getattr(scene, "narration", None) or (scene.get("narration") if isinstance(scene, dict) else "")
            if not narr_text:
                narr_text = getattr(scene, "description", None) or (scene.get("description", "") if isinstance(scene, dict) else "")

            audio_dur = await generate_speech_audio(narr_text, voice, audio_path)

            # Target scene duration from storyboard or audio length
            planned_dur = getattr(scene, "duration", None) or (scene.get("duration", 6) if isinstance(scene, dict) else 6)
            effective_dur = max(float(planned_dur), audio_dur + 0.5, 3.0)

            scene_audios.append(audio_path)
            scene_durations.append(effective_dur)

        # Step 2: Render each scene clip sequentially
        for idx, scene in enumerate(scenes):
            if is_cancelled_func and is_cancelled_func():
                raise asyncio.CancelledError("Render job cancelled by user")

            scene_dur = scene_durations[idx]
            scene_dict = scene.model_dump() if hasattr(scene, "model_dump") else (scene if isinstance(scene, dict) else vars(scene))

            scene_raw_video = os.path.join(temp_dir, f"scene_{idx}_raw.mp4")

            # Progress calculation: scenes take 15% to 85% of progress
            scene_base_pct = int(15 + (idx / total_scenes) * 70)
            if progress_callback:
                await progress_callback(scene_base_pct, f"Rendering Scene {idx+1}/{total_scenes}: {scene_dict.get('title', 'Scene')}...")

            async def scene_sub_progress(sub_pct: int, msg: str):
                if progress_callback:
                    calc_pct = scene_base_pct + int((sub_pct / 100.0) * (70 / total_scenes))
                    await progress_callback(min(84, calc_pct), msg)

            raw_clip, prov_type, prov_name, fb_reason = await provider_manager.render_scene(
                scene=scene_dict,
                scene_idx=idx,
                total_scenes=total_scenes,
                entity=entity,
                env=env,
                style=style,
                aspect_ratio=aspect_ratio,
                duration=scene_dur,
                output_path=scene_raw_video,
                fps=fps,
                engine_mode=engine_mode,
                progress_callback=scene_sub_progress,
            )

            if prov_type == "ai_video":
                overall_provider_used = "ai_video"
                overall_provider_name = prov_name
            if fb_reason:
                overall_fallback_reason = fb_reason

            # Remux scene raw video with its audio track using ffmpeg
            scene_final_clip = os.path.join(temp_dir, f"scene_{idx}_final.mp4")
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            cmd = [
                ffmpeg, "-y",
                "-i", raw_clip,
                "-i", scene_audios[idx],
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                "-movflags", "+faststart",
                scene_final_clip,
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            scene_video_files.append(scene_final_clip)

        # Step 3: Concatenate scene clips with FFmpeg concat demuxer
        if progress_callback:
            await progress_callback(88, "Stitching scene clips and finalizing MP4 container...")

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
            await progress_callback(100, "Render complete! Video ready.")

    return {
        "video_path": output_video_path,
        "provider_used": overall_provider_used,
        "provider_name": overall_provider_name,
        "fallback_reason": overall_fallback_reason,
        "duration": sum(scene_durations),
        "scenes_count": total_scenes,
    }
