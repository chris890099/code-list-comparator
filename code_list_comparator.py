import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image

# --- Page setup ---
st.set_page_config(
    page_title="Code List Comparator | Seamaster",
    page_icon="🌊",
    layout="wide"
)

# --- Custom Seamaster Branding + UI ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Open Sans', sans-serif;
        }

        .stApp {
            background: linear-gradient(145deg, #e6f0fa, #f0f6ff);
            background-attachment: fixed;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 4rem;
            padding-right: 4rem;
        }

        h1, h2, h3 {
            color: #003366;
        }

        .stButton>button {
            background-color: #00509e;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1em;
            font-weight: bold;
        }

        .stButton>button:hover {
            background-color: #003f7f;
        }

        [data-testid="stDeploymentStatus"] {
            display: none !important;
        }

        footer, header, #MainMenu {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Logo ---
logo = Image.open("sm logo.png")
st.image(logo, width=300)

# --- App Title ---
st.markdown("## Seamaster Maritime & Logistics — Code List Comparator")
st.markdown("Upload **Seamaster Records** and **Transporter Records** (CSV, XLSX, TXT, PDF) to compare and highlight matches & differences.")

# --- PDF extractor ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return pd.DataFrame([[line.strip()] for line in text.splitlines() if line.strip()], columns=["Code"])

# --- File loader ---
def load_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".txt"):
        return pd.read_csv(uploaded_file, delimiter="\t", header=None)
    else:
        return pd.read_excel(uploaded_file)

# --- Uploaders ---
file1 = st.file_uploader("📁 Upload Seamaster Records", type=["csv", "xls", "xlsx", "txt", "pdf"])
file2 = st.file_uploader("📁 Upload Transporter Records", type=["csv", "xls", "xlsx", "txt", "pdf"])

# --- Comparison Logic ---
if file1 and file2:
    try:
        df1 = load_file(file1)
        df2 = load_file(file2)

        list1 = df1.astype(str).stack().str.strip().unique()
        list2 = df2.astype(str).stack().str.strip().unique()

        set1, set2 = set(list1), set(list2)

        matches = sorted(set1 & set2)
        only_in_1 = sorted(set1 - set2)
        only_in_2 = sorted(set2 - set1)

        st.subheader("📊 Summary")
        st.markdown(f"✅ **Total Matches:** {len(matches)}")
        st.markdown(f"❌ **In Seamaster Records only:** {len(only_in_1)}")
        st.markdown(f"❌ **In Transporter Records only:** {len(only_in_2)}")

        with st.expander("✅ View Matching Codes"):
            st.write(matches)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("❌ In Seamaster Records only")
            st.write(only_in_1 if only_in_1 else "✅ No differences")

        with col2:
            st.subheader("❌ In Transporter Records only")
            st.write(only_in_2 if only_in_2 else "✅ No differences")

    except Exception as e:
        st.error(f"🚨 Error processing files: {e}")
