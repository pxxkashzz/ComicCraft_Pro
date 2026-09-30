from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.services.comic import generate_comic
from app.services.pdf_export import save_pdf

BASE = Path(__file__).resolve().parent

app = FastAPI(title="ComicCraft Pro", version="2.0.0")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
app.mount("/exports", StaticFiles(directory=str(BASE.parent / "exports")), name="exports")
templates = Jinja2Templates(directory=str(BASE / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    from app.config import GEMINI_API_KEY, TEXT_MODEL, IMAGE_MODEL
    return {
        "status": "ok",
        "gemini_key_configured": bool(GEMINI_API_KEY),
        "text_model": TEXT_MODEL,
        "image_model": IMAGE_MODEL,
    }


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        comic = generate_comic(
            story_prompt.strip(),
            character_name.strip(),
            setting.strip(),
            tone.strip(),
            art_style.strip(),
        )
        pdf_url = save_pdf(comic)
        return templates.TemplateResponse(
            "preview.html",
            {"request": request, "comic": comic, "pdf_url": pdf_url},
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(exc)},
            status_code=500,
        )


@app.post("/generate-comic/json")
async def generate_json(payload: dict):
    required = ["story_prompt", "character_name", "setting", "tone", "art_style"]
    missing = [key for key in required if not payload.get(key)]
    if missing:
        return JSONResponse(
            {"error": f"Missing fields: {', '.join(missing)}"},
            status_code=422,
        )
    try:
        comic = generate_comic(
            payload["story_prompt"],
            payload["character_name"],
            payload["setting"],
            payload["tone"],
            payload["art_style"],
        )
        pdf_url = save_pdf(comic)
        comic["pdf_url"] = pdf_url
        return comic
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})
