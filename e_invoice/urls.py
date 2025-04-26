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
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from e_invoices.views import register, sign_in, logout

from e_invoices.views import manage_user_permissions, update_permissions, get_user_permissions

from e_invoices.views import company_detail, company_detail_sub, company_add

from e_invoices.views import main

from e_invoices.views import front4

from e_invoices.views import number_distribution, create_number_distribution

from e_invoices.views import number_distribution, twb2bmainitem, twb2blineitem, twb2bmainitem_filter, twb2bmainitem_delete_selected_invoices,twb2bmainitem_export_invoices, twb2bmainitem_update_void_status

from e_invoices.views import upload, import_log, upload_file_tw, run_script_tw

from e_invoices.views import run_script, upload_file, invoice_list, invoice_detail, update_invoice_status
# from e_invoices.views import document_list
# from e_invoices.views import generate_pdf
# from e_invoices.views import reconcil
# from e_invoices.views import invoice_list, invoice_detail, upload_file, run_script, twa0101_detail
# from e_invoices.views import delete_selected_invoices
# from e_invoices.views import twa0101
# from e_invoices.views import export_invoices




urlpatterns = [

    path('admin/', admin.site.urls),

#-------------------for login/register-------------------

    path('accounts/register/', register, name='register'),
    path('login/',sign_in, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

#-------------------for 主頁面-------------------

    path('',main, name='main'),

#-------------------for 儀錶板------------------- 

    path('front4/', front4, name = 'front4'), 
   
#-------------------for 使用者權限-------------------

    path('update-permissions/<int:user_id>/', update_permissions, name='update_permissions'),
    path('permissions/', manage_user_permissions, name='manage_permissions'),
    path('get-user-permissions/<int:user_id>/', get_user_permissions, name='get_user_permissions'),

#-------------------for 營業人-------------------

    path('company_detail/', company_detail, name='company_detail'),  # 營業人列表
    path('company_detail/<str:company_id>/', company_detail_sub, name='company_detail_sub'),  # 營業人詳細頁面
    path('company/add/', company_add, name='company_add'),  # 營業人新增頁面

#-------------------for B2B 發票-------------------

    path('twb2bmainitem/', twb2bmainitem, name='twb2bmainitem'),
    path('twb2bmainitem_filter/', twb2bmainitem_filter, name = 'twb2bmainitem_filter'),
    path("twb2bmainitem_export_invoices/", twb2bmainitem_export_invoices, name="twb2bmainitem_export_invoices"),
    path('twb2bmainitem_delete_selected_invoices/', twb2bmainitem_delete_selected_invoices, name='twb2bmainitem_delete_selected_invoices'),
    path('document/<int:id>/', twb2blineitem, name='twb2blineitem'),
    path('twb2bmainitem_update_void_status/', twb2bmainitem_update_void_status, name='twb2bmainitem_update_void_status'),

#-------------------for 發票字軌-------------------

    path('number_distribution/', number_distribution, name='number_distribution'),
    path('create_number_distribmution/', create_number_distribution, name='create_number_distribution'),

#-------------------for 資料匯入-------------------

    path('upload_invoice/', upload, name='upload_invoice'),
    path('import_log/', import_log, name='import_log'),
    path('upload_file_tw/', upload_file_tw, name='upload_file_tw'),
    path('run_script_tw/', run_script_tw, name='run_script_tw'),

#-------------------for OCR-------------------

    path('invoice_list/', invoice_list, name='invoice_list'),
    path('invoices/invoice_list/', invoice_list, name='invoice_list'),  
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path("run_script/", run_script, name="run_script"),
    path('upload/', upload_file, name='upload_file'),
    path('update_invoice_status/', update_invoice_status, name = 'update_invoice_status'),
  # Ensure this exists

#------------------- protype -------------------
    # path('loguot/', logout, name = 'logout'),
    # path('edocument/',document_list, name='document_list'),
    # path('reconcil/',reconcil, name = 'reconcil'),
    # path('generate_pdf/<str:document_id>/', generate_pdf, name='generate_pdf'),
    # path('document/<int:id>/', twa0101_detail, name='twa0101_detail'),
    # path('test/', twa0101, name='test'),
    # path('invoice_filter/', invoice_filter, name = 'invoice_filter'),
    # path('delete_selected_invoices/', delete_selected_invoices, name='delete_selected_invoices'),
    # path("export_invoices/", export_invoices, name="export_invoices"),
    # path('update_void_status/', update_void_status, name='update_void_status'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)