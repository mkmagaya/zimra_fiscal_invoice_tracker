# ZIMRA Invoice Verification Tool

## Overview
This Streamlit application verifies ZIMRA FDMS invoices using the official invoice verification portal.  
It supports **bulk verification via Excel upload** and **single invoice verification via URL**.

The system automatically classifies invoices as:

- ✅ **VALID**
- ❌ **INVALID** (with validation error messages)
- ⚠️ **ERROR** (network or unexpected page structure)

---

## Features
- Bulk invoice verification from Excel
- Single invoice verification via URL
- Automatic detection of valid and invalid invoices
- Extraction of validation error comments (where applicable)
- Progress bar for large uploads
- Flexible Excel format support
- Summary counts for results

---

## Supported Input Methods

### 1. Upload Excel File
Upload any Excel file (`.xlsx` or `.xls`) containing invoice verification URLs.

### 2. Insert Single Link
Paste a single ZIMRA FDMS verification URL to verify one invoice.

---

## ⚠️ Important Upload Requirements (READ BEFORE UPLOADING)

To ensure successful processing, your Excel file **must meet the following minimum requirements**:

### ✅ Required Column
Your document **must contain a column named**:

- Column name is **case-insensitive**
- Leading/trailing spaces are ignored
- Column order does **not** matter

**Examples that work:**
- `Verification Url`
- `verification url`
- `VERIFICATION URL`

---

### ❌ Common Causes of Errors
- Missing **Verification Url** column
- Empty cells in the Verification Url column
- Invalid or incomplete URLs (missing `https://`)
- Header rows duplicated as data
- Non-URL text in the Verification Url column

---

### ✔ Best Practices
- Ensure each row contains **one complete ZIMRA verification link**
- Avoid merged cells
- Avoid formulas in the Verification Url column
- Keep data clean and consistent
- Remove blank rows before uploading

---

## Output Explanation

| Column         | Description |
|---------------|-------------|
| Status        | Invoice status: `VALID`, `INVALID`, or `ERROR` |
| Invoice Number| Extracted invoice number (when available) |
| Comment       | Validation error or status message |

---

## Technical Stack
- Python
- Streamlit
- Pandas
- Requests
- BeautifulSoup4

---

## Disclaimer
This tool scrapes publicly available invoice verification pages.  
Users are responsible for complying with ZIMRA policies and applicable laws.

---

## Future Enhancements
- Export results to Excel
- Retry mechanism for failed requests
- Rate-limit protection
- Parallel processing for large uploads
- Summary charts and analytics

