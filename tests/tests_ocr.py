from app.services.ocr_services import extract_text


file_path =  "New Dataset/Cash Flows/Consolidated Cash Flow Statement 2017.pdf"

result = extract_text(file_path)

for page in result["pages"]:
    print("\n")
    print("PAGE", page["page_number"])

    print(page["text"])
