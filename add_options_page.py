import pymupdf


# -------------------------------------------------------------------
# Font sizes — change these values to adjust the page's text
# -------------------------------------------------------------------

TITLE_FONT_SIZE = 16
INSTRUCTIONS_FONT_SIZE = 9
OPTION_LABEL_FONT_SIZE = 10
TEXT_INPUT_FONT_SIZE = 9

# Keep 0 for automatic sizing of the checkbox mark.
# This does not control the printed label beside the checkbox.
CHECKBOX_MARK_FONT_SIZE = 0


# -------------------------------------------------------------------
# Options
# -------------------------------------------------------------------
#
# Each row contains:
#   visible label, PDF field name, input type
#
# Supported input types:
#   "checkbox"
#   "text"
#
# Keep PDF field names consistent with your JavaScript lookups and
# the derivative rules in configure_pdf.py.
# -------------------------------------------------------------------

OPTIONS = [
    ("Has Hardy Trait", "Has Hardy Trait", "checkbox"),
]


def add_options_page(doc):
    """Append an options page to the original three-page PDF."""
    if len(doc) != 3:
        raise ValueError(
            f"Expected a three-page input PDF, but found {len(doc)} pages. "
            "This function is intended to append page 4."
        )

    # Match the first page's displayed width and height.
    width = doc[0].rect.width
    height = doc[0].rect.height

    page = doc.new_page(width=width, height=height)

    # Page heading.
    page.insert_text(
        (50, 55),
        "Character Options",
        fontsize=TITLE_FONT_SIZE,
        fontname="hebo",
    )

    # Instructions below the heading.
    page.insert_text(
        (50, 80),
        "Select traits and enter other character options below.",
        fontsize=INSTRUCTIONS_FONT_SIZE,
        fontname="helv",
    )

    existing_names = {
        widget.field_name
        for existing_page in doc
        for widget in existing_page.widgets()
    }

    y = 125
    row_spacing = 40

    for label, field_name, input_type in OPTIONS:
        if field_name in existing_names:
            raise ValueError(f"Duplicate PDF field name: {field_name}")

        if y + 24 > height - 50:
            raise ValueError("Too many options to fit on this page.")

        # Printed label on the left.
        page.insert_text(
            (50, y + 16),
            label,
            fontsize=OPTION_LABEL_FONT_SIZE,
            fontname="helv",
        )

        widget = pymupdf.Widget()
        widget.field_name = field_name
        widget.field_label = label
        widget.border_color = (0, 0, 0)
        widget.border_width = 1
        widget.fill_color = (1, 1, 1)

        if input_type == "checkbox":
            widget.field_type = pymupdf.PDF_WIDGET_TYPE_CHECKBOX
            widget.rect = pymupdf.Rect(300, y, 320, y + 20)
            widget.text_font = "ZaDb"
            widget.text_fontsize = CHECKBOX_MARK_FONT_SIZE
            widget.field_value = "Off"

        elif input_type == "text":
            widget.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
            widget.rect = pymupdf.Rect(
                300,
                y,
                width - 50,
                y + 24,
            )
            widget.text_font = "Helv"
            widget.text_fontsize = TEXT_INPUT_FONT_SIZE
            widget.field_value = ""

        else:
            raise ValueError(f"Unknown input type: {input_type}")

        page.add_widget(widget)
        existing_names.add(field_name)
        y += row_spacing