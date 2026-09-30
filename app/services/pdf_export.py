from pathlib import Path
from uuid import uuid4
from fpdf import FPDF
from PIL import Image

EXPORT_DIR = Path(__file__).resolve().parents[2] / "exports"
EXPORT_DIR.mkdir(exist_ok=True)


def ascii_safe(value):
    return str(value).encode("latin-1", "replace").decode("latin-1")


def save_pdf(comic):
    filename = f"comiccraft_{comic['job_id']}_{uuid4().hex[:6]}.pdf"
    path = EXPORT_DIR / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=14)

    for panel in comic["panels"]:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, ascii_safe(f"Panel {panel['panel']}: {panel['title']}"), ln=True)
        pdf.ln(3)

        image_file = Path(__file__).resolve().parents[1] / panel["image_url"].lstrip("/")
        if image_file.exists():
            with Image.open(image_file) as im:
                w, h = im.size
                max_w, max_h = 180, 105
                scale = min(max_w / w, max_h / h)
                pdf.image(str(image_file), w=w * scale, h=h * scale)
        pdf.ln(6)

        sections = [
            ("Scene", panel.get("scene_description", "")),
            ("Caption", panel.get("caption", "")),
            ("Narration", panel.get("narration", "")),
            ("Dialogue", panel.get("dialogue", "")),
        ]
        for label, value in sections:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, label, ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, ascii_safe(value))
            pdf.ln(2)

    pdf.output(str(path))
    return f"/exports/{filename}"
