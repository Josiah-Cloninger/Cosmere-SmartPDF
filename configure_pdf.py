from collections import Counter, defaultdict
from pathlib import Path
import re

import pymupdf

from add_options_page import add_options_page


# -------------------------------------------------------------------
# Project files
# -------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

INPUT = PROJECT_DIR / "original.pdf"
OUTPUT = PROJECT_DIR / "interactive.pdf"

# Set False if your input PDF already contains the options page.
ADD_OPTIONS_PAGE = True

# Converts names such as "Strength.Page 2" to the base name "Strength".
# Unsuffixed names such as "Has Hardy Trait" remain unchanged.
PAGE_SUFFIX = re.compile(r"\.Page \d+$")


# -------------------------------------------------------------------
# Existing synchronization and skill configuration
# -------------------------------------------------------------------

STATS = {
    "Speed",
    "Strength",
    "Intellect",
    "Willpower",
    "Presence",
    "Awareness",
}

# These names match rank-checkbox prefixes.
# Example: "Heavy Weaponry Rank 1".
SKILLS = {
    "Agility",
    "Athletics",
    "Heavy Weaponry",
    "Light Weaponry",
    "Stealth",
    "Thievery",
    "Crafting",
    "Deduction",
    "Discipline",
    "Intimidation",
    "Lore",
    "Medicine",
    "Deception",
    "Insight",
    "Leadership",
    "Perception",
    "Persuasion",
    "Survival",
}

# Preserve the original trigger choices.
SYNC_EVENT = "Bl"
SKILLS_EVENT = "Bl"
RANK_EVENT = "Bl"


# -------------------------------------------------------------------
# Derivative calculation rules
# -------------------------------------------------------------------
#
# field_base:
#   A list of field base names that trigger the JavaScript.
#   "Strength" matches Strength.Page 1, Strength.Page 2, etc.
#   "Has Hardy Trait" matches that exact unsuffixed field name.
#
# javascript:
#   An external JavaScript file in this project folder.
#
# event:
#   "V"  = Validate: an edited value is being committed.
#   "Bl" = Blur: the field loses focus, even without a value change.
#   "Fo" = Focus: the user enters the field.
#   "K"  = Keystroke: editing/commit events; requires special JS logic.
#   "U"  = Mouse Up: mouse release over the widget.
#
# To add another calculation:
#   1. Create its JavaScript file.
#   2. Add a rule below.
#   3. Rebuild the PDF.
#
# To change when a calculation runs:
#   Change the rule's event key, then rebuild.
#   Also adapt the JavaScript to that event's value semantics.
#
# Rules may overlap. For example, Strength triggers both its own
# derivatives and health. Scripts for the same field/event are joined
# in the order their rules appear below.
# -------------------------------------------------------------------

DERIVATIVE_RULES = [
    {
        "field_base": ["Strength"],
        "javascript": "calculate_str_derivatives.js",
        "event": "V",
    },
    {
        "field_base": ["Speed"],
        "javascript": "calculate_spd_derivatives.js",
        "event": "V",
    },
    {
        "field_base": ["Intellect"],
        "javascript": "calculate_int_derivatives.js",
        "event": "V",
    },
    {
        "field_base": ["Willpower"],
        "javascript": "calculate_wil_derivatives.js",
        "event": "V",
    },
    {
        "field_base": ["Awareness"],
        "javascript": "calculate_awa_derivatives.js",
        "event": "V",
    },
    {
        "field_base": ["Presence"],
        "javascript": "calculate_pre_derivatives.js",
        "event": "V",
    },
    {
        "field_base": ["Level", "Strength"],
        "javascript": "calculate_health.js",
        "event": "V",
    },
    {
        "field_base": ["Has Hardy Trait"],
        "javascript": "calculate_health.js",
        "event": "Bl",
    },
]


EVENT_NAMES = {
    "V": "Validate",
    "Bl": "Blur",
    "Fo": "Focus",
    "K": "Keystroke",
    "U": "Mouse Up",
}


# -------------------------------------------------------------------
# File and configuration helpers
# -------------------------------------------------------------------

def load_javascript(filename):
    """Load JavaScript from a separate file."""
    path = PROJECT_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(
            f"Missing JavaScript file: {path}\n"
            "Create the file or correct its name in the configuration."
        )

    source = path.read_text(encoding="utf-8")

    if not source.strip():
        raise ValueError(f"JavaScript file is empty: {path}")

    return source


def load_derivative_rules():
    """Validate rules and load their external JavaScript."""
    loaded_rules = []
    source_cache = {}

    for index, rule in enumerate(DERIVATIVE_RULES, start=1):
        field_names = rule.get("field_base")

        # Accept both the current list format and older single strings.
        if isinstance(field_names, str):
            field_names = [field_names]

        if (
            not isinstance(field_names, list)
            or not field_names
            or any(
                not isinstance(name, str) or not name.strip()
                for name in field_names
            )
        ):
            raise ValueError(
                f"Derivative rule {index}: field_base must be "
                "a nonempty string or list of nonempty strings."
            )

        event_key = rule.get("event")

        if event_key not in EVENT_NAMES:
            raise ValueError(
                f"Derivative rule {index}: unsupported event "
                f"{event_key!r}. Choose from {list(EVENT_NAMES)}."
            )

        filename = rule.get("javascript")

        if not isinstance(filename, str) or not filename.strip():
            raise ValueError(
                f"Derivative rule {index}: javascript must "
                "name an external JavaScript file."
            )

        if filename not in source_cache:
            source_cache[filename] = load_javascript(filename)

        loaded_rules.append({
            "field_base": list(dict.fromkeys(field_names)),
            "javascript": filename,
            "event": event_key,
            "source": source_cache[filename],
        })

    return loaded_rules


