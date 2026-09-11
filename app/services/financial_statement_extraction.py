import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.schemas.document import BalanceSheetData
from app.services.ocr_services import extract_text
from app.services.financial_validation import (
    validate_balance_sheet,
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


# =========================================================
# Balance Sheet Extraction
# =========================================================

def extract_balance_sheet(pdf_path, ocr_text):
    """
    Extract structured Balance Sheet information.

    The original PDF is used as the primary source.
    OCR text is provided as supporting information.
    """

    prompt = f"""
You are extracting structured information from a Balance Sheet.

The document may contain multiple financial periods.

IMPORTANT RULES:

1. Extract the statement title exactly as visible.

2. Extract the unit exactly as visibly written on the document.

3. Do NOT infer or add a currency symbol.

4. For example, if the document visibly says:
   "= in '000"
   then return the unit as:
   "= in '000"

5. Do not change the unit based on outside knowledge.

6. Extract every visible financial period.

7. Preserve the period labels exactly as shown.

8. Extract every meaningful financial line item from the statement.

9. Do not omit line items simply because they are not part
   of the main accounting equation.

10. Preserve the original line-item label as closely as possible.

11. Extract the values for each period and associate each value
    with the correct period.

12. Do not swap values between periods.

13. Preserve negative values when they are explicitly shown.

14. Do not calculate missing values.

15. Do not infer values from other rows.

16. If a value is unreadable or ambiguous, return null.

17. Do not invent a financial value.

18. Separate the statement into:
    - liabilities
    - assets
    - other_items

19. Put capital, reserves, minority interest, deposits,
    borrowings and other liability-side items under
    liabilities when they appear under the
    capital and liabilities section.

20. Put cash, balances with banks, investments, advances,
    fixed assets, other assets and similar items under
    assets when they appear under the assets section.

21. Put items such as contingent liabilities and bills for
    collection under other_items when they appear separately
    from the main assets and liabilities sections.

22. Preserve rows labelled "Total".

23. Do not create totals yourself.

24. If a row is explicitly labelled as a total on the document,
    extract its reported value.

25. Add evidence text for important extracted values when possible.

26. Include the page number in evidence when possible.

27. Use the original document layout to determine which number
    belongs to which row and period.

28. OCR text may contain recognition errors.

29. Treat the original document as the primary source when
    OCR text and the document disagree.

30. Do not use outside knowledge.

31. Do not mathematically reconstruct unreadable values.

32. Do not change a value because another value could be
    calculated from it.

33. Return ONLY JSON matching the provided schema.

OCR TEXT:

---------------- OCR TEXT ----------------

{ocr_text}

-------------- END OCR TEXT --------------
"""

    # =========================================================
    # Read PDF
    # =========================================================

    try:

        with open(pdf_path, "rb") as file:
            pdf_bytes = file.read()

    except FileNotFoundError:

        raise FileNotFoundError(
            f"Balance Sheet file not found: {pdf_path}"
        )

    except Exception as error:

        raise ValueError(
            f"Could not read Balance Sheet file: {error}"
        )


    # =========================================================
    # Create PDF input for Gemini
    # =========================================================

    pdf_part = types.Part.from_bytes(
        data=pdf_bytes,
        mime_type="application/pdf"
    )


    # =========================================================
    # Send request to Gemini
    # =========================================================

    response = None

    for attempt in range(3):

        try:

            print(
                f"\nSending request to Gemini "
                f"(attempt {attempt + 1}/3)..."
            )

            response = client.models.generate_content(
                model=model,
                contents=[
                    pdf_part,
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=BalanceSheetData
                )
            )

            break

        except Exception as error:

            error_message = str(error)

            # -------------------------------------------------
            # Retry temporary Gemini errors
            # -------------------------------------------------

            if "503" not in error_message:

                print(
                    "\nGemini request failed:"
                )

                print(error_message)

                raise error

            if attempt == 2:

                print(
                    "\nGemini failed after 3 attempts."
                )

                raise error

            print(
                "\nGemini is temporarily unavailable."
            )

            print(
                "Retrying in 5 seconds..."
            )

            time.sleep(5)


    # =========================================================
    # Validate Gemini response
    # =========================================================

    if response is None:

        raise RuntimeError(
            "Gemini did not return a response."
        )

    if not response.text:

        raise ValueError(
            "Gemini returned an empty response."
        )

    try:

        balance_sheet = (
            BalanceSheetData.model_validate_json(
                response.text
            )
        )

    except Exception as error:

        print(
            "\nGemini returned invalid structured data:"
        )

        print(response.text)

        raise ValueError(
            f"Could not validate Gemini response: {error}"
        )


    return balance_sheet


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    file_path = (
        "New Dataset/Balance Sheet/"
        "Consolidated Balance Sheet 2017.pdf"
    )


    # =========================================================
    # OCR
    # =========================================================

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


    # =========================================================
    # Gemini Extraction
    # =========================================================

    result = extract_balance_sheet(
        file_path,
        ocr_text
    )


    print(
        "\n========== BALANCE SHEET JSON ==========\n"
    )

    print(
        result.model_dump_json(
            indent=2
        )
    )


    # =========================================================
    # Financial Validation
    # =========================================================

    validations = validate_balance_sheet(
        result
    )


    print(
        "\n========== VALIDATION RESULTS ==========\n"
    )

    for validation in validations:

        print(validation)


    # =========================================================
    # Overall Status
    # =========================================================

    overall_status = get_overall_status(
        validations
    )


    print(
        "\n========== OVERALL STATUS ==========\n"
    )

    print(overall_status)