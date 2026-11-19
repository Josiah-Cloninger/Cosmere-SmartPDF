import pymupdf


# -------------------------------------------------------------------
# Page 4 content
# -------------------------------------------------------------------
#
# Keep PDF field names consistent with the lookups in
# calculate_stats.js and calculate_skills.js.
# -------------------------------------------------------------------

# Facet heading, then the attributes shown under it.
ENHANCED_GROUPS = [
    ("PHYSICAL", ["Strength", "Speed"]),
    ("COGNITIVE", ["Intellect", "Willpower"]),
    ("SPIRITUAL", ["Awareness", "Presence"]),
]

ENHANCED_FIELDS = [
    f"Enhanced {attribute}"
    for _, attributes in ENHANCED_GROUPS
    for attribute in attributes
]

# Each row contains: talent name, PDF field name, effect on the sheet.
TRAITS = [
    ("Hardy", "Has Hardy Trait", "Max health +1 per level."),
    ("Composed", "Has Composed Trait", "Max focus +1 per tier."),
    ("Invested", "Has Invested Trait", "Max Investiture +1 per tier."),
    (
        "Collected",
        "Has Collected Trait",
        "Cognitive and Spiritual defense +2.",
    ),
    (
        "Customary Garb",
        "Has Customary Garb Trait",
        "Physical and Spiritual defense +2. "
        "Tick only while visibly wearing suitable attire.",
    ),
    ("Surefooted", "Has Surefooted Trait", "Movement +10 ft."),
]

TRAIT_FIELDS = [field_name for _, field_name, _ in TRAITS]

NOTES_COLUMNS = 4

NOTES_FIELDS = [
    f"Other Traits and Notes {column}"
    for column in range(1, NOTES_COLUMNS + 1)
]

ENHANCED_APPLIES = (
    "Skill modifiers, movement, lifting capacity, recovery die, "
    "senses range, and unarmed damage update automatically. "
    "Add the bonus yourself to talents that directly use the attribute."
)
ENHANCED_EXCLUDES = (
    "Defenses, maximum health, maximum focus, and maximum Investiture "
    "always use the attribute without its Enhanced bonus."
)


# -------------------------------------------------------------------
# Appearance
# -------------------------------------------------------------------

BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
BAND_GRAY = (0.76, 0.76, 0.76)
TEXT_GRAY = (0.35, 0.35, 0.35)

HEADING_FONT = "tibo"
LABEL_FONT = "hebo"
BODY_FONT = "helv"

ENHANCED_INPUT_FONT_SIZE = 20
NOTES_INPUT_FONT_SIZE = 10

LEFT = 18
RIGHT = 594
COLUMN_GAP = 10


# -------------------------------------------------------------------
# Drawing helpers
# -------------------------------------------------------------------

def centered_text(page, rect, text, font, size, color=BLACK):
    """Print one line of text, centered in rect."""
    width = pymupdf.get_text_length(text, fontname=font, fontsize=size)
    x = rect.x0 + (rect.width - width) / 2
    page.insert_text(
        (x, rect.y0 + size),
        text,
        fontname=font,
        fontsize=size,
        color=color,
    )


def wrapped_text(page, rect, text, font, size, color=BLACK):
    """Print text wrapped to rect, failing rather than clipping it."""
    unused = page.insert_textbox(
        rect,
        text,
        fontname=font,
        fontsize=size,
        color=color,
    )

    if unused < 0:
        raise ValueError(f"Text does not fit its box: {text}")


def panel(page, rect, fill=WHITE, notch=7):
    """Draw a notched panel with the sheet's offset double border."""
    def outline(r):
        return [
            (r.x0 + notch, r.y0),
            (r.x1 - notch, r.y0),
            (r.x1, r.y0 + notch),
            (r.x1, r.y1 - notch),
            (r.x1 - notch, r.y1),
            (r.x0 + notch, r.y1),
            (r.x0, r.y1 - notch),
            (r.x0, r.y0 + notch),
            (r.x0 + notch, r.y0),
        ]

    page.draw_polyline(
        outline(rect + (2, 2, 2, 2)),
        color=BLACK,
        fill=WHITE,
        width=0.75,
    )
    page.draw_polyline(
        outline(rect),
        color=BLACK,
        fill=fill,
        width=1.25,
    )


def copy_artwork(page, source_doc, source_page, clip):
    """Copy part of an existing sheet page to the same position."""
    page.show_pdf_page(clip, source_doc, source_page, clip=clip)


