import pdfplumber

with pdfplumber.open("INV-SA-2627-011.pdf") as pdf:
    for page in pdf.pages:
        print(page.extract_text())