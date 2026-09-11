# Intelligent Document Intelligence

AI-powered document extraction, validation, and persistence platform.

## Project Overview

Intelligent Document Intelligence is a financial document processing system that extracts structured information from uploaded documents using AI, validates the extracted data, stores the results in a database, and displays them through a web dashboard.

The system supports four document types:

- Invoice
- Balance Sheet
- Profit & Loss Statement
- Cash Flow Statement

The application is designed to convert unstructured financial documents into structured, machine-readable data while performing document-specific financial validation checks.

## Key Features

- Upload financial documents through a web interface.
- Select the document type before processing.
- Validate file type and file size before processing.
- Extract text from PDFs and images using OCR.
- Use Gemini AI for intelligent document understanding and information extraction.
- Generate structured JSON from unstructured financial documents.
- Validate extracted data using Pydantic schemas.
- Perform arithmetic and balance checks on financial data.
- Store documents and extraction results in SQLite using SQLAlchemy.
- Retrieve previously processed documents.
- Display extraction results, validation status, and evidence in a dashboard.
- Highlight missing, unreadable, or invalid information where applicable.
- View raw structured JSON returned by the backend API.

## System Architecture

The application follows this processing pipeline:

```text
Frontend Dashboard
        |
        v
FastAPI REST API
        |
        v
Document Validation
        |
        v
Text Extraction / OCR
        |
        v
Gemini AI Extraction
        |
        v
Pydantic Schema Validation
        |
        v
Financial Validation
        |
        v
Database Persistence
        |
        v
API Response
        |
        v
Frontend Dashboard
```

### Processing Workflow

1. The user selects a document type and uploads a PDF or image.
2. The backend validates the file extension, file size, and basic file requirements.
3. Text is extracted directly from text-based PDFs where possible.
4. OCR is used for scanned or image-based documents.
5. Gemini AI extracts relevant financial information into a structured format.
6. Pydantic validates the extracted structure and data types.
7. Financial validation rules are applied according to the document type.
8. The document metadata, extracted data, and validation results are stored in SQLite.
9. The processed result is returned to the frontend and displayed in the dashboard.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API framework |
| Gemini AI | Intelligent document extraction |
| Pydantic | Data validation and structured schemas |
| SQLite | Database storage |
| SQLAlchemy | Database ORM and persistence |
| Tesseract OCR | Text extraction from scanned documents |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | Frontend functionality |
| Render | Application deployment |

## Supported Document Types

### 1. Invoice

Extracts information such as:

- Invoice number
- Invoice date
- Currency
- Seller details
- Buyer details
- Line items
- Taxable amount
- Tax amount
- Discount
- Total amount
- Supporting evidence
- Validation results

Validation may include checks such as:

```text
Subtotal + Tax - Discount ≈ Total Amount
```

### 2. Balance Sheet

Extracts financial information related to:

- Assets
- Liabilities
- Equity
- Financial periods
- Supporting evidence

Validation includes balance sheet arithmetic checks such as:

```text
Assets ≈ Liabilities + Equity
```

### 3. Profit & Loss Statement

Extracts:

- Income or revenue
- Expenses
- Profit or loss
- Financial periods
- Supporting evidence

Validation includes arithmetic checks between revenue, expenses, and reported profit or loss.

### 4. Cash Flow Statement

Extracts cash flow information under:

- Operating activities
- Investing activities
- Financing activities
- Cash and cash equivalents
- Financial periods
- Supporting evidence

Validation may include checks such as:

```text
Opening Cash Balance + Net Cash Movement ≈ Closing Cash Balance
```

## Frontend

The frontend provides an interactive dashboard for uploading documents and viewing processed results.

### Frontend Features

- Document type selection.
- PDF, JPG, JPEG, and PNG upload control.
- Process Document action.
- Processing status messages.
- Dashboard showing previously processed documents.
- Document name, document type, status, and processed time.
- Detailed extracted key-value pairs.
- Financial tables and line items.
- Financial validation and calculation results.
- Highlighting of missing or unreadable fields where applicable.
- Display of failed financial validations.
- View of the raw structured JSON returned by the backend.

Processed results are displayed directly in the dashboard. The current implementation does not provide a download or export feature for generated outputs.

## API Endpoints

### Process Uploaded Document

```http
POST /api/v1/documents/process
```

Accepts a financial document and processes it using file validation, OCR/text extraction, Gemini AI extraction, schema validation, and financial validation.

#### Form Parameters

