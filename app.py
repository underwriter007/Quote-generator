import streamlit as st
from fpdf import FPDF
import tempfile
from datetime import date

# 1. App Header
st.title("PaintPals LLC - Quote Generator")

# 2. Customer & Vehicle Details
st.header("Customer Information")
col_a, col_b = st.columns(2)
with col_a:
    customer_name = st.text_input("Customer Name")
    customer_phone = st.text_input("Phone Number")
with col_b:
    customer_email = st.text_input("Email Address")
    car_info = st.text_input("Vehicle (Year/Make/Model)")

st.divider()

# 3. Memory to hold the line items while you type
if "line_items" not in st.session_state:
    st.session_state.line_items = []

# 4. The Web Form Interface for Line Items
st.subheader("Add Line Items")
with st.form("add_item_form", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        desc = st.text_input("Description (e.g., Tailgate - Paint)")
    with col2:
        pts = st.number_input("Points", min_value=0.5, step=0.5)
    
    add_item = st.form_submit_button("Add Line Item")
    
    if add_item and desc:
        st.session_state.line_items.append({"desc": desc, "pts": pts})
        st.rerun() # Refreshes the app instantly when an item is added

# 5. Display Items (Now with Remove Buttons)
if st.session_state.line_items:
    st.subheader("Current Quote Items")
    
    # Loop through the list and add a delete button for each item
    for i, item in enumerate(st.session_state.line_items):
        col_text, col_btn = st.columns([4, 1])
        with col_text:
            st.write(f"- {item['desc']}: {item['pts']} pts (${item['pts'] * 100:,.2f})")
        with col_btn:
            if st.button("❌", key=f"delete_{i}"):
                st.session_state.line_items.pop(i) # Removes the item from memory
                st.rerun() # Refreshes the app instantly

    # Automatically build the PDF in the background
    pdf = FPDF()
    pdf.add_page()
    
    # Shop Info Header
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, "PaintPals LLC, 8715 192nd DR SE, Snohomish, WA 98290, 425-387-9993", new_x="LMARGIN", new_y="NEXT", align="L")
    
    current_date = date.today().strftime("%m/%d/%Y")
    pdf.cell(0, 6, f"{current_date}", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(8)

    # Dynamic Customer Info in PDF
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 6, f"{customer_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"{car_info}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, "Points $100/point", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Table Headers
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(100, 8, "Description", border=1)
    pdf.cell(40, 8, "Qty / Points", border=1, align="C")
    pdf.cell(40, 8, "Amount", border=1, new_x="LMARGIN", new_y="NEXT", align="R")
    
    # Calculate Math & Build Table rows
    pdf.set_font("Helvetica", size=10)
    subtotal = 0
    for item in st.session_state.line_items:
        amount = item["pts"] * 100
        subtotal += amount
        pdf.cell(100, 8, item["desc"], border=1)
        pdf.cell(40, 8, str(item["pts"]), border=1, align="C")
        pdf.cell(40, 8, f"${amount:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align="R")
    
    # Totals
    tax = subtotal * 0.099
    grand_total = subtotal + tax
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(140, 8, "Sub Total: ", align="R")
    pdf.cell(40, 8, f"${subtotal:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.cell(140, 8, "Sales Tax: ", align="R")
    pdf.cell(40, 8, f"${tax:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.cell(140, 8, "Grand Total: ", align="R")
    pdf.cell(40, 8, f"${grand_total:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align="R")

    # 6. Single Download Button
    st.divider()
    safe_name = customer_name.replace(" ", "_") if customer_name else "Customer"
    file_name = f"Quote_{safe_name}.pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            pdf_bytes = f.read()
            
    st.download_button(label="Download PDF Quote", data=pdf_bytes, file_name=file_name, mime="application/pdf")
