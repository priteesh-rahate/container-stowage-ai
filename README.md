# Container Stowage AI

An AI-assisted container vessel stowage planning system built with FastAPI and React. The project supports cargo manifest handling, container placement, vessel layout visualization, voyage simulation, and a local AI assistant.

> **Project status:** Academic project using a synthetic vessel layout. It is not certified for real-world vessel operations.

## Features

- Cargo manifest upload and processing
- Container placement and stowage planning
- Container position validation, including 40-foot container footprints
- Synthetic vessel layout with 4,000 slots
- Multi-port voyage loading and discharge simulation
- Local AI assistant using Ollama
- Automated Python tests

## Technology Stack

**Backend:** Python, FastAPI, Pydantic, Pandas

**Frontend:** React, TypeScript, Vite

**AI:** Ollama with the Qwen2.5 7B model

## Prerequisites

Install the following:

- Git
- Python 3.11
- Node.js and npm
- Ollama (required for the local AI assistant)

## Installation on Windows

### 1. Clone the repository

```powershell
git clone <REPOSITORY_URL>
cd container-stowage-ai
```

Replace `<REPOSITORY_URL>` with the GitHub repository URL.

### 2. Set up the Python backend

From the project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Backend API documentation:

http://127.0.0.1:8000/docs

### 3. Set up the frontend

Open a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite, normally:

http://localhost:5173

### 4. Set up the local AI assistant

Install Ollama, then run:

```powershell
ollama pull qwen2.5:7b
```

Make sure Ollama is running before using AI features. Other project features may work without the local AI model, depending on their implementation.

## Running Tests

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Project Structure

```text
container-stowage-ai/
├── backend/
│   ├── main.py
│   ├── ai_service.py
│   ├── placement.py
│   ├── slots.py
│   ├── vessel_layout.py
│   └── voyage_simulation.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
├── requirements.txt
├── sample_manifest.csv
└── README.md
```

Additional tests and sample manifests are included in the repository.

## Collaboration

1. Create a separate branch for each feature or fix.
2. Commit changes with descriptive messages.
3. Push the branch to GitHub.
4. Open a pull request to review changes before merging into `main`.

## Limitations

The vessel layout is synthetic. The system is intended for academic demonstration and development, not operational maritime decision-making. Real-world deployment would require additional validation for vessel stability, stack loads, structural constraints, dangerous goods segregation, and applicable maritime regulations.
