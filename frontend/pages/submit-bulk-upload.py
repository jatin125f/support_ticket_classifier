import csv
import hashlib
import io

import httpx
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 60.0
TICKET_RESULT_FIELDS = (
    "id",
    "text",
    "category",
    "priority",
    "confidence",
    "method",
)

st.set_page_config(page_title="Bulk Ticket Upload", page_icon="🎫", layout="wide")
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


def parse_csv_upload(content: bytes):
    if not content:
        raise ValueError("The CSV file is empty.")

    try:
        decoded_content = content.decode("utf-8")
    except UnicodeDecodeError:
        decoded_content = content.decode("latin-1")

    try:
        rows = list(csv.reader(io.StringIO(decoded_content, newline=""), strict=True))
    except csv.Error as error:
        raise ValueError("The uploaded file is not a valid CSV.") from error

    if not rows or not rows[0]:
        raise ValueError("The CSV file must start with a header or ticket text.")

    header = rows[0]
    text_column = next(
        (column for column in header if column.strip().lower() == "text"),
        None,
    )
    is_headerless_sample = text_column is None and len(header) == 1
    if text_column is None and not is_headerless_sample:
        raise ValueError("The CSV must contain the required 'text' column.")

    if is_headerless_sample:
        columns = ["text"]
        data_rows = rows
    else:
        columns = header
        text_index = next(
            index
            for index, column in enumerate(header)
            if column.strip().lower() == "text"
        )
        data_rows = rows[1:]

    preview_rows = []
    ticket_texts = []
    for row in data_rows:
        if not row or not any(value.strip() for value in row):
            continue
        padded_row = row + [""] * max(0, len(columns) - len(row))
        preview_rows.append(dict(zip(columns, padded_row)))
        if is_headerless_sample:
            ticket_text = row[0].strip()
        elif text_index < len(row):
            ticket_text = row[text_index].strip()
        else:
            ticket_text = ""
        if ticket_text:
            ticket_texts.append(ticket_text)

    if not preview_rows or not ticket_texts:
        raise ValueError("The CSV contains no ticket text to upload.")

    if is_headerless_sample:
        normalized_csv = io.StringIO(newline="")
        writer = csv.writer(normalized_csv)
        writer.writerow(["text"])
        writer.writerows([[row[0]] for row in data_rows if row and row[0].strip()])
        upload_content = normalized_csv.getvalue().encode("utf-8")
    else:
        upload_content = content

    return columns, preview_rows, upload_content


def validate_bulk_response(result):
    if not isinstance(result, dict):
        raise ValueError("The bulk upload API returned an unexpected response.")

    count_fields = ("total_rows", "successful_rows", "failed_rows")
    for field in count_fields:
        value = result.get(field)
        if type(value) is not int or value < 0:
            raise ValueError("The bulk upload API returned invalid summary counts.")

    tickets = result.get("tickets")
    if not isinstance(tickets, list):
        raise ValueError("The bulk upload API did not return a ticket list.")
    if result["successful_rows"] != len(tickets):
        raise ValueError("The bulk upload API returned inconsistent ticket counts.")

    for ticket in tickets:
        if not isinstance(ticket, dict) or any(
            field not in ticket for field in TICKET_RESULT_FIELDS
        ):
            raise ValueError("The bulk upload API returned an invalid ticket result.")
        if not isinstance(ticket["text"], str):
            raise ValueError("The bulk upload API returned invalid ticket text.")

    return result


st.title("Bulk Ticket Upload")
st.write("Upload a CSV of customer support tickets for backend classification.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
upload_content = None
preview_columns = []
preview_rows = []
validation_error = None
uploaded_bytes = None
upload_fingerprint = None

if uploaded_file is None:
    st.info("Select a CSV file to preview and validate it before uploading.")
else:
    uploaded_bytes = uploaded_file.getvalue()
    upload_fingerprint = hashlib.sha256(uploaded_bytes).hexdigest()
    filename = uploaded_file.name
    if not filename.lower().endswith(".csv"):
        validation_error = "Please choose a file with a .csv extension."
    else:
        try:
            preview_columns, preview_rows, upload_content = parse_csv_upload(
                uploaded_bytes
            )
        except ValueError as error:
            validation_error = str(error)

    if preview_rows:
        st.subheader("CSV preview")
        st.dataframe(
            preview_rows,
            column_order=preview_columns,
            hide_index=True,
            use_container_width=True,
        )
    if validation_error:
        st.error(validation_error)

upload_clicked = st.button(
    "Upload & Classify",
    type="primary",
    disabled=uploaded_file is None or validation_error is not None,
)

if upload_clicked and uploaded_file is not None and upload_content is not None:
    safe_filename = uploaded_file.name.replace("\\", "/").rsplit("/", 1)[-1]
    try:
        response = httpx.post(
            f"{API_BASE_URL}/tickets/bulk",
            files={"file": (safe_filename, upload_content, "text/csv")},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        try:
            result = response.json()
        except ValueError as error:
            raise ValueError("The bulk upload API returned invalid JSON.") from error
        result = validate_bulk_response(result)
        st.session_state["bulk_upload_result"] = result
        st.session_state["bulk_upload_fingerprint"] = upload_fingerprint
    except httpx.RequestError:
        st.error(
            f"Could not connect to the backend at {API_BASE_URL}. "
            "Confirm that the FastAPI service is running."
        )
    except httpx.HTTPStatusError as error:
        st.error(
            f"The bulk upload API returned HTTP {error.response.status_code}. "
            "Check that the CSV follows the required format and try again."
        )
    except ValueError as error:
        st.error(str(error))

saved_result = st.session_state.get("bulk_upload_result")
saved_fingerprint = st.session_state.get("bulk_upload_fingerprint")
if (
    uploaded_file is not None
    and saved_result is not None
    and saved_fingerprint == upload_fingerprint
):
    successful_rows = saved_result["successful_rows"]
    failed_rows = saved_result["failed_rows"]
    total_rows = saved_result["total_rows"]
    if successful_rows == total_rows:
        st.success(f"Upload completed successfully: {successful_rows} ticket(s) processed.")
    elif successful_rows > 0 and failed_rows > 0:
        st.warning(
            f"Upload partially completed: {successful_rows} of {total_rows} "
            f"ticket(s) processed; {failed_rows} failed."
        )
    elif successful_rows == 0 and failed_rows > 0:
        st.error(
            f"Upload failed: none of the {total_rows} ticket(s) could be processed."
        )

    st.subheader("Upload summary")
    summary_columns = st.columns(3)
    summary_columns[0].metric("Total rows", saved_result["total_rows"])
    summary_columns[1].metric(
        "Tickets processed", saved_result["successful_rows"]
    )
    summary_columns[2].metric("Failed rows", saved_result["failed_rows"])

    st.subheader("Classification results")
    tickets = saved_result["tickets"]
    if tickets:
        result_rows = [
            {
                "Ticket ID": ticket["id"],
                "Ticket text": ticket["text"],
                "Category": ticket["category"],
                "Priority": ticket["priority"],
                "Confidence": ticket["confidence"],
                "Method": ticket["method"],
                **({"Status": ticket["status"]} if "status" in ticket else {}),
            }
            for ticket in tickets
        ]
        st.dataframe(result_rows, hide_index=True, use_container_width=True)
    else:
        st.info("The API did not return any classified tickets.")

    errors = saved_result.get("errors")
    if isinstance(errors, list) and errors:
        st.subheader("Upload Errors")
        for upload_error in errors:
            with st.container(border=True):
                if isinstance(upload_error, dict):
                    if "row" in upload_error:
                        st.caption("Row number")
                        st.text(str(upload_error["row"]))
                    if "text" in upload_error:
                        st.caption("Ticket text")
                        st.text(str(upload_error["text"]))
                    if "error" in upload_error:
                        st.caption("Backend error")
                        st.text(str(upload_error["error"]))
                else:
                    st.text(str(upload_error))
