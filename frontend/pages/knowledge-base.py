import httpx
import streamlit as st

from backend.app.services.kb_retriever import retrieve_knowledge


API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 10.0

st.set_page_config(page_title="Knowledge Base", page_icon="📚", layout="wide")
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


def get_knowledge_base():
    response = httpx.get(
        f"{API_BASE_URL}/knowledge-base",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    try:
        documents = response.json()
    except ValueError as error:
        raise ValueError("The knowledge-base API returned invalid JSON.") from error

    if not isinstance(documents, list):
        raise ValueError("The knowledge-base API returned an unexpected response.")
    for document in documents:
        if (
            not isinstance(document, dict)
            or not isinstance(document.get("name"), str)
            or not isinstance(document.get("content"), str)
        ):
            raise ValueError("The knowledge-base API returned an invalid document.")
    return documents


st.title("Knowledge Base")
st.write("Browse support policies and search for guidance relevant to a ticket.")

try:
    documents = get_knowledge_base()
except httpx.RequestError:
    st.error(
        f"Could not connect to the knowledge-base API at {API_BASE_URL}. "
        "Confirm that the FastAPI backend is running."
    )
    st.stop()
except httpx.HTTPStatusError as error:
    st.error(
        f"The knowledge-base API returned HTTP {error.response.status_code}."
    )
    st.stop()
except ValueError as error:
    st.error(f"Could not read knowledge-base documents: {error}")
    st.stop()

st.subheader("Available documents")
if not documents:
    st.info("No knowledge-base documents are currently available.")
else:
    st.caption(f"{len(documents)} document(s)")
    for document in documents:
        title = document.get("title") or document["name"]
        with st.expander(f"{title} ({document['name']})"):
            st.write(document["content"])

st.subheader("Search knowledge base")
query = st.text_input(
    "Support query",
    placeholder="For example: My payment failed but I was charged",
)
if st.button("Search", type="primary"):
    if not query.strip():
        st.session_state.pop("knowledge_search_query", None)
        st.session_state.pop("knowledge_search_results", None)
        st.warning("Enter a support query to search the knowledge base.")
    else:
        try:
            results = retrieve_knowledge(query.strip(), top_k=len(documents))
            if not isinstance(results, list) or any(
                not isinstance(result, dict)
                or not isinstance(result.get("name"), str)
                or not isinstance(result.get("content"), str)
                for result in results
            ):
                raise ValueError("The knowledge search returned invalid results.")
            st.session_state["knowledge_search_query"] = query.strip()
            st.session_state["knowledge_search_results"] = results
        except Exception as error:
            st.error(f"Could not search the knowledge base: {error}")
            st.stop()

saved_query = st.session_state.get("knowledge_search_query")
saved_results = st.session_state.get("knowledge_search_results")
if saved_query is not None and saved_results is not None:
    st.markdown(f"#### Results for: {saved_query}")
    if not saved_results:
        st.info("No relevant knowledge-base content matched that query.")
    else:
        titles_by_name = {
            document["name"]: document.get("title") or document["name"]
            for document in documents
        }
        for result in saved_results:
            result_title = titles_by_name.get(result["name"], result["name"])
            similarity = result.get("similarity")
            heading = result_title
            if similarity is not None:
                heading += f" — relevance: {similarity}"
            with st.expander(heading):
                st.write(result["content"])