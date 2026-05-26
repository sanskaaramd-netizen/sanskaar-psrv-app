import streamlit as st
import os

from invoice_parser import extract_invoice_data
from eway_parser import extract_eway_data
from psrv_generator import generate_psrv


st.title("PSRV One-Click Generator")

invoice_file = st.file_uploader("Upload Invoice PDF", type=["pdf"])
eway_file = st.file_uploader("Upload E-Way Bill PDF", type=["pdf"])

if st.button("Generate PSRV"):

    if not invoice_file or not eway_file:
        st.error("Please upload both Invoice PDF and E-Way Bill PDF.")

    else:
        base_dir = os.getcwd()

        os.makedirs("INVOICES", exist_ok=True)
        os.makedirs("OUTPUT", exist_ok=True)

        invoice_path = os.path.join("INVOICES", invoice_file.name)
        eway_path = os.path.join("INVOICES", eway_file.name)

        with open(invoice_path, "wb") as f:
            f.write(invoice_file.getbuffer())

        with open(eway_path, "wb") as f:
            f.write(eway_file.getbuffer())

        invoice_data = extract_invoice_data(invoice_path)
        eway_data = extract_eway_data(eway_path)

        output_path = os.path.join("OUTPUT", "Generated_PSRV.xlsx")

        possible_templates = [
            os.path.join(base_dir, "TEMPLATES", "PSRV Format.xlsx"),
            os.path.join(base_dir, "templates", "PSRV Format.xlsx"),
            os.path.join(base_dir, "App files", "TEMPLATES", "PSRV Format.xlsx"),
            os.path.join(base_dir, "App files", "templates", "PSRV Format.xlsx"),
        ]

        template_path = None

        for path in possible_templates:
            if os.path.exists(path):
                template_path = path
                break

        if template_path is None:
            st.error("PSRV template file not found.")
            st.write("Checked these locations:")
            for path in possible_templates:
                st.code(path)
            st.stop()

        generate_psrv(
            invoice_data=invoice_data,
            eway_data=eway_data,
            template_path=template_path,
            output_path=output_path
        )

        st.success("PSRV Generated Successfully!")

        with open(output_path, "rb") as file:
            st.download_button(
                label="Download PSRV",
                data=file,
                file_name="Generated_PSRV.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )