import config
import uuid
import json

try:
    from ibm_watson import AssistantV2
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    HAS_WATSON_SDK = True
except ImportError:
    HAS_WATSON_SDK = False

class AssistantService:
    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
        self.client = None
        self.assistant_id = config.WATSON_ASSISTANT_ID
        
        # If not simulating, attempt to initialize the Watson SDK
        if not self.simulation_mode:
            if not HAS_WATSON_SDK:
                print("ibm-watson SDK not installed. Defaulting to simulation mode.")
                self.simulation_mode = True
            else:
                try:
                    authenticator = IAMAuthenticator(config.WATSON_ASSISTANT_APIKEY)
                    self.client = AssistantV2(
                        version='2021-11-27',
                        authenticator=authenticator
                    )
                    self.client.set_service_url(config.WATSON_ASSISTANT_URL)
                except Exception as e:
                    print(f"Failed to initialize live Watson Assistant client, defaulting to simulation. Error: {e}")
                    self.simulation_mode = True

    def create_session(self):
        """
        Creates a new session. In simulation mode, returns a random UUID.
        """
        if self.simulation_mode or not self.client:
            return f"sim-{uuid.uuid4()}"
        
        try:
            response = self.client.create_session(
                assistant_id=self.assistant_id
            ).get_result()
            return response.get("session_id")
        except Exception as e:
            print(f"Error creating live Watson Assistant session: {e}. Falling back to simulation.")
            self.simulation_mode = True
            return f"sim-{uuid.uuid4()}"

    def delete_session(self, session_id):
        """
        Deletes a session.
        """
        if self.simulation_mode or not self.client or session_id.startswith("sim-"):
            return True
            
        try:
            self.client.delete_session(
                assistant_id=self.assistant_id,
                session_id=session_id
            )
            return True
        except Exception as e:
            print(f"Error deleting Watson session: {e}")
            return False

    def send_message(self, session_id, text, state_context=None):
        """
        Sends a message to the assistant.
        state_context: a dict representing the user's questionnaire state in Simulation Mode.
        """
        if self.simulation_mode or not self.client or session_id.startswith("sim-"):
            return self._handle_simulation(text, state_context)
            
        try:
            response = self.client.message(
                assistant_id=self.assistant_id,
                session_id=session_id,
                input={
                    'message_type': 'text',
                    'text': text
                }
            ).get_result()
            
            # Parse responses
            messages = []
            generic = response.get("output", {}).get("generic", [])
            for item in generic:
                if item.get("response_type") == "text":
                    messages.append(item.get("text"))
                    
            if not messages:
                messages.append("I received your input. How else can I assist with this incident?")
                
            return {
                "response": "\n\n".join(messages),
                "is_complete": False, # Live flows are managed in Watson Dialog
                "collected_data": {}
            }
        except Exception as e:
            print(f"Error sending message to live Watson Assistant: {e}. Falling back to simulation.")
            return self._handle_simulation(text, state_context)

    def _handle_simulation(self, text, state_context):
        """
        Simulates the Watson Assistant conversation flow for gathering incident reports.
        Conversation Flow:
        Start -> Welcome -> Describe -> Location -> People -> Danger -> Details -> Summary
        """
        if state_context is None:
            state_context = {
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

        step = state_context.get("step", "WELCOME")
        data = state_context.get("data", {})
        
        response_text = ""
        is_complete = False
        
        # Clean text input
        text_clean = text.strip()
        
        if step == "WELCOME":
            response_text = "Welcome to Crisis360 AI emergency reporting assistant. To help me triage this incident, please describe **what happened** in detail."
            state_context["step"] = "ASK_DESCRIPTION"
            
        elif step == "ASK_DESCRIPTION":
            if len(text_clean) < 5:
                response_text = "Please provide a valid description of what happened so we can correctly classify this crisis."
            else:
                data["description"] = text_clean
                response_text = "Thank you. **Where is this incident located?** Please specify the building, floor, room, or general area."
                state_context["step"] = "ASK_LOCATION"
                
        elif step == "ASK_LOCATION":
            if len(text_clean) < 3:
                response_text = "Please specify a location so emergency teams can be dispatched (e.g. Building B, Chemistry Lab)."
            else:
                data["location"] = text_clean
                response_text = "Got it. **How many people are affected or injured?** (Enter a number, or 0 if none)"
                state_context["step"] = "ASK_PEOPLE"
                
        elif step == "ASK_PEOPLE":
            # Attempt to parse number
            try:
                # Find digits in text
                digits = "".join([c for c in text_clean if c.isdigit()])
                if digits:
                    people = int(digits)
                else:
                    people = 0
                data["people_affected"] = people
                response_text = "Is there **immediate danger** or an active threat to life/property? (Yes / No)"
                state_context["step"] = "ASK_DANGER"
            except Exception:
                response_text = "Please enter a number for people affected (e.g., 0, 5, 12)."
                
        elif step == "ASK_DANGER":
            clean_ans = text_clean.lower()
            if "yes" in clean_ans or "y" == clean_ans:
                data["immediate_danger"] = "Yes"
            else:
                data["immediate_danger"] = "No"
            response_text = "Are there any **additional details** or immediate hazard flags (e.g. smoke, wires exposed, system downtime) you want to include? (Or type 'None')"
            state_context["step"] = "ASK_DETAILS"
            
        elif step == "ASK_DETAILS":
            if text_clean.lower() != "none" and text_clean.lower() != "no":
                data["additional_details"] = text_clean
            else:
                data["additional_details"] = "No additional details provided."
                
            response_text = (
                "🚨 **Incident report structured successfully!**\n\n"
                f"• **Description:** {data['description']}\n"
                f"• **Location:** {data['location']}\n"
                f"• **People Affected:** {data['people_affected']}\n"
                f"• **Immediate Danger:** {data['immediate_danger']}\n"
                f"• **Details:** {data['additional_details']}\n\n"
                "I am ready to submit this report to **IBM watsonx.ai Decision Engine** for triage. "
                "Type **'Submit'** to process or **'Reset'** to start over."
            )
            state_context["step"] = "ASK_SUBMIT"
            
        elif step == "ASK_SUBMIT":
            if "submit" in text_clean.lower() or "yes" in text_clean.lower():
                response_text = "Processing... Incident has been successfully logged. Routing to AI Response Center."
                is_complete = True
            elif "reset" in text_clean.lower():
                response_text = "Resetting conversational flow. Please describe **what happened**."
                state_context["step"] = "ASK_DESCRIPTION"
                state_context["data"] = {
                    "reported_by": "Anonymous",
                    "description": "",
                    "location": "",
                    "people_affected": 0,
                    "immediate_danger": "No",
                    "additional_details": ""
                }
            else:
                response_text = "Please confirm by typing **'Submit'** to send this report to Watsonx, or **'Reset'** to clear the form."
                
        state_context["data"] = data
        return {
            "response": response_text,
            "is_complete": is_complete,
            "collected_data": data,
            "state_context": state_context
        }
