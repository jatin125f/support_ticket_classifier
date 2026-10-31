import io
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == (
        "AI Customer Support Ticket Classifier API is running"
    )


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_ticket():
    response = client.post(
        "/tickets",
        json={"text": "My payment was deducted"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Payment"
    assert data["priority"] == "High"
    assert data["status"] == "Open"
    assert data["rule_prediction"] == "Payment"
    assert isinstance(data["rule_confidence"], float)
    assert isinstance(data["ml_prediction"], str)
    assert isinstance(data["ml_confidence"], float)
    assert "suggested_reply" in data
    assert "similar_tickets" in data
    assert "knowledge_base" in data


def test_create_ticket_validation_error():
    response = client.post(
        "/tickets",
        json={"text": "hi"},
    )
    assert response.status_code == 422 or response.status_code == 400


def test_get_tickets():
    response = client.get("/tickets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_tickets_with_filters():
    response = client.get("/tickets?category=Payment&priority=High&status=Open")
    assert response.status_code == 200
    tickets = response.json()
    assert isinstance(tickets, list)
    for t in tickets:
        assert t["category"] == "Payment"
        assert t["priority"] == "High"
        assert t["status"] == "Open"


def test_get_tickets_search():
    response = client.get("/tickets?search=payment")
    assert response.status_code == 200
    tickets = response.json()
    assert isinstance(tickets, list)
    assert len(tickets) > 0


def test_get_single_ticket():
    # First create a ticket
    create_res = client.post("/tickets", json={"text": "My order has not arrived yet"})
    assert create_res.status_code == 200
    ticket_id = create_res.json()["id"]

    # Fetch the ticket
    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ticket_id
    assert data["category"] == "Delivery"
    assert "similar_tickets" in data
    assert "knowledge_base" in data


def test_get_single_ticket_not_found():
    response = client.get("/tickets/9999999")
    assert response.status_code == 404


def test_update_ticket_status():
    create_res = client.post("/tickets", json={"text": "Please cancel my order immediately"})
    ticket_id = create_res.json()["id"]

    # Update to In Progress
    patch_res1 = client.patch(
        f"/tickets/{ticket_id}/status",
        json={"status": "In Progress"}
    )
    assert patch_res1.status_code == 200
    assert patch_res1.json()["status"] == "In Progress"

    # Update to Resolved
    patch_res2 = client.patch(
        f"/tickets/{ticket_id}/status",
        json={"status": "Resolved"}
    )
    assert patch_res2.status_code == 200
    assert patch_res2.json()["status"] == "Resolved"


def test_update_ticket_status_invalid():
    create_res = client.post("/tickets", json={"text": "I want a refund for damaged item"})
    ticket_id = create_res.json()["id"]

    response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={"status": "ClosedPermanently"}
    )
    assert response.status_code == 400


def test_analytics():
    response = client.get("/analytics")
    assert response.status_code == 200
    data = response.json()

    assert "total_tickets" in data
    assert "open_tickets" in data
    assert "in_progress_tickets" in data
    assert "resolved_tickets" in data
    assert "high_priority_tickets" in data
    assert "avg_confidence" in data
    assert "category_counts" in data
    assert "priority_counts" in data
    assert "status_counts" in data
    assert "method_counts" in data


def test_knowledge_base_endpoint():
    response = client.get("/knowledge-base")
    assert response.status_code == 200
    docs = response.json()
    assert isinstance(docs, list)
    assert len(docs) >= 5
    names = [doc["name"] for doc in docs]
    assert "payment" in names
    assert "account" in names


def test_bulk_upload_csv():
    csv_data = "id,text\n1,My payment failed on checkout\n2,Package was delayed\n"
    file = io.BytesIO(csv_data.encode("utf-8"))

    response = client.post(
        "/tickets/bulk",
        files={"file": ("bulk_test.csv", file, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["successful_rows"] == 2
    assert data["failed_rows"] == 0
    assert len(data["tickets"]) == 2


def test_bulk_upload_invalid_file():
    txt_data = b"This is not a CSV file."
    file = io.BytesIO(txt_data)

    response = client.post(
        "/tickets/bulk",
        files={"file": ("invalid.txt", file, "text/plain")}
    )
    assert response.status_code == 400