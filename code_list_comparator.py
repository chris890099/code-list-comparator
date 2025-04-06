import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import base64

# --- Page Config ---
st.set_page_config(
    page_title="Manifest Match | Seamaster",
    page_icon="🌊",
    layout="wide"
)

# --- Custom CSS Styling ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Orbitron:wght@400;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: linear-gradient(135deg, #0a0c1b 0%, #1a1e3a 100%);
            padding: 1rem;
            overflow: hidden;
        }

        .block-container {
            padding: 2rem;
            border-radius: 15px;
            background: rgba(30, 41, 59, 0.85);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        h1 {
            font-family: 'Orbitron', sans-serif;
            color: #00ddeb !important;
            text-shadow: 0 0 5px rgba(0, 221, 235, 0.3);
        }

        h2, h3, .stMarkdown, .stTextInput > label {
            color: #e0e7ff !important;
        }

        /* File Uploader Label (Seamaster Report, Transporter Report) */
        .stFileUploader > label {
            color: #000000 !important;
            font-weight: 800;
            font-size: 1.2rem !important; /* Increased text size */
        }

        /* File Uploader Styling */
        .stFileUploader {
            border: 2px dashed #60a5fa !important;
            border-radius: 10px !important;
            padding: 0.75rem !important;
            background: #0088aa !important;
            transition: border 0.3s ease, transform 0.2s ease;
            max-width: 90% !important;
        }

        .stFileUploader:hover {
            border: 2px dashed #93c5fd !important;
            transform: scale(1.01);
        }

        /* File name and size text */
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] strong {
            color: #0088aa !important;
            font-weight: 500 !important;
        }

        /* Compare Button */
        .stButton>button {
            background: linear-gradient(90deg, #00ddeb 0%, #3b82f6 100%);
            color: white;
            font-family: 'Orbitron', sans-serif;
            font-weight: 600;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            border: none;
            box-shadow: 0 0 15px rgba(0, 221, 235, 0.4);
            transition: transform 0.2s ease, box-shadow 0.3s ease;
        }

        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 25px rgba(0, 221, 235, 0.7);
        }

        /* Summary Boxes */
        .summary-box {
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            color: white;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.2s ease;
        }

        .summary-box:hover {
            transform: translateY(-2px);
        }

        .match-box {
            box-shadow: 0 0 15px rgba(34, 197, 94, 0.5);
        }

        .diff-box {
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.5);
        }

        /* Expander and Columns */
        .stExpander, .stColumn {
            background: rgba(45, 55, 72, 0.9);
            border-radius: 10px;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stExpanderHeader {
            color: #0088aa !important;
            font-weight: 600 !important;
        }

        /* Expander content (Matching Codes) */
        .stExpander div[data-testid="stMarkdownContainer"] p {
            color: #ffffff !important;
        }

        /* Download Links */
        a {
            color: #00ddeb !important;
            text-decoration: none !important;
            font-weight: 500;
        }

        a:hover {
            color: #67e8f9 !important;
            text-decoration: underline !important;
        }

        /* Results section for scrolling */
        #results-section {
            scroll-margin-top: 20px; /* Ensure smooth scrolling with offset */
        }

        /* Scroll Prompt Styling */
        .scroll-prompt {
            background: rgba(0, 221, 235, 0.2);
            border: 1px solid #00ddeb;
            border-radius: 8px;
            padding: 0.75rem;
            margin: 0.5rem 0;
            color: #e0e7ff;
            font-weight: 500;
            text-align: center;
            box-shadow: 0 0 10px rgba(0, 221, 235, 0.3);
            font-size: 0.9rem;
        }

        .scroll-prompt a {
            color: #67e8f9 !important;
            font-weight: 600;
            text-decoration: underline;
        }

        .scroll-prompt a:hover {
            color: #ffffff !important;
        }
    </style>

    <!-- JavaScript to dynamically apply styles to file uploader elements -->
    <script>
        // Function to apply styles to file uploader elements
        function applyFileUploaderStyles() {
            // Target the "Drag and drop file here" and "Limit 200MB per file..." text
            const dropzoneElements = document.querySelectorAll('div[data-testid="stFileDropzone"] span');
            dropzoneElements.forEach(element => {
                element.style.color = '#ff4d4f'; // Set to white
                element.style.fontWeight = '500';
                element.style.fontSize = '0.9rem';
                element.style.opacity = '1';
            });

            // Target the "Browse files" button text
            const browseButtons = document.querySelectorAll('div[data-testid="stFileUploader"] button');
            browseButtons.forEach(button => {
                button.style.color = '#ff4d4f'; // Set to white
                button.style.background = '#60a5fa';
                button.style.borderRadius = '8px';
                button.style.padding = '0.4rem 0.8rem';
                button.style.fontWeight = '600';
                button.style.fontSize = '0.9rem';
                button.style.border = 'none';
                button.style.opacity = '1';
            });
        }

        // Use MutationObserver to detect when the file uploader elements are added to the DOM
        const observer = new MutationObserver((mutations, obs) => {
            const dropzone = document.querySelector('div[data-testid="stFileDropzone"]');
            if (dropzone) {
                applyFileUploaderStyles();
                obs.disconnect(); // Stop observing once the styles are applied
            }
        });

        // Start observing the document body for changes
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Also try applying styles immediately in case the elements are already loaded
        document.addEventListener('DOMContentLoaded', applyFileUploaderStyles);
    </script>
    """,
    unsafe_allow_html=True
)

# --- App Title ---
st.title("🔍 Seamaster Manifest Match")
st.write("Compare codes between two files (CSV, XLS, XLSX, TXT, PDF, or images) with ease.")

# --- Helper Functions ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return pd.DataFrame([[line.strip()] for line in text.splitlines() if line.strip()], columns=["Code"])

def extract_text_from_image(uploaded_file):
    img = Image.open(uploaded_file)
    text = pytesseract.image_to_string(img)
    return pd.DataFrame([[line.strip()] for line in text.splitlines() if line.strip()], columns=["Code"])

def load_file(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif name.endswith((".png", ".jpg", ".jpeg")):
        return extract_text_from_image(uploaded_file)
    elif name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith(".txt"):
        return pd.read_csv(uploaded_file, delimiter="\t", header=None)
    else:
        return pd.read_excel(uploaded_file)

def get_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'

# --- State to Track Comparison ---
if 'comparison_done' not in st.session_state:
    st.session_state.comparison_done = False

# --- Placeholder for Scroll Prompt ---
prompt_placeholder = st.empty()

# --- Upload Section ---
st.markdown("### 📍 Upload Files")
col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("📁 Upload Seamaster Report", type=["csv", "xls", "xlsx", "txt", "pdf", "png", "jpg", "jpeg"])
with col2:
    file2 = st.file_uploader("🚚 Upload Transporter Report", type=["csv", "xls", "xlsx", "txt", "pdf", "png", "jpg", "jpeg"])

# --- Comparison Logic ---
if file1 and file2:
    if st.button("Compare Files"):
        with st.spinner("Processing files..."):
            try:
                df1 = load_file(file1)
                df2 = load_file(file2)

                list1 = df1.astype(str).stack().str.strip().unique()
                list2 = df2.astype(str).stack().str.strip().unique()

                set1, set2 = set(list1), set(list2)
                matches = sorted(set1 & set2)
                only_in_1 = set1 - set2
                only_in_2 = set2 - set1

                # Set comparison done flag
                st.session_state.comparison_done = True

                # Update the placeholder with the scroll prompt
                with prompt_placeholder.container():
                    st.markdown(
                        """
                        <div class="scroll-prompt">
                            🎉 Comparison complete! Please scroll down to view the results, or 
                            <a href="#results-section">click here to jump to the results</a>.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # --- Summary ---
                st.markdown('<div id="results-section"></div>', unsafe_allow_html=True)  # Anchor for scrolling
                st.markdown("### 📊 Results")
                st.markdown(
                    f'<div class="summary-box match-box"><strong>Total Matches:</strong> {len(matches)}</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="summary-box diff-box"><strong>Only in Seamaster:</strong> {len(only_in_1)}</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="summary-box diff-box"><strong>Only in Transporter:</strong> {len(only_in_2)}</div>',
                    unsafe_allow_html=True
                )

                # --- Detailed Results ---
                with st.expander("✅ Matching Codes", expanded=False):
                    st.write(matches)
                    if matches:
                        df_matches = pd.DataFrame(matches, columns=["Matching Codes"])
                        st.markdown(get_download_link(df_matches, "matches.csv"), unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("❌ Seamaster Report Only")
                    st.write(sorted(only_in_1) if only_in_1 else "✅ No differences")
                    if only_in_1:
                        df_only1 = pd.DataFrame(sorted(only_in_1), columns=["Seamaster Report Only"])
                        st.markdown(get_download_link(df_only1, "seamaster_only.csv"), unsafe_allow_html=True)

                with col2:
                    st.subheader("❌ Transporter Report Only")
                    st.write(sorted(only_in_2) if only_in_2 else "✅ No differences")
                    if only_in_2:
                        df_only2 = pd.DataFrame(sorted(only_in_2), columns=["Transporter Report Only"])
                        st.markdown(get_download_link(df_only2, "transporter_only.csv"), unsafe_allow_html=True)

            except Exception as e:
                st.error(f"🚨 Error: {str(e)}. Please check file formats and try again.")
else:
    st.info("Please upload both files to start the comparison.")

# --- Ensure Prompt Persists After Re-render ---
if st.session_state.comparison_done:
    with prompt_placeholder.container():
        st.markdown(
            """
            <div class="scroll-prompt">
                🎉 Comparison complete! Please scroll down to view the results, or 
                <a href="#results-section">click here to jump to the results</a>.
            </div>
            """,
            unsafe_allow_html=True
        )
        # --- HIDE STREAMLIT DEFAULTS ---
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_link__qRIco {display: none;} /* Hides the deploy button badge */
    .css-18ni7ap.e8zbici2 {display: none;} /* Hides the top space with deploy icon */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)