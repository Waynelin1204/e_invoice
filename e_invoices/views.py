from django.shortcuts import render, redirect
import django.contrib.auth.views as auth_view
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from e_invoices.models import RegisterForm
from e_invoices.models import LoginForm
from e_invoices.models import Invoice
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from e_invoices.models import Sapfagll03
from e_invoices.models import Myinvoiceportal 
from django.db import connection
from e_invoices.models import Twa0101
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import get_list_or_404

def front4(request):
	return render(request,'front4.html')
	
#def test(request):
#	return render(request,'test.html')


def twa0101(request):
    # Fetch documents for display, with optional search filtering
    documents = Twa0101.objects.all()
    context = {
	'documents': documents,
    }

    return render(request, 'test.html', context)



def export_invoices(request):
    """Export all columns of selected invoices to an Excel file."""
    selected_invoice_numbers = request.GET.get("ids", "").split(",")

    # Fetch all records from the database for the selected IDs
    invoices = Twa0101.objects.filter(invoice_number__in=selected_invoice_numbers).values()  # Get all fields

    if not invoices:
        return HttpResponse("No records found.", status=400)

    # Convert QuerySet to DataFrame (includes all DB columns)
    df = pd.DataFrame(list(invoices))  

    # Ensure all columns are included, even if some values are empty
    df.fillna("", inplace=True)

    # Create Excel file in memory
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="exported_invoices.xlsx"'

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)  # Write all DB columns to Excel
    
    return response



    
def register(request):

    form = RegisterForm()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    context = {
        'form':form
    }
    return render(request, 'accounts/register.html', context)

def sign_in(request):

    form=LoginForm()
    #form = AuthenticationForm()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
             login(request, user)
             return redirect('document_list')  # ✅ Corrected

    context = {
        'form': form
    }
    return render(request, 'accounts/login.html', context)

def logout(request):
	logout(request)
	return redirect('/account/login.html')

@login_required(login_url="Login")
def document_list(request):
    # Count the total number of documents for each status
    status_counts = Invoice.objects.values('status').annotate(count=Count('status'))

    # Convert the status counts into a dictionary with proper keys
    status_dict = {status['status']: status['count'] for status in status_counts}

    # Ensure all statuses exist in the dictionary, default to 0 if missing
    all_statuses = ['created', 'error', 'in_progress', 'completed']
    status_dict = {status: status_dict.get(status, 0) for status in all_statuses}

    # Get the count of all documents
    all_documents_count = Invoice.objects.count()

    # Fetch documents for display, with optional search filtering
    documents = Invoice.objects.all()

    # Handling search query if provided
    search_query = request.GET.get('search', '')
    if search_query:
        documents = documents.filter(document_id__icontains=search_query)

    # Pass counts and documents to the template
    context = {
        'documents': documents,
        'status_dict': status_dict,
        'all_documents_count': all_documents_count,
    }

    return render(request, 'edocument.html', context)

