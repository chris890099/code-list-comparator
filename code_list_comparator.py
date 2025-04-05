import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

# --- Page Setup ---
st.set_page_config(
    page_title="Code List Comparator | Seamaster",
    page_icon="🌊",
    layout="wide"
)

# --- Consistent Dark Mode UI Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b1d2c !important;
        color: white !important;
    }

    .stApp {
        background-color: #0b1d2c;
        color: white;
    }

    h1, h2, h3, h4, h5, h6, p, label, span {
        color: white !important;
    }

    .block-container {
        padding: 2rem 3rem;
        background-color: #122a3f;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }

    .stFileUploader {
        background-color: #1d3557 !important;
        border: 2px dashed #4fc3f7;
        border-radius: 12px;
        padding: 1rem;
        color: white !important;
    }

    .stButton>button {
        background-color: #2196f3 !important;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
    }

    .stButton>button:hover {
        background-color: #1976d2 !important;
    }

    .st-expander {
        background-color: #1a2635 !important;
        color: white !important;
    }

    footer, header, #MainMenu {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("🔍 Seamaster Code List Comparator")
st.write("Upload two files (CSV, XLS, XLSX, TXT, PDF) to compare and find matching and non-matching codes.")

# --- File Parsing ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return pd.DataFrame([[line.strip()] for line in text.splitlines() if line.strip()], columns=["Code"])

def load_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".txt"):
        return pd.read_csv(uploaded_file, delimiter="\t", header=None)
    else:
        return pd.read_excel(uploaded_file)

# --- Upload Section ---
st.markdown("### 📂 Upload Files")
file1 = st.file_uploader("🗂️ Upload Seamaster Report", type=["csv", "xls", "xlsx", "txt", "pdf"])
file2 = st.file_uploader("🚚 Upload Trucker Report", type=["csv", "xls", "xlsx", "txt", "pdf"])

# --- Comparison ---
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

        st.markdown("### 📊 Summary")
        st.success(f"✅ **Total Matches:** {len(matches)}")
        st.error(f"❌ **Only in Seamaster Report:** {len(only_in_1)}")
        st.error(f"❌ **Only in Transporter Report:** {len(only_in_2)}")

        with st.expander("✅ Matching Codes"):
            st.write(matches)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("❌ In Seamaster Report Only")
            st.write(only_in_1 if only_in_1 else "✅ No differences")

        with col2:
            st.subheader("❌ In Transporter Report Only")
            st.write(only_in_2 if only_in_2 else "✅ No differences")

    except Exception as e:
        st.error(f"🚨 Error processing files: {e}")