def add_text_widget(page, field_name, label, rect, font_size, flags=0):
    widget = pymupdf.Widget()
    widget.field_name = field_name
    widget.field_label = label
    widget.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
    widget.field_flags = flags
    widget.rect = rect
    widget.text_font = "Helv"
    widget.text_fontsize = font_size
    widget.field_value = ""
    page.add_widget(widget)
    return widget


def add_checkbox_widget(page, field_name, label, rect):
    widget = pymupdf.Widget()
    widget.field_name = field_name
    widget.field_label = label
    widget.field_type = pymupdf.PDF_WIDGET_TYPE_CHECKBOX
    widget.rect = rect
    widget.border_color = BLACK
    widget.border_width = 1
    widget.fill_color = WHITE
    widget.text_font = "ZaDb"
    widget.text_fontsize = 0
    widget.field_value = "Off"
    page.add_widget(widget)


# -------------------------------------------------------------------
# Page sections
# -------------------------------------------------------------------

def draw_header(page):
    title_panel = pymupdf.Rect(240, 16, RIGHT - 2, 74)
    panel(page, title_panel)
    centered_text(
        page,
        pymupdf.Rect(title_panel.x0, 24, title_panel.x1, 50),
        "CHARACTER OPTIONS",
        HEADING_FONT,
        18,
    )
    centered_text(
        page,
        pymupdf.Rect(title_panel.x0, 50, title_panel.x1, 66),
        "Calculated values on page 1 update as you change these options.",
        BODY_FONT,
        8.5,
        TEXT_GRAY,
    )


def draw_enhanced_section(doc, page):
    band = pymupdf.Rect(0, 84, page.rect.width, 214)
    page.draw_rect(band, color=None, fill=BAND_GRAY)

    centered_text(
        page,
        pymupdf.Rect(0, 90, page.rect.width, 106),
        "ENHANCED ATTRIBUTES",
        HEADING_FONT,
        13,
    )

    group_width = (
        RIGHT - 2 - LEFT - COLUMN_GAP * 2 * (len(ENHANCED_GROUPS) - 1)
    ) / len(ENHANCED_GROUPS)

    for index, (facet, attributes) in enumerate(ENHANCED_GROUPS):
        x0 = LEFT + index * (group_width + COLUMN_GAP * 2)
        centered_text(
            page,
            pymupdf.Rect(x0, 112, x0 + group_width, 124),
            facet,
            LABEL_FONT,
            9,
        )

        box_width = (group_width - COLUMN_GAP) / 2

        for position, attribute in enumerate(attributes):
            box_x0 = x0 + position * (box_width + COLUMN_GAP)
            box = pymupdf.Rect(box_x0, 128, box_x0 + box_width, 204)
            panel(page, box, notch=5)
            centered_text(
                page,
                pymupdf.Rect(box.x0, box.y0 + 7, box.x1, box.y0 + 17),
                attribute.upper(),
                BODY_FONT,
                8.5,
            )
            centered_text(
                page,
                pymupdf.Rect(box.x0, box.y0 + 17, box.x1, box.y0 + 26),
                "ENHANCED",
                BODY_FONT,
                6.5,
                TEXT_GRAY,
            )

            widget = add_text_widget(
                page,
                f"Enhanced {attribute}",
                f"Enhanced {attribute} bonus",
                pymupdf.Rect(box.x0 + 8, box.y0 + 30, box.x1 - 8, box.y1 - 8),
                ENHANCED_INPUT_FONT_SIZE,
            )
            # Center the entered number (PDF quadding: 1 = center).
            doc.xref_set_key(widget.xref, "Q", "1")


def draw_enhanced_rules(page):
    rules = pymupdf.Rect(LEFT, 224, RIGHT - 2, 290)
    panel(page, rules)

    middle = (rules.x0 + rules.x1) / 2
    page.draw_line(
        (middle, rules.y0 + 8),
        (middle, rules.y1 - 8),
        color=BLACK,
        width=0.5,
    )

    columns = [
        ("ENHANCED AFFECTS", ENHANCED_APPLIES, rules.x0 + 12, middle - 10),
        ("ENHANCED DOES NOT AFFECT", ENHANCED_EXCLUDES, middle + 10, rules.x1 - 12),
    ]

    for heading, text, x0, x1 in columns:
        page.insert_text(
            (x0, rules.y0 + 16),
            heading,
            fontname=LABEL_FONT,
            fontsize=8,
        )
        wrapped_text(
            page,
            pymupdf.Rect(x0, rules.y0 + 20, x1, rules.y1 - 3),
            text,
            BODY_FONT,
            8,
            TEXT_GRAY,
        )


