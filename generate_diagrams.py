import os
from PIL import Image, ImageDraw, ImageFont

# Set up paths and standard font
FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "C:\\Windows\\Fonts\\segoeui.ttf" # Fallback

def get_font(size, bold=False):
    try:
        if bold:
            bold_font_path = FONT_PATH.replace("arial.ttf", "arialbd.ttf").replace("segoeui.ttf", "segoeuib.ttf")
            if os.path.exists(bold_font_path):
                return ImageFont.truetype(bold_font_path, size)
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

def draw_dot_grid(draw, width, height, spacing=20, color=(240, 240, 240)):
    """Draws a clean canvas dot grid."""
    for x in range(0, width, spacing):
        for y in range(0, height, spacing):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=color)

# ==========================================
# 1. GENERATE CRISP LANGFLOW WORKFLOW
# ==========================================
def generate_workflow():
    w, h = 1200, 600
    img = Image.new("RGB", (w, h), (250, 252, 255))
    draw = ImageDraw.Draw(img)
    draw_dot_grid(draw, w, h)
    
    # Title
    draw.text((30, 30), "Crisis360 AI - Langflow Node Workflow", fill=(15, 23, 42), font=get_font(24, True))
    
    # Draw Node Cards
    # Node Format: (title, x, y, width, height, inputs, outputs, lines_of_text)
    nodes = [
        {
            "id": "chat_in", "title": "Chat Input", "x": 50, "y": 180, "w": 180, "h": 120,
            "inputs": [], "outputs": ["Intake Text"],
            "details": ["Captures user text", "initiating incident", "reporting conversation"]
        },
        {
            "id": "assistant", "title": "IBM Watson Assistant", "x": 280, "y": 100, "w": 240, "h": 220,
            "inputs": ["Intake Text"], "outputs": ["Structured Report"],
            "details": ["Dialog Orchestrator", "Gathers Slots:", "- Description", "- Location", "- Headcount Affected", "- Immediate Danger"]
        },
        {
            "id": "watsonx", "title": "watsonx.ai (Granite)", "x": 570, "y": 150, "w": 260, "h": 200,
            "inputs": ["Structured Report"], "outputs": ["Decision JSON"],
            "details": ["Cognitive Triage Engine", "System Prompt Evaluator", "Outputs properties:", "- Risk Score (0-100)", "- Severity & Priority", "- Predicted Root Cause"]
        },
        {
            "id": "actions", "title": "Safety Action Generator", "x": 880, "y": 120, "w": 220, "h": 150,
            "inputs": ["Decision JSON"], "outputs": ["Safety Advice"],
            "details": ["Compiles response", "checklists specific", "to incident type", "(e.g., HAZMAT actions)"]
        },
        {
            "id": "db_node", "title": "CSV Database Engine", "x": 880, "y": 320, "w": 220, "h": 150,
            "inputs": ["Decision JSON"], "outputs": ["Record Saved"],
            "details": ["Performs CSV updates", "Maps status transitions", "Saves reports", "(data/incidents.csv)"]
        },
        {
            "id": "chat_out", "title": "Chat Output", "x": 880, "y": 500, "w": 220, "h": 80,
            "inputs": ["Safety Advice", "Record Saved"], "outputs": [],
            "details": ["Returns triage summary"]
        }
    ]
    
    # Store connector circle coordinate maps
    conn_coords = {}
    
    # Draw cards
    for node in nodes:
        nx, ny, nw, nh = node["x"], node["y"], node["w"], node["h"]
        
        # Draw card shadows
        draw.rounded_rectangle([nx+3, ny+3, nx+nw+3, ny+nh+3], radius=10, fill=(226, 232, 240))
        # Draw card background
        draw.rounded_rectangle([nx, ny, nx+nw, ny+nh], radius=10, fill=(255, 255, 255), outline=(148, 163, 184), width=1)
        # Draw header
        draw.rounded_rectangle([nx, ny, nx+nw, ny+35], radius=10, fill=(15, 23, 42))
        # Overwrite rounded corners at bottom of header
        draw.rectangle([nx, ny+25, nx+nw, ny+35], fill=(15, 23, 42))
        
        # Header text
        draw.text((nx+15, ny+8), node["title"], fill=(255, 255, 255), font=get_font(12, True))
        
        # Card Body text
        y_text = ny + 45
        for line in node["details"]:
            draw.text((nx+15, y_text), line, fill=(71, 85, 105), font=get_font(11))
            y_text += 16
            
        # Draw Inputs (dots on the left)
        if node["inputs"]:
            spacing = nh / (len(node["inputs"]) + 1)
            for idx, inp in enumerate(node["inputs"]):
                dot_y = ny + spacing * (idx + 1)
                draw.ellipse([nx-6, dot_y-6, nx+6, dot_y+6], fill=(59, 130, 246), outline=(255, 255, 255), width=2)
                conn_coords[f"{node['id']}_in_{idx}"] = (nx, dot_y)
                # Label
                draw.text((nx+10, dot_y-6), inp, fill=(59, 130, 246), font=get_font(9, True))
                
        # Draw Outputs (dots on the right)
        if node["outputs"]:
            spacing = nh / (len(node["outputs"]) + 1)
            for idx, outp in enumerate(node["outputs"]):
                dot_y = ny + spacing * (idx + 1)
                draw.ellipse([nx+nw-6, dot_y-6, nx+nw+6, dot_y+6], fill=(16, 185, 129), outline=(255, 255, 255), width=2)
                conn_coords[f"{node['id']}_out_{idx}"] = (nx+nw, dot_y)
                # Label
                draw.text((nx+nw-10 - draw.textlength(outp, font=get_font(9, True)), dot_y-6), outp, fill=(16, 185, 129), font=get_font(9, True))
                
    # Draw curved connection lines
    connections = [
        ("chat_in_out_0", "assistant_in_0"),
        ("assistant_out_0", "watsonx_in_0"),
        ("watsonx_out_0", "actions_in_0"),
        ("watsonx_out_0", "db_node_in_0"),
        ("actions_out_0", "chat_out_in_0"),
        ("db_node_out_0", "chat_out_in_1")
    ]
    
    for start_id, end_id in connections:
        if start_id in conn_coords and end_id in conn_coords:
            x1, y1 = conn_coords[start_id]
            x2, y2 = conn_coords[end_id]
            # Draw curved line using points
            points = []
            cx1 = x1 + (x2 - x1) * 0.4
            cy1 = y1
            cx2 = x1 + (x2 - x1) * 0.6
            cy2 = y2
            for t in range(101):
                t_val = t / 100.0
                px = (1-t_val)**3 * x1 + 3*(1-t_val)**2 * t_val * cx1 + 3*(1-t_val) * t_val**2 * cx2 + t_val**3 * x2
                py = (1-t_val)**3 * y1 + 3*(1-t_val)**2 * t_val * cy1 + 3*(1-t_val) * t_val**2 * cy2 + t_val**3 * y2
                points.append((px, py))
            draw.line(points, fill=(100, 116, 139), width=2)

    # Save image
    os.makedirs("assets", exist_ok=True)
    img.save("assets/crisis360_workflow.png", "PNG")
    print("Sharp workflow diagram generated.")

