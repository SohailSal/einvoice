from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
import json
from django.db import transaction
from .models import Item, Customer, Invoice, InvoiceItem
from django.core.exceptions import ValidationError
from django.db import DatabaseError 
from icecream import ic
from . import utils
import requests

@login_required
def customers(request):
	customers = Customer.objects.order_by('id')
	return render(request, 'sales/customers.html', context={"customers": customers})

@login_required
def customer_add(request):
	return render(request, 'sales/customer_add.html', context={})

def customer_post(request):
	data = json.loads(request.body)
	name = data['name']
	ntn_cnic = data['ntn_cnic'] if data['ntn_cnic'] else ""
	phone = data['phone'] if data['phone'] else ""
	address = data['address'] if data['address'] else ""
	province = data['province'] if data['province'] else ""
	registration_type = data['registration_type'] if data['registration_type'] else ""

	try:
		with transaction.atomic():
			customer = Customer(name=name, ntn_cnic=ntn_cnic, phone=phone, address=address, province=province, registration_type=registration_type)
			customer.full_clean()
			customer.save()
	except (ValidationError, DatabaseError) as e:
		if hasattr(e, 'message_dict'):
			errors = e.message_dict
		else:
			errors = {'non_field_errors': e.messages} # Fallback for non-field errors
		
		return JsonResponse({'errors': errors}, safe=False)

	return JsonResponse({'messages':{'success':'The customer saved!'}}, safe=False)

def customer_edit(request,id):
	customer = get_object_or_404(Customer, pk=id)
	return render(request, 'sales/customer_edit.html', context={"customer":customer})

def customer_edit_post(request):
	customer = get_object_or_404(Customer, pk=request.POST['id'])
	customer.name = request.POST['name'] if request.POST['name'] else ""
	customer.ntn_cnic = request.POST['ntn_cnic'] if request.POST['ntn_cnic'] else ""
	customer.phone = request.POST['phone'] if request.POST['phone'] else ""
	customer.address = request.POST['address'] if request.POST['address'] else ""
	customer.province = request.POST['province'] if request.POST['province'] else ""
	customer.registration_type = request.POST['registration_type'] if request.POST['registration_type'] else ""
	customer.save()
	messages.success(request, 'The customer has been updated successfully.')
	return HttpResponseRedirect(reverse('sales:customers'))

def customer_delete(request,id):
	customer = get_object_or_404(Customer, pk=id)
	customer.delete()
	messages.success(request, 'The customer has been deleted successfully.')
	return HttpResponseRedirect(reverse('sales:customers'))

@login_required
def items(request):
	items = Item.objects.all()
	return render(request, 'sales/items.html', context={'items':items})

@login_required
def item_add(request):
	return render(request, 'sales/item_add.html', context={})

def item_post(request):
	data = json.loads(request.body)
	hs_code = data['hs_code'] if data['hs_code'] else ""
	uo_m = data['uo_m'] if data['uo_m'] else ""
	description = data['description']
	purchase_rate = data['purchase_rate'] if data['purchase_rate'] else 0
	sale_rate = data['sale_rate'] if data['sale_rate'] else 0
	quantity = data['quantity'] if data['quantity'] else 0

	try:
		with transaction.atomic():
			item = Item(hs_code=hs_code, uo_m=uo_m, description=description, purchase_rate=purchase_rate, sale_rate=sale_rate, quantity=quantity)
			item.full_clean()
			item.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		if hasattr(e, 'message_dict'):
			errors = e.message_dict
		else:
			errors = {'non_field_errors': e.messages} # Fallback for non-field errors
		
		return JsonResponse({'errors': errors}, safe=False)
		# return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The item saved!'}}, safe=False)

def item_edit(request,id):
	item = get_object_or_404(Item, pk=id)
	return render(request, 'sales/item_edit.html', context={"item":item})

