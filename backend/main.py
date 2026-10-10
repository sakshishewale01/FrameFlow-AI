from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


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


class StoryboardResponse(BaseModel):
    prompt: str
    style: Style
    duration: Duration
    aspect_ratio: AspectRatio
    scenes: list[Scene]
    message: str


app = FastAPI(title="FrameFlow AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_scenes(request: StoryboardRequest) -> list[Scene]:
    scene_count = 3 if request.duration == 15 else 4 if request.duration == 30 else 5
    base_duration = request.duration // scene_count
    remainder = request.duration - (base_duration * scene_count)
    beats = [
        ("The spark", f"Open with the central idea: {request.prompt}. Set the mood with a clear visual hook."),
        ("The journey", "Introduce the main subject and show the first meaningful change or discovery."),
        ("The turning point", "Build momentum with a challenge, surprising detail, or emotional shift."),
        ("The reveal", "Bring the story together with the most memorable image and a satisfying payoff."),
        ("The next frame", "End on a hopeful final beat that invites the viewer to keep exploring."),
    ]
    return [
        Scene(
            scene_number=index + 1,
            title=beats[index][0],
            description=beats[index][1],
            duration=base_duration + (1 if index < remainder else 0),
        )
        for index in range(scene_count)
    ]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/storyboard", response_model=StoryboardResponse)
def create_storyboard(request: StoryboardRequest) -> StoryboardResponse:
    return StoryboardResponse(
        prompt=request.prompt,
        style=request.style,
        duration=request.duration,
        aspect_ratio=request.aspect_ratio,
        scenes=build_scenes(request),
        message="Storyboard ready. This is a rule-based planning preview, not a finished video.",
    )
