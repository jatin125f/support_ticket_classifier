"""
Validators for ticket classification categories, priorities, and statuses.
"""

ALLOWED_CATEGORIES = [
    "Payment",
    "Account",
    "Delivery",
    "Cancellation",
    "Refund",
    "Unknown"
]

ALLOWED_PRIORITIES = [
    "High",
    "Medium",
    "Low"
]

ALLOWED_STATUSES = [
    "Open",
    "In Progress",
    "Resolved"
]


def validate_category(category: str) -> str:
    """Normalize and validate ticket category."""
    if not category:
        return "Unknown"
    norm = category.strip().title()
    return norm if norm in ALLOWED_CATEGORIES else "Unknown"


def validate_priority(priority: str) -> str:
    """Normalize and validate ticket priority."""
    if not priority:
        return "Low"
    norm = priority.strip().title()
    return norm if norm in ALLOWED_PRIORITIES else "Low"


def is_valid_status(status: str) -> bool:
    """Check if status is an allowed workflow status."""
    return status in ALLOWED_STATUSES


def validate_ticket_text(text: str) -> str:
    """Validate ticket text length and content."""
    cleaned = (text or "").strip()
    if len(cleaned) < 3:
        raise ValueError("Ticket text must be at least 3 characters long.")
    return cleaned
