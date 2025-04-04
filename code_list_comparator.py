import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

# --- Page setup ---
st.set_page_config(
    page_title="Code List Comparator | Seamaster",
    page_icon="🌊",
    layout="wide"
)

# --- App Title ---
st.title("Seamaster Maritime & Logistics — Code List Comparator")
st.markdown("Upload any two files (CSV, XLS, XLSX, TXT, PDF) to detect matching and non-matching codes.")

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
file1 = st.file_uploader("📁 Upload Code List 1", type=["csv", "xls", "xlsx", "txt", "pdf"])
file2 = st.file_uploader("📁 Upload Code List 2", type=["csv", "xls", "xlsx", "txt", "pdf"])

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
        st.markdown(f"❌ **Codes in File 1 but not File 2:** {len(only_in_1)}")
        st.markdown(f"❌ **Codes in File 2 but not File 1:** {len(only_in_2)}")

        with st.expander("✅ View Matching Codes"):
            st.write(matches)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("❌ In File 1 but not in File 2")
            st.write(only_in_1 if only_in_1 else "✅ No differences")

        with col2:
            st.subheader("❌ In File 2 but not in File 1")
            st.write(only_in_2 if only_in_2 else "✅ No differences")

    except Exception as e:
        st.error(f"🚨 Error processing files: {e}")
