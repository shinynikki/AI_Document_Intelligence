# =========================================================
# Cash Flow Extraction Service
# =========================================================
#
# Extracts structured Cash Flow Statement data from a PDF
# using Gemini.
#
# The original PDF is the primary source of truth.
# OCR text is supplied only as supporting information.
# =========================================================


import os
import time
from pathlib import Path


from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError


from app.schemas.document import CashFlowData
from app.services.ocr_services import extract_text


# =========================================================
# Configuration
# =========================================================


load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


MODEL_NAME = (
    os.getenv("GEMINI_MODEL")
    or "gemini-3.6-flash"
)


if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# Extraction Prompt
# =========================================================


EXTRACTION_PROMPT = """
You are extracting structured financial information from a
Cash Flow Statement PDF.

The document type has already been identified as:

Cash Flow Statement.

Your task is to extract the information exactly as reported
in the document and return JSON matching the CashFlowData schema.

=========================================================
PRIMARY SOURCE OF TRUTH
=========================================================

1. Use the original PDF as the primary source of truth.

2. Use OCR text only as supporting information.

3. If OCR text conflicts with a clearly visible value or label
   in the PDF, prefer the PDF.

4. Do not invent, calculate, estimate, or infer values.

5. Extract only information that is visibly reported.

6. If a value is missing, unreadable, or represented by a dash,
   return null where the schema allows null.

=========================================================
NUMBERS
=========================================================

1. Preserve every reported number exactly in meaning.

2. Numbers inside parentheses are negative.

   Example:
   (33,898,658) -> -33898658

3. Do not change negative values into positive values.

4. Do not accidentally move a value to another period.

5. Do not calculate missing totals.

6. Do not use arithmetic to replace a missing reported value.

=========================================================
LABELS
=========================================================

1. Preserve the exact visible financial line-item labels as much
   as possible.

2. Do not rename a line item simply to match an example label.

3. Keep separate line items separate.

4. Do not combine multiple rows into one row.

5. Extract every meaningful financial line item.

6. Include adjustment rows, even when their values are negative.

7. Section headings alone are not line items unless they have
   an actual reported financial value.

=========================================================
PERIODS
=========================================================

1. Extract every financial period shown in the statement.

2. Preserve the original period names where possible.

3. Keep each value associated with its correct period.

4. Do not assume that every row has values for every period.

5. If a row has no value for a period, use null.

=========================================================
UNITS AND CURRENCY
=========================================================

1. Extract the unit exactly as shown in the document.

2. Preserve the currency if visible.

3. Do not infer a currency or unit that is not visible.

=========================================================
SECTION CLASSIFICATION
=========================================================

Place each line item into exactly one appropriate section.

---------------------------------------------------------
operating_activities
---------------------------------------------------------

Include line items belonging to cash flows from operating
activities.

Examples:

- Profit before tax
- Profit before taxation
- Depreciation
- Finance costs
- Interest expense
- Adjustments for non-cash items
- Working capital changes
- Changes in receivables
- Changes in inventories
- Changes in payables
- Taxes paid
- Net cash flow from operating activities
- Net cash flow used in operating activities
- Net cash from operating activities

---------------------------------------------------------
investing_activities
---------------------------------------------------------

Include line items belonging to cash flows from investing
activities.

Examples:

- Purchase of property, plant and equipment
- Purchase of fixed assets
- Proceeds from sale of fixed assets
- Purchase of investments
- Sale of investments
- Acquisitions
- Other investing activities
- Net cash flow from investing activities
- Net cash flow used in investing activities
- Net cash from investing activities
- Net cash used in investing activities

---------------------------------------------------------
financing_activities
---------------------------------------------------------

Include line items belonging to cash flows from financing
activities.

Examples:

- Proceeds from borrowings
- Repayment of borrowings
- Debt redemption
- Dividends paid
- Dividend tax
- Share capital changes
- Other financing activities
- Net cash flow from financing activities
- Net cash flow used in financing activities
- Net cash generated from financing activities
- Net cash from financing activities

---------------------------------------------------------
other_items
---------------------------------------------------------

Include separately reported cash-related adjustments that do
not belong directly to operating, investing, or financing
activities.

Examples:

- Effect of exchange fluctuation on translation reserve
- Effect of exchange rate changes
- Cash and cash equivalents on amalgamation
- Other separately reported cash adjustments

Do not place ordinary operating, investing, or financing rows
in this section.

---------------------------------------------------------
reconciliation
---------------------------------------------------------

Include only the final cash reconciliation rows.

Examples:

- Net increase in cash and cash equivalents
- Net decrease in cash and cash equivalents
- Net increase / (decrease) in cash and cash equivalents
- Net increase (decrease) in cash and cash equivalents
- Net change in cash and cash equivalents
- Cash and cash equivalents as at April 1st
- Cash and cash equivalents as at April 1
- Cash and cash equivalents at April 1st
- Cash and cash equivalents at April 1
- Cash and cash equivalents as at March 31st
- Cash and cash equivalents as at March 31
- Cash and cash equivalents at March 31st
- Cash and cash equivalents at March 31

IMPORTANT:

Do not place "Net increase / (decrease) in cash and cash
equivalents" inside operating_activities.

Do not place "Net increase / (decrease) in cash and cash
equivalents" inside investing_activities.

Do not place "Net increase / (decrease) in cash and cash
equivalents" inside financing_activities.

It belongs in reconciliation.

=========================================================
EVIDENCE
=========================================================

For important line items, include evidence whenever supported
by the schema.

Evidence should contain:

- Visible source text
- Page number

Do not invent evidence.

=========================================================
FINAL INSTRUCTION
=========================================================

Return ONLY valid JSON matching the requested CashFlowData
schema.

Do not include markdown fences.

Do not include explanations outside the JSON.
"""


