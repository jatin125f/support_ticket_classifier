import pytest
from backend.app.services.sla import calculate_priority
from backend.app.ai.validators import (
    validate_category,
    validate_priority,
    is_valid_status,
    validate_ticket_text
)


def test_high_priority():
    result = calculate_priority("My payment was deducted")
    assert result == "High"


@pytest.mark.parametrize(
    "text",
    [
        "My item is missing",
        "My package is missing",
        "The product is missing",
        "My order is missing",
        "The item missing from my delivery",
        "The package missing from my delivery",
        "The product missing from my order",
        "The order missing from my account",
    ],
)
def test_missing_item_or_order_is_medium_priority(text):
    assert calculate_priority(text) == "Medium"


def test_existing_high_priority_examples_remain_high():
    assert calculate_priority("Someone hacked my account") == "High"
    assert calculate_priority("My refund is for a damaged product") == "High"
    assert calculate_priority("Please cancel my order immediately") == "High"


def test_medium_priority():
    result = calculate_priority("My package is delayed")
    assert result == "Medium"


def test_low_priority():
    result = calculate_priority("When will my package arrive?")
    assert result == "Low"


def test_unrelated_missing_text_remains_low_priority():
    assert calculate_priority("My account information is missing") == "Low"


def test_priority_validator():
    assert validate_priority("high") == "High"
    assert validate_priority("MEDIUM") == "Medium"
    assert validate_priority("invalid_val") == "Low"


def test_category_validator():
    assert validate_category("payment") == "Payment"
    assert validate_category("REFUND") == "Refund"
    assert validate_category("invalid_cat") == "Unknown"


def test_status_validator():
    assert is_valid_status("Open") is True
    assert is_valid_status("In Progress") is True
    assert is_valid_status("Resolved") is True
    assert is_valid_status("ClosedPermanently") is False


def test_ticket_text_validator():
    assert validate_ticket_text("Hello world") == "Hello world"
    with pytest.raises(ValueError):
        validate_ticket_text("  a ")