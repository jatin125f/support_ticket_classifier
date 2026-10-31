import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DATA_PATH = DATA_DIR / "sample" / "tickets.csv"
KB_DIR = DATA_DIR / "knowledge_base"
MODEL_PATH = Path(__file__).resolve().parent / "services" / "ticket_classifier.pkl"

# Project info
PROJECT_NAME = "AI-Powered Customer Support Ticket Classifier"
API_VERSION = "1.0.0"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./support_tickets.db")

# AI / LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.30"))

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
