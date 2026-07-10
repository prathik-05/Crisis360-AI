import streamlit as st
import pandas as pd
import os
from services.incident_engine import get_all_incidents, update_incident, get_incident_by_id
from services.report_service import generate_incident_pdf
from utils.helpers import get_severity_badge, render_timeline

def show_page():
    st.markdown("<h2 style='margin-bottom: 5px;'>📄 Admin Monitoring Panel & History</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px;'>Manage active cases, update dispatcher workflows, assign responding agents, and export digital verification reports.</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Load all incidents
    df = get_all_incidents()
    
    if df.empty:
        st.info("No incident reports recorded in the database.")
        return
        
    # Search, Filter, Sort Controls in a multi-column block
    col_search, col_filter, col_sort = st.columns([2, 1, 1])
    
    with col_search:
        search_query = st.text_input("🔍 Search Incident ID, Location, or Description:", value="")
        
    with col_filter:
        status_types = ["All Statuses"] + list(df["status"].unique())
        selected_status = st.selectbox("Filter by Status:", status_types)
        
    with col_sort:
        sort_opts = {
            "Newest First": ("timestamp", False),
            "Oldest First": ("timestamp", True),
            "Risk Score: High to Low": ("risk_score", False),
            "Risk Score: Low to High": ("risk_score", True)
        }
        selected_sort = st.selectbox("Sort by:", list(sort_opts.keys()))
        
    # Apply search, filters, and sorting
    filtered_df = df.copy()
    
    if search_query:
        search_query = search_query.lower()
        filtered_df = filtered_df[
            filtered_df["incident_id"].str.lower().contains(search_query) |
            filtered_df["location"].str.lower().contains(search_query) |
            filtered_df["description"].str.lower().contains(search_query) |
            filtered_df["reported_by"].str.lower().contains(search_query)
        ]
        
    if selected_status != "All Statuses":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]
        
    sort_col, sort_asc = sort_opts[selected_sort]
    filtered_df = filtered_df.sort_values(by=sort_col, ascending=sort_asc)
    
    # Display Incidents Data Grid
    st.markdown(f"<p style='color: #94a3b8; font-size: 13px; font-weight: bold;'>Showing {len(filtered_df)} Incident reports</p>", unsafe_allow_html=True)
    
    # Build clean interactive table list
    for _, row in filtered_df.iterrows():
        status_val = row["status"]
        status_color = "#3b82f6"
        if status_val == "Resolved":
            status_color = "#10b981"
        elif status_val == "In Progress":
            status_color = "#f59e0b"
        elif status_val == "Assigned":
            status_color = "#a78bfa"
            
        severity_badge = get_severity_badge(row["severity"])
        
        # Grid details header
        st.markdown(
            f"""
            <div class="crisis-card" style="padding: 18px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span style="font-weight: 800; font-size: 16px; color: #60a5fa;">{row['incident_id']}</span>
                        <span style="color: #64748b; font-size: 12px; margin-left: 10px;">{row['timestamp']}</span>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        {severity_badge}
                        <span class="badge" style="background-color: {status_color}; color: white; border: none;">{status_val}</span>
                        <span style="font-size: 12px; font-weight: 700; color: #94a3b8;">Risk Score: {row['risk_score']}/100</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 20px;">
                    <div>
                        <p style="margin: 0; font-size: 13px; color: #e2e8f0;">
                            <strong>Location:</strong> {row['location']}<br/>
                            <strong>Description:</strong> {row['description']}
                        </p>
                    </div>
                    <div style="border-left: 1px solid #1e293b; padding-left: 20px; font-size: 12.5px; color: #94a3b8;">
                        <strong>Department:</strong> {row['assigned_department']}<br/>
                        <strong>Assigned Responder:</strong> {row['assigned_to']}<br/>
                        <strong>Priority:</strong> {row['priority']} | <strong>SLA Response:</strong> {row['estimated_response']}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Action Panel Expander for each incident
        with st.expander(f"⚙️ Manage Operations Context for {row['incident_id']}"):
            # Display current timeline
            st.markdown("<p style='font-size: 12px; font-weight: bold; color: #60a5fa; margin-bottom: 5px;'>Operations Status Timeline</p>", unsafe_allow_html=True)
            render_timeline(row["status"])
            st.write("")
            
            # Form to assign, transition status, export PDF
            col_act_status, col_act_dept, col_act_to = st.columns(3)
            
            # Status list
            status_list = ["Reported", "AI Classified", "Assigned", "In Progress", "Resolved"]
            status_idx = status_list.index(row["status"]) if row["status"] in status_list else 0
            
            with col_act_status:
                new_status = st.selectbox(
                    "Transition Status:", 
                    status_list, 
                    index=status_idx,
                    key=f"status_select_{row['incident_id']}"
                )
                
            with col_act_dept:
                departments = ["Unassigned", "Emergency Response", "Facilities Management", "Cybersecurity Operations", "Environmental Health & Safety", "Medical Response"]
                dept_idx = departments.index(row["assigned_department"]) if row["assigned_department"] in departments else 0
                new_dept = st.selectbox(
                    "Re-route Department:", 
                    departments, 
                    index=dept_idx,
                    key=f"dept_select_{row['incident_id']}"
                )
                
            with col_act_to:
                responders = ["Unassigned", "Officer Mark Vance", "Analyst Ryan Reynolds", "Tech David Miller", "Chief Fire Marshal Hunt", "Paramedic Coordinator Jones", "Officer Jane Doe"]
                resp_idx = responders.index(row["assigned_to"]) if row["assigned_to"] in responders else 0
                new_resp = st.selectbox(
                    "Assign Responder:", 
                    responders, 
                    index=resp_idx,
                    key=f"resp_select_{row['incident_id']}"
                )
                
            # Submit updates
            col_save, col_pdf, col_analyze = st.columns([1, 1, 1.2])
            with col_save:
                if st.button("💾 Apply Changes", key=f"save_btn_{row['incident_id']}", use_container_width=True):
                    updates = {
                        "status": new_status,
                        "assigned_department": new_dept,
                        "assigned_to": new_resp
                    }
                    update_incident(row["incident_id"], updates)
                    st.success(f"Incident {row['incident_id']} updated.")
                    st.rerun()
                    
            with col_pdf:
                # PDF report path
                pdf_filename = f"{row['incident_id']}_report.pdf"
                pdf_dir = os.path.join("data", "reports")
                pdf_path = os.path.join(pdf_dir, pdf_filename)
                
                # Check and generate PDF report
                try:
                    generate_incident_pdf(row.to_dict(), pdf_path)
                    
                    with open(pdf_path, "rb") as f:
                        pdf_data = f.read()
                        
                    st.download_button(
                        label="📥 Export PDF Report",
                        data=pdf_data,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        key=f"pdf_btn_{row['incident_id']}",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Failed to generate report PDF: {e}")
                    
            with col_analyze:
                if st.button("🤖 Inspect AI Assessment", key=f"inspect_btn_{row['incident_id']}", use_container_width=True):
                    # Set selected incident in state and route page
                    st.session_state["selected_incident_id"] = row["incident_id"]
                    st.session_state["active_page"] = "AI Response Center"
                    st.rerun()
