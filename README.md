# NIW Petition Document Generator

## Overview
This project is a comprehensive toolset designed to assist in the preparation and generation of documents for U.S. National Interest Waiver (NIW) petitions under the EB-2 visa category. The system automates the creation of well-structured "Proposed Endeavor" documents, which are a critical component of NIW applications.

## Key Features
- **Automated Document Generation**: Creates professionally formatted PDF documents for NIW petitions
- **Multi-Agent System**: Utilizes specialized AI agents for different stages of document preparation
- **Web Research Integration**: Can gather and cite credible sources to support the petition
- **PDF Creation**: Generates properly formatted PDFs with proper fonts and structure
- **Web Content Capture**: Can capture and save web pages as PDFs for evidence collection

## Project Structure
```
legal/
├── Adeosun_Adewale_Victor/      # Example petition documents
│   ├── exhibit1B/              # Exhibit folders containing source materials
│   ├── exhibit1C/
│   └── ...
└── proposed_endeavour_agent/    # Main application code
    ├── agent.py                # Core agent functionality
    ├── generate_niw.py         # Main script for NIW document generation
    ├── DejaVuSans.ttf          # Font file for PDF generation
    ├── DejaVuSerif-Bold.ttf    # Bold font variant
    ├── DejaVuSerif-Italic.ttf  # Italic font variant
    └── test_output/            # Directory for generated documents
```

## Prerequisites
- Python 3.9+
- Google ADK (AI Development Kit)
- Chrome or Chromium browser (for web capture functionality)
- Required Python packages:
  - fpdf
  - requests
  - selenium
  - webdriver-manager
  - google-adk

## Installation
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd legal
   ```

2. Install the required Python packages:
   ```bash
   pip install fpdf requests selenium webdriver-manager
   ```

3. Install the Google ADK (follow the official installation instructions)

## Usage
1. Run the main script:
   ```bash
   python proposed_endeavour_agent/generate_niw.py
   ```

2. When prompted, paste your full CV text and press Enter twice.

3. The system will analyze your CV and suggest 5 potential endeavor topics.

4. Select your preferred topic, and the system will:
   - Research credible sources
   - Generate a comprehensive proposed endeavor document
   - Save it as a PDF in the appropriate directory

## Key Components

### 1. CV Analysis Agent
- Extracts the applicant's name from their CV
- Brainstorms 5 suitable NIW endeavor topics
- Identifies key qualifications and experiences

### 2. Research Agent
- Finds credible U.S. government and academic sources
- Validates URLs and checks link status
- Captures web pages as PDFs for evidence

### 3. Document Writer Agent
- Generates well-structured, persuasive content
- Incorporates citations and references
- Maintains consistent formatting and professional tone

## Example Output
Generated documents follow this structure:
```
Proposed Endeavor for [Applicant Name]

Topic: [Selected Topic]

[Comprehensive document content...]
```

## License
This project is for educational and informational purposes only. Please consult with a qualified immigration attorney for legal advice regarding your specific situation.

---

## ADK Agent Documentation (Original)

### What is an ADK Agent?

## What is an ADK Agent?

The `LlmAgent` (often aliased simply as `Agent`) is a core component in ADK that acts as the "thinking" part of your application. It leverages the power of a Large Language Model (LLM) for:
- Reasoning
- Understanding natural language
- Making decisions
- Generating responses
- Interacting with tools

Unlike deterministic workflow agents that follow predefined paths, an `LlmAgent`'s behavior is non-deterministic. It uses the LLM to interpret instructions and context, deciding dynamically how to proceed, which tools to use (if any), or whether to transfer control to another agent.

## Required Agent Structure

For ADK to discover and run your agents properly (especially with `adk web`), your project must follow a specific structure:

```
parent_folder/
    agent_folder/         # This is your agent's package directory
        __init__.py       # Must import agent.py
        agent.py          # Must define root_agent
        .env              # Environment variables
```

### Essential Components:

1. **`__init__.py`**
   - Must import the agent module: `from . import agent`
   - This makes your agent discoverable by ADK

2. **`agent.py`**
   - Must define a variable named `root_agent`
   - This is the entry point that ADK uses to find your agent

3. **Command Location**
   - Always run `adk` commands from the parent directory, not from inside the agent directory
   - Example: Run `adk web` from the parent folder that contains your agent folder

This structure ensures that ADK can automatically discover and load your agent when running commands like `adk web` or `adk run`.

## Key Components

### 1. Identity (`name` and `description`)
- **name** (Required): A unique string identifier for your agent
- **description** (Optional, but recommended): A concise summary of the agent's capabilities. Used for other agents to determine if they should route a task to this agent.

### 2. Model (`model`)
- Specifies which LLM powers the agent (e.g., "gemini-2.0-flash")
- Affects the agent's capabilities, cost, and performance

### 3. Instructions (`instruction`)
The most critical parameter for shaping your agent's behavior. It defines:
- Core task or goal
- Personality or persona
- Behavioral constraints
- How to use available tools
- Desired output format

### 4. Tools (`tools`)
Optional capabilities beyond the LLM's built-in knowledge, allowing the agent to:
- Interact with external systems
- Perform calculations
- Fetch real-time data
- Execute specific actions

## Getting Started

This example uses the same virtual environment created in the root directory. Make sure you have:

1. Activated the virtual environment from the root directory:
```bash
# macOS/Linux:
source ../.venv/bin/activate
# Windows CMD:
..\.venv\Scripts\activate.bat
# Windows PowerShell:
..\.venv\Scripts\Activate.ps1
```

2. Set up your API key:
   - Rename `.env.example` to `.env` in the greeting_agent folder
   - Add your Google API key to the `GOOGLE_API_KEY` variable in the `.env` file

## Running the Example

To run this basic agent example, you'll use the ADK CLI tool which provides several ways to interact with your agent:

1. Navigate to the 1-basic-agent directory containing your agent folder.
2. Start the interactive web UI:
```bash
adk web
```

3. Access the web UI by opening the URL shown in your terminal (typically http://localhost:8000)

4. Select your agent from the dropdown menu in the top-left corner of the UI

5. Start chatting with your agent in the textbox at the bottom of the screen

### Troubleshooting

If your agent doesn't appear in the dropdown menu:
- Make sure you're running `adk web` from the parent directory (1-basic-agent), not from inside the agent directory
- Check that your `__init__.py` properly imports the agent module
- Verify that `agent.py` defines a variable named `root_agent`

### Alternative Run Methods

The ADK CLI tool provides several options:

- **`adk web`**: Launches an interactive web UI for testing your agent with a chat interface
- **`adk run [agent_name]`**: Runs your agent directly in the terminal
- **`adk api_server`**: Starts a FastAPI server to test API requests to your agent

### Example Prompts to Try

- "How do you say hello in Spanish?"
- "What's a formal greeting in Japanese?"
- "Tell me how to greet someone in French"

You can exit the conversation or stop the server by pressing `Ctrl+C` in your terminal.

This example demonstrates a simple agent that responds to greeting-related queries, showing the fundamentals of agent creation with ADK.
