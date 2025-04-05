import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

# --- Page Config ---
st.set_page_config(
    page_title="Code List Comparator | Seamaster",
    page_icon="🌊",
    layout="wide"
)

# --- Custom CSS Styling ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: linear-gradient(to right, #eef5fb, #f9fbfd);
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .block-container {
            padding: 2rem 3rem;
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.06);
            background-color: #ffffff;
        }

        h1, h2, h3, h4 {
            color: #003366;
        }

        .stFileUploader {
            border: 2px dashed #00509e;
            border-radius: 12px;
            padding: 1rem;
            background-color: #f0f6ff;
        }

        .stButton>button {
            background-color: #00509e;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 0.6rem 1.5rem;
        }

        .stButton>button:hover {
            background-color: #003f7f;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- App Title ---
st.title("🔍 Seamaster Code List Comparator")
st.write("Upload two files (CSV, XLS, XLSX, TXT, PDF) to compare and find matching and non-matching codes.")

# --- PDF Extraction ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return pd.DataFrame([[line.strip()] for line in text.splitlines() if line.strip()], columns=["Code"])

# --- Load Any File ---
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
file1 = st.file_uploader("Upload Seamaster Report", type=["csv", "xls", "xlsx", "txt", "pdf"])
file2 = st.file_uploader("Trucker Report", type=["csv", "xls", "xlsx", "txt", "pdf"])

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
        st.error(f"❌ **Only in File 1:** {len(only_in_1)}")
        st.error(f"❌ **Only in File 2:** {len(only_in_2)}")

        with st.expander("✅ Matching Codes"):
            st.write(matches)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("❌ In File 1 Only")
            st.write(only_in_1 if only_in_1 else "✅ No differences")

        with col2:
            st.subheader("❌ In File 2 Only")
            st.write(only_in_2 if only_in_2 else "✅ No differences")

    except Exception as e:
        st.error(f"🚨 Error processing files: {e}")
