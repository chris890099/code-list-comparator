import streamlit as st
import pandas as pd
import fitz  # PyMuPDF for PDF support

# --- Branding & Config ---
st.set_page_config(page_title="Seamaster — Code Comparator", layout="centered", initial_sidebar_state="collapsed")

# --- Custom CSS ---
st.markdown("""
    <style>
        body {
            background-color: #e6f0ff;
        }
        header, footer, .stDeployButton {
            visibility: hidden;
        }
        .stApp {
            padding-top: 40px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Logo ---
st.image("logomark.png", width=120)

# --- Title ---
st.title("Seamaster Maritime & Logistics — Code List Comparator")
st.markdown("Upload any two files (**CSV**, **XLS**, **XLSX**, **TXT**, or **PDF**) to detect matching and non-matching codes.")

# --- PDF Reader ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return pd.DataFrame(lines, columns=["Code"])

# --- Load File Based on Type ---
def load_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".txt"):
        return pd.read_csv(uploaded_file, delimiter="\t", header=None)
    else:
        return pd.read_excel(uploaded_file)

# --- Upload Files ---
st.markdown("📁 **Upload Code List 1**")
file1 = st.file_uploader("", type=["csv", "xls", "xlsx", "txt", "pdf"], key="file1")

st.markdown("📁 **Upload Code List 2**")
file2 = st.file_uploader("", type=["csv", "xls", "xlsx", "txt", "pdf"], key="file2")

# --- Compare Logic ---
if file1 and file2:
    try:
        df1 = load_file(file1)
        df2 = load_file(file2)

        # Flatten both to strings
        list1 = df1.astype(str).stack().str.strip().unique()
        list2 = df2.astype(str).stack().str.strip().unique()

        # Comparison
        matches = sorted(set(list1).intersection(list2))
        only_in_1 = sorted(set(list1) - set(list2))
        only_in_2 = sorted(set(list2) - set(list1))

        st.subheader("🔍 Comparison Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Matches", len(matches))
        col2.metric("❌ In File 1 Only", len(only_in_1))
        col3.metric("❌ In File 2 Only", len(only_in_2))

        with st.expander("View Matching Codes"):
            st.write(matches if matches else "No matches found.")

        with st.expander("Codes in File 1 but not in File 2"):
            st.write(only_in_1 if only_in_1 else "✅ No differences.")

        with st.expander("Codes in File 2 but not in File 1"):
            st.write(only_in_2 if only_in_2 else "✅ No differences.")

    except Exception as e:
        st.error(f"❗ Error processing files: {e}")
