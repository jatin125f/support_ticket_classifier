import os
from dotenv import load_dotenv
from backend.app.ai.llm_client import generate_gemini_response

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

ALLOWED_CATEGORIES = {
    "Payment",
    "Account",
    "Delivery",
    "Cancellation",
    "Refund",
    "Unknown"
}


def llm_fallback(text: str) -> dict:
    """
    LLM fallback using Gemini API for ambiguous or low-confidence tickets.
    """
    prompt = f"""You are an AI customer support classifier.

Classify the following customer support ticket into exactly one of these categories:
Payment
Account
Delivery
Cancellation
Refund
Unknown

Customer ticket:
"{text}"

Return ONLY the category name. Nothing else."""

    try:
        raw_output = generate_gemini_response(prompt, model_name=MODEL_NAME)

        if not raw_output:
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "method": "gemini_error"
            }

        cleaned = raw_output.strip().strip('"').strip("'").title()

        if cleaned not in ALLOWED_CATEGORIES:
            matched = None
            for cat in ALLOWED_CATEGORIES:
                if cat.lower() in cleaned.lower():
                    matched = cat
                    break
            cleaned = matched if matched else "Unknown"

        return {
            "category": cleaned,
            "confidence": 0.80 if cleaned != "Unknown" else 0.20,
            "method": "gemini"
        }

    except Exception:
        return {
            "category": "Unknown",
            "confidence": 0.0,
            "method": "gemini_error"
        }