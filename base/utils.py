import xlsxwriter
import io
from icecream import ic
from django.db.models import Sum, Q, F
from django.db import transaction as trans
from django.db import DatabaseError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

def generate_report(ledger_data):
    # Create a new workbook and add a worksheet
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('ledger')
    header1 = "&CHere is some centered header."
    footer1 = "&LHere is some left aligned footer."

    worksheet.set_header(header1)
    worksheet.set_footer(footer1)
    # Define the column headers
    headers = ['Date', 'Ref', 'Description', 'Debit', 'Credit', 'Running Balance']

    # Write the column headers to the worksheet
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    balance = 0
    ob = 0
    row_count = 3

    format1 = workbook.add_format({'num_format': 'd mmmm yyyy'})
    format2 = workbook.add_format({'num_format': '#,##0.00'})
    worksheet.set_column(0, 0, 18)

    year_setting = Setting.objects.filter(name__iexact='year').first().value
    year = get_object_or_404(Year, pk=year_setting)
    prev_yr = Year.objects.filter(id = year.previous).first()
    # start_dt = year.start_date.strftime("%Y-%m-%d")


    worksheet.write(1,2, 'Opening Balance')
    worksheet.write(1,5, ob, format2)
    balance = float(ob)
    for row, data in enumerate(ledger_data, start=2):
        balance += float(data['debit']) - float(data['credit'])

        worksheet.write(row, 0, data['date'], format1)
        worksheet.write(row, 1, data['ref'])
        worksheet.write(row, 2, data['description'])
        worksheet.write(row, 3, data['debit'], format2)
        worksheet.write(row, 4, data['credit'], format2)
        worksheet.write(row, 5, balance, format2)

        row_count = row_count + 1

    # Write the totals
    total_debit = sum(float(data['debit']) for data in ledger_data)
    total_credit = sum(float(data['credit']) for data in ledger_data)

    worksheet.write(row_count, 1, 'Totals')
    worksheet.write(row_count, 3, total_debit, format2)
    worksheet.write(row_count, 4, total_credit, format2)

    # Save the workbook
    worksheet.autofit()
    workbook.close()
    output.seek(0)
    filename = "ledger.xlsx"
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response