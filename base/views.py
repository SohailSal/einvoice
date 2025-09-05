from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q
from icecream import ic
import fiscalyear
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime

import requests
import json
import os
from . import utils
from sales.models import Invoice

# logins

def home(request):
    return render(request, 'base/home.html')

@login_required
def dashboard(request):
	users = User.objects.order_by('id')
	return render(request, 'base/dashboard.html', context={"users": users})

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login')

        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/login')
        else:
            auth_login(request, user)
            # setting year session
            request.session["hello"] = "world"

            next_url = request.GET.get("next")
            if next_url:
                 return redirect(next_url)
            else:
                 return redirect('/dashboard')

    return render(request, 'base/login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)

        if user.exists():
            messages.info(request, "Username already taken!")
            return redirect('/register')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username
        )

        user.set_password(password)
        user.save()

        messages.info(request, "Account created Successfully!")
        return redirect('/register')

    return render(request, 'base/register.html')

def logout_view(request):
    logout(request)
    return redirect('/home')

@login_required
def reports(request):
    return render(request, 'base/reports.html', context={})


def scenario(request):
    api_url = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb" 
    api_key = os.getenv("API_KEY_FBR")
    api_data = ""
    
    payload = { 
    "invoiceType": "Sale Invoice", 
    "invoiceDate": "2025-04-21", 
    "sellerNTNCNIC": "1000645", 
    "sellerBusinessName": "PetroChemical & Lubricants Co (Pvt) Ltd", 
    "sellerProvince": "Sindh", 
    "sellerAddress": "Karachi", 
    "buyerNTNCNIC": "1000000000000", 
    "buyerBusinessName": "FERTILIZER MANUFAC IRS NEW", 
    "buyerProvince": "Sindh", 
    "buyerAddress": "Karachi", 
    "buyerRegistrationType": "Unregistered", 
    "invoiceRefNo": "",  
    "scenarioId": "SN002",
    "items": [ 
            { 
                "hsCode": "0101.2100", 
                "productDescription": "product Description", 
                "rate": "18%", 
                "uoM": "Numbers, pieces, units", 
                "quantity": 1, 
                "totalValues": 0, 
                "valueSalesExcludingST":1000, 
                "fixedNotifiedValueOrRetailPrice":0, 
                "salesTaxApplicable": 180, 
                "salesTaxWithheldAtSource":0, 
                "extraTax": "", 
                "furtherTax": 120, 
                "sroScheduleNo": "", 
                "fedPayable": 0, 
                "discount": 0, 
                "saleType": "Goods at standard rate (default)", 
                "sroItemSerialNo": "" 
            } 
        ] 
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        api_data = response.json()
        JsonResponse(api_data)
    except requests.exceptions.RequestException as e:
        api_data = f"Error calling API: {e}"
        JsonResponse(api_data)
    return JsonResponse(api_data)

def reports_invoices(request):
    start = request.POST['start_date']
    end = request.POST['end_date']
    invoices = Invoice.objects.filter(invoice_date__range=(start,end)).values()
    # converted = list(invoices)
    # return JsonResponse(converted, safe=False)
    if invoices:
        response = utils.generate_report(invoices)
        return response
    else:
        messages.warning(request, "No invoices were present!")
        return redirect('/reports')

@login_required
def fbr(request):
    return render(request, 'base/fbr.html', context={})
