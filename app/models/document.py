# =========================================================
# Document Database Model
# =========================================================

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text
)

from app.core.database import Base


# =========================================================
# Document Table
# =========================================================

class Document(Base):

    __tablename__ = "documents"

    # -----------------------------------------------------
    # Primary key
    # -----------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # -----------------------------------------------------
    # Original uploaded filename
    # -----------------------------------------------------

    filename = Column(
        String,
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # Document type
    #
    # invoice
    # balance_sheet
    # profit_loss
    # cash_flow
    # -----------------------------------------------------

    document_type = Column(
        String,
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # Processing status
    #
    # PROCESSED
    # FAILED
    # -----------------------------------------------------

    status = Column(
        String,
        nullable=False
    )

    # -----------------------------------------------------
    # Extracted structured JSON
    # -----------------------------------------------------

    extracted_data = Column(
        Text,
        nullable=True
    )

    # -----------------------------------------------------
    # Financial validation results
    # -----------------------------------------------------

    validations = Column(
        Text,
        nullable=True
    )

    # -----------------------------------------------------
    # Overall validation status
    #
    # PASS
    # FAILED
    # NOT_APPLICABLE
    # -----------------------------------------------------

    overall_status = Column(
        String,
        nullable=True
    )

    # -----------------------------------------------------
    # Error message, if processing failed
    # -----------------------------------------------------

    error_message = Column(
        Text,
        nullable=True
    )

    # -----------------------------------------------------
    # Creation timestamp
    # -----------------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )