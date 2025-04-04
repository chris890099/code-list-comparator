import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import base64
from PIL import Image
from io import BytesIO

# --- Streamlit Config ---
st.set_page_config(
    page_title="Code List Comparator | Seamaster",
    page_icon="🌊",
    layout="wide"
)

# --- Custom Styles ---
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Open Sans', sans-serif;
        }}

        .stApp {{
            background: linear-gradient(135deg, #f0f6ff, #e6f0fa);
            background-attachment: fixed;
        }}

        .block-container {{
            padding-top: 3rem;
            padding-bottom: 3rem;
            padding-left: 4rem;
            padding-right: 4rem;
        }}

        .stButton>button {{
            background-color: #004080;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1.5em;
            font-weight: bold;
        }}

        .stButton>button:hover {{
            background-color: #00264d;
        }}

        .stFileUploader label {{
            font-weight: 600;
            font-size: 1rem;
            color: #003366;
        }}

        [data-testid="stDeploymentStatus"] {{
            display: none !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- App Title ---
st.markdown("## 🚢 Seamaster Code Comparison Tool")
st.markdown("Upload **Seamaster records** and **Transporter records** to compare unique and overlapping codes.")

# --- PDF Extractor ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return pd.DataFrame([[line.strip()] for line in text.splitlines() if line.strip()], columns=["Code"])

# --- File Loader ---
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
file1 = st.file_uploader("📁 Seamaster Records", type=["csv", "xls", "xlsx", "txt", "pdf"])
file2 = st.file_uploader("📁 Transporter Records", type=["csv", "xls", "xlsx", "txt", "pdf"])

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

        st.markdown("---")
        st.subheader("📊 Comparison Summary")
        st.markdown(f"✅ **Matches:** {len(matches)}")
        st.markdown(f"⚠️ **Only in Seamaster Records:** {len(only_in_1)}")
        st.markdown(f"⚠️ **Only in Transporter Records:** {len(only_in_2)}")

        with st.expander("✅ View Matching Codes"):
            st.write(matches)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🧾 Seamaster Only")
            st.write(only_in_1 if only_in_1 else "✅ No unique codes")

        with col2:
            st.subheader("🧾 Transporter Only")
            st.write(only_in_2 if only_in_2 else "✅ No unique codes")

    except Exception as e:
        st.error(f"🚨 Error processing files: {e}")
else:
    # --- Loading Placeholder with Animated Gradient Banner ---
    img_placeholder = """
    <div style="margin-top: 3rem; text-align: center;">
        <img src="data:image/png;base64,{}" width="500" alt="Loading trucks and ships animation" style="border-radius: 16px; box-shadow: 0 0 12px rgba(0,0,0,0.15);"/>
        <p style="color:#00509e;font-weight:500;margin-top:1rem;">Waiting for file upload...</p>
    </div>
    """.format(base64.b64encode(Image.new("RGB", (800, 200), color=(3, 78, 129)).tobytes()).decode('utf-8'))

    st.markdown(img_placeholder, unsafe_allow_html=True)
