# FrameFlow AI

**From first thought to next frame.** FrameFlow AI is an automated text-to-animated-video creative studio that turns a text prompt into an intelligent choreographed storyboard and renders an animated MP4 video with consistent characters, dynamic motion, and voiceover narration.

## Overview

FrameFlow provides an end-to-end creative workflow:
1. **Prompt Analysis**: Extracts character traits, colors, setting, and actions from the prompt.
2. **Choreographed Storyboarding**: Formulates structured scene beats with visual staging, dance choreography (swaying, squash & stretch bouncing, 360° pirouettes), and voiceover scripts.
3. **Consistent Character Design**: Generates a high-definition character sprite once, ensuring 100% visual identity consistency across every scene.
4. **Living Environment Physics**: Renders animated water wave displacement, floating bobbing lily pads, ground contact shadows, expanding impact ripple rings, and rising glowing fireflies.
5. **Real 2D Animation Engine**: Applies classical animation principles (squash & stretch, parabolic bounce trajectories, rotational sway, horizontal perspective flips).
6. **MP4 Video & Audio Assembly**: Remuxes synchronized voiceover narration with the animated footage into a streaming-ready MP4 video.

## Current features

- Dark, responsive creative studio interface with FrameFlow branding.
- Prompt editor with validation and clear empty, loading, success, and error states.
- Educational, Cartoon, Cinematic, Story, and Nursery Rhyme style choices.
- 15, 30, and 60 second duration choices with adaptive scene splitting.
- 16:9, 9:16, and 1:1 canvas aspect ratio choices.
- **Choreographed Animation Staging**: Scene cards show distinct motion instructions (e.g. *Sway & Bob*, *Squash, Stretch & High Hopping*, *360° Dance Pirouette*, *Joyful Finale Celebration*).
- **True 2D Character Animation**: Characters physically hop, stretch, squash, tilt, and spin rather than remaining static slides.
- **Environment Motion**: Living water surfaces, wave oscillation, and dynamic particle systems.
- **Consistent Character Appearance**: Character sprite is generated and maintained across all scenes.
- **Voiceover Narration**: Free neural voiceover synthesis powered by Microsoft Edge Neural Voices.
- **CPU-Optimized (40+ FPS)**: Renders directly on Windows with 16 GB RAM and no GPU requirements.
- **In-browser HTML5 Video Player & Direct MP4 Download**.

## Technology stack

- Frontend: React 18, Vite, JavaScript, CSS, Lucide React icons.
- Backend: Python, FastAPI, Pydantic, Uvicorn, Pillow, NumPy, imageio-ffmpeg, edge-tts.
- Communication: JSON over HTTP with CORS enabled for the local Vite server.

## Architecture

```text
Browser (React + Vite)
        |
        | POST /api/storyboard   ---> Generates scenes with motion & narration choreography
        | POST /api/render-video ---> Triggers async 2D animation rendering pipeline
        | GET  /api/video-status ---> Polls real-time progress (0% - 100%)
        | GET  /api/video/{id}   ---> Streams and downloads animated MP4 video
        v
FastAPI Backend
 ├── animation_engine.py (Character sprite builder, environment physics, 2D choreography)
 ├── video_generator.py (Frame compilation + edge-tts audio + FFmpeg stitcher)
 └── generated_videos/  (Rendered MP4 artifacts)
```

## Project structure

```text
FrameFlow-AI/
├── backend/
│   ├── main.py
│   ├── animation_engine.py
│   ├── video_generator.py
│   ├── requirements.txt
│   └── generated_videos/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── .env
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── .env
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Prerequisites

- Windows 10/11
- Python 3.10 or newer
- Node.js 18 or newer and npm

## Windows setup

Open PowerShell in the project folder:

```powershell
cd "C:\Users\saksh\OneDrive\Pictures\Documents\FrameFlow-AI"
```

Create and activate a backend virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

In a second PowerShell terminal, install frontend dependencies:

```powershell
cd "C:\Users\saksh\OneDrive\Pictures\Documents\FrameFlow-AI\frontend"
npm install
```

## Run the application

Terminal 1, from the project root with the virtual environment active:

```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2, from `frontend\`:

```powershell
npm run dev
```

Open the app at [http://localhost:5173](http://localhost:5173). FastAPI's interactive documentation is at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), and the health check is at `http://127.0.0.1:8000/api/health`.

## Example workflow

Prompt:

> A tiny lighthouse keeper discovers a constellation hidden in the ocean and follows its light home.

Choose `Cinematic`, `30s`, and `16:9`, then click **Generate storyboard**. The backend returns four rule-based scene beats, each with a title, description, and duration. The interface labels this as a planning preview so it is not confused with generated video.

## Limitations

- Scene descriptions use fixed rule-based beats; there is no model call.
- No images, audio, narration, video rendering, persistence, authentication, or deployment are implemented.
- The local API URL is intentionally fixed for this learning phase.

## Learning objectives

- Understand React state, controlled form inputs, conditional rendering, and async requests.
- Understand a FastAPI route, Pydantic request/response models, and CORS.
- Trace a JSON request from the browser to the backend and back.
- Practice separating a useful product workflow from future AI integrations.

## Future enhancements

Add a provider-independent AI service layer, scene editing, visual references, user projects, downloadable storyboards, accessibility review, automated tests, and video rendering only after the planning workflow is stable.

## Contributing

This is a personal learning project, but feedback and small educational improvements are welcome. Please explain the change and keep the local setup instructions accurate.

## License

No license has been selected yet. Treat the repository as all rights reserved until a license is added.