def item_edit_post(request):
	item = get_object_or_404(Item, pk=request.POST['id'])
	item.hs_code = request.POST['hs_code'] if request.POST['hs_code'] else ""
	item.uo_m = request.POST['uo_m'] if request.POST['uo_m'] else ""
	item.description = request.POST['description']
	item.purchase_rate = request.POST['purchase_rate'] if request.POST['purchase_rate'] else 0
	item.sale_rate = request.POST['sale_rate'] if request.POST['sale_rate'] else 0
	item.quantity = request.POST['quantity'] if request.POST['quantity'] else 0
	item.save()
	messages.success(request, 'The item has been updated successfully.')
	return HttpResponseRedirect(reverse('sales:items'))

def item_delete(request,id):
	item = get_object_or_404(Item, pk=id)
	item.delete()
	messages.success(request, 'The item has been deleted successfully.')
	return HttpResponseRedirect(reverse('sales:items'))


@login_required
def invoices(request):
	invoices = Invoice.objects.order_by('id')
	return render(request, 'sales/invoices.html', context={"invoices": invoices})

@login_required
def invoice_add(request):
	items = [i.select() for i in Item.objects.all()]
	customers = [i.select() for i in Customer.objects.all()]
	return render(request, 'sales/invoice_add.html', context={'items':items,'customers':customers})

def invoice_save(request):
	data = json.loads(request.body)
	# invoice_number = data['invoice_number']
	invoice_date = data['invoice_date'] if data['invoice_date'] else None
	ic(data['invoice_type'])
	invoice_type = data['invoice_type'] if data['invoice_type'] else None
	ic(data['invoice_type'])
	# invoice_number = utils.generate_invoice_number(invoice_date) if data['invoice_date'] else None
	invoice_number = "INV001"
	customer = None if (data['customer'] == '0') else get_object_or_404(Customer, pk=data['customer'])
	items = []

	try:
		with transaction.atomic():
			invoice = Invoice(invoice_number=invoice_number, customer=customer, invoice_date=invoice_date, invoice_type=invoice_type)
			invoice.full_clean()
			invoice.save()
			for entry in data['entries']:
				item = get_object_or_404(Item, pk=entry['item']) if entry['item'] else None
				rate = float(entry['rate']) if entry['rate'] else None
				uo_m = entry['uo_m'] if entry['uo_m'] else None
				quantity = float(entry['quantity']) if entry['quantity'] else None
				total_values = float(entry['total_values']) if entry['total_values'] else None
				fixed_notified_value_or_retail_price = float(entry['fixed_notified_value_or_retail_price']) if entry['fixed_notified_value_or_retail_price'] else None
				value_sales_excluding_st = float(entry['value_sales_excluding_st']) if entry['value_sales_excluding_st'] else None
				sales_tax_applicable = float(entry['sales_tax_applicable']) if entry['sales_tax_applicable'] else None
				sales_tax_withheld_at_source = float(entry['sales_tax_withheld_at_source']) if entry['sales_tax_withheld_at_source'] else None
				extra_tax = float(entry['extra_tax']) if entry['extra_tax'] else None
				further_tax = float(entry['further_tax']) if entry['further_tax'] else None
				sro_schedule_no = entry['sro_schedule_no'] if entry['sro_schedule_no'] else None
				fed_payable = float(entry['fed_payable']) if entry['fed_payable'] else None
				discount = float(entry['discount']) if entry['discount'] else None
				sale_type = entry['sale_type'] if entry['sale_type'] else None
				sro_item_serial_no = entry['sro_item_serial_no'] if entry['sro_item_serial_no'] else None

				# total = (total + total_values) if total_values else None
				items.append(InvoiceItem(invoice=invoice, item=item, quantity=quantity, uo_m=uo_m, rate=rate, total_values=total_values, value_sales_excluding_st=value_sales_excluding_st, fixed_notified_value_or_retail_price=fixed_notified_value_or_retail_price, sales_tax_applicable=sales_tax_applicable, sales_tax_withheld_at_source=sales_tax_withheld_at_source, extra_tax=extra_tax, further_tax=further_tax, sro_schedule_no=sro_schedule_no, fed_payable=fed_payable, discount=discount, sale_type=sale_type, sro_item_serial_no=sro_item_serial_no))
				# update stock item's quantity
				# item.quantity = float(item.quantity) - quantity
				item.save()

			for item in items:
				item.full_clean()
			for item in items:
				item.save()
			# invoice.amount = total
			invoice.save()

	except (ValidationError, DatabaseError) as e:
		ic(e)
		if hasattr(e, 'message_dict'):
			errors = e.message_dict
		else:
			errors = {'non_field_errors': e.messages} # Fallback for non-field errors
		
		return JsonResponse({'errors': errors}, safe=False)

	return JsonResponse({'messages':{'success':'The invoice saved!'}}, safe=False)


