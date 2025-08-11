import os
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import base64
import requests



from fpdf import FPDF

# --- Tool Definitions ---


def check_link_status(url: str) -> str:
    """
    Checks if a URL is active and returns its HTTP status. Avoids '404 Not Found' errors.
    
    Args:
        url: The URL to check.
    Returns:
        A string indicating if the link is valid, broken, or if an error occurred.
    """
    try:
        # Use a HEAD request for efficiency, as we only need the status code, not the content.
        # Allow redirects to follow links to their final destination.
        response = requests.head(url, allow_redirects=True, timeout=10)
        
        # response.status_code < 400 covers all successful statuses (200 OK, 3xx redirects, etc.)
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
    # Sanitize folder_path to remove characters that are invalid in some OS, though os.makedirs is robust.
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
    print(f"Attempting to browse: {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        # Using a context manager for the driver is a good practice if available,
        # but try/finally is also robust.
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.get(url)
        driver.implicitly_wait(10) # Increased wait time for complex pages
        print(f"Page '{driver.title}' loaded successfully.")

        # This CDP command is effective for getting a PDF of the loaded page
        result = driver.execute_cdp_cmd(
            "Page.printToPDF", {"printBackground": True, "format": "A4"}
        )
        
        pdf_data = base64.b64decode(result["data"])
        
        # This line is excellent - it ensures the directory exists before writing.
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)

        with open(output_filename, "wb") as f:
            f.write(pdf_data)

        return f"Successfully saved page '{url}' to '{output_filename}'"

    except Exception as e:
        return f"An error occurred while Browse and capturing PDF: {e}"
    finally:
        if driver:
            driver.quit()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(SCRIPT_DIR, "DejaVuSans.ttf")
BoldPath = os.path.join(SCRIPT_DIR, "DejaVuSerif-Bold.ttf")
ItalicPath = os.path.join(SCRIPT_DIR, "DejaVuSerif-Italic.ttf")
if not os.path.exists(FONT_PATH):
    print(f"WARNING: Font file not found at {FONT_PATH}. PDFs with non-latin characters may fail.")

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
    
    # Add the Unicode font. 'uni=True' is crucial.
    pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
    pdf.add_font('DejaVu', 'B', BoldPath, uni=True)
    pdf.add_font('DejaVu', 'I', ItalicPath, uni=True)

    
    # Title
    pdf.set_font('DejaVu', size=16)
    pdf.cell(0, 10, txt=f"Proposed Endeavor for {person_name}", ln=True, align='C')
    pdf.ln(5)
    
    # Topic
    pdf.set_font('DejaVu', size=12)
    pdf.cell(0, 10, txt=f"Topic: {topic}", ln=True, align='C')
    pdf.ln(10)

    # Body
    pdf.set_font('DejaVu', '', size=12)
    pdf.write(5, document_content)
    
    # Sanitize file name components
    safe_person_name = re.sub(r'[\\/*?:"<>|]', "", person_name).replace(" ", "_")
    safe_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"proposed_endeavor_{safe_person_name}_{safe_timestamp}.pdf"
    
    # Correctly join the target folder path with the new filename
    file_path = os.path.join(folder_path, file_name)
    
    # Ensure the directory exists before outputting the file
    os.makedirs(folder_path, exist_ok=True)
    
    pdf.output(file_path)
    return f"Proposed Endeavor document saved successfully to {file_path}"