def generate_pdf(request, document_id):
    try:
        document = Invoice.objects.get(document_id=str(document_id))
    except Invoice.DoesNotExist:
        return HttpResponse("Document not found.", status=404)

    # Remove or comment out the early return below:
    # return HttpResponse(f"Document found: {document.document_id}, Status: {document.status}")

    # Use the XML file path from the instance (document) rather than the model class
    xml_file_path = document.xml_file_path  # Correct way to access the stored file path

    # Open the XML file from the stored path
    try:
        with open(xml_file_path, "r", encoding="utf-8") as file:
            xml_data = file.read()
    except FileNotFoundError:
        return HttpResponse("XML file not found.", status=404)

    # Parse XML data
    root = ET.fromstring(xml_data)
    extracted_text = f"Document ID: {document.document_id}\nStatus: {document.status}"

    response = HttpResponse(content_type="application/pdf")
    #response["Content-Disposition"] = "inline"  # Show in browser instead of downloading
    response["Content-Disposition"] = f'attachment; filename="invoice_{document_id}.pdf'
    p = canvas.Canvas(response, pagesize=letter)
    #p.drawString(200, 750, "eDocument Details")
    # Draw text at the specified positions
    p.setFont("Helvetica", 12)  # Set font size

    # Header Section
    p.drawString(400, 730, f"{document.buyer_name}")
    p.drawString(400, 750, f"Invoice No.: {document.document_id}")
    p.drawString(400, 730, f"Issue Date: {document.issue_date}")
    
    #p.drawString(400, 710, f"Customer No.: {document.buyer_name}")

    # Buyer & Delivery Details
    p.drawString(100, 670, f"Buyer Name: {document.buyer_name}")
    p.drawString(100, 650, f"Buyer Address: {document.buyer_addr1}")
    p.drawString(100, 630, f"Buyer TIN: {document.buyer_tin_id}")
    p.drawString(100, 610, f"Buyer BRN: {document.buyer_brn_id}")

    p.drawString(400, 670, f"Delivery Address: {document.delivery_addr1}")

    # Industry Classification & Tax Details
    #p.drawString(100, 570, f"Industry Classification: {document.industry_classification}")
    p.drawString(400, 550, f"Taxable Amount: {document.taxable_amount}")
    p.drawString(400, 530, f"Tax Amount: {document.tax_amount}")
    #p.drawString(400, 510, f"Total Excl. Tax: {document.total_excl_tax}")
    #p.drawString(400, 490, f"Total Incl. Tax: {document.total_incl_tax}")
    p.drawString(400, 470, f"Prepaid Amount: {document.prepaid_amount}")
    p.drawString(400, 450, f"Amount to Pay: {document.payable_amount}")

    # Supplier Details
    p.drawString(100, 430, f"Supplier Name: {document.supplier_name}")
    p.drawString(100, 410, f"Supplier Address: {document.supplier_addr1}")
    p.drawString(100, 390, f"Supplier TIN ID: {document.supplier_tin_id}")
    p.drawString(100, 370, f"Supplier BRN ID: {document.supplier_brn_id}")

    # Tax Summary
    #p.drawString(400, 370, f"Tax Code: {document.tax_code}")
    p.drawString(400, 350, f"Taxable Amount: {document.taxable_amount}")
    p.drawString(400, 330, f"Tax Rate: {document.tax_rate}")
    p.drawString(400, 310, f"Tax Amount: {document.tax_amount}")

    # Item Details (Product Information Table)
    p.drawString(100, 280, "Article No.")
    p.drawString(200, 280, "Description")
    p.drawString(400, 280, "Quantity")
    p.drawString(450, 280, "Unit")
    p.drawString(500, 280, "Unit Price")
    p.drawString(550, 280, "Tax Rate")
    p.drawString(600, 280, "Net Amount")

    p.drawString(100, 260, f"{document.item_id}")
    p.drawString(200, 260, f"{document.item_name}")
    p.drawString(400, 260, f"{document.item_quantity}")
    #p.drawString(450, 260, f"{document.item_unit}")
    p.drawString(500, 260, f"{document.item_unit_price}")
    p.drawString(550, 260, f"{document.tax_rate}")
    p.drawString(600, 260, f"{document.line_ext_amount}")

    # Total Calculation
    #p.drawString(500, 220, f"Subtotal: {document.subtotal}")
    p.drawString(500, 200, f"Taxable Amount: {document.taxable_amount}")
    p.drawString(500, 180, f"Tax Amount: {document.tax_amount}")
    #p.drawString(500, 160, f"Total Excl. Tax: {document.total_excl_tax}")
    #p.drawString(500, 140, f"Total Incl. Tax: {document.total_incl_tax}")
    p.drawString(500, 120, f"Prepaid Amount: {document.prepaid_amount}")
    p.drawString(500, 100, f"Amount to Pay: {document.payable_amount}")

    # Additional Information
    p.drawString(100, 80, f"XML File Path: {xml_file_path}")

    p.save()

    return response

