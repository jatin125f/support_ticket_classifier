# AI Customer Support Ticket Classifier & Triage System

An end-to-end intelligent customer support ticket classification and triage operations platform powered by a hybrid architecture combining a local Scikit-Learn machine learning model with Google Gemini LLM fallback.

---

## Features

- **Hybrid AI Engine**:
  - High-speed local ML model (TF-IDF + Classifier) for low-latency predictions.
  - Dynamic Google Gemini LLM fallback when classification confidence falls below the configurable threshold.
- **Automated Triage & Routing**:
  - Categorization across support topics (Billing, Technical, Account, Delivery, Cancellation, etc.).
  - Priority scoring (Low, Medium, High, Critical) and sentiment analysis.
- **Knowledge Base Retrieval (RAG-lite)**:
  - Automatically matches incoming issues against support articles to suggest instant resolution steps.
- **Similar Ticket Matching**:
  - Computes similarity across previous historical tickets to surface prior resolutions.
- **Interactive Web Interface**:
  - Modern web dashboard (`/app/code.html`) for ticket triage, status management, filtering, and metrics.
  - Single ticket submission and bulk CSV ticket ingestion with live progress.
- **Production-Ready Backend**:
  - FastAPI with async request handling, CORS middleware, and Pydantic validation schemas.
  - SQLAlchemy ORM with SQLite (or configurable PostgreSQL/MySQL via `DATABASE_URL`).
  - Comprehensive test suite with 150+ unit and integration tests.

---

## Project Structure

```text
support-ticket-classifier/
├── backend/
│   ├── app/
│   │   ├── ai/               # Hybrid classification engine & Gemini integration
│   │   ├── db/               # SQLAlchemy models and session management
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Ticket, KB, similarity, and ML classifier services
│   │   └── main.py           # FastAPI application entrypoint
│   └── tests/                # Test suite (API, engine, validators)
├── data/
│   ├── knowledge_base/       # Knowledge base articles
│   ├── sample/               # Sample ticket CSVs and test datasets
│   └── raw/                  # Raw training records
├── docs/                     # Architecture and evaluation documentation
├── frontend/
│   └── web/                  # Web dashboard UI (HTML, CSS, JS)
├── scripts/                  # Training and evaluation helper scripts
├── .env.example              # Sample environment configuration
├── requirements.txt          # Python dependencies
└── README.md
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.11 / 3.12 / 3.13)
- Git

### 2. Clone Repository
```bash
git clone https://github.com/jatin125f/support_ticket_classifier.git
cd support_ticket_classifier
```

### 3. Create Virtual Environment
```bash
python -m venv .venv

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and add your Google Gemini API key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-2.5-flash
CONFIDENCE_THRESHOLD=0.30
DATABASE_URL=sqlite:///./support_tickets.db
CORS_ORIGINS=*
```

---

## Running the Application

### Start the FastAPI Server
```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Interactive API Docs (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative Docs (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Web Dashboard**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)

---

## Running Tests

Run the full pytest suite:
```bash
pytest
```

To run with coverage reporting:
```bash
pytest --cov=backend
```

---

## Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/tickets` | Submit and automatically classify a new support ticket |
| `GET` | `/api/tickets` | List tickets with optional status/category filtering |
| `GET` | `/api/tickets/{id}` | Retrieve details of a specific ticket |
| `PATCH` | `/api/tickets/{id}/status` | Update resolution status of a ticket |
| `POST` | `/api/tickets/bulk` | Ingest multiple tickets via CSV upload |
| `GET` | `/api/tickets/{id}/similar` | Find historically similar tickets |
| `GET` | `/api/analytics` | Summary metrics (category distribution, priority breakdowns) |
| `GET` | `/health` | Service health status |

---

## License

This project is licensed under the MIT License.