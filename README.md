# Intelligent Document Intelligence

AI-powered document extraction, validation, and persistence platform.

## Project Overview

Intelligent Document Intelligence is a financial document processing system that extracts structured information from uploaded documents using AI, validates the extracted data, stores the results in a database, and displays them through a web dashboard.

The system supports four document types:

- Invoice
- Balance Sheet
- Profit & Loss Statement
- Cash Flow Statement

## Key Features

- Upload financial documents through a web interface.
- Validate file type and file size before processing.
- Extract text from PDFs and images using OCR.
- Use Gemini AI for intelligent document understanding.
- Generate structured JSON from unstructured financial documents.
- Validate extracted data using Pydantic schemas.
- Perform arithmetic and balance checks on financial data.
- Store documents and extraction results in SQLite using SQLAlchemy.
- Retrieve previously processed documents.
- Display extraction results, validation status, and evidence in a dashboard.

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
Text & OCR Extraction
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
API Response and Frontend Dashboard
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API framework |
| Gemini AI | Intelligent document extraction |
| Pydantic | Data validation and structured schemas |
| SQLite | Database storage |
| SQLAlchemy | Database ORM |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | Frontend functionality |
| Tesseract OCR | Text extraction from scanned documents |

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
- Total amount
- Validation results

### 2. Balance Sheet

Extracts financial information related to:

- Assets
- Liabilities
- Equity
- Financial periods
- Supporting evidence

Validation includes balance sheet arithmetic checks.

### 3. Profit & Loss Statement

Extracts:

- Income
- Expenses
- Profit or loss
- Financial periods
- Supporting evidence

Validation includes arithmetic checks between revenue, expenses, and profit or loss.

### 4. Cash Flow Statement

Extracts cash flow information under:

- Operating activities
- Investing activities
- Financing activities
- Cash and cash equivalents
- Financial periods
- Supporting evidence

## API Endpoints

### Process Uploaded Document

```http
POST /api/v1/documents/process
```

Accepts a financial document and processes it using OCR, Gemini extraction, schema validation, and financial validation.

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

Returns a list of all previously processed documents.

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
GEMINI_MODEL=gemini-3.6-flash
```

Do not commit the `.env` file to GitHub.

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

- Backend: FastAPI application deployed as a web service.
- Frontend: Static HTML, CSS, and JavaScript deployed as a static site.
- Database: SQLite database used for persistence.
- AI Model: Google Gemini API.

Environment variables such as `GEMINI_API_KEY` are configured securely through the deployment platform rather than committed to the repository.

## Validation Approach

The system performs two levels of validation.

### Schema Validation

Pydantic validates the structure and data types of the extracted JSON.

### Financial Validation

Financial consistency checks are performed depending on the document type.

Examples include:

- Invoice taxable amount + tax approximately equals total amount.
- Balance sheet assets equal liabilities + equity.
- Profit/loss calculations match reported figures.
- Cash flow opening balance + net movement approximately equals closing balance.

Each validation result includes:

- Check description
- Calculated value
- Reported value
- Variance
- Status

## Future Improvements

- Improve extraction accuracy for missing or ambiguous fields.
- Add support for additional document formats.
- Implement asynchronous document processing.
- Add authentication and user-specific document access.
- Replace SQLite with PostgreSQL for production scalability.
- Add automated test coverage.
- Improve frontend visualization of extracted financial data.

## Conclusion

Intelligent Document Intelligence combines OCR, AI-powered extraction, schema validation, financial reasoning, and database persistence into a single document-processing workflow.

The project demonstrates an end-to-end AI application capable of converting unstructured financial documents into validated and structured information.