from app.layout_builder import (
    build_comic_layout,
)

from app.schemas import StoryPanel


def test_layout_builder():

    panels = [

        StoryPanel(
            panel_number=1,

            title="The Beginning",

            scene_description=(
                "A fox enters the forest."
            ),

            image_prompt=(
                "A fox walking "
                "through a forest."
            ),

            caption=(
                "The journey begins."
            ),

            narration=(
                "Foxy walks into "
                "the mysterious forest."
            ),

            dialogue="Hello, forest!",
        )

    ]

    image_paths = [
        "/static/panels/test.png"
    ]

    layout = build_comic_layout(
        story_panels=panels,
        image_paths=image_paths,
    )

    assert len(layout) == 1

    assert (
        layout[0]["panel_number"]
        == 1
    )

    assert (
        layout[0]["image"]
        == "/static/panels/test.png"
    )