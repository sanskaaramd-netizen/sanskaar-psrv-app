import streamlit as st
import os

from invoice_parser import extract_invoice_data
from eway_parser import extract_eway_data
from psrv_generator import generate_psrv


st.title("PSRV One-Click Generator")

invoice_file = st.file_uploader(
    "Upload Invoice PDF",
    type=["pdf"]
)

eway_file = st.file_uploader(
    "Upload E-Way Bill PDF",
    type=["pdf"]
)


if st.button("Generate PSRV"):

    if not invoice_file or not eway_file:

        st.error(
            "Please upload both PDFs."
        )

    else:

        # ==========================
        # Save Uploaded Files
        # ==========================
        invoice_path = os.path.join(
            "INVOICES",
            invoice_file.name
        )

        eway_path = os.path.join(
            "INVOICES",
            eway_file.name
        )

        with open(invoice_path, "wb") as f:
            f.write(invoice_file.getbuffer())

        with open(eway_path, "wb") as f:
            f.write(eway_file.getbuffer())

        # ==========================
        # Extract Data
        # ==========================
        invoice_data = extract_invoice_data(
            invoice_path
        )

        eway_data = extract_eway_data(
            eway_path
        )

        # ==========================
        # Output File
        # ==========================
        output_path = os.path.join(
            "OUTPUT",
            "Generated_PSRV.xlsx"
        )

        # ==========================
        # Generate PSRV
        # ==========================
        generate_psrv(
            invoice_data=invoice_data,
            eway_data=eway_data,
            template_path="templates/PSRV Format.xlsx",
            output_path=output_path
        )

        st.success(
            "PSRV Generated Successfully!"
        )

        # ==========================
        # Download Button
        # ==========================
        with open(output_path, "rb") as file:

            st.download_button(
                label="Download PSRV",
                data=file,
                file_name="Generated_PSRV.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
