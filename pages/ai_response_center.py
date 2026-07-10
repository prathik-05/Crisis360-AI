import streamlit as st
import json
from services.incident_engine import get_all_incidents, get_incident_by_id, update_incident
from services.watsonx_service import WatsonxService
from utils.helpers import render_risk_gauge, render_escalation_banner, render_root_cause_prediction, get_severity_badge, render_timeline

def show_page():
    st.markdown("<h2 style='margin-bottom: 5px;'>🤖 AI Response Center</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px;'>IBM watsonx.ai Granite Decision Engine. Triage categorization, risk levels, root causes, and safety actions.</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Get all incidents
    df = get_all_incidents()
    
    if df.empty:
        st.info("No incident reports available. Please go to 'Report Incident' to log an issue.")
        return
        
    # Get incident choices for selectbox
    choices = [f"{row['incident_id']} - {row['location']} ({row['status']})" for _, row in df.iterrows()]
    
    # Determine default selection index
    default_idx = 0
    if st.session_state["selected_incident_id"]:
        match_idx = df[df["incident_id"] == st.session_state["selected_incident_id"]].index
        if len(match_idx) > 0:
            # find location in choices list
            target_id = st.session_state["selected_incident_id"]
            for idx, choice in enumerate(choices):
                if choice.startswith(target_id):
                    default_idx = idx
                    break
                    
    selected_choice = st.selectbox("Select Incident Report to Assess:", choices, index=default_idx)
    selected_id = selected_choice.split(" - ")[0]
    
    # Store currently selected id in session state
    st.session_state["selected_incident_id"] = selected_id
    
    incident = get_incident_by_id(selected_id)
    if not incident:
        st.error("Selected incident not found.")
        return
        
    # Show Raw Report Card
    st.markdown("<h3>📋 Raw Intake Data</h3>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="crisis-card">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px;">
                <div><strong>Reporter:</strong> {incident['reported_by']}</div>
                <div><strong>Intake Date:</strong> {incident['timestamp']}</div>
                <div><strong>Physical Location:</strong> {incident['location']}</div>
                <div><strong>Headcount Affected:</strong> {incident['people_affected']}</div>
                <div><strong>Immediate Life Danger:</strong> {incident['immediate_danger']}</div>
                <div><strong>Current Processing Phase:</strong> {incident['status']}</div>
            </div>
            <strong>Description:</strong>
            <p style="background-color: rgba(0,0,0,0.25); padding: 12px; border-radius: 8px; font-size: 13.5px; border: 1px solid #1e293b; margin: 8px 0 0 0;">
                {incident['description']}
            </p>
            <div style="margin-top: 8px;">
                <strong>Additional Context:</strong> {incident['additional_details']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Timeline
    render_timeline(incident["status"])
    st.write("")
    
    # If the incident has not been processed yet (status is "Reported")
    if incident["status"] == "Reported":
        st.warning("Decision Status: UNTRIAGED. This incident has not been analyzed by IBM watsonx.ai Granite model.")
        
        if st.button("⚡ Execute IBM watsonx.ai Decision Engine", type="primary", use_container_width=True):
            with st.spinner("Analyzing incident parameters using Granite-3-8b-instruct..."):
                watsonx = WatsonxService(simulation_mode=st.session_state["simulation_mode"])
                
                # Call watsonx service
                analysis_results = watsonx.analyze_incident(
                    description=incident["description"],
                    location=incident["location"],
                    people_affected=incident["people_affected"],
                    immediate_danger=incident["immediate_danger"],
                    additional_details=incident["additional_details"]
                )
                
                # Save results back to incident in database
                # Convert list to semicolon-delimited string
                actions_str = ";".join(analysis_results.get("immediate_actions", []))
                causes_str = ";".join(analysis_results.get("root_causes", []))
                
                # Convert escalation bool to string
                esc_dict = analysis_results.get("escalation", {"escalate": False, "reason": ""})
                escalate_bool = str(esc_dict.get("escalate", False))
                escalate_reason = esc_dict.get("reason", "")
                
                updates = {
                    "status": "AI Classified",
                    "incident_type": analysis_results.get("incident_type", "Safety Hazard"),
                    "severity": analysis_results.get("severity", "Moderate"),
                    "priority": analysis_results.get("priority", "P3"),
                    "risk_score": int(analysis_results.get("risk_score", 30)),
                    "confidence": int(analysis_results.get("confidence", 80)),
                    "estimated_response": analysis_results.get("estimated_response", "30 minutes"),
                    "assigned_department": analysis_results.get("recommended_team", "Facilities Management"),
                    "immediate_actions": actions_str,
                    "root_causes": causes_str,
                    "escalate": escalate_bool,
                    "escalate_reason": escalate_reason,
                    "executive_summary": json.dumps(analysis_results.get("executive_summary", {}))
                }
                
                # Save updates
                update_incident(selected_id, updates)
                st.success("Triage analysis complete! Incident routed and prioritized.")
                st.rerun()
    else:
        # Incident has been processed - show advanced decision dashboard
        st.markdown("<h3>🧠 AI Response Cockpit</h3>", unsafe_allow_html=True)
        
        # Risk score and warning banner on top
        col_gauge, col_esc = st.columns([1, 1])
        with col_gauge:
            render_risk_gauge(incident["risk_score"])
        with col_esc:
            # Escalation
            escalate_bool = str(incident.get("escalate", "False")).lower() == "true"
            render_escalation_banner(escalate_bool, incident.get("escalate_reason", ""))
            
            # Root Cause Box
            causes_raw = incident.get("root_causes", "")
            if isinstance(causes_raw, list):
                causes = causes_raw
            else:
                causes = [c.strip() for c in causes_raw.split(";") if c.strip()]
            render_root_cause_prediction(causes)

        # Classification parameters card
        st.markdown(
            f"""
            <div class="crisis-card">
                <h4 style="margin: 0 0 16px 0; color: #60a5fa;">Triage Metrics</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px;">
                    <div>
                        <span style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; display: block; margin-bottom: 2px;">Assigned Department</span>
                        <strong style="color: #f1f5f9; font-size: 14.5px;">{incident['assigned_department']}</strong>
                    </div>
                    <div>
                        <span style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; display: block; margin-bottom: 2px;">Classification</span>
                        <strong style="color: #f1f5f9; font-size: 14.5px;">{incident['incident_type']}</strong>
                    </div>
                    <div>
                        <span style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; display: block; margin-bottom: 2px;">Severity Index</span>
                        <strong style="color: #fecaca; font-size: 14.5px;">{get_severity_badge(incident['severity'])}</strong>
                    </div>
                    <div>
                        <span style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; display: block; margin-bottom: 2px;">Response Priority</span>
                        <strong style="color: #fbd38d; font-size: 14.5px;">{incident['priority']}</strong>
                    </div>
                    <div>
                        <span style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; display: block; margin-bottom: 2px;">SLA Dispatch Time</span>
                        <strong style="color: #93c5fd; font-size: 14.5px;">{incident['estimated_response']}</strong>
                    </div>
                    <div>
                        <span style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; display: block; margin-bottom: 2px;">Model Confidence</span>
                        <strong style="color: #34d399; font-size: 14.5px;">{incident['confidence']}%</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Split actions and executive summary details
        col_act, col_sum = st.columns([1, 1])
        
        with col_act:
            st.markdown("<h4 style='color: #60a5fa;'>🛠 Recommended Safety Actions</h4>", unsafe_allow_html=True)
            
            # parse actions
            act_raw = incident.get("immediate_actions", "")
            if isinstance(act_raw, list):
                actions = act_raw
            else:
                actions = [a.strip() for a in act_raw.split(";") if a.strip()]
                
            for idx, action in enumerate(actions):
                st.checkbox(action, value=False, key=f"act_{selected_id}_{idx}")
                
        with col_sum:
            st.markdown("<h4 style='color: #60a5fa;'>📄 Consulting Executive Summary</h4>", unsafe_allow_html=True)
            
            # parse summary
            summary_raw = incident.get("executive_summary", {})
            if isinstance(summary_raw, str):
                try:
                    summary_data = json.loads(summary_raw)
                except Exception:
                    summary_data = {
                        "summary": summary_raw,
                        "business_impact": "Operational interruptions reported. Ongoing threat mitigation.",
                        "recommended_actions": "Monitor remediation checklist. Log all recovery hours.",
                        "risk_level": "High-priority classification.",
                        "next_steps": "Complete incident post-mortem analysis."
                    }
            else:
                summary_data = summary_raw
                
            st.markdown(
                f"""
                <div class="crisis-card" style="padding: 18px; background-color: rgba(15, 23, 42, 0.45);">
                    <p style="font-size: 13px; margin: 0 0 10px 0;"><strong>Incident Summary:</strong> {summary_data.get('summary', 'N/A')}</p>
                    <p style="font-size: 13px; margin: 0 0 10px 0;"><strong>Business Impact:</strong> {summary_data.get('business_impact', 'N/A')}</p>
                    <p style="font-size: 13px; margin: 0 0 10px 0;"><strong>Recommended Action:</strong> {summary_data.get('recommended_actions', 'N/A')}</p>
                    <p style="font-size: 13px; margin: 0 0 10px 0;"><strong>Risk level:</strong> {summary_data.get('risk_level', 'N/A')}</p>
                    <p style="font-size: 13px; margin: 0;"><strong>Next Steps:</strong> {summary_data.get('next_steps', 'N/A')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Re-execute button
        st.write("---")
        if st.button("🔄 Re-run watsonx.ai Decision Engine", use_container_width=True):
            # Change status back to reported to allow re-running
            update_incident(selected_id, {"status": "Reported"})
            st.rerun()
