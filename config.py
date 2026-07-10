import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"
ASSETS_DIR = BASE_DIR / "assets"
UTILS_DIR = BASE_DIR / "utils"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
PROMPTS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
UTILS_DIR.mkdir(exist_ok=True)

# Load environment variables
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()

# IBM Watsonx.ai Configuration
WATSONX_APIKEY = os.getenv("IBM_WATSONX_APIKEY", "")
WATSONX_PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID", "")
WATSONX_URL = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_MODEL = os.getenv("IBM_WATSONX_MODEL", "ibm/granite-3-8b-instruct")

# IBM Watson Assistant Configuration
WATSON_ASSISTANT_APIKEY = os.getenv("IBM_WATSON_ASSISTANT_APIKEY", "")
WATSON_ASSISTANT_URL = os.getenv("IBM_WATSON_ASSISTANT_URL", "https://api.us-south.assistant.watson.cloud.ibm.com")
WATSON_ASSISTANT_ID = os.getenv("IBM_WATSON_ASSISTANT_ID", "")

# Determine if Simulation Mode is active
# Simulation mode is ON if any core credentials are empty
IS_SIMULATION_DEFAULT = not (bool(WATSONX_APIKEY) and bool(WATSONX_PROJECT_ID) and bool(WATSON_ASSISTANT_APIKEY) and bool(WATSON_ASSISTANT_ID))

def is_simulation_mode(session_state=None):
    """
    Checks if simulation mode should be active. 
    Streamlit session state can override this dynamically.
    """
    if session_state and "simulation_mode" in session_state:
        return session_state["simulation_mode"]
    return IS_SIMULATION_DEFAULT

def save_env_variables(variables: dict):
    """
    Saves environment variables to .env file and reloads dotenv.
    """
    lines = []
    for key, value in variables.items():
        lines.append(f"{key}={value}\n")
    
    with open(ENV_FILE, "w") as f:
        f.writelines(lines)
    
    # Reload environment
    load_dotenv(ENV_FILE, override=True)
    
    # Update global variables in this module
    global WATSONX_APIKEY, WATSONX_PROJECT_ID, WATSONX_URL, WATSONX_MODEL
    global WATSON_ASSISTANT_APIKEY, WATSON_ASSISTANT_URL, WATSON_ASSISTANT_ID, IS_SIMULATION_DEFAULT
    
    WATSONX_APIKEY = variables.get("IBM_WATSONX_APIKEY", "")
    WATSONX_PROJECT_ID = variables.get("IBM_WATSONX_PROJECT_ID", "")
    WATSONX_URL = variables.get("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    WATSONX_MODEL = variables.get("IBM_WATSONX_MODEL", "ibm/granite-3-8b-instruct")
    
    WATSON_ASSISTANT_APIKEY = variables.get("IBM_WATSON_ASSISTANT_APIKEY", "")
    WATSON_ASSISTANT_URL = variables.get("IBM_WATSON_ASSISTANT_URL", "https://api.us-south.assistant.watson.cloud.ibm.com")
    WATSON_ASSISTANT_ID = variables.get("IBM_WATSON_ASSISTANT_ID", "")
    
    IS_SIMULATION_DEFAULT = not (bool(WATSONX_APIKEY) and bool(WATSONX_PROJECT_ID) and bool(WATSON_ASSISTANT_APIKEY) and bool(WATSON_ASSISTANT_ID))
