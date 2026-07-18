# Crisis360 AI
### AI-Powered Incident Response & Crisis Management Platform
**Detect. Assess. Respond. Resolve.**

Crisis360 AI is an enterprise-grade emergency decision platform. It integrates **IBM Watson Assistant** and **IBM watsonx.ai (Granite-3-8b-instruct)** to automate incident reporting, analyze risk profiles, assign response priorities, predict root causes, and compile consulting-grade summary reports.

---

## 🤖 Project Classification: Langflow Node Workflow & IBM Bob Development

Crisis360 AI is structured as an **Agentic AI Langflow Project** implemented via Python Streamlit, leveraging watsonx.ai and Watson Assistant. 

The application logic mirrors a **Langflow node-link canvas architecture** composed of the following interconnected nodes:
1.  **Chat Input Node:** Gathers user incident reports via natural language.
2.  **IBM Watson Assistant Node:** Orchestrates dialogue slots (Description, Location, Headcount, Danger).
3.  **watsonx.ai Granite Node:** Evaluates severity, priorities, risk indexes, and root causes.
4.  **Safety Action Generator Node:** Generates incident-specific containment guidelines.
5.  **CSV Database Node:** Saves and loads transaction logs from `data/incidents.csv`.
6.  **Chat Output Node / Admin Cockpit:** Visualizes metrics, timelines, and downloadable PDF files.

*The codebase, Streamlit session routing, and API exception handlers were developed and optimized using the **IBM Bob developer assistant** (as certified in our IBM SkillsBuild credentials).*

---

## 💡 System Architecture: "Why Watson Assistant + watsonx.ai?"

Crisis360 AI demonstrates a clear architectural separation between conversational orchestration and cognitive reasoning.

```
                    SYSTEM ARCHITECTURE

                  ┌──────────────────────┐
                  │      USER            │
                  └──────────┬───────────┘
                             │
                             ▼
                 IBM Watson Assistant
                 (Intake & Dialogue Flow)
                             │
                             ▼
              Incident Information Collection
              (Desc, Location, People, Danger)
                             │
                             ▼
                 IBM watsonx.ai (Granite)
                 (Cognitive Reasoning Engine)
                             │
       ┌────────────┬─────────────┬────────────┐
       ▼            ▼             ▼
 Classification  Severity AI   Action Generator
  & Department   Risk Scoring   Root Cause Predict
       │            │             │
       └────────────┴─────────────┘
                    │
                    ▼
            Incident Processing Engine
            (Timeline State Machine & CSV)
                    │
      ┌─────────────┴─────────────┐
      ▼                           ▼
 Plotly Analytics           Admin Monitoring Panel
 (8 Analytical Charts)      (Action Center & PDF)
```

1. **IBM Watson Assistant (Dialogue Flow)**: Mandated with conversational orchestration. It acts as the intake clerk, walking the reporter step-by-step to gather critical, validated parameters: incident description, location details, headcount affected, and immediate life danger flags. This guarantees clean input structure.
2. **IBM watsonx.ai (Granite Model)**: Serves as the cognitive triage engine. It processes the raw variables, calculates an objective Risk Score (0-100), predicts underlying root causes, decides if executive escalation is required, and drafts professional executive reports.

---

## 🛠️ Features (MVP)

1. **Conversational AI Intake**: Multi-step interactive dialogue modeled after Watson Assistant. Features evaluation shortcuts to load pre-configured emergency scenarios instantly.
2. **watsonx.ai Granite Decision Engine**:
   - **Triage Classification**: Routes reports into 8 types (Fire, Cybersecurity, Chemical, Medical, active threat, etc.).
   - **Incident Risk Score (0-100)**: Displays glowing gauges and indicator progress bars.
   - **Executive Escalation Banners**: Highlights cases with high risk scores or active threats.
   - **Predicted Root Causes**: Suggests underlying operational triggers (e.g. thermal battery runaways for fires).
   - **Safety Checklist**: Lists immediate response actions for responders.
3. **8-Chart Plotly Analytics Dashboard**:
   - Category Distribution (Donut Chart)
   - Severity Level Breakdown (Bar Chart)
   - Daily Reporting Trend (Line Chart)
   - Department Involvement (Horizontal Bar Chart)
   - Category vs Severity Heatmap (Imshow Grid)
   - Response Priority Breakdown (Bar Chart)
   - Risk Score Distribution (Box Plot)
   - Average Resolution Time by Team (Bar Chart)
4. **Admin Control Center**:
   - Filter, sort, and search logged incidents.
   - Re-route departments, assign responders, and transition statuses along the **Timeline State Machine** (`Reported` ➔ `AI Classified` ➔ `Assigned` ➔ `In Progress` ➔ `Resolved`).
   - Export official, digitally signed PDF incident reports.

---

## 📊 Evaluation Criteria Matching

| Criterion | How Crisis360 AI Meets It |
| :--- | :--- |
| **Usage of IBM Cloud-Platform** | Directly uses `ibm-watson` and `ibm-watsonx-ai` SDKs with Granite models. Features **Simulation Mode** (enabled by default) for immediate evaluation without api keys. |
| **Scalability & Innovation** | High separation between conversational intake and reasoning. Modular design handles multiple facilities. Real-time Plotly charts scale with logged data volumes. |
| **Contribution & Social Benefit** | Accelerates emergency response dispatch times. Standardized triage processes prevent human dispatching mistakes, directly improving public and workplace safety. |
| **Readiness for Deployment** | Written in Streamlit, ready to host on IBM Cloud Code Engine or Community. Automatically creates and populates CSV databases. Generates standardized, downloadable PDF reports. |
| **Commercial Viability** | Highly viable SaaS offering for corporate offices, hospitals, universities, manufacturing sites, and public institutions managing compliance and daily hazards. |
| **Future Scope** | Integration with IoT temperature and humidity sensors for automatic alert generation, CCTV camera feed analysis via visual Watson models, and enterprise IBM Db2 databases. |

---

## 🚀 Installation & Local Execution

### Prerequisites
- Python 3.8 to 3.11 installed.

### Setup
1. Clone or copy the project folder to your system:
   ```bash
   cd C:\Users\SVCS\Desktop\ibmproject
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the validation test suite to check backend services:
   ```bash
   python verify_backend.py
   ```

4. Run the Streamlit web application:
   ```bash
   streamlit run app.py
   ```

5. Open your browser and navigate to the local address shown (typically `http://localhost:8501`).

---

## ⚙️ IBM Cloud Live Configuration

To switch from **Simulation Mode** to **Live IBM Cloud API connectivity**:
1. Open the **Settings** tab in the sidebar of the running web application.
2. Toggle "Activate Simulation Mode" off.
3. Input your:
   - watsonx.ai IAM API Key
   - watsonx.ai Project ID
   - watsonx.ai Endpoint URL (e.g. `https://us-south.ml.cloud.ibm.com`)
   - IBM Watson Assistant API Key
   - Watson Assistant ID
   - Watson Assistant URL (e.g. `https://api.us-south.assistant.watson.cloud.ibm.com`)
4. Click **Save Credentials & Reload Configurations**. This will save configurations to a local `.env` file and initialize the active SDK connections.
