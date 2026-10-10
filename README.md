# FrameFlow AI

**From first thought to next frame.** FrameFlow AI is a learning-focused creative studio that turns a text prompt into a structured storyboard preview.

## Overview

FrameFlow is an early portfolio project for learning how an AI-oriented product is assembled. The current app collects a prompt and creative settings, sends them to a FastAPI endpoint, and displays a rule-based sequence of scenes. It does **not** render a finished video yet.

## Motivation

Turning a blank page into a coherent video plan can be difficult. A storyboard is a useful first step: it makes the subject, pacing, and visual beats concrete before more advanced generation tools are introduced.

## Current features

- Dark, responsive creative studio interface with FrameFlow branding.
- Prompt editor with validation and helpful empty, loading, success, and error states.
- Educational, Cartoon, Cinematic, Story, and Nursery Rhyme style choices.
- 15, 30, and 60 second duration choices.
- 16:9, 9:16, and 1:1 canvas choices.
- React request to `POST http://127.0.0.1:8000/api/storyboard`.
- Rule-based storyboard generation with numbered scenes and balanced durations.

## Planned roadmap

The following are intentionally **planned**, not implemented:

1. Genuine AI scene planning using a model provider selected later.
2. AI-generated visual references for each scene.
3. Narration, music, and caption planning.
4. Rendered video output and export.
5. Saved projects, authentication, and collaborative editing.

## Technology stack

- Frontend: React 18, Vite, JavaScript, CSS, Lucide React icons.
- Backend: Python, FastAPI, Pydantic, Uvicorn.
- Communication: JSON over HTTP with CORS enabled for the local Vite server.

## Architecture

```text
Browser (React + Vite)
        |
        | POST /api/storyboard
        v
FastAPI (rule-based storyboard service)
        |
        v
JSON response: settings + scenes
```

## Project structure

```text
FrameFlow-AI/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
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
