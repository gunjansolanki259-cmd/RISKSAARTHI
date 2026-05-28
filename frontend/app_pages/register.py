import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api/register"


def show_register():

    st.markdown("## 📝 Register on RISKSAARTHI")
    st.markdown("---")

    # Predefined roles
    roles = [
        "Loan Officer",
        "Risk Analyst",
        "System User"
    ]

    with st.form("register_form"):

        name = st.text_input("👤 Full Name")
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        role = st.selectbox("💼 Select Role", roles)

        submit = st.form_submit_button("Register")

    if submit:

        if not name or not email or not password:
            st.warning("Please fill all fields")
            return

        payload = {
            "name": name,
            "email": email,
            "password": password,
            "role": role
        }

        try:
            res = requests.post(API_URL, json=payload, timeout=5)

            if res.status_code == 200:
                data = res.json()

                if data.get("status") == "success":
                    st.success("✅ Registration successful! Please login.")
                else:
                    st.error(data.get("message"))

            else:
                st.error("Registration failed")

        except Exception as e:
            st.error(f"⚠ Backend not reachable: {e}")