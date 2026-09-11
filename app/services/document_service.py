# =========================================================
# Document Service
# =========================================================
#
# Central service for document processing.
#
# Responsibilities:
# 1. Validate the uploaded file and document type.
# 2. Run OCR only when required.
# 3. Select the appropriate extraction service.
# 4. Run the corresponding financial validation.
# 5. Return structured extraction and validation results.
#
# Individual extraction services remain responsible for
# understanding their own document formats.
# =========================================================


from pathlib import Path


# =========================================================
# OCR
# =========================================================

from app.services.ocr_services import (
    extract_text
)


# =========================================================
# Invoice Extraction
# =========================================================

from app.services.extraction_service import (
    extract_invoice
)


# =========================================================
# Balance Sheet Extraction
# =========================================================

from app.services.financial_statement_extraction import (
    extract_balance_sheet
)


# =========================================================
# Profit & Loss Extraction
# =========================================================

from app.services.profit_loss_extraction import (
    extract_profit_loss
)


# =========================================================
# Cash Flow Extraction
# =========================================================

from app.services.cash_flow_extraction import (
    extract_cash_flow
)


# =========================================================
# Financial Validation
# =========================================================

from app.services.financial_validation import (
    validate_invoice,
    validate_balance_sheet,
    validate_profit_loss,
    validate_cash_flow,
    get_overall_status
)


# =========================================================
# Supported Document Types
# =========================================================


SUPPORTED_DOCUMENT_TYPES = {
    "invoice",
    "balance_sheet",
    "profit_loss",
    "cash_flow"
}


# =========================================================
# Document Type Normalization
# =========================================================


def normalize_document_type(document_type):
    """
    Normalize and validate the requested document type.
    """

    if not isinstance(document_type, str):
        raise ValueError(
            "Document type must be a string."
        )

    document_type = document_type.strip().lower()

    # Allow a few common naming variations.
    aliases = {
        "balance sheet": "balance_sheet",
        "balance-sheet": "balance_sheet",
        "profit and loss": "profit_loss",
        "profit & loss": "profit_loss",
        "profit-loss": "profit_loss",
        "cash flow": "cash_flow",
        "cash-flow": "cash_flow"
    }

    document_type = aliases.get(
        document_type,
        document_type
    )

    if document_type not in SUPPORTED_DOCUMENT_TYPES:

        raise ValueError(
            "Unsupported document type. "
            "Choose one of: "
            "invoice, balance_sheet, profit_loss, cash_flow."
        )

    return document_type


# =========================================================
# OCR Text Extraction
# =========================================================


def get_ocr_text(file_path):
    """
    Run OCR once and combine all page text into one string.

    Returns
    -------
    str
        Combined OCR text from all pages.
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

        page_text = page.get(
            "text",
            ""
        )

        if page_text:
            ocr_text_parts.append(
                str(page_text)
            )

    ocr_text = "\n".join(
        ocr_text_parts
    ).strip()

    if not ocr_text:

        raise ValueError(
            "OCR completed but no text was extracted."
        )

    return ocr_text


# =========================================================
# Process Document
# =========================================================


def process_document(
    file_path,
    document_type
):
    """
    Process a financial document from upload to validation.

    Parameters
    ----------
    file_path : str or Path
        Path to the uploaded document.

    document_type : str
        Supported values:
            - invoice
            - balance_sheet
            - profit_loss
            - cash_flow

    Returns
    -------
    dict
        {
            "document_type": str,
            "extracted_data": dict,
            "validations": list,
            "overall_status": str
        }
    """

    # -----------------------------------------------------
    # Convert to Path
    # -----------------------------------------------------

    file_path = Path(file_path)


    # -----------------------------------------------------
    # Validate Document Type
    # -----------------------------------------------------

    document_type = normalize_document_type(
        document_type
    )


    # -----------------------------------------------------
    # Validate File
    # -----------------------------------------------------

    if not file_path.exists():

        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    if not file_path.is_file():

        raise ValueError(
            f"Provided path is not a file: {file_path}"
        )


    # =====================================================
    # Invoice
    # =====================================================

    if document_type == "invoice":

        # Invoice extraction requires OCR text.
        ocr_text = get_ocr_text(
            file_path
        )

        extracted_data = extract_invoice(
            file_path,
            ocr_text
        )

        validations = validate_invoice(
            extracted_data
        )


    # =====================================================
    # Balance Sheet
    # =====================================================

    elif document_type == "balance_sheet":

        # Balance Sheet extraction requires OCR text.
        ocr_text = get_ocr_text(
            file_path
        )

        extracted_data = extract_balance_sheet(
            file_path,
            ocr_text
        )

        validations = validate_balance_sheet(
            extracted_data
        )


    # =====================================================
    # Profit & Loss
    # =====================================================

    elif document_type == "profit_loss":

        # Profit & Loss extraction requires OCR text.
        ocr_text = get_ocr_text(
            file_path
        )

        extracted_data = extract_profit_loss(
            file_path,
            ocr_text
        )

        validations = validate_profit_loss(
            extracted_data
        )


    # =====================================================
    # Cash Flow
    # =====================================================

    elif document_type == "cash_flow":

        # Cash Flow extraction performs its own OCR and
        # structured extraction internally.
        #
        # Do not call get_ocr_text() here because it would
        # duplicate OCR processing and may cause inconsistent
        # extraction results.

        extracted_data = extract_cash_flow(
            file_path
        )

        validations = validate_cash_flow(
            extracted_data
        )


    # =====================================================
    # Validate Extraction Result
    # =====================================================

    if extracted_data is None:

        raise ValueError(
            f"Extraction failed for document type: "
            f"{document_type}"
        )


    # =====================================================
    # Overall Validation Status
    # =====================================================

    overall_status = get_overall_status(
        validations
    )


    # =====================================================
    # Serialize Extracted Data
    # =====================================================

    if hasattr(
        extracted_data,
        "model_dump"
    ):

        extracted_data_dict = extracted_data.model_dump()

    elif hasattr(
        extracted_data,
        "dict"
    ):

        # Compatibility with older Pydantic versions.
        extracted_data_dict = extracted_data.dict()

    elif isinstance(
        extracted_data,
        dict
    ):

        extracted_data_dict = extracted_data

    else:

        raise TypeError(
            "Extractor returned an unsupported data type: "
            f"{type(extracted_data).__name__}"
        )


    # =====================================================
    # Return Final Result
    # =====================================================

    return {
        "document_type": document_type,

        "extracted_data": extracted_data_dict,

        "validations": validations,

        "overall_status": overall_status
    }


# =========================================================
# Direct Test
# =========================================================


if __name__ == "__main__":

    file_path = (
        "New Dataset/Balance Sheet/"
        "Consolidated Balance Sheet 2017.pdf"
    )


    print(
        "\n========== PROCESSING DOCUMENT ==========\n"
    )


    result = process_document(
        file_path,
        "balance_sheet"
    )


    print(
        "\n========== DOCUMENT TYPE ==========\n"
    )

    print(
        result["document_type"]
    )


    print(
        "\n========== EXTRACTED DATA ==========\n"
    )

    print(
        result["extracted_data"]
    )


    print(
        "\n========== VALIDATIONS ==========\n"
    )

    for validation in result["validations"]:

        print(validation)


    print(
        "\n========== OVERALL STATUS ==========\n"
    )

    print(
        result["overall_status"]
    )