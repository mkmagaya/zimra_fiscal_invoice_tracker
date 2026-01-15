import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
import time


# ---------------------------------------------------
# Function to scrape data from a single URL
# ---------------------------------------------------
def scrape_data(url):
    try:
        if not isinstance(url, str) or not url.strip():
            return None, None, None

        url = url.strip()

        if url.lower() == "verification url":
            return None, None, None

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return "ERROR", None, f"HTTP {response.status_code}"

        soup = BeautifulSoup(response.content, "html.parser")

        # -------------------------------
        # Determine status
        # -------------------------------
        header_div = soup.find("div", class_="header-text")
        if not header_div:
            return "ERROR", None, "Missing status header"

        header_text = header_div.text.strip().lower()

        status = "VALID" if "invoice is valid" in header_text else "INVALID"

        # -------------------------------
        # Invoice Number (exists for both)
        # -------------------------------
        invoice_number = None
        labels = soup.find_all("label")

        for label in labels:
            if label.text.strip() == "INVOICE NUMBER":
                invoice_number = label.find_next("div", class_="result-text").text.strip()
                break

        # -------------------------------
        # Validation errors (INVALID only)
        # -------------------------------
        comment = None
        if status == "INVALID":
            errors_block = soup.find("div", class_="val-errors-block")
            if errors_block:
                errors = [e.text.strip() for e in errors_block.find_all("div", class_="col")]
                comment = "; ".join(errors)
            else:
                comment = "Invoice is not valid"

        return status, invoice_number, comment

    except requests.exceptions.Timeout:
        return "ERROR", None, "Connection timed out"
    except Exception as e:
        return "ERROR", None, str(e)


# ---------------------------------------------------
# Streamlit App
# ---------------------------------------------------
def streamlit_app():
    st.set_page_config(page_title="ZIMRA Invoice Verifier", layout="centered")
    st.title("ZIMRA Invoice Verifier")

    option = st.radio(
        "Select Input Option:",
        ["Upload Excel File", "Insert Single Link"]
    )

    # ---------------------------------------------------
    # Upload Excel File
    # ---------------------------------------------------
    if option == "Upload Excel File":
        uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    #     if uploaded_file:
    #         try:
    #             df = pd.read_excel(uploaded_file, header=None)

    #             headers = [
    #                 "Document Type", "Document No.", "Date Time", "Fiscal Day No.",
    #                 "Fiscal Day Status", "Fiscal Day Synchronized", "Global Receipt No.",
    #                 "Receipt Counter", "Currency Code", "Creation Date", "Document Amount", "User ID",
    #                 "FDMS Status", "Verification Url", "FDMS Receipt ID",
    #                 "FDMS Server Date", "Error Code", "FDMS Operation ID",
    #             ]
    #             df.columns = headers

    #             results = []

    #             total_rows = len(df)
    #             progress_bar = st.progress(0)
    #             status_text = st.empty()

    #             for i, row in df.iterrows():
    #                 verification_url = row["Verification Url"]

    #                 status, invoice_number, comment = scrape_data(verification_url)

    #                 if status:
    #                     results.append({
    #                         "Status": status,
    #                         "Invoice Number": invoice_number,
    #                         "Comment": comment
    #                     })

    #                 progress = int(((i + 1) / total_rows) * 100)
    #                 progress_bar.progress(progress)
    #                 status_text.text(f"Processing {i + 1} of {total_rows} invoices...")

    #                 time.sleep(0.1)

    #             progress_bar.empty()
    #             status_text.empty()

    #             results_df = pd.DataFrame(results)

    #             st.subheader("Invoice Verification Results")
    #             st.dataframe(results_df, use_container_width=True)

    #             # Summary
    #             st.markdown("### Summary")
    #             st.write(results_df["Status"].value_counts())

    #         except Exception as e:
    #             st.error(f"Error processing file: {str(e)}")

    # ---------------------------------------------------
    # Flexible upload file handling
    # ---------------------------------------------------
        if uploaded_file:
            try:
                # Read Excel with automatic headers
                df = pd.read_excel(uploaded_file)

                # List of critical columns we require
                critical_columns = ["Verification Url"]

                # Check if critical columns exist
                missing_columns = [col for col in critical_columns if col not in df.columns]
                if missing_columns:
                    st.error(f"Missing critical columns: {', '.join(missing_columns)}")
                else:
                    results = []

                    total_rows = len(df)
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, row in df.iterrows():
                        verification_url = row["Verification Url"]

                        status, invoice_number, comment = scrape_data(verification_url)

                        if status:
                            results.append({
                                "Status": status,
                                "Invoice Number": invoice_number,
                                "Comment": comment
                            })

                        # Update progress
                        progress = int(((i + 1) / total_rows) * 100)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing {i + 1} of {total_rows} invoices...")

                        time.sleep(0.1)

                    progress_bar.empty()
                    status_text.empty()

                    results_df = pd.DataFrame(results)

                    st.subheader("Invoice Verification Results")
                    st.dataframe(results_df, use_container_width=True)

                    # Summary
                    st.markdown("### Summary")
                    st.write(results_df["Status"].value_counts())

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

    # ---------------------------------------------------
    # Insert Single Link
    # ---------------------------------------------------
    else:
        url = st.text_input("Enter Verification URL")

        if st.button("Verify"):
            with st.spinner("Verifying invoice..."):
                status, invoice_number, comment = scrape_data(url)

            if status == "VALID":
                st.success("Invoice is valid ✅")
            elif status == "INVALID":
                st.error("Invoice is NOT valid ❌")
                st.table(pd.DataFrame({
                    "Invoice Number": [invoice_number],
                    "Comment": [comment]
                }))
            else:
                st.warning(comment)


# ---------------------------------------------------
# Run App
# ---------------------------------------------------
if __name__ == "__main__":
    streamlit_app()
