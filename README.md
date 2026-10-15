# FrameFlow AI

**From first thought to next frame.** FrameFlow AI is a creative studio that turns a text prompt into an intelligent storyboard and renders a fully narrated MP4 video preview.

## Overview

FrameFlow provides an end-to-end creative workflow. The app collects a prompt and creative settings, generates style-tailored scene beats with voiceover scripts, renders motion visual cards, synthesizes spoken narration, and compiles an MP4 video with in-browser playback and downloads.

## Current features

- Dark, responsive creative studio interface with FrameFlow branding.
- Prompt editor with validation and clear empty, loading, success, and error states.
- Educational, Cartoon, Cinematic, Story, and Nursery Rhyme style choices.
- 15, 30, and 60 second duration choices with adaptive scene splitting.
- 16:9, 9:16, and 1:1 canvas aspect ratio choices.
- Style-specific voiceover narration generation (using Microsoft Edge Neural Voices).
- Asynchronous video rendering pipeline powered by Pillow, imageio, and FFmpeg.
- Real-time progress bar tracking voiceover synthesis, frame rendering, and MP4 assembly.
- In-browser HTML5 video player and direct MP4 file download.
- Dynamic backend URL configuration via `.env`.

## Technology stack

- Frontend: React 18, Vite, JavaScript, CSS, Lucide React icons.
- Backend: Python, FastAPI, Pydantic, Uvicorn, Pillow, imageio-ffmpeg, edge-tts.
- Communication: JSON over HTTP with CORS enabled for the local Vite server.

## Architecture

```text
Browser (React + Vite)
        |
        | POST /api/storyboard   ---> Generates scene beats & voiceover narration
        | POST /api/render-video ---> Triggers async video compilation job
        | GET  /api/video-status ---> Polls real-time progress (0% - 100%)
        | GET  /api/video/{id}   ---> Streams and downloads MP4 video
        v
FastAPI Backend
 ├── video_generator.py (Pillow frame generator + edge-tts audio + FFmpeg stitcher)
 └── generated_videos/  (Rendered MP4 artifacts)
```

## Project structure

```text
FrameFlow-AI/
├── backend/
│   ├── main.py
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
