import pdfplumber
import re


def extract_invoice_data(pdf_path):

    data = {
        "invoice_number": "",
        "invoice_date": "",
        "po_number": "",
        "gstin": "",
        "materials": []
    }

    full_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # Invoice Number
    match = re.search(r'INV-SA-\d+/\d+-\d+', full_text)
    if match:
        data["invoice_number"] = match.group()

    # Invoice Date
    match = re.search(r'Invoice Date\s*:\s*(\d{2}/\d{2}/\d{4})', full_text)
    if match:
        data["invoice_date"] = match.group(1)

    # PO Number
    match = re.search(r'P\.O\.#\s*:\s*(\d+)', full_text)
    if match:
        data["po_number"] = match.group(1)

    # GSTIN (Maruti GSTIN)
    match = re.search(r'GSTIN[:\s]+([0-9A-Z]{15})', full_text)
    if match:
        data["gstin"] = match.group(1)

    # Material Extraction
    lines = full_text.split("\n")

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        # Material Code Pattern
        code_match = re.match(
            r'^\d+\s+([A-Z0-9]+)\/\s+(.*)',
            line
        )

        if code_match:

            material_code = code_match.group(1)

            description = code_match.group(2)

            qty = ""

            j = i + 1

            while j < len(lines):

                next_line = lines[j].strip()

                # Next item begins
                if re.match(r'^\d+\s+[A-Z0-9]+\/', next_line):
                    break

                # Quantity line
                qty_match = re.search(r'(\d+\.\d+)\s+pcs', next_line)

                if qty_match:
                    qty = str(int(float(qty_match.group(1))))
                    break

                description += " " + next_line

                j += 1

            data["materials"].append(
                {
                    "code": material_code,
                    "description": description.strip(),
                    "qty": qty
                }
            )

            i = j

        else:
            i += 1

    return data
