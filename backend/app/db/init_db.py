from sqlalchemy import text
from backend.app.db.session import engine, Base
from backend.app.db.models import Ticket


def init_database():
    Base.metadata.create_all(bind=engine)

    # Check and migrate columns safely for existing SQLite tables
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(tickets);")).fetchall()
            existing_columns = [row[1] for row in result]

            if "created_at" not in existing_columns:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN created_at DATETIME;"))
                conn.commit()
                print("Added 'created_at' column to tickets table.")
    except Exception as e:
        print(f"Schema check notice: {e}")

    print("Database initialized successfully!")
    print("Table 'tickets' is ready.")


if __name__ == "__main__":
    init_database()