# FrameFlow AI

**From first thought to next frame.** FrameFlow AI is an automated general-purpose text-to-animation studio that transforms arbitrary user prompts into intelligent, multi-scene choreographed storyboards and renders genuine animated MP4 videos with dynamic sprites, multi-depth parallax environments, virtual camera movement, and synchronized voiceover narration.

---

## Key Features

1. **Universal Prompt-to-Animation Semantic Engine**:
   - Accepts arbitrary user prompts describing characters, vehicles, objects, animals, nature, environments, actions, or stories (never hardcoded to any single example).
   - Intelligently extracts subject category, traits, colors, setting, lighting, motion choreography, and camera dynamics.
   - Automatically partitions any requested duration into coherent narrative acts and sequential scenes.

2. **Full Multi-Layer Procedural 2D Rendering Engine**:
   - Generates genuine 2D animations using Python (`Pillow`, `NumPy`, `imageio`, `imageio-ffmpeg`).
   - Category-specific procedural sprite rendering (aerodynamic rockets with exhaust flame, sports cars with headlights & spinning wheels, marine creatures with swimming undulation, birds with flapping wings, astronauts with walking strides, and celestial bodies with rotating corona flares).
   - Multi-depth parallax backgrounds (distant celestial/sky layers, midground terrain/skylines, animated ground/water with wave oscillation).
   - Dynamic 2D camera viewport motion: smooth zoom push-in, dramatic pull-back, horizontal panning, tracking shots, and crane tilts.
   - Atmospheric particle systems: rain with streaks, bubbles, falling snow, drifting space dust, and fire embers.
   - Cinematic letterboxing with scene counters, choreography badges, and subtitle narration.

3. **Optional AI Video Generation with Graceful Fallback**:
   - Modular provider architecture under `backend/video_providers/`:
     - `procedural`: 100% free, runs locally with zero external API dependencies.
     - `ai_video`: Supports configurable external AI video generation models (Pollinations, Hugging Face Inference API, Replicate).
   - Configurable via standard environment variables (`POLLINATIONS_API_KEY`, `HF_TOKEN`, `REPLICATE_API_TOKEN`).
   - If an AI video provider is unconfigured, rate-limited, or unavailable, the system automatically and seamlessly falls back to the local Procedural Animation Engine without failing the render.

4. **Extended Durations (5s to 300s / 5 Minutes)**:
   - Supports user-selected durations from short 5-15 second clips up to 300 seconds (5 full minutes).
   - Divides longer videos into sequential scenes, renders each scene directly to disk with frame streaming to keep memory usage low, and stitches them into a single master MP4 via FFmpeg.

5. **Integrated Background Jobs & Interactive UI**:
   - Asynchronous job execution with real-time percentage progress and descriptive stage polling.
   - Job cancellation endpoint (`/api/cancel-job/{id}`) to halt long renders on demand.
   - Secure video streaming & download endpoint with path-traversal prevention.
   - HTML5 video player with autoplay, replay, and instant MP4 file download.
   - Creative style presets: Cinematic, Cartoon, Cyberpunk, Educational, Fantasy, Story, Nursery Rhyme.
   - Canvas formats: 16:9 Landscape, 9:16 Shorts/Reels, 1:1 Square.

---

## Architecture

```text
Browser (React + Vite)
        |
        | POST /api/storyboard   ---> Universal semantic prompt analysis & scene mapping
        | POST /api/render-video ---> Launches async background rendering job
        | GET  /api/video-status ---> Polls real-time progress & engine metadata
        | POST /api/cancel-job   ---> Cancels active render job
        | GET  /api/video/{id}   ---> Streams and downloads validated MP4 video
        v
FastAPI Backend
 ├── prompt_interpreter.py       (Semantic entity extraction & multi-scene architect)
 ├── procedural_engine.py        (Parallax backgrounds, dynamic sprites, camera transforms)
 ├── video_providers/            (Base interface, AI video provider, Procedural provider, Manager)
 ├── video_generator.py          (Audio synthesis, sequential clip compilation, FFmpeg stitcher)
 └── generated_videos/           (Master rendered MP4 files)
```

---

## Project Structure

```text
FrameFlow-AI/
├── backend/
│   ├── main.py                  # FastAPI server & route handlers
│   ├── prompt_interpreter.py    # Universal prompt parser & narrative beats
│   ├── procedural_engine.py     # 2D procedural rendering engine
│   ├── video_generator.py       # Render orchestrator & FFmpeg stitcher
│   ├── test_pipeline.py         # End-to-end verification test suite
│   ├── requirements.txt         # Python dependencies
│   ├── generated_videos/        # Rendered MP4 output directory
│   └── video_providers/
│       ├── __init__.py
│       ├── base.py              # Base provider interface
│       ├── procedural_provider.py
│       ├── ai_provider.py       # External AI video API integration
│       └── manager.py           # Provider orchestrator & fallback
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Studio UI with duration controls, player, & progress
│   │   ├── main.jsx
│   │   └── styles.css           # Modern dark-glassmorphic stylesheet
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Prerequisites

- **OS**: Windows 10 or 11
- **Python**: 3.10 or newer (Python 3.14 compatible)
- **Node.js**: 18 or newer and npm

---

## Windows Setup & Installation

### 1. Open PowerShell in the project directory
```powershell
cd "c:\Users\saksh\OneDrive\Pictures\Documents\FrameFlow-AI"
```

### 2. Set up Backend Python Virtual Environment
```powershell
# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install required Python dependencies
python -m pip install -r backend\requirements.txt
```

### 3. Optional: Configure AI Video Provider
If you want to use external AI video generation, create a `.env` file in the root or set environment variables:
```powershell
# Optional Pollinations API key
$env:POLLINATIONS_API_KEY="your_api_key_here"

# Or optional Hugging Face Token
$env:HF_TOKEN="your_hf_token_here"
```
*(If no key is configured, FrameFlow automatically uses the built-in Procedural 2D Engine with zero setup.)*

### 4. Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

## Running the Application

### Terminal 1: Start FastAPI Backend
From the project root:
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Terminal 2: Start Frontend Development Server
In a second PowerShell terminal:
```powershell
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Running the Test Suite

To verify the end-to-end rendering pipeline across different prompts, durations, and aspect ratios:
```powershell
python -m backend.test_pipeline
```
This tests:
- Semantic entity and environment parsing
- Multi-scene storyboard generation
- Sequential rendering of 16:9, 9:16, and 1:1 video clips
- FFmpeg container integrity validation (ensures valid, uncorrupted MP4s)

---

## What Works & Technical Details

- **Universal Prompt Interpretation**: Generates custom scenes, motions, and narration for any prompt (vehicles, animals, robots, humanoids, nature, celestial bodies).
- **Actual Playable MP4 Video**: Renders real 15-24 FPS video encoded with H.264 (`yuv420p`, `-movflags +faststart`) and AAC audio.
- **Duration Support**: Clips from 5 seconds up to 300 seconds (5 minutes), sequentially segmented and stitched.
- **Audio Synchronization**: Automatically generates voiceover narration via Edge TTS; falls back gracefully to clean audio tracks if offline so rendering never fails.
- **Memory Safety**: Frames are streamed sequentially to temporary video files on disk rather than accumulating in RAM.
- **Job Cancellation**: Allows interrupting in-progress video renders cleanly.
