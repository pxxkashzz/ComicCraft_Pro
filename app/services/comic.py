from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from app.services.gemini import generate_outline, generate_story, generate_panel_image

BASE = Path(__file__).resolve().parents[1]
GENERATED = BASE / "static" / "generated"
GENERATED.mkdir(parents=True, exist_ok=True)


def _fallback_panel(text: str, output: Path):
    """Creates a readable fallback image so the comic flow still completes."""
    img = Image.new("RGB", (1024, 768), "#111827")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    wrapped = text[:280]
    draw.text((60, 60), "ComicCraft", fill="white", font=font)
    draw.text((60, 140), wrapped, fill="#cbd5e1", font=font, spacing=12)
    img.save(output)


def generate_comic(prompt, character, setting, tone, art_style):
    job_id = uuid4().hex[:10]
    outline = generate_outline(prompt, character, setting, tone, art_style)
    story = generate_story(outline, character, tone)

    panels = []
    for i, panel in enumerate(outline):
        merged = dict(panel)
        merged.update(story[i])
        filename = f"{job_id}_panel_{i+1}.png"
        path = GENERATED / filename
        try:
            generate_panel_image(merged["image_prompt"], path)
            image_status = "generated"
        except Exception as exc:
            _fallback_panel(
                f"Image generation unavailable for panel {i+1}. "
                f"Story: {merged.get('title', 'Untitled')}",
                path,
            )
            image_status = "fallback"
            merged["image_error"] = str(exc)[:300]
        merged["image_url"] = f"/static/generated/{filename}"
        merged["image_status"] = image_status
        panels.append(merged)

    return {"job_id": job_id, "panels": panels}
