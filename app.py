import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import io
from PyPDF2 import PdfReader
import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import tempfile
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-1.5-flash')

# Set page config
st.set_page_config(
    page_title="MedBuddy",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Updated CSS (same as before)
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
        color: #2c3e50;
    }
    .stButton>button {
        background-color: #007bff;
        color: white !important;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
    }
    .report-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: #2c3e50;
    }
    /* ... (rest of the CSS remains the same) ... */
    </style>
""", unsafe_allow_html=True)

def create_pdf_report(analysis, organ_type):
    """Create a PDF report from the analysis"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12
    )
    
    # Build the PDF content
    story = []
    
    # Add title
    story.append(Paragraph(f"Medical Analysis Report - {organ_type}", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Add analysis content
    # Split the analysis into sections and format them
    sections = analysis.split('\n\n')
    for section in sections:
        if section.strip():
            if section.startswith(('#', '1.', '2.', '3.', '4.', '5.')):
                story.append(Paragraph(section, heading_style))
            else:
                story.append(Paragraph(section, normal_style))
            story.append(Spacer(1, 12))
    
    # Build the PDF
    doc.build(story)
    return temp_file.name

def create_analysis_prompt(text, organ_type):
    # ... (same as before) ...
    return f"""As a specialized medical AI assistant for {organ_type} analysis, provide a comprehensive evaluation:

    1. 🔍 Key Findings:
       - Primary observations
       - Critical measurements
       - Notable patterns

    2. 📋 Diagnostic Assessment:
       - Potential diagnoses (ranked by likelihood)
       - Supporting evidence
       - Differential diagnoses

    3. ⚠️ Areas of Concern:
       - Critical abnormalities
       - Risk factors
       - Comparative analysis with normal ranges

    4. 💡 Recommendations:
       - Suggested follow-up tests
       - Monitoring requirements
       - Specialist consultations if needed

    5. 📊 Risk Assessment:
       - Severity indicators
       - Progression markers
       - Prognosis factors

    Medical Report Content:
    {text}
    """

def analyze_text(text, organ_type):
    """Analyze text with enhanced prompt"""
    prompt = create_analysis_prompt(text, organ_type)
    response = model.generate_content(prompt)
    return response.text

def analyze_image(image, organ_type):
    """Analyze medical image with enhanced prompt"""
    # ... (same as before) ...
    prompt = f"""As an expert medical imaging specialist focusing on {organ_type} scans, provide a detailed professional analysis:

    1. 🔍 Technical Assessment:
       - Image quality
       - Positioning
       - Anatomical coverage

    2. 📋 Structural Analysis:
       - Normal anatomical findings
       - Anatomical variants
       - Key measurements

    3. ⚠️ Pathological Findings:
       - Abnormalities detected
       - Location and characteristics
       - Severity assessment

    4. 💡 Clinical Correlation:
       - Potential clinical implications
       - Differential diagnoses
       - Risk stratification

    5. 📊 Recommendations:
       - Follow-up imaging
       - Additional views/sequences
       - Clinical correlation needs
    """
    
    response = vision_model.generate_content([prompt, image])
    return response.text

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Sidebar
with st.sidebar:
    st.image("logo.png", width=100)
    st.title("MedBuddy")
    st.markdown("---")
    
    organ_type = st.selectbox(
        "Select Analysis Type",
        ["Brain", "Heart"],
        format_func=lambda x: f"🧠 {x}" if x == "Brain" else f"❤️ {x}"
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    MedBuddy leverages advanced AI to assist healthcare professionals in:
    - 📊 Medical Report Analysis
    - 🔍 Image Scan Interpretation
    - 💡 Clinical Decision Support
    """)

# Main content
st.title("Medical Analysis Dashboard")
st.markdown("---")

# Tabs for different functionalities
tab1, tab2 = st.tabs(["📄 Report Analysis", "🔍 Scan Analysis"])

with tab1:
    st.header("Medical Report Analysis")
    uploaded_file = st.file_uploader(
        "Upload Medical Report (PDF)",
        type=['pdf'],
        help="Upload a medical report in PDF format for AI analysis"
    )
    
    if uploaded_file:
        with st.spinner("Processing report..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            text = extract_text_from_pdf(uploaded_file)
            analysis = analyze_text(text, organ_type)
            
            st.success("Analysis Complete!")
            with st.expander("View Detailed Analysis", expanded=True):
                st.markdown(analysis)
            
            # Add download button for PDF report
            if st.button("📥 Download Analysis Report"):
                pdf_path = create_pdf_report(analysis, organ_type)
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                st.download_button(
                    label="Click here to download PDF",
                    data=pdf_bytes,
                    file_name=f"medical_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                # Clean up the temporary file
                os.unlink(pdf_path)

with tab2:
    st.header("Medical Scan Analysis")
    uploaded_file = st.file_uploader(
        "Upload Medical Scan",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a medical scan image for AI analysis"
    )
    
    if uploaded_file:
        with st.spinner("Analyzing scan..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            image = Image.open(uploaded_file)
            analysis = analyze_image(image, organ_type)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(image, caption=f"{organ_type} Scan", use_column_width=True)
            with col2:
                st.markdown("### Analysis Results")
                st.markdown(analysis)
            
            # Add download button for PDF report
            if st.button("📥 Download Scan Analysis Report"):
                pdf_path = create_pdf_report(analysis, organ_type)
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                st.download_button(
                    label="Click here to download PDF",
                    data=pdf_bytes,
                    file_name=f"scan_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                # Clean up the temporary file
                os.unlink(pdf_path)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div style='text-align: center; color: #2c3e50;'>
            Made with ❤️ by Team ALPHA20
        </div>
    """, unsafe_allow_html=True)

# Session state for analytics
if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = 0