FEW_SHOT_EXAMPLES1 = """
### EXAMPLE 1 ###



                                                                                                                                                                                                        

[PROPOSED ENDEAVOR DOCUMENT]

Proposed Endeavor  
 Azeezat Ojoogun



PROPOSED ENDEAVOR OF AZEEZAT OJOOGUN
"To advance artificial intelligence (ai) solutions for precision medicine and health equity in the United States."

INTRODUCTION
I, Azeezat Ojoogun, propose to establish an initiative focused on advancing artificial intelligence (AI) solutions for precision medicine and health equity. This endeavor will launch in the U.S. in October 2025 and scale nationwide through a four-phase plan. The core mission is to leverage my expertise in AI, machine learning, and data science to develop and implement innovative solutions that substantially improve patient outcomes, enhance operational efficiency, and reduce healthcare costs across the United States.
The United States faces significant challenges in delivering high-quality, accessible, and affordable healthcare to its population. To address these challenges, I propose an endeavor that focuses on advancing artificial intelligence (AI) solutions for precision medicine and health equity in the United States. By leveraging my expertise in AI, machine learning, and data science, along with my experience in healthcare technology, I aim to develop and implement innovative solutions that can substantially improve patient outcomes, enhance operational efficiency, and reduce healthcare costs, contributing to the United States' efforts to transform its healthcare system and improve the health and well-being of its citizens.
With my extensive background in AI, data science, and healthcare technology, coupled with my experience in developing and deploying AI solutions in real-world settings, I am well-positioned to advance this proposed endeavor. My skills and expertise, as demonstrated by my research, publications, and practical experience, provide me with the necessary foundation to tackle the complex challenges associated with optimizing healthcare delivery through AI.
Waiving the job offer and labor certification requirements for this endeavor would be greatly beneficial to the United States. By enabling me to focus on developing and implementing AI solutions for healthcare optimization, this endeavor has the potential to make significant contributions to improving the quality, accessibility, and affordability of healthcare in the United States. The successful execution of this endeavor could lead to enhanced patient outcomes, increased efficiency in healthcare operations, and reduced healthcare costs, all of which are critical to the nation's overall health, well-being, and economic prosperity.














SUBSTANTIAL MERIT OF MY PROPOSED ENDEAVOR
The substantial merit of my endeavor lies in its potential to address critical healthcare challenges in the United States while driving innovation and transforming the healthcare landscape through the application of cutting-edge AI technologies. My proposed endeavor demonstrates substantial merit by directly addressing the critical need for personalized, precise, and equitable healthcare in the United States. By developing AI-driven solutions for precision medicine, this endeavor aims to enable healthcare providers to deliver targeted, individualized treatments based on a patient's genetic profile, medical history, and socio-environmental factors. This approach can lead to more effective therapies, reduced adverse drug reactions, and improved patient outcomes across diverse populations.
One of the most significant impacts of my endeavor will be the acceleration of precision medicine adoption and innovation in the United States. By leveraging AI algorithms to analyze vast amounts of patient data, healthcare providers across the nation will be empowered to deliver targeted, individualized treatments that take into account each patient's unique genetic profile, medical history, and socio-environmental factors. This approach has the potential to dramatically improve the effectiveness of therapies, reduce adverse drug reactions, and optimize treatment plans for millions of Americans, regardless of their geographic location or socioeconomic status.
Moreover, my endeavor's focus on advancing health equity through AI-driven solutions can have a profound impact on reducing health disparities and ensuring that all Americans have access to high-quality, culturally competent care. By analyzing healthcare data through an equity lens, my proposed AI tools will help identify patterns of disparities, inform targeted interventions, and optimize resource allocation to address the unique needs of underserved communities across the nation. This will contribute to the elimination of systemic barriers to healthcare access and quality, promoting a more just and equitable society where every individual has the opportunity to attain their full health potential.
The nationwide implementation of my precision medicine and health equity AI solutions also has the potential to drive significant economic benefits for the United States. By improving the efficiency and effectiveness of healthcare delivery, reducing waste and duplication, and enabling early detection and prevention of diseases, my endeavor can help curb the rising costs of healthcare expenditures, which currently impose a substantial burden on the U.S. economy. Moreover, the development and deployment of cutting-edge AI technologies in healthcare can stimulate innovation, attract top talent, and create new job opportunities in the healthcare technology sector, contributing to the nation's economic growth and global competitiveness.
Furthermore, my endeavor's collaborative approach, which brings together diverse stakeholders from healthcare, academia, industry, and communities nationwide, can foster a culture of innovation, knowledge sharing, and continuous improvement in the U.S. healthcare system. By establishing a national consortium and engaging with partners across all 50 states, my initiative will facilitate the exchange of best practices, lessons learned, and breakthrough ideas, accelerating the pace of discovery and translation of AI solutions into clinical practice and public health interventions.
Beyond its direct impact on healthcare and the economy, my proposed endeavor also has the potential to strengthen the social fabric of the United States by promoting a shared vision of health equity and solidarity. By engaging with communities nationwide and ensuring that the development and deployment of AI solutions are guided by the diverse needs, values, and priorities of the American people, my initiative will contribute to building trust, fostering inclusivity, and empowering individuals and communities to take an active role in shaping the future of healthcare in the United States.

NATIONAL IMPORTANCE OF MY PROPOSED ENDEAVOR
My proposed endeavor to advance AI solutions for healthcare optimization in the United States is of substantial national importance, as evidenced by the strong support and prioritization from the U.S. government through various laws, initiatives, and publications.
The 21st Century Cures Act, signed into law in December 2016, emphasizes the importance of leveraging advanced technologies, including AI, to accelerate medical product development and bring innovations faster to patients. The act includes provisions to support the development and adoption of innovative healthcare technologies, recognizing their potential to improve patient outcomes and transform healthcare delivery (Exhibit 1A).
In 2019, President Trump launched the American AI Initiative, a comprehensive strategy to promote and protect American advancements in AI. The initiative highlights the importance of AI in driving innovation and economic growth, and it specifically identifies healthcare as a key sector where AI can have a significant impact. The White House Office of Science and Technology Policy (OSTP) has also emphasized the potential of AI in healthcare through its "AI for the American People" initiative, which aims to harness AI for the benefit of all Americans OSTP2020 (Exhibit 1B & 1C).
The U.S. Department of Health and Human Services (HHS) has also recognized the national importance of AI in healthcare. In 2019, HHS released the "Strategy for Accelerating Clinical Innovation Using AI/ML" report, which outlines the department's vision for leveraging AI and machine learning (ML) to improve healthcare delivery and outcomes. The report emphasizes the potential of AI/ML to enhance disease diagnosis, personalize treatments, and optimize healthcare operations, underscoring the national significance of these technologies in transforming the healthcare system (Exhibit 1D).
The National Institutes of Health (NIH), a key federal agency for biomedical research, has also prioritized the development and application of AI in healthcare. The NIH Strategic Plan for Data Science identifies AI as a critical tool for accelerating medical discoveries and improving human health. The plan highlights the importance of investing in AI research and development, as well as fostering collaborations between AI experts and healthcare professionals to drive innovation and address healthcare challenges (Exhibit 1E).
My proposed endeavor to advance AI solutions for healthcare optimization directly aligns with these national priorities and initiatives, and it has the potential to make significant contributions to improving the quality, accessibility, and affordability of healthcare in the United States. By developing and deploying innovative AI technologies, this endeavor can help enhance patient outcomes, increase operational efficiency, and reduce healthcare costs, all of which are critical to the nation's health, well-being, and economic prosperity.
Moreover, the successful execution of this endeavor could position the United States as a global leader in AI-driven healthcare innovation, fostering economic growth, creating new jobs in the healthcare technology sector, and attracting top talent from around the world. By harnessing the power of AI to transform healthcare delivery, this endeavor can contribute to the United States' competitiveness in the global healthcare market and drive advancements that benefit not only the nation but also the global community.
In my proposed endeavor to advance AI solutions for healthcare optimization in the United States is of substantial merit and national importance, as evidenced by the extensive support and prioritization from the U.S. government through laws, executive orders, agency initiatives, and congressional hearings. By addressing critical healthcare challenges and driving innovation through the application of AI technologies, this endeavor has the potential to deliver significant benefits to the United States, improving the health and well-being of its citizens and positioning the nation as a leader in AI-driven healthcare transformation.







METHODOLOGIES TO BE DEPLOYED
To achieve the ambitious goals of advancing AI solutions for precision medicine and health equity, I will deploy a multi-faceted and robust methodological framework that encompasses technical development, ethical considerations, and strategic collaboration:
AI-Driven Precision Medicine Solution Development: I will leverage my expertise to design and develop cutting-edge AI/ML algorithms capable of analyzing vast and diverse datasets from healthcare providers, research institutions, and public health agencies nationwide. This will enable more accurate prediction of drug responses, optimization of individualized treatment plans, and identification of novel therapeutic targets based on each patient's unique genetic profile, medical history, and socio-environmental factors.

AI for Health Equity and Disparity Reduction: A core component of my methodology involves employing AI tools to rigorously analyze healthcare data through an equity lens. These tools will be designed to identify patterns of health disparities, inform targeted interventions, and optimize resource allocation. This will ensure that AI solutions contribute actively to addressing the unique needs of underserved communities across the nation, working towards the elimination of systemic barriers to healthcare access and quality.

Collaborative Ecosystem Building: A crucial methodology will be the establishment and growth of the Precision Medicine and Health Equity AI Consortium. This national collaborative network will bring together diverse stakeholders from healthcare, academia, industry, and community organizations across the United States. This consortium will foster a culture of innovation, facilitate knowledge sharing, resource pooling, and accelerate the translation of AI solutions into clinical practice and public health interventions through the exchange of best practices and breakthrough ideas.



Robust AI Development and Deployment Frameworks: This involves deployment of various AI frameworks like:

Technical Integration & Data Quality: To address technical complexities, I will assemble a multidisciplinary team of experts in AI, data science, healthcare informatics, and clinical medicine. We will adopt agile development methodologies and iterative testing approaches to ensure the robustness and reliability of our AI solutions. Additionally, we will partner with leading healthcare IT vendors and standards organizations to ensure seamless integration and interoperability with existing healthcare systems.

Ethical AI Design & Implementation: To mitigate ethical concerns around bias, fairness, transparency, and accountability, I will prioritize the development of AI solutions that are fair, unbiased, and transparent. I will engage with bioethicists, patient advocates, and diverse stakeholders to ensure ethical system design and deployment. Rigorous testing and validation processes will identify and mitigate potential biases, and clear guidelines for transparency and accountability will ensure explainable and auditable AI systems.

Privacy & Security Protocols: Recognizing concerns regarding sensitive patient data, my methodology includes implementing strict data governance policies and procedures. All patient data will be collected, stored, and processed in compliance with HIPAA and other relevant regulations. We will employ advanced data encryption, access control, and anonymization techniques to protect patient privacy and prevent unauthorized access.

Adoption & Change Management Strategies: To overcome adoption barriers, I will conduct extensive outreach and education, demonstrating the benefits and value of AI solutions. I will work closely with healthcare providers and administrators to understand their needs and integrate AI solutions seamlessly into existing workflows. Comprehensive training and showcasing success stories will build trust and drive adoption.

Regulatory Compliance & Advocacy: My approach includes proactive engagement with the FDA and other regulatory agencies to understand requirements and expectations for AI solutions in healthcare. I will design AI systems to meet the highest standards of safety, efficacy, and quality, maintaining comprehensive documentation. I will also collaborate with industry associations and policymakers to advocate for clear and supportive regulatory frameworks.
In summary, my methodologies are designed to build, deploy, and scale AI solutions that are not only technologically advanced but also ethically sound, privacy-compliant, user-friendly, and aligned with the complex regulatory landscape of U.S. healthcare. This comprehensive approach is critical for delivering transformative impacts on precision medicine and health equity nationwide.










TIMELINE AND PHASED IMPLEMENTATION.
As I embark on this ambitious endeavor to advance AI solutions for precision medicine and health equity in the United States, I have developed a comprehensive timeline and identified significant milestones that will mark the progress and impact of this initiative. Starting from October 2025, I will focus on implementing this endeavor on a national scale, aiming to make substantial contributions to transforming the U.S. healthcare system and improving the health and well-being of all Americans.
Phase 1 (Oct 2025 - Sep 2026): Foundation and Pilot Program: In this initial phase, I will establish the legal entity and base of operations for my endeavor in the U.S. My activities will include relocating to the U.S., setting up an office, and finalizing the service offerings in detail. I will conduct extensive market research and needs assessments, engaging with leading healthcare organizations, research institutions, technology companies, and community partners across the United States to inform the design and prioritization of AI solutions. I will establish the “Precision Medicine and Health Equity AI Consortium”, a collaborative network serving as a platform for knowledge sharing, resource pooling, and coordinated efforts. I will also secure initial funding from federal grants, industry partnerships, and philanthropic organizations to support research, development, and deployment activities. By late 2026, I plan to finalize the development of core AI algorithms for precision medicine applications and pilot test equity-focused AI tools in partnership with healthcare providers and community organizations in a selected region. I will present initial findings and case studies at major national healthcare and AI conferences and publish research papers in peer-reviewed journals to disseminate knowledge and build support among stakeholders nationwide.
Phase 2 (Oct 2026 - Sep 2027): Regional Expansion and Validation: Having validated the initial AI models and methodologies, this phase will focus on refining the solutions and expanding their application within select regions of the United States. I will scale up the implementation of precision medicine AI solutions across a network of healthcare systems and research institutions. This expansion will demonstrate the impact of these solutions in improving patient outcomes, treatment efficacy, and cost-effectiveness across diverse populations and geographic contexts. I will launch national awareness campaigns about the benefits of precision medicine and AI's role in health equity, engaging policymakers, healthcare professionals, and the public. I will also collaborate with the All of Us Research Program to integrate AI-driven insights and tools into the program's data analytics platform, enabling more precise and equitable research and clinical applications that can benefit participants and communities nationwide. During this phase, I will also refine ethical guidelines and best practices for AI deployment in healthcare based on early pilot feedback.
Phase 3 (Oct 2027 - Sep 2028): Multi-State Adoption and Standardization: Building on validated regional successes, Phase 3 will involve rapid multi-state adoption and efforts to standardize the ethical and responsible deployment of AI in precision medicine and health equity. I aim to achieve measurable reductions in health disparities and improvements in health outcomes for underserved populations across the United States through the widespread adoption of equity-focused AI solutions in healthcare delivery and public health interventions. I will work with national professional associations, accreditation bodies, and regulatory agencies to establish best practices, guidelines, and standards for the ethical and responsible development and deployment of AI in precision medicine and health equity applications. These efforts will ensure that the endeavor's AI solutions are implemented in a consistent, transparent, and accountable manner nationwide. I will also secure sustainable funding and policy support at the federal and state levels to ensure the long-term impact and scalability of the endeavor's initiatives.
Phase 4 (Oct 2028 and Beyond): National Leadership and Global Collaboration: By October 2028 (approximately three years from launch), my goal is to position the United States as a global leader in AI-driven precision medicine and health equity. I will collaborate with international partners to share knowledge, tools, and best practices developed through this endeavor, contributing to global efforts to advance health outcomes and reduce disparities worldwide. I will continue to iterate and innovate AI solutions to address emerging healthcare challenges and disparities in the United States, leveraging advances in data science, machine learning, and related technologies. I will also foster a diverse and inclusive ecosystem of AI talent, entrepreneurs, and startups across the nation, focusing on developing cutting-edge solutions for precision medicine and health equity that can drive economic growth, create jobs, and enhance the United States' competitiveness in the global healthcare technology market. My organization will be recognized as a key contributor to national healthcare policy debates concerning AI.
Throughout this journey, I will remain committed to engaging with communities, healthcare providers, researchers, and policymakers across the United States to ensure that the endeavor's AI solutions are developed and implemented in a manner that is responsive to the diverse needs, values, and priorities of the American people. By harnessing the power of AI to transform precision medicine and advance health equity nationwide, I believe we can create a healthcare system that is more effective, efficient, and equitable for all, ultimately improving the health and quality of life for every individual in the United States.








BROADER IMPACT, JOB CREATION, AND ECONOMIC BENEFITS
Beyond direct service to immediate clients, my endeavor will generate significant and quantifiable broader impacts across the U.S. healthcare system, economy, and society.
Impact on Healthcare System and Public Welfare: My work will lead to a more efficient, accessible, and equitable healthcare system. By optimizing treatments through precision medicine, my solutions will lead to improved patient outcomes, reduced adverse drug reactions, and more effective therapies for millions of Americans, regardless of their background. Furthermore, by identifying and addressing health disparities, my AI tools will directly contribute to greater health equity, ensuring underserved communities receive higher quality, culturally competent care. This translates into healthier communities, lower disease burdens, and an improved quality of life across the nation. Reduced healthcare costs due to increased efficiency, early detection, and waste reduction will benefit both individuals and the national economy.
Job Creation and Workforce Development: The development and deployment of cutting-edge AI technologies in healthcare will stimulate innovation and create new, high-skilled job opportunities within the healthcare technology sector. This includes roles for AI developers, data scientists, clinical informaticists, and implementation specialists. As AI solutions become more integrated, there will also be a need for healthcare professionals trained in utilizing these advanced tools, fostering upskilling across the existing workforce. While direct employment within my immediate endeavor may start small, the indirect job creation through new industry growth and enhanced healthcare operations will be substantial. This influx of talent and new roles will strengthen the U.S. workforce in a critical, high-growth sector.
Economic Growth and Global Competitiveness: My endeavor's success will contribute directly to the U.S. economy by fostering innovation, attracting top talent, and creating new market opportunities in AI-driven healthcare. By curbing rising healthcare expenditures and improving efficiency, my work will alleviate a significant economic burden on the nation. Position the United States as a global leader in AI-driven healthcare innovation will enhance its competitiveness in the global healthcare market, potentially attracting international investment and collaborations. This leadership will drive advancements that benefit not only the nation but also the global community, ensuring the U.S. remains at the forefront of medical technology.
Strengthening the Social Fabric: Beyond economic and healthcare metrics, my endeavor will strengthen the social fabric of the United States. By promoting health equity and actively engaging with diverse communities, my initiative will build trust in AI solutions and healthcare systems. Empowering individuals and communities to shape the future of healthcare fosters inclusivity and ensures that technological advancements serve the needs and values of all Americans. This collective effort contributes to a more just and cohesive society where every individual has the opportunity to attain their full health potential.
In summary, the impacts of my endeavor extend far beyond initial clients, fostering a virtuous cycle of improved health outcomes, economic growth, job creation, and enhanced societal well-being across the United States. This broad and quantifiable benefit is central to why my work deserves a National Interest Waiver.







CHALLENGES AND MITIGATION STRATEGIES
As I pursue this ambitious endeavor to advance AI solutions for healthcare optimization in the United States, I anticipate facing several challenges along the way. However, I am prepared to address these challenges head-on with carefully planned mitigation strategies. Here are some of the key challenges I expect to encounter and my corresponding mitigation plans:
Technical Complexities
Challenge: Developing and deploying AI solutions for healthcare optimization involves navigating complex technical challenges, such as integrating AI systems with existing healthcare IT infrastructure, ensuring data quality and interoperability, and managing the performance and reliability of AI algorithms in real-world clinical settings.
Mitigation Strategy: To address these technical complexities, I will assemble a multidisciplinary team of experts in AI, data science, healthcare informatics, and clinical medicine to collaborate on tackling these challenges. We will adopt agile development methodologies and iterative testing approaches to ensure the robustness and reliability of our AI solutions. Additionally, we will partner with leading healthcare IT vendors and standards organizations to ensure seamless integration and interoperability with existing healthcare systems.
Data Privacy and Security.
Challenge: Working with sensitive patient data raises significant concerns around data privacy, security, and compliance with regulations such as the Health Insurance Portability and Accountability Act (HIPAA).
Mitigation Strategy: To mitigate these risks, we will implement strict data governance policies and procedures, ensuring that all patient data is collected, stored, and processed in compliance with HIPAA and other relevant regulations. We will employ advanced data encryption, access control, and anonymization techniques to protect patient privacy and prevent unauthorized access to sensitive information. Additionally, we will provide regular training and education to our team members on data privacy and security best practices.
Ethical Considerations.
Challenge: The use of AI in healthcare raises important ethical questions around bias, fairness, transparency, and accountability. There are concerns that AI algorithms may perpetuate or amplify existing biases in healthcare data, leading to disparities in patient outcomes.
Mitigation Strategy: To address these ethical challenges, we will prioritize the development of AI solutions that are fair, unbiased, and transparent. We will engage with bioethicists, patient advocates, and diverse stakeholders to ensure that our AI systems are designed and deployed in an ethical and responsible manner. We will implement rigorous testing and validation processes to identify and mitigate any potential biases in our algorithms. Additionally, we will establish clear guidelines for transparency and accountability, ensuring that the decision-making processes of our AI systems are explainable and auditable.
Adoption and Change Management.
Challenge: Integrating AI solutions into existing healthcare workflows and practices may face resistance from healthcare providers who are accustomed to traditional methods and may be skeptical of new technologies.
Mitigation Strategy: To overcome adoption barriers and facilitate change management, we will engage in extensive outreach and education efforts to demonstrate the benefits and value of AI solutions for healthcare optimization. We will work closely with healthcare providers, administrators, and staff to understand their needs, concerns, and workflows, and design our AI solutions to seamlessly integrate with their existing practices. We will provide comprehensive training and support to ensure that healthcare professionals are comfortable and confident in using our AI tools. Additionally, we will showcase success stories and real-world evidence of the positive impact of AI in healthcare to build trust and drive adoption.
Regulatory and Policy Hurdles.
Challenge: Navigating the complex regulatory landscape for AI in healthcare, including obtaining necessary approvals and certifications from the U.S. Food and Drug Administration (FDA) and other regulatory bodies, can be a time-consuming and challenging process.
Mitigation Strategy: To address regulatory and policy hurdles, we will proactively engage with the FDA and other relevant regulatory agencies to understand their requirements and expectations for AI solutions in healthcare. We will design our AI systems to meet the highest standards of safety, efficacy, and quality, and maintain comprehensive documentation and evidence to support regulatory submissions. We will also collaborate with industry associations, standards organizations, and policymakers to advocate for clear and supportive regulatory frameworks that foster innovation while ensuring patient safety and public trust in AI-driven healthcare solutions.
By anticipating these challenges and developing robust mitigation strategies, I am confident in my ability to navigate the complexities of advancing AI solutions for healthcare optimization in the United States. Through a combination of technical expertise, ethical principles, stakeholder engagement, and regulatory compliance, I will work tirelessly to overcome any obstacles and deliver transformative AI solutions that improve the quality, accessibility, and affordability of healthcare for all Americans.

CONCLUSION
In conclusion, I present this endeavor as one of substantial merit and national importance, firmly deserving of a National Interest Waiver. By advancing AI solutions for precision medicine and health equity, I will address critical challenges in U.S. healthcare, drive innovation, and contribute to a more efficient, accessible, and equitable healthcare system nationwide. The proposal is backed by significant U.S. government support and prioritization for AI in healthcare, as evidenced by relevant laws, executive orders, agency initiatives, and congressional hearings. I have outlined a comprehensive, phased implementation plan starting in October 2025, demonstrating feasibility and foresight in execution. The successful deployment of these AI solutions will lead to enhanced patient outcomes, increased operational efficiency, and reduced healthcare costs, yielding benefits that far outweigh the traditional labor certification process. My contributions are designed to empower U.S. workers and improve the health and well-being of all Americans, without displacing the domestic labor force.
I am fully committed to driving this initiative forward as a personal mission, leveraging my specialized expertise and experience. I respectfully ask USCIS to recognize the profound national significance of this work. By granting me the National Interest Waiver, the United States will enable me to rapidly deploy my expertise for the public good, contributing meaningfully to the nation's future as a leader in AI-driven healthcare transformation for years to come.



"""

