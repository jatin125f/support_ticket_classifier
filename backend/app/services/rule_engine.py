from backend.app.services.preprocess import preprocess_text
from backend.app.services.missing_delivery import is_missing_delivery_issue


CATEGORY_KEYWORDS = {
    "Payment": [
        "payment",
        "paid",
        "charged",
        "deducted",
        "transaction",
        "card",
    ],
    "Account": [
        "password",
        "login",
        "account",
        "email",
        "username",
    ],
   "Delivery": [
    "package",
     "delivery",
    "arrive",
    "arrived",
    "delayed",
    "shipping",
    "where is my order",
],
    "Cancellation": [
        "cancel",
        "cancellation",
    ],
    "Refund": [
        "refund",
        "damaged",
        "broken",
        "return",
    ],
}


def classify_by_rules(text: str) -> dict:
    text = preprocess_text(text)

    # Give cancellation requests priority
    if "cancel" in text or "cancellation" in text:
        return {
            "category": "Cancellation",
            "confidence": 1.0,
        }

    if is_missing_delivery_issue(text):
        return {
            "category": "Delivery",
            "confidence": 1.0,
        }

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            if keyword in text:
                score += 1

        scores[category] = score

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    if best_score == 0:
        return {
            "category": "Unknown",
            "confidence": 0.0,
        }

    confidence = min(best_score / 3, 1.0)

    return {
        "category": best_category,
        "confidence": round(confidence, 2),
    }


if __name__ == "__main__":

    test_tickets = [
        "My payment was deducted but my order is pending",
        "I forgot my password",
        "Where is my package?",
        "I want to cancel my order",
        "I want a refund for my damaged product",
    ]

    print("\n===== RULE ENGINE TEST =====")

    for ticket in test_tickets:
        result = classify_by_rules(ticket)

        print("\nTicket:", ticket)
        print("Category:", result["category"])
        print("Confidence:", result["confidence"])