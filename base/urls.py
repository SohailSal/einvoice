from django.urls import path,include
from . import views
from . import utils

app_name = "base"
urlpatterns = [
	path('',views.home),

# logins
    path('home', views.home, name="home"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'), 
    path('logout', views.logout_view, name='logout'),

# reports
    path('reports', views.reports, name='reports'),  
    path('reports_invoices', views.reports_invoices, name='reports_invoices'),
    path('scenario', views.scenario, name='scenario'),
    path('fbr', views.fbr, name='fbr'),
    path('get_transaction_type', views.get_transaction_type, name='get_transaction_type'),
    path('get_sale_type_to_rate', views.get_sale_type_to_rate, name='get_sale_type_to_rate'),
    path('sro_schedule', views.sro_schedule, name='sro_schedule'),
    path('sro_item', views.sro_item, name='sro_item'),
    path('get_hs_codes', views.get_hs_codes, name='get_hs_codes'),
    path('get_hs_uom', views.get_hs_uom, name='get_hs_uom'),
    path('get_reg_type', views.get_reg_type, name='get_reg_type'),
    path('get_status', views.get_status, name='get_status'),
]