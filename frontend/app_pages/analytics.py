import streamlit as st
import requests
import pandas as pd
import plotly.express as px



API_URL = "http://127.0.0.1:8000/api/analytics"



@st.cache_data(ttl=5)
def fetch_analytics(user_id, mode):
    try:
        params = {
            "user_id": user_id,
            "mode": mode
        }

        res = requests.get(API_URL, params=params, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None


# -------------------------------
# Trend Calculator
# -------------------------------
def calc_trend(current, previous):
    if previous == 0:
        return "0%", "neutral"

    change = ((current - previous) / previous) * 100

    if change > 0:
        return f"+{change:.1f}%", "up"
    elif change < 0:
        return f"{change:.1f}%", "down"
    return "0%", "neutral"


# -------------------------------
# Dashboard KPIs
# -------------------------------
def show_dashboard():
    st.markdown("## RISKSAARTHI – Analytics Dashboard")
    st.caption("#### Loan Risk & Borrower Behavior Insights")

    # Toggle
    user_id = st.session_state.get("user_id")

    view_mode = st.radio(
        "Select Data View",
        ["My Data", "Global Data"],
        horizontal=True
    )

    mode = "user" if view_mode == "My Data" else "global"

    data = fetch_analytics(user_id, mode)

    if not data:
        st.error("⚠ Failed to load analytics API")
        return

    # -------------------------------
    # KPIs
    # -------------------------------

    total_current = data.get("recent_total", 0)
    total_previous = data.get("total_applications", 0)

    risk_current = data.get("recent_high_risk", 0)
    risk_previous = data.get("high_risk_cases", 0)

    credit_current = data.get("recent_avg_score", 0)
    credit_previous = data.get("average_credit_score", 0)

    total_delta, total_dir = calc_trend(total_current, total_previous)
    risk_delta, risk_dir = calc_trend(risk_current, risk_previous)
    credit_delta, credit_dir = calc_trend(credit_current, credit_previous)

    col1, col2, col3 = st.columns(3)

    # -------------------------------
    # Total Applications KPI
    # -------------------------------
    col1.markdown(f"""
    <div class="kpi-card blue">
    <div class="kpi-icon blue">📊</div>
    <div class="kpi-body">
    <div class="kpi-title">Recent Applications</div>
    <div class="kpi-value">{total_current:,}</div>
    <div class="kpi-delta {total_dir}">
    {total_delta}
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # High Risk KPI
    # -------------------------------
    col2.markdown(f"""
    <div class="kpi-card red">
    <div class="kpi-icon red">⚠</div>
    <div class="kpi-body">
    <div class="kpi-title">Recent High Risk Cases</div>
    <div class="kpi-value">{risk_current:,}</div>
    <div class="kpi-delta {risk_dir}">
    {risk_delta}
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # Credit Score KPI
    # -------------------------------
    col3.markdown(f"""
    <div class="kpi-card blue">
    <div class="kpi-icon green">💳</div>
    <div class="kpi-body">
    <div class="kpi-title">Recent Avg Credit Score</div>
    <div class="kpi-value">{credit_current:.2f}</div>
    <div class="kpi-delta {credit_dir}">
    {credit_delta}
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('---')

    # -------------------------------
    # Top Risk Borrowers Table
    # -------------------------------
    st.markdown('### 🚨 Top High Risk Borrowers')

    risk_df = pd.DataFrame(data.get("top_risk_borrowers", []))

    if not risk_df.empty:
        st.dataframe(risk_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No high risk borrowers found")


# -------------------------------
# Analytics Visualizations
# -------------------------------
def show_analytics():

    st.markdown('---')
    st.markdown('## Analytics Visualizations')

    # Toggle
    user_id = st.session_state.get("user_id")

    view_mode = st.radio(
        "Select Data View",
        ["My Data", "Global Data"],
        horizontal=True,
        key="analytics_toggle"
    )

    mode = "user" if view_mode == "My Data" else "global"

    data = fetch_analytics(user_id, mode)

    if not data:
        st.error("⚠ Failed to load analytics API")
        return

    # Color configs
    risk_colors = {
        "Low Risk": "#37A73F",
        "Medium Risk": "#ECD042",
        "High Risk": "#F24008"
    }

    default_colors = {
        "Likely Non-Default": "#37A73F",
        "Likely Default": "#F24008"
    }

    # -------------------------
    # Row 1 → Default vs Non-Default Distribution
    # -------------------------

    c1, c2 = st.columns(2)

    default_df = pd.DataFrame(data.get("default_distribution", []))

    with c1:
        st.markdown("### Default vs Non-Default Distribution")

        if not default_df.empty:
            fig = px.pie(
                default_df,
                values="count",
                names="default_status",
                hole=0.3,
                color="default_status",
                color_discrete_map=default_colors
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available")

    with c2:
        st.markdown("""
        ### 🔎 Key Insights

        ##### 1. This chart shows the proportion of borrowers likely to default versus those expected to repay.

        ##### 2. A higher percentage of **Likely Default cases** indicates increased financial risk for lenders.

        ##### 3. If the majority of borrowers fall into the **Non-Default category**, it suggests a relatively healthy loan portfolio.

        ##### 4. Financial institutions can use this insight to **adjust lending policies and risk thresholds**.
        """)

    st.markdown('---')

    # -------------------------
    # Row 2 → Risk Level Distribution
    # -------------------------

    c1, c2 = st.columns(2)

    risk_df = pd.DataFrame(data.get("risk_distribution", []))

    with c1:
        st.markdown("### Risk Level Distribution")

        if not risk_df.empty:
            fig2 = px.bar(
                risk_df,
                x="risk_level",
                y="count",
                text="count",
                color="risk_level",
                color_discrete_map=risk_colors
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No data available")

    with c2:
        st.markdown("""
        ### 🔎 Key Insights

        ##### 1. Borrowers are categorized into **Low, Medium, and High risk levels** based on the machine learning prediction.

        ##### 2. A higher number of **High Risk borrowers** indicates greater chances of loan defaults.

        ##### 3. The distribution helps lenders **identify overall portfolio risk exposure**.

        ##### 4. Risk segmentation allows banks to apply **different interest rates or approval policies** for each category.
        """)

    st.markdown('---')

    # -------------------------
    # Row 3 → Credit Behaviour
    # -------------------------

    c1, c2 = st.columns(2)

    credit_df = pd.DataFrame(data.get("credit_behavior", []))

    with c1:
        st.markdown("### Credit Behaviour Insights")

        if not credit_df.empty:
            fig3 = px.bar(
                credit_df,
                x="cibil_range",
                y="borrowers",
                color="borrowers",
                color_continuous_scale="Blues",
                labels={
                    "cibil_range": "CIBIL Range",
                    "borrowers": "Number of Borrowers"
                }
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("No data available")

    with c2:
        st.markdown("""
        ### 🔎 Key Insights

        ##### 1. This chart shows how borrowers are distributed across different **CIBIL score ranges**.

        ##### 2. Borrowers with **higher credit scores generally have better repayment behaviour**.

        ##### 3. Lower CIBIL score groups represent applicants with **potentially higher financial risk**.

        ##### 4. The insight helps lenders understand the **creditworthiness profile of the borrower population**.
        """)

    st.markdown('---')

    # -------------------------
    # Row 4 → Risk by Income Group
    # -------------------------

    c1, c2 = st.columns(2)

    income_risk_df = pd.DataFrame(data.get("risk_by_income", []))

    with c1:
        st.markdown("### Risk Level by Income Group")

        if not income_risk_df.empty:
            fig8 = px.bar(
                income_risk_df,
                x="income_group",
                y="count",
                color="risk_level",
                barmode="stack",
                color_discrete_map=risk_colors
            )
            st.plotly_chart(fig8, use_container_width=True)
        else:
            st.warning("No data available")

    with c2:
        st.markdown("""
        ### 🔎 Key Insights

        ##### 1. Borrowers are grouped into **Low, Middle, and High income categories**.

        ##### 2. Higher risk levels within lower income groups may indicate **financial instability or repayment challenges**.

        ##### 3. High income borrowers usually show **lower risk levels**.

        ##### 4. This insight helps lenders **balance financial inclusion with risk management**.
        """)

    st.markdown('---')

    # -------------------------
    # Row 5 → Income vs Loan
    # -------------------------

    c1, c2 = st.columns(2)

    income_df = pd.DataFrame(data.get("income_loan_relation", []))

    with c1:
        st.markdown("### Annual Income vs Loan Amount")

        if not income_df.empty:

            fig4 = px.scatter(
                income_df,
                x="annual_income",
                y="loan_amount",
                color="risk_level",
                size="loan_amount",
                hover_data=["credit_score"],
                labels={
                    "annual_income": "Annual Income (₹)",
                    "loan_amount": "Loan Amount (₹)"
                },
                color_discrete_map=risk_colors
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("No data available")

    with c2:
        st.markdown("""
        ### 🔎 Key Insights

        ##### 1. This scatter plot shows the relationship between **borrower income and requested loan amount**.

        ##### 2. Generally, borrowers with **higher income tend to apply for larger loans**.

        ##### 3. High risk borrowers requesting large loans may represent **potential financial risk**.

        ##### 4. Lenders can use this insight to **evaluate whether loan amounts are proportional to borrower income**.
        """)

    st.markdown('---')

    # -------------------------
    # Row 6 → Monthly Trend
    # -------------------------

    c1, c2 = st.columns(2)

    trend_df = pd.DataFrame(data.get("monthly_trend", []))

    with c1:
        st.markdown("### Monthly Loan Applications Trend")

        if not trend_df.empty:
            trend_df["month"] = trend_df["month"].astype(str)

            fig9 = px.line(
                trend_df.sort_values("month"),
                x="month",
                y="applications",
                markers=True,
                labels={
                    "month": "Month",
                    "applications": "Applications"
                }
            )

            fig9.update_xaxes(type="category")


            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.warning("No data available")

    with c2:
        st.markdown("""
        ### 🔎 Key Insights

        ##### 1. This chart tracks how the **number of loan applications changes over time**.

        ##### 2. Increasing trends may indicate **growing demand for credit**.

        ##### 3. Sudden spikes in applications could be linked to **economic factors or seasonal demand**.

        ##### 4. Monitoring trends helps financial institutions **plan resources and lending strategies**.
        """)

    # -------------------------
    # Row 7 → Credit Score vs Risk Probability
    # -------------------------

    c1, c2 = st.columns(2)

    credit_risk_df = pd.DataFrame(data.get("credit_vs_risk", []))

    with c1:
        st.markdown("### Credit Score vs Risk Probability")

        if not credit_risk_df.empty:
            # Safe conversion (ONLY if needed)
            if credit_risk_df["risk_probability"].max() <= 1:
                credit_risk_df["risk_probability_percent"] = credit_risk_df["risk_probability"] * 100
            else:
                credit_risk_df["risk_probability_percent"] = credit_risk_df["risk_probability"]

            fig6 = px.scatter(
                credit_risk_df,
                x="credit_score",
                y="risk_probability_percent",
                color="risk_probability_percent",
                size="risk_probability_percent",
                color_continuous_scale="RdYlGn_r",
                labels={
                    "credit_score": "Credit Score",
                    "risk_probability_percent": "Risk Probability (%)"
                }
            )

            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.warning("No data available")

    with c2:
        st.markdown("""
        ### 🔎 Key Insights

        ##### 1. This chart illustrates how **credit scores influence predicted default risk**.

        ##### 2. Borrowers with **lower credit scores generally have higher predicted risk probabilities**.

        ##### 3. Higher credit scores are typically associated with **lower risk of default**.

        ##### 4. This relationship validates that the machine learning model is **capturing meaningful financial patterns**.
        """)

    st.markdown('---')

    # -------------------------
    # Row 8 → Loan Amount Distribution
    # -------------------------

    c1, c2 = st.columns(2)

    loan_df = pd.DataFrame(data.get("loan_amount_distribution", []))

    with c1:
        st.markdown("### Loan Amount Distribution")

        if not loan_df.empty:
            fig5 = px.histogram(
                loan_df,
                x="loan_amount",
                nbins=30,
                labels={"loan_amount": "Loan Amount (₹)"}
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.warning("No data available")

    with c2:
        st.markdown("""
        ### 🔎 Key Insights

        ##### 1. This histogram shows the frequency of different **loan amount ranges** requested by borrowers.

        ##### 2. It helps identify the **most common loan sizes** in the dataset.

        ##### 3. If very large loans appear frequently, it may increase the **overall credit exposure of the lender**.

        ##### 4. The distribution can guide financial institutions in **designing loan products suited to borrower demand**.
        """)

    st.markdown('---')

    # -------------------------
    # Row 9 → Age vs Loan Amount
    # -------------------------

    c1, c2 = st.columns(2)

    age_df = pd.DataFrame(data.get("age_vs_loan", []))

    with c1:
        st.markdown("### Age vs Loan Amount")

        if not age_df.empty:
            fig7 = px.scatter(
                age_df,
                x="age",
                y="loan_amount",
                color="risk_level",
                hover_data=["credit_score"],
                labels={
                    "age": "Age",
                    "loan_amount": "Loan Amount (₹)"
                },
                color_discrete_map={
                    "Low Risk": "#18F47C",
                    "Medium Risk": "#E7CD31",
                    "High Risk": "#EE381A"
                }
            )

            st.plotly_chart(fig7, use_container_width=True)
        else:
            st.warning("No data available")

    with c2:
        st.markdown("""
        ### 🔎 Key Insights

        ##### 1. This chart explores how **borrower age relates to loan demand**.

        ##### 2. Middle-aged borrowers often request **larger loan amounts**, possibly due to major financial commitments.

        ##### 3. Younger borrowers may apply for **smaller loans due to lower income levels**.

        ##### 4. Understanding age-based borrowing patterns helps lenders **design targeted financial products**.
        """)
