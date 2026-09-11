from pathlib import Path

import pymupdf
import pytesseract

from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    ImageOps
)


# Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


ALLOWED_TYPES = [".pdf", ".jpg", ".jpeg", ".png"]
MAX_PAGES = 3


def preprocess_image(image):
    """
    Prepare an image before sending it to Tesseract.
    """

    # Fix the orientation if the image contains orientation information
    image = ImageOps.exif_transpose(image)

    # Make small text easier for OCR to read
    width, height = image.size
    image = image.resize((width * 3, height * 3))

    # Convert to grayscale
    image = ImageOps.grayscale(image)

    # Improve contrast
    image = ImageOps.autocontrast(image)
    image = ImageEnhance.Contrast(image).enhance(1.5)

    # Make text slightly sharper
    image = image.filter(ImageFilter.SHARPEN)

    return image


def run_ocr(image):
    """
    Run Tesseract OCR on an image.
    """

    image = preprocess_image(image)

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text.strip()


def extract_from_pdf(file_path):
    """
    Extract text from a PDF.

    If the PDF contains usable text, use it directly.
    Otherwise, convert each page to an image and use Tesseract.
    """

    try:
        document = pymupdf.open(file_path)

    except Exception:
        raise ValueError("The PDF file is corrupt or cannot be opened.")

    if len(document) == 0:
        document.close()
        raise ValueError("The PDF does not contain any pages.")

    if len(document) > MAX_PAGES:
        document.close()
        raise ValueError("The document cannot contain more than 3 pages.")

    pages = []

    for page_number, page in enumerate(document, start=1):

        # Try normal PDF text extraction first
        text = page.get_text().strip()

        # If there is not enough text, treat it as a scanned PDF
        if len(text) < 50:

            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples
            )

            text = run_ocr(image)

        pages.append({
            "page_number": page_number,
            "text": text
        })

    document.close()

    return {
        "pages": pages
    }


def extract_from_image(file_path):
    """
    Extract text from a JPG or PNG image.
    """

    try:
        image = Image.open(file_path)

        # Make sure the image can actually be read
        image.load()

    except Exception:
        raise ValueError("The image file is corrupt or cannot be opened.")

    text = run_ocr(image)

    return {
        "pages": [
            {
                "page_number": 1,
                "text": text
            }
        ]
    }


def extract_text(file_path):
    """
    Main function for document text extraction.
    """

    file_path = Path(file_path)

    # Check that the file exists
    if not file_path.exists():
        raise FileNotFoundError("File does not exist.")

    # Check that the file is not empty
    if file_path.stat().st_size == 0:
        raise ValueError("The uploaded file is empty.")

    # Check file type
    extension = file_path.suffix.lower()

    if extension not in ALLOWED_TYPES:
        raise ValueError(
            "Only PDF, JPG, JPEG and PNG files are supported."
        )

    # Process the file according to its type
    if extension == ".pdf":
        return extract_from_pdf(file_path)

    return extract_from_image(file_path)