import json
import config
from pathlib import Path

# Try importing IBM Watsonx SDK (wrapped to prevent crash if not installed/importable)
try:
    from ibm_watsonx_ai.foundation_models import Model
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    HAS_WATSONX_SDK = True
except ImportError:
    HAS_WATSONX_SDK = False

class WatsonxService:
    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
        self.project_id = config.WATSONX_PROJECT_ID
        self.model_id = config.WATSONX_MODEL
        self.client = None
        self.prompt_template = ""
        
        # Load prompt template
        self._load_prompt_template()
        
        # Initialize Watsonx SDK if not simulating
        if not self.simulation_mode and HAS_WATSONX_SDK:
            try:
                credentials = {
                    "url": config.WATSONX_URL,
                    "apikey": config.WATSONX_APIKEY
                }
                
                # Parameters for Granite model
                parameters = {
                    "decoding_method": "greedy",
                    "max_new_tokens": 1024,
                    "min_new_tokens": 1,
                    "temperature": 0.0,
                    "repetition_penalty": 1.0
                }
                
                self.client = Model(
                    model_id=self.model_id,
                    params=parameters,
                    credentials=credentials,
                    project_id=self.project_id
                )
            except Exception as e:
                print(f"Failed to initialize live watsonx.ai client, falling back to Simulation. Error: {e}")
                self.simulation_mode = True

    def _load_prompt_template(self):
        """Loads prompt from crisis_prompt.txt"""
        try:
            path = Path(config.PROMPTS_DIR) / "crisis_prompt.txt"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    self.prompt_template = f.read()
            else:
                self.prompt_template = "Analyze the incident: {description}. Return JSON."
        except Exception as e:
            print(f"Error loading prompt template: {e}")
            self.prompt_template = "Analyze the incident: {description}. Return JSON."

    def analyze_incident(self, description, location, people_affected, immediate_danger, additional_details):
        """
        Sends the incident details to watsonx.ai (Granite) or triggers Simulation Mode.
        Returns a dictionary containing the structured incident analysis.
        """
        if self.simulation_mode or not self.client:
            return self._run_simulation(description, location, people_affected, immediate_danger, additional_details)
            
        try:
            # Format prompt with parameters
            formatted_prompt = self.prompt_template.format(
                description=description,
                location=location,
                people_affected=people_affected,
                immediate_danger=immediate_danger,
                additional_details=additional_details
            )
            
            # Call Granite model
            response = self.client.generate_text(prompt=formatted_prompt)
            
            # Clean response text to extract JSON
            clean_response = response.strip()
            # If the model wrapped response in ```json ... ```, strip it
            if clean_response.startswith("```"):
                lines = clean_response.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                clean_response = "\n".join(lines).strip()
                
            result_json = json.loads(clean_response)
            return result_json
        except Exception as e:
            print(f"watsonx.ai API call failed: {e}. Falling back to simulation analysis.")
            return self._run_simulation(description, location, people_affected, immediate_danger, additional_details)

    def _run_simulation(self, description, location, people_affected, immediate_danger, additional_details):
        """
        Generates structured JSON analysis using static rules to simulate watsonx.ai.
        """
        desc_l = description.lower() + " " + additional_details.lower()
        
        # 1. Classification & Department
        if any(w in desc_l for w in ["fire", "smoke", "burn", "flame", "spark", "explosion"]):
            incident_type = "Fire Hazard"
            recommended_team = "Emergency Response Team"
            est_response = "5 minutes"
            actions = [
                "Evacuate nearby personnel and trigger the building fire alarm.",
                "Isolate or cut off the electrical breaker if safe to do so.",
                "Call the municipal fire department immediately.",
                "Evacuate to the designated assembly point."
            ]
            root_causes = [
                "Electrical short circuit or equipment overload",
                "Thermal failure of batteries or power converters",
                "Combustible materials stored near heat sources"
            ]
            base_risk = 55
        elif any(w in desc_l for w in ["hack", "ransomware", "virus", "phishing", "malware", "cyber", "breach", "server locked", "leak"]):
            incident_type = "Cybersecurity Breach"
            recommended_team = "Cybersecurity Operations"
            est_response = "15 minutes"
            actions = [
                "Disconnect affected server/computer from local network switch immediately.",
                "Notify IT Security Helpdesk and do not pay any ransoms.",
                "Capture screenshots of messages and preserve logs if possible.",
                "Initiate emergency endpoint lockdown procedures."
            ]
            root_causes = [
                "Credential compromise via sophisticated phishing link",
                "Exploitation of unpatched software vulnerability",
                "Unauthorized lateral movement from third-party network"
            ]
            base_risk = 50
        elif any(w in desc_l for w in ["spill", "chemical", "leak", "acid", "toxic", "gas", "fumes", "hazmat"]):
            incident_type = "Chemical Hazard"
            recommended_team = "Environmental Health & Safety"
            est_response = "10 minutes"
            actions = [
                "Evacuate chemical lab and seal the ventilation doors.",
                "Equip responding team with proper gas masks and chemical suits.",
                "Apply appropriate neutralizing agent or absorbents.",
                "Ventilate the area using dedicated fume extractors."
            ]
            root_causes = [
                "Cracked container housing or damaged seals",
                "Incorrect shelf storage or workspace handling",
                "Failure of chemical containment safety valve"
            ]
            base_risk = 45
        elif any(w in desc_l for w in ["slip", "fall", "injury", "heart", "pain", "medical", "blood", "unconscious", "accident", "broken"]):
            incident_type = "Medical Emergency"
            recommended_team = "Medical Response Unit"
            est_response = "8 minutes"
            actions = [
                "Do not move the victim unless they are in immediate hazard.",
                "Apply first aid/CPR if certified and dispatch nearby responder.",
                "Call emergency medical services (911) if injuries are major.",
                "Keep the patient calm and warm until paramedics arrive."
            ]
            root_causes = [
                "Physical slip hazard or wet walking surface",
                "Pre-existing acute health condition",
                "Lack of warning signage or anti-slip stair treads"
            ]
            base_risk = 40
        elif any(w in desc_l for w in ["threat", "weapon", "active shooter", "intruder", "fight", "assault", "robbery"]):
            incident_type = "Active Threat"
            recommended_team = "Security Operations"
            est_response = "3 minutes"
            actions = [
                "Initiate Run-Hide-Fight protocol and lock corridor doors.",
                "Call local law enforcement immediately (911).",
                "Mute all mobile phones and remain silent.",
                "Alert campus or facility administration to broadcast lockdown."
            ]
            root_causes = [
                "Unauthorized building entry via tailgating",
                "Physical altercation escalation",
                "Security perimeter control breach"
            ]
            base_risk = 70
        elif any(w in desc_l for w in ["power", "outage", "elevator", "hvac", "ac", "water leak", "pipe", "roof", "light", "fixture"]):
            incident_type = "Infrastructure Failure"
            recommended_team = "Facilities Management"
            est_response = "30 minutes"
            actions = [
                "Ground affected elevator units and display clear service notices.",
                "Isolate local water valves to stop flooding.",
                "Notify facility technicians to check grid controllers.",
                "Deploy backup generators if crucial server spaces are impacted."
            ]
            root_causes = [
                "Corrosion or failure of main building piping line",
                "Overloading of primary electrical breaker panels",
                "Degradation of aging elevator mechanical cables"
            ]
            base_risk = 30
        else:
            incident_type = "Safety Hazard"
            recommended_team = "Facilities Management"
            est_response = "45 minutes"
            actions = [
                "Secure the hazard zone using barricades or cones.",
                "Log standard service ticket with details and photographs.",
                "Clear path around the hazard area to prevent incidents."
            ]
            root_causes = [
                "Lack of routine maintenance checks",
                "Environmental wear and tear"
            ]
            base_risk = 20

        # 2. Risk Score calculation
        danger_factor = 40 if immediate_danger.lower() == "yes" else 0
        people = int(people_affected)
        people_factor = 25 if people >= 15 else (15 if people > 0 else 0)
        
        # Calculate calculated risk score (0-100)
        risk_score = min(100, base_risk + danger_factor + people_factor)
        
        # Severity mapping
        if risk_score >= 75:
            severity = "Critical"
            priority = "P1"
        elif risk_score >= 50:
            severity = "Major"
            priority = "P2"
        elif risk_score >= 25:
            severity = "Moderate"
            priority = "P3"
        else:
            severity = "Minor"
            priority = "P4"

        # 3. Escalation Prediction
        escalate = risk_score > 70 or people >= 15 or immediate_danger.lower() == "yes"
        escalate_reason = ""
        if escalate:
            reasons = []
            if immediate_danger.lower() == "yes":
                reasons.append("immediate threat to life/property is present")
            if people >= 15:
                reasons.append(f"high headcount affected ({people} individuals)")
            if risk_score > 70:
                reasons.append(f"extreme hazard risk score calculated ({risk_score}/100)")
            escalate_reason = f"Automated escalation triggered due to: {', '.join(reasons)}."

        # 4. Confidence Score
        confidence = 94 if len(description) > 50 else 82

        # 5. Executive Summary sections
        summary = f"An incident classified as {incident_type} occurred at {location}. The reporter indicated: '{description}'."
        
        if incident_type == "Fire Hazard":
            impact = "High potential for structural damage, data center loss, and smoke inhalation injuries."
            rec_action = "Deploy building evacuation marshals, check fire suppression, notify local authorities."
            risk_lvl = "Critical. Fire events require immediate containment to prevent catastrophic building loss."
            steps = "Inspect server room cooling systems, replace outdated batteries, execute fire safety drills quarterly."
        elif incident_type == "Cybersecurity Breach":
            impact = "Operational interruption to finance/administrative databases, potential compliance fines, data theft risks."
            rec_action = "Isolate VLAN networks, reset corporate credentials, initiate cybersecurity forensic analysis."
            risk_lvl = "High. Compromised administrator environments present active propagation threats."
            steps = "Implement Multi-Factor Authentication (MFA), patch active directory nodes, run staff phishing awareness campaigns."
        elif incident_type == "Chemical Hazard":
            impact = "Hazardous chemical inhalation, building evacuation downtime, chemical burn hazards."
            rec_action = "Seal laboratory vents, deploy spill absorption kits, alert local HAZMAT."
            risk_lvl = "High. Toxic chemical concentrations can lead to immediate respiratory issues."
            steps = "Introduce secondary containment bins, install air quality alert sensors, retrain lab staff on spill procedures."
        elif incident_type == "Medical Emergency":
            impact = "Risk of severe physical injury, organizational liability, workplace safety audit review."
            rec_action = "Coordinate first responder access, secure transport path, notify next of kin."
            risk_lvl = "Medium. Medical emergencies require immediate first responder support to prevent complications."
            steps = "Install safety railings, place wet floors signage promptly during rains, offer CPR training to reception staff."
        elif incident_type == "Active Threat":
            impact = "Extreme threat to physical safety, legal liability, high brand damage, long-term psychological impacts."
            rec_action = "Broadcast building lockdown message, initiate active shooter protocol, secure all entry/exit terminals."
            risk_lvl = "Critical. Active physical threats require direct coordination with municipal police forces."
            steps = "Upgrade keycard turnstiles, restrict tailgating at entrances, install CCTV surveillance arrays."
        else:
            impact = "Minor operational disruption, local utility outages, delays in administrative processes."
            rec_action = "Notify technicians, assign work repair ticket, block access around affected facility."
            risk_lvl = "Low to Medium. Non-hazardous facility events are managed through routine repairs."
            steps = "Audit facility equipment lifecycle, set up preventative maintenance schedules, replace legacy valves/relays."

        executive_summary = {
            "summary": summary,
            "business_impact": impact,
            "recommended_actions": rec_action,
            "risk_level": risk_lvl,
            "next_steps": steps
        }

        # Structure complete JSON output matching prompt requirements
        return {
            "incident_type": incident_type,
            "severity": severity,
            "priority": priority,
            "confidence": confidence,
            "recommended_team": recommended_team,
            "estimated_response": est_response,
            "risk_score": risk_score,
            "immediate_actions": actions,
            "root_causes": root_causes,
            "escalation": {
                "escalate": escalate,
                "reason": escalate_reason
            },
            "executive_summary": executive_summary
        }