# -------------------------------------------------------------------
# PDF action helpers
# -------------------------------------------------------------------

def action_location(doc, widget_xref, event_key):
    """Find the dictionary location for a widget's additional action."""
    aa_type, aa_value = doc.xref_get_key(widget_xref, "AA")

    if aa_type == "xref":
        return int(aa_value.split()[0]), event_key

    return widget_xref, f"AA/{event_key}"


def set_action(doc, widget_xref, event_key, javascript):
    """Assign JavaScript to one widget/event combination."""
    action = (
        "<< /S /JavaScript /JS "
        + pymupdf.get_pdf_str(javascript)
        + " >>"
    )

    xref, key = action_location(doc, widget_xref, event_key)
    doc.xref_set_key(xref, key, action)


def add_script(event_scripts, event_key, javascript):
    """Queue scripts instead of overwriting earlier rules."""
    event_scripts[event_key].append(javascript)


# -------------------------------------------------------------------
# PDF configuration
# -------------------------------------------------------------------

def main():
    if not INPUT.is_file():
        raise FileNotFoundError(f"Input PDF not found: {INPUT}")

    sync_js = load_javascript("sync_fields.js")
    skills_js = load_javascript("calculate_skills.js")
    derivative_rules = load_derivative_rules()

    assigned_actions = []

    with pymupdf.open(INPUT) as doc:
        # Add the options page before collecting widgets so its
        # checkbox/text fields can receive derivative actions too.
        if ADD_OPTIONS_PAGE:
            add_options_page(doc)

        groups = defaultdict(set)
        fields = []

        for page_number, page in enumerate(doc):
            for field in page.widgets():
                name = field.field_name or ""
                base_name = PAGE_SUFFIX.sub("", name)

                fields.append(
                    (field.xref, name, base_name, field.field_type)
                )

                if (
                    field.field_type == pymupdf.PDF_WIDGET_TYPE_TEXT
                    and PAGE_SUFFIX.search(name)
                ):
                    groups[base_name].add(page_number)

        # Synchronize only page-suffixed text fields that occur
        # on more than one page.
        linked_names = {
            name
            for name, pages in groups.items()
            if len(pages) > 1
        }

        supported_types = {
            pymupdf.PDF_WIDGET_TYPE_TEXT,
            pymupdf.PDF_WIDGET_TYPE_CHECKBOX,
        }

        # This includes both page-suffixed text fields and
        # unsuffixed options such as "Has Hardy Trait".
        available_field_bases = {
            base_name
            for _, _, base_name, field_type in fields
            if field_type in supported_types
        }

        for rule in derivative_rules:
            missing = (
                set(rule["field_base"]) - available_field_bases
            )

            if missing:
                raise RuntimeError(
                    f"Trigger fields missing for "
                    f"{rule['javascript']}:\n"
                    + "\n".join(sorted(missing))
                    + "\n\nAvailable text/checkbox base names:\n"
                    + "\n".join(sorted(available_field_bases))
                )

        for xref, name, base_name, field_type in fields:
            event_scripts = defaultdict(list)

            if field_type == pymupdf.PDF_WIDGET_TYPE_TEXT:
                has_page_suffix = bool(PAGE_SUFFIX.search(name))

                # Queue synchronization before skill calculations.
                if has_page_suffix and base_name in linked_names:
                    add_script(event_scripts, SYNC_EVENT, sync_js)

                if has_page_suffix and base_name in STATS:
                    add_script(event_scripts, SKILLS_EVENT, skills_js)

            elif field_type == pymupdf.PDF_WIDGET_TYPE_CHECKBOX:
                match = re.fullmatch(r"(.+) Rank ([1-5])", name)

                if match and match.group(1) in SKILLS:
                    add_script(event_scripts, RANK_EVENT, skills_js)

            # Derivative matching is outside the text-field branch:
            # it applies to both text inputs and checkboxes.
            if field_type in supported_types:
                for rule in derivative_rules:
                    if base_name in rule["field_base"]:
                        add_script(
                            event_scripts,
                            rule["event"],
                            rule["source"],
                        )

            # One action per event, containing all queued scripts.
            # This prevents Strength's health rule from replacing
            # Strength's other derivative calculations.
            for event_key, scripts in event_scripts.items():
                combined_js = "\n;\n".join(scripts)

                set_action(
                    doc,
                    xref,
                    event_key,
                    combined_js,
                )

                assigned_actions.append(
                    (xref, event_key, name)
                )

        # The input is always original.pdf. It is not overwritten.
        doc.save(OUTPUT)

    # Verify action entries were saved.
    # This does not execute JavaScript or test viewer compatibility.
    with pymupdf.open(OUTPUT) as doc:
        for widget_xref, event_key, name in assigned_actions:
            xref, key = action_location(
                doc,
                widget_xref,
                event_key,
            )

            action_type, _ = doc.xref_get_key(xref, key)

            if action_type == "null":
                raise RuntimeError(
                    f"Missing saved action: {name}, "
                    f"event {event_key}"
                )

    counts = Counter(
        event_key
        for _, event_key, _ in assigned_actions
    )

    for event_key, count in sorted(counts.items()):
        print(
            f"Verified {count} "
            f"{EVENT_NAMES[event_key]} actions."
        )

    print(f"Saved {OUTPUT.name}.")
    print(f"{INPUT.name} was not changed.")


if __name__ == "__main__":
    main()