| Parameter | Type | Description |
|---|---|---|
| `file` | File | Uploaded PDF or image |
| `document_type` | String | Type of financial document |

Supported document types:

```text
invoice
balance_sheet
profit_loss
cash_flow
```

### Retrieve All Processed Documents

```http
GET /api/v1/documents
```

Returns a list of all previously processed documents, including their metadata and processing status.

### Retrieve a Specific Document

```http
GET /api/v1/documents/{document_name}
```

Returns the latest processed result for a specific document.

### Health Check

```http
GET /api/v1/health
```

Returns the health status of the backend service.

## API Error Handling

The API returns controlled and consistent error responses for invalid files and processing failures.

Example:

```json
{
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "Only PDF, JPG, JPEG, and PNG documents are supported."
  }
}
```

Possible error scenarios include:

- Unsupported file type.
- Invalid or corrupted file.
- File size exceeding the allowed limit.
- OCR or text extraction failure.
- AI/model processing failure.
- Timeout or external service failure.
- Database or persistence failure.
- Unexpected processing errors.

Errors are handled without exposing stack traces, API keys, or sensitive implementation details to end users.

## Sample JSON Output

The following is an example of the structured response returned by the document processing API:

```json
{
  "document_name": "sample_invoice.pdf",
  "document_type": "invoice",
  "status": "processed",
  "extracted_data": {
    "invoice_number": "INV-23891",
    "invoice_date": "2026-08-15",
    "currency": "USD",
    "vendor_name": "ABC Technologies",
    "subtotal": 12500.0,
    "tax_amount": 625.0,
    "discount": 0.0,
    "total_amount": 13125.0,
    "line_items": [
      {
        "description": "Service A",
        "quantity": 1,
        "unit_price": 12500.0,
        "amount": 12500.0
      }
    ]
  },
  "validation": {
    "checks": [
      {
        "name": "invoice_total_check",
        "formula": "subtotal + tax_amount - discount",
        "calculated_value": 13125.0,
        "reported_value": 13125.0,
        "variance": 0.0,
        "status": "PASS"
      }
    ],
    "overall_status": "PASS",
    "issues": []
  },
  "processing_metadata": {
    "ocr_used": true,
    "processing_time_ms": 2840
  }
}
```

The actual response structure may vary depending on the document type and extracted fields. The backend returns consistent machine-readable JSON containing document details, extracted data, validation results, processing status, and processing metadata.

## Validation Approach

The system performs two levels of validation.

### Schema Validation

Pydantic validates the structure and data types of the extracted JSON.

This ensures that:

- Required fields follow the expected schema.
- Numeric fields contain valid numeric values.
- Structured objects and arrays follow the expected format.
- Invalid data structures are rejected or flagged.

### Financial Validation

Financial consistency checks are performed depending on the document type.

Examples include:

- Invoice taxable amount + tax approximately equals total amount.
- Balance sheet assets equal liabilities + equity.
- Profit/loss calculations match reported figures.
- Cash flow opening balance + net movement approximately equals closing balance.

Each validation result may include:

- Check name or description.
- Formula used.
- Calculated value.
- Reported value.
- Variance.
- Validation status.
- Issues or explanations where applicable.

## Database and Persistence

SQLite is used as the persistence layer, with SQLAlchemy providing database interaction and ORM functionality.

The system stores processed-document metadata and extraction results, allowing previously processed documents to remain available through the dashboard.

Persisted information may include:

- Document name.
- Document type.
- Processing status.
- Processed timestamp.
- Extracted structured data.
- Validation results.
- Processing metadata.

The frontend retrieves stored documents through the backend API.

## Project Structure

```text
AI_Document_Intelligence/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── models/
│   │   └── document.py
│   │
│   ├── routes/
│   │   └── documents.py
│   │
│   ├── schemas/
│   │   └── document_schemas.py
│   │
│   ├── services/
│   │   ├── ocr_services.py
│   │   ├── extraction_service.py
│   │   ├── document_services.py
│   │   └── validation_service.py
│   │
│   └── main.py
│
├── frontend/
│   └── index.html
│
├── tests/
│   └── ...
│
├── requirements.txt
├── Dockerfile
├── README.md
└── .env.example
```

## Installation and Setup

### Clone the Repository

```bash
git clone https://github.com/shinynikki/AI_Document_Intelligence.git
cd AI_Document_Intelligence
```

### Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model
```

Do not commit the `.env` file to GitHub.

API keys, credentials, and tokens must be stored in environment variables and must not be hardcoded in the source code.

### Run the Backend

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

## Deployment

The application is deployed using Render.

### Deployment Components

- **Backend:** FastAPI application deployed as a web service.
- **Frontend:** Static HTML, CSS, and JavaScript deployed as a static site.
- **Database:** SQLite database used for persistence.
- **AI Model:** Google Gemini API.
- **OCR:** Tesseract OCR for scanned or image-based documents.

Environment variables such as `GEMINI_API_KEY` are configured securely through the deployment platform rather than committed to the repository.

### Deployment Requirements

The deployed application should provide:

- Public frontend URL.
- Public backend API URL.
- Swagger/OpenAPI documentation URL.
- Working health endpoint.

The backend and frontend communicate through the deployed API.

## Testing

The application should be tested against the following scenarios:

| Test Scenario | Expected Result |
|---|---|
| Invoice processing | Extract structured invoice data and validate totals |
| Balance sheet processing | Extract financial fields and perform balance checks |
| Profit & Loss processing | Extract revenue, expenses, and profit/loss values |
| Cash flow processing | Extract operating, investing, and financing activities |
| Scanned/image-based document | OCR extracts readable text for further processing |
| Missing or unreadable field | Field is flagged instead of being fabricated |
| Financial validation failure | Failed calculation is clearly reported |
| Unsupported file type | Controlled error response is returned |
| Invalid or corrupted file | Application handles the error without crashing |

Automated tests should cover:

- File validation.
- Financial validation calculations.
- At least one API processing flow.

## Assumptions

- Users upload PDF, JPG, JPEG, or PNG documents.
- The document type is selected by the user before processing.
- Uploaded documents are assumed to contain relevant financial information.
- OCR is used when text cannot be directly extracted from the document.
- Extracted values that are missing or unreadable are not fabricated.
- Financial validation is performed only when the required values are available.
- SQLite is used as the persistence layer for the current implementation.
- The Gemini API key must be configured through environment variables.
- The application is intended for financial document extraction and validation rather than accounting or auditing certification.

## AI and Tool Usage Declaration

This project uses AI and software tools to support document processing:

- **Gemini AI:** Used for extracting structured information from unstructured financial documents.
- **Tesseract OCR:** Used for extracting text from scanned or image-based documents.
- **Pydantic:** Used for validating extracted data against predefined schemas.
- **FastAPI:** Used to build the backend API.
- **SQLAlchemy and SQLite:** Used for database persistence.
- **HTML, CSS, and JavaScript:** Used to build the frontend dashboard.

AI-generated extraction results are processed through schema validation and document-specific financial validation rules. The system does not hardcode expected document outputs or validation outcomes.

## Known Limitations

- Extraction accuracy may decrease for poor-quality scans, handwritten content, or heavily distorted documents.
- OCR accuracy depends on document image quality and text clarity.
- Financial validation cannot always be performed when required values are missing or unreadable.
- The current application uses SQLite, which may not be suitable for high-concurrency production workloads.
- Authentication and user-specific access control are not currently implemented.
- Processing may take longer for larger or more complex documents.
- The system depends on the availability and rate limits of the Gemini API.
- The current frontend displays processed results directly but does not provide download or export functionality.

## Production Improvement Notes

For production deployment, the following improvements could be considered:

- Migrate from SQLite to PostgreSQL for scalability and concurrent access.
- Introduce asynchronous or background document processing.
- Add authentication and authorization for user-specific document access.
- Implement stronger monitoring, structured logging, and alerting.
- Add retry mechanisms and timeout handling for external AI and OCR services.
- Improve extraction accuracy through confidence scoring and human review workflows.
- Add comprehensive automated testing and continuous integration.
- Implement secure file storage and document lifecycle management.
- Add rate limiting and API access controls.
- Improve frontend visualization and filtering of extracted financial data.
- Add document download or export functionality if required in future versions.

## Future Improvements

- Improve extraction accuracy for missing or ambiguous fields.
- Add support for additional document formats.
- Implement asynchronous document processing.
- Add authentication and user-specific document access.
- Replace SQLite with PostgreSQL for production scalability.
- Improve frontend visualization of extracted financial data.
- Expand financial validation rules for additional document-specific scenarios.

## Conclusion

Intelligent Document Intelligence combines OCR, AI-powered extraction, schema validation, financial reasoning, and database persistence into a single document-processing workflow.

The project demonstrates an end-to-end AI application capable of converting unstructured financial documents into validated and structured information while providing a searchable dashboard for reviewing processed results.