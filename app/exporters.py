from pathlib import Path
import textwrap

from fpdf import FPDF
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent.parent

EXPORT_DIR = (
    BASE_DIR
    / "static"
    / "exports"
)

PANEL_DIR = (
    BASE_DIR
    / "static"
    / "panels"
)

EXPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def clean_text(value):
    if value is None:
        return ""

    text = str(value)

    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        "…": "...",
        "•": "-",
        "→": "->",
        "←": "<-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = (
        text
        .encode("latin-1", "ignore")
        .decode("latin-1")
    )

    return text


def find_image(image_value):
    """
    Find the actual image file from the
    image path stored in layout.
    """

    if not image_value:
        return None

    image_value = str(image_value).strip()

    # ------------------------------------------------
    # CASE 1:
    # /static/panels/panel_xxx.png
    # ------------------------------------------------

    if image_value.startswith("/static/"):

        relative_path = image_value[
            len("/static/"):
        ]

        direct_path = (
            BASE_DIR
            / "static"
            / relative_path
        )

        if direct_path.exists():
            return direct_path

    # ------------------------------------------------
    # CASE 2:
    # static/panels/panel_xxx.png
    # ------------------------------------------------

    clean_path = image_value.lstrip("/")

    direct_path = (
        BASE_DIR
        / clean_path
    )

    if direct_path.exists():
        return direct_path

    # ------------------------------------------------
    # CASE 3:
    # Actual absolute Windows path
    # ------------------------------------------------

    absolute_path = Path(image_value)

    if (
        absolute_path.is_absolute()
        and absolute_path.exists()
    ):
        return absolute_path

    # ------------------------------------------------
    # CASE 4:
    # Search inside static/panels
    # ------------------------------------------------

    filename = Path(
        image_value
    ).name

    if filename:

        possible_file = (
            PANEL_DIR
            / filename
        )

        if possible_file.exists():
            return possible_file

    # ------------------------------------------------
    # CASE 5:
    # Search recursively
    # ------------------------------------------------

    if filename:

        matches = list(
            PANEL_DIR.rglob(filename)
        )

        if matches:
            return matches[0]

    return None


def add_text(
    pdf,
    text,
    font_size=10,
    bold=False,
):
    text = clean_text(text)

    if not text:
        return

    if bold:
        pdf.set_font(
            "Arial",
            "B",
            font_size,
        )
    else:
        pdf.set_font(
            "Arial",
            "",
            font_size,
        )

    paragraphs = text.split("\n")

    for paragraph in paragraphs:

        if not paragraph.strip():
            pdf.ln(3)
            continue

        lines = textwrap.wrap(
            paragraph,
            width=85,
            break_long_words=True,
            break_on_hyphens=True,
        )

        for line in lines:

            pdf.multi_cell(
                180,
                6,
                line,
            )


def save_pdf(
    contents=None,
    filename="comic.pdf",
    layout=None,
    comic_id=None,
    **kwargs,
):

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    # =================================================
    # TITLE PAGE
    # =================================================

    pdf.add_page()

    pdf.set_font(
        "Arial",
        "B",
        24,
    )

    pdf.cell(
        0,
        15,
        "ComicCraft",
        ln=True,
        align="C",
    )

    pdf.set_font(
        "Arial",
        "",
        13,
    )

    pdf.cell(
        0,
        10,
        "AI Generated Comic",
        ln=True,
        align="C",
    )

    pdf.ln(10)

    # =================================================
    # CHECK LAYOUT
    # =================================================

    if layout is None:
        layout = []

    if not isinstance(layout, list):
        layout = []

    # =================================================
    # EACH PANEL
    # =================================================

    for index, panel in enumerate(layout):

        if not isinstance(panel, dict):
            continue

        pdf.add_page()

        # ------------------------------------------------
        # PANEL NUMBER
        # ------------------------------------------------

        panel_number = panel.get(
            "panel_number",
            index + 1,
        )

        pdf.set_font(
            "Arial",
            "B",
            16,
        )

        pdf.cell(
            0,
            10,
            clean_text(
                f"Panel {panel_number}"
            ),
            ln=True,
        )

        pdf.ln(2)

        # ------------------------------------------------
        # TITLE
        # ------------------------------------------------

        title = panel.get(
            "title",
            "",
        )

        if title:

            add_text(
                pdf,
                title,
                font_size=14,
                bold=True,
            )

            pdf.ln(2)

        # ------------------------------------------------
        # IMAGE
        # ------------------------------------------------

        image_value = panel.get(
            "image",
            "",
        )

        image_path = find_image(
            image_value
        )

        if image_path is not None:

            try:

                with Image.open(
                    image_path
                ) as img:

                    width, height = img.size

                # A4 usable width
                max_width = 180

                # Maximum image height
                max_height = 110

                if width > 0 and height > 0:

                    ratio = min(
                        max_width / width,
                        max_height / height,
                    )

                    display_width = (
                        width * ratio
                    )

                    display_height = (
                        height * ratio
                    )

                else:

                    display_width = 180
                    display_height = 100

                x_position = (
                    210 - display_width
                ) / 2

                pdf.image(
                    str(image_path),
                    x=x_position,
                    y=None,
                    w=display_width,
                    h=display_height,
                )

                pdf.ln(5)

            except Exception as error:

                pdf.set_font(
                    "Arial",
                    "I",
                    10,
                )

                add_text(
                    pdf,
                    f"Image loading error: {error}",
                )

        else:

            pdf.set_font(
                "Arial",
                "I",
                10,
            )

            add_text(
                pdf,
                "Image not found.",
            )

        # ------------------------------------------------
        # SCENE
        # ------------------------------------------------

        scene = panel.get(
            "scene_description",
            "",
        )

        if scene:

            add_text(
                pdf,
                "Scene:",
                font_size=11,
                bold=True,
            )

            add_text(
                pdf,
                scene,
                font_size=10,
            )

            pdf.ln(2)

        # ------------------------------------------------
        # CAPTION
        # ------------------------------------------------

        caption = panel.get(
            "caption",
            "",
        )

        if caption:

            add_text(
                pdf,
                "Caption:",
                font_size=11,
                bold=True,
            )

            add_text(
                pdf,
                caption,
                font_size=10,
            )

            pdf.ln(2)

        # ------------------------------------------------
        # NARRATION
        # ------------------------------------------------

        narration = panel.get(
            "narration",
            "",
        )

        if narration:

            add_text(
                pdf,
                "Narration:",
                font_size=11,
                bold=True,
            )

            add_text(
                pdf,
                narration,
                font_size=10,
            )

            pdf.ln(2)

        # ------------------------------------------------
        # DIALOGUE
        # ------------------------------------------------

        dialogue = panel.get(
            "dialogue",
            "",
        )

        if dialogue:

            add_text(
                pdf,
                "Dialogue:",
                font_size=11,
                bold=True,
            )

            add_text(
                pdf,
                dialogue,
                font_size=10,
            )

    # =================================================
    # FILE NAME
    # =================================================

    if comic_id:

        filename = (
            f"comiccraft_{comic_id}.pdf"
        )

    file_path = (
        EXPORT_DIR
        / filename
    )

    # =================================================
    # SAVE
    # =================================================

    pdf.output(
        str(file_path)
    )

    return (
        f"/static/exports/{filename}"
    )