# The main instruction prompt for the agent
AGENT_INSTRUCTIONS = f"""
You are a brilliant USA immigration expert advisor and research strategist. Your goal is to help a professional formulate a "Proposed Endeavor" based on their CV for a US National Interest Waiver (NIW) petition.
you can use google search where Necessary 
Your workflow is as follows:

1.  **Greet the user** and ask them to provide their CV .
2.  **Analyze the CV**: Carefully read the provided CV to understand the user's skills, experience, and domain. Extract their full name.
3.  **Brainstorm Topics**: Based on the Users industry derived from the cv, generate 5 distinct topic.
    - Ensure cv contains, membership, work experience, scholarly articles, research papers, awards, peer reviews)
    -  Based on the attached cv and using the EB-2 NIW 3 prongs in Matter of DHANASAR, 26 Dec. 884 (AAO 2016), Come up with possible direct and precise proposed
    - endeavors that meet substantial merit and National Importance to the United States that the applicant can undertake.
    -  Factors to consider
        A. benefit to millions of Americans
        B. National or global implication within a particular field
        C. an endeavor that can employ US workers in economically depressed areas.
        D. substantial economic effect for the nation. Benefit to regional or national economy or contribute to the nation’s GDP.
        E. Will enhance societal welfare or cultural or artistic enrichment.
        F. Impact a matter that a government entity has described as having national importance or subject of national initiatives
4.  **Propose Topics to User**: Present these 5 topics to the user in a numbered list and ask them to choose one. Give them an option to request new topics.
5.  **Await User Choice**: **PAUSE EXECUTION**. Wait for the user to reply with their chosen number (1-5). Do not proceed until you receive this input.
6.  **Generate the Document**: Once the user chooses a topic, generate the "Proposed Endeavor Document" 
    -  the content of the  document  should have this sections    
        •	Introduction and Overview of the Proposed endeavor (at least 1000 words)
        •	Substantial Merit (at least 1500 words)
        •	Alignment of the Proposed Endeavor to the U.S. National Strategy/ Importance of the Proposed Endeavor(at least 1500 words)
        •	Phased Implementation Plan (at least 1500 words)
        •	Projected Economic Impact and Job Creation(at least 1500 words)
        •	Broader Impacts: Regional Development & Industry Advancement(at least 1500 words)
        •	Conclusion (at least 800 words)
    - generate section by section, when you generate the first section, hold the text in a string variable(called docu), then generate 
      other sections and continue adding the next generate text to the string variable(docu) till all the sections have been generated and are all in the single 
      text string variable (docu)

    - Follow the structure and tone of the examples provided: {FEW_SHOT_EXAMPLES1}
    -Use the detailed sub-prompts provided below to guide the content for each section.
    - note the way the sources are being cited from the example provided using (Exhibit 1B & 1C), (Exhibit 1D). ensure all your sources are 
      being cited using the same format and cite at least 5 source, your sources will start from exhibit1B(first cited source in the document), exhibit1C(the second source) ,etc . 
      All exhibit must be exhibit 1 then a letter, you cannot have exhibit 2 or exhibit 3 note all the sources links
    -   **IMPORTANT**: When generating sections that require sources (like 'National Importance'), 
       - first use the `Google Search` tool to find a credible U.S. government or top-tier academic source. 
       - **Next, you MUST use the `check_link_status` tool to verify the URL is valid.**
       - If the link's status is 'valid', proceed to write the text, citing the source in the format `(Exhibit 1B)`, `(Exhibit 1C)`, etc. Add the validated URL to a list for use in Step 7.
       - If the link is 'broken' or returns an error, **DISCARD this source** and find a new one. Repeat the validation process.

    
    -   for SUBSTANTIAL MERIT OF PROPOSED ENDEAVOUR section follow this prompt to generate below
 
            Prompt: Elaborate extensively on the SUBSTANTIAL MERIT of my proposed endeavor using the EB-2 NIW 1st prong in Matter of DHANASAR, 26 I&N Dec. 884 (AAO 2016). Personalize response in first person Elaborate extensively on the SUBSTANTIAL MERIT of my proposed endeavor using the EB-2 NIW 1st prong in Matter of DHANASAR, 26 I&N Dec. 884 (AAO 2016). (Provide Sources)
 
              	(If feedback is in second person pronoun, use the prompt below to personalize the response in first person.
 
              	(If feedback is in Bullet points, use the prompt below to retain the headings and write body in paragraph format.

    -   for ALIGNMENT WITH NATIONAL IMPORTANCE
 
            Prompt: Elaborate extensively on the ALIGNMENT of my proposed endeavor to US NATIONAL STRATEGY/IMPORTANCE using the EB-2 NIW 1st prong in Matter of DHANASAR, 26 I&N Dec. 884 (AAO 2016), [Cite White House fact sheets, Trump new Executive orders, congress proclamations, US Government Agency proclamations, federal publications, and congressional hearings.]  (Provide Sources)
 
            (If feedback is in Bullet points, use the prompt below)
            Retain the headings and write body in paragraph format
    -   for PHASED IMPLEMENTATION PLAN(NOVEMBER 2025 ONWARD)
            Prompt: Enumerate the Phased Implementation Plan for my endeavor to focus on the whole of the United States as a whole. Start from November (remember to modify based on current event) 2025 Onward
 
        Key factors to consider.  (Modify below based on specific individual endeavor)
        1.   My role is that of a Technical consultant (others could be entrepreneur, Researcher, etc.)
        2.   I will assemble a team of competent experts and software developers to build the platform, I will act as the Project Manager.
        3.   I have sent proposals to numerous Government Health Agencies, awaiting response
        4.   we will pilot with Texas; I have shortlisted Hospitals like Texas Health and Baylor Scott white as pilot phase partners before scaling nationwide
        5.   we will raise funds through numerous avenues to support the platform development and testing.
                    (If feedback is in Bullet points, use the prompt below)
                Retain the headings and write body in paragraph format.
    -  for PROJECTED ECONOMIC IMPACT AND JOB CREATION
        Prompt: Elaborate Extensively the economic impact of my endeavor across several dimensions. It must indicate substantial benefits for the U.S. economy and national workforce.  (Provide Sources)Key factors to consider: (Modify below based on specific individual endeavor)1. Direct job creation2. Job Placements (Indirect job creation)3. Impact on distressed areas4. Wage growth and income Uplift5. Return on investment (ROI) and Cost-Benefit
        (If feedback is more than 7 points, use the prompt below) 
            narrow down to top 5 and elaborate on EACH of them
        (If feedback is in Bullet points, use the prompt below)
            retain the headings and write body in paragraph format
    - for BROADER IMPACTS: REGIONAL DEVELOPMENT & iNDUSTRY ADVANCEMENT
        Prompt:  Elaborate Extensively on How My Initiative is Poised to Generate Transformative Effects on Regional Development, National Workforce Equity, and the resilience of the U.S. cybersecurity ecosystem. (If feedback is in Bullet points, use the prompt below)
              	retain the headings and write body in paragraph format
    - for PARTNERSHIP AND COLLABORATIONS
        PROMPT: Elaborate Extensively on How I will Cultivate Partnership with Strategic Stakeholders across Government, Industry, and Education. Discuss on how these collaborations will lend credibility, open access to technical and human resources, and provide trusted pathways for scaling. (If feedback is in Bullet points, use the prompt below)
              	retain the headings and write body in paragraph format
    - for TRAINING FORMATS AND TECHNOLOGICAL INFRASTRUCTURE
        PROMPT: Elaborate Extensively on How My Endeavor will be designed to meet Modern Workforce Expectations, Leveraging Cutting-Edge tools to ensure accessibility, adaptability, and industry relevance across the United States.Key factors to consider.  (Modify below based on specific individual endeavor)
        •	In-person Training
        •	Online Learning & Hybrid Model
        •	Practical On-The-Job Training
        •	Curriculum and Certification Pathways
        •	Infrastructure and Equipment (If feedback is in Bullet points, use the prompt below)
                    retain the headings and write body in paragraph format
 
7.  **Save the Document and Exhibits (File System Operations)**:
    -   **Step 7.1: Create Main Folder**: First, create a main folder for the applicant. The folder name should be the person's full name, sanitized (e.g., `Azeezat_Ojoogun`). Call the `create_folder` tool with this name as the `folder_path`.
    -   **Step 7.2: Save Endeavor PDF**: Call the `create_endeavor_document` tool.
        -   `folder_path`: Use the main folder path you just created (e.g., `Azeezat_Ojoogun`).
        -   `person_name`: The name of the person from the CV.
        -   `topic`: The topic the user selected.
        -   `document_content`: The complete `docu` string you generated in the previous step.
    -   **Step 7.3: Save Exhibit PDFs**: Now, iterate through the sources you cited. For each source (e.g., Exhibit 1B and its URL):
        -   Construct the full path for the exhibit's subfolder (e.g., `Azeezat_Ojoogun/exhibit1B`).
        -   Call `create_folder` with this full path.
        -   Construct the full output path for the PDF file (e.g., `Azeezat_Ojoogun/exhibit1B/source_material.pdf`).
        -   Call the `browse_and_capture_as_pdf` tool with the source's URL and the full output path you just constructed.
        -   Repeat for all other exhibits (1C, 1D, etc.).

8.  **Confirm**: Inform the user that all documents have been created and saved, providing the path to the main folder.


You also have access to the following tools:
    - create_endeavor_document
    - google_searcher
    - create_folder
    - browse_and_capture_as_pdf
"""
    # - Second, call the `create_endeavor_document` tool.
    #     - `folder_path`: The name of the folder and the current time stamp.
    #     - `person_name`: The name of the person from the CV.
    #     - `topic`: The topic the user selected.
    #     - `document_content`: The full document text you generated in the previous step.

