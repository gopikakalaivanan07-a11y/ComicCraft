from app.schemas import StoryPanel


def build_comic_layout(
    story_panels: list[StoryPanel],
    image_paths: list[str],
) -> list[dict]:


    if len(story_panels) != len(image_paths):

        raise ValueError(
            "The number of story panels "
            "must match the number of images."
        )

    layout = []

    for index, panel in enumerate(
        story_panels
    ):

        layout.append(
            {
                "panel_number":
                    panel.panel_number,

                "title":
                    panel.title,

                "image":
                    image_paths[index],

                "scene_description":
                    panel.scene_description,

                "caption":
                    panel.caption,

                "narration":
                    panel.narration,

                "dialogue":
                    panel.dialogue,

                "image_prompt":
                    panel.image_prompt,
            }
        )

    return layout