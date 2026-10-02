import json
import re

from app.config import settings
from app.gemini_client import generate_text
from app.schemas import PanelOutline, StoryPanel


def extract_json_array(text: str) -> list[dict]:

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
            "Gemini did not return valid JSON."
        )

    return json.loads(
        cleaned[start : end + 1]
    )


def generate_story(
    outlines: list[PanelOutline],
    character_name: str,
    tone: str,
) -> list[StoryPanel]:

    outline_json = json.dumps(
        [
            panel.model_dump()
            for panel in outlines
        ],
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
You are the professional comic script writer
for ComicCraft.

Main character:
{character_name}

Story tone:
{tone}

Here is the generated five-panel outline:

{outline_json}

Expand this outline into a complete comic script.

Return ONLY valid JSON.

Do not use Markdown.
Do not use ```.

Return exactly 5 objects.

Every object must contain:

panel_number
title
scene_description
image_prompt
caption
narration
dialogue

Rules:

1. Preserve panel order.
2. Preserve the original image_prompt.
3. Keep character continuity.
4. narration should be 1-3 short sentences.
5. caption should be a short comic-style caption.
6. dialogue should be concise.
7. If no dialogue is required, return an empty string.
8. Make the story coherent from panel 1 to panel 5.
9. Keep content family-friendly.
10. Do not add graphic content.
"""

    raw_response = generate_text(
        prompt=prompt,
        model=settings.gemini_pro_model,
        temperature=0.9,
        max_output_tokens=3500,
    )

    data = extract_json_array(raw_response)

    if len(data) != 5:
        raise ValueError(
            "Gemini did not return exactly 5 story panels."
        )

    return [
        StoryPanel.model_validate(item)
        for item in data
    ]