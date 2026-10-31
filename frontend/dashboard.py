import logging

import httpx
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 60.0


st.set_page_config(
    page_title="AI-Powered Customer Support Ticket Classifier",
    page_icon="🎫",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1100px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.2);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("Support Desk")
    st.caption("AI-powered ticket triage")
    st.divider()

st.title("AI-Powered Customer Support Ticket Classifier")
st.write(
    "Review and classify incoming customer support requests from one workspace."
)

st.subheader("Dashboard")
st.write(
    "Enter a customer ticket below to prepare it for classification and agent review."
)

logger = logging.getLogger(__name__)


def display_classification_result(result):
    st.subheader("Classification Result")

    category_col, priority_col, confidence_col, method_col = st.columns(4)
    category_col.metric("Category", result.get("category", "N/A"))
    priority_col.metric("Priority", result.get("priority", "N/A"))
    confidence_col.metric("Confidence", result.get("confidence", "N/A"))
    method_col.metric("Classification Method", result.get("method", "N/A"))

    st.markdown("#### Model details")
    rule_col, ml_col = st.columns(2)
    rule_col.metric("Rule prediction", result["rule_prediction"])
    rule_col.metric("Rule confidence", result["rule_confidence"])
    ml_col.metric("ML prediction", result["ml_prediction"])
    ml_col.metric("ML confidence", result["ml_confidence"])

    st.markdown("#### Suggested reply")
    st.write(result.get("suggested_reply") or "No suggested reply was returned.")

    similar_tickets = result.get("similar_tickets") or []
    st.markdown("#### Similar tickets")
    if similar_tickets:
        st.dataframe(
            [
                {
                    "Ticket ID": ticket.get("id", "N/A"),
                    "Ticket text": ticket.get("text", "N/A"),
                    "Category": ticket.get("category", "N/A"),
                    "Priority": ticket.get("priority", "N/A"),
                    "Similarity": ticket.get("similarity", "N/A"),
                }
                for ticket in similar_tickets
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No similar tickets were returned.")

    knowledge_base = result.get("knowledge_base") or []
    st.markdown("#### Knowledge-base results")
    if knowledge_base:
        for item in knowledge_base:
            name = item.get("name", "Knowledge-base document")
            similarity = item.get("similarity", "N/A")
            with st.expander(f"{name} — similarity: {similarity}"):
                st.write(item.get("content", "No content was returned."))
    else:
        st.info("No knowledge-base results were returned.")


with st.container(border=True):
    st.markdown("### Classify a customer ticket")
    ticket_text = st.text_area(
        "Ticket description",
        placeholder="For example: I was charged for my order, but it is still showing as pending.",
        height=180,
        help="Paste the customer's message here.",
    )

    if st.button("Classify Ticket", type="primary"):
        if not ticket_text.strip():
            st.warning("Enter a ticket description before continuing.")
        else:
            try:
                for attempt in range(2):
                    try:
                        response = httpx.post(
                            f"{API_BASE_URL}/tickets",
                            json={"text": ticket_text.strip()},
                            timeout=REQUEST_TIMEOUT_SECONDS,
                        )
                        break
                    except (httpx.ConnectError, httpx.ConnectTimeout):
                        if attempt == 1:
                            raise
                response.raise_for_status()
                result = response.json()
                if not isinstance(result, dict):
                    raise ValueError("The ticket API returned an unexpected response.")
                display_classification_result(result)
            except Exception:
                logger.exception("Ticket classification failed.")
                st.error(
                    "Ticket classification could not be completed. Please try again. "
                    "If the problem continues, contact the system administrator."
                )
