from django.urls import path
from . import views
# from . import utils

app_name = "sales"
urlpatterns = [
    path("customers", views.customers, name="customers"),
	path('customer_add',views.customer_add,name='customer_add'),
    path('customer_post', views.customer_post, name='customer_post'),
    path('customer_edit/<int:id>', views.customer_edit, name='customer_edit'),
    path('customer_edit_post', views.customer_edit_post, name='customer_edit_post'),
    path('customer_delete/<int:id>', views.customer_delete, name='customer_delete'),
    path("items", views.items, name="items"),
	path('item_add',views.item_add,name='item_add'),
    path('item_post', views.item_post, name='item_post'),
    path('item_edit/<int:id>', views.item_edit, name='item_edit'),
    path('item_edit_post', views.item_edit_post, name='item_edit_post'),
    path('item_delete/<int:id>', views.item_delete, name='item_delete'),
    path("invoices", views.invoices, name="invoices"),
	path('invoice_add',views.invoice_add,name='invoice_add'),
    path('invoice_save', views.invoice_save, name='invoice_save'),
    path('invoice_post', views.invoice_post, name='invoice_post'),
    path('invoice_delete/<int:id>', views.invoice_delete, name='invoice_delete'),
    path('getRate', views.getRate, name='getRate'),
    path('invoice/<int:id>', views.invoice, name='invoice'),
]