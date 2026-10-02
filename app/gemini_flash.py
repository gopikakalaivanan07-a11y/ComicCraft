import json
import re

from app.config import settings
from app.gemini_client import generate_text
from app.schemas import PanelOutline


def extract_json_array(text: str) -> list[dict]:
    """
    Extract a JSON array even if Gemini accidentally
    wraps it inside Markdown code fences.
    """

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1:
        raise ValueError(
            "Gemini did not return a valid JSON array."
        )

    json_text = cleaned[start : end + 1]

    return json.loads(json_text)


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> list[PanelOutline]:

    prompt = f"""
You are the outline writer for ComicCraft,
an AI-powered comic story creator.

Create EXACTLY 5 sequential comic panels.

USER STORY IDEA:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

Return ONLY valid JSON.

Do not use Markdown.
Do not use ```.

The JSON must be an array containing exactly
5 objects.

Every object must contain:

panel_number
title
scene_description
image_prompt

Rules:

1. panel_number must be 1, 2, 3, 4, 5.
2. Keep the main character visually consistent.
3. The story should have a clear beginning,
   middle and ending.
4. scene_description should be 1-2 sentences.
5. image_prompt must describe the visual scene.
6. image_prompt must not contain dialogue.
7. Keep the story family-friendly.
8. Avoid graphic or disturbing content.
9. Make the five panels flow naturally.
"""

    raw_response = generate_text(
        prompt=prompt,
        model=settings.gemini_flash_model,
        temperature=0.8,
        max_output_tokens=2200,
    )

    data = extract_json_array(raw_response)

    if len(data) != 5:
        raise ValueError(
            "Gemini did not return exactly 5 panels."
        )

    panels = []

    for item in data:
        panels.append(
            PanelOutline.model_validate(item)
        )

    return panels