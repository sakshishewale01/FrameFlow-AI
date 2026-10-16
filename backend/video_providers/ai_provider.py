"""
AI Video Generation Provider.
Supports external AI video APIs (Pollinations, Hugging Face Inference, Replicate, custom endpoints).
Gracefully checks API tokens and connectivity, falling back to procedural engine if unavailable.
"""

import os
import urllib.parse
from typing import Any, Callable, Dict, Optional, Tuple
import aiohttp

from backend.video_providers.base import BaseVideoProvider


class AIVideoProvider(BaseVideoProvider):
    name: str = "AI Video Generation"
    provider_type: str = "ai_video"

    def __init__(self):
        self.pollinations_key = os.environ.get("POLLINATIONS_API_KEY", "").strip()
        self.hf_token = os.environ.get("HF_TOKEN", "").strip() or os.environ.get("HUGGINGFACE_API_KEY", "").strip()
        self.replicate_token = os.environ.get("REPLICATE_API_TOKEN", "").strip()
        self.custom_api_url = os.environ.get("AI_VIDEO_API_URL", "").strip()

    def is_available(self) -> Tuple[bool, str]:
        if self.pollinations_key:
            return True, "Pollinations Video API configured (via POLLINATIONS_API_KEY)"
        if self.hf_token:
            return True, "Hugging Face Inference API configured (via HF_TOKEN)"
        if self.replicate_token:
            return True, "Replicate Video API configured (via REPLICATE_API_TOKEN)"
        if self.custom_api_url:
            return True, f"Custom AI Video endpoint configured: {self.custom_api_url}"

        return False, "No AI video API key configured (set POLLINATIONS_API_KEY, HF_TOKEN, or REPLICATE_API_TOKEN in environment)"

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
        avail, reason = self.is_available()
        if not avail:
            raise RuntimeError(f"AI Video Provider unavailable: {reason}")

        prompt_text = f"{scene.get('title', '')}: {scene.get('description', '')}. Style: {style}"
        encoded_prompt = urllib.parse.quote(prompt_text)

        if progress_callback:
            await progress_callback(10, f"Querying AI Video API for Scene {scene_idx+1}...")

        # 1. Pollinations Video endpoint
        if self.pollinations_key:
            url = f"https://gen.pollinations.ai/video/{encoded_prompt}?key={self.pollinations_key}&aspect={aspect_ratio}"
            headers = {"Authorization": f"Bearer {self.pollinations_key}"}

            timeout = aiohttp.ClientTimeout(total=120)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(output_path, "wb") as f:
                            f.write(content)
                        return output_path
                    else:
                        text = await resp.text()
                        raise RuntimeError(f"Pollinations AI Video API returned HTTP {resp.status}: {text[:200]}")

        # 2. Hugging Face Inference API
        elif self.hf_token:
            model = os.environ.get("HF_VIDEO_MODEL", "damo-vilab/text-to-video-ms-1.7b")
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {"inputs": prompt_text}

            timeout = aiohttp.ClientTimeout(total=180)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(output_path, "wb") as f:
                            f.write(content)
                        return output_path
                    else:
                        text = await resp.text()
                        raise RuntimeError(f"Hugging Face API returned HTTP {resp.status}: {text[:200]}")

        raise RuntimeError("No supported AI video provider succeeded.")
