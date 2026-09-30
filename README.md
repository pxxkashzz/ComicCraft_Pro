# ComicCraft Pro

A professional AI comic creator based on the supplied ComicCraft project specification.

## Features
- 5-panel comic generation
- Gemini text generation for outline/story/dialogue
- Gemini image generation for panel artwork
- Futuristic glass/liquid-glass-inspired UI
- Dark/light mode with saved preference
- Responsive mobile + desktop layout
- Generation progress UI
- Per-panel retry
- PDF export
- FastAPI + Jinja2
- Render-ready configuration
- API health check

## Current Gemini integration
This version uses the current Google GenAI Python SDK (`google-genai`) rather than the older `google-generativeai` SDK.

Default models:
- Text: `gemini-3.8-flash`
- Images: `gemini-3.1-flash-image`

Both can be overridden with environment variables.

## Local setup

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Put your Gemini API key in .env
uvicorn app.main:app --reload
```

Open:
http://127.0.0.1:8000

API health:
http://127.0.0.1:8000/health

## Render
Build:
`pip install -r requirements.txt`

Start:
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Environment:
`GEMINI_API_KEY` = your key

Never commit `.env` or expose your Gemini API key in frontend JavaScript.

## Notes
Generated files are stored on the local filesystem for the current service instance. For a production multi-user library, use object storage/database in a later upgrade.
# ComicCraft_Pro
