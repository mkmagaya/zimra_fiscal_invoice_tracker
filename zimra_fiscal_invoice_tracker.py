import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib3.exceptions import ConnectTimeoutError
import time

# Function to scrape data from a single URL
def scrape_data(url):
    try:
        # Send HTTP request
        response = requests.get(url, timeout=10)  # Set timeout for the request
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract specific fields
            header_text = soup.find('div', class_='header-text').text.strip()
            
            if "Invoice is valid" in header_text:
                return None, None  # Return None for both invoice and comment
            else:
                invoice_number = soup.find('div', class_='invoice-number-box').find('div', class_='result-text-2').text.strip()
                comment = soup.find('div', class_='mb-2').text.strip()
                return invoice_number, comment
        else:
            st.warning(f"Failed to fetch data from {url}. Status code: {response.status_code}")
            return None, None
    except ConnectTimeoutError:
        st.error(f"Connection to {url} timed out. Please check your internet connection and try again.")
        return None, None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None, None

# Streamlit app
def streamlit_app():
    st.title("Zimra Invoice Verifier")
    timeout_error_shown = False
    last_timeout_timestamp = 0
    
    option = st.radio("Select Input Option:", ["Upload Excel File", "Insert Single Link"])
    
    if option == "Upload Excel File":
        # Upload Excel file
        uploaded_file = st.file_uploader("Upload Excel file")
        
        if uploaded_file is not None:
            try:
                # Read data from Excel file into DataFrame without headers
                df = pd.read_excel(uploaded_file, header=None)
                
                # Assign default header row headings
                headers = [
                    "Document Type", "Document No.", "Date Time", "Fiscal Day No.", "Fiscal Day Status", 
                    "Fiscal Day Sysnchronised", "Global Receipt No.", "Receipt Counter", "Currency Code", 
                    "Document Amount", "User ID", "FDMS Status", "Verification Url", "FDMS Receipt ID", 
                    "FDMS Server Date", "FDMS Operation ID"
                ]
                df.columns = headers
                
                invalid_invoices = []
                comments = []
                
                # Iterate over rows and scrape data from Verification Url column
                for index, row in df.iterrows():
                    verification_url = row["Verification Url"]  # Assuming the column name is "Verification Url"
                    invoice_number, comment = scrape_data(verification_url)
                    if invoice_number is not None:
                        invalid_invoices.append(invoice_number)
                        comments.append(comment)
                
                # Display invalid invoices with corresponding comments in a table
                st.subheader("Invalid Invoices:")
                data = {"Invoice Number": invalid_invoices, "Comment": comments}
                invalid_df = pd.DataFrame(data)
                st.table(invalid_df)
            except Exception as e:
                st.error(f"An error occurred while processing the file: {str(e)}")
                if isinstance(e, ConnectTimeoutError) and not timeout_error_shown:
                    st.error(f"Connection timeout error. Please check your internet connection and try again.")
                    timeout_error_shown = True
    
    elif option == "Insert Single Link":
        # Insert single link
        url = st.text_input("Enter URL:")
        
        if st.button("Verify"):
            try:
                if url:
                    invoice_number, comment = scrape_data(url)
                    if invoice_number is not None:
                        # Display result in a table
                        data = {"Invoice Number": [invoice_number], "Comment": [comment]}
                        result_df = pd.DataFrame(data)
                        st.table(result_df)
                    else:
                        st.info("Invoice is valid.")
            except ConnectTimeoutError:
                if not timeout_error_shown:
                    st.error(f"Connection to {url} timed out. Please check your internet connection and try again.")
                    timeout_error_shown = True
                    last_timeout_timestamp = time.time()
                else:
                    current_timestamp = time.time()
                    # Wait for 5 seconds before allowing another attempt
                    if current_timestamp - last_timeout_timestamp < 5:
                        st.warning("Waiting for connection...")
                        time.sleep(5 - (current_timestamp - last_timeout_timestamp))
            except Exception as e:
                st.error(f"An error occurred while processing the link: {str(e)}")

if __name__ == "__main__":
    streamlit_app()
