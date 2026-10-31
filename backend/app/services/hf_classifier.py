from functools import lru_cache
from math import isfinite
from typing import Any

MODEL_NAME = "cross-encoder/nli-deberta-v3-small"

CATEGORY_DESCRIPTIONS = {
    "Payment": "payment, billing, or transaction issues",
    "Account": "account access, login, password, or account settings",
    "Delivery": "delivery, shipping, or order arrival",
    "Cancellation": "cancelling an order",
    "Refund": "refunds, returns, or damaged products",
    "Unknown": "a customer-support issue outside the listed categories",
}


@lru_cache(maxsize=1)
def _get_classifier() -> Any:
    """Load on first use and reuse the model across Streamlit reruns."""
    from transformers import pipeline

    return pipeline(
        "zero-shot-classification",
        model=MODEL_NAME,
        device=-1,
    )


def classify_with_huggingface(text: str) -> dict:
    """Classify a ticket into one of the canonical support categories."""
    classifier = _get_classifier()
    result = classifier(
        text,
        candidate_labels=list(CATEGORY_DESCRIPTIONS.values()),
        multi_label=False,
    )

    if not isinstance(result, dict):
        raise ValueError("Hugging Face classifier returned an invalid result.")

    labels = result.get("labels")
    scores = result.get("scores")
    if not isinstance(labels, list) or not labels or not isinstance(scores, list):
        raise ValueError("Hugging Face classifier returned no labels or scores.")

    label_to_category = {
        description: category
        for category, description in CATEGORY_DESCRIPTIONS.items()
    }

    try:
        best_index = max(range(len(labels)), key=lambda index: float(scores[index]))
        description = labels[best_index]
        confidence = float(scores[best_index])
        category = label_to_category[description]
    except (IndexError, KeyError, TypeError, ValueError) as error:
        raise ValueError(
            "Hugging Face classifier returned an unknown label or invalid score."
        ) from error

    if not isfinite(confidence):
        raise ValueError("Hugging Face classifier returned a non-finite score.")

    return {
        "category": category,
        "confidence": round(confidence, 2),
        "method": "huggingface_zero_shot",
    }
