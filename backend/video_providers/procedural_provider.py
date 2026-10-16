"""
FrameFlow Procedural 2D Animation Provider.
Generates genuine 2D animations using local Pillow and ImageIO without any external APIs.
"""

import math
import os
from typing import Any, Callable, Dict, Optional, Tuple
import imageio
import numpy as np

from backend.procedural_engine import RESOLUTIONS, render_procedural_frame
from backend.video_providers.base import BaseVideoProvider


class ProceduralProvider(BaseVideoProvider):
    name: str = "FrameFlow Procedural 2D Engine"
    provider_type: str = "procedural"

    def is_available(self) -> Tuple[bool, str]:
        return True, "Locally available (Pillow + ImageIO H.264)"

    async def render_scene_clip(
        self,
        scene: Dict[str, Any],
        scene_idx: int,
        total_scenes: int,
        entity: Dict[str, Any],
        env: Dict[str, Any],
        style: str,
        aspect_ratio: str,
        duration: float,
        output_path: str,
        fps: int = 15,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        width, height = RESOLUTIONS.get(aspect_ratio, (1280, 720))
        total_frames = max(1, int(duration * fps))

        scene_title = scene.get("title", f"Scene {scene_idx + 1}")
        scene_desc = scene.get("description", "")
        narration = scene.get("narration", "")
        motion_type = scene.get("motion_type", "hover_and_sway")
        camera_motion = scene.get("camera_motion", "pan_right")

        writer = imageio.get_writer(
            output_path,
            fps=fps,
            codec="libx264",
            pixelformat="yuv420p",
            macro_block_size=None,
        )

        try:
            for f in range(total_frames):
                frame_img = render_procedural_frame(
                    width=width,
                    height=height,
                    entity=entity,
                    env=env,
                    scene_number=scene_idx + 1,
                    total_scenes=total_scenes,
                    scene_title=scene_title,
                    scene_description=scene_desc,
                    narration_text=narration,
                    motion_type=motion_type,
                    camera_motion=camera_motion,
                    frame_idx=f,
                    total_frames_in_scene=total_frames,
                    fps=fps,
                )
                writer.append_data(np.array(frame_img))

                # Periodically report frame-level micro-progress
                if progress_callback and f % (fps * 2) == 0:
                    pct = int((f / total_frames) * 100)
                    await progress_callback(pct, f"Rendering frame {f+1}/{total_frames} of Scene {scene_idx+1}...")
        finally:
            writer.close()

        return output_path
