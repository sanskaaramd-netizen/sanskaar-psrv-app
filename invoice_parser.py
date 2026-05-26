import pdfplumber
import re


def clean_amount(value):
    return value.replace(",", "").strip()


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

    # Invoice Number
    match = re.search(r"#\s*:\s*(INV-[A-Z]+-\d+/\d+-\d+)", text)
    if match:
        data["invoice_number"] = match.group(1)

    # Invoice Date
    match = re.search(r"Invoice Date\s*:\s*(\d{2}/\d{2}/\d{4})", text)
    if match:
        data["invoice_date"] = match.group(1)

    # PO Number
    match = re.search(r"P\.O\.#\s*:\s*(\d+)", text)
    if match:
        data["po_number"] = match.group(1)

    # GSTIN - take buyer/Maruti GSTIN if present
    gstins = re.findall(r"GSTIN[:\s]+([0-9A-Z]{15})", text)
    if gstins:
        data["gstin"] = gstins[-1]

    # Grand Total
    totals = re.findall(r"Total\s*₹?([\d,]+\.\d{2})", text)
    if totals:
        data["grand_total"] = clean_amount(totals[-1])

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    i = 0

    while i < len(lines):
        line = lines[i]

        item_match = re.match(
            r"^(\d+)\s+([A-Z0-9]+)\/\s+(.*)",
            line
        )

        if not item_match:
            i += 1
            continue

        code = item_match.group(2)
        first_desc_part = item_match.group(3)

        # Extract numeric fields from the first item line
        nums = re.findall(r"[\d,]+\.\d{2}|\d+%", line)

        hsn_match = re.search(r"\s(\d{7,8})\s", line)
        hsn = hsn_match.group(1) if hsn_match else ""

        qty = ""
        rate = ""
        cgst_amount = ""
        sgst_amount = ""
        amount = ""

        # Example numeric order:
        # qty, rate, 9%, cgst_amt, 9%, sgst_amt, amount
        normal_numbers = [x for x in nums if "%" not in x]

        if len(normal_numbers) >= 5:
            qty = str(int(float(clean_amount(normal_numbers[0]))))
            rate = clean_amount(normal_numbers[1])
            cgst_amount = clean_amount(normal_numbers[2])
            sgst_amount = clean_amount(normal_numbers[3])
            amount = clean_amount(normal_numbers[4])

        description_parts = []

        # Remove table numbers from first desc
        first_desc_part = re.sub(r"\s+\d{7,8}.*", "", first_desc_part).strip()
        if first_desc_part:
            description_parts.append(first_desc_part)

        j = i + 1

        while j < len(lines):
            next_line = lines[j]

            # Stop when next item starts
            if re.match(r"^\d+\s+[A-Z0-9]+\/", next_line):
                break

            # Stop at invoice totals
            if (
                "Sub Total" in next_line
                or "Total In Words" in next_line
                or "CGST9" in next_line
                or "SGST9" in next_line
                or "Payment Made" in next_line
                or "Balance Due" in next_line
                or "Terms & Conditions" in next_line
                or "Notes" in next_line
            ):
                break

            # Skip unit-only lines like "0 pcs" or "pcs"
            if re.match(r"^\d*\s*pcs$", next_line, re.IGNORECASE):
                j += 1
                continue

            description_parts.append(next_line)

            j += 1

        description = " ".join(description_parts).strip()

        data["materials"].append({
            "code": code,
            "description": description,
            "hsn": hsn,
            "qty": qty,
            "rate": rate,
            "amount": amount,
            "cgst_amount": cgst_amount,
            "sgst_amount": sgst_amount
        })

        i = j

    return data