def draw_traits_section(page):
    section = pymupdf.Rect(LEFT, 300, RIGHT - 2, 522)
    panel(page, section)
    centered_text(
        page,
        pymupdf.Rect(section.x0, section.y0 + 8, section.x1, section.y0 + 24),
        "TALENTS",
        HEADING_FONT,
        13,
    )

    columns = 2
    rows = (len(TRAITS) + 1) // columns
    pad = 12
    top = section.y0 + 30
    cell_width = (section.width - pad * 2 - COLUMN_GAP) / columns
    cell_height = (section.y1 - 8 - top) / rows

    for index, (label, field_name, effect) in enumerate(TRAITS):
        row, column = divmod(index, columns)
        x0 = section.x0 + pad + column * (cell_width + COLUMN_GAP)
        y0 = top + row * cell_height

        if row > 0:
            page.draw_line(
                (x0, y0),
                (x0 + cell_width, y0),
                color=TEXT_GRAY,
                width=0.4,
            )

        add_checkbox_widget(
            page,
            field_name,
            label,
            pymupdf.Rect(x0 + 2, y0 + 10, x0 + 18, y0 + 26),
        )
        page.insert_text(
            (x0 + 26, y0 + 21),
            label,
            fontname=LABEL_FONT,
            fontsize=11,
        )
        wrapped_text(
            page,
            pymupdf.Rect(x0 + 26, y0 + 26, x0 + cell_width, y0 + cell_height),
            effect,
            BODY_FONT,
            8.5,
            TEXT_GRAY,
        )


def draw_notes_section(page):
    notes = pymupdf.Rect(LEFT, 532, RIGHT - 2, 764)
    panel(page, notes)
    centered_text(
        page,
        pymupdf.Rect(notes.x0, notes.y0 + 8, notes.x1, notes.y0 + 24),
        "OTHER TRAITS & NOTES",
        HEADING_FONT,
        13,
    )

    pad = 10
    top = notes.y0 + 28
    bottom = notes.y1 - 8
    column_width = (
        notes.width - pad * 2 - COLUMN_GAP * (NOTES_COLUMNS - 1)
    ) / NOTES_COLUMNS

    for index, field_name in enumerate(NOTES_FIELDS):
        x0 = notes.x0 + pad + index * (column_width + COLUMN_GAP)

        # Divider centered in the gap before each later column.
        if index > 0:
            divider_x = x0 - COLUMN_GAP / 2
            page.draw_line(
                (divider_x, top),
                (divider_x, bottom),
                color=BLACK,
                width=0.5,
            )

        add_text_widget(
            page,
            field_name,
            f"Other traits and notes, column {index + 1}",
            pymupdf.Rect(x0, top, x0 + column_width, bottom),
            NOTES_INPUT_FONT_SIZE,
            flags=pymupdf.PDF_TX_FIELD_IS_MULTILINE,
        )


# -------------------------------------------------------------------
# Page assembly
# -------------------------------------------------------------------

def add_options_page(doc):
    """Append the character options page to the three-page sheet."""
    if len(doc) != 3:
        raise ValueError(
            f"Expected a three-page input PDF, but found {len(doc)} pages. "
            "This function is intended to append page 4."
        )

    existing_names = {
        widget.field_name
        for existing_page in doc
        for widget in existing_page.widgets()
    }
    duplicates = existing_names.intersection(
        ENHANCED_FIELDS + TRAIT_FIELDS + NOTES_FIELDS
    )

    if duplicates:
        raise ValueError(f"Duplicate PDF field names: {sorted(duplicates)}")

    # PyMuPDF cannot copy artwork from the document being edited.
    source_doc = pymupdf.open("pdf", doc.tobytes())

    page = doc.new_page(width=doc[0].rect.width, height=doc[0].rect.height)

    # Reuse the Radiant sheet's logo and footer. The logo is copied in
    # two parts so its lower tip is kept without the "Radiant Sheet" title.
    copy_artwork(page, source_doc, 2, pymupdf.Rect(14, 12, 230, 71))
    copy_artwork(page, source_doc, 2, pymupdf.Rect(14, 71, 60, 80))
    copy_artwork(page, source_doc, 2, pymupdf.Rect(100, 770, 512, 790))

    draw_header(page)
    draw_enhanced_section(doc, page)
    draw_enhanced_rules(page)
    draw_traits_section(page)
    draw_notes_section(page)

    source_doc.close()
