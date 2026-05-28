import streamlit as st


def get_theme(theme="light"):

    return {
        "bg": "#0E1117" if theme == "dark" else "#F7F9FC",
        "surface": "#1F2933" if theme == "dark" else "#FFFFFF",
        "text": "#E5E7EB" if theme == "dark" else "#1F2933",
        "text_muted": "#9CA3AF" if theme == "dark" else "#6B7280",
        "border": "#2D3748" if theme == "dark" else "#E5E7EB",

        "primary": "#6366F1",
        "secondary": "#3B82F6",

        "success": "#22C55E",
        "warning": "#F59E0B",
        "danger": "#EF4444",
    }


def load_css(theme="light"):

    c = get_theme(theme)

    st.markdown(f"""
    <style>

    /* =====================================================
    GLOBAL APP STYLE
    ===================================================== */

    .stApp {{
        background-color: {c['bg']};
        color: {c['text']};
        font-family: 'Inter', sans-serif;
    }}


    /* =====================================================
    SIDEBAR
    ===================================================== */

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg,{c['primary']},{c['secondary']});
    }}

    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}

    section[data-testid="stSidebar"] button {{

        padding:12px 14px;
        border-radius:10px;
        margin-bottom:8px;

        border:1px solid rgba(255,255,255,0.2);
        background:rgba(255,255,255,0.15);

        font-weight:500;
        width:100%;

        transition:0.2s;
    }}

    section[data-testid="stSidebar"] button:hover {{

        background:rgba(255,255,255,0.25);
        transform:translateX(4px);
    }}

    section[data-testid="stSidebar"] button[kind="primary"] {{

        background:rgba(255,255,255,0.35);
        border-left:5px solid #22C55E;
        font-weight:600;

        box-shadow:0 2px 10px rgba(0,0,0,0.2);
    }}


    /* =====================================================
    TITLES
    ===================================================== */

    .dashboard-title {{
        font-size:36px;
        font-weight:800;
        color:{c['primary']};
        text-align:center;
    }}

    .section-title {{
        font-size:22px;
        font-weight:700;
        color:{c['primary']};
        margin:30px 0 15px;
    }}
    
    /* ===============================
   USER CARD (SIDEBAR)
=============================== */
.user-card {{
    display: flex;
    align-items: center;
    gap: 12px;

    padding: 14px;
    margin-top: 10px;

    border-radius: 16px;

    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);

    border: 1px solid rgba(255, 255, 255, 0.15);

    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);

    transition: all 0.3s ease;
    cursor: pointer;
}}

/* Hover Effect 🔥 */
.user-card:hover {{
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(59, 130, 246, 0.5);
}}

/* Icon */
.user-icon {{
    font-size: 28px;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    padding: 10px;
    border-radius: 12px;
    color: white;
}}

/* Text Container */
.user-info {{
    display: flex;
    flex-direction: column;
}}

/* Name */
.user-name {{
    font-size: 15px;
    font-weight: 600;
    color: #ffffff;
}}

/* ID */
.user-id {{
    font-size: 12px;
    opacity: 0.7;
    color: #d1d5db;
}}


    /* =====================================================
MAIN METRIC CARDS (Prediction Results)
===================================================== */

.metric-card {{

background:{c['surface']};
border:1px solid {c['border']};

border-radius:16px;

padding:24px;

box-shadow:0 8px 24px rgba(0,0,0,0.08);

transition:0.25s;

display:flex;
flex-direction:column;
justify-content:center;
align-items:flex-start;

height:100%;

min-height:180px;

}}

.metric-card:hover {{

transform:translateY(-6px);
border-color:{c['primary']};

box-shadow:0 14px 36px rgba(0,0,0,0.18);

}}

.metric-card h4 {{

margin-bottom:10px;

color:{c['text_muted']};

font-weight:600;

}}

.metric-card h2 {{

font-size:34px;

font-weight:700;

margin:0;

}}


    /* =====================================================
PROGRESS BARS
===================================================== */

.progress-container{{

margin-top:10px;

height:8px;

background:rgba(255,255,255,0.15);

border-radius:20px;

overflow:hidden;
}}

.progress-bar{{

height:100%;

background:#3B82F6;

border-radius:20px;

transition:0.6s ease;
}}
    
    
    /* =====================================================
    KPI CARDS (FOIR / Financial indicators)
    ===================================================== */

    .kpi-card {{

        display:flex;
        align-items:center;
        gap:16px;

        background: var(--surface);

color: var(--text);

padding:20px;

border-radius:14px;

box-shadow:0 4px 12px rgba(0,0,0,0.08);

border:2px solid #3b82f6;
    }}

    .kpi-card:hover {{
        transform:translateY(-4px);
    }}

    .kpi-card.blue {{
        border-color:#3B82F6;
    }}

    .kpi-body {{
        flex:1;
    }}

    .kpi-title {{
        font-size:22px;
        color:{c['text_muted']};
        margin-bottom:4px;
    }}

    .kpi-value {{
        font-size:34px;
        font-weight:700;
    }}

    .kpi-delta {{
        font-size:18px;
        margin-top:4px;
        font-weight:600;
    }}

    .kpi-icon {{

        width:46px;
        height:46px;

        border-radius:50%;

        display:flex;
        align-items:center;
        justify-content:center;

        font-size:22px;

        color:white;
    }}

    .kpi-icon.blue {{
        background:#3B82F6;
    }}

    .kpi-icon.green {{
        background:#22C55E;
    }}

    .kpi-icon.red {{
        background:#EF4444;
    }}



    /* =====================================================
    EXPLANATION PANEL
    ===================================================== */

.explanation-box{{

background: rgba(59,130,246,0.08);

border-left:5px solid #3B82F6;

padding:18px;

border-radius:12px;

margin-top:10px;
}}

.explanation-item{{

padding:8px 0;

font-size:20px;

color:inherit;

border-bottom:1px dashed rgba(255,255,255,0.08);
}}

.explanation-item:last-child{{

border-bottom:none;
}}



    /* =====================================================
    REASONING CARDS
    ===================================================== */

    .reason-card {{

        background:{c['surface']};

        border:1px solid {c['border']};

        padding:12px;

        border-radius:10px;

        margin-bottom:10px;

        font-size:18px;

        box-shadow:0 4px 10px rgba(0,0,0,0.05);
    }}



    /* =====================================================
   FEATURE CARDS (ENHANCED)
   ===================================================== */

.feature-card {{

    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 16px;
    padding: 22px;

    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    text-align: center;

    transition: all 0.25s ease;
    height: 150px;
    gap: 6px;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}}

/* Icon inside card */
.feature-card h2 {{
    margin-bottom: 6px;
}}

/* Title */
.feature-card h4 {{
    margin-bottom: 4px;
    font-size: 16px;
}}

/* Description */
.feature-card p {{
    font-size: 13px;
    opacity: 0.8;
}}

/* Hover effect */
.feature-card:hover {{
    transform: translateY(-6px) scale(1.02);
    border-color: {c['primary']};
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}}

/* Row spacing */
.card-row-gap {{
    height: 20px;
}}

/* Timeline */
.timeline {{
    border-left: 3px solid {c['primary']};
    padding-left: 18px;
    margin-left: 10px;
}}

.timeline-step {{
    margin-bottom: 14px;
    font-size: 14px;
}}

.timeline-step span {{
    font-weight: bold;
    color: {c['primary']};
}}



    /* =====================================================
    BUTTON STYLE
    ===================================================== */

    .stButton > button {{

        background: linear-gradient(135deg,{c['primary']},{c['secondary']});

        color:white;

        border-radius:10px;

        border:none;

        padding:10px 18px;

        font-weight:600;

        transition:0.2s;
    }}

    .stButton > button:hover {{

        transform:translateY(-2px);

        box-shadow:0 6px 16px rgba(0,0,0,0.2);
    }}

    </style>
    """, unsafe_allow_html=True)


    # =====================================================
    # APP TITLE
    # =====================================================

    st.markdown("""
    <style>
    .flag-title{
    font-size:56px;
    font-weight:800;
    text-align:center;
    background:linear-gradient(135deg,#FFA726,#66BB6A);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    }
    </style>

    <h1 class="flag-title">RiskSaarthi</h1>
    """, unsafe_allow_html=True)


    st.markdown("""
    <h3 style="text-align:center; color:#93C5FD;">
    AI-Driven Loan Risk Assessment & Explainable Credit Analytics System for India
    </h3>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>

    /* Target buttons inside history filter section */
    div[data-testid="stHorizontalBlock"] button {
        border-radius: 8px;
        font-weight: 600;
        padding: 6px 12px;
    }

    /* All button (default look) */
    button:has(span:contains("All")) {
        background-color: #444 !important;
        color: white !important;
    }

    /* Low Risk → Green */
    button:has(span:contains("Low")) {
        background-color: #2ecc71 !important;
        color: white !important;
    }

    /* Medium Risk → Orange */
    button:has(span:contains("Medium")) {
        background-color: #f39c12 !important;
        color: white !important;
    }

    /* High Risk → Red */
    button:has(span:contains("High")) {
        background-color: #e74c3c !important;
        color: white !important;
    }

    /* Hover effect */
    button:hover {
        opacity: 0.85 !important;
    }

    </style>
    """, unsafe_allow_html=True)
