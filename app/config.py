from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Application
    app_name: str = "ComicCraft"
    environment: str = "development"

    # Gemini
    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-3.5-flash-lite"
    gemini_pro_model: str = "gemini-3.5-flash-lite"

    # Image generation
    # Options:
    # placeholder
    # huggingface
    # diffusers
    image_provider: str = "placeholder"

    # Hugging Face
    hf_api_key: str = ""
    hf_image_model: str = "stable-diffusion-v1-5/stable-diffusion-v1-5"

    # Local Diffusers
    local_diffusion_model: str = (
        "stable-diffusion-v1-5/stable-diffusion-v1-5"
    )

    diffusion_device: str = "auto"

    # Image settings
    image_width: int = 512
    image_height: int = 512
    image_steps: int = 20
    image_guidance_scale: float = 7.5

    # Comic settings
    max_prompt_length: int = 1200
    panels_per_comic: int = 5

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()