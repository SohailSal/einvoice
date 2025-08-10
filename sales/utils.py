import random
from .models import Invoice
from icecream import ic
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from num2words import num2words
from datetime import datetime

def generate_invoice_number(d):
    chunks = []
    document = get_object_or_404(Document, pk=2)
    prefix = document.prefix
    dt = datetime.strptime(d,'%Y-%m-%d')
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    counter = '1' if Invoice.objects.count() == 0 else str(int(Invoice.objects.last().invoice_number.split('/')[-1])+1)
    chunks.append(prefix+'/')
    chunks.append(year+'/')
    chunks.append(month+'/')
    # chunks.append(counter.zfill(3))
    chunks.append(counter)
    str1 = ""
    for ele in chunks:
        str1 += ele
 
    return str1

def generate_invoice(id):
    invoice = get_object_or_404(Invoice, pk=id)
    products = [i.select() for i in invoice.invoiceitem_set.all()]
    company_ntn = "1000645"
    company_name = "PetroChemical & Lubricants Co (Pvt) Ltd"
    company_province = "Sindh"
    company_address = "Karachi"

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

	# Define styles
    heading3 = getSampleStyleSheet()["h3"]
    heading4 = getSampleStyleSheet()["h4"]
    # heading3 = styles["h3"]
    data_style = ParagraphStyle(name="Data", fontSize=10)
    amount_style = ParagraphStyle(name="amount", fontSize=10, alignment=TA_RIGHT)
    custom_style = ParagraphStyle(
        name='CustomStyle',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=12,
        textColor=colors.red,
    )
    h = 800
    h = h-50
    c.drawString(30, h, company_name)
    c.drawString(300, h, "Bill To:")
    h = h-20
    c.drawString(30, h, company_address)
    c.drawString(300, h, invoice.customer.name)
    h = h-20
    c.drawString(30, h, company_contact)
    c.drawString(300, h, invoice.customer.address)
    h = h-30
    c.drawString(30, h, f"Invoice Number: {invoice.invoice_number}")
    h = h-20
    c.drawString(30, h, f"Invoice Date: {invoice.invoice_date}")
    cnt = len(products)

	# Create product table
    data = [[Paragraph("PRODUCT", heading3), Paragraph("QUANTITY", heading3), Paragraph("PRICE (Rs.)", heading3), Paragraph("AMOUNT (Rs.)", heading3)]]
    data.extend([[Paragraph(p["name"], data_style), Paragraph(str(p["quantity"]), data_style), Paragraph(f"{p['price']:.2f}", amount_style), Paragraph(f"{p['quantity'] * p['price']:0,.2f}", amount_style)] for p in products])

    total_amount = sum([p["quantity"] * p["price"] for p in products])
    data.extend([[Paragraph("Total Amount", heading4), Paragraph(""), Paragraph(""), Paragraph(f"Rs.{total_amount:0,.2f}", amount_style)]])

    table = Table(data, colWidths=[100, 100, 100, 100], style=[('LINEABOVE',(0,1),(3,1),1,colors.black), ('LINEBEFORE',(3,1),(3,cnt),1,colors.black), ('LINEAFTER',(3,1),(3,cnt),1,colors.black), ('LINEABOVE',(-1,-1),(-1,-1),1,colors.black), ('LINEBELOW',(-1,-1),(-1,-1),1,colors.black,0,None,None,2,2)])

    th = cnt*20 + 70
    h = h - th
    table.wrapOn(c, 50, h)
    table.drawOn(c, 50, h)

    h = h - 30
    c.drawString(50, h, "Rupees")
    c.drawString(95, h, num2words(f"{total_amount:.2f}") + " only.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
