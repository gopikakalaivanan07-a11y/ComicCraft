from google import genai
from google.genai import types

from app.config import settings


def get_client() -> genai.Client:

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Open .env and add your Gemini API key."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_text(
    prompt: str,
    model: str,
    temperature: float = 0.8,
    max_output_tokens: int = 2500,
) -> str:

    client = get_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=temperature,

            max_output_tokens=max_output_tokens,

            # IMPORTANT:
            # Ask Gemini API to return JSON.
            response_mime_type="application/json",
        ),
    )

    text = getattr(
        response,
        "text",
        None,
    )

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text.strip()