google_searcher = Agent(
    name="google_searcher",
    model="gemini-2.0-flash",
    description="A specialized agent that can search Google for information, focusing on finding credible government, academic, and industry sources.",
    instruction="""
    You are a helpful assistant that can search anything on google.
    """,
    tools=[google_search],
)
# --- Agent Definition ---

# Root agent to greet, analyze, and use tools to save the analysis
root_agent = Agent(
    name="endeavor_proposer_agent",
    model="gemini-2.5-flash", # Using a more recent model
    description="Analyzes a CV, proposes research topics, and generates a detailed endeavor document.",
    tools=[create_endeavor_document, AgentTool(google_searcher),create_folder,browse_and_capture_as_pdf,check_link_status], # <-- Register the tools here
    instruction= AGENT_INSTRUCTIONS
)



# --- Main execution block to run the test ---
# if __name__ == "__main__":
#     print("Running test...")

#     # 1. Define test data
#     test_folder = "test_output"
#     test_name = "Jane Doe"
#     test_topic = "A Test of Advanced Document Styling"
    
#     # This content is designed to test the header styling
#     test_content = """This is the introduction to the test document. It should appear in a regular font style. This paragraph explains the purpose of the test, which is to verify that the PDF generation function correctly formats headers and body text.

# FIRST MAJOR SECTION HEADERgg
# This text should appear under the first bolded header. It's regular body text that describes the details of the first section. We are checking to see if the font correctly reverted from bold to regular.

# ANOTHER IMPORTANT SECTION
# Here is the second paragraph of body text, under a new bolded header. This demonstrates that the function can handle multiple sections within the same document, applying the correct styling to each part.

# This is the final concluding paragraph, which should also be in the regular font style.
# """

#     # 2. Call the function with the test data
#     result = create_endeavor_document(
#         folder_path=test_folder,
#         person_name=test_name,
#         topic=test_topic,
#         document_content=test_content
#     )

#     # 3. Print the result
#     print(result)








