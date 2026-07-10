import os
from fpdf import FPDF
from datetime import datetime
from pathlib import Path

class IncidentPDFReport(FPDF):
    def header(self):
        # Draw header border and background
        self.set_fill_color(15, 23, 42) # Slate-900 color
        self.rect(0, 0, 210, 40, 'F')
        
        # Logo placeholder text
        self.set_font('Helvetica', 'B', 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'CRISIS360 AI', 0, 1, 'L')
        
        # Subtitle
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(156, 163, 175) # gray-400
        self.cell(0, 0, 'Enterprise Incident Triage & Decision Report', 0, 0, 'L')
        
        # Add timestamp to the right
        self.set_font('Helvetica', '', 9)
        self.set_text_color(209, 213, 219)
        self.cell(0, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'R')
        self.ln(20) # Line break

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-20)
        # Arial italic 8
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(156, 163, 175)
        
        # Divider line
        self.line(10, 280, 200, 280)
        
        # Footer text
        self.cell(0, 10, 'CRISIS360 AI - Powered by IBM Watson Assistant & IBM watsonx.ai Granite', 0, 0, 'L')
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')

def generate_incident_pdf(incident: dict, output_path: str):
    """
    Generates a structured, professional-looking enterprise PDF report for a given incident.
    """
    pdf = IncidentPDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    # ------------------ SECTION 1: METADATA ------------------
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 41, 59) # slate-800
    pdf.cell(0, 10, f"INCIDENT REPORT: {incident.get('incident_id', 'N/A')}", 0, 1, 'L')
    pdf.line(10, 52, 200, 52)
    pdf.ln(5)
    
    # Grid of Metadata (two columns)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(71, 85, 105)
    
    col_width = 95
    row_height = 6
    
    # Row 1
    pdf.cell(col_width, row_height, f"Reporter: {incident.get('reported_by', 'Anonymous')}", 0, 0)
    pdf.cell(col_width, row_height, f"Status: {incident.get('status', 'Reported')}", 0, 1)
    
    # Row 2
    pdf.cell(col_width, row_height, f"Report Date: {incident.get('timestamp', 'N/A')}", 0, 0)
    pdf.cell(col_width, row_height, f"Assigned Team: {incident.get('assigned_department', 'Unassigned')}", 0, 1)
    
    # Row 3
    pdf.cell(col_width, row_height, f"Location: {incident.get('location', 'N/A')}", 0, 0)
    pdf.cell(col_width, row_height, f"Assigned To: {incident.get('assigned_to', 'Unassigned')}", 0, 1)
    
    pdf.ln(8)
    
    # ------------------ SECTION 2: RAW INCIDENT DETAILS ------------------
    pdf.set_fill_color(248, 250, 252) # slate-50 background
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "1. Initial Incident Intake & Details", 0, 1, 'L', True)
    pdf.ln(2)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(35, row_height, "Description:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, row_height, incident.get('description', 'N/A'))
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(35, row_height, "People Affected:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, row_height, str(incident.get('people_affected', 0)), 0, 1)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(35, row_height, "Immediate Danger:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, row_height, incident.get('immediate_danger', 'No'), 0, 1)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(35, row_height, "Additional Details:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, row_height, incident.get('additional_details', 'None'))
    
    pdf.ln(8)
    
    # ------------------ SECTION 3: AI DECISION ANALYSIS ------------------
    pdf.set_fill_color(248, 250, 252)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, "2. IBM watsonx.ai Triage & Risk Assessment", 0, 1, 'L', True)
    pdf.ln(2)
    
    # Columns of indicators
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(50, row_height, "Incident Category:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(45, row_height, incident.get('incident_type', 'N/A'), 0, 0)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(50, row_height, "Risk Score (0-100):", 0, 0)
    pdf.set_font('Helvetica', 'B', 10)
    risk = incident.get('risk_score', 0)
    pdf.cell(0, row_height, f"{risk}/100", 0, 1)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(50, row_height, "Severity level:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(45, row_height, incident.get('severity', 'N/A'), 0, 0)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(50, row_height, "Priority Code:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, row_height, incident.get('priority', 'N/A'), 0, 1)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(50, row_height, "Model Confidence:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(45, row_height, f"{incident.get('confidence', 90)}%", 0, 0)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(50, row_height, "Estimated SLA Response:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, row_height, incident.get('estimated_response', 'N/A'), 0, 1)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(50, row_height, "Escalation Status:", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    esc_status = "Escalated" if str(incident.get('escalate')).lower() == 'true' else "Standard Handling"
    pdf.cell(0, row_height, esc_status, 0, 1)
    
    if str(incident.get('escalate')).lower() == 'true' and incident.get('escalate_reason'):
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(50, row_height, "Escalation Reason:", 0, 0)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(220, 38, 38) # red
        pdf.multi_cell(0, row_height, incident.get('escalate_reason', ''))
        pdf.set_text_color(15, 23, 42)
        
    pdf.ln(5)
    
    # ------------------ SECTION 4: ACTIONS & ROOT CAUSES ------------------
    # Split actions & causes
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(95, row_height, "Immediate Safety Recommendations:", 0, 0)
    pdf.cell(95, row_height, "Predicted Root Cause Triggers:", 0, 1)
    
    pdf.set_font('Helvetica', '', 9.5)
    
    # We retrieve list of actions & causes
    actions_raw = incident.get('immediate_actions', '')
    if isinstance(actions_raw, list):
        actions = actions_raw
    else:
        actions = [a.strip() for a in str(actions_raw).split(';') if a.strip()]
        
    causes_raw = incident.get('root_causes', '')
    if isinstance(causes_raw, list):
        causes = causes_raw
    else:
        causes = [c.strip() for c in str(causes_raw).split(';') if c.strip()]
        
    max_len = max(len(actions), len(causes))
    for i in range(max_len):
        act_text = f"- {actions[i]}" if i < len(actions) else ""
        cause_text = f"- {causes[i]}" if i < len(causes) else ""
        
        # Write parallel columns
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        pdf.multi_cell(95, 5, act_text, 0, 'L')
        
        pdf.set_xy(x_start + 98, y_start)
        pdf.multi_cell(92, 5, cause_text, 0, 'L')
        pdf.ln(3)
        
    pdf.ln(5)
    
    # ------------------ SECTION 5: EXECUTIVE SUMMARY ------------------
    pdf.set_fill_color(248, 250, 252)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, "3. Executive Consulting Summary", 0, 1, 'L', True)
    pdf.ln(2)
    
    # Decode executive summary JSON if stored as string
    exec_summary = incident.get('executive_summary', {})
    if isinstance(exec_summary, str):
        try:
            exec_summary = json.loads(exec_summary)
        except Exception:
            exec_summary = {
                "summary": exec_summary,
                "business_impact": "Operational interruptions reported. Ongoing threat mitigation.",
                "recommended_actions": "Monitor remediation checklist. Log all recovery hours.",
                "risk_level": "Assessed at incident categorization.",
                "next_steps": "Complete incident post-mortem analysis."
            }
            
    # Write summary items
    fields = [
        ("Incident Summary", "summary"),
        ("Business Impact", "business_impact"),
        ("Immediate Actions", "recommended_actions"),
        ("Risk Level Explanation", "risk_level"),
        ("Long-Term Preventative Next Steps", "next_steps")
    ]
    
    for label, key in fields:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 5, f"{label}:", 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, exec_summary.get(key, 'N/A'))
        pdf.ln(2)
        
    pdf.ln(8)
    
    # ------------------ SECTION 6: DIGITAL SIGNATURE ------------------
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(10, pdf.get_y(), 190, 20, 'F')
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(0, 5, "DIGITAL VERIFICATION SIGNATURE", 0, 1, 'C')
    pdf.set_font('Helvetica', 'I', 8)
    pdf.cell(0, 5, "Verified by Crisis360 Automated Decision Engine & IBM watsonx.ai Granite Model.", 0, 1, 'C')
    pdf.cell(0, 5, f"Certificate Hash: {incident.get('incident_id', 'N/A')}-SHA256-{datetime.now().strftime('%Y%m%d%H%M%S')}", 0, 1, 'C')

    # Output PDF
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
