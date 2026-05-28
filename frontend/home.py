import streamlit as st
import requests
from app_pages import predict, analytics, history, contact, about
from styles import load_css
from PIL import Image
import os
import base64

st.set_page_config(page_title="RISKSAARTHI", layout="wide")

# ------------------------------------------------
# AUTH SESSION STATE
# ------------------------------------------------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("user_id", None)
st.session_state.setdefault("user_name", None)

# ------------------------------------------------
# CONFIG
# ------------------------------------------------
API_URL = "http://127.0.0.1:8000/api"

# ------------------------------------------------
# Helpers
# ------------------------------------------------
@st.cache_data(ttl=5)
def load_icon(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def fetch_analytics():
    try:
        res = requests.get(f"{API_URL}/analytics", timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# ------------------------------------------------
# Paths
# ------------------------------------------------
base_dir = os.path.dirname(__file__)

logo = Image.open(os.path.join(base_dir, "assets", "logo.png"))
st.sidebar.image(logo, use_container_width=True)

# Icons
total_icon = load_icon(os.path.join(base_dir, "assets", "statistics.png"))
risk_icon = load_icon(os.path.join(base_dir, "assets", "siren.png"))
credit_icon = load_icon(os.path.join(base_dir, "assets", "credit-score.png"))

ai_icon = load_icon(os.path.join(base_dir, "assets", "ai.png"))
explain_icon = load_icon(os.path.join(base_dir, "assets", "explaination.png"))
security_icon = load_icon(os.path.join(base_dir, "assets", "log.png"))
india_icon = load_icon(os.path.join(base_dir, "assets", "india.png"))

# ------------------------------------------------
# Theme
# ------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

dark_mode = st.sidebar.toggle("🌙 Dark Mode")
st.session_state.theme = "dark" if dark_mode else "light"

load_css(st.session_state.theme)

# ------------------------------------------------
# Navigation
# ------------------------------------------------
st.sidebar.markdown("# RISKSAARTHI")

# ------------------------------------------------
# GLOBAL REFRESH BUTTON
# ------------------------------------------------
if st.sidebar.button("🔄 Refresh App"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

st.session_state.setdefault("nav_page", "home")


def nav_button(label, page):
    active = st.session_state.nav_page == page
    btn_type = "primary" if active else "secondary"

    if st.sidebar.button(label, key=f"nav_{page}", type=btn_type):
        st.session_state.nav_page = page
        st.rerun()


# ------------------------------------------------
# DYNAMIC NAVIGATION
# ------------------------------------------------

# BEFORE LOGIN
if not st.session_state.logged_in:
    nav_button("🏠 Home", "home")
    nav_button("👨🏻‍💼 About Us", "about")

    st.sidebar.markdown("---")
    nav_button("🔑 Login", "login")
    nav_button("📝 Register", "register")

# AFTER LOGIN
else:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div class="user-card">
        <div class="user-icon">🧑‍💼</div>
        <div class="user-info">
            <div class="user-name">{st.session_state.name}</div>
            <div class="user-id">ID: {st.session_state.user_id}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")


    nav_button("🏠 Home", "home")
    nav_button("👨🏻‍💼 About Us", "about")
    nav_button("🔍 Predict Loan Risk", "predict")
    nav_button("📊 Analytics Dashboard", "analytics")
    nav_button("📜 Prediction History", "history")
    nav_button("📞 Contact Us", "contact")

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state["nav_page"] = "home"
        st.session_state["logged_in"] = False
        st.rerun()


# ------------------------------------------------
# ROUTING WITH PROTECTION
# ------------------------------------------------

protected_pages = ["predict", "analytics", "history", "contact"]

if (
    st.session_state.nav_page in protected_pages
    and not st.session_state.logged_in
):
    st.warning("🔒 Please login to access this page")
    st.session_state.nav_page = "login"
    st.rerun()


if st.session_state.nav_page == "login":
    from app_pages import login
    login.show_login()

elif st.session_state.nav_page == "register":
    from app_pages import register
    register.show_register()

elif st.session_state.nav_page == "predict":
    predict.show_prediction()

elif st.session_state.nav_page == "analytics":
    analytics.show_dashboard()
    analytics.show_analytics()

elif st.session_state.nav_page == "history":
    history.show_history()

elif st.session_state.nav_page == "contact":
    contact.show_contact()

elif st.session_state.nav_page == "about":
    about.show()

# ------------------------------------------------
# Home Page
# ------------------------------------------------
else:
    st.markdown("## Welcome to RISKSAARTHI")

    with st.spinner("Loading analytics..."):
        data = fetch_analytics()

    if not data:
        st.warning("⚠️ Unable to load analytics. Showing default values.")
        data = {
            "total_applications": 0,
            "high_risk_cases": 0,
            "average_credit_score": 0
        }

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <img src="data:image/png;base64,{total_icon}" width="50">
            <h4>Total Predictions Made</h4>
            <h2>{data.get('total_applications', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <img src="data:image/png;base64,{risk_icon}" width="50">
            <h4>High Risk Cases</h4>
            <h2>{data.get('high_risk_cases', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <img src="data:image/png;base64,{credit_icon}" width="50">
            <h4>Average Credit Score</h4>
            <h2>{data.get('average_credit_score', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Features
    st.markdown("## System Features")

    f1, f2, f3, f4 = st.columns(4)

    features = [
        ("AI-Based Risk Prediction", ai_icon),
        ("Explainable Model Insights", explain_icon),
        ("Secure Logging System", security_icon),
        ("Indian Credit Risk Insights", india_icon)
    ]

    for col, (feature, icon) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <img src="data:image/png;base64,{icon}" width="60">
                <h4>{feature}</h4>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align:center; font-size:16px;'>
    <b>Contributors:</b> Devansh Kumar Singh & Gunjan Singh Solanki <br>
    <b>Guides:</b> Mr. Krishnakant Pandey & Ms. Srishti Yadav
    </p>
    """, unsafe_allow_html=True)