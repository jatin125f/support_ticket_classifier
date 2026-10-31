import csv
import io
import os
from typing import Optional

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.app.schemas import (
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate
)
from backend.app.ai.hybrid_engine import hybrid_classify
from backend.app.services.ticket_service import save_ticket
from backend.app.services.similarity import find_similar_tickets
from backend.app.services.kb_retriever import retrieve_knowledge, load_knowledge_base
from backend.app.db.session import SessionLocal
from backend.app.db.models import Ticket

app = FastAPI(
    title="AI Customer Support Ticket Classifier",
    description="AI-powered customer support ticket classification and triage operations API",
    version="1.0.0"
)

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount web frontend
frontend_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "web")
)
if os.path.exists(frontend_dir):
    app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/dashboard")
def dashboard_redirect():
    return RedirectResponse(url="/app/code.html")


@app.get("/queue")
def queue_redirect():
    return RedirectResponse(url="/app/ticket-queue.html")


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "AI Customer Support Ticket Classifier API is running",
        "docs_url": "/docs",
        "dashboard_url": "/app/code.html"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Create and classify a new ticket
@app.post("/tickets", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    clean_text = ticket.text.strip()
    if len(clean_text) < 3:
        raise HTTPException(
            status_code=400,
            detail="Ticket text must be at least 3 characters long."
        )

    result = hybrid_classify(clean_text)

    saved_ticket = save_ticket(
        clean_text,
        result,
        db=db
    )

    return {
        "id": saved_ticket.id,
        "text": clean_text,
        "category": result["category"],
        "priority": result["priority"],
        "confidence": result["confidence"],
        "method": result["method"],
        "rule_prediction": result["rule_prediction"],
        "rule_confidence": result["rule_confidence"],
        "ml_prediction": result["ml_prediction"],
        "ml_confidence": result["ml_confidence"],
        "suggested_reply": result["suggested_reply"],
        "status": saved_ticket.status,
        "similar_tickets": result.get("similar_tickets", []),
        "knowledge_base": result.get("knowledge_base", []),
    }


# Get all tickets with optional filtering and search
@app.get("/tickets")
def get_tickets(
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)

    if category and category.strip() and category != "All Categories":
        query = query.filter(Ticket.category == category.strip())

    if priority and priority.strip() and priority != "All Priorities":
        query = query.filter(Ticket.priority == priority.strip())

    if status and status.strip() and status != "All Statuses":
        query = query.filter(Ticket.status == status.strip())

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(Ticket.text.ilike(term))

    tickets = query.order_by(Ticket.id.desc()).all()

    return [
        {
            "id": ticket.id,
            "text": ticket.text,
            "category": ticket.category,
            "priority": ticket.priority,
            "confidence": ticket.confidence,
            "method": ticket.method,
            "suggested_reply": ticket.suggested_reply,
            "status": ticket.status,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None
        }
        for ticket in tickets
    ]


# Get a single ticket with similar tickets and knowledge base reference
@app.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Exclude the current ticket from similar tickets
    similar_tickets = find_similar_tickets(
        ticket.text,
        top_k=3,
        exclude_text=ticket.text
    )

    # Retrieve relevant knowledge base policy document
    knowledge_base = retrieve_knowledge(ticket.text, top_k=1)

    return {
        "id": ticket.id,
        "text": ticket.text,
        "category": ticket.category,
        "priority": ticket.priority,
        "confidence": ticket.confidence,
        "method": ticket.method,
        "suggested_reply": ticket.suggested_reply,
        "status": ticket.status,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "similar_tickets": similar_tickets,
        "knowledge_base": knowledge_base
    }


# Update ticket status
@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    allowed_statuses = ["Open", "In Progress", "Resolved"]
    normalized_status = status_update.status.strip()

    if normalized_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{status_update.status}'. Allowed statuses: {allowed_statuses}"
        )

    ticket.status = normalized_status
    db.commit()
    db.refresh(ticket)

    return {
        "message": "Ticket status updated successfully",
        "id": ticket.id,
        "status": ticket.status
    }


