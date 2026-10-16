"""
Base video generation provider interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Tuple


class BaseVideoProvider(ABC):
    """Abstract interface for video generation providers."""

    name: str = "BaseProvider"
    provider_type: str = "base"

    @abstractmethod
    def is_available(self) -> Tuple[bool, str]:
        """Check whether the provider is configured and available to use."""
        pass

    @abstractmethod
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
        """Renders an individual scene video clip file to output_path."""
        pass
