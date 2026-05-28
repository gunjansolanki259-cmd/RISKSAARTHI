import streamlit as st
import requests
import os


MODEL_API = "http://127.0.0.1:8000/api/model-info"

st.set_page_config(page_title="About | RISKSAARTHI", layout="wide")

# ------------------------------------------------
# Fetch Model Info (Dynamic)
# ------------------------------------------------
@st.cache_data(ttl=60)
def fetch_model_info():
    try:
        res = requests.get(MODEL_API, timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.warning("Failed to fetch model info")
        return {
            "model_name": "Unknown",
            "version": "N/A",
            "last_updated": "N/A"
        }


def show():

    st.markdown("## ℹ️ About RISKSAARTHI")
    st.markdown("---")

    # ------------------------------------------------
    # ABOUT, Our Mission and What we do
    # ------------------------------------------------
    st.markdown("### 🧠 Application Insights")

    st.info("""
    RISKSAARTHI is an AI-powered loan risk prediction system designed to help financial institutions 
    evaluate borrower risk efficiently and accurately.

    It uses Machine Learning to analyze applicant details such as income, credit score, and loan parameters 
    to predict default probability, classify risk levels, and provide explainable insights.
    """)

    st.markdown("---")

    st.markdown("### 🎯 Our Mission")
    st.info("Reduce financial risk and improve decision-making using machine learning and data-driven insights.")
    st.markdown("---")

    st.markdown("### 🧠 What We Do")
    st.info("""- Predict loan default probability
    - Classify applicants into risk categories
    - Provide explainable AI insights
    - Offer analytics dashboards for decision support""")
    st.markdown("---")

    # ------------------------------------------------
    # KEY FEATURES (2 ROWS)
    # ------------------------------------------------

    features = [
        ("🧠", "AI Prediction", "ML-based classification"),
        ("⚡", "Real-time", "Instant analytics"),
        ("🔍", "Explainable", "Transparent output"),
        ("🔐", "Secure", "Safe logging"),
        ("🎯", "User Friendly", "Simple UI"),
        ("📊", "Visual Insights", "Charts & graphs")
    ]

    st.markdown("### 📊 Key Features")

    # FIRST ROW
    row1 = st.columns(3)

    for col, (icon, title, desc) in zip(row1, features[:3]):
        with col:
            st.markdown(f"""
                    <div class="feature-card">
                        <h2>{icon}</h2>
                        <h4>{title}</h4>
                        <p>{desc}</p>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="card-row-gap"></div>', unsafe_allow_html=True)

    # SECOND ROW
    row2 = st.columns(3)

    for col, (icon, title, desc) in zip(row2, features[3:]):
        with col:
            st.markdown(f"""
                    <div class="feature-card">
                        <h2>{icon}</h2>
                        <h4>{title}</h4>
                        <p>{desc}</p>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ------------------------------------------------
    # HOW IT WORKS
    # ------------------------------------------------
    st.markdown("### ⚙️ How It Works")

    st.markdown("""
            <div class="timeline">
            <div class="timeline-step"><span>1.</span> User submits loan application</div>
            <div class="timeline-step"><span>2.</span> Data validation & processing</div>
            <div class="timeline-step"><span>3.</span> Feature preparation</div>
            <div class="timeline-step"><span>4.</span> ML predicts probability</div>
            <div class="timeline-step"><span>5.</span> Risk classification</div>
            <div class="timeline-step"><span>6.</span> Credit score calculation</div>
            <div class="timeline-step"><span>7.</span> Explanation generation</div>
            <div class="timeline-step"><span>8.</span> Stored in database</div>
            <div class="timeline-step"><span>9.</span> Analytics dashboard display</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ------------------------------------------------
    # ML WORKFLOW
    # ------------------------------------------------
    st.markdown("### 🔄 ML Workflow")

    st.code("""
    User Input
       ↓
    Data Validation
       ↓
    Feature Engineering
       ↓
    Best Model Selection
       ↓
    Risk Probability
       ↓
    Risk Classification
       ↓
    Credit Score Mapping
       ↓
    Explanation Generation
       ↓
    Database Storage
       ↓
    Analytics Dashboard
    """, language="text")

    st.markdown("---")

    # ------------------------------------------------
    # SYSTEM ARCHITECTURE
    # ------------------------------------------------
    st.markdown("### 🏗️ System Architecture")

    BASE_DIR = os.path.dirname(__file__)
    image_path = os.path.abspath(
        os.path.join(BASE_DIR, "../assets/artitechture2.png")
    )

    st.image(image_path, caption="System Architecture")
    st.code("""
        Synthetic Data → MySQL → ML Training → Model (.pkl)
                                        ↓
                                   FastAPI Backend
                                        ↓
                            Prediction + Explanation Engine
                                        ↓
                                 Stored in DB
                                        ↓
                              Streamlit Dashboard
        """)

    st.markdown("---")

    # ------------------------------------------------
    # MODEL INFO (DYNAMIC)
    # ------------------------------------------------
    st.markdown("### 🤖 Model Information")

    model = fetch_model_info()

    m1, m2, m3 = st.columns(3)

    m1.metric("Model", model.get("model_name", "N/A"))
    m2.metric("Version", model.get("version", "N/A"))
    m3.metric("Last Updated", model.get("last_updated", "N/A"))

    st.caption("""
    - Model loaded dynamically from backend  
    - Supports versioning and updates  
    - Designed for loan default risk classification  
    """)

    st.markdown("---")

    # ------------------------------------------------
    # TECH STACK
    # ------------------------------------------------
    st.markdown("### 💻 Tech Stack")

    st.markdown("""
        | Layer | Technology |
        |------|-----------|
        | Backend | FastAPI |
        | ML | Scikit-Learn / Pandas |
        | Database | MySQL |
        | Frontend | Streamlit |
        | ORM | mysql-connector |
        | Model Storage | Joblib |
        | Visualization | Plotly |
        | Validation | Pydantic |
        | Testing | Pytest |
        | Dev Tools | Jupyter / PyCharm |
        """)

    st.markdown("---")

    # ------------------------------------------------
    # DEVELOPERS
    # ------------------------------------------------
    st.markdown("### 👨‍💻 Developers")

    d1, d2 = st.columns(2)

    with d1:
        st.success("""
            **Devansh Kumar Singh**  
            BBD University  
            Data Science & AI Student
            """)

    with d2:
        st.success("""
            **Gunjan Singh Solanki**  
            BBD University  
            Data Science & AI Student
            """)
    st.markdown("---")

    # ------------------------------------------------
    # DATA PRIVACY & DISCLAIMER
    # ------------------------------------------------
    st.markdown("### ⚠️ Data Privacy & Disclaimer")

    st.warning("""
    This application is developed strictly for academic purposes.

    - Any identity information (such as PAN or Aadhaar-like inputs) is **simulated and not verified**.
    - The system uses **hashing techniques** to ensure that sensitive data is not stored in raw form.
    - Users are advised **not to enter real Aadhaar numbers or sensitive personal information**.
    - This project does not comply with production-level regulatory requirements such as UIDAI guidelines.

    The identity feature is implemented only to demonstrate **fraud detection and unique applicant tracking concepts**.
    """)

    st.markdown("---")
    st.info("This project is developed as part of a BCA (Data Science & Artificial Intelligence) final year academic project.")