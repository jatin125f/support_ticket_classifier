from backend.app.services.preprocess import preprocess_text 
from backend.app.services.missing_delivery import is_missing_delivery_issue


HIGH_PRIORITY_KEYWORDS = [
    "urgent",
    "immediately",
    "fraud",
    "hacked",
    "stolen",
    "charged twice",
    "money deducted",
    "payment was deducted",
    "payment failed",
    "account locked",
    "damaged",
]


MEDIUM_PRIORITY_KEYWORDS = [
    "delayed",
    "pending",
    "not received",
    "cannot login",
    "cancel",
    "refund",
]


def calculate_priority(text: str) -> str:
    text = preprocess_text(text)

    # Check high priority keywords
    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword in text:
            return "High"

    if is_missing_delivery_issue(text):
        return "Medium"

    # Check medium priority keywords
    for keyword in MEDIUM_PRIORITY_KEYWORDS:
        if keyword in text:
            return "Medium"

    # Everything else
    return "Low"    


if __name__ == "__main__":

    test_tickets = [
        "My payment was deducted but my order is pending",
        "My package is delayed",
        "How can I change my email?",
        "Someone hacked my account",
    ]

    print("\n===== PRIORITY ENGINE TEST =====")

    for ticket in test_tickets:
        priority = calculate_priority(ticket)

        print("\nTicket:", ticket)
        print("Priority:", priority)