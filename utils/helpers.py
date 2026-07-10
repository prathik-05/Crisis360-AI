import streamlit as st

def local_css(file_path):
    """
    Injects custom CSS from the file into the Streamlit app.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        # Fallback if CSS loading fails
        pass

def get_severity_badge(severity):
    """
    Returns the HTML badge code for a specific severity.
    """
    sev_lower = str(severity).lower()
    if sev_lower == "critical":
        return '<span class="badge badge-critical">Critical</span>'
    elif sev_lower in ["major", "high"]:
        return '<span class="badge badge-major">Major</span>'
    elif sev_lower in ["moderate", "medium"]:
        return '<span class="badge badge-moderate">Moderate</span>'
    else:
        return '<span class="badge badge-minor">Minor</span>'

def render_metric_card(label, value, color_gradient=None):
    """
    Renders a premium metric card using HTML.
    """
    gradient_style = ""
    if color_gradient:
        gradient_style = f"background: {color_gradient}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
        
    card_html = f"""
    <div class="metric-card">
        <div class="metric-value" style="{gradient_style}">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_timeline(current_status):
    """
    Renders an interactive and visually polished timeline step diagram.
    """
    statuses = ["Reported", "AI Classified", "Assigned", "In Progress", "Resolved"]
    
    # Determine the status index
    current_index = -1
    for i, status in enumerate(statuses):
        if status.lower() == str(current_status).lower().replace("_", " "):
            current_index = i
            break
    
    # Calculate progress width percentage (0% to 100%)
    if current_index == -1:
        progress_width = 0
    else:
        progress_width = (current_index / (len(statuses) - 1)) * 90  # Max 90% wide line
        
    timeline_html = f"""
    <div class="timeline-stepper">
        <div class="timeline-progress-bar" style="width: calc({progress_width}% + 5%);"></div>
    """
    
    for i, status in enumerate(statuses):
        step_class = ""
        icon = str(i + 1)
        
        # If the incident is fully Resolved, show all steps as completed with checkmarks
        if str(current_status).lower().replace("_", " ") == "resolved":
            step_class = "completed"
            icon = "✓"
        else:
            if i == current_index:
                step_class = "active"
            elif i < current_index:
                step_class = "completed"
                icon = "✓"
            
        timeline_html += f"""
        <div class="timeline-step {step_class}">
            <div class="timeline-node">{icon}</div>
            <div class="timeline-label">{status}</div>
        </div>
        """
        
    timeline_html += "</div>"
    st.markdown(timeline_html, unsafe_allow_html=True)

def render_risk_gauge(score):
    """
    Renders a premium glowing progress bar and numeric indicator representing the risk score.
    """
    score = max(0, min(100, int(score)))
    
    # Color calculations based on score
    if score >= 75:
        level = "Critical Risk"
        color = "#ef4444"
        bg_glow = "rgba(239, 68, 68, 0.2)"
    elif score >= 50:
        level = "High Risk"
        color = "#f59e0b"
        bg_glow = "rgba(245, 158, 11, 0.2)"
    elif score >= 25:
        level = "Moderate Risk"
        color = "#3b82f6"
        bg_glow = "rgba(59, 130, 246, 0.2)"
    else:
        level = "Low Risk"
        color = "#10b981"
        bg_glow = "rgba(16, 185, 129, 0.2)"
        
    gauge_html = f"""
    <div class="risk-gauge-container crisis-card" style="border-color: {color}; box-shadow: 0 10px 30px {bg_glow};">
        <div class="metric-label">Incident Risk Analysis</div>
        <div class="risk-score-display" style="color: {color}; text-shadow: 0 0 15px {color};">{score} <span style="font-size: 20px; color: #64748b;">/ 100</span></div>
        <div class="risk-level-label" style="color: {color};">{level}</div>
        <div style="width: 100%; background-color: #1e293b; border-radius: 9999px; height: 10px; margin-top: 15px; overflow: hidden; position: relative;">
            <div style="width: {score}%; background-color: {color}; height: 100%; border-radius: 9999px; box-shadow: 0 0 10px {color}; transition: width 1s ease;"></div>
        </div>
    </div>
    """
    st.markdown(gauge_html, unsafe_allow_html=True)

def render_escalation_banner(escalate, reason):
    """
    Renders an escalation status warning banner.
    """
    if escalate:
        st.markdown(f"""
        <div class="critical-alert">
            <h4 style="margin: 0 0 8px 0; color: #f87171; display: flex; align-items: center;">
                🚨 EXECUTIVE ESCALATION RECOMMENDED
            </h4>
            <p style="margin: 0; color: #fca5a5; font-size: 14px;">
                <strong>Reason:</strong> {reason}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
            <h4 style="margin: 0; color: #34d399; font-size: 14px; display: flex; align-items: center;">
                ✓ Standard SLA Handling: Incident falls within default departmental thresholds. No executive escalation required.
            </h4>
        </div>
        """, unsafe_allow_html=True)

def render_root_cause_prediction(causes):
    """
    Renders root cause suggestions.
    """
    if not causes:
        return
        
    if isinstance(causes, str):
        causes_list = [causes]
    elif isinstance(causes, list):
        causes_list = causes
    else:
        causes_list = []
        
    html = """
    <div class="crisis-card">
        <h4 style="margin: 0 0 12px 0; color: #60a5fa;">🔍 AI Predicted Root Causes</h4>
        <ul style="margin: 0; padding-left: 20px; color: #cbd5e1; font-size: 14px;">
    """
    for cause in causes_list:
        html += f"<li style='margin-bottom: 6px;'>{cause}</li>"
    html += """
        </ul>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
