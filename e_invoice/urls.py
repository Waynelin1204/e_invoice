"""
URL configuration for e_invoice project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from e_invoices.views import register
from e_invoices.views import document_list
from e_invoices.views import sign_in
from e_invoices.views import logout
from e_invoices.views import generate_pdf
from e_invoices.views import reconcil
from e_invoices.views import front4
from e_invoices.views import twa0101
from e_invoices.views import export_invoices

 



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', register, name='register'),
    path('accounts/login/',sign_in, name='login'),
    path('front4/', front4, name = 'front4'),
    path('test/', twa0101, name='test'),
    #path('loguot/', logout, name = 'logout'),
    path('edocument/',document_list, name='document_list'),
    path('reconcil/',reconcil, name = 'reconcil'),
    path('generate_pdf/<str:document_id>/', generate_pdf, name='generate_pdf'),
    path("export-invoices/", export_invoices, name="export_invoices")
]

