import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.schemas.document import ProfitLossData
from app.services.ocr_services import extract_text


# =========================================================
# Gemini Setup
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")

client = genai.Client(
    api_key=api_key
)


# =========================================================
# Profit & Loss Extraction
# =========================================================

def extract_profit_loss(pdf_path, ocr_text):
    """
    Extract structured information from a Profit & Loss
    statement using Gemini.

    The original PDF is provided to Gemini together with
    OCR text.

    The PDF is treated as the primary source when OCR
    contains errors.
    """

    prompt = f"""
You are extracting structured information from a
Profit & Loss statement.

The document may contain multiple financial periods.

IMPORTANT RULES:

1. Extract the statement title exactly as visible.

2. Extract the unit exactly as visibly written on the
   document.

3. Do NOT infer or add a currency symbol.

4. For example, if the document visibly says:
   "= in '000"
   then return the unit as:
   "= in '000"

5. Do not change the unit based on outside knowledge.

6. Extract every visible financial period.

7. Preserve the period labels exactly as shown.

8. Extract every meaningful financial line item from
   the statement.

9. Do not omit line items simply because they are not
   required for the main financial validation.

10. Preserve the original line-item label as closely
    as possible.

11. Extract the values for each period and associate
    each value with the correct period.

12. Do not swap values between periods.

13. Preserve negative values when they are explicitly
    shown.

14. Do not calculate missing values.

15. Do not infer values from other rows.

16. If a value is unreadable or ambiguous, return null.

17. Do not invent a financial value.

18. Separate the statement into these sections when
    they are present:

    - income
    - expenditure
    - profit
    - appropriations
    - earnings_per_share
    - other_items

19. Put rows appearing under the INCOME section into
    income.

20. Put rows appearing under the EXPENDITURE section
    into expenditure.

21. Put rows appearing under the PROFIT section into
    profit.

22. Put rows appearing under the APPROPRIATIONS section
    into appropriations.

23. Put Basic and Diluted earnings per share and similar
    EPS rows into earnings_per_share.

24. Put meaningful financial rows that do not clearly
    belong to the above sections into other_items.

25. Preserve rows labelled "Total".

26. Do not create totals yourself.

27. If a row is explicitly labelled as a total on the
    document, extract its reported value.

28. Preserve labels such as:

    "Net profit for the year"
    "Less: Minority interest"
    "Add: Share in profits of associates"

    exactly or as closely as possible.

29. Preserve the meaning of "Less" and "Add" in the
    original label.

30. Do not change the sign of a value merely because
    the row contains the word "Less" or "Add".

31. If the document explicitly shows a negative value,
    preserve that negative value.

32. If the document shows a dash such as "-",
    treat the value as missing and return null.

33. Extract all visible rows under APPROPRIATIONS.

34. Extract EPS values exactly as shown, including
    Basic and Diluted values.

35. Add evidence text for important extracted values
    when possible.

36. Include the page number in evidence when possible.

37. Use the original document layout to determine which
    number belongs to which row and period.

38. OCR text may contain recognition errors.

39. Treat the original PDF/document as the primary source
    when OCR text and the document disagree.

40. Do not use outside knowledge.

41. Do not mathematically reconstruct unreadable values.

42. Do not change a value because another value could be
    calculated from it.

43. Missing or unreadable values must be null.

44. Return ONLY JSON matching the provided schema.

OCR TEXT:
---------------- OCR TEXT ----------------
{ocr_text}
-------------- END OCR TEXT --------------
"""

    # =====================================================
    # Read PDF
    # =====================================================

    try:

        with open(pdf_path, "rb") as file:
            pdf_bytes = file.read()

    except FileNotFoundError:

        raise FileNotFoundError(
            f"Profit & Loss file not found: {pdf_path}"
        )

    except Exception as error:

        raise ValueError(
            f"Could not read Profit & Loss file: {error}"
        )

    # =====================================================
    # Create Gemini PDF Input
    # =====================================================

    pdf_part = types.Part.from_bytes(
        data=pdf_bytes,
        mime_type="application/pdf"
    )

    response = None

    # =====================================================
    # Gemini Request
    # =====================================================

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
                    response_schema=ProfitLossData
                )
            )

            break

        except Exception as error:

            error_message = str(error)

            # -------------------------------------------------
            # 429 = Quota / Rate Limit
            # -------------------------------------------------

            if "429" in error_message:

                print(
                    "\nGemini API quota has been exceeded."
                )

                print(
                    "No additional retry will be attempted."
                )

                print(
                    "The extraction cannot continue until "
                    "the Gemini quota becomes available."
                )

                raise error

            # -------------------------------------------------
            # 503 = Temporary Gemini Service Error
            # -------------------------------------------------

            if "503" not in error_message:

                print(
                    "\nGemini request failed:"
                )

                print(error_message)

                raise error

            # -------------------------------------------------
            # Retry temporary 503 errors
            # -------------------------------------------------

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

    # =====================================================
    # Check Response
    # =====================================================

    if response is None:

        raise RuntimeError(
            "Gemini did not return a response."
        )

    if not response.text:

        raise ValueError(
            "Gemini returned an empty response."
        )

    # =====================================================
    # Validate Gemini Response
    # =====================================================

    try:

        profit_loss = (
            ProfitLossData.model_validate_json(
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

    return profit_loss


# =========================================================
# Direct Test
# =========================================================

if __name__ == "__main__":

    file_path = (
        "New Dataset/Profit & Loss/"
        "Consolidated Profit & Loss 2017.pdf"
    )

    # =====================================================
    # OCR
    # =====================================================

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

    # =====================================================
    # Gemini Extraction
    # =====================================================

    result = extract_profit_loss(
        file_path,
        ocr_text
    )

    # =====================================================
    # Print Extracted JSON
    # =====================================================

    print(
        "\n========== PROFIT & LOSS JSON ==========\n"
    )

    print(
        result.model_dump_json(
            indent=2
        )
    )

    # =====================================================
    # Financial Validation
    # =====================================================

    from app.services.financial_validation import (
        validate_profit_loss,
        get_overall_status
    )

    validations = validate_profit_loss(
        result
    )

    print(
        "\n========== VALIDATION RESULTS ==========\n"
    )

    for validation in validations:

        print(validation)

    # =====================================================
    # Overall Status
    # =====================================================

    overall_status = get_overall_status(
        validations
    )

    print(
        "\n========== OVERALL STATUS ==========\n"
    )

    print(overall_status)