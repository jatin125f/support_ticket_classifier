import httpx
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"
TICKET_STATUSES = ["Open", "In Progress", "Resolved"]

st.set_page_config(page_title="Ticket Queue", page_icon="🎫", layout="wide")
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
    response = httpx.get(f"{API_BASE_URL}{path}", timeout=10.0)
    response.raise_for_status()
    return response.json()


st.title("Ticket Queue")
st.write("Review, search, and update the status of customer support tickets.")

refresh_clicked = st.button("Refresh", type="secondary")
try:
    tickets = get_api_json("/tickets")
    if not isinstance(tickets, list):
        raise ValueError("The ticket API returned an unexpected response.")
except httpx.RequestError as error:
    st.error(
        f"Could not connect to the ticket API at {API_BASE_URL}. "
        f"Confirm the FastAPI backend is running. Details: {error}"
    )
    st.stop()
except httpx.HTTPStatusError as error:
    st.error(f"Ticket API returned HTTP {error.response.status_code}.")
    st.stop()
except ValueError as error:
    st.error(f"Could not read tickets from the API: {error}")
    st.stop()

if refresh_clicked:
    st.success("Ticket queue refreshed.")

if "queue_status_success" in st.session_state:
    st.success(st.session_state.pop("queue_status_success"))

category_options = ["All Categories"] + sorted(
    {ticket.get("category", "Unknown") for ticket in tickets}
)
priority_options = ["All Priorities"] + sorted(
    {ticket.get("priority", "Unknown") for ticket in tickets}
)
status_options = ["All Statuses"] + sorted(
    {ticket.get("status", "Unknown") for ticket in tickets}
)

filter_col1, filter_col2, filter_col3 = st.columns(3)
selected_category = filter_col1.selectbox(
    "Category",
    category_options,
    accept_new_options=False,
    filter_mode=None,
)
selected_priority = filter_col2.selectbox(
    "Priority",
    priority_options,
    accept_new_options=False,
    filter_mode=None,
)
selected_status = filter_col3.selectbox(
    "Status",
    status_options,
    accept_new_options=False,
    filter_mode=None,
)

filtered_tickets = [
    ticket
    for ticket in tickets
    if (selected_category == "All Categories"
        or ticket.get("category") == selected_category)
    and (selected_priority == "All Priorities"
         or ticket.get("priority") == selected_priority)
    and (selected_status == "All Statuses"
         or ticket.get("status") == selected_status)
]

st.caption(f"{len(filtered_tickets)} ticket(s)")
table_rows = [
    {
        "Ticket ID": ticket.get("id", "N/A"),
        "Ticket text": ticket.get("text", ""),
        "Category": ticket.get("category", "N/A"),
        "Priority": ticket.get("priority", "N/A"),
        "Confidence": ticket.get("confidence", "N/A"),
        "Method": ticket.get("method", "N/A"),
        "Status": ticket.get("status", "N/A"),
    }
    for ticket in filtered_tickets
]
st.dataframe(table_rows, hide_index=True, use_container_width=True)

st.subheader("Ticket details")
if not filtered_tickets:
    st.info("No tickets match the selected filters.")
else:
    ticket_ids = [ticket["id"] for ticket in filtered_tickets if "id" in ticket]
    if not ticket_ids:
        st.info("The API returned tickets without ticket IDs.")
    else:
        selected_ticket_id = st.selectbox(
            "Select a ticket to review",
            ticket_ids,
            format_func=lambda ticket_id: f"Ticket #{ticket_id}",
            accept_new_options=False,
            filter_mode=None,
        )

        try:
            selected_ticket = get_api_json(f"/tickets/{selected_ticket_id}")
            if not isinstance(selected_ticket, dict):
                raise ValueError("The ticket details API returned an unexpected response.")
        except httpx.RequestError as error:
            st.error(f"Could not connect to the ticket API: {error}")
            st.stop()
        except httpx.HTTPStatusError as error:
            st.error(
                f"Could not load ticket #{selected_ticket_id}: "
                f"HTTP {error.response.status_code}."
            )
            st.stop()
        except ValueError as error:
            st.error(f"Could not read ticket details: {error}")
            st.stop()

        with st.container(border=True):
            st.markdown(f"### Ticket #{selected_ticket.get('id', selected_ticket_id)}")
            st.markdown("**Full ticket text**")
            st.write(selected_ticket.get("text", "No ticket text was returned."))

            detail_col1, detail_col2 = st.columns(2)
            detail_col1.metric("Category", selected_ticket.get("category", "N/A"))
            detail_col2.metric("Priority", selected_ticket.get("priority", "N/A"))

            detail_col3, detail_col4 = st.columns(2)
            detail_col3.metric("Confidence", selected_ticket.get("confidence", "N/A"))
            detail_col4.metric(
                "Classification method", selected_ticket.get("method", "N/A")
            )
            st.metric("Status", selected_ticket.get("status", "N/A"))

        st.markdown("#### Update status")
        current_status = selected_ticket.get("status", "Open")
        status_index = (
            TICKET_STATUSES.index(current_status)
            if current_status in TICKET_STATUSES
            else 0
        )
        new_status = st.selectbox(
            "Ticket status",
            TICKET_STATUSES,
            index=status_index,
            key=f"ticket_status_{selected_ticket_id}",
            accept_new_options=False,
            filter_mode=None,
        )

        if st.button("Save Status", type="primary"):
            try:
                response = httpx.patch(
                    f"{API_BASE_URL}/tickets/{selected_ticket_id}/status",
                    json={"status": new_status},
                    timeout=10.0,
                )
                response.raise_for_status()
                result = response.json()
                st.session_state["queue_status_success"] = result.get(
                    "message", "Ticket status updated successfully."
                )
                st.rerun()
            except httpx.RequestError as error:
                st.error(f"Could not connect to the ticket API: {error}")
            except httpx.HTTPStatusError as error:
                try:
                    detail = error.response.json().get("detail")
                except ValueError:
                    detail = error.response.text
                st.error(
                    detail or f"Status update failed with HTTP "
                    f"{error.response.status_code}."
                )
            except ValueError as error:
                st.error(f"Could not read the status update response: {error}")