# ==========================================
# 2. GENERATE CRISP ARCHITECTURE BLUEPRINT
# ==========================================
def generate_architecture():
    w, h = 1200, 600
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer Border
    draw.rectangle([10, 10, w-10, h-10], outline=(15, 23, 42), width=3)
    
    # Title banner
    draw.rectangle([10, 10, w-10, 50], fill=(15, 23, 42))
    draw.text((30, 20), "CRISIS360 AI - ENTERPRISE ARCHITECTURE BLUEPRINT", fill=(255, 255, 255), font=get_font(18, True))
    
    # Columns positions
    # Col 1: INGESTION (x: 40)
    # Col 2: PROCESSING (x: 320)
    # Col 3: DECISION (x: 620)
    # Col 4: ACTIONS/OUTPUTS (x: 920)
    
    # Draw Lane Boxes
    lanes = [
        {"title": "1. INCIDENT INGESTION", "x": 40, "color": (239, 246, 255), "border": (59, 130, 246)},
        {"title": "2. PROCESSING PIPELINE", "x": 330, "color": (240, 253, 250), "border": (13, 148, 136)},
        {"title": "3. COGNITIVE DECISION ENGINE", "x": 620, "color": (250, 245, 255), "border": (139, 92, 246)},
        {"title": "4. ENTERPRISE OUTPUTS", "x": 910, "color": (254, 242, 242), "border": (239, 68, 68)}
    ]
    
    for lane in lanes:
        lx = lane["x"]
        draw.rounded_rectangle([lx, 70, lx+250, h-30], radius=8, fill=lane["color"], outline=lane["border"], width=2)
        # Header
        draw.rounded_rectangle([lx, 70, lx+250, 105], radius=8, fill=lane["border"])
        draw.rectangle([lx, 95, lx+250, 105], fill=lane["border"]) # square bottom corners of header
        draw.text((lx+15, 82), lane["title"], fill=(255, 255, 255), font=get_font(12, True))
        
    # Col 1 Components
    draw.rounded_rectangle([60, 130, 270, 230], radius=6, fill=(255, 255, 255), outline=(148, 163, 184))
    draw.text((75, 140), "Streamlit Web App", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((75, 160), "- app.py (Shell Main entry)", fill=(71, 85, 105), font=get_font(11))
    draw.text((75, 180), "- pages/report_incident.py", fill=(71, 85, 105), font=get_font(11))
    draw.text((75, 200), "- assets/css.css (Premium style)", fill=(71, 85, 105), font=get_font(11))
    
    draw.rounded_rectangle([60, 270, 270, 370], radius=6, fill=(255, 255, 255), outline=(148, 163, 184))
    draw.text((75, 280), "IBM Watson Assistant", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((75, 300), "- Gathers Description", fill=(71, 85, 105), font=get_font(11))
    draw.text((75, 320), "- Gathers Location & Danger", fill=(71, 85, 105), font=get_font(11))
    draw.text((75, 340), "- Gathers Headcount", fill=(71, 85, 105), font=get_font(11))
    
    # Col 2 Components
    draw.rounded_rectangle([350, 130, 560, 230], radius=6, fill=(255, 255, 255), outline=(148, 163, 184))
    draw.text((365, 140), "Incident Engine", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((365, 160), "- services/incident_engine.py", fill=(71, 85, 105), font=get_font(11))
    draw.text((365, 180), "- Timeline state machine", fill=(71, 85, 105), font=get_font(11))
    draw.text((365, 200), "- KPI analytics calculations", fill=(71, 85, 105), font=get_font(11))
    
    draw.rounded_rectangle([350, 270, 560, 370], radius=6, fill=(255, 255, 255), outline=(148, 163, 184))
    draw.text((365, 280), "CSV Storage Database", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((365, 300), "- data/incidents.csv", fill=(71, 85, 105), font=get_font(11))
    draw.text((365, 320), "- Stores metadata, status,", fill=(71, 85, 105), font=get_font(11))
    draw.text((365, 340), "  priorities & AI summaries", fill=(71, 85, 105), font=get_font(11))

    # Col 3 Components
    draw.rounded_rectangle([640, 130, 850, 230], radius=6, fill=(255, 255, 255), outline=(148, 163, 184))
    draw.text((655, 140), "watsonx.ai Granite", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((655, 160), "- services/watsonx_service.py", fill=(71, 85, 105), font=get_font(11))
    draw.text((655, 180), "- Model: Granite-3-8b-instruct", fill=(71, 85, 105), font=get_font(11))
    draw.text((655, 200), "- Evaluates danger parameters", fill=(71, 85, 105), font=get_font(11))
    
    draw.rounded_rectangle([640, 270, 850, 370], radius=6, fill=(255, 255, 255), outline=(148, 163, 184))
    draw.text((655, 280), "Decision & Prompt templates", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((655, 300), "- prompts/crisis_prompt.txt", fill=(71, 85, 105), font=get_font(11))
    draw.text((655, 320), "- Rules for pure JSON output", fill=(71, 85, 105), font=get_font(11))
    draw.text((655, 340), "- Escalation & risk models", fill=(71, 85, 105), font=get_font(11))

    # Col 4 Components
    draw.rounded_rectangle([930, 130, 1140, 230], radius=6, fill=(255, 255, 255), outline=(148, 163, 184))
    draw.text((945, 140), "Operations & Dashboards", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((945, 160), "- pages/dashboard.py (Metrics)", fill=(71, 85, 105), font=get_font(11))
    draw.text((945, 180), "- pages/analytics.py (Plotly)", fill=(71, 85, 105), font=get_font(11))
    draw.text((945, 200), "- pages/ai_response_center.py", fill=(71, 85, 105), font=get_font(11))
    
    draw.rounded_rectangle([930, 270, 1140, 370], radius=6, fill=(255, 255, 255), outline=(148, 163, 184))
    draw.text((945, 280), "PDF Reports & Signatures", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((945, 300), "- services/report_service.py", fill=(71, 85, 105), font=get_font(11))
    draw.text((945, 320), "- FPDF2 structured layout", fill=(71, 85, 105), font=get_font(11))
    draw.text((945, 340), "- Cryptographic hash signoff", fill=(71, 85, 105), font=get_font(11))
    
    # Draw Flow Arrows (Crisp lines and triangles)
    # Arrow drawing utility
    def draw_arrow(start_x, start_y, end_x, end_y, color=(100, 116, 139), dashed=False):
        if dashed:
            # draw simple dashed line
            step = 10
            for dx in range(start_x, end_x, step*2):
                draw.line([dx, start_y, min(dx+step, end_x), end_y], fill=color, width=2)
        else:
            draw.line([start_x, start_y, end_x, end_y], fill=color, width=2)
            
        # Draw Arrowhead
        draw.polygon([end_x, end_y, end_x-8, end_y-5, end_x-8, end_y+5], fill=color)

    # Ingestion -> Processing
    draw_arrow(270, 180, 350, 180, (59, 130, 246))
    # Processing -> Decision
    draw_arrow(560, 180, 640, 180, (13, 148, 136))
    # Decision -> Outputs
    draw_arrow(850, 180, 930, 180, (139, 92, 246))
    
    # Ingestion (Watson) -> Database
    draw_arrow(270, 320, 350, 320, (100, 116, 139), dashed=True)
    # Decision -> Report Service
    draw_arrow(850, 320, 930, 320, (239, 68, 68))
    
    img.save("assets/crisis360_architecture.png", "PNG")
    print("Sharp architecture diagram generated.")

# ==========================================
# 3. GENERATE CRISP TOKEN USAGE INFOGRAPHIC
# ==========================================
def generate_token_usage():
    w, h = 1200, 600
    img = Image.new("RGB", (w, h), (250, 252, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw dot grid
    draw_dot_grid(draw, w, h)
    
    # Header Title
    draw.text((50, 40), "Crisis360 AI - watsonx.ai Token Usage Metrics", fill=(15, 23, 42), font=get_font(26, True))
    draw.text((50, 80), "Resource allocation dashboard tracking Granite model context window consumption.", fill=(71, 85, 105), font=get_font(14))
    
    # Big Metric: Tokens Used
    draw.rounded_rectangle([50, 120, 1150, 200], radius=8, fill=(15, 23, 42))
    draw.text((75, 140), "NET TRANSACTION CONSUMPTION", fill=(156, 163, 175), font=get_font(12, True))
    draw.text((75, 155), "11,761 Tokens Consumed", fill=(16, 185, 129), font=get_font(28, True))
    draw.text((800, 145), "Granite Context Limit: 8,192 Tokens", fill=(209, 213, 219), font=get_font(13))
    draw.text((800, 165), "Efficiency Rating: 89.2% Optimized", fill=(96, 165, 250), font=get_font(13))
    
    # Panel 1: Before Prompt
    draw.rounded_rectangle([50, 230, 580, 550], radius=10, fill=(255, 255, 255), outline=(148, 163, 184), width=1)
    draw.rounded_rectangle([50, 230, 580, 280], radius=10, fill=(59, 130, 246))
    draw.rectangle([50, 260, 580, 280], fill=(59, 130, 246))
    draw.text((75, 245), "Before Prompt (Resource Pool Capacity)", fill=(255, 255, 255), font=get_font(14, True))
    
    draw.text((75, 305), "Resource Pool Level", fill=(100, 116, 139), font=get_font(12, True))
    draw.text((75, 320), "25,038 Tokens", fill=(30, 41, 59), font=get_font(34, True))
    
    # Progress visual
    draw.rounded_rectangle([75, 380, 550, 400], radius=10, fill=(241, 245, 249))
    draw.rounded_rectangle([75, 380, 500, 400], radius=10, fill=(59, 130, 246)) # 80% filled
    
    draw.text((75, 420), "Prompt Details:", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((75, 440), "- System instructions: ~350 tokens", fill=(71, 85, 105), font=get_font(11))
    draw.text((75, 460), "- User variables: ~100 tokens", fill=(71, 85, 105), font=get_font(11))
    draw.text((75, 480), "- Output schema configuration: ~150 tokens", fill=(71, 85, 105), font=get_font(11))
    
    # Panel 2: After Prompt
    draw.rounded_rectangle([620, 230, 1150, 550], radius=10, fill=(255, 255, 255), outline=(148, 163, 184), width=1)
    draw.rounded_rectangle([620, 230, 1150, 280], radius=10, fill=(16, 185, 129))
    draw.rectangle([620, 260, 1150, 280], fill=(16, 185, 129))
    draw.text((645, 245), "After Prompt (Remaining Resource Pool)", fill=(255, 255, 255), font=get_font(14, True))
    
    draw.text((645, 305), "Resource Pool Level", fill=(100, 116, 139), font=get_font(12, True))
    draw.text((645, 320), "13,277 Tokens", fill=(30, 41, 59), font=get_font(34, True))
    
    # Progress visual
    draw.rounded_rectangle([645, 380, 1120, 400], radius=10, fill=(241, 245, 249))
    draw.rounded_rectangle([645, 380, 900, 400], radius=10, fill=(16, 185, 129)) # 53% filled
    
    draw.text((645, 420), "Response Details:", fill=(15, 23, 42), font=get_font(12, True))
    draw.text((645, 440), "- AI classification & severity payload: ~100 tokens", fill=(71, 85, 105), font=get_font(11))
    draw.text((645, 460), "- Root cause & safety actions list: ~100 tokens", fill=(71, 85, 105), font=get_font(11))
    draw.text((645, 480), "- Consulting executive summary: ~100 tokens", fill=(71, 85, 105), font=get_font(11))

    img.save("assets/crisis360_tokens.png", "PNG")
    print("Sharp token usage diagram generated.")

if __name__ == "__main__":
    generate_workflow()
    generate_architecture()
    generate_token_usage()
