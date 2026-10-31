from backend.app.services.rule_engine import classify_by_rules
from backend.app.services.ml_classifier import classify_with_ml
from backend.app.services.sla import calculate_priority
from backend.app.services.llm_fallback import llm_fallback
from backend.app.services.similarity import find_similar_tickets
from backend.app.services.kb_retriever import retrieve_knowledge
from backend.app.services.reply_drafter import draft_reply
from backend.app.services.ticket_service import save_ticket


CONFIDENCE_THRESHOLD = 0.30


def hybrid_classify(text: str) -> dict:
    """
    Hybrid AI classification pipeline.

    Uses:
    1. Rule Engine
    2. ML Classifier
    3. LLM Fallback for low-confidence cases
    4. Priority Engine
    5. Similar Ticket Search
    6. Knowledge Base
    7. Suggested Reply
    """

    # Rule prediction
    rule_result = classify_by_rules(text)

    # ML prediction
    ml_result = classify_with_ml(text)

    # Priority
    priority = calculate_priority(text)

    # Similar tickets
    similar_tickets = find_similar_tickets(text)

    # Knowledge Base
    knowledge_base = retrieve_knowledge(text)

    if rule_result["category"] != "Unknown":
        final_category = rule_result["category"]
        confidence = rule_result["confidence"]
        method = "rules"
    else:
        final_category = ml_result["category"]
        confidence = ml_result["confidence"]
        method = "ml"

    # Low confidence → LLM fallback
    if confidence < CONFIDENCE_THRESHOLD:

        llm_result = llm_fallback(text)

        final_category = llm_result["category"]
        confidence = llm_result["confidence"]
        method = llm_result["method"]

    # Generate suggested reply
    suggested_reply = draft_reply(
        text,
        final_category,
        knowledge_base
    )

    return {
        "category": final_category,
        "priority": priority,
        "confidence": round(confidence, 2),
        "method": method,
        "similar_tickets": similar_tickets,
        "knowledge_base": knowledge_base,
        "suggested_reply": suggested_reply,

        "rule_prediction": rule_result["category"],
        "rule_confidence": rule_result["confidence"],

        "ml_prediction": ml_result["category"],
        "ml_confidence": ml_result["confidence"],
    }


if __name__ == "__main__":

    test_tickets = [
        "My payment was deducted but my order is pending",
        "I forgot my password",
        "Where is my package?",
        "I want a refund for my damaged product",
        "Please cancel my order",
        "Something strange happened and I need help",
    ]

    print("\n===== HYBRID AI ENGINE TEST =====")

    for ticket in test_tickets:

        result = hybrid_classify(ticket)
        saved_ticket = save_ticket(ticket, result)

        print("\nTicket:", ticket)
        print("Final Category:", result["category"])
        print("Priority:", result["priority"])
        print("Confidence:", result["confidence"])
        print("Method:", result["method"])

        print("Similar Tickets:")

        if result["similar_tickets"]:

            for similar_ticket in result["similar_tickets"]:

                print(
                    f"  #{similar_ticket['id']} | "
                    f"{similar_ticket['category']} | "
                    f"{similar_ticket['similarity']}"
                )

        else:

            print("  No similar tickets found.")

        print("Knowledge Base:")

        if result["knowledge_base"]:

            for kb in result["knowledge_base"]:

                print(
                    f"  {kb['name']} | "
                    f"Similarity: {kb['similarity']}"
                )

        else:

            print("  No relevant knowledge found.")

        print("Suggested Reply:")
        print(" ", result["suggested_reply"])