import streamlit as st
import os
import config
from services.incident_engine import initialize_database, get_all_incidents
from config import save_env_variables, CSV_PATH

def show_page():
    st.markdown("<h2 style='margin-bottom: 5px;'>⚙ Platform Settings</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px;'>Manage API connections, credentials, operational parameters, and database state.</p>", unsafe_allow_html=True)
    st.write("---")
    
    # ------------------ SECTION 1: MODE CONFIGURATION ------------------
    st.markdown("<h3>🔌 API Operation Mode</h3>", unsafe_allow_html=True)
    
    # Check if config has keys configured
    has_keys = bool(config.WATSONX_APIKEY) and bool(config.WATSONX_PROJECT_ID) and bool(config.WATSON_ASSISTANT_APIKEY) and bool(config.WATSON_ASSISTANT_ID)
    
    col_mode, col_info = st.columns([1, 2])
    
    with col_mode:
        sim_mode_toggle = st.toggle(
            "Activate Simulation Mode", 
            value=st.session_state["simulation_mode"],
            help="When active, IBM APIs are simulated locally. Turn off to connect to live IBM Cloud services."
        )
        
        if sim_mode_toggle != st.session_state["simulation_mode"]:
            st.session_state["simulation_mode"] = sim_mode_toggle
            st.success(f"Operation Mode updated: {'Simulation Mode' if sim_mode_toggle else 'Live Connect'}")
            st.rerun()
            
    with col_info:
        if st.session_state["simulation_mode"]:
            st.warning("⚠️ Simulation Mode Active: Local mock functions are being used. Live IBM Cloud Watson Assistant and watsonx.ai calls are bypassed.")
        else:
            if not has_keys:
                st.error("❌ Key Misconfiguration: IBM Cloud keys are missing. Configure credentials below or toggle Simulation Mode back on to avoid app crashes.")
            else:
                st.success("✓ Live Connect Active: IBM SDKs will attempt connection using configured keys.")

    st.write("---")
    
    # ------------------ SECTION 2: CREDENTIALS FORM ------------------
    st.markdown("<h3>🔑 IBM Cloud Credentials</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; color: #94a3b8;'>Specify your IBM Cloud IAM API Key, watsonx.ai project details, and Watson Assistant details. Saves to local .env configuration file.</p>", unsafe_allow_html=True)
    
    with st.form("credentials_form"):
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            st.markdown("<h5 style='color: #60a5fa; margin-bottom: 10px;'>IBM watsonx.ai</h5>", unsafe_allow_html=True)
            apikey_wx = st.text_input("watsonx.ai IAM API Key:", value=config.WATSONX_APIKEY, type="password")
            proj_id_wx = st.text_input("watsonx.ai Project ID:", value=config.WATSONX_PROJECT_ID)
            url_wx = st.text_input("watsonx.ai Endpoint URL:", value=config.WATSONX_URL)
            model_wx = st.text_input("watsonx.ai Granite Model ID:", value=config.WATSONX_MODEL)
            
        with col_w2:
            st.markdown("<h5 style='color: #60a5fa; margin-bottom: 10px;'>IBM Watson Assistant</h5>", unsafe_allow_html=True)
            apikey_wa = st.text_input("Watson Assistant API Key:", value=config.WATSON_ASSISTANT_APIKEY, type="password")
            id_wa = st.text_input("Watson Assistant ID:", value=config.WATSON_ASSISTANT_ID)
            url_wa = st.text_input("Watson Assistant URL:", value=config.WATSON_ASSISTANT_URL)
            
        submit_btn = st.form_submit_button("💾 Save Credentials & Reload Configurations")
        
        if submit_btn:
            variables = {
                "IBM_WATSONX_APIKEY": apikey_wx,
                "IBM_WATSONX_PROJECT_ID": proj_id_wx,
                "IBM_WATSONX_URL": url_wx,
                "IBM_WATSONX_MODEL": model_wx,
                "IBM_WATSON_ASSISTANT_APIKEY": apikey_wa,
                "IBM_WATSON_ASSISTANT_ID": id_wa,
                "IBM_WATSON_ASSISTANT_URL": url_wa
            }
            try:
                save_env_variables(variables)
                # Recalculate default simulation mode state
                st.session_state["simulation_mode"] = config.is_simulation_mode()
                st.success("Credentials saved to .env and environment reloaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to write configuration variables: {e}")
                
    st.write("---")
    
    # ------------------ SECTION 3: SYSTEM ADMINISTRATION ------------------
    st.markdown("<h3>🛡️ Database Administration</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; color: #94a3b8;'>Actions to reset case database state or restore default testing reports.</p>", unsafe_allow_html=True)
    
    col_reset, col_desc = st.columns([1, 2])
    with col_reset:
        if st.button("🚨 Reset Database to Defaults", type="primary", use_container_width=True):
            try:
                # Remove CSV if exists
                if CSV_PATH.exists():
                    os.remove(CSV_PATH)
                # Re-initialize
                initialize_database()
                st.success("CSV database deleted and re-initialized with mock records.")
                st.rerun()
            except Exception as e:
                st.error(f"Reset failed: {e}")
                
    with col_desc:
        st.markdown(
            """
            <div style="font-size: 12px; color: #94a3b8; line-height: 1.5;">
                <strong>WARNING:</strong> Resetting database deletes all manually logged incidents and reverts 'incidents.csv' to the 6 default mock incidents. Restores SLA parameters, status timelines, and demo reports.
            </div>
            """,
            unsafe_allow_html=True
        )
