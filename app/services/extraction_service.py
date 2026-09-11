import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.schemas.document import InvoiceData
from app.services.ocr_services import extract_text
from app.services.financial_validation import (
    validate_invoice,
    get_overall_status
)


# =========================================================
# Load environment variables
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")


# =========================================================
# Create Gemini client
# =========================================================

client = genai.Client(
    api_key=api_key
)


def extract_invoice(image_path, ocr_text):
    """
    Extract structured invoice information using:

    1. The original invoice image
    2. OCR text from Tesseract
    3. Gemini for semantic extraction

    The image is the primary source for understanding
    the document layout and table structure.
    """

    prompt = f"""
You are extracting structured information from a financial invoice.

You have TWO sources of information:

1. The original invoice image.
   Use this to understand the visual layout, table rows,
   columns and relationships between values.

2. OCR text produced by Tesseract.
   Use this as searchable text to help read the document.

The original invoice image is the primary source for understanding
the table structure. The OCR text is supporting information.

IMPORTANT RULES:

1. Extract every identifiable product line from the invoice.

2. If the invoice contains numbered products such as
   1, 2, 3, 4, 5 and 6, create a separate line_item for each.

3. Do NOT combine different products into one line item.

4. Use the visual table layout to determine which quantity,
   rate and amount belong to each product row.

5. Separate quantity and unit.
   For example:
   "48 PCS" means quantity = 48 and unit = "PCS".

6. Extract the product description exactly or as close as
   possible to what is visible on the invoice.

7. Extract HSN/SAC when clearly visible.

8. Extract unit price/rate only when it can be confidently
   associated with that product row.

9. Extract the line amount only when it can be confidently
   associated with that product row.

10. If a value is unreadable or ambiguous, use null.
    NEVER guess.

11. Do not calculate missing values.

12. Extract the invoice number if clearly visible.

13. Extract the invoice date only when the document clearly
    identifies the date as the invoice date.

14. Extract seller and buyer/consignee information when visible.

15. Extract GSTIN, email, phone number and address when clearly
    visible.

16. Extract subtotal, taxable amount, tax amount and total amount
    only when their labels clearly identify them.

17. Extract CGST, SGST, IGST and their rates and amounts when
    clearly visible.

18. Extract payment information and bank details when visible.

19. Extract delivery notes and other document references when visible.

20. Do not use outside knowledge.

21. Do not invent missing information.

22. Add evidence text for important extracted values when possible.

23. If information is not present or cannot be read reliably,
    return null.

24. Return ONLY JSON matching the provided schema.

25. Treat the original image as the source of truth when OCR text
    contains obvious recognition errors.

26. Do not interpret corrupted OCR characters as valid numbers
    unless the value is clearly supported by the invoice image.

27. If a numeric value cannot be reliably associated with the
    correct table column or row, return null.

28. Do not assume that a value such as "99", "0.45", or similar
    OCR fragments represents a discount, amount, rate, or tax
    unless the visual table structure clearly confirms it.

29. If a line item's amount, discount, rate, or quantity is
    ambiguous, return null for that specific field rather than
    guessing.

30. Do not modify or mathematically reconstruct an unreadable
    value just because another value could be calculated from it.

31. Extract round_off only when it is explicitly shown or labeled
    on the document, such as "Round Off".

32. Do not calculate or infer round_off.

33. If round_off is not explicitly visible, return null.

Here is the OCR text:

---------------- OCR TEXT ----------------
{ocr_text}
-------------- END OCR TEXT --------------
"""

    # =========================================================
    # Read original invoice image
    # =========================================================

    with open(image_path, "rb") as file:
        image_bytes = file.read()

    # =========================================================
    # Create image input for Gemini
    # =========================================================

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/jpeg"
    )

    # =========================================================
    # Send request to Gemini
    # Retry only temporary 503 errors.
    # =========================================================

    for attempt in range(3):

        try:
            print(
                f"\nSending request to Gemini "
                f"(attempt {attempt + 1}/3)..."
            )

            response = client.models.generate_content(
                model=model,
                contents=[
                    image_part,
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=InvoiceData,
                ),
            )

            break

        except Exception as error:

            error_message = str(error)

            # Do not retry non-temporary errors.
            if "503" not in error_message:

                print("\nGemini request failed:")
                print(error_message)

                raise error

            # If this was the final attempt, raise the error.
            if attempt == 2:
                raise error

            print(
                "\nGemini is temporarily unavailable."
            )

            print(
                "Retrying in 5 seconds..."
            )

            time.sleep(5)

    # =========================================================
    # Validate Gemini response using Pydantic
    # =========================================================

    invoice = InvoiceData.model_validate_json(
        response.text
    )

    return invoice


# =========================================================
# Test extraction
# =========================================================

if __name__ == "__main__":

    file_path = (
        "New Dataset/Invoices/20251118_000612.jpg"
    )

    # ---------------------------------------------------------
    # Run OCR
    # ---------------------------------------------------------

    ocr_result = extract_text(
        file_path
    )

    ocr_text = "\n".join(
        page["text"]
        for page in ocr_result["pages"]
    )

    print(
        "\n========== OCR TEXT ==========\n"
    )

    print(ocr_text)

    print(
        "\n========== END OCR TEXT ==========\n"
    )

    # ---------------------------------------------------------
    # Extract invoice using Gemini
    # ---------------------------------------------------------

    result = extract_invoice(
        file_path,
        ocr_text
    )

    print(
        "\n========== EXTRACTED JSON ==========\n"
    )

    print(
        result.model_dump_json(
            indent=2
        )
    )

    # ---------------------------------------------------------
    # Run financial validation
    # ---------------------------------------------------------

    validations = validate_invoice(
        result
    )

    print(
        "\n========== VALIDATION RESULTS ==========\n"
    )

    for validation in validations:
        print(validation)

    # ---------------------------------------------------------
    # Calculate overall status
    # ---------------------------------------------------------

    overall_status = get_overall_status(
        validations
    )

    print(
        "\n========== OVERALL STATUS ==========\n"
    )

    print(overall_status)