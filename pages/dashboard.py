import streamlit as st
import pandas as pd
from datetime import datetime
from services.incident_engine import calculate_kpis, get_all_incidents
from utils.helpers import render_metric_card, get_severity_badge

def show_page():
    st.markdown("<h2 style='margin-bottom: 5px;'>🏠 Executive Command Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px;'>Real-time AI-powered crisis indicators, triage parameters, and department response SLAs.</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Calculate KPIs
    kpis = calculate_kpis()
    
    # Render primary KPI block
    st.markdown("<h4 style='color: #60a5fa; margin-bottom: 15px;'>Primary Operations Status</h4>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_metric_card("Total Reports", kpis["total_incidents"], "linear-gradient(to right, #60a5fa, #3b82f6)")
    with col2:
        render_metric_card("Active Open", kpis["open_incidents"], "linear-gradient(to right, #fb7185, #f43f5e)")
    with col3:
        render_metric_card("Resolved", kpis["closed_incidents"], "linear-gradient(to right, #34d399, #10b981)")
    with col4:
        render_metric_card("Critical Count", kpis["critical_incidents"], "linear-gradient(to right, #f87171, #ef4444)")
    with col5:
        render_metric_card("Avg Severity", kpis["avg_severity"], "linear-gradient(to right, #e2e8f0, #cbd5e1)")
        
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Render secondary KPI block
    st.markdown("<h4 style='color: #60a5fa; margin-bottom: 15px;'>Triage & SLA Analysis</h4>", unsafe_allow_html=True)
    
    col6, col7, col8, col9, col10 = st.columns(5)
    with col6:
        render_metric_card("Most Common", kpis["most_common"], "linear-gradient(to right, #818cf8, #6366f1)")
    with col7:
        render_metric_card("Response SLA", f"{kpis['sla_met_pct']}%", "linear-gradient(to right, #fbbf24, #f59e0b)")
    with col8:
        render_metric_card("Avg Resolution", f"{kpis['avg_resolution_hrs']} hrs", "linear-gradient(to right, #22d3ee, #06b6d4)")
    with col9:
        render_metric_card("Critical Today", kpis["critical_today"], "linear-gradient(to right, #f43f5e, #be123c)")
    with col10:
        render_metric_card("Teams Involved", kpis["departments_count"], "linear-gradient(to right, #a78bfa, #8b5cf6)")

    st.write("---")
    
    # Split layout: Critical active reports / Recent incidents list
    col_left, col_right = st.columns([1, 1])
    
    df = get_all_incidents()
    
    with col_left:
        st.markdown("<h3 style='color: #f87171;'>🚨 Active Critical Alerts</h3>", unsafe_allow_html=True)
        critical_active = df[(df["severity"].str.lower() == "critical") & (df["status"] != "Resolved")]
        
        if critical_active.empty:
            st.markdown(
                """
                <div style="background-color: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 16px;">
                    <span style="color: #34d399; font-weight: bold;">✓ All Systems Clear</span>
                    <p style="color: #a7f3d0; font-size: 13px; margin: 4px 0 0 0;">No active critical-severity incidents requiring immediate containment.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for _, row in critical_active.iterrows():
                # Glow active warning cards
                st.markdown(
                    f"""
                    <div class="critical-alert">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-weight: 800; font-size: 15px; color: #ef4444;">{row['incident_id']} - {row['incident_type']}</span>
                            <span class="badge badge-critical">Critical</span>
                        </div>
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #fecaca;">
                            <strong>Location:</strong> {row['location']}<br/>
                            <strong>Reported:</strong> {row['timestamp']}<br/>
                            <strong>Description:</strong> {row['description']}
                        </p>
                        <div style="background-color: rgba(0,0,0,0.2); padding: 8px; border-radius: 6px; font-size: 12px; color: #fca5a5; font-style: italic;">
                            <strong>Escalation:</strong> {row['escalate_reason']}
                        </div>
                        <div style="margin-top: 10px;">
                            <span style="font-size: 11px; font-weight: 700; color: #f87171; text-transform: uppercase;">Assigned Team: {row['assigned_department']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
    with col_right:
        st.markdown("<h3>📋 Recent Activity Logs</h3>", unsafe_allow_html=True)
        recent_df = df.sort_values(by="timestamp", ascending=False).head(5)
        
        if recent_df.empty:
            st.info("No incident reports found in the database.")
        else:
            for _, row in recent_df.iterrows():
                status_color = "#3b82f6"
                if row["status"] == "Resolved":
                    status_color = "#10b981"
                elif row["status"] == "In Progress":
                    status_color = "#f59e0b"
                elif row["status"] == "Assigned":
                    status_color = "#a78bfa"
                    
                severity_badge = get_severity_badge(row["severity"])
                
                st.markdown(
                    f"""
                    <div class="crisis-card" style="padding: 14px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: 700; font-size: 14px; color: #60a5fa;">{row['incident_id']} - {row['location']}</span>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                {severity_badge}
                                <span style="font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 4px; background-color: {status_color}; color: white; text-transform: uppercase;">{row['status']}</span>
                            </div>
                        </div>
                        <p style="margin: 0; font-size: 12.5px; color: #cbd5e1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            {row['description']}
                        </p>
                        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748b; margin-top: 6px;">
                            <span>Reported: {row['timestamp']}</span>
                            <span style="font-weight: 600; color: #94a3b8;">Risk Score: {row['risk_score']}/100</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
    st.write("---")
    
    # Separation Section "Why Watson Assistant + Watsonx?"
    st.markdown("<h3 style='color: #60a5fa;'>💡 System Architecture Design: Why Watson Assistant + Watsonx?</h3>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="crisis-card">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                <div>
                    <h5 style="color: #93c5fd; margin-bottom: 8px;">💬 1. Conversational Orchestration (Watson Assistant)</h5>
                    <p style="font-size: 13.5px; color: #cbd5e1; line-height: 1.5; margin: 0;">
                        IBM Watson Assistant manages the frontend dialogue flow, ensuring robust, validated, and structured conversational data collection. It guides the reporter systematically to gather:
                    </p>
                    <ul style="font-size: 13px; color: #94a3b8; margin: 8px 0 0 0; padding-left: 20px;">
                        <li>Incident description details</li>
                        <li>Precise physical location coordinates</li>
                        <li>Headcount of personnel affected or injured</li>
                        <li>Immediate life danger validation flags</li>
                    </ul>
                </div>
                <div>
                    <h5 style="color: #93c5fd; margin-bottom: 8px;">🧠 2. AI Decision Reasoning & Triage (IBM watsonx.ai)</h5>
                    <p style="font-size: 13.5px; color: #cbd5e1; line-height: 1.5; margin: 0;">
                        Once data collection completes, raw values are passed to IBM watsonx.ai (Granite). The AI Decision Engine reasons over the incident data, executing complex triage:
                    </p>
                    <ul style="font-size: 13px; color: #94a3b8; margin: 8px 0 0 0; padding-left: 20px;">
                        <li>Intelligent classification and department routing</li>
                        <li>Severity assessment & risk scoring (0-100)</li>
                        <li>Root cause prediction and SLA calculation</li>
                        <li>Executive advisory summary report writing</li>
                    </ul>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
