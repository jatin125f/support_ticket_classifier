import httpx
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 10.0
REQUIRED_TICKET_FIELDS = (
    "id",
    "text",
    "category",
    "priority",
    "confidence",
    "method",
    "status",
)

st.set_page_config(
    page_title="Ticket Detail & Suggested Reply",
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


def get_api_json(path: str):
    response = httpx.get(
        f"{API_BASE_URL}{path}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    try:
        return response.json()
    except ValueError as error:
        raise ValueError("The API returned invalid JSON.") from error


def stop_with_api_error(error: Exception, context: str) -> None:
    if isinstance(error, httpx.RequestError):
        st.error(
            f"{context}: could not connect to the backend at {API_BASE_URL}. "
            f"Confirm that FastAPI is running. Details: {error}"
        )
    elif isinstance(error, httpx.HTTPStatusError):
        st.error(
            f"{context}: the API returned HTTP {error.response.status_code}."
        )
    else:
        st.error(f"{context}: {error}")
    st.stop()


st.title("Ticket Detail & Suggested Reply")
st.write("Review the ticket, its supporting context, and the AI-drafted response.")

try:
    tickets = get_api_json("/tickets")
    if not isinstance(tickets, list):
        raise ValueError("Expected the ticket list endpoint to return a list.")

    ticket_ids = []
    for ticket in tickets:
        if not isinstance(ticket, dict) or not isinstance(ticket.get("id"), int):
            raise ValueError("The ticket list contains an invalid ticket record.")
        ticket_ids.append(ticket["id"])
except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as error:
    stop_with_api_error(error, "Could not load tickets")

if not ticket_ids:
    st.info("There are no tickets available to review.")
    st.stop()

selected_ticket_id = st.selectbox(
    "Select a ticket",
    ticket_ids,
    format_func=lambda ticket_id: f"Ticket #{ticket_id}",
    accept_new_options=False,
    filter_mode=None,
)

try:
    ticket = get_api_json(f"/tickets/{selected_ticket_id}")
    if not isinstance(ticket, dict):
        raise ValueError("Expected the ticket detail endpoint to return an object.")
    missing_fields = [
        field for field in REQUIRED_TICKET_FIELDS if field not in ticket
    ]
    if missing_fields:
        raise ValueError(
            "Ticket details are missing required fields: "
            + ", ".join(missing_fields)
        )

    similar_tickets = ticket.get("similar_tickets", [])
    knowledge_base = ticket.get("knowledge_base", [])
    if not isinstance(similar_tickets, list):
        raise ValueError("The similar_tickets field must be a list.")
    if not isinstance(knowledge_base, list):
        raise ValueError("The knowledge_base field must be a list.")
    if any(not isinstance(item, dict) for item in similar_tickets):
        raise ValueError("The API returned an invalid similar ticket record.")
    if any(not isinstance(item, dict) for item in knowledge_base):
        raise ValueError("The API returned an invalid knowledge-base record.")
except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as error:
    stop_with_api_error(error, f"Could not load ticket #{selected_ticket_id}")

with st.container(border=True):
    st.subheader(f"Ticket #{ticket['id']}")
    st.markdown("**Full ticket text**")
    st.write(ticket["text"])

    first_row = st.columns(3)
    first_row[0].metric("Category", ticket["category"])
    first_row[1].metric("Priority", ticket["priority"])
    first_row[2].metric("Confidence", ticket["confidence"])

    second_row = st.columns(2)
    second_row[0].metric("Classification method", ticket["method"])
    second_row[1].metric("Current status", ticket["status"])

st.subheader("AI Suggested Reply")
suggested_reply = ticket.get("suggested_reply")
if not isinstance(suggested_reply, str) or not suggested_reply.strip():
    st.warning("No suggested reply was returned for this ticket.")
    suggested_reply = ""

st.markdown("#### Human Review")
st.write(
    "Review the AI suggestion and edit the text below as needed before using it. "
    "Edits remain in this page only; no reply is sent or saved."
)
st.text_area(
    "Suggested reply (editable)",
    value=suggested_reply,
    height=180,
    key=f"suggested_reply_{selected_ticket_id}",
)

st.subheader("Similar Tickets")
if similar_tickets:
    st.dataframe(
        [
            {
                "Ticket ID": item.get("id", "N/A"),
                "Ticket text": item.get("text", "N/A"),
                "Category": item.get("category", "N/A"),
                "Similarity": item.get("similarity", "N/A"),
            }
            for item in similar_tickets
        ],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("No similar tickets were returned.")

st.subheader("Knowledge Base")
if knowledge_base:
    for index, item in enumerate(knowledge_base, start=1):
        source = item.get("name") or item.get("source") or f"Source {index}"
        similarity = item.get("similarity")
        title = f"{source}"
        if similarity is not None:
            title += f" — similarity: {similarity}"
        with st.expander(title):
            st.write(item.get("content", "No content was returned."))
else:
    st.info("No knowledge-base results were returned.")