# =========================================================
# OCR Helper
# =========================================================


def _extract_ocr_text(file_path):
    """
    Run OCR and combine all page text into one string.

    OCR is supporting context only. The original PDF remains
    the primary source of truth for Gemini.
    """

    ocr_result = extract_text(
        file_path
    )

    if not isinstance(ocr_result, dict):

        raise ValueError(
            "OCR service returned an invalid response."
        )

    pages = ocr_result.get(
        "pages",
        []
    )

    if not pages:

        raise ValueError(
            "OCR completed but no pages were returned."
        )

    ocr_text_parts = []

    for page in pages:

        if not isinstance(page, dict):
            continue

        page_number = page.get(
            "page_number",
            "unknown"
        )

        page_text = page.get(
            "text",
            ""
        )

        if page_text:

            ocr_text_parts.append(
                f"--- PAGE {page_number} ---\n"
                f"{page_text}"
            )

    ocr_text = "\n\n".join(
        ocr_text_parts
    ).strip()

    return ocr_text


# =========================================================
# Gemini Extraction
# =========================================================


def extract_cash_flow(
    file_path,
    ocr_text=None
):
    """
    Extract structured Cash Flow Statement data using Gemini.

    Parameters
    ----------
    file_path : str or Path
        Path to the Cash Flow PDF.

    ocr_text : str, optional
        OCR text already generated by another service.

        If omitted, OCR is performed inside this function.

    Returns
    -------
    CashFlowData
        Validated structured Cash Flow Statement data.
    """

    file_path = Path(
        file_path
    )


    # -----------------------------------------------------
    # Validate file
    # -----------------------------------------------------

    if not file_path.exists():

        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    if not file_path.is_file():

        raise ValueError(
            f"Provided path is not a file: {file_path}"
        )


    # -----------------------------------------------------
    # Read original PDF
    # -----------------------------------------------------

    try:

        pdf_bytes = file_path.read_bytes()

    except Exception as error:

        raise ValueError(
            f"Could not read the PDF file: {error}"
        ) from error


    if not pdf_bytes:

        raise ValueError(
            "The PDF file is empty."
        )


    # -----------------------------------------------------
    # Get OCR supporting text
    # -----------------------------------------------------

    if ocr_text is None:

        ocr_text = _extract_ocr_text(
            file_path
        )

    if ocr_text is None:

        ocr_text = ""


    # -----------------------------------------------------
    # Prepare Gemini request
    # -----------------------------------------------------

    pdf_part = types.Part.from_bytes(
        data=pdf_bytes,
        mime_type="application/pdf"
    )

    full_prompt = (
        EXTRACTION_PROMPT
        + "\n\n"
        + "OCR TEXT FROM THE DOCUMENT:\n"
        + str(ocr_text)
        + "\n\n"
        + "END OCR TEXT"
    )


    # -----------------------------------------------------
    # Call Gemini with retry handling
    # -----------------------------------------------------

    response = None

    max_attempts = 3

    for attempt in range(max_attempts):

        try:

            print(
                "\nSending Cash Flow extraction request "
                f"to Gemini "
                f"(attempt {attempt + 1}/{max_attempts})..."
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    pdf_part,
                    full_prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CashFlowData
                )
            )

            break


        except Exception as error:

            error_message = str(
                error
            ).upper()


            # -------------------------------------------------
            # Quota errors should not be retried
            # -------------------------------------------------

            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
                or "QUOTA" in error_message
            ):

                raise RuntimeError(
                    "Gemini API quota has been exhausted. "
                    "Please try again after the quota resets."
                ) from error


            # -------------------------------------------------
            # Temporary service errors
            # -------------------------------------------------

            is_temporary_error = (
                "503" in error_message
                or "UNAVAILABLE" in error_message
                or "500" in error_message
                or "INTERNAL" in error_message
                or "TIMEOUT" in error_message
            )

            if is_temporary_error and attempt < max_attempts - 1:

                wait_seconds = 2 ** attempt

                print(
                    "Gemini is temporarily unavailable. "
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(
                    wait_seconds
                )

                continue


            # -------------------------------------------------
            # All other errors
            # -------------------------------------------------

            raise RuntimeError(
                f"Gemini extraction failed: {error}"
            ) from error


    # -----------------------------------------------------
    # Check response
    # -----------------------------------------------------

    if response is None:

        raise RuntimeError(
            "Gemini did not return a response."
        )


    response_text = getattr(
        response,
        "text",
        None
    )


    if not response_text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )


    # -----------------------------------------------------
    # Validate Gemini output with Pydantic
    # -----------------------------------------------------

    try:

        cash_flow = CashFlowData.model_validate_json(
            response_text
        )

    except ValidationError as error:

        raise ValueError(
            "Gemini returned data that does not match "
            "the Cash Flow schema."
        ) from error


    return cash_flow


# =========================================================
# Direct Test
# =========================================================


if __name__ == "__main__":

    file_path = (
        r"New Dataset\Cash Flows"
        r"\Consolidated Cash Flow Statement 2017.pdf"
    )


    try:

        result = extract_cash_flow(
            file_path
        )


        print(
            "\n========== CASH FLOW EXTRACTION ==========\n"
        )


        print(
            result.model_dump_json(
                indent=2
            )
        )


    except Exception as error:

        print(
            "\n========== EXTRACTION ERROR ==========\n"
        )

        print(
            error
        )