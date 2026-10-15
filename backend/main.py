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
    motion_type: str = "sway_and_bob"
    character_action: str = ""
    motion_instruction: str = ""


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


app = FastAPI(title="FrameFlow AI API", version="0.3.0")

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

    # Choreography mapping for true animated video
    motion_profiles = [
        ("sway_and_bob", "Gentle Floating & Sway", "Wakes up gracefully on the magical water, gently swaying side-to-side (±15°) with floating rhythmic bobbing."),
        ("bounce_and_hop", "High Bounce with Squash & Stretch", "Rhythmic parabolic jumps with classical squash on landing (0.74x) and stretch in air (1.28x), sending expanding water ripples across the pond."),
        ("pirouette_spin", "360° Dance Pirouette", "Full 360-degree dance pirouette with perspective flip and centrifugal magical sparkles flying outward."),
        ("grand_finale", "Joyful Finale Celebration", "Energetic celebratory dance with high leaps, rapid shimmy, and shimmering water reflection."),
        ("sway_and_bob", "Encore Floating Bow", "Graceful bow on the enchanted pond under glowing starlight, settling into tranquil ripples."),
    ]

    # Style-specific storytelling narratives and visual staging
    style_templates = {
        "Cinematic": [
            ("The Awakening", f"Panoramic camera reveals {prompt_clean}. Soft volumetric mist and glowing water reflections.", f"On a tranquil enchanted pond, the dance begins: {prompt_clean}."),
            ("Catching the Rhythm", "Dynamic medium focus tracking the character as the melody gathers momentum.", "With joyful courage, the character leaps into the rhythm, sending ripples across the water."),
            ("The Magical Pirouette", "Close camera orbit as the character spins gracefully in mid-air.", "Spinning under the moonlight, a flurry of golden sparkles bursts into the night sky."),
            ("The Grand Celebration", "Sweeping crane pullback revealing the full radiant dance on the illuminated pond.", "The water sings in harmony as the final dance reaches its triumphant crescendo."),
            ("Lingering Starlight", "Twilight silhouette on the glowing water, echoing the beauty of the performance.", "From first thought to next frame, the magic of the dance lingers on."),
        ],
        "Cartoon": [
            ("Jump into Action!", f"Vibrant color splash: {prompt_clean}! High-energy bouncy entrance.", f"Whoa, look at that! It's {prompt_clean}! Time to dance and groove!"),
            ("Bouncing Bonanza!", "Zany cartoon physics with exaggerated squash, stretch, and bouncy hops.", "Boing! Bouncing high into the air and splashing joyful waves everywhere!"),
            ("Super Spin Twirl!", "Whirlwind cartoon spin with sparkling stars and comic action lines.", "Round and round we go! A dizzying, delightful 360-degree twirl!"),
            ("Victory Hop!", "Confetti water splashes and huge cartoon smiles.", "Hooray! What an incredible dance party on the pond!"),
            ("See Ya Next Dance!", "Happy wave and playful wink to the audience.", "Until our next great adventure, keep on moving and grooving!"),
        ],
        "Educational": [
            ("Introduction of Form", f"Clear focal staging observing: {prompt_clean}. Fluid mechanics and natural balance.", f"Notice the natural equilibrium of our subject: {prompt_clean} as kinetic movement begins."),
            ("Oscillation and Rhythm", "Analytical view demonstrating harmonic bounce, energy transfer, and ripple propagation.", "As vertical force is applied, elastic deformation creates harmonic oscillation across the surface."),
            ("Rotational Dynamics", "Demonstrating angular momentum and symmetry through a continuous 360-degree axis rotation.", "Through conservation of angular momentum, the spin maintains clean center-of-mass balance."),
            ("Harmonic Synthesis", "Full environmental overview illustrating resonance between character and fluid surface.", "All physical forces align, creating a textbook demonstration of fluid-surface dynamics."),
            ("Concluding Principle", "Summary perspective highlighting repeatable biomechanical principles in nature.", "A perfect fusion of organic rhythm, motion mechanics, and fluid physics."),
        ],
        "Story": [
            ("Once Upon a Thought", f"Atmospheric storybook composition: {prompt_clean}. Gentle fireflies and moonlit waves.", f"Once upon a quiet evening, a magical dance unfolded: {prompt_clean}."),
            ("The Rhythm Awakens", "The character finds its true groove, hopping joyfully across the water lilies.", "Every bounce told a story of courage, splashing light into the twilight pond."),
            ("A Whirl of Magic", "Spinning gracefully as stardust swirls around the petals.", "In a breathtaking pirouette, the night seemed to stand still in wonder."),
            ("A Heartwarming Finale", "Soft golden glow illuminates the peaceful pond as the dance concludes.", "And the pond whispered its joy, holding the memory of this enchanted moment forever."),
            ("Goodnight Little Lotus", "Gentle closing scene under sleepy constellations.", "Sleep sweet, until the dawn sun wakes the pond again."),
        ],
        "Nursery Rhyme": [
            ("Twinkle and Begin!", f"Playful pastel skies with floating stars: {prompt_clean}.", f"Listen close, little friends! Here comes {prompt_clean}!"),
            ("Hop Hop Hop!", "Cheery little hops splashing along the happy rainbow ripples.", "Hop hop hop, jump up high! Tap tap tap, touching the sky!"),
            ("Spin Around!", "Bouncy spinning fun with sparkling bubbles.", "Twirl around, spin and play, dancing all our cares away!"),
            ("Happy Claps!", "Cheery celebration with sweet smiling stars.", "Clap your hands and shout hooray, what a happy, sunny day!"),
            ("Sweet Dreams", "Gentle lullaby chime with sleepy moonbeams.", "Rest your head and close your eyes, under the cozy nighttime skies!"),
        ],
    }

    beats = style_templates.get(request.style, style_templates["Cinematic"])

    return [
        Scene(
            scene_number=index + 1,
            title=beats[index][0],
            description=beats[index][1],
            narration=beats[index][2],
            motion_type=motion_profiles[index][0],
            character_action=motion_profiles[index][1],
            motion_instruction=motion_profiles[index][2],
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