# Comprehensive ticket analytics
@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    total_tickets = db.query(Ticket).count()

    open_tickets = db.query(Ticket).filter(Ticket.status == "Open").count()
    in_progress_tickets = db.query(Ticket).filter(Ticket.status == "In Progress").count()
    resolved_tickets = db.query(Ticket).filter(Ticket.status == "Resolved").count()
    high_priority_tickets = db.query(Ticket).filter(Ticket.priority == "High").count()
    payment_tickets = db.query(Ticket).filter(Ticket.category == "Payment").count()

    # Category counts
    all_categories = ["Payment", "Account", "Delivery", "Cancellation", "Refund", "Unknown"]
    category_counts = {}
    for cat in all_categories:
        category_counts[cat] = db.query(Ticket).filter(Ticket.category == cat).count()

    # Priority counts
    priority_counts = {
        "High": high_priority_tickets,
        "Medium": db.query(Ticket).filter(Ticket.priority == "Medium").count(),
        "Low": db.query(Ticket).filter(Ticket.priority == "Low").count()
    }

    # Status counts
    status_counts = {
        "Open": open_tickets,
        "In Progress": in_progress_tickets,
        "Resolved": resolved_tickets
    }

    # Classification method counts
    method_rows = db.query(Ticket.method).all()
    method_counts = {}
    for row in method_rows:
        m = row[0] or "unknown"
        method_counts[m] = method_counts.get(m, 0) + 1

    # Average confidence calculation
    confidence_rows = db.query(Ticket.confidence).all()
    avg_confidence = (
        round(sum(row[0] for row in confidence_rows) / len(confidence_rows), 3)
        if confidence_rows
        else 0.0
    )

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "high_priority_tickets": high_priority_tickets,
        "payment_tickets": payment_tickets,
        "category_counts": category_counts,
        "priority_counts": priority_counts,
        "status_counts": status_counts,
        "method_counts": method_counts,
        "avg_confidence": avg_confidence
    }


# Category-wise analytics endpoint
@app.get("/analytics/categories")
def get_category_analytics(db: Session = Depends(get_db)):
    categories = [
        "Payment",
        "Account",
        "Delivery",
        "Cancellation",
        "Refund",
        "Unknown"
    ]
    return {
        cat: db.query(Ticket).filter(Ticket.category == cat).count()
        for cat in categories
    }


# Knowledge base list endpoint
@app.get("/knowledge-base")
def get_knowledge_base():
    """
    Return all knowledge base policy documents.
    """
    docs = load_knowledge_base()
    return docs


# Bulk CSV ticket upload
@app.post("/tickets/bulk")
async def bulk_upload_tickets(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    content = await file.read()

    try:
        decoded_content = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            decoded_content = content.decode("latin-1")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="CSV file must be UTF-8 or compatible encoding"
            )

    reader = csv.DictReader(io.StringIO(decoded_content))

    if not reader.fieldnames or "text" not in [col.strip().lower() for col in reader.fieldnames]:
        raise HTTPException(
            status_code=400,
            detail="CSV must contain a 'text' column"
        )

    # Resolve text column key case-insensitively
    text_key = next((col for col in reader.fieldnames if col.strip().lower() == "text"), "text")

    processed_tickets = []
    errors = []
    row_number = 1

    for row in reader:
        row_number += 1
        raw_text = row.get(text_key, "").strip()

        if not raw_text:
            continue

        try:
            result = hybrid_classify(raw_text)
            saved_ticket = save_ticket(raw_text, result, db=db)

            processed_tickets.append({
                "id": saved_ticket.id,
                "text": raw_text,
                "category": result["category"],
                "priority": result["priority"],
                "confidence": result["confidence"],
                "method": result["method"],
                "status": saved_ticket.status
            })
        except Exception as e:
            errors.append({
                "row": row_number,
                "text": raw_text[:50],
                "error": str(e)
            })

    return {
        "message": "Bulk tickets processed successfully",
        "total_rows": len(processed_tickets) + len(errors),
        "successful_rows": len(processed_tickets),
        "failed_rows": len(errors),
        "errors": errors,
        "tickets": processed_tickets
    }