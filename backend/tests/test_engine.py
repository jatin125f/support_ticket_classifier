import pytest

import backend.app.ai.hybrid_engine as hybrid_engine
from backend.app.ai.hybrid_engine import hybrid_classify
from backend.app.services.preprocess import preprocess_text
from backend.app.services.rule_engine import classify_by_rules
from backend.app.services.sla import calculate_priority
from backend.app.services.ml_classifier import classify_with_ml
from backend.app.services.similarity import find_similar_tickets
from backend.app.services.kb_retriever import retrieve_knowledge
from backend.app.services.reply_drafter import draft_reply


def test_preprocess_text():
    raw = "Hello! My PAYMENT was deducted... 123"
    cleaned = preprocess_text(raw)
    assert "payment" in cleaned
    assert "123" not in cleaned
    assert "!" not in cleaned


def test_rule_classification():
    res = classify_by_rules("Please cancel my order")
    assert res["category"] == "Cancellation"
    assert res["confidence"] == 1.0


def test_ml_classification():
    res = classify_with_ml("I forgot my account password")
    assert res["category"] == "Account"
    assert res["confidence"] > 0


@pytest.mark.parametrize(
    ("text", "expected_category"),
    [
        ("My payment failed", "Payment"),
        ("Where is my package?", "Delivery"),
        ("I forgot my password", "Account"),
        ("I want a refund", "Refund"),
        ("Please cancel my order", "Cancellation"),
    ],
)
def test_clear_rule_match_takes_precedence(text, expected_category):
    result = hybrid_classify(text)

    assert result["category"] == expected_category
    assert result["method"] == "rules"
    assert result["confidence"] == result["rule_confidence"]


@pytest.mark.parametrize(
    "text",
    [
        "My item is missing",
        "My package is missing",
        "My product is missing",
        "My order is missing",
        "My parcel is missing",
        "item missing",
        "item is missing",
        "product missing",
        "product is missing",
        "package missing",
        "package is missing",
        "parcel missing",
        "parcel is missing",
        "item not received",
        "package not received",
        "order not received",
        "shows delivered but not received",
        "My order was delivered but I did not receive it",
    ],
)
def test_missing_item_tickets_are_delivery_and_medium_priority(text):
    result = hybrid_classify(text)

    assert result["category"] == "Delivery"
    assert result["priority"] == "Medium"


@pytest.mark.parametrize(
    "text",
    [
        "item missing",
        "item is missing",
        "product missing",
        "product is missing",
        "package missing",
        "package is missing",
        "parcel missing",
        "parcel is missing",
        "item not received",
        "product not received",
        "package not received",
        "parcel not received",
        "order not received",
        "item is not there",
        "product is not there",
        "item isn't there",
        "product isn't there",
        "item was not there",
        "product was not there",
        "item wasn't there",
        "product wasn't there",
        "item not in package",
        "product not in package",
        "item missing from package",
        "product missing from package",
        "item missing from parcel",
        "product missing from parcel",
        "item missing from order",
        "product missing from order",
        "missing from package",
        "missing from parcel",
        "missing from order",
        "missing from my package",
        "item missing in my package",
        "package arrived but item is missing",
        "package received but item is missing",
        "parcel arrived but item is missing",
        "parcel received but item is missing",
        "order received but item is missing",
        "order received but item is not there",
        "package received but product is not there",
        "parcel received but product is not there",
        "received the package but item is missing",
        "received the parcel but item is missing",
        "received the order but item is missing",
        "received package but did not receive the item",
        "received parcel but did not receive the item",
        "received order but did not receive the item",
        "delivered but not received",
        "shows delivered but not received",
        "marked delivered but not received",
        "says delivered but I did not receive it",
        "says delivered but I haven't received it",
        "delivery shows delivered but item not received",
        "package says delivered but I didn't get it",
        "parcel says delivered but I didn't get it",
        "I didn't receive my item",
        "I did not receive my item",
        "I haven't received my item",
        "I have not received my item",
        "I never received my item",
        "I didn't get my item",
        "I did not get my item",
        "I haven't got my item",
        "I never got my item",
        "My item hasn't arrived",
        "Order received but item is not there",
        "My product is not there",
        "Package arrived but item is missing",
        "I received the parcel but did not receive the item",
        "Shows delivered but I did not receive it",
        "I never received my product",
    ],
)
def test_missing_delivery_phrases_are_consistent(text):
    assert classify_by_rules(text)["category"] == "Delivery"
    assert calculate_priority(text) == "Medium"
    assert draft_reply(text, "Delivery", []) == (
        "We understand that your item is missing. Please check your order "
        "tracking for the latest delivery status. If the tracking shows that "
        "the order was delivered but you have not received it, please contact "
        "our support team so we can investigate the issue."
    )


