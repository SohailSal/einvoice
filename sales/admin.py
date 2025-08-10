from django.contrib import admin
from .models import Item, Customer, Invoice, InvoiceItem

admin.site.register(Item)
admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)