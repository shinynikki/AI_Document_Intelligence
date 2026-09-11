# =========================================================
# Document API Routes
# =========================================================

import json
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.services.document_service import (
    SUPPORTED_DOCUMENT_TYPES,
    process_document,
)


# =========================================================
# Router
# =========================================================

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


# =========================================================
# Upload Directory
# =========================================================

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


# =========================================================
# Allowed File Extensions
# =========================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}


# =========================================================
# Helper Functions
# =========================================================

def serialize_document(document):
    """
    Convert a SQLAlchemy Document object into a JSON-safe dictionary.
    """

    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "status": document.status,
        "overall_status": document.overall_status,
        "error_message": document.error_message,
        "created_at": (
            document.created_at.isoformat()
            if document.created_at
            else None
        ),
    }


def serialize_full_document(document):
    """
    Convert a SQLAlchemy Document object into a complete API response.
    """

    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "status": document.status,

        "extracted_data": (
            json.loads(document.extracted_data)
            if document.extracted_data
            else None
        ),

        "validations": (
            json.loads(document.validations)
            if document.validations
            else None
        ),

        "overall_status": document.overall_status,
        "error_message": document.error_message,

        "created_at": (
            document.created_at.isoformat()
            if document.created_at
            else None
        ),
    }


# =========================================================
# POST /api/v1/documents/process
# =========================================================

@router.post("/process")
async def process_uploaded_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Upload, extract, validate and persist a document.
    """

    # -----------------------------------------------------
    # Validate document type
    # -----------------------------------------------------

    document_type = document_type.strip().lower()

    if document_type not in SUPPORTED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported document type. Choose one of: "
                "invoice, balance_sheet, profit_loss, cash_flow."
            ),
        )

    # -----------------------------------------------------
    # Validate filename
    # -----------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename.",
        )

    # -----------------------------------------------------
    # Validate extension
    # -----------------------------------------------------

    original_filename = Path(file.filename).name
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, JPG, JPEG and PNG files are supported.",
        )

    # -----------------------------------------------------
    # Save uploaded file
    # -----------------------------------------------------

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")

    saved_filename = f"{timestamp}_{original_filename}"
    saved_path = UPLOAD_DIRECTORY / saved_filename

    try:
        with saved_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save uploaded file: {error}",
        )

    finally:
        await file.close()

    # -----------------------------------------------------
    # Process document
    # -----------------------------------------------------

    try:
        result = process_document(
            saved_path,
            document_type,
        )

        # =================================================
        # Save successful result
        # =================================================

        document = Document(
            filename=original_filename,
            document_type=document_type,
            status="PROCESSED",
            extracted_data=json.dumps(
                result["extracted_data"]
            ),
            validations=json.dumps(
                result["validations"]
            ),
            overall_status=result["overall_status"],
            error_message=None,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return serialize_full_document(document)

    except Exception as error:

        # =================================================
        # Roll back failed database transaction
        # =================================================

        db.rollback()

        error_message = str(error)

        # =================================================
        # Save failed processing attempt
        # =================================================

        failed_document = Document(
            filename=original_filename,
            document_type=document_type,
            status="FAILED",
            extracted_data=None,
            validations=None,
            overall_status="FAILED",
            error_message=error_message,
        )

        try:
            db.add(failed_document)
            db.commit()
            db.refresh(failed_document)

        except Exception:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail="Document processing failed and could not be saved.",
            )

        raise HTTPException(
            status_code=422,
            detail={
                "message": "Document processing failed.",
                "document_id": failed_document.id,
                "error": error_message,
            },
        )


# =========================================================
# GET /api/v1/documents
# =========================================================

@router.get("")
def get_all_documents(
    db: Session = Depends(get_db),
):
    """
    Return all processed documents.

    Latest documents appear first.
    """

    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        serialize_document(document)
        for document in documents
    ]


# =========================================================
# GET /api/v1/documents/{document_name}
# =========================================================

@router.get("/{document_name}")
def get_document(
    document_name: str,
    db: Session = Depends(get_db),
):
    """
    Return the latest document with the requested filename.
    """

    document = (
        db.query(Document)
        .filter(Document.filename == document_name)
        .order_by(Document.created_at.desc())
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return serialize_full_document(document)