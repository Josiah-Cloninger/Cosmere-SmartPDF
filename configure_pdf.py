from collections import Counter, defaultdict
from pathlib import Path
import re

import pymupdf


# -------------------------------------------------------------------
# Files and field naming
# -------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

INPUT = PROJECT_DIR / "original.pdf"
OUTPUT = PROJECT_DIR / "smart_character_sheet.pdf"

# Matches suffixes such as ".Page 1" and ".Page 2".
# For example, "Strength.Page 2" has base name "Strength".
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

# These are the prefixes used by the rank checkbox field names.
# For example: "Heavy Weaponry Rank 1".
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

# Preserve the original script's event choices.
SYNC_EVENT = "Bl"
SKILLS_EVENT = "Bl"
RANK_EVENT = "Bl"


# -------------------------------------------------------------------
# Derivative calculation rules
# -------------------------------------------------------------------
#
# Each rule connects:
#   field_base -> the field that triggers the calculation
#   javascript -> the external JavaScript file to run
#   event      -> when that JavaScript runs
#
# Common event keys:
#
#   "V"  = Validate:
#          Runs when an edited value is being committed.
#          Use event.value in JavaScript to read the proposed new value.
#
#   "Bl" = Blur:
#          Runs when the field loses focus, even without a value change.
#          Read event.target.valueAsString for the field's current value.
#
#   "Fo" = Focus:
#          Runs when the user enters the field.
#          This is usually not appropriate for recalculating edited values.
#
#   "K"  = Keystroke:
#          Runs during editing and also during commitment.
#          This requires different JavaScript logic. Do not switch an
#          ordinary Validate script to "K" without adapting that script.
#
# To change a trigger, change the rule's "event" below, then rebuild.
# Also adapt the JavaScript if the new event exposes values differently.
#
# IMPORTANT:
# Changing a rule here removes the old generated trigger on the next
# build because this script always starts from original.pdf, not from
# the previously generated smart_character_sheet.pdf.
# Actions already present in original.pdf are otherwise retained unless
# this script writes a replacement for the same field/event.
# -------------------------------------------------------------------

DERIVATIVE_RULES = [
    {
        "field_base": "Strength",
        "javascript": "calculate_str_derivatives.js",
        "event": "V",
    },
    {
        "field_base": "Speed",
        "javascript": "calculate_spd_derivatives.js",
        "event": "V",
    },
    {
        "field_base": "Intellect",
        "javascript": "calculate_int_derivatives.js",
        "event": "V",
    },
    {
        "field_base": "Willpower",
        "javascript": "calculate_wil_derivatives.js",
        "event": "V",
    },
        {
        "field_base": "Awareness",
        "javascript": "calculate_awa_derivatives.js",
        "event": "V",
    },
    {
        "field_base": "Presence",
        "javascript": "calculate_pre_derivatives.js",
        "event": "V",
    },
    {
        "field_base": "Level",
        "javascript": "calculate_lvl_derivatives.js",
        "event": "V",
    },


    # TO ADD SPEED DERIVATIVES:
    #
    # 1. Create configure_speed_derivatives.js in this same folder.
    # 2. Put the Speed-derived calculations in that JavaScript file.
    # 3. Uncomment the following rule.
    # 4. Rerun: python configure_pdf.py
    #
    # With event "V", the Speed JavaScript should read:
    #     var speed = Number(event.value);
    #
    # The filename is your choice. If you instead call the file
    # calculate_speed_derivatives.js, use that filename below.
    #
    # {
    #     "field_base": "Speed",
    #     "javascript": "configure_speed_derivatives.js",
    #     "event": "V",
    # },
]


EVENT_NAMES = {
    "V": "Validate",
    "Bl": "Blur",
    "Fo": "Focus",
    "K": "Keystroke",
    "U": "Mouse Up",
}


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def load_javascript(filename):
    """Read an external JavaScript file from the project folder."""
    path = PROJECT_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(
            f"Missing JavaScript file: {path}\n"
            "Create the file or correct its configured filename."
        )

    return path.read_text(encoding="utf-8")


def action_location(doc, widget_xref, event_key):
    """Find where to write an additional action in the PDF."""
    aa_type, aa_value = doc.xref_get_key(widget_xref, "AA")

    if aa_type == "xref":
        return int(aa_value.split()[0]), event_key

    return widget_xref, f"AA/{event_key}"


def set_action(doc, widget_xref, event_key, javascript):
    """Write a JavaScript action for one widget and event."""
    action = (
        "<< /S /JavaScript /JS "
        + pymupdf.get_pdf_str(javascript)
        + " >>"
    )

    xref, key = action_location(doc, widget_xref, event_key)
    doc.xref_set_key(xref, key, action)


