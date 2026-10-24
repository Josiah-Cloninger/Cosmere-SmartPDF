# Interactive Character Sheet

Python and JavaScript tools for adding field synchronization,
skill calculations, and derived statistics to a PDF character sheet.

## Files

- `configure_pdf.py`: Builds the interactive PDF and attaches field events.
- `sync_fields.js`: Synchronizes repeated fields.
- `calculate_skills.js`: Calculates skill totals.
- `calculate_strength_derivatives.js`: Calculates Strength-derived values.
- `original.pdf`: Input PDF.
- `interactive.pdf`: Generated output; not tracked in Git.

## Setup

Install Python and the project dependencies:

```bash
python -m pip install -r requirements.txt
```

Place the required `original.pdf` in the project folder if it is not
included in this repository.

## Build

```bash
python configure_pdf.py
```

Open the generated `interactive.pdf` in a PDF viewer that supports
the JavaScript features used by the project.

## Editing calculations

Keep calculation logic in separate `.js` files.

Configure which fields and events trigger derivative calculations
in `DERIVATIVE_RULES` inside `configure_pdf.py`.

After changing Python or JavaScript files, rerun the build command.