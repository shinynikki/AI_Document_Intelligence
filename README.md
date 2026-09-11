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
- Extract text from PDFs and images.
- Use Gemini AI for intelligent document understanding.
- Generate structured JSON from unstructured financial documents.
- Validate extracted data using Pydantic schemas.
- Perform arithmetic and balance checks on financial data.
- Store documents and extraction results in SQLite using SQLAlchemy.
- Retrieve previously processed documents.
- Display extraction results, validation status, and evidence in a dashboard.

## System Architecture

The application follows this processing pipeline:

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

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend programming language |
| FastAPI | REST API framework |
| Gemini AI | Intelligent document extraction |
| Pydantic | Data validation and structured schemas |
| SQLite | Database storage |
| SQLAlchemy | Database ORM |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | Frontend functionality |
| OCR | Text extraction from scanned documents |

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