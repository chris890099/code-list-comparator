import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from io import StringIO

# --- PAGE SETTINGS ---
st.set_page_config(
    page_title="Seamaster Code Comparator",
    page_icon="🔎",
    layout="centered"
)

# --- CUSTOM BACKGROUND & LOGO ---
st.markdown(
    """
    <style>
    body {
        background-color: #f0f7ff;
        background-image: linear-gradient(to right, #d0e6ff, #f0f7ff);
    }
    .stApp {
        padding-top: 30px;
    }
    header, footer, .viewerBadge_container__1QSob, .stDeployButton {
        visibility: hidden;
    }
    #MainMenu {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- LOGO AND TITLE ---
st.image("logomark.png", width=120)
st.markdown(
    "<h1 style='color:#003366;'>Seamaster Maritime & Logistics — Code List Comparator</h1>",
    unsafe_allow_html=True
)
st.markdown("Upload any two files (CSV, XLS, XLSX, TXT, PDF) to detect matching and non-matching codes.")

# --- FUNCTION TO EXTRACT TEXT FROM PDF ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return pd.DataFrame([line.strip() for line in text.splitlines() if line.strip()], columns=["Code"])

# --- LOAD FILES ---
def load_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".txt"):
        return pd.read_csv(uploaded_file, delimiter="\t", header=None)
    else:
        return pd.read_excel(uploaded_file)

# --- FILE UPLOADERS ---
st.markdown("### 📂 Upload Code List 1")
file1 = st.file_uploader("Upload Code List 1", type=["csv", "xls", "xlsx", "txt", "pdf"])

st.markdown("### 📂 Upload Code List 2")
file2 = st.file_uploader("Upload Code List 2", type=["csv", "xls", "xlsx", "txt", "pdf"])

# --- PROCESS FILES ---
if file1 and file2:
    try:
        df1 = load_file(file1)
        df2 = load_file(file2)

        list1 = df1.astype(str).stack().str.strip().unique()
        list2 = df2.astype(str).stack().str.strip().unique()

        matches = sorted(set(list1).intersection(set(list2)))
        missing_in_2 = sorted(set(list1) - set(list2))
        missing_in_1 = sorted(set(list2) - set(list1))

        st.markdown("## 🔍 Comparison Results")

        st.write(f"✅ Total Matches: **{len(matches)}**")
        st.write(matches if matches else "No matches found.")

        st.write(f"❌ Total Missing in Code List 2: **{len(missing_in_2)}**")
        st.write(missing_in_2 if missing_in_2 else "✅ No differences.")

        st.write(f"❌ Total Missing in Code List 1: **{len(missing_in_1)}**")
        st.write(missing_in_1 if missing_in_1 else "✅ No differences.")

    except Exception as e:
        st.error(f"Error processing files: {e}")
