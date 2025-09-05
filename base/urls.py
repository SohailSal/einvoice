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
]