# FinSight-AI

### Financial Intelligence Platform

FinSight-AI is a financial intelligence application built using Python, FastAPI and SQLite. It helps manage financial project information, track budgets, monitor revenue and expenditure, and provide project-level financial analytics.

The project is being developed as an integrated capstone, progressively incorporating data engineering, machine learning and Generative AI capabilities.

---

## 1. Project Objectives

- Manage financial project records.
- Track project budgets, revenue and expenditure.
- Monitor financial project performance.
- Provide REST APIs for financial project management.
- Build a foundation for advanced financial analytics and AI integration.

## 2. Current Features

- FastAPI backend.
- SQLite database integration using SQLAlchemy.
- Create, Read, Update and Delete (CRUD) operations.
- Pydantic request validation and response schemas.
- Project-level financial analytics API.
- Error handling and input validation.
- Automated testing using Pytest.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend REST API |
| SQLite | Database |
| SQLAlchemy | Database ORM |
| Pydantic | Data validation |
| Pytest | Automated testing |
| HTTPX | API testing |
| Postman | Manual API testing |
| Git & GitHub | Version control |

## 4. Project Structure

```text
FinSight-AI/
│
├── app/
│   ├── __init__.py
│   ├── calculations.py
│   ├── crud.py
│   ├── database.py
│   ├── init_db.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── services.py
│
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_calculations.py
│   ├── test_crud.py
│   └── test_services.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

## 5. Installation and Setup

### Clone the repository

```bash
git clone https://github.com/RevanthReddy25/FinSight-AI.git
cd FinSight-AI
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Run the Application

Initialize the database:

```bash
python -m app.init_db
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The application will run locally at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## 7. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/projects/` | Create a financial project |
| GET | `/projects/` | Retrieve all projects |
| GET | `/projects/{project_id}` | Retrieve a project by ID |
| PATCH | `/projects/{project_id}` | Update project details |
| DELETE | `/projects/{project_id}` | Delete a project |
| GET | `/projects/{project_id}/analytics` | Retrieve financial analytics |

## 8. Testing

Run all automated tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

The V2 implementation has achieved 26 passing tests and 91% test coverage in the development environment.

---

Developed as part of the FinSight-AI capstone project.