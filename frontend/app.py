import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st


pages = [
    st.Page("dashboard.py", title="Dashboard", default=True),
    st.Page("pages/ticket-queue.py", title="Ticket Queue"),
    st.Page(
        "pages/ticket-detail-suggested-reply.py",
        title="Ticket Detail & Suggested Reply",
    ),
    st.Page("pages/submit-bulk-upload.py", title="Submit Bulk Upload"),
    st.Page("pages/analytics.py", title="Analytics"),
    st.Page("pages/knowledge-base.py", title="Knowledge Base"),
]

navigation = st.navigation(pages)
navigation.run()
