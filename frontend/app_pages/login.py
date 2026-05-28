import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api/login"


def show_login():

    st.markdown("## 🔑 Login to RISKSAARTHI")
    st.markdown("---")

    with st.form("login_form"):

        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")

        submit = st.form_submit_button("Login")

    if submit:

        if not email or not password:
            st.warning("Please fill all fields")
            return

        payload = {
            "email": email,
            "password": password
        }

        try:
            res = requests.post(API_URL, json=payload, timeout=5)

            if res.status_code == 200:
                data = res.json()

                if data.get("status") == "success":

                    # STORE SESSION
                    st.session_state.user_id = data["user_id"]
                    st.session_state.name = data["name"]
                    st.session_state.email = data["email"]
                    st.session_state.logged_in = True

                    st.success("✅ Login successful!")

                    st.session_state.nav_page = "home"
                    st.rerun()

                else:
                    st.error(data.get("message"))

            else:
                st.error("Login failed")

        except Exception as e:
            st.error(f"⚠ Backend not reachable: {e}")