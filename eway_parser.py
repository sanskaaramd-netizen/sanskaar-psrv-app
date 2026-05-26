import pdfplumber
import re


def extract_eway_data(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    data = {
        "eway_bill_no": ""
    }

    match = re.search(r"E-Way Bill No\.?:\s*(\d+)", text)

    if match:
        data["eway_bill_no"] = match.group(1)

    return data
