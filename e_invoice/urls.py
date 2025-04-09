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
from e_invoices.views import invoice_list, invoice_detail, upload_file, run_script, twa0101_detail
from e_invoices.views import main, update_invoice_status, invoice_filter, company_detail, company_detail_sub
from e_invoices.views import manage_user_permissions, update_permissions, get_user_permissions
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', register, name='register'),
    path('login/',sign_in, name='login'),
    path('front4/', front4, name = 'front4'),
    path('test/', twa0101, name='test'),
    #path('loguot/', logout, name = 'logout'),
    path('edocument/',document_list, name='document_list'),
    path('reconcil/',reconcil, name = 'reconcil'),
    path('generate_pdf/<str:document_id>/', generate_pdf, name='generate_pdf'),
    path("export_invoices/", export_invoices, name="export_invoices"),
    path('invoices/invoice_list/', invoice_list, name='invoice_list'),  
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('document/<int:id>/', twa0101_detail, name='twa0101_detail'),
    path('upload/', upload_file, name='upload_file'),  # Ensure this exists
    path('', invoice_list, name='invoice_list'),
    path("run-script/", run_script, name="run_script"),
    path('main/',main, name='main'),
    path('update_invoice_status/', update_invoice_status, name = 'update_invoice_status'),
    path('invoice_filter/', invoice_filter, name = 'invoice_filter'),
    path('company_detail/', company_detail, name='company_detail'),  # 營業人列表
    path('company_detail/<str:company_id>/', company_detail_sub, name='company_detail_sub'),  # 營業人詳細頁面
    path('update-permissions/<int:user_id>/', update_permissions, name='update_permissions'),
    path('permissions/', manage_user_permissions, name='manage_permissions'),
    path('get-user-permissions/<int:user_id>/', get_user_permissions, name='get_user_permissions'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

]

