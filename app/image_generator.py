from pathlib import Path
import hashlib

from PIL import Image, ImageDraw

from app.config import settings


BASE_DIR = Path(__file__).resolve().parent.parent

PANEL_DIR = BASE_DIR / "static" / "panels"

PANEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


_pipeline = None


def safe_filename(
    prompt: str,
    panel_number: int,
) -> str:

    digest = hashlib.sha256(
        prompt.encode("utf-8")
    ).hexdigest()[:16]

    return (
        f"panel_{panel_number}_{digest}.png"
    )


def create_placeholder_image(
    prompt: str,
    path: Path,
    panel_number: int,
) -> str:

    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height,
        ),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (
            15,
            15,
            settings.image_width - 15,
            settings.image_height - 15,
        ),
        outline="black",
        width=5,
    )

    draw.text(
        (35, 35),
        f"ComicCraft - Panel {panel_number}",
        fill="black",
    )

    text = prompt[:250]

    lines = []

    for i in range(0, len(text), 45):
        lines.append(
            text[i:i + 45]
        )

    y = 100

    for line in lines[:8]:

        draw.text(
            (35, y),
            line,
            fill="black",
        )

        y += 35

    image.save(path)

    return f"/static/panels/{path.name}"


def generate_with_diffusers(
    prompt: str,
    path: Path,
) -> str:

    global _pipeline

    import torch

    from diffusers import StableDiffusionPipeline

    if _pipeline is None:

        device = settings.diffusion_device

        if device == "auto":

            device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

        dtype = (
            torch.float16
            if device == "cuda"
            else torch.float32
        )

        _pipeline = StableDiffusionPipeline.from_pretrained(
            settings.local_diffusion_model,
            torch_dtype=dtype,
        )

        _pipeline = _pipeline.to(device)

    result = _pipeline(
        prompt,
        height=settings.image_height,
        width=settings.image_width,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance_scale,
    )

    result.images[0].save(path)

    return f"/static/panels/{path.name}"


def generate_with_huggingface(
    prompt: str,
    path: Path,
) -> str:

    if not settings.hf_api_key:

        raise RuntimeError(
            "HF_API_KEY is missing. "
            "Add it to .env or use "
            "IMAGE_PROVIDER=placeholder."
        )

    from huggingface_hub import InferenceClient

    client = InferenceClient(
        provider="hf-inference",
        api_key=settings.hf_api_key,
    )

    image = client.text_to_image(
        prompt,
        model=settings.hf_image_model,
    )

    image.save(path)

    return f"/static/panels/{path.name}"


def generate_image(
    prompt: str,
    panel_number: int,
) -> str:

    filename = safe_filename(
        prompt,
        panel_number,
    )

    path = PANEL_DIR / filename

    if path.exists():

        return f"/static/panels/{filename}"

    enhanced_prompt = f"""
High-quality comic illustration.

Clear composition.
Expressive character.
Consistent character design.
Detailed environment.
Cinematic lighting.
Family-friendly.
No text.
No watermark.

Comic style:
{prompt}
"""

    provider = (
        settings.image_provider
        .lower()
        .strip()
    )

    if provider == "placeholder":

        return create_placeholder_image(
            enhanced_prompt,
            path,
            panel_number,
        )

    if provider == "huggingface":

        return generate_with_huggingface(
            enhanced_prompt,
            path,
        )

    if provider == "diffusers":

        return generate_with_diffusers(
            enhanced_prompt,
            path,
        )

    raise RuntimeError(
        f"Unsupported IMAGE_PROVIDER: "
        f"{settings.image_provider}"
    )
