from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=5,
        max_length=1200,
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=80,
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=120,
    )

    tone: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    art_style: str = Field(
        ...,
        min_length=1,
        max_length=80,
    )

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style",
    )
    @classmethod
    def clean_values(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty.")

        return value


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class StoryPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str
    dialogue: str = ""


class Comic(BaseModel):
    comic_id: str

    story_prompt: str
    character_name: str
    setting: str
    tone: str
    art_style: str

    panels: list[StoryPanel]

    pdf_path: str | None = None