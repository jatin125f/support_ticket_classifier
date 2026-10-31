# System Architecture & Design

This document details the architectural design and operational flow of the **AI Customer Support Ticket Classifier**.

---

## High-Level Overview

```text
[ Client Layer ]
  ├── Web Dashboard (/app/code.html)
  └── REST API Clients / Curl / External CRM
           │
           ▼
[ FastAPI Application Layer ] (backend/app/main.py)
  ├── CORS Middleware & Request Validation (Pydantic Schemas)
  ├── Static File Serving (/app)
  └── API Routes (/api/tickets, /api/analytics, /health)
           │
           ├──────────────────────────────┬──────────────────────────────┐
           ▼                              ▼                              ▼
[ Hybrid Classification Engine ]   [ Knowledge Base RAG ]      [ Similarity Engine ]
  ├── Local ML Classifier            ├── Knowledge Base Files    ├── TF-IDF Vectorizer
  │   (TF-IDF + SGD/LinearSVC)       │   (data/knowledge_base/)  └── Cosine Similarity
  │   Confidence >= 0.30?            └── Top-K Article Match         over Past Tickets
  │   ├── Yes ──> Final Prediction
  │   └── No  ──> Google Gemini API
  │               (LLM Fallback)
           │
           ▼
[ Data Persistence Layer ]
  ├── SQLAlchemy ORM (models.py)
  └── SQLite / PostgreSQL Database (support_tickets.db)
```

---

## Core Components

### 1. API & Presentation Layer
- **Framework**: FastAPI (Python 3)
- **Static Assets**: Hosted via FastAPI `StaticFiles` mounting at `/app`.
- **Validation**: Strict request payload schema checking via Pydantic (`TicketCreate`, `TicketStatusUpdate`).
- **Endpoints**:
  - `POST /api/tickets`: Single ticket ingest & triage.
  - `POST /api/tickets/bulk`: CSV batch ticket processing.
  - `GET /api/tickets`: Filterable query interface.
  - `PATCH /api/tickets/{id}/status`: Lifecycle tracking (`open`, `in_progress`, `resolved`, `closed`).
  - `GET /api/tickets/{id}/similar`: Surfacing historically related tickets.
  - `GET /api/analytics`: Aggregate metrics.

### 2. Hybrid Classification Engine
The system uses a two-tier classification pipeline:
1. **Tier 1 - Local Machine Learning (`classify_with_ml`)**:
   - Model: Scikit-learn pipeline (TF-IDF + Calibrated Classifier).
   - Speed: < 5ms inference latency.
   - Outputs: Predicted Category, Priority, Urgency, Confidence score.
2. **Tier 2 - Gemini LLM Fallback (`classify_with_gemini`)**:
   - Trigger: Activated when Tier 1 confidence is below the configured threshold (default `0.30`), or when novel vocabulary/ambiguity is detected.
   - Provider: Google GenAI (`gemini-2.5-flash`).
   - Outputs: Structured JSON matching the classification schema.

### 3. Knowledge Base & Similarity Retrieval
- **Knowledge Base (RAG-lite)**:
  - Vectorizes query ticket description against pre-indexed resolution articles in `data/knowledge_base/`.
  - Recommends the top relevant articles and actionable guidance to support agents.
- **Similar Ticket Engine**:
  - Computes cosine similarity across historical tickets stored in the database.
  - Helps agents identify recurring issues and reuse proven resolution steps.

### 4. Database Layer
- **ORM**: SQLAlchemy.
- **Model**: `Ticket` table tracking:
  - `id`, `text`, `customer_email`
  - `category`, `priority`, `urgency`
  - `confidence`, `classification_method` (`ml` vs `gemini`)
  - `status`, `assigned_to`, `created_at`, `updated_at`
