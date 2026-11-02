# Consilium

**A council of AI models deliberates on your question.**

Consilium is a web application that uses multiple AI models to produce structured, evidence-aware responses. Rather than relying on one model’s first answer, its backend routes a request, extracts relevant information, runs independent analyses, reviews claims against available evidence, and applies a final safety check.

The project is built with **FastAPI**, **React**, **TypeScript**, and **Vite**, and uses **Groq** to access language models.

> **Important:** Consilium is an experimental AI application, not a medical device or a substitute for professional care. AI-generated information can be incorrect, incomplete, or out of date. Do not use it to diagnose or treat a condition. Consult a qualified healthcare professional for medical advice. For urgent or emergency symptoms, contact local emergency services.

## Contents

- [What Consilium does](#what-consilium-does)
- [How it works](#how-it-works)
- [Architecture](#architecture)
- [Technology stack](#technology-stack)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [Using the API](#using-the-api)
- [Project structure](#project-structure)
- [Privacy and security](#privacy-and-security)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## What Consilium does

Consilium accepts a question through a web interface or its API and returns a structured response. Depending on the request and pipeline result, the response can include:

- A safety assessment and route
- Extracted information and details that may be missing or unclear
- A final answer and assessment
- Claims and available sources
- Uncertainties
- Model deliberation details
- The pipeline phases that completed

The design goal is to make responses more considered and transparent than a single, unreviewed model output. Using multiple models does **not** guarantee correctness.

## How it works

The backend runs a multi-stage pipeline. Some independent model calls may run in parallel.

1. **Safety assessment and routing**  
   A safety classifier and router assess the request. Safety results can affect the route.

2. **Relevant information extraction**  
   The system extracts details relevant to the request and identifies information that is missing, ambiguous, or unreadable. It does not assume every request contains a complete patient profile.

3. **Independent analysis**  
   Two analyst models produce separate responses.

4. **Evidence retrieval and claim review**  
   The pipeline identifies claims and evaluates them against evidence available to the application. Evidence and source availability may vary.

5. **Peer review**  
   The analysts review each other’s initial work.

6. **Re-evaluation**  
   The analyses are reconsidered in light of peer review and evidence.

7. **Final adjudication**  
   A separate model synthesizes the reviewed information into a structured answer.

8. **Final safety check**  
   The output receives a final safety review, with urgent guidance elevated when appropriate.

The API runs this work as a single request; it does not currently provide live server-side progress updates. The frontend displays a simplified phase indicator, which may not correspond to real-time backend progress.

## Architecture

```text
┌──────────────────────┐       HTTP / JSON       ┌──────────────────────┐
│                      │  POST /api/council      │                      │
│  React + TypeScript  │ ──────────────────────▶ │  FastAPI backend     │
│  Vite frontend       │ ◀────────────────────── │  Pipeline and API    │
│  localhost:5173      │       JSON response     │  localhost:8000      │
└──────────────────────┘                         └──────────┬───────────┘
                                                            │
                                                            │ model requests
                                                            ▼
                                                 ┌────────────────────────┐
                                                 │ Groq API and configured │
                                                 │ language models         │
                                                 └────────────────────────┘
```

- The **frontend** collects the user’s prompt and displays the response.
- The **backend** validates requests, orchestrates the pipeline, and returns structured JSON.
- The **model provider** processes model requests using the configured API key.

## Technology stack

| Area | Technology |
|---|---|
| Backend | Python 3.12+, FastAPI, Uvicorn |
| Frontend | React 19, TypeScript, Vite |
| Model access | Groq Python SDK |
| Validation and configuration | Pydantic |
| HTTP client | HTTPX |
| UI animation | Framer Motion |
| Fonts | Instrument Serif and Sora |

### Default model roles

The model IDs below are defaults and can be overridden with environment variables.

| Role | Default model |
|---|---|
| Router | `openai/gpt-oss-20b` |
| Safety classifier | `openai/gpt-oss-safeguard-20b` |
| Simple/general response | `openai/gpt-oss-20b` |
| Analyst 1 | `openai/gpt-oss-120b` |
| Analyst 2 | `openai/gpt-oss-20b` |
| Final adjudicator | `openai/gpt-oss-120b` |
| Vision/report use | `qwen/qwen3.6-27b` |

Model availability depends on your Groq account and the provider’s current model offerings.

## Getting started

### Prerequisites

Install the following before you begin:

- Python 3.12 or later
- Node.js 18 or later
- npm
- A Groq API key

### 1. Clone the repository

```bash
git clone <repo-url>
cd Consilium
```

Replace `<repo-url>` with the repository’s clone URL.

### 2. Create and activate a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

From the repository root:

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file from the provided template:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your Groq API key. Keep this file local; **never commit a real key**.

```env
GROQ_API_KEY=your_key_here

MODEL_ROUTER=openai/gpt-oss-20b
MODEL_SAFETY=openai/gpt-oss-safeguard-20b
MODEL_SIMPLE=openai/gpt-oss-20b
MODEL_MODEL1=openai/gpt-oss-120b
MODEL_MODEL2=openai/gpt-oss-20b
MODEL_MODEL3=openai/gpt-oss-120b
MODEL_VISION=qwen/qwen3.6-27b

MAX_TOKENS=2048
TEMPERATURE=0.3
```

The model and generation settings are optional overrides if the application provides defaults for them. See [Configuration](#configuration).

### 5. Start the backend

From the repository root, with the virtual environment activated:

```bash
uvicorn backend.main:app --reload --port 8000
```

The backend should be available at `http://localhost:8000`.

### 6. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite—typically [http://localhost:5173](http://localhost:5173).

The development server is configured to proxy API requests to the backend. Keep both servers running while using the local application.

## Configuration

Application settings are managed through environment variables, usually loaded from the root `.env` file.

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Groq API key; required for model requests |
| `MODEL_ROUTER` | `openai/gpt-oss-20b` | Request-routing model |
| `MODEL_SAFETY` | `openai/gpt-oss-safeguard-20b` | Safety-classification model |
| `MODEL_SIMPLE` | `openai/gpt-oss-20b` | Simple/general response model |
| `MODEL_MODEL1` | `openai/gpt-oss-120b` | First analyst model |
| `MODEL_MODEL2` | `openai/gpt-oss-20b` | Second analyst model |
| `MODEL_MODEL3` | `openai/gpt-oss-120b` | Final adjudication model |
| `MODEL_VISION` | `qwen/qwen3.6-27b` | Vision/report model setting |
| `MAX_TOKENS` | `2048` | Maximum tokens for a model call |
| `TEMPERATURE` | `0.3` | Model sampling temperature |

The backend configuration is defined in `backend/config.py`. Check that file for the authoritative list of supported settings and defaults.

## Using the API

### `POST /api/council`

Submit a prompt as JSON:

```http
POST /api/council
Content-Type: application/json
```

```json
{
  "prompt": "What questions should I ask my doctor about this diagnosis?"
}
```

The response is a JSON object. Its fields include the prompt, route, safety assessment, answer, assessment, extracted information, claims, sources, uncertainties, model details, final safety result, and completed pipeline phases. Some values may be `null` or empty, depending on the request and the pipeline result.

A shortened, illustrative response shape:

```json
{
  "prompt": "What questions should I ask my doctor about this diagnosis?",
  "route": "MEDICAL_ANALYSIS",
  "safety": {
    "risk_level": "safe",
    "route_override": false,
    "red_flags": [],
    "reason": "..."
  },
  "answer": "...",
  "assessment": {
    "certainty": "possible",
    "evidence_quality": "moderate"
  },
  "extracted_information": {},
  "claims": [],
  "sources": [],
  "uncertainties": [],
  "model_details": null,
  "final_safety": null,
  "phases_completed": [
    "safety_and_routing",
    "information_extraction",
    "dual_model_analysis",
    "evidence_retrieval",
    "peer_review",
    "re_evaluation",
    "final_claim_matrix",
    "final_adjudication",
    "final_safety_gate"
  ]
}
```

The example is for illustration; actual values and optional fields depend on the implementation and result.

### `GET /health`

Check whether the backend is responding:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

FastAPI’s interactive API documentation is normally available at [http://localhost:8000/docs](http://localhost:8000/docs) while the backend is running.

## Project structure

```text
Consilium/
├── .env.example
├── REPORT.md
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Settings and environment variables
│   ├── llm_client.py           # Groq client helpers
│   ├── models.py               # Request and response schemas
│   ├── pipeline.py             # Deliberation pipeline orchestration
│   ├── prompts.py              # System prompts and templates
│   ├── requirements.txt        # Python dependencies
│   └── routers/
│       └── council.py          # Council API endpoint
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts           # Vite configuration and API proxy
    └── src/
        ├── App.tsx              # Root component and application state
        ├── App.css
        ├── index.css
        ├── api/
        │   └── council.ts       # Frontend API client
        ├── components/
        │   ├── CouncilView.tsx
        │   ├── PhaseIndicator.tsx
        │   ├── PromptInput.tsx
        │   └── ResponsePanel.tsx
        └── types/
            └── index.ts         # TypeScript interfaces
```

## Privacy and security

- Prompts are sent to Groq for model processing. Review the provider’s current privacy and data-handling terms before using the application with sensitive information.
- Do not submit personally identifying information or confidential medical records.
- Keep `.env` out of version control. Never put API keys in frontend code, screenshots, logs, or public issue reports.
- Before deploying the backend publicly, add appropriate authentication, rate limiting, abuse protection, and production configuration. The current API has no authentication and is intended for local development unless secured separately.
- Review logging, data retention, and any evidence-retrieval behavior before using the application with real users.
- A safety classifier and final safety check can reduce risk but cannot guarantee that every unsafe or incorrect response will be detected.

## Known limitations

- **Requests are synchronous:** the API waits for the pipeline to finish; it does not stream the answer.
- **No conversation history:** requests are stateless; follow-up questions do not automatically include prior context.
- **Progress is not live:** the frontend phase indicator uses client-side behavior and is not a server-sent progress feed.
- **No wired image/report upload flow:** a vision model setting may be present, but that does not mean image or PDF upload is available in the UI.
- **No caching:** repeated prompts may run the pipeline again.
- **No authentication:** the API does not require a user account by default.

## Troubleshooting

### The backend reports a missing or invalid API key

- Confirm `.env` exists in the expected location.
- Check that `GROQ_API_KEY` contains a valid key and has no surrounding quotes or accidental spaces.
- Restart the backend after changing environment variables.
- Never share the key in terminal screenshots, logs, or public reports.

### The frontend cannot reach the backend

- Confirm the backend is running on port `8000`.
- Confirm the frontend is running and check the proxy configuration in `frontend/vite.config.ts`.
- Look at both terminal windows for startup errors.

### A model request fails

- Check that the configured model IDs are available to your Groq account.
- Verify your API key and provider account status.
- Inspect the backend terminal for the error details, taking care not to publish sensitive request data.

### Python or Node dependencies fail to install

- Verify your Python and Node.js versions meet the prerequisites.
- Activate the Python virtual environment before installing or running backend dependencies.
- Run `npm install` from the `frontend` directory.

## License

**All rights reserved.** No license is currently provided. Unless a license is added, others do not receive permission to use, modify, or redistribute this project. Making the repository public does not change that.