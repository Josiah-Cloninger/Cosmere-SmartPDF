import pymupdf

with pymupdf.open("smart_character_sheet.pdf") as doc:
    for page_number, page in enumerate(doc, start=1):
        for field in page.widgets():
            print(
                f"Page {page_number} | "
                f"Name: {field.field_name!r} | "
                f"Type: {field.field_type_string} | "
                f"Value: {field.field_value!r}"
            )