def test_standalone_missing_is_not_delivery():
    assert classify_by_rules("missing")["category"] == "Unknown"
    assert calculate_priority("missing") == "Low"


def test_delayed_delivery_reply_and_priority_are_unchanged():
    result = classify_by_rules("My package is delayed")
    assert result["category"] == "Delivery"
    assert calculate_priority("My package is delayed") == "Medium"
    reply = draft_reply("My package is delayed", "Delivery", [{"content": "policy"}])
    assert "facing a delivery issue" in reply
    assert "your item is missing" not in reply


def test_unknown_rule_uses_ml_result(monkeypatch):
    monkeypatch.setattr(
        hybrid_engine,
        "classify_by_rules",
        lambda text: {"category": "Unknown", "confidence": 0.0},
    )
    monkeypatch.setattr(
        hybrid_engine,
        "classify_with_ml",
        lambda text: {
            "category": "Payment",
            "confidence": 0.8,
            "method": "huggingface_zero_shot",
        },
    )
    monkeypatch.setattr(hybrid_engine, "calculate_priority", lambda text: "Low")
    monkeypatch.setattr(hybrid_engine, "find_similar_tickets", lambda text: [])
    monkeypatch.setattr(hybrid_engine, "retrieve_knowledge", lambda text: [])
    monkeypatch.setattr(
        hybrid_engine,
        "draft_reply",
        lambda text, category, knowledge_base: "Thanks for contacting support.",
    )

    result = hybrid_classify("An uncommon support request")

    assert result["category"] == "Payment"
    assert result["method"] == "ml"
    assert result["confidence"] == 0.8


def test_payment_ticket():
    result = hybrid_classify("My payment was deducted")
    assert result["category"] == "Payment"
    assert result["priority"] == "High"
    assert "suggested_reply" in result


def test_account_ticket():
    result = hybrid_classify("I forgot my password")
    assert result["category"] == "Account"


def test_delivery_ticket():
    result = hybrid_classify("Where is my package?")
    assert result["category"] == "Delivery"


def test_refund_ticket():
    result = hybrid_classify("I want a refund for my damaged product")
    assert result["category"] == "Refund"
    assert result["priority"] == "High"


def test_cancellation_ticket():
    result = hybrid_classify("Please cancel my order immediately")
    assert result["category"] == "Cancellation"
    assert result["priority"] == "High"


def test_similarity_search():
    results = find_similar_tickets("Where is my package?", top_k=2)
    assert isinstance(results, list)
    if results:
        assert "similarity" in results[0]
        assert "text" in results[0]


def test_knowledge_base_retrieval():
    kb = retrieve_knowledge("My payment was deducted", top_k=1)
    assert len(kb) > 0
    assert kb[0]["name"] == "payment"
    assert "Payment" in kb[0]["content"]


def test_suggested_reply():
    kb = retrieve_knowledge("Please cancel my order", top_k=1)
    reply = draft_reply("Please cancel my order", "Cancellation", kb)
    assert "cancel" in reply.lower()


@pytest.mark.parametrize(
    "text",
    [
        "My item is missing",
        "My package is missing",
        "My product is missing",
        "My parcel is missing",
        "item missing",
        "product missing",
        "package missing",
        "parcel missing",
        "item not received",
        "package not received",
        "order not received",
        "shows delivered but not received",
        "My order was delivered but I did not receive it",
    ],
)
def test_missing_delivery_reply(text):
    reply = draft_reply(text, "Delivery", [])

    assert reply == (
        "We understand that your item is missing. Please check your order "
        "tracking for the latest delivery status. If the tracking shows that "
        "the order was delivered but you have not received it, please contact "
        "our support team so we can investigate the issue."
    )


def test_unrelated_delivery_reply_is_unchanged():
    reply = draft_reply("My package is delayed", "Delivery", [{"content": "policy"}])

    assert "facing a delivery issue" in reply
    assert "your item is missing" not in reply


def test_low_confidence_fallback():
    # An obscure or unusual prompt that has very low ML/rule confidence
    result = hybrid_classify("The purple chameleon is dancing on a wire in the moonlight")
    assert "category" in result
    assert "method" in result
    # It will either be gemini fallback or low confidence classification
    assert result["confidence"] <= 1.0