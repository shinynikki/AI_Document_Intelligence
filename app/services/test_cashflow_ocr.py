from app.services.ocr_services import extract_text


file_path = (
    r"New Dataset\Cash Flows"
    r"\Consolidated Cash Flow Statement 2017.pdf"
)


result = extract_text(file_path)


print("\n========== CASH FLOW OCR ==========\n")

for page in result["pages"]:

    print(f"\n========== PAGE {page['page_number']} ==========\n")

    print(page["text"])