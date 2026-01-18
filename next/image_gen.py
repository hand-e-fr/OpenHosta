


from enum import Enum

class SlideLayoutType(Enum):
    CENTERED = "centered"
    LEFT = "left"
    RIGHT = "right"
    TWO_COLUMNS = "two_columns"
    TITLE = "title"
    TITLE_SUBTITLE = "title_subtitle"
    BLANK = "blank"

from dataclasses import dataclass

@dataclass
class ColorTheme:
    background: str
    text: str
    accent: str

from PIL import Image
from io import BytesIO

from OpenHosta import emulate

def image_of(brief: str, template_background: Image.Image, color_theme: ColorTheme, layout: SlideLayoutType) -> str:
    """
    Produce a comprehensive, structured written description of a presentation slide based on a visual concept or brief.
    This output will be used to guide designers, developers, or presenters who need to understand or recreate the slide without seeing it.
    
    **Guidance: What to Include in Your Description**

    Your response should be a **single, well-organized paragraph (or two if necessary)** that includes the following elements in this order:

    1. **Overall Layout & Aesthetic**
        
        - Mention layout (e.g., two-column, full-bleed, grid).
        - Background color (with hex code if provided).
        - Text and accent colors (with hex codes).
        - General style (e.g., modern, corporate, minimalist, high-tech).
    2. **Title & Headers**
        
        - Slide title at the top (text, formatting, colors).
        - Any secondary branding or identifiers (e.g., logo, slide number).
    3. **Left/Top Section (if applicable)**
        
        - Title of the section.
        - Type of visual (e.g., diagram, chart, icon).
        - Key elements: labels, colors, connectors, annotations.
        - Specific data callouts (e.g., "Duration: 5d", "EF: 12").
    4. **Right/Bottom Section (if applicable)**
        
        - Title of the section.
        - Type of visual (e.g., Gantt chart, bar graph, list).
        - Axis labels, timeframes, rows, categories.
        - Data representation (e.g., bars, milestones, progress markers).
    5. **Footer or Corner Details**
        
        - Slide number, copyright, source, or other small text in corners.
        
    **Tone & Style**

    - Use **clear, professional, and precise language**.
    - Be **descriptive, not interpretive**—focus on _what is visible_, not implications.
    - Use **full sentences** rather than bullet points (unless otherwise requested).
    - Include **color references, positioning, typography cues**, and **data labels**.

    Args:
        subject: The subject of the slide.
        template_background: The background image of the slide.
        color_theme: The color theme of the slide.
        layout: The layout of the slide.
      
    Returns:
       The image prompt for the slide.
    """
    return emulate()
    
    
from OpenHosta import closure

fill = closure("fill this object", force_return_type=ColorTheme)
theme = fill("A professional theme based on red and green")
theme = fill("A fun kid friendly theme")

from OpenHosta import ask
steps = ask("describes steps to cook a home made burger")

img_txt = image_of(
    f"pert vs gantt diagrams. Sample values are from this example: {steps}", 
    None, 
    theme, 
    SlideLayoutType.TWO_COLUMNS
    )

img_txt = """
A professional presentation slide featuring a modern two-column layout with a dark slate blue background (#1e293b). The design utilizes crisp white text (#f8fafc) and vibrant red (#ef4444) accents for highlights. The overall slide title at the top in large white and red text reads "PROJECT MANAGEMENT VISUALIZATION: PERT vs. GANTT". In the top right corner is a stylized 'PM' logo in red and white.
The left column, titled "PERT NETWORK DIAGRAM: PROJECT FLOW" in white with a red underline, displays a clean, vector-style illustration of a PERT chart network diagram. It features interconnected red circular nodes labeled "START", "TASK A", "TASK B", "TASK C", "TASK D", "TASK E", "MILESTONE 1", and "END". Red arrows indicate the flow between nodes, with white text labels for data such as "Duration: 5d", "ES: 0, EF: 5", and "Duration: 3d".
The right column, titled "GANTT CHART: TIMELINE & PROGRESS" in white with a red underline, shows a structured Gantt chart timeline. A horizontal timeline axis at the top features months from "JAN" to "DEC" and corresponding weeks, with vertical grid lines. Rows list tasks like "Phase 1: Initiation", "Task 1: Initiation", "Phase 2: Planning", "Task 2: Planning", "Phase 3: Execution", "Task 3: Execution", "Phase 4: Monitoring", "Phase 5: Closure", and "Milestones". Horizontal bars and diamonds in red and white indicate task durations, progress, and milestones (e.g., "Phase 1: Initiation", "Milestone 2", "Execution", "Closure").
The bottom right corner contains the text "SLIDE 04" in white.
"""

import requests
import os
token = os.environ.get("HH_INFERENCE_ENDPOINT")
provider = "replicate"
model = "Qwen/Qwen-Image-2512"
API_URL = "https://router.huggingface.co/replicate/v1/models/qwen/qwen-image-2512/predictions"
headers = {"Authorization": f"Bearer {token}"}


payload = {"input": {"prompt": img_txt}}
response = requests.post(API_URL, headers=headers | {"prefer": 'wait'}, json=payload)
resp = response.json()

img = requests.get(resp['output'][0], headers=headers)

# Convert img.content into PIL Image
img = Image.open(BytesIO(img.content))
os.environ["GTK_PATH"] = ""
img.show()
