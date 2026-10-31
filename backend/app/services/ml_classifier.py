import logging
import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ticket_classifier.pkl")

# Keep the existing trained model available as the fallback.
model = joblib.load(MODEL_PATH)

logger = logging.getLogger(__name__)


def classify_with_ml(text: str) -> dict:
    """
    Use Hugging Face as the primary classifier and scikit-learn as a fallback.
    """
    try:
        # Import lazily so missing Hugging Face dependencies also trigger fallback.
        from backend.app.services.hf_classifier import classify_with_huggingface

        return classify_with_huggingface(text)
    except Exception:
        logger.exception(
            "Hugging Face classification failed; using the scikit-learn fallback."
        )

    # Fall back to the original scikit-learn/joblib prediction logic.
    # Predict category
    category = model.predict([text])[0]

    # Get confidence
    probabilities = model.predict_proba([text])[0]
    confidence = max(probabilities)

    return {
        "category": category,
        "confidence": round(float(confidence), 2),
        "method": "sklearn_fallback"
    }


if __name__ == "__main__":
    test_tickets = [
        "My payment was deducted but my order is pending",
        "I forgot my password",
        "Where is my package?",
        "I want a refund for my damaged product",
        "Please cancel my order",
    ]

    print("\n===== ML CLASSIFIER TEST =====")
    for ticket in test_tickets:
        result = classify_with_ml(ticket)
        print("\nTicket:", ticket)
        print("Category:", result["category"])
        print("Confidence:", result["confidence"])
        print("Method:", result["method"])