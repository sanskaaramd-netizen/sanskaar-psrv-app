import pdfplumber
import re


def extract_invoice_data(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    data = {
        "invoice_number": "",
        "invoice_date": "",
        "po_number": "",
        "gstin": "",
        "grand_total": "",
        "materials": []
    }

    inv = re.search(r"#\s*:\s*(INV-[A-Z]+-\d+/\d+-\d+)", text)
    if inv:
        data["invoice_number"] = inv.group(1)

    date = re.search(r"Invoice Date\s*:\s*(\d{2}/\d{2}/\d{4})", text)
    if date:
        data["invoice_date"] = date.group(1)

    po = re.search(r"P\.O\.#\s*:\s*(\d+)", text)
    if po:
        data["po_number"] = po.group(1)

    gstins = re.findall(r"GSTIN[:\s]+([0-9A-Z]{15})", text)
    if gstins:
        data["gstin"] = gstins[-1]

    total = re.search(r"Total\s*₹?([\d,]+\.\d{2})", text)
    if total:
        data["grand_total"] = total.group(1).replace(",", "")

    lines = text.split("\n")

    for i, line in enumerate(lines):
        line = line.strip()

        match = re.match(
            r"^\d+\s+([A-Z0-9]+)\/\s+(.*?)\s+(\d{7,8})\s+(\d+\.\d+)\s+([\d,]+\.\d{2})\s+(\d+)%\s+([\d,]+\.\d{2})\s+(\d+)%\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})",
            line
        )

        if match:
            code = match.group(1)
            desc = match.group(2)
            hsn = match.group(3)
            qty = str(int(float(match.group(4))))
            rate = match.group(5).replace(",", "")
            cgst_percent = match.group(6)
            cgst_amount = match.group(7).replace(",", "")
            sgst_percent = match.group(8)
            sgst_amount = match.group(9).replace(",", "")
            amount = match.group(10).replace(",", "")

            extra_desc = []

            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()

                if re.match(r"^\d+\s+[A-Z0-9]+\/", next_line):
                    break

                if "Sub Total" in next_line:
                    break

                if next_line and not re.match(r"^\d+\s+pcs$", next_line):
                    extra_desc.append(next_line)

                j += 1

            full_desc = desc + " " + " ".join(extra_desc)

            data["materials"].append({
                "code": code,
                "description": full_desc.strip(),
                "hsn": hsn,
                "qty": qty,
                "rate": rate,
                "amount": amount,
                "cgst_percent": cgst_percent,
                "cgst_amount": cgst_amount,
                "sgst_percent": sgst_percent,
                "sgst_amount": sgst_amount
            })

    return data