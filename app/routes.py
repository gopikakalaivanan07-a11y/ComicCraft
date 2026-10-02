from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.exporters import save_pdf
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image, safe_filename
from app.layout_builder import build_comic_layout
from app.schemas import Comic, PromptRequest
from app.storage import get_comic, save_comic


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter()


def validate_story_prompt(prompt: str) -> str:

    prompt = prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Story prompt is required.",
        )

    if len(prompt) > settings.max_prompt_length:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Story prompt must be less than "
                f"{settings.max_prompt_length} characters."
            ),
        )

    return prompt


def generate_complete_comic(
    data: PromptRequest,
) -> Comic:

    # 1. Generate outline
    outline = generate_outline(
        story_prompt=data.story_prompt,
        character_name=data.character_name,
        setting=data.setting,
        tone=data.tone,
        art_style=data.art_style,
    )

    # 2. Generate story
    story = generate_story(
        outlines=outline,
        character_name=data.character_name,
        tone=data.tone,
    )

    # 3. Generate images
    image_paths = []

    for panel in story:

        image_path = generate_image(
            prompt=panel.image_prompt,
            panel_number=panel.panel_number,
        )

        image_paths.append(image_path)

    # 4. Build layout
    layout = build_comic_layout(
        story_panels=story,
        image_paths=image_paths,
    )

    # 5. Create comic ID
    comic_id = uuid4().hex

    # 6. Create PDF
    pdf_path = save_pdf(
        layout=layout,
        comic_id=comic_id,
        contents=story,
    )

    # 7. Create Comic object
    comic = Comic(
        comic_id=comic_id,
        story_prompt=data.story_prompt,
        character_name=data.character_name,
        setting=data.setting,
        tone=data.tone,
        art_style=data.art_style,
        panels=story,
        pdf_path=pdf_path,
    )

    # 8. Save comic
    save_comic(comic)

    return comic


@router.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": settings.app_name,
            "image_provider": settings.image_provider,
        },
    )


@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    try:

        data = PromptRequest(
            story_prompt=validate_story_prompt(
                story_prompt
            ),
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": settings.app_name,
                "error": str(exc),
                "form": {
                    "story_prompt": story_prompt,
                    "character_name": character_name,
                    "setting": setting,
                    "tone": tone,
                    "art_style": art_style,
                },
            },
            status_code=400,
        )

    try:

        comic = generate_complete_comic(data)

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": settings.app_name,
                "error": str(exc),
                "form": data.model_dump(),
            },
            status_code=500,
        )

    preview_panels = []

    for panel in comic.panels:

        filename = safe_filename(
            panel.image_prompt,
            panel.panel_number,
        )

        preview_panels.append(
            {
                **panel.model_dump(),
                "image_url": (
                    f"/static/panels/{filename}"
                ),
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "title": settings.app_name,
            "comic": comic,
            "preview_panels": preview_panels,
        },
    )


@router.post("/generate-comic/json")
async def generate_json(
    data: PromptRequest,
):

    try:

        comic = generate_complete_comic(data)

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    layout = []

    for panel in comic.panels:

        filename = safe_filename(
            panel.image_prompt,
            panel.panel_number,
        )

        layout.append(
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "image": (
                    f"/static/panels/{filename}"
                ),
                "scene_description": panel.scene_description,
                "caption": panel.caption,
                "narration": panel.narration,
                "dialogue": panel.dialogue,
                "image_prompt": panel.image_prompt,
            }
        )

    return {
        "success": True,
        "comic_id": comic.comic_id,
        "layout": layout,
        "pdf_path": comic.pdf_path,
    }


@router.get("/export/{comic_id}")
async def export_comic(
    comic_id: str,
):

    comic = get_comic(comic_id)

    if not comic:

        raise HTTPException(
            status_code=404,
            detail="Comic not found.",
        )

    if not comic.pdf_path:

        raise HTTPException(
            status_code=404,
            detail="PDF path not available.",
        )

    # Convert stored URL path to real file path
    pdf_path = BASE_DIR / comic.pdf_path.lstrip("/")

    if not pdf_path.exists():

        raise HTTPException(
            status_code=404,
            detail=f"PDF file not found: {pdf_path}",
        )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"comiccraft_{comic_id}.pdf",
    )


@router.get("/export-success/{comic_id}")
async def export_success(
    request: Request,
    comic_id: str,
):

    comic = get_comic(comic_id)

    if not comic:

        raise HTTPException(
            status_code=404,
            detail="Comic not found.",
        )

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "title": settings.app_name,
            "comic": comic,
        },
    )


@router.get("/test-image")
async def test_image(
    prompt: str = (
        "A friendly fox in an enchanted forest"
    ),
):

    try:

        image_path = generate_image(
            prompt=prompt,
            panel_number=0,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return {
        "success": True,
        "image_path": image_path,
    }