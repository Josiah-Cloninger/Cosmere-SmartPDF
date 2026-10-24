from pathlib import Path
import pymupdf

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT = PROJECT_DIR / "blur_test.pdf"
TARGET = "Character Name.Page 1"

with pymupdf.open(PROJECT_DIR / "original.pdf") as doc:
    target_xref = None

    for page in doc:
        for field in page.widgets():
            if field.field_name == TARGET:
                target_xref = field.xref
                break
        if target_xref is not None:
            break

    if target_xref is None:
        raise RuntimeError(f"Field not found: {TARGET}")

    script = 'app.alert("The Blur script is running.");'
    action = (
        "<< /S /JavaScript /JS "
        + pymupdf.get_pdf_str(script)
        + " >>"
    )

    # An existing additional-actions dictionary may be indirect.
    aa_type, aa_value = doc.xref_get_key(target_xref, "AA")

    if aa_type == "xref":
        aa_xref = int(aa_value.split()[0])
        doc.xref_set_key(aa_xref, "Bl", action)
    else:
        doc.xref_set_key(target_xref, "AA/Bl", action)

    doc.save(OUTPUT)

# Verify the action survived saving.
with pymupdf.open(OUTPUT) as doc:
    for page in doc:
        for field in page.widgets():
            if field.field_name == TARGET:
                aa_type, aa_value = doc.xref_get_key(field.xref, "AA")

                if aa_type == "xref":
                    aa_xref = int(aa_value.split()[0])
                    result = doc.xref_get_key(aa_xref, "Bl")
                else:
                    result = doc.xref_get_key(field.xref, "AA/Bl")

                print("Saved Blur action:", result)
                if result[0] == "null":
                    raise RuntimeError("Blur action was not saved.")

print("Created blur_test.pdf")