def add_script(event_scripts, event_key, javascript):
    """Queue scripts so the same event is written only once."""
    event_scripts[event_key].append(javascript)


# -------------------------------------------------------------------
# Build the output PDF
# -------------------------------------------------------------------

def main():
    if not INPUT.is_file():
        raise FileNotFoundError(f"Input PDF not found: {INPUT}")

    sync_js = load_javascript("sync_fields.js")
    skills_js = load_javascript("calculate_skills.js")

    # Load only enabled derivative rules.
    derivative_rules = []

    for rule in DERIVATIVE_RULES:
        if rule["event"] not in EVENT_NAMES:
            raise ValueError(
                f"Unsupported event key in derivative rule: "
                f"{rule['event']!r}"
            )

        derivative_rules.append({
            **rule,
            "source": load_javascript(rule["javascript"]),
        })

    actions = []

    with pymupdf.open(INPUT) as doc:
        groups = defaultdict(set)
        fields = []

        # Collect widgets before editing their actions.
        for page_number, page in enumerate(doc):
            for field in page.widgets():
                name = field.field_name
                base_name = PAGE_SUFFIX.sub("", name)

                fields.append(
                    (field.xref, name, base_name, field.field_type)
                )

                if (
                    field.field_type == pymupdf.PDF_WIDGET_TYPE_TEXT
                    and PAGE_SUFFIX.search(name)
                ):
                    groups[base_name].add(page_number)

        linked_names = {
            name
            for name, pages in groups.items()
            if len(pages) > 1
        }

        # Catch a configured trigger field that does not exist.
        # Derivative rules target page-suffixed text fields, matching
        # the existing stat-field naming convention.
        available_stat_bases = {
            base_name
            for _, name, base_name, field_type in fields
            if (
                field_type == pymupdf.PDF_WIDGET_TYPE_TEXT
                and PAGE_SUFFIX.search(name)
            )
        }

        for rule in derivative_rules:
            if rule["field_base"] not in available_stat_bases:
                raise RuntimeError(
                    "No page-suffixed text field found for "
                    f"{rule['field_base']!r}.\n"
                    "Check the rule's field_base and your PDF field names."
                )

        for xref, name, base_name, field_type in fields:
            # Multiple scripts may share an event. Queue them together
            # instead of allowing one set_action() call to overwrite another.
            event_scripts = defaultdict(list)

            if field_type == pymupdf.PDF_WIDGET_TYPE_TEXT:
                has_page_suffix = bool(PAGE_SUFFIX.search(name))

                # Synchronization is queued before skill calculations.
                # When both use Blur, Page 1 is synchronized first.
                if has_page_suffix and base_name in linked_names:
                    add_script(event_scripts, SYNC_EVENT, sync_js)

                if has_page_suffix and base_name in STATS:
                    add_script(event_scripts, SKILLS_EVENT, skills_js)

                # Add derivatives only to their configured source field.
                if has_page_suffix:
                    for rule in derivative_rules:
                        if base_name == rule["field_base"]:
                            add_script(
                                event_scripts,
                                rule["event"],
                                rule["source"],
                            )

            elif field_type == pymupdf.PDF_WIDGET_TYPE_CHECKBOX:
                match = re.fullmatch(r"(.+) Rank ([1-5])", name)

                if match and match.group(1) in SKILLS:
                    add_script(event_scripts, RANK_EVENT, skills_js)

            # Scripts sharing an event run in queue order.
            # If a derivative uses Blur, it therefore runs after the
            # synchronization and skill scripts queued above.
            for event_key, scripts in event_scripts.items():
                set_action(
                    doc,
                    xref,
                    event_key,
                    "\n;\n".join(scripts),
                )
                actions.append((xref, event_key, name))

        doc.save(OUTPUT)

    # Reopen the generated PDF and check that each assigned action exists.
    # This checks saved action entries, not JavaScript runtime behavior.
    with pymupdf.open(OUTPUT) as doc:
        for widget_xref, event_key, name in actions:
            xref, key = action_location(
                doc,
                widget_xref,
                event_key,
            )
            action_type, _ = doc.xref_get_key(xref, key)

            if action_type == "null":
                raise RuntimeError(
                    f"Missing saved action: {name}, event {event_key}"
                )

    counts = Counter(event for _, event, _ in actions)

    for event_key, count in sorted(counts.items()):
        label = EVENT_NAMES.get(event_key, event_key)
        print(f"Verified {count} {label} actions.")

    print("Saved smart_character_sheet.pdf; original.pdf was not changed.")


if __name__ == "__main__":
    main()
