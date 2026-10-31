import os
import sys
import argparse
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.session import SessionLocal, engine, Base
from backend.app.db.models import Ticket
from backend.app.ai.hybrid_engine import hybrid_classify
from backend.app.services.ticket_service import save_ticket
from backend.app.db.init_db import init_database

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sample", "tickets.csv"))


def seed_database(reset: bool = False):
    init_database()
    db = SessionLocal()

    try:
        current_count = db.query(Ticket).count()
        print(f"Current tickets in database: {current_count}")

        if reset:
            print("Reset flag detected. Clearing existing tickets table...")
            db.query(Ticket).delete()
            db.commit()
            print("Cleared existing tickets.")
        elif current_count > 0:
            print("Database already has records. To cleanly reseed with sample dataset, run with '--reset'.")
            return

        if not os.path.exists(DATA_PATH):
            print(f"Dataset not found at {DATA_PATH}")
            return

        df = pd.read_csv(DATA_PATH)
        print(f"Seeding {len(df)} sample tickets through hybrid AI classification...")

        seeded = 0
        for _, row in df.iterrows():
            text = row["text"]
            result = hybrid_classify(text)
            save_ticket(text, result, db=db)
            seeded += 1

        print(f"Successfully seeded {seeded} tickets!")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed support ticket database with sample dataset.")
    parser.add_argument("--reset", action="store_true", help="Clear existing tickets before seeding")
    args = parser.parse_args()

    seed_database(reset=args.reset)
