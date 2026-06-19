# Agentic Visual Desktop Copilot 👁️✨

An AI-powered, vision-based desktop assistant that "sees" your screen, understands natural language instructions, and visually highlights exactly where you need to click by drawing a glowing overlay on your desktop.

![Agent Architecture](logs/annotated_screen.png)  
*(Example of OmniParser's bounding box recognition, automatically saved to `logs/annotated_screen.png` during execution.)*

## 🌟 How It Works

Instead of blindly guessing coordinates, this Copilot uses a sophisticated pipeline combining local vision parsing and lightning-fast cloud LLM reasoning:

1. **Trigger & Capture:** You press the global hotkey (`Ctrl + Shift + Space`) and type your natural language instruction into the terminal. The copilot instantly captures your screen using `mss`.
2. **Vision Parsing (OmniParser):** The screenshot is sent to a locally hosted instance of Microsoft's **OmniParser**. OmniParser identifies all interactive GUI elements (buttons, icons, text boxes) and extracts their coordinates and text via OCR.
3. **Reasoning Engine (Groq + Llama 3.3):** The parsed list of elements is stripped of heavy coordinates to save tokens and sent to **Groq** running the `llama-3.3-70b-versatile` model. The LLM acts as the reasoning engine to determine exactly which element ID matches your instruction.
4. **Visual Overlay:** A borderless, click-through **PyQt5** overlay is drawn directly on your screen, pulsing a yellow bounding box around the target element. 
5. **Confirmation:** The copilot uses `pynput` to listen for your global mouse clicks. Once you click inside the bounding box, the overlay disappears and the copilot is ready for its next instruction.

## 🛠️ Technology Stack

* **Orchestration:** Python (`main.py`, `src/controller.py`)
* **Screen Capture:** `mss` (fast, multi-monitor support)
* **Vision / Parsing:** Microsoft [OmniParser](https://github.com/microsoft/OmniParser) (running locally via Gradio API)
* **Reasoning / LLM:** Groq API (`llama-3.3-70b-versatile` for extremely fast inference)
* **GUI Overlay:** `PyQt5` (Frameless, translucent, always-on-top window)
* **Global Input Hooks:** `keyboard` (for the hotkey) and `pynput` (for detecting the confirmation click)

## 🚀 Setup & Installation

### 1. Prerequisites
* Python 3.10+
* Windows OS (Linux/Mac support possible with minor PyQt window flag tweaks)

### 2. Install Dependencies
Create a virtual environment and install the required packages:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
# Get an API key from console.groq.com
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# The address where your local OmniParser Gradio server is running
OMNIPARSER_ENDPOINT=http://127.0.0.1:7861
```

### 4. Setup OmniParser
This project relies on OmniParser to function.
1. Navigate to the `OmniParser` directory.
2. Follow OmniParser's setup instructions (downloading models, installing its specific dependencies into its own environment).
3. Start the OmniParser server: `python gradio_demo.py`

## 💻 Usage

To run the copilot, you will need two terminal windows running side-by-side.

**Terminal 1: Start the Vision Engine**
```powershell
cd OmniParser
# Activate OmniParser's environment if you use a separate one
python gradio_demo.py
```
*Wait until you see the Gradio URL `http://127.0.0.1:7861`.*

**Terminal 2: Start the Copilot**
```powershell
.\venv\Scripts\activate
python main.py
```

### Triggering the Agent
1. Press `Ctrl + Shift + Space` from anywhere on your computer.
2. The `main.py` terminal will prompt you to enter your instruction (e.g., *"How do I exit this application?"* or *"Click the search bar"*).
3. Wait a few seconds for the pipeline to run.
4. A yellow pulsing box will appear over the correct UI element on your screen.
5. Click inside the box to dismiss it!

## 🧠 Architectural Highlights & Optimizations
* **Token Optimization:** Screen parsing generates massive JSONs. The `groq_client.py` strips out the `bbox` coordinate dictionaries and truncates long paragraphs of text before sending them to Groq. This prevents hitting the 12,000 TPM limit on free tiers while retaining 100% of the reasoning accuracy.
* **Non-blocking Overlays:** PyQt5 operates on the main thread, while the `pynput` click listener runs in the background. A custom event loop (`app.processEvents()`) bridges the two safely.
* **Coordinate Mapping:** OmniParser returns coordinates as `[center_x, center_y, width, height]` ratios. The controller correctly translates these ratios to physical pixel coordinates based on your active screen resolution.
