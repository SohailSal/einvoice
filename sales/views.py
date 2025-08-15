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

def invoice_post(request):
	data = json.loads(request.body)
	# invoice_number = data['invoice_number']
	invoice_date = data['invoice_date'] if data['invoice_date'] else None
	invoice_number = utils.generate_invoice_number(invoice_date) if data['invoice_date'] else None
	customer = None if (data['customer'] == '0') else get_object_or_404(Customer, pk=data['customer'])
	description = data['description']
	items = []

	try:
		with transaction.atomic():
			invoice = Invoice(invoice_number=invoice_number, customer=customer, invoice_date=invoice_date, description=description)
			invoice.full_clean()
			invoice.save(commit=False)
			for entry in data['entries']:
				item = get_object_or_404(Item, pk=entry['item']) if entry['item'] else None
				quantity = float(entry['quantity']) if entry['quantity'] else None
				rate = float(entry['rate']) if entry['rate'] else None
				amount = float(entry['amount']) if entry['amount'] else None
				total = (total + amount) if amount else None
				items.append(InvoiceItem(invoice=invoice, item=item, quantity=quantity, rate=rate, amount=amount))
				# update stock item's quantity
				item.quantity = float(item.quantity) - quantity
				item.save()

			for item in items:
				item.full_clean()
			for item in items:
				item.save()
			invoice.amount = total
			invoice.save()

	except (ValidationError, DatabaseError) as e:
		ic(e)
		if hasattr(e, 'message_dict'):
			errors = e.message_dict
		else:
			errors = {'non_field_errors': e.messages} # Fallback for non-field errors
		
		return JsonResponse({'errors': errors}, safe=False)

	return JsonResponse({'messages':{'success':'The invoice saved!'}}, safe=False)

def getRate(request):
	data = json.loads(request.body)
	if data['item']:
		item = get_object_or_404(Item, pk=data['item'])
		return JsonResponse({'rate': item.sale_rate, 'hs_code': item.hs_code}, safe=False)
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
