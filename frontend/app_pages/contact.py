import streamlit as st
import requests

CONTACT_API = "http://127.0.0.1:8000/api/contact"


# ------------------------------------------------
# PAGE
# ------------------------------------------------
def show_contact():

    # 🔒 Auth check
    if not st.session_state.get("logged_in"):
        st.warning("🔒 Please login to use contact form")
        st.stop()

    # Get user details from session
    user_id = st.session_state.get("user_id")
    name = st.session_state.get("name", "")
    email = st.session_state.get("email", "")

    # ------------------------------------------------
    # CONTACT FORM
    # ------------------------------------------------
    st.markdown("## 📞 Contact Us")
    st.write("📩 Have questions or feedback? Send us a message.")

    with st.container():

        with st.form("contact_form"):

            col1, col2 = st.columns(2)

            with col1:
                st.text_input(
                    "👤 Your Name",
                    value=name,
                    disabled=True  # 🔒 read-only
                )

            with col2:
                st.text_input(
                    "📧 Your Email",
                    value=email,
                    disabled=True  # 🔒 read-only
                )

            message = st.text_area("💬 Your Message")

            submit = st.form_submit_button("🚀 Send Message")

            if submit:

                if not message.strip():
                    st.warning("Message cannot be empty")
                    st.stop()

                payload = {
                    "user_id": user_id,
                    "name": name,
                    "email": email,
                    "message": message,
                }

                try:
                    res = requests.post(CONTACT_API, json=payload, timeout=5)

                    if res.status_code == 200:
                        data = res.json()

                        if data.get("status") == "success":
                            st.success("✅ Message sent successfully!")
                        else:
                            st.error(f"❌ {data.get('message')}")

                    else:
                        st.error("❌ Failed to submit message")

                except Exception as e:
                    st.error(f"⚠ Backend not reachable: {e}")
