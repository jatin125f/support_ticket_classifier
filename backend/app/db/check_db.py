from backend.app.db.session import SessionLocal
from backend.app.db.models import Ticket


def check_database():

    db = SessionLocal()

    try:
        tickets = db.query(Ticket).all()

        print("\n===== DATABASE RECORDS =====")
        print("Total Tickets:", len(tickets))

        for ticket in tickets:
            print("\nID:", ticket.id)
            print("Text:", ticket.text)
            print("Category:", ticket.category)
            print("Priority:", ticket.priority)
            print("Confidence:", ticket.confidence)
            print("Method:", ticket.method)
            print("Status:", ticket.status)

    finally:
        db.close()


if __name__ == "__main__":
    check_database()