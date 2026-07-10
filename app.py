import streamlit as st
import os
import sys
from pathlib import Path

# Add root folder to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

# Import config and database initializer
import config
from services.incident_engine import initialize_database, get_all_incidents
from utils.helpers import local_css

# Page Configuration
st.set_page_config(
    page_title="Crisis360 AI - Emergency Triage Platform",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data and session state
initialize_database()

if "simulation_mode" not in st.session_state:
    st.session_state["simulation_mode"] = config.is_simulation_mode()

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Dashboard"

if "selected_incident_id" not in st.session_state:
    st.session_state["selected_incident_id"] = None

# Inject global premium styling
local_css(Path(config.ASSETS_DIR) / "css.css")

# Sidebar Logo and Branding
st.sidebar.markdown(
    """
    <div style='text-align: center; padding-bottom: 20px;'>
        <h1 style='font-size: 26px; color: #60a5fa; margin-bottom: 5px; font-weight: 800;'>CRISIS360 AI</h1>
        <p style='color: #94a3b8; font-size: 12px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase;'>Detect. Assess. Respond. Resolve.</p>
        <hr style='border: 0; border-top: 1px solid #1e293b; margin-top: 15px;'/>
    </div>
    """,
    unsafe_allow_html=True
)

# Navigation Menu
pages = {
    "Dashboard": "🏠 Dashboard",
    "Report Incident": "📝 Report Incident",
    "AI Response Center": "🤖 AI Response Center",
    "Analytics": "📊 Analytics",
    "Incident History": "📄 Incident History",
    "Settings": "⚙ Settings"
}

# Render Navigation Buttons
st.sidebar.markdown("<p style='font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.1em; margin-left: 5px;'>Control Center</p>", unsafe_allow_html=True)

for page_key, page_label in pages.items():
    # Highlight the active button
    if st.session_state["active_page"] == page_key:
        if st.sidebar.button(page_label, key=f"nav_{page_key}", use_container_width=True, type="primary"):
            pass
    else:
        if st.sidebar.button(page_label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state["active_page"] = page_key
            st.rerun()

# Simulation Mode Status Card in Sidebar
st.sidebar.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
if st.session_state["simulation_mode"]:
    st.sidebar.markdown(
        """
        <div style="background-color: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 12px; text-align: center;">
            <span style="color: #fbbf24; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Simulation Mode Active</span>
            <p style="color: #d97706; font-size: 10px; margin: 4px 0 0 0;">IBM APIs simulated locally. Toggle in Settings.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        """
        <div style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px; text-align: center;">
            <span style="color: #34d399; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">IBM Cloud Live Connect</span>
            <p style="color: #059669; font-size: 10px; margin: 4px 0 0 0;">Connected to Watson Assistant & watsonx.ai</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Footer credits
st.sidebar.markdown(
    """
    <div style='position: fixed; bottom: 15px; width: 220px; font-size: 10px; color: #475569;'>
        <p style='margin: 0;'>Crisis360 AI - IBM Cloud Platform</p>
        <p style='margin: 2px 0 0 0;'>Granite Engine v3.0</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Route to active page
active_page = st.session_state["active_page"]

# Dynamically import page modules
if active_page == "Dashboard":
    from pages.dashboard import show_page
    show_page()
elif active_page == "Report Incident":
    from pages.report_incident import show_page
    show_page()
elif active_page == "AI Response Center":
    from pages.ai_response_center import show_page
    show_page()
elif active_page == "Analytics":
    from pages.analytics import show_page
    show_page()
elif active_page == "Incident History":
    from pages.incident_history import show_page
    show_page()
elif active_page == "Settings":
    from pages.settings import show_page
    show_page()
