from psrv_generator import generate_psrv

invoice_data = {
    "invoice_number": "INV-SA-26/27-011",
    "invoice_date": "13/04/2026",
    "po_number": "7000029799",
    "gstin": "24AAACM0829Q3Z8",
    "grand_total": "28137.10",

    "materials": [
        {
            "code": "MA2G1006000",
            "description": "PRO-DL30 DIGITAL SPIRIT LEVEL",
            "qty": "1",
            "hsn": "90318000",
            "amount": "2470.00",
            "cgst_amount": "222.30",
            "sgst_amount": "222.30"
        },
        {
            "code": "MA8MG003000",
            "description": "CUSTOM RACK SHELF NILKAMAL LIMITED",
            "qty": "3",
            "hsn": "94032090",
            "amount": "21375.00",
            "cgst_amount": "1923.75",
            "sgst_amount": "1923.75"
        }
    ]
}

eway_data = {
    "eway_bill_no": "652116733941"
}

generate_psrv(
    invoice_data=invoice_data,
    eway_data=eway_data,
    template_path="templates/PSRV Format.xlsx",
    output_path="output/Generated_PSRV.xlsx"
)

print("Done")