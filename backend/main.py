"""
FrameFlow AI - Main FastAPI Application.
Provides endpoints for:
- Universal prompt-to-storyboard generation (5s to 300s)
- Background video rendering with cancellation support
- Progress polling and provider metadata
- Secure video streaming & download
"""

import asyncio
import os
import re
import uuid
from typing import Any, Dict, List, Literal, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.prompt_interpreter import compute_scenes_for_duration, detect_entity, detect_environment
from backend.video_generator import OUTPUT_DIR, render_video_job
from backend.video_providers.manager import VideoProviderManager

Style = Literal["Cinematic", "Cartoon", "Educational", "Story", "Nursery Rhyme", "Cyberpunk", "Fantasy"]
AspectRatio = Literal["16:9", "9:16", "1:1"]
EngineMode = Literal["auto", "procedural", "ai_video"]


class StoryboardRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)
    style: Style = "Cinematic"
    duration: int = Field(default=30, ge=5, le=300)
    aspect_ratio: AspectRatio = "16:9"
    engine_mode: EngineMode = "auto"


class Scene(BaseModel):
    scene_number: int
    title: str
    description: str
    duration: int
    narration: str = ""
    motion_type: str = "hover_and_sway"
    camera_motion: str = "pan_right"
    character_action: str = ""
    motion_instruction: str = ""


class StoryboardResponse(BaseModel):
    prompt: str
    style: Style
    duration: int
    aspect_ratio: AspectRatio
    engine_mode: EngineMode
    scenes: List[Scene]
    entity: Dict[str, Any]
    environment: Dict[str, Any]
    message: str


class VideoRenderRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)
    style: Style = "Cinematic"
    duration: int = Field(default=30, ge=5, le=300)
    aspect_ratio: AspectRatio = "16:9"
    engine_mode: EngineMode = "auto"
    scenes: Optional[List[Scene]] = None


class VideoStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    stage: str
    provider_used: Optional[str] = None
    provider_name: Optional[str] = None
    fallback_reason: Optional[str] = None
    video_url: Optional[str] = None
    error: Optional[str] = None


app = FastAPI(title="FrameFlow AI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory jobs store
jobs: Dict[str, dict] = {}
# Cancel flags
cancelled_jobs: set[str] = set()


def create_scenes_from_prompt(prompt: str, style: str, duration: int) -> List[Scene]:
    """Generates prompt-specific scenes across any duration up to 300s."""
    raw_scenes = compute_scenes_for_duration(prompt, style, duration)
    return [Scene(**s) for s in raw_scenes]


async def background_video_runner(
    job_id: str,
    prompt: str,
    style: str,
    aspect_ratio: str,
    duration: int,
    scenes: List[Scene],
    engine_mode: str,
):
    async def update_progress(pct: int, stage_msg: str):
        if job_id in jobs:
            jobs[job_id]["progress"] = pct
            jobs[job_id]["stage"] = stage_msg

    def is_cancelled() -> bool:
        return job_id in cancelled_jobs

    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["stage"] = "Initializing render pipeline..."
        jobs[job_id]["progress"] = 3

        result = await render_video_job(
            job_id=job_id,
            prompt=prompt,
            style=style,
            aspect_ratio=aspect_ratio,
            duration=duration,
            scenes=scenes,
            engine_mode=engine_mode,
            progress_callback=update_progress,
            is_cancelled_func=is_cancelled,
        )

        if is_cancelled():
            jobs[job_id]["status"] = "cancelled"
            jobs[job_id]["stage"] = "Render cancelled by user."
            return

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["stage"] = "Video ready for playback!"
        jobs[job_id]["video_url"] = f"/api/video/{job_id}"
        jobs[job_id]["video_path"] = result["video_path"]
        jobs[job_id]["provider_used"] = result["provider_used"]
        jobs[job_id]["provider_name"] = result["provider_name"]
        jobs[job_id]["fallback_reason"] = result["fallback_reason"]

    except asyncio.CancelledError:
        jobs[job_id]["status"] = "cancelled"
        jobs[job_id]["stage"] = "Render cancelled by user."
    except Exception as e:
        import traceback
        traceback.print_exc()
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["stage"] = f"Render failed: {str(e)}"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0"}


@app.get("/api/providers")
def get_providers():
    manager = VideoProviderManager()
    return manager.get_provider_status()


@app.post("/api/storyboard", response_model=StoryboardResponse)
def create_storyboard(request: StoryboardRequest) -> StoryboardResponse:
    scenes = create_scenes_from_prompt(request.prompt, request.style, request.duration)
    entity = detect_entity(request.prompt)
    env = detect_environment(request.prompt)

    return StoryboardResponse(
        prompt=request.prompt,
        style=request.style,
        duration=request.duration,
        aspect_ratio=request.aspect_ratio,
        engine_mode=request.engine_mode,
        scenes=scenes,
        entity=entity,
        environment=env,
        message=f"Storyboard generated with {len(scenes)} coherent narrative scenes ({request.duration}s total).",
    )


@app.post("/api/render-video")
async def start_video_render(request: VideoRenderRequest, background_tasks: BackgroundTasks) -> dict:
    scenes = request.scenes or create_scenes_from_prompt(
        request.prompt,
        request.style,
        request.duration,
    )
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "stage": "Queued for rendering...",
        "video_url": None,
        "error": None,
        "provider_used": None,
        "provider_name": None,
        "fallback_reason": None,
    }

    background_tasks.add_task(
        background_video_runner,
        job_id=job_id,
        prompt=request.prompt,
        style=request.style,
        aspect_ratio=request.aspect_ratio,
        duration=request.duration,
        scenes=scenes,
        engine_mode=request.engine_mode,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "scenes": [s.model_dump() for s in scenes],
    }


@app.get("/api/video-status/{job_id}", response_model=VideoStatusResponse)
def get_video_status(job_id: str) -> VideoStatusResponse:
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return VideoStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", 0),
        stage=job.get("stage", ""),
        provider_used=job.get("provider_used"),
        provider_name=job.get("provider_name"),
        fallback_reason=job.get("fallback_reason"),
        video_url=job.get("video_url"),
        error=job.get("error"),
    )


@app.post("/api/cancel-job/{job_id}")
def cancel_video_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    cancelled_jobs.add(job_id)
    jobs[job_id]["status"] = "cancelling"
    jobs[job_id]["stage"] = "Cancelling render job..."
    return {"status": "cancelling", "job_id": job_id}


@app.get("/api/video/{job_id}")
def download_video(job_id: str):
    # Security: validate job_id to prevent directory traversal
    if not re.match(r"^[a-zA-Z0-9_\-]+$", job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    # Verify path is strictly inside OUTPUT_DIR
    real_path = os.path.realpath(video_path)
    real_dir = os.path.realpath(OUTPUT_DIR)
    if not real_path.startswith(real_dir):
        raise HTTPException(status_code=403, detail="Unsafe file path access")

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"frameflow_{job_id[:8]}.mp4",
        headers={"Accept-Ranges": "bytes"},
    )
