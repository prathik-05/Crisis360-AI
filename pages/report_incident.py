import streamlit as st
from services.assistant_service import AssistantService
from services.incident_engine import create_incident
from utils.helpers import local_css

def show_page():
    st.markdown("<h2 style='margin-bottom: 5px;'>📝 AI Incident Intake</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px;'>Report workplace incidents via conversation. Powered by IBM Watson Assistant.</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Initialize assistant service
    assistant = AssistantService(simulation_mode=st.session_state["simulation_mode"])
    
    # Initialize chat history and state
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
        
    if "assistant_state" not in st.session_state:
        st.session_state["assistant_state"] = {
            "step": "WELCOME",
            "data": {
                "reported_by": "Anonymous",
                "description": "",
                "location": "",
                "people_affected": 0,
                "immediate_danger": "No",
                "additional_details": ""
            }
        }
        
    if "chat_session_id" not in st.session_state:
        st.session_state["chat_session_id"] = assistant.create_session()
        
    # Trigger first welcome message if empty
    if not st.session_state["chat_messages"]:
        welcome_result = assistant.send_message(
            st.session_state["chat_session_id"],
            "hello",
            st.session_state["assistant_state"]
        )
        st.session_state["assistant_state"] = welcome_result.get("state_context")
        st.session_state["chat_messages"].append({
            "role": "assistant",
            "text": welcome_result.get("response")
        })

    # Render Chat History Container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state["chat_messages"]:
        bubble_class = "chat-bubble-assistant" if msg["role"] == "assistant" else "chat-bubble-user"
        st.markdown(
            f"""
            <div style="display: flex; width: 100%;">
                <div class="chat-bubble {bubble_class}">
                    {msg['text'].replace('\n', '<br/>')}
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check if conversation is completed
    is_completed = st.session_state["assistant_state"].get("step") == "ASK_SUBMIT"
    
    if is_completed:
        # Prompt for submit/reset buttons
        st.markdown(
            """
            <div style="background-color: rgba(96, 165, 250, 0.1); border: 1px solid rgba(96, 165, 250, 0.3); border-radius: 8px; padding: 16px; text-align: center; margin-bottom: 20px;">
                <span style="color: #60a5fa; font-weight: bold; font-size: 15px;">Conversation Intake Completed</span>
                <p style="color: #93c5fd; font-size: 13px; margin: 4px 0 12px 0;">All details have been gathered. Submit to send data to the IBM watsonx.ai reasoning engine.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Route to watsonx.ai", use_container_width=True, type="primary"):
                # Save incident to database (un-triage status: "Reported" - wait for Watsonx execution)
                collected_data = st.session_state["assistant_state"]["data"]
                
                # Pre-populated defaults prior to watsonx classification
                collected_data["status"] = "Reported"
                collected_data["assigned_department"] = "Unassigned"
                collected_data["incident_type"] = "Pending Analysis"
                collected_data["severity"] = "Moderate"
                collected_data["priority"] = "P3"
                collected_data["risk_score"] = 0
                collected_data["confidence"] = 0
                collected_data["estimated_response"] = "Unscheduled"
                collected_data["immediate_actions"] = ""
                collected_data["root_causes"] = "Unknown"
                collected_data["escalate"] = "False"
                collected_data["escalate_reason"] = ""
                collected_data["executive_summary"] = "Awaiting decision triage..."
                collected_data["assigned_to"] = "Unassigned"
                
                # Save & Route
                new_id = create_incident(collected_data)
                
                # Reset chat state
                assistant.delete_session(st.session_state["chat_session_id"])
                del st.session_state["chat_messages"]
                del st.session_state["assistant_state"]
                del st.session_state["chat_session_id"]
                
                st.session_state["selected_incident_id"] = new_id
                st.session_state["active_page"] = "AI Response Center"
                st.success(f"Incident {new_id} created successfully!")
                st.rerun()
                
        with col2:
            if st.button("🗑 Reset Form", use_container_width=True):
                assistant.delete_session(st.session_state["chat_session_id"])
                del st.session_state["chat_messages"]
                del st.session_state["assistant_state"]
                del st.session_state["chat_session_id"]
                st.rerun()
    else:
        # Chat input bar
        user_input = st.chat_input("Provide response here...")
        if user_input:
            # Append User message
            st.session_state["chat_messages"].append({
                "role": "user",
                "text": user_input
            })
            
            # Send message to Assistant
            result = assistant.send_message(
                st.session_state["chat_session_id"],
                user_input,
                st.session_state["assistant_state"]
            )
            
            # Save state and response
            st.session_state["assistant_state"] = result.get("state_context")
            st.session_state["chat_messages"].append({
                "role": "assistant",
                "text": result.get("response")
            })
            
            st.rerun()
            
    # Quick reporting shortcut for evaluations
    st.write("")
    st.write("")
    with st.expander("⚡ Evaluation Shortcuts (One-Click Pre-fills)"):
        st.markdown("<p style='font-size: 12px; color: #94a3b8;'>Select one of the scenarios below to quickly populate the chat state and test the AI Decision engine directly.</p>", unsafe_allow_html=True)
        
        col_sc1, col_sc2, col_sc3 = st.columns(3)
        with col_sc1:
            if st.button("🔥 Critical Server Room Fire", use_container_width=True):
                st.session_state["assistant_state"] = {
                    "step": "ASK_SUBMIT",
                    "data": {
                        "reported_by": "System Administrator",
                        "description": "Smoke detector triggered. Thick black smoke rising from UPS racks in server room B1.",
                        "location": "Building B, Server Vault 03",
                        "people_affected": 2,
                        "immediate_danger": "Yes",
                        "additional_details": "Sprinkler system hasn't activated yet. Power is running."
                    }
                }
                st.session_state["chat_messages"] = [
                    {"role": "assistant", "text": "Shortcut Selected: Server Room Fire."},
                    {"role": "assistant", "text": "Details loaded. Ready to route. Click 'Route to watsonx.ai' below."}
                ]
                st.rerun()
                
        with col_sc2:
            if st.button("💻 Ransomware Network Locked", use_container_width=True):
                st.session_state["assistant_state"] = {
                    "step": "ASK_SUBMIT",
                    "data": {
                        "reported_by": "Finance Clerk Jane",
                        "description": "Red warning ransom note appeared on all terminals, locking database access.",
                        "location": "Finance Wing, Building A, 2nd Floor",
                        "people_affected": 18,
                        "immediate_danger": "No",
                        "additional_details": "Active directory looks blocked. Network drives show strange extensions."
                    }
                }
                st.session_state["chat_messages"] = [
                    {"role": "assistant", "text": "Shortcut Selected: Ransomware Breach."},
                    {"role": "assistant", "text": "Details loaded. Ready to route. Click 'Route to watsonx.ai' below."}
                ]
                st.rerun()
                
        with col_sc3:
            if st.button("🧪 Chemical Acid Spill", use_container_width=True):
                st.session_state["assistant_state"] = {
                    "step": "ASK_SUBMIT",
                    "data": {
                        "reported_by": "Lab Manager Dave",
                        "description": "Hydrofluoric acid glass jar dropped. Approximately 500ml of hazardous acid pooled on lab benches.",
                        "location": "Science Hall, Chemistry Room 210",
                        "people_affected": 4,
                        "immediate_danger": "Yes",
                        "additional_details": "Fumes spreading. Ventilation shut down to avoid corridor exposure."
                    }
                }
                st.session_state["chat_messages"] = [
                    {"role": "assistant", "text": "Shortcut Selected: Chemical Leak."},
                    {"role": "assistant", "text": "Details loaded. Ready to route. Click 'Route to watsonx.ai' below."}
                ]
                st.rerun()
