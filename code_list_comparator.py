import streamlit as st
import pandas as pd
import io

def process_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file, header=None)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(uploaded_file, header=None)
        elif uploaded_file.name.endswith('.txt'):
            return pd.read_csv(uploaded_file, header=None, delimiter='\t')
        else:
            st.error("Unsupported file type. Please upload .csv, .xlsx, or .txt files.")
            return None
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

def compare_codes(df1, df2):
    df1[0] = df1[0].astype(str).str.strip().str.upper()
    df2[0] = df2[0].astype(str).str.strip().str.upper()

    set1 = set(df1[0])
    set2 = set(df2[0])

    matches = set1.intersection(set2)
    only_in_1 = set1 - set2
    only_in_2 = set2 - set1

    result = {
        "Matches": list(matches),
        "Only in List 1": list(only_in_1),
        "Only in List 2": list(only_in_2)
    }
    return result

def generate_download(result):
    output = io.StringIO()
    for category, codes in result.items():
        output.write(f"{category}\n")
        for code in codes:
            output.write(f"{code}\n")
        output.write("\n")
    return output.getvalue()

# UI starts here
st.title("🔍 Compare Code Lists")

st.markdown("Upload two files containing 7-character codes (Excel, CSV, or TXT). Case-insensitive.")

file1 = st.file_uploader("Upload Code List 1", type=["csv", "xls", "xlsx", "txt"])
file2 = st.file_uploader("Upload Code List 2", type=["csv", "xls", "xlsx", "txt"])

if file1 and file2:
    df1 = process_file(file1)
    df2 = process_file(file2)

    if df1 is not None and df2 is not None:
        if st.button("Compare"):
            with st.spinner("Comparing..."):
                result = compare_codes(df1, df2)

            st.success("Comparison complete!")

            for key in result:
                st.subheader(key)
                st.write(result[key])

            # Download button
            download_data = generate_download(result)
            st.download_button("📥 Download Results", download_data, file_name="comparison_results.txt")

