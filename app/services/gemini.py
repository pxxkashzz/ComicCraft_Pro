import base64
import json
import re
from pathlib import Path

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, TEXT_MODEL, IMAGE_MODEL

_client = None


def get_client():
    global _client
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file locally or "
            "Render Environment Variables."
        )
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _clean_json(text: str):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def generate_outline(prompt: str, character: str, setting: str, tone: str, art_style: str):
    instruction = f"""
Create a cohesive 5-panel comic outline.

User story idea: {prompt}
Main character: {character}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY valid JSON as an array of exactly 5 objects.
Each object must contain:
panel, title, scene_description, narration, dialogue, image_prompt

Keep the same main character consistent across all five panels.
Make the image_prompt detailed enough for an image model.
Do not include markdown fences.
"""
    response = get_client().models.generate_content(
        model=TEXT_MODEL,
        contents=instruction,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
        ),
    )
    data = _clean_json(response.text)
    if not isinstance(data, list) or len(data) != 5:
        raise RuntimeError("Gemini returned an invalid 5-panel outline.")
    return data


def generate_story(outline, character: str, tone: str):
    compact = json.dumps(outline, ensure_ascii=False)
    instruction = f"""
Turn this 5-panel outline into polished comic narration and dialogue.

Character: {character}
Tone: {tone}

Outline:
{compact}

Return ONLY valid JSON as an array of exactly 5 objects.
Each object must contain:
panel, narration, dialogue, caption

Keep the story coherent and concise for a comic page.
Do not change panel order.
Do not include markdown fences.
"""
    response = get_client().models.generate_content(
        model=TEXT_MODEL,
        contents=instruction,
        config=types.GenerateContentConfig(
            temperature=0.7,
            response_mime_type="application/json",
        ),
    )
    data = _clean_json(response.text)
    if not isinstance(data, list) or len(data) != 5:
        raise RuntimeError("Gemini returned invalid story data.")
    return data


def generate_panel_image(image_prompt: str, output_path: Path):
    prompt = (
        "Create a single polished comic panel illustration. "
        "No speech bubbles, no captions, no watermark-like text. "
        "Keep the visual style consistent with this prompt: " + image_prompt
    )
    response = get_client().models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="4:3",
                image_size="1K",
            ),
        ),
    )

    for part in response.parts:
        if getattr(part, "inline_data", None) is not None:
            image = part.as_image()
            image.save(output_path)
            return str(output_path)

    raise RuntimeError("Gemini image model returned no image data.")