@login_required(login_url="Login")
def reconcil(request):
	display_limit = int(request.GET.get("display_limit",25))
	
	tax_code_filter = request.GET.get("tax_code")
	document_type_filter = request.GET.get("document_type")
	document_number_filter = request.GET.get("search","")


	query = """
		SELECT
			s.document_number,
			s.tax_code,
			s.document_type,
			s.posting_date,
			s.amount_in_doc_curr,
			s.document_currency,
			s.amount_in_lc,
			s.local_currency,
			s.including_tax_amount,
			i.internalId,
			i.totalPayableAmount,
			i.totalExcludingTax,
			i.totalNetAmount
		FROM e_invoices_sapfagll03 s
		LEFT JOIN e_invoices_myinvoiceportal i
		ON s.document_number = SUBSTR(i.internalId, 1, LENGTH(i.internalId) - 4)
	"""
	
	filters = []
	if tax_code_filter:
		filters.append(f"s.tax_code = '{tax_code_filter}'")
	if document_type_filter:
		filters.append(f"s.document_type = '{document_type_filter}'")
	if document_number_filter:
		document_number_filter = document_number_filter.strip()
		filters.append(f"CAST(s.document_number AS TEXT) LIKE '%{document_number_filter}%'")
		
	
	if filters:
		query += " WHERE " + " AND ".join(filters)
		
	query += " ORDER BY s.posting_date DESC"
	query += f" LIMIT {display_limit}"
	print(document_number_filter)
	print("check")


	with connection.cursor() as cursor:
		cursor.execute(query)
		merged_data = [
			{
				"document_number": row[0],
				"tax_code": row[1],
				"document_type":row[2],
				"posting_date": row[3],
				"amount_in_doc_curr":row[4],
				"document_currency":row[5],
				"amount_in_lc":row[6],
				"local_currency":row[7],
				"including_tax_amount":row[8],
				"internalId":row[9],
				"totalPayableAmount":row[10],
				"totalExcludingTax":row[11],
				"totalNetAmount":row[12]
			}
			for row in cursor.fetchall()
		]
	
		cursor.execute('SELECT DISTINCT "Tax Code" FROM e_invoices_sapfagll03')
		tax_codes = [row[0] for row in cursor.fetchall()]
		
		cursor.execute('SELECT DISTINCT "Document Type" FROM e_invoices_sapfagll03')
		document_types = [row[0] for row in cursor.fetchall()]

	
	return render(request, "reconcil.html", {
		"merged_data": merged_data,
		"tax_codes":tax_codes,
		"document_types":document_types,
		"display_limit":display_limit,
		"search_query":document_number_filter,
	})	
	# sap_data = Sapfagll03.objects.all()
	
	# invoice_data = {invoice.internal_id_trimmed: invoice for invoice in Myinvoiceportal.objects.all()}
	
	# merged_data = []
	
	# for sap in sap_data:
	
		# invoice = invoice_data.get(sap.document_number)
		# merged_data.append({
			# "document_number":sap.document_number,
			# "tax_code":sap.tax_code,
			# "document_type":sap.document_type,
			# "posting_date": sap.posting_date,
			# "amount_in_doc_curr":sap.amount_in_doc_curr,
			# "document_currency":sap.document_currency,
			# "amount_in_lc":sap.amount_in_lc,
			# "local_currency":sap.local_currency,
			# "including_tax_amount":sap.including_tax_amount,
			# "internalId":invoice.internal_id if invoice else "N/A",
			# "totalPayableAmount":invoice.totalPayableAmount if invoice else "N/A",
			# "totalExcludingTax":invoice.totalExcludingTax if invoice else "N/A",
			# "totalNetAmount":invoice.totalNetAmount if invoice else "N/A",
			
		# })
		
	# return render(request, "reconcil.html", {"merged_data":merged_data})
		
