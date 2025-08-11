import os
import re
import json
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

# --- All Tool Definitions (Copied from your original code) ---
# It's good practice to keep these in a separate file (e.g., `tools.py`) and import them,
# but for this example, they are included here directly.

from fpdf import FPDF
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import base64

def check_link_status(url: str) -> str:
    """
    Checks if a URL is active and returns its HTTP status. Avoids '404 Not Found' errors.
    Args:
        url: The URL to check.
    Returns:
        A string indicating if the link is valid, broken, or if an error occurred.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        if response.status_code < 400:
            return f"Link is valid. Status code: {response.status_code}"
        else:
            return f"Link is broken. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error checking link: {e}. The URL may be invalid or the server is down."

def create_folder(folder_path: str) -> str:
    """
    Creates a folder at the specified path, including any necessary parent directories.
    Args:
        folder_path: The full path of the folder to create (e.g., 'John_Doe/exhibits').
    Returns:
        A message confirming the folder creation or if it already exists.
    """
    safe_folder_path = re.sub(r'[?:"<>|]', "", folder_path)
    if not os.path.exists(safe_folder_path):
        os.makedirs(safe_folder_path)
        return f"Folder '{safe_folder_path}' created successfully."
    return f"Folder '{safe_folder_path}' already exists."

def browse_and_capture_as_pdf(url: str, output_filename: str) -> str:
    """
    Visits a web link using a headless Chrome browser and saves the rendered page as a PDF.
    Args:
        url: The full URL to visit (e.g., 'https://www.google.com').
        output_filename: The full local path to save the PDF file (e.g., 'output/John_Doe/exhibit1B/source.pdf').
    Returns:
        A message confirming the PDF creation or reporting an error.
    """
    print(f"Attempting to browse and capture: {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = None
    try:
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.get(url)
        driver.implicitly_wait(10)
        print(f"Page '{driver.title}' loaded successfully.")
        result = driver.execute_cdp_cmd(
            "Page.printToPDF", {"printBackground": True, "format": "A4"}
        )
        pdf_data = base64.b64decode(result["data"])
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        with open(output_filename, "wb") as f:
            f.write(pdf_data)
        return f"Successfully saved page '{url}' to '{output_filename}'"
    except Exception as e:
        return f"An error occurred while Browse and capturing PDF: {e}"
    finally:
        if driver:
            driver.quit()

# --- Font Setup for PDF Creation ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# IMPORTANT: Make sure you have the 'DejaVuSans.ttf' font file in the same directory as your script,
# or provide the correct path to it. You may need to download it first.
FONT_PATH = os.path.join(SCRIPT_DIR, "DejaVuSans.ttf")

if not os.path.exists(FONT_PATH):
    print(f"WARNING: Font file not found at {FONT_PATH}. PDFs with non-latin characters may fail.")
    # As a fallback, we can try to proceed without it, but it's not ideal.
    # The create_endeavor_document function will handle the error.

def create_endeavor_document(folder_path: str, person_name: str, topic: str, document_content: str) -> str:
    """
    Creates a structured PDF document for a proposed endeavor inside a specified folder.
    Args:
        folder_path: The path to the folder where the PDF will be saved (e.g., 'John_Doe').
        person_name: The name of the person the endeavor is for (e.g., 'John Doe').
        topic: The chosen topic for the endeavor.
        document_content: The full, structured text content of the proposed endeavor.
    Returns:
        A confirmation message with the path to the created PDF.
    """
    if not os.path.exists(FONT_PATH):
        return f"Error: Font file not found at {FONT_PATH}. Cannot create PDF."

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
    
    # Title
    pdf.set_font('DejaVu', size=16)
    pdf.multi_cell(0, 10, txt=f"Proposed Endeavor for {person_name}", align='C')
    pdf.ln(5)

    # Topic
    pdf.set_font('DejaVu', size=12)
    pdf.multi_cell(0, 10, txt=f"Topic: {topic}", align='C')
    pdf.ln(10)

    # Body
    pdf.set_font('DejaVu', size=11)
    pdf.multi_cell(0, 5, txt=document_content)
    
    # File Naming and Saving
    safe_person_name = re.sub(r'[\\/*?:"<>|]', "", person_name).replace(" ", "_")
    safe_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"proposed_endeavor_{safe_person_name}_{safe_timestamp}.pdf"
    file_path = os.path.join(folder_path, file_name)
    
    os.makedirs(folder_path, exist_ok=True)
    pdf.output(file_path)
    return f"Proposed Endeavor document saved successfully to {file_path}"


# --- Specialized Agent Definitions ---

# Agent 1: Analyzes the CV to extract name and brainstorm topics.
cv_analyzer_agent = Agent(
    name="cv_analyzer_agent",
    model="gemini-1.5-flash",
    description="Analyzes a professional CV to extract the applicant's name and brainstorm 5 suitable NIW endeavor topics.",
    instruction="""
    You are an expert US immigration advisor. Read the provided CV carefully.
    1. Extract the applicant's full name.
    2. Brainstorm 5 distinct, precise, and compelling proposed endeavor topics suitable for an EB-2 NIW petition.
    3. Return the information as a single, clean JSON object with two keys: 'full_name' (a string) and 'topics' (a list of 5 strings).
    Do not add any other text or formatting around the JSON object.
    """
)

# Agent 2: Researches a given topic to find credible sources.
research_agent = Agent(
    name="research_agent",
    model="gemini-1.5-flash",
    description="Finds credible U.S. government or academic sources for a specific topic.",
    tools=[AgentTool(google_search)],
    instruction="""
    You are a diligent research assistant. Your goal is to find 5 highly credible sources for the given topic.
    Focus on U.S. government websites (ending in .gov), official publications, congressional records, or top-tier academic research.
    Return a clean JSON list of 5 URL strings. Do not add any other text.
    """
)

# Agent 3: Writes one section of the endeavor document at a time.
writer_agent = Agent(
    name="writer_agent",
    model="gemini-1.5-pro", # Using a more powerful model for high-quality writing
    description="Writes a single, detailed section of the NIW Proposed Endeavor document.",
    instruction="""
    You are a brilliant writer specializing in U.S. immigration petitions. Your task is to write a single, detailed section for a "Proposed Endeavor" document.
    - Write in the first person ("I will...", "My endeavor...").
    - Ensure the tone is professional, confident, and persuasive.
    - The section should be substantial and well-developed (aim for at least 800 words).
    - If provided with sources, cite them naturally within the text using the format (Exhibit 1B), (Exhibit 1C), etc., corresponding to the order they are given.
    - Do not write the section title itself, only the body text for that section.
    """
)


# --- Main Orchestrator Logic ---

def orchestrate_endeavor_creation():
    """Controls the end-to-end workflow of creating the endeavor document."""
    
    print("Welcome to the NIW Endeavor Document Generator! 🚀")
    cv_text = input("Please paste the full text of your CV and press Enter twice:\n\n")

    # === Step 1: Analyze CV and Get Topics ===
    print("\n1. Analyzing your CV and brainstorming topics...")
    try:
        analysis_response = cv_analyzer_agent.generate(cv_text)
        analysis_data = json.loads(analysis_response)
        applicant_name = analysis_data['full_name']
        topics = analysis_data['topics']
        print(f"Analysis complete. Applicant identified as: {applicant_name}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error: Could not parse the analysis from the agent. Please try again. Details: {e}")
        return

    # === Step 2: User Selects Topic ===
    print("\nPlease choose a topic for your proposed endeavor:")
    for i, topic in enumerate(topics):
        print(f"  {i+1}. {topic}")

    chosen_index = -1
    while chosen_index < 0 or chosen_index >= len(topics):
        try:
            choice = int(input(f"\nEnter the number of your choice (1-{len(topics)}): "))
            if 1 <= choice <= len(topics):
                chosen_index = choice - 1
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    chosen_topic = topics[chosen_index]
    print(f"\nGreat choice! We will proceed with the topic: '{chosen_topic}'")

    # === Step 3: Research and Validate Sources ===
    print("\n2. Researching credible sources for your topic...")
    validated_sources = []
    try:
        source_urls_response = research_agent.generate(f"Topic: {chosen_topic}")
        source_urls = json.loads(source_urls_response)
        
        print("Validating sources...")
        for i, url in enumerate(source_urls):
            status = check_link_status(url)
            if "valid" in status.lower():
                exhibit_label = f"Exhibit 1{chr(ord('B') + i)}" # Creates Exhibit 1B, 1C, ...
                validated_sources.append({"url": url, "exhibit": exhibit_label})
                print(f"  - {exhibit_label}: {url} [VALID]")
            else:
                print(f"  - {url} [BROKEN/INVALID] - Skipping.")
    except Exception as e:
        print(f"Could not complete research phase. Continuing without sources. Error: {e}")

    # === Step 4: Generate Document Content, Section by Section ===
    print("\n3. Generating the Proposed Endeavor document. This may take several minutes...")
    
    sections = [
        "Introduction and Overview",
        "Substantial Merit",
        "National Importance",
        "Phased Implementation Plan",
        "Projected Economic Impact and Job Creation",
        "Broader Impacts and Conclusion"
    ]
    full_document_content = ""
    
    # Create a string of sources for the writer agent's prompt
    source_info_for_prompt = "\n".join([f"{s['exhibit']}: {s['url']}" for s in validated_sources])

    for i, section_title in enumerate(sections):
        print(f"  - Writing section {i+1}/{len(sections)}: {section_title}...")
        prompt = (
            f"Write the '{section_title}' section for a Proposed Endeavor document.\n"
            f"The applicant's name is {applicant_name}.\n"
            f"The chosen topic is: '{chosen_topic}'.\n"
            f"Here are the credible sources you can cite:\n{source_info_for_prompt}"
        )
        section_content = writer_agent.generate(prompt)
        full_document_content += f"## {section_title.upper()}\n\n{section_content}\n\n"

    print("Document generation complete!")

    # === Step 5: Save All Files ===
    print("\n4. Saving all documents and exhibits to your local file system...")
    
    # Create main folder
    sanitized_name = re.sub(r'[\\/*?:"<>|]', "", applicant_name).replace(" ", "_")
    main_folder_path = os.path.join(os.getcwd(), sanitized_name)
    print(create_folder(main_folder_path))

    # Save the main endeavor PDF
    print(create_endeavor_document(
        folder_path=main_folder_path,
        person_name=applicant_name,
        topic=chosen_topic,
        document_content=full_document_content
    ))

    # Save the exhibit PDFs
    for source in validated_sources:
        exhibit_folder_path = os.path.join(main_folder_path, source['exhibit'])
        print(create_folder(exhibit_folder_path))
        pdf_path = os.path.join(exhibit_folder_path, "source_material.pdf")
        print(browse_and_capture_as_pdf(url=source['url'], output_filename=pdf_path))
        
    # === Step 6: Confirmation ===
    print("\n--- All Done! ---")
    print(f"Your NIW Proposed Endeavor documents have been successfully created.")
    print(f"You can find them in the following directory: {main_folder_path}\n")


if __name__ == "__main__":
    # To run this, you need to have the google.adk library installed and configured,
    # along with all other dependencies like fpdf, requests, selenium, webdriver-manager.
    orchestrate_endeavor_creation()