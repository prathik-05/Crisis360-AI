import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from config import DATA_DIR

CSV_PATH = DATA_DIR / "incidents.csv"

# Pre-populated realistic mock incidents
MOCK_INCIDENTS = [
    {
        "incident_id": "INC-1001",
        "timestamp": (datetime.now() - timedelta(days=25, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "reported_by": "Dr. Sarah Jenkins",
        "description": "Chemical spill in Chemistry Lab 304. Approximately 1 liter of hydrochloric acid leaked onto the bench and floor.",
        "location": "Science Wing, Building C, Room 304",
        "people_affected": 3,
        "immediate_danger": "Yes",
        "additional_details": "Spill kit deployed but fumes are strong. Ventilation activated.",
        "status": "Resolved",
        "assigned_department": "Environmental Health & Safety",
        "incident_type": "Chemical Hazard",
        "severity": "Major",
        "priority": "P2",
        "risk_score": 68,
        "confidence": 95,
        "estimated_response": "10 minutes",
        "immediate_actions": "Evacuate the room;Secure the area;Wear proper personal protective equipment (PPE);Neutralize spill with sodium bicarbonate.",
        "root_causes": "Improper chemical container storage;Damaged container shelving",
        "escalate": "False",
        "escalate_reason": "",
        "executive_summary": "Chemical spill occurred in Lab 304 involving hydrochloric acid. No injuries reported. Acid neutralized and cleaned by HAZMAT response team. Lab declared safe after air quality check.",
        "resolution_time_mins": 45.0,
        "assigned_to": "Officer Mark Vance"
    },
    {
        "incident_id": "INC-1002",
        "timestamp": (datetime.now() - timedelta(days=20, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
        "reported_by": "IT Helpdesk",
        "description": "Ransomware pop-up on multiple administrative computers in the finance department. Local network drives inaccessible.",
        "location": "Administration Building, 2nd Floor Finance Office",
        "people_affected": 15,
        "immediate_danger": "No",
        "additional_details": "Computers display a locking message demanding BTC. In-house servers disconnected to prevent lateral movement.",
        "status": "Resolved",
        "assigned_department": "Cybersecurity Operations",
        "incident_type": "Cybersecurity Breach",
        "severity": "Critical",
        "priority": "P1",
        "risk_score": 88,
        "confidence": 97,
        "estimated_response": "15 minutes",
        "immediate_actions": "Disconnect affected machines from network;Isolate core servers;Do not pay ransom;Initiate backup restoration sequence.",
        "root_causes": "Phishing email link clicked;Outdated system security patch",
        "escalate": "True",
        "escalate_reason": "Active malware propagation and business operations impacted.",
        "executive_summary": "Ransomware attack targeted finance systems. Prompt network isolation prevented server infection. Restored systems from offsite backups. Financial data verified secure.",
        "resolution_time_mins": 360.0,
        "assigned_to": "Analyst Ryan Reynolds"
    },
    {
        "incident_id": "INC-1003",
        "timestamp": (datetime.now() - timedelta(days=15, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "reported_by": "Security Guard Alan",
        "description": "Minor electrical sparks from the elevator breaker panel in the lobby.",
        "location": "Main Entrance Lobby, Elevator Control Room",
        "people_affected": 0,
        "immediate_danger": "Yes",
        "additional_details": "Smell of burning rubber. Elevator has been grounded and turned off.",
        "status": "Resolved",
        "assigned_department": "Facilities Management",
        "incident_type": "Infrastructure Failure",
        "severity": "Moderate",
        "priority": "P3",
        "risk_score": 42,
        "confidence": 92,
        "estimated_response": "30 minutes",
        "immediate_actions": "Cut main breaker power;Post Out of Service signs;Contact elevator technician.",
        "root_causes": "Loose wiring connection;Overloaded circuits",
        "escalate": "False",
        "escalate_reason": "",
        "executive_summary": "Breaker panel sparks grounded main lobby elevator. Maintenance technicians replaced the faulty relay board. Panel load tested and recertified.",
        "resolution_time_mins": 120.0,
        "assigned_to": "Tech David Miller"
    },
    {
        "incident_id": "INC-1004",
        "timestamp": (datetime.now() - timedelta(days=10, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "reported_by": "Professor David K.",
        "description": "Active smoke detector and smell of fire near the server room in the basement of Building B.",
        "location": "Building B, Basement Corridor, Room 05",
        "people_affected": 25,
        "immediate_danger": "Yes",
        "additional_details": "Alarms sounding in the building. Evacuation in progress.",
        "status": "In Progress",
        "assigned_department": "Emergency Response",
        "incident_type": "Fire Hazard",
        "severity": "Critical",
        "priority": "P1",
        "risk_score": 95,
        "confidence": 98,
        "estimated_response": "5 minutes",
        "immediate_actions": "Sound fire alarm;Evacuate all personnel;Contact local fire department;Shut off main power supply.",
        "root_causes": "Server UPS battery thermal runaway;Inadequate AC cooling",
        "escalate": "True",
        "escalate_reason": "High risk of fire spreading to structural building elements.",
        "executive_summary": "Smoke detected near basement server room. Building evacuated. Emergency responders on site. Server battery rack isolated. Fire department checking for structural heat signatures.",
        "resolution_time_mins": 0.0,
        "assigned_to": "Chief Fire Marshal Hunt"
    },
    {
        "incident_id": "INC-1005",
        "timestamp": (datetime.now() - timedelta(days=5, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
        "reported_by": "Receptionist Emily",
        "description": "Visitor slipped on wet stairs and is unable to stand up. Complaining of severe back pain.",
        "location": "North Entrance Stairs, Building A",
        "people_affected": 1,
        "immediate_danger": "No",
        "additional_details": "Rainy day, steps were wet. No wet floor sign was placed. Paramedics called.",
        "status": "Assigned",
        "assigned_department": "Medical Response",
        "incident_type": "Medical Emergency",
        "severity": "Major",
        "priority": "P2",
        "risk_score": 55,
        "confidence": 94,
        "estimated_response": "8 minutes",
        "immediate_actions": "Do not move the victim;Keep victim warm;Clear a pathway for emergency personnel;Place warning signs.",
        "root_causes": "Wet weather tracking;Missing warning signs;Lack of anti-slip tread",
        "escalate": "False",
        "escalate_reason": "",
        "executive_summary": "Visitor suffered physical injury from falling on stairs. Medical crew dispatched. Patient stabilized and transferred to ambulance. Steps dried and safety cones deployed.",
        "resolution_time_mins": 0.0,
        "assigned_to": "Paramedic Coordinator Jones"
    },
    {
        "incident_id": "INC-1006",
        "timestamp": (datetime.now() - timedelta(days=2, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
        "reported_by": "Lab Tech Frank",
        "description": "Fluorescent light fixture buzzing loudly and flickering. Smell of hot plastic in the hallway.",
        "location": "Building A, 1st Floor Corridor near Room 112",
        "people_affected": 0,
        "immediate_danger": "No",
        "additional_details": "Smell suggests electrical failure of the ballast unit. Not currently sparking.",
        "status": "Reported",
        "assigned_department": "Facilities Management",
        "incident_type": "Infrastructure Failure",
        "severity": "Minor",
        "priority": "P4",
        "risk_score": 15,
        "confidence": 90,
        "estimated_response": "2 hours",
        "immediate_actions": "Turn off light switch;Mark fixture out of service;Log maintenance work order.",
        "root_causes": "Ballast end-of-life component degradation",
        "escalate": "False",
        "escalate_reason": "",
        "executive_summary": "Ballast burnout reported in hallway corridor light. Light turned off, pending routine electrician replacement.",
        "resolution_time_mins": 0.0,
        "assigned_to": "Unassigned"
    }
]

def initialize_database():
    """
    Initializes the incidents.csv file if it does not exist.
    """
    if not CSV_PATH.exists():
        df = pd.DataFrame(MOCK_INCIDENTS)
        df.to_csv(CSV_PATH, index=False)
        print("Database initialized with mock incidents.")

def get_all_incidents():
    """
    Reads all incidents from CSV and returns them as a pandas DataFrame.
    """
    initialize_database()
    try:
        df = pd.read_csv(CSV_PATH)
        # Ensure correct column types
        df['people_affected'] = pd.to_numeric(df['people_affected'], errors='coerce').fillna(0).astype(int)
        df['risk_score'] = pd.to_numeric(df['risk_score'], errors='coerce').fillna(0).astype(int)
        df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce').fillna(0).astype(int)
        df['resolution_time_mins'] = pd.to_numeric(df['resolution_time_mins'], errors='coerce').fillna(0.0)
        return df
    except Exception as e:
        print(f"Error reading CSV database: {e}")
        return pd.DataFrame(columns=[
            "incident_id", "timestamp", "reported_by", "description", "location", 
            "people_affected", "immediate_danger", "additional_details", "status", 
            "assigned_department", "incident_type", "severity", "priority", 
            "risk_score", "confidence", "estimated_response", "immediate_actions", 
            "root_causes", "escalate", "escalate_reason", "executive_summary", 
            "resolution_time_mins", "assigned_to"
        ])

def get_incident_by_id(incident_id):
    """
    Returns a dictionary of a specific incident, or None.
    """
    df = get_all_incidents()
    match = df[df["incident_id"] == incident_id]
    if not match.empty:
        return match.iloc[0].to_dict()
    return None

def create_incident(data: dict):
    """
    Generates a new incident, assigns ID, and saves to CSV.
    """
    df = get_all_incidents()
    
    # Generate new ID (INC-100X)
    if not df.empty:
        # Extract numeric IDs and find max
        ids = df["incident_id"].str.extract(r'INC-(\d+)')[0].astype(int)
        next_id = f"INC-{ids.max() + 1}"
    else:
        next_id = "INC-1001"
        
    new_row = {
        "incident_id": next_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reported_by": data.get("reported_by", "Anonymous"),
        "description": data.get("description", ""),
        "location": data.get("location", "Not Specified"),
        "people_affected": int(data.get("people_affected", 0)),
        "immediate_danger": data.get("immediate_danger", "No"),
        "additional_details": data.get("additional_details", ""),
        "status": data.get("status", "Reported"),
        "assigned_department": data.get("assigned_department", "Unassigned"),
        "incident_type": data.get("incident_type", "Pending Analysis"),
        "severity": data.get("severity", "Moderate"),
        "priority": data.get("priority", "P3"),
        "risk_score": int(data.get("risk_score", 30)),
        "confidence": int(data.get("confidence", 80)),
        "estimated_response": data.get("estimated_response", "Unscheduled"),
        "immediate_actions": data.get("immediate_actions", ""),
        "root_causes": data.get("root_causes", "Unknown"),
        "escalate": str(data.get("escalate", "False")),
        "escalate_reason": data.get("escalate_reason", ""),
        "executive_summary": data.get("executive_summary", ""),
        "resolution_time_mins": float(data.get("resolution_time_mins", 0.0)),
        "assigned_to": data.get("assigned_to", "Unassigned")
    }
    
    # Append row
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    return next_id

def update_incident(incident_id, updates: dict):
    """
    Updates specific fields for an incident (e.g. status, assignment, etc.)
    """
    df = get_all_incidents()
    idx = df[df["incident_id"] == incident_id].index
    if len(idx) > 0:
        # If transitioning to 'Resolved', calculate resolution time if not already set
        if updates.get("status") == "Resolved":
            # get original timestamp
            orig_ts = df.loc[idx[0], "timestamp"]
            try:
                dt_orig = datetime.strptime(orig_ts, "%Y-%m-%d %H:%M:%S")
                dt_now = datetime.now()
                diff_mins = (dt_now - dt_orig).total_seconds() / 60.0
                updates["resolution_time_mins"] = round(diff_mins, 1)
            except Exception:
                updates["resolution_time_mins"] = 60.0 # Default fallback
                
        for key, value in updates.items():
            if key in df.columns:
                df.loc[idx[0], key] = value
                
        df.to_csv(CSV_PATH, index=False)
        return True
    return False

def calculate_kpis():
    """
    Calculates detailed metrics for the Dashboard.
    """
    df = get_all_incidents()
    
    total = len(df)
    if total == 0:
        return {
            "total_incidents": 0, "open_incidents": 0, "closed_incidents": 0, "critical_incidents": 0,
            "avg_severity": "N/A", "most_common": "None", "sla_met_pct": 100, "avg_resolution_hrs": 0.0,
            "critical_today": 0, "departments_count": 0
        }
        
    # Status breakdown
    closed_states = ["Resolved"]
    open_incidents = len(df[~df["status"].isin(closed_states)])
    closed_incidents = len(df[df["status"].isin(closed_states)])
    
    # Severity breakdown
    critical_incidents = len(df[df["severity"].str.lower() == "critical"])
    
    # Critical reported today
    today_str = datetime.now().strftime("%Y-%m-%d")
    critical_today = len(df[(df["severity"].str.lower() == "critical") & (df["timestamp"].str.contains(today_str))])
    
    # Average Risk Score / Severity map
    avg_risk = df["risk_score"].mean()
    if avg_risk >= 75:
        avg_sev = "Critical"
    elif avg_risk >= 50:
        avg_sev = "Major"
    elif avg_risk >= 25:
        avg_sev = "Moderate"
    else:
        avg_sev = "Minor"
        
    # Most common type
    if not df.empty:
        most_common = df["incident_type"].mode()
        most_common = most_common.iloc[0] if not most_common.empty else "N/A"
    else:
        most_common = "N/A"
        
    # SLA Met % (For MVP: P1 resolved in < 8 hours, P2 in < 24 hours, others in < 48 hours)
    sla_met_count = 0
    resolved_df = df[df["status"] == "Resolved"]
    total_resolved = len(resolved_df)
    
    for _, row in resolved_df.iterrows():
        res_time_hrs = row["resolution_time_mins"] / 60.0
        priority = row["priority"]
        if priority == "P1" and res_time_hrs <= 8.0:
            sla_met_count += 1
        elif priority == "P2" and res_time_hrs <= 24.0:
            sla_met_count += 1
        elif priority in ["P3", "P4"] and res_time_hrs <= 48.0:
            sla_met_count += 1
        elif priority not in ["P1", "P2", "P3", "P4"]:
            sla_met_count += 1
            
    sla_pct = int((sla_met_count / total_resolved) * 100) if total_resolved > 0 else 100
    
    # Average Resolution Time for resolved incidents (in hours)
    if total_resolved > 0:
        avg_res_hrs = round((resolved_df["resolution_time_mins"].mean()) / 60.0, 1)
    else:
        avg_res_hrs = 0.0
        
    # Affected unique departments
    departments_count = df[df["assigned_department"] != "Unassigned"]["assigned_department"].nunique()
    
    return {
        "total_incidents": total,
        "open_incidents": open_incidents,
        "closed_incidents": closed_incidents,
        "critical_incidents": critical_incidents,
        "avg_severity": avg_sev,
        "most_common": most_common,
        "sla_met_pct": sla_pct,
        "avg_resolution_hrs": avg_res_hrs,
        "critical_today": critical_today,
        "departments_count": departments_count
    }
