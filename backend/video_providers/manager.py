"""
Provider Manager and Orchestrator.
Coordinates between AI video generation and the local procedural animation fallback.
"""

import logging
from typing import Any, Callable, Dict, Optional, Tuple

from backend.video_providers.ai_provider import AIVideoProvider
from backend.video_providers.base import BaseVideoProvider
from backend.video_providers.procedural_provider import ProceduralProvider

logger = logging.getLogger("frameflow.providers")


class VideoProviderManager:
    """Orchestrates video rendering providers with automatic fallback."""

    def __init__(self):
        self.procedural_provider = ProceduralProvider()
        self.ai_provider = AIVideoProvider()

    def get_provider_status(self) -> Dict[str, Any]:
        ai_avail, ai_reason = self.ai_provider.is_available()
        proc_avail, proc_reason = self.procedural_provider.is_available()
        return {
            "procedural": {"available": proc_avail, "status": proc_reason},
            "ai_video": {"available": ai_avail, "status": ai_reason},
        }

    async def render_scene(
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
        engine_mode: str = "auto",
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[str, str, str, Optional[str]]:
        """
        Renders a scene clip.
        Returns (output_path, provider_type, provider_name, fallback_reason)
        """
        # Determine whether to attempt AI video
        attempt_ai = engine_mode in ["ai_video", "auto"]
        ai_available, ai_reason = self.ai_provider.is_available()

        if attempt_ai and ai_available:
            try:
                if progress_callback:
                    await progress_callback(20, f"Generating Scene {scene_idx+1} with AI Video Provider...")
                clip_path = await self.ai_provider.render_scene_clip(
                    scene=scene,
                    scene_idx=scene_idx,
                    total_scenes=total_scenes,
                    entity=entity,
                    env=env,
                    style=style,
                    aspect_ratio=aspect_ratio,
                    duration=duration,
                    output_path=output_path,
                    fps=fps,
                    progress_callback=progress_callback,
                )
                return clip_path, "ai_video", self.ai_provider.name, None
            except Exception as e:
                logger.warning(f"AI Video provider failed on scene {scene_idx+1}: {e}. Falling back to procedural engine.")
                fallback_reason = f"AI Video generation failed ({str(e)[:120]}); seamlessly fell back to FrameFlow Procedural Engine."
        else:
            if engine_mode == "ai_video":
                fallback_reason = f"AI Video requested but unconfigured: {ai_reason}. Using FrameFlow Procedural Engine fallback."
            else:
                fallback_reason = None

        # Fallback / Direct procedural animation engine
        clip_path = await self.procedural_provider.render_scene_clip(
            scene=scene,
            scene_idx=scene_idx,
            total_scenes=total_scenes,
            entity=entity,
            env=env,
            style=style,
            aspect_ratio=aspect_ratio,
            duration=duration,
            output_path=output_path,
            fps=fps,
            progress_callback=progress_callback,
        )

        return clip_path, "procedural", self.procedural_provider.name, fallback_reason