def invoice_post(request, id):
	invoice = get_object_or_404(Invoice, pk=id)
	payload = {
		"invoiceType": invoice.invoice_type, 
		"invoiceDate": invoice.invoice_date.strftime("%Y-%m-%d"), 
		"sellerNTNCNIC": "1000645", 
		"sellerBusinessName": "PetroChemical & Lubricants Co (Pvt) Ltd", 
		"sellerProvince": "Sindh", 
		"sellerAddress": "Karachi", 
		"buyerNTNCNIC": invoice.customer.ntn_cnic, 
		"buyerBusinessName": invoice.customer.name, 
		"buyerProvince": invoice.customer.province, 
		"buyerAddress": invoice.customer.address, 
		"buyerRegistrationType": invoice.customer.registration_type, 
		"invoiceRefNo": "",
		"scenarioId": "SN005",
		"items": []
	}
	for i in invoice.items.all():
		payload["items"].append({
			"hsCode": i.item.hs_code, 
			"productDescription": i.item.description, 
			"rate": f"{i.rate}", 
			# "rate": f"{i.rate}%", 
			"uoM": i.uo_m, 
			"quantity": i.quantity, 
			"totalValues": int(round(float(i.total_values))), 
			"valueSalesExcludingST": int(round(float(i.value_sales_excluding_st))), 
			"fixedNotifiedValueOrRetailPrice": int(round(float(i.fixed_notified_value_or_retail_price))), 
			"salesTaxApplicable": int(round(float(i.sales_tax_applicable))), 
			"salesTaxWithheldAtSource": int(round(float(i.sales_tax_withheld_at_source))), 
			"extraTax": "", 
			# "extraTax": i.extra_tax, 
			"furtherTax": int(round(float(i.further_tax))), 
			"sroScheduleNo": i.sro_schedule_no, 
			"fedPayable": int(round(float(i.fed_payable))), 
			"discount": int(round(float(i.discount))), 
			"saleType": i.sale_type, 
			"sroItemSerialNo": i.sro_item_serial_no 
		})

	api_url = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb" 
	api_key = "769de299-8a51-31a3-a325-6ddfa2b6b763"
	api_data = ""
	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {api_key}"
	}

	try:
		response = requests.post(api_url, headers=headers, data=json.dumps(payload))
		response.raise_for_status()
		api_data = response.json()
		ic(api_data)
		fbr_inv_no = api_data.get('invoiceNumber')
		invoice.invoice_number_fbr = fbr_inv_no
		invoice.save()
		HttpResponse(fbr_inv_no)
	except requests.exceptions.RequestException as e:
		api_data = f"Error calling API: {e}"
		JsonResponse(api_data)
	return HttpResponse(fbr_inv_no)
	# return JsonResponse({'messages':{'success':'The invoice saved!'}}, safe=False)

def getRate(request):
	data = json.loads(request.body)
	if data['item']:
		item = get_object_or_404(Item, pk=data['item'])
		return JsonResponse({'uo_m': item.uo_m, 'hs_code': item.hs_code}, safe=False)
	else:
		return JsonResponse({'rate': 0}, safe=False)

def invoice_delete(request,id):
	invoice = get_object_or_404(Invoice, pk=id)
	invoice.delete()
	messages.success(request, 'The invoice has been deleted successfully.')
	return HttpResponseRedirect(reverse('sales:invoices'))

def invoice(request,id):
	buffer = utils.generate_invoice(id)
	return FileResponse(buffer, as_attachment=True, filename="invoice.pdf")
