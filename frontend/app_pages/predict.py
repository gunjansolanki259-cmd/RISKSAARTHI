import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import re

API_URL = "http://127.0.0.1:8000/api/predict"


def fetch_model_info():
    try:
        res = requests.get("http://127.0.0.1:8000/api/model-info", timeout=5)
        res.raise_for_status()
        return res.json()
    except:
        return None


def show_prediction():
    if not st.session_state.get("logged_in"):
        st.warning("🔒 Please login to access this page")
        st.stop()

    # ===============================
    # Header
    # ===============================

    st.markdown("# 🧠 RiskSaarthi AI Risk Prediction")

    model_info = fetch_model_info()

    if model_info:
        st.caption(
            f"Model: {model_info.get('model_name')} | "
            f"Version: {model_info.get('version')} | "
            f"Last Updated: {model_info.get('last_updated')}"
        )
    else:
        st.caption("Model info unavailable")

    user_id = st.session_state.get("user_id")
    st.markdown(f"👤 Logged in as: **{st.session_state.get('name')}**")

    st.markdown("---")

    # ===============================
    # Loan Application Form
    # ===============================

    with st.form("prediction_form"):

        st.markdown("### 🧑 Applicant Information")

        c1, c2 = st.columns(2)

        with c1:
            identity_type = st.selectbox(
                "🪪 Identity Type",
                ["Aadhaar", "PAN"]
            )

            identity_number = st.text_input(
                "🔐 Identity Number",
                placeholder="Enter Aadhaar / PAN",
                type="password"
            )

        with c2:
            emp = st.selectbox(
                "Employment Type",
                ["Salaried", "Self-Employed"]
            )
            age = st.number_input("Age",  18, 70, value=None, placeholder="Enter age (21 - 60)")

        st.markdown("### 💰 Financial Profile")

        c3, c4 = st.columns(2)

        with c3:
            income = st.number_input("Annual Income (₹)", value=None, placeholder="Enter Annual Income e.g. 500000")

        with c4:
            existing = st.number_input("Existing Loans", value= 0)

        st.markdown("### 🏦 Loan Details")
        c5, c6 = st.columns(2)
        with c5:
            loan = st.number_input("Loan Amount (₹)", value=None, placeholder="Enter Loan Amount e.g. 250000")
            tenure = st.number_input("Loan Tenure (Months)", value=None, placeholder="Enter Loan Tenure in Months (06 - 360) e.g. 60")

        with c6:
            cibil = st.number_input("CIBIL Score", 300, 900, value=None, placeholder="Enter CIBIL Score (300 - 900) e.g. 750")
            interest_rate = st.number_input("Interest Rate (%)", min_value=1.0, max_value=30.0, value=None, placeholder="Enter Current Interest Rate e.g. 7.60")

        colA, colB = st.columns(2)

        submit = colA.form_submit_button("Predict Risk")
        reset = colB.form_submit_button("Reset Form")

    if reset:
        st.rerun()

    # ===============================
    # Prediction
    # ===============================

    if submit:
        if None in [age, income, loan, tenure, cibil, interest_rate]:
            st.warning("Please fill all required fields")
            st.stop()

        # VALIDATION
        if not identity_number.strip():
            st.warning("Please enter Identity Number")
            st.stop()

        if identity_type == "Aadhaar" and not re.fullmatch(r"\d{12}", identity_number):
            st.warning("Invalid Aadhaar format")
            st.stop()

        if identity_type == "PAN" and not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", identity_number.upper()):
            st.warning("Invalid PAN format")
            st.stop()

        # PAYLOAD
        payload = {
            "user_id": user_id,
            "identity_type": identity_type,
            "identity_number": identity_number,

            "age": age,
            "annual_income": income,
            "cibil_score": cibil,
            "employment_type": emp,
            "loan_amount": loan,
            "loan_tenure": tenure,
            "existing_loans": existing,
            "interest_rate": interest_rate
        }

        with st.spinner("Analyzing Loan Risk... Evaluating Credit Profile..."):
            try:
                res = requests.post(API_URL, json=payload, timeout=10)
            except Exception:
                st.error("❌ Cannot connect to prediction API")
                return

        if res.status_code != 200:
            st.error("Prediction Failed")
            return

        st.success("Prediction Completed Successfully")
        data = res.json()
        emi = data.get("emi", 0)
        loan_decision = data.get("loan_decision", "Unknown")

        # MASKED DISPLAY
        full_id = data.get("applicant_id")

        short_id = full_id[:10].upper() if full_id else "Generated"

        st.text_input(
            "🆔 Applicant ID",
            value=short_id,
            disabled=True
        )

        masked_identity = "XXXX XXXX " + identity_number[-4:]
        st.caption(f"Identity Used: {identity_type} ({masked_identity})")

        timestamp = datetime.now().strftime("%d %b %Y %I:%M %p")

        col4 = st.columns(1)[0]

        col4.markdown(
            f"""
            <div class="metric-card">
            <h4>Monthly EMI</h4>
            <h2>₹ {emi}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("## 📊 Prediction Results")

        risk = data["risk_level"]
        prob = data["probability"]
        credit_score = data["credit_score"]


        col1, col2, col3 = st.columns(3)

        risk_color = {
            "Low": "#22C55E",
            "Medium": "#F59E0B",
            "High": "#EF4444"
        }.get(risk, "#9CA3AF")

        risk_icon = {
            "Low": "🟢",
            "Medium": "🟡",
            "High": "🔴"
        }.get(risk, "⚪")

        col1.markdown(
            f"""
            <div class="metric-card" style="border:2px solid {risk_color};">
            <h4>Risk Level</h4>
            <h2 style="color:{risk_color}">
            {risk_icon} {risk.upper()} RISK
            </h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        if credit_score < 600:
            score_color = "#EF4444"
            score_label = "Poor"
        elif credit_score < 700:
            score_color = "#F59E0B"
            score_label = "Average"
        else:
            score_color = "#22C55E"
            score_label = "Good"

        col2.markdown(
            f"""
            <div class="metric-card" style="border:2px solid {score_color};">
            <h4>Generated Credit Score</h4>
            <h2 style="color:{score_color}; font-size:42px;">
            {credit_score}
            </h2>
            <p style="color:{score_color}; font-weight:600;">
            {score_label} Credit Profile
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        decision_map = {
            "Approved": ("APPROVED", "#22C55E", "✅"),
            "Rejected": ("REJECTED", "#EF4444", "❌"),
        }

        decision_text, decision_color, icon = decision_map.get(
            loan_decision,
            ("REVIEW", "#F59E0B", "⚠")
        )

        confidence = f"{100 - prob:.1f}%"

        col3.markdown(
            f"""
            <div class="metric-card" style="border:2px solid {decision_color};">
            <h4>Loan Decision</h4>
            <h2 style="color:{decision_color}">
            {icon} {decision_text}
            </h2>
            <p style="font-weight:600;">
            Confidence: {confidence}
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # ===============================
        # Risk Probability Gauge
        # ===============================

        st.markdown("## Risk Probability")
        col1, col2 = st.columns([2, 1])

        # ===============================
        # Gauge Chart
        # ===============================

        with col1:

            fig = go.Figure(go.Indicator(
                mode="gauge",  # removed number
                value=prob,

                gauge={
                    "axis": {"range": [0, 100]},

                    "bar": {"color": risk_color},

                    "steps": [
                        {"range": [0, 30], "color": "#d4edda"},
                        {"range": [30, 60], "color": "#fff3cd"},
                        {"range": [60, 100], "color": "#f8d7da"}
                    ],

                    "threshold": {
                        "line": {"color": "black", "width": 5},
                        "thickness": 0.8,
                        "value": prob
                    }
                }
            ))

            fig.update_layout(
                height=360,
                margin=dict(l=20, r=20, t=50, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)

        # ===============================
        # Animated Probability Counter
        # ===============================

        with col2:

            counter = st.empty()

            for i in range(0, int(prob) + 1, 2):

                if i < 30:
                    color = "#22C55E"
                elif i < 60:
                    color = "#F59E0B"
                else:
                    color = "#EF4444"

                counter.markdown(
                    f"""
                    <div style="
                    text-align:left;
                    font-size:40px;
                    font-weight:700;
                    color:{color};
                    ">
                    {i}% Probability
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                time.sleep(0.02)

            counter.markdown(
                f"""
                <div style="
                text-align:center;
                font-size:40px;
                font-weight:700;
                color:{risk_color};
                ">
                {prob:.1f}% Probability
                </div>
                """,
                unsafe_allow_html=True
            )

            # ===============================
            # Risk Explanation Box
            # ===============================

            interpretation = (
                "Low probability of loan default"
                if prob < 30 else
                "Moderate loan default risk"
                if prob < 60 else
                "High probability of loan default"
            )

            st.markdown(
                f"""
                <div style="
                margin-top:18px;
                padding:20px;
                border-radius:14px;
                background: rgba(255,255,255,0.06);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border:1px solid rgba(255,255,255,0.12);
                border-left:4px solid {risk_color};
                box-shadow:0 8px 20px rgba(0,0,0,0.25);
                ">

                <div style="
                font-size:18px;
                font-weight:700;
                margin-bottom:8px;
                ">
                ⚠ Risk Insight
                </div>

                <div style="
                font-size:17px;
                opacity:0.9;
                ">
                {interpretation}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        # ===============================
        # FOIR KPI Card
        # ===============================

        foir = data.get("foir", 0)
        # Handle EMI = 0 case
        foir_display = "No EMI" if emi == 0 else f"{foir:.1f}%"

        if emi == 0:
            foir_status = "No Debt"
        elif foir < 40:
            foir_status = "Healthy"
        elif foir < 60:
            foir_status = "Moderate"
        else:
            foir_status = "Risky"

        st.markdown(
            f"""
        <div class="kpi-card" style="
        background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(59,130,246,0.05));
        border:1px solid rgba(59,130,246,0.25);
        border-radius:12px;
        padding:18px;
        ">

        <div class="kpi-icon blue">💳</div>

        <div class="kpi-body">

        <div class="kpi-title">FOIR Ratio</div>

        <div class="kpi-value">{foir_display}</div>

        <div class="kpi-delta">
        {foir_status}
        </div>

        </div>
        </div>
        """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # ===============================
        # Financial Indicators
        # ===============================

        st.markdown("## 📈 Financial Health Indicators")

        # EMI burden calculation (banking metric)
        monthly_income = income / 12 if income else 0
        emi_burden = min((emi / monthly_income) * 100, 100) if monthly_income else 0

        ratio_percent = min(emi_burden, 100)
        debt_percent = min(existing * 20, 100)
        tenure_percent = min((tenure / 120) * 100, 100)

        # Handle EMI = 0 case safely
        emi_display = "No EMI" if emi == 0 else f"{emi_burden:.1f}%"
        emi_status = (
            "No Debt" if emi == 0
            else "Healthy" if emi_burden < 30
            else "Moderate" if emi_burden < 50
            else "High"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="kpi-card blue" style="
        background:linear-gradient(135deg,rgba(37,99,235,0.12),rgba(37,99,235,0.04));
        border:1px solid rgba(37,99,235,0.25);
        border-radius:12px;
        padding:16px;
        ">
                <div class="kpi-icon blue">💰</div>
                <div class="kpi-body">
                    <div class="kpi-title">EMI Burden</div>
                    <div class="kpi-value">{emi_display}</div>
                    <div class="progress-container">
                    <div class="progress-bar" style="width:{ratio_percent}%"></div>
                    </div>
                    <div class="kpi-delta">{emi_status}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="kpi-card blue" style="
        background:linear-gradient(135deg,rgba(37,99,235,0.12),rgba(37,99,235,0.04));
        border:1px solid rgba(37,99,235,0.25);
        border-radius:12px;
        padding:16px;
        ">
                <div class="kpi-icon blue">🏦</div>
                <div class="kpi-body">
                    <div class="kpi-title">Debt Burden</div>
                    <div class="kpi-value">{existing}</div>
                    <div class="progress-container">
                    <div class="progress-bar" style="width:{debt_percent}%"></div>
                    </div>
                    <div class="kpi-delta">Active Loans</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="kpi-card blue" style="
        background:linear-gradient(135deg,rgba(37,99,235,0.12),rgba(37,99,235,0.04));
        border:1px solid rgba(37,99,235,0.25);
        border-radius:12px;
        padding:16px;
        ">
                <div class="kpi-icon blue">⏳</div>
                <div class="kpi-body">
                    <div class="kpi-title">Loan Tenure</div>
                    <div class="kpi-value">{tenure}</div>
                    <div class="progress-container">
                    <div class="progress-bar" style="width:{tenure_percent}%"></div>
                    </div>
                    <div class="kpi-delta">Months</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ===============================
        # Explanation Panel
        # ===============================

        st.markdown("## 📊 Model Explanation")

        explanation = data["explanation"]

        if isinstance(explanation, str):
            explanation = [explanation]

        html = '<div class="explanation-box">'

        for item in explanation:
            html += f'<div class="explanation-item">✔ {item}</div>'

        html += '</div>'

        st.markdown(html, unsafe_allow_html=True)

        st.markdown("---")

        # ===============================
        # Feature Importance
        # ===============================

        st.markdown("## 🔎 Feature Importance")

        df = pd.DataFrame(data.get("top_factors", []))
        # df = pd.DataFrame(data["top_factors"])
        df = df.sort_values("importance")

        fig2 = go.Figure(
            go.Bar(
                x=df["importance"],
                y=df["feature"],
                orientation="h",
                text=(df["importance"] * 100).round(1).astype(str) + "%",
                textposition="auto",

                marker=dict(
                    color=df["importance"],
                    colorscale=[
                        [0, "#dbeafe"],
                        [0.5, "#3b82f6"],
                        [1, "#1e40af"]
                    ],

                    colorbar=dict(
                        title="Importance",
                        thickness=15,
                        len=0.8
                    ),

                    showscale=True
                )
            )
        )

        fig2.update_layout(
            title="Top Factors Influencing Prediction",
            xaxis_title="Importance Score",
            yaxis_title="Features",
            height=520
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # ===============================
        # AI Reasoning Cards
        # ===============================

        st.markdown("## 🤖 Model Decision Factors")

        reasoning = [
            "✔ Strong credit score"
            if cibil > 700 else
            "⚠ Moderate credit score",

            "⚠ High EMI compared to income"
            if emi > income * 0.4 else
            "✔ EMI manageable",

            "✔ Stable employment"
            if emp == "Salaried" else
            "⚠ Income variability possible"
        ]

        for r in reasoning:

            color = "#22C55E" if "✔" in r else "#F59E0B"

            st.markdown(
                f"""
                <div style="
                border-left:4px solid {color};
                padding:12px;
                border-radius:10px;
                margin-bottom:10px;
                background:rgba(255,255,255,0.04);
                ">
                {r}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown(
            f"""
        <div style="text-align:right; opacity:0.7; font-size:14px;">
        Prediction generated on: {timestamp}
        </div>
        """,
            unsafe_allow_html=True
        )