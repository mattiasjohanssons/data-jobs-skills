from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="Data Jobs Skills Explorer",
    page_icon="📊",
    layout="wide",
)

st.title("Data Jobs Skills Explorer")
st.write(
    "Explore job postings and see which skills are most frequently mentioned for common data roles."
)

st.markdown(
    """
### What this app does
- Fetches job postings from the JobSearch API
- Extracts common skills from title + description text
- Shows the top skills for a selected role

Go to **Role Skills** in the left sidebar to get started.
"""
)

