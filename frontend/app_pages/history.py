import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/history"


# -----------------------------
# Fetch History Data (Cached)
# -----------------------------
@st.cache_data(ttl=30)
def fetch_history(user_id, mode):

    try:
        params = {
            "user_id": user_id,
            "mode": mode
        }

        res = requests.get(API_URL, params=params, timeout=10)

        if res.status_code != 200:
            return pd.DataFrame()

        return pd.DataFrame(res.json())

    except Exception:
        return pd.DataFrame()


# -----------------------------
# History Page
# -----------------------------
def show_history():

    # 🔒 Auth check
    if not st.session_state.get("logged_in"):
        st.warning("🔒 Please login to access this page")
        st.stop()

    st.markdown("## RISKSAARTHI – Prediction History")

    user_id = st.session_state.get("user_id")

    # -----------------------------
    # Session State
    # -----------------------------
    if "history_mode" not in st.session_state:
        st.session_state.history_mode = "global"

    if "history_page" not in st.session_state:
        st.session_state.history_page = 1

    if "history_filter" not in st.session_state:
        st.session_state.history_filter = "All"

    # -----------------------------
    # 🔘 Toggle
    # -----------------------------
    view_mode = st.radio(
        "Select Data View",
        ["My Data", "Global Data"],
        horizontal=True
    )

    st.session_state.history_mode = "user" if view_mode == "My Data" else "global"

    # -----------------------------
    # Fetch Data
    # -----------------------------
    df = fetch_history(user_id, st.session_state.history_mode)

    if df.empty:
        st.warning("No history available or backend not responding.")
        return

    # -----------------------------
    # Clean Data
    # -----------------------------
    if "risk_level" in df.columns:
        df["risk_level"] = df["risk_level"].fillna("Unknown")

    if "prediction_time" in df.columns:
        df["prediction_time"] = pd.to_datetime(
            df["prediction_time"]
        ).dt.strftime("%Y-%m-%d %H:%M")

    # -----------------------------
    # Search
    # -----------------------------
    search = st.text_input("🔍 Search by Applicant ID or Date")

    if search:
        st.session_state.history_page = 1

        mask = df.astype(str).apply(
            lambda col: col.str.contains(search, case=False)
        ).any(axis=1)

        df = df[mask]

    # -----------------------------
    # Risk Filter
    # -----------------------------
    st.write("### Filter by Risk")

    c1, c2, c3, c4 = st.columns(4)

    if c1.button("All"):
        st.session_state.history_filter = "All"
        st.session_state.history_page = 1

    if c2.button("Low"):
        st.session_state.history_filter = "Low Risk"
        st.session_state.history_page = 1

    if c3.button("Medium"):
        st.session_state.history_filter = "Medium Risk"
        st.session_state.history_page = 1

    if c4.button("High"):
        st.session_state.history_filter = "High Risk"
        st.session_state.history_page = 1

    if st.session_state.history_filter != "All":
        df = df[
            df["risk_level"].str.lower() ==
            st.session_state.history_filter.lower()
        ]

    # -----------------------------
    # Pagination
    # -----------------------------
    rows_per_page = 8

    total_pages = max(1, (len(df) + rows_per_page - 1) // rows_per_page)

    current_page = st.session_state.history_page
    current_page = max(1, min(current_page, total_pages))

    start = (current_page - 1) * rows_per_page
    end = start + rows_per_page

    page_df = df.iloc[start:end]

    # -----------------------------
    # Table
    # -----------------------------
    st.dataframe(page_df, use_container_width=True, hide_index=True)

    # -----------------------------
    # Export
    # -----------------------------
    csv = df.to_csv(index=False)

    st.download_button(
        "⬇ Download CSV",
        csv,
        "prediction_history.csv",
        "text/csv"
    )

    # -----------------------------
    # Pagination Controls
    # -----------------------------
    p1, p2, p3 = st.columns([1, 1, 1])

    if p1.button("⬅ Previous") and current_page > 1:
        st.session_state.history_page -= 1
        st.rerun()

    p2.markdown(
        f"<center>Page {current_page} / {total_pages}</center>",
        unsafe_allow_html=True
    )

    if p3.button("Next ➡") and current_page < total_pages:
        st.session_state.history_page += 1
        st.rerun()