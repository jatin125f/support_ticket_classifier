import re

from backend.app.services.preprocess import preprocess_text


_MISSING_DELIVERY_PATTERNS = (
    r"\b(?:item|product|package|parcel|order)\b"
    r"(?:\s+(?:is|are|was|were))?\s+missing\b",
    r"\bmissing\b(?:\s+\w+){0,3}\s+\b(?:item|product|package|parcel|order)\b",
    r"\b(?:item|product)\b.{0,35}\bnot\s+there\b",
    r"\b(?:item|product)\b.{0,35}\bnot\s+in\s+(?:the\s+)?(?:package|parcel|order)\b",
    r"\b(?:item|product)\b.{0,20}\bmissing\b.{0,20}\b"
    r"(?:from|in)\s+(?:(?:the|my|our|your)\s+)?(?:package|parcel|order)\b",
    r"\bmissing\b.{0,20}\bfrom\s+(?:(?:the|my|our|your)\s+)?"
    r"(?:package|parcel|order)\b",
    r"\b(?:item|product|package|parcel|order)\b.{0,35}\bnot\s+received\b",
    r"\b(?:did\s+not|have\s+not|has\s+not|never)\s+"
    r"(?:receiv(?:e|ed)|get|got)\b.{0,35}\b(?:item|product|package|parcel|order)\b",
    r"\b(?:item|product|package|parcel|order)\b.{0,35}\b"
    r"(?:not\s+arrived|never\s+arrived)\b",
    r"\bdelivered\b.{0,50}\b(?:not\s+received|did\s+not\s+receive|"
    r"have\s+not\s+received|has\s+not\s+received|did\s+not\s+get|"
    r"have\s+not\s+got|never\s+received|never\s+got)\b",
)


def is_missing_delivery_issue(text: str) -> bool:
    text = text.lower().replace("n't", " not")
    text = re.sub(
        r"\b(is|are|was|were|did|do|does|have|has|had)n\s+t\b",
        r"\1 not",
        text,
    )
    normalized_text = preprocess_text(text)
    return any(
        re.search(pattern, normalized_text)
        for pattern in _MISSING_DELIVERY_PATTERNS
    )
