import httpx
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 10.0
CATEGORY_NAMES = (
    "Payment",
    "Account",
    "Delivery",
    "Cancellation",
    "Refund",
    "Unknown",
)
PRIORITY_NAMES = ("High", "Medium", "Low")
STATUS_NAMES = ("Open", "In Progress", "Resolved")
COUNT_FIELDS = (
    "total_tickets",
    "open_tickets",
    "in_progress_tickets",
    "resolved_tickets",
)

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")
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


def get_analytics():
    response = httpx.get(
        f"{API_BASE_URL}/analytics",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    try:
        return response.json()
    except ValueError as error:
        raise ValueError("The analytics API returned invalid JSON.") from error


def validate_counts(value, expected_names, field_name):
    if not isinstance(value, dict):
        raise ValueError(f"The analytics API returned invalid {field_name}.")

    for name in expected_names:
        count = value.get(name)
        if type(count) is not int or count < 0:
            raise ValueError(f"The analytics API returned invalid {field_name}.")

    return value


def validate_analytics(data):
    if not isinstance(data, dict):
        raise ValueError("The analytics API returned an unexpected response.")

    for field in COUNT_FIELDS:
        count = data.get(field)
        if type(count) is not int or count < 0:
            raise ValueError("The analytics API returned invalid ticket totals.")

    validate_counts(data.get("category_counts"), CATEGORY_NAMES, "category counts")
    validate_counts(data.get("priority_counts"), PRIORITY_NAMES, "priority counts")
    validate_counts(data.get("status_counts"), STATUS_NAMES, "status counts")
    return data


st.title("Ticket Analytics")
st.write("Explore ticket volume and distribution using the current ticket records.")

refresh_clicked = st.button("Refresh", type="secondary")
try:
    analytics = validate_analytics(get_analytics())
except httpx.RequestError:
    st.error(
        f"Could not connect to the analytics API at {API_BASE_URL}. "
        "Confirm that the FastAPI backend is running."
    )
    st.stop()
except httpx.HTTPStatusError as error:
    st.error(f"The analytics API returned HTTP {error.response.status_code}.")
    st.stop()
except ValueError as error:
    st.error(f"Could not read ticket analytics: {error}")
    st.stop()

if refresh_clicked:
    st.success("Analytics refreshed.")

metric_columns = st.columns(4)
metric_columns[0].metric("Total tickets", analytics["total_tickets"])
metric_columns[1].metric("Open", analytics["open_tickets"])
metric_columns[2].metric("In Progress", analytics["in_progress_tickets"])
metric_columns[3].metric("Resolved", analytics["resolved_tickets"])

if analytics["total_tickets"] == 0:
    st.info("There are no tickets to analyze yet. Analytics will appear here once tickets are added.")

st.subheader("Ticket counts")
count_columns = st.columns(3)
count_sections = (
    ("Category-wise ticket count", "category_counts", CATEGORY_NAMES),
    ("Priority-wise ticket count", "priority_counts", PRIORITY_NAMES),
    ("Status-wise ticket count", "status_counts", STATUS_NAMES),
)
for column, (title, field, names) in zip(count_columns, count_sections):
    column.markdown(f"#### {title}")
    column.dataframe(
        [{"Name": name, "Tickets": analytics[field][name]} for name in names],
        hide_index=True,
        use_container_width=True,
    )

st.subheader("Distribution")
chart_columns = st.columns(2)
category_chart_data = {
    name: analytics["category_counts"][name] for name in CATEGORY_NAMES
}
priority_chart_data = {
    name: analytics["priority_counts"][name] for name in PRIORITY_NAMES
}
with chart_columns[0]:
    st.markdown("#### Category distribution")
    st.bar_chart(category_chart_data, y_label="Tickets", x_label="Category")
with chart_columns[1]:
    st.markdown("#### Priority distribution")
    st.bar_chart(priority_chart_data, y_label="Tickets", x_label="Priority")