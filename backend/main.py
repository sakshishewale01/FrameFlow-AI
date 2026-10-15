import asyncio
import os
import uuid
from typing import Dict, Literal, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.video_generator import OUTPUT_DIR, render_video_job

Style = Literal["Educational", "Cartoon", "Cinematic", "Story", "Nursery Rhyme"]
AspectRatio = Literal["16:9", "9:16", "1:1"]
Duration = Literal[15, 30, 60]


class StoryboardRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=1000)
    style: Style = "Cinematic"
    duration: Duration = 30
    aspect_ratio: AspectRatio = "16:9"


class Scene(BaseModel):
    scene_number: int
    title: str
    description: str
    duration: int
    narration: str = ""


class StoryboardResponse(BaseModel):
    prompt: str
    style: Style
    duration: Duration
    aspect_ratio: AspectRatio
    scenes: list[Scene]
    message: str


class VideoRenderRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=1000)
    style: Style = "Cinematic"
    duration: Duration = 30
    aspect_ratio: AspectRatio = "16:9"
    scenes: Optional[list[Scene]] = None


class VideoStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    stage: str
    video_url: Optional[str] = None
    error: Optional[str] = None


app = FastAPI(title="FrameFlow AI API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job state store
jobs: Dict[str, dict] = {}


def build_scenes(request: StoryboardRequest) -> list[Scene]:
    scene_count = 3 if request.duration == 15 else 4 if request.duration == 30 else 5
    base_duration = request.duration // scene_count
    remainder = request.duration - (base_duration * scene_count)
    prompt_clean = request.prompt.strip()

    # Style-specific storytelling narratives and visual staging
    style_templates = {
        "Cinematic": [
            ("The Awakening", f"Wide panoramic shot establishes the scene: {prompt_clean}. Soft volumetric mist and dramatic rim lighting.", f"In the stillness of the beginning, an unforgettable vision stirs: {prompt_clean}."),
            ("The Crossing", "Medium tracking camera glides with the protagonist as tension mounts and the environment shifts.", "With every measured step forward, the world unveils mysteries long concealed."),
            ("The Turning Point", "Intense low-angle focus, high contrast, golden embers illuminate a pivotal revelation.", "Here in the crucible of discovery, the hidden truth bursts into brilliant focus."),
            ("The Luminous Return", "Sweeping crane pullback into the infinite horizon, triumphant amber aura and lens flare.", "Guided by the constellations of the journey, the path home shines clear and true."),
            ("The Horizon Awaits", "Lingering cinematic silhouette under twilight stars, leaving an indelible cinematic impression.", "From first thought to next frame, the echo of wonder travels on."),
        ],
        "Cartoon": [
            ("Jump into Action!", f"Vibrant color splash and zany perspective: {prompt_clean}. Bouncy energetic frame introduction.", f"Whoa, look at that! It's {prompt_clean}! Get ready for an epic adventure!"),
            ("Up, Down, and Around!", "Fast dynamic panning shot with playful squash-and-stretch cartoon motion and bright pop accents.", "Off we go zooming through twists, turns, and hilarious surprises!"),
            ("A Wild Twist!", "Exaggerated close-up with funny expressions and sparkles of lightning cartoon energy.", "Hold onto your hats! A totally unexpected puzzle pops right into view!"),
            ("Victory Dance!", "Celebratory fireworks of confetti, sunny golden hues, and happy character poses.", "Hooray! Together we solved it, bringing joy and color to everyone around!"),
            ("To the Next Fun!", "Waving goodbye with a bouncy wink to the camera and vibrant rainbow trail.", "What wild ride will we take tomorrow? Stay tuned for more fun!"),
        ],
        "Educational": [
            ("Foundational Concept", f"Clear analytical visualization: {prompt_clean}. High-definition focal diagram with informative layout.", f"Let us examine our central premise: {prompt_clean}. Notice how the core elements interact."),
            ("The Mechanism at Work", "Step-by-step breakdown highlighting moving components, arrows of motion, and structural clarity.", "As the process unfolds, key variables guide the reaction and drive meaningful change."),
            ("Critical Observation", "Magnified split-frame comparison displaying before-and-after results with precision.", "At this pivotal junction, evidence confirms what theory predicted."),
            ("Synthesized Conclusion", "Comprehensive master view connecting each data point into a unified understanding.", "By tracing every step, we uncover a repeatable blueprint for discovery."),
            ("Practical Application", "Real-world contextual demonstration inspiring further exploration and practical mastery.", "With these principles in hand, you are ready to apply this insight anywhere."),
        ],
        "Story": [
            ("Once Upon a Thought", f"Atmospheric storybook composition: {prompt_clean}. Warm painterly textures and gentle shadows.", f"Once upon a quiet evening, a wondrous tale unfolded: {prompt_clean}."),
            ("Into the Deep Woods", "Winding cobblestone path illuminated by fireflies and gentle lanterns.", "A curious heart set forth into the quiet unknown, listening to the secrets of the wind."),
            ("The Moment of Truth", "Dramatic firelight reflection revealing a choice that tests courage and kindness.", "When the shadows whispered doubt, courage flickered and sparked into flame."),
            ("A Heartwarming Dawn", "Soft golden morning light cascades across peaceful landscapes, comforting and warm.", "At last, peace settled over the land, woven into the hearts of all who believed."),
            ("The Story Continues", "Gentle closing of the book illustration with glowing stars fading softly into memory.", "And they remembered: every ending is simply the threshold of another great tale."),
        ],
        "Nursery Rhyme": [
            ("Twinkle and Begin!", f"Playful pastel skies with floating stars and smiling clouds: {prompt_clean}.", f"Listen close, little friends! Here comes a happy song about {prompt_clean}!"),
            ("Pitter Patter Steps", "Cheery little footprints dancing along a gentle rainbow road with soft grass.", "Tiptoe, tap-tap, happy and bright, dancing along in the sweet morning light!"),
            ("Peek-a-boo Surprise!", "Bouncy pop-up illustration with big friendly smiles and sparkling bubbles.", "Peek-a-boo! What do we see? A marvelous surprise for you and for me!"),
            ("Sweet Dreams and Hugs", "A cozy moon smiling down softly on warm glowing cottages with sleepy lanterns.", "Rest your head, close your eyes tight, the stars are singing goodnight, goodnight!"),
            ("Until Tomorrow Sings", "Gentle lullaby chime with friendly critters nestled warmly together.", "Sleep sweet until the bright sun wakes the morning sky again!"),
        ],
    }

    beats = style_templates.get(request.style, style_templates["Cinematic"])

    return [
        Scene(
            scene_number=index + 1,
            title=beats[index][0],
            description=beats[index][1],
            narration=beats[index][2],
            duration=base_duration + (1 if index < remainder else 0),
        )
        for index in range(scene_count)
    ]


async def background_video_runner(job_id: str, prompt: str, style: str, aspect_ratio: str, duration: int, scenes: list[Scene]):
    async def update_progress(pct: int, stage_msg: str):
        if job_id in jobs:
            jobs[job_id]["progress"] = pct
            jobs[job_id]["stage"] = stage_msg

    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["stage"] = "Starting generation..."
        jobs[job_id]["progress"] = 5

        video_path = await render_video_job(
            job_id=job_id,
            prompt=prompt,
            style=style,
            aspect_ratio=aspect_ratio,
            duration=duration,
            scenes=scenes,
            progress_callback=update_progress,
        )

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["stage"] = "Video ready for playback!"
        jobs[job_id]["video_url"] = f"/api/video/{job_id}"
        jobs[job_id]["video_path"] = video_path
    except Exception as e:
        import traceback
        traceback.print_exc()
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["stage"] = f"Failed: {str(e)}"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/storyboard", response_model=StoryboardResponse)
def create_storyboard(request: StoryboardRequest) -> StoryboardResponse:
    scenes = build_scenes(request)
    return StoryboardResponse(
        prompt=request.prompt,
        style=request.style,
        duration=request.duration,
        aspect_ratio=request.aspect_ratio,
        scenes=scenes,
        message=f"Storyboard ready ({len(scenes)} scenes). Click 'Render Video' to produce the narrated MP4 preview.",
    )


@app.post("/api/render-video")
async def start_video_render(request: VideoRenderRequest, background_tasks: BackgroundTasks) -> dict:
    scenes = request.scenes or build_scenes(
        StoryboardRequest(
            prompt=request.prompt,
            style=request.style,
            duration=request.duration,
            aspect_ratio=request.aspect_ratio,
        )
    )
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "stage": "Queued for rendering...",
        "video_url": None,
        "error": None,
    }

    background_tasks.add_task(
        background_video_runner,
        job_id=job_id,
        prompt=request.prompt,
        style=request.style,
        aspect_ratio=request.aspect_ratio,
        duration=request.duration,
        scenes=scenes,
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
        video_url=job.get("video_url"),
        error=job.get("error"),
    )


@app.get("/api/video/{job_id}")
def download_video(job_id: str):
    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"frameflow_{job_id[:8]}.mp4",
        headers={"Accept-Ranges": "bytes"},
    )
