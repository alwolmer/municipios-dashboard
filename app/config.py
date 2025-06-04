import streamlit as st

LOAD_LOCAL = st.secrets["settings"].get("load_local", False)
REMOTE_REPO_URL = st.secrets["settings"].get("remote_repo_url")