import sys
import os
import json
from pathlib import Path

# Add root folder to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from services.incident_engine import initialize_database, get_all_incidents, create_incident, calculate_kpis, get_incident_by_id
from services.watsonx_service import WatsonxService
from services.assistant_service import AssistantService

def test_database():
    print("--- 1. Testing Database & Incident Engine ---")
    initialize_database()
    df = get_all_incidents()
    print(f"Total incidents found in DB: {len(df)}")
    
    # Test Create
    mock_data = {
        "reported_by": "Test Engineer",
        "description": "Flickering power supply ballast in laboratory basement.",
        "location": "Science Hall, basement",
        "people_affected": 0,
        "immediate_danger": "No",
        "additional_details": "Buzzing sounds."
    }
    new_id = create_incident(mock_data)
    print(f"Successfully created new incident. Assigned ID: {new_id}")
    
    # Test read by id
    incident = get_incident_by_id(new_id)
    assert incident is not None, "Failed to retrieve newly created incident"
    print(f"Incident {new_id} details matched: Location: {incident['location']}")
    
    # Test KPIs
    kpis = calculate_kpis()
    print("Calculated KPIs successfully:")
    for k, v in kpis.items():
        print(f"  {k}: {v}")
    print("Database test passed!\n")

def test_watsonx_service():
    print("--- 2. Testing watsonx.ai Service (Simulation Mode) ---")
    wx = WatsonxService(simulation_mode=True)
    
    print("Sending Fire Emergency details...")
    response = wx.analyze_incident(
        description="Smoke rising from server racks. Visible flames in UPS battery compartment.",
        location="Data Center Room 1",
        people_affected=2,
        immediate_danger="Yes",
        additional_details="Fire extinguisher deployed but flame is expanding."
    )
    
    print("Watsonx Response JSON:")
    print(json.dumps(response, indent=2))
    
    assert response["incident_type"] == "Fire Hazard", "Categorization failed"
    assert response["severity"] == "Critical", "Severity prediction failed"
    assert response["priority"] == "P1", "Priority assignment failed"
    assert response["escalation"]["escalate"] is True, "Escalation check failed"
    print("watsonx.ai test passed!\n")

def test_assistant_service():
    print("--- 3. Testing Watson Assistant Service (Simulation Mode) ---")
    assistant = AssistantService(simulation_mode=True)
    session_id = assistant.create_session()
    print(f"Created session ID: {session_id}")
    
    # Send a sequence of messages to simulate user intake
    state_ctx = None
    messages = [
        "hello",
        "Water is pooling in the basement near the high voltage power vault.",
        "Engineering Building, Basement A",
        "2",
        "Yes",
        "Fumes starting to smell like burnt plastic."
    ]
    
    for msg in messages:
        # Encode safely for console print
        safe_msg = msg.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
        print(f"User: '{safe_msg}'")
        res = assistant.send_message(session_id, msg, state_ctx)
        state_ctx = res.get("state_context")
        safe_response = res.get('response').encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
        print(f"Assistant:\n{safe_response}\n")
        
    print("Intake state data:")
    print(json.dumps(state_ctx["data"], indent=2))
    
    assert res["is_complete"] is False, "Should wait for 'Submit' response to complete"
    
    # Send submit
    res_final = assistant.send_message(session_id, "Submit", state_ctx)
    safe_final_user = "Submit".encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
    print(f"User: '{safe_final_user}'")
    safe_final_resp = res_final.get('response').encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
    print(f"Assistant:\n{safe_final_resp}\n")
    assert res_final["is_complete"] is True, "Flow failed to complete"
    print("Watson Assistant test passed!\n")

if __name__ == "__main__":
    print("=========================================")
    print("Crisis360 AI Service Verification Suite")
    print("=========================================\n")
    try:
        test_database()
        test_watsonx_service()
        test_assistant_service()
        print("ALL TESTS PASSED SUCCESSFULLY!")
    except Exception as e:
        print(f"TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
