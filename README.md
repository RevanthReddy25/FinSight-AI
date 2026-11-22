# FinSightAI – Financial Data Management & Intelligence Platform

FinSightAI is a finance-focused data management and intelligence platform designed to streamline financial transaction processing, data validation, vendor management, invoice storage, and data-quality monitoring.

The platform combines a FastAPI backend, SQLite relational database, MongoDB document database, and Python-based data processing to provide a foundation for intelligent financial analytics.

## Key Features

### 1. Financial Transaction Management
- Create, retrieve, update, and manage financial transactions.
- Organize transactions by projects, vendors, and categories.
- Track transaction types and payment statuses.
- Perform financial calculations and analytics.

### 2. CSV Data Ingestion
- Upload financial transaction data through the API.
- Process CSV files using Pandas.
- Validate incoming transaction records.
- Track import batches and processing status.
- Prevent duplicate file imports using file hashing.

### 3. Data Validation and Quality
- Validate transaction amounts, dates, and required fields.
- Detect potentially duplicated transactions.
- Identify invalid financial records.
- Preserve rejected records with their original data and validation errors.
- Generate data-quality reports.

### 4. Vendor Management
- Normalize vendor names.
- Support vendor identification and reconciliation.
- Track unresolved vendor records.
- Maintain vendor-related financial information.

### 5. MongoDB Integration
- Store invoice extraction documents.
- Manage document metadata and AI processing logs.
- Support invoice-related queries and aggregation.
- Maintain indexes for efficient document retrieval.

### 6. Data Quality Reporting
- Generate financial data-quality reports.
- Analyze transaction records and import batches.
- Identify potential duplicates and validation issues.
- Include MongoDB invoice metrics when MongoDB is accessible.

### 7. Automated Testing
- Test API endpoints and database operations.
- Test CSV ingestion and validation.
- Test duplicate detection and rejected-record handling.
- Test vendor resolution and MongoDB document models.

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Programming Language | Python |
| Relational Database | SQLite |
| ORM | SQLAlchemy |
| Document Database | MongoDB |
| Data Processing | Pandas |
| Database Migrations | Alembic |
| Testing Framework | Pytest |
| API Documentation | Swagger UI |

## Project Structure

```text
FinSight-AI/
│
├── app/
│   ├── data_quality/           # Data quality metrics and reporting
│   ├── ingestion/               # CSV ingestion and import processing
│   ├── mongodb/                 # MongoDB operations and analytics
│   ├── validation/              # Transaction validation and duplicate detection
│   │
│   ├── main.py                  # FastAPI application
│   ├── database.py              # SQLite database configuration
│   ├── init_db.py               # Database table initialization
│   ├── models.py                # SQLAlchemy database models
│   ├── schemas.py               # API request and response schemas
│   ├── crud.py                  # Database CRUD operations
│   ├── services.py              # Business logic and analytics
│   ├── calculations.py          # Financial calculations
│   ├── vendor_resolution.py     # Vendor resolution
│   └── invoice_vendor_service.py
│
├── migrations/                  # Database migration files
├── reports/                     # Generated data-quality reports
├── scripts/                     # Utility and reporting scripts
├── tests/                       # Automated test suite
│
├── financial_transactions.csv   # Sample financial transaction data
├── test_transactions.csv        # Sample test data
├── requirements.txt             # Python dependencies
├── alembic.ini                  # Alembic configuration
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later (use a Python version compatible with the installed dependencies).
- Git.
- MongoDB Atlas account for MongoDB functionality.

### 1. Clone the Repository

```bash
git clone https://github.com/RevanthReddy25/FinSight-AI.git
cd FinSight-AI
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure MongoDB

Create a `.env` file in the project root:

```env
MONGODB_URI=your_mongodb_atlas_connection_string
MONGODB_DATABASE=finsightai
```

Replace the placeholder with your MongoDB Atlas connection string.

The database name defaults to `finsightai` if `MONGODB_DATABASE` is not specified.

Ensure your MongoDB Atlas network access settings allow connections from your environment.

**Security:** Never commit your `.env` file or expose database credentials.

MongoDB configuration is required for MongoDB-dependent functionality. The SQLite-based application uses a local database.

### 5. Initialize the SQLite Database

Run:

```powershell
python -m app.init_db
```

This creates the database tables using SQLAlchemy.

The SQLite database is stored in the project root:

```text
finsight.db
```

## Running the Application

Start the FastAPI development server:

```powershell
python -m uvicorn app.main:app --reload
```

The application will be available at:

| Resource | Address |
|---|---|
| API | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

Use Swagger UI to explore and test the available API endpoints.

## Demonstrating the Project

The following commands demonstrate important project capabilities.

### 1. Start the API

```powershell
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Explore the available endpoints, including financial project management and transaction import functionality.

### 2. Run the Automated Test Suite

```powershell
pytest -v
```

### 3. Run a Specific Test Module

Example:

```powershell
pytest tests/test_import_upload.py -v
```

### 4. Generate a Data Quality Report

```powershell
python -m scripts.generate_data_quality_report
```

The generated report is saved at:

```text
reports/data_quality_report.md
```

MongoDB metrics are included when the MongoDB connection is available.

### 5. Run Individual Database Initialization

```powershell
python -m app.init_db
```

This initializes the SQLite database tables.

## Testing

The automated test suite covers:

- FastAPI endpoint operations.
- Financial calculations.
- Database CRUD operations.
- CSV loading and ingestion.
- Import batch processing.
- Transaction validation.
- Duplicate detection.
- Rejected-record management.
- Vendor resolution and reconciliation.
- MongoDB document models and operations.

Run all tests:

```powershell
pytest -v
```

## Future Enhancements

Potential areas for extending the platform:

- Financial forecasting using machine learning.
- Intelligent invoice data extraction.
- AI-powered financial document analysis.
- Retrieval-Augmented Generation (RAG) for financial documents.
- Automated financial insights and reporting.
- Advanced anomaly detection and fraud-risk analysis.
- Natural-language querying of financial data.

## Author

**FinSightAI – Financial Data Management & Intelligence Platform**

A finance-focused software engineering project.