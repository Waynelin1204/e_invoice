import os
import xml.etree.ElementTree as ET
from datetime import datetime
import sqlite3

# Define XML namespaces
namespaces = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "default": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:name:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "puf": "urn:pagero:ExtensionComponent:1.0",
}

# Path to XML file in Downloads folder
downloads_folder = os.path.expanduser("/home/pi/Downloads/Response/")

# List all XML files in the directory
xml_files = [f for f in os.listdir(downloads_folder) if f.endswith(".xml")]

# Loop through each XML file
for xml_file in xml_files:
	xml_file_path = os.path.join(downloads_folder, xml_file)
    
    # Read and parse each XML file
	with open(xml_file_path, "r", encoding="utf-8") as file:
		xml_data = file.read()

	# Parse XML
	root = ET.fromstring(xml_data)
	    # Extract values
	document_id = root.find(".//cac:DocumentReference/cbc:ID", namespaces).text  # Invoice ID
	response_code = root.find("cac:DocumentResponse/cac:Response/cbc:ResponseCode", namespaces).text
	clearance_reference_id = root.find(".//puf:ClearanceReferenceID/cbc:ID", namespaces).text  # Invoice ID
	clearance_qrcode = root.find(".//puf:ClearanceQR/puf:QRString", namespaces).text  # Invoice ID
	clearance_status_code_element = root.find(".//cac:status/cbc:StatusReasonCode", namespaces)
	clearance_status_code = clearance_status_code_element.text if clearance_status_code_element is not None else ""
	clearance_reason_element = root.find(".//cac:status/cbc:StatusReason", namespaces)
	clearance_reason = clearance_reason_element.text if clearance_reason_element is not None else ""
	
	#========================================================
	#invoicetypecode = ""
	#issue_date = ""
	#issue_time = ""
	#document_currency = ""
	#buyer_reference = ""
	#self_billing = ""
	
	# Extract Supplier Details
	
	#supplier_name = ""
	#supplier_tin_id = ""
	#supplier_brn_id = ""
	#supplier_id = ""
	#supplier_addr1 = ""
	#supplier_addr2 = ""
	#supplier_addr3 = ""
	#supplier_addr4 = ""
	#supplier_country = ""
	#supplier_scheme_id = ""
	#supplier_Legal_name = ""
	#supplier_phone_element= ""
	#supplier_phone = ""
	
	
	
	# Extract Buyer Details
	#buyer_name = ""
	#buyer_supp_assign_id = ""
	#buyer_id = ""
	#buyer_tin_id = ""
	#buyer_brn_id = ""
	#buyer_addr1 = ""
	#buyer_addr2 = ""
	#buyer_addr3 = ""
	#buyer_addr4 = ""
	#buyer_scheme_id =""
	#buyer_Legal_name = ""
	#buyer_phone = ""
	#buyer_email= ""
	#buyer_country = ""
	
	#AccountingContact
	#buyer_account_name = ""
	#buyer_account_phone = ""
	#buyer_account_email = ""
	
	#Delivery Details
	#delivery_addr1 = ""
	#delivery_addr2  = ""
	#delivery_addr3  = ""
	#delivery_addr4  = ""
	#delivery_country  = ""
	# delivery_tin_id  = ""
	# delivery_name  = ""
	# delivery_id  = ""
	# delivery_scheme_id = ""
	
	# # Extract Tax Details
	# tax_amount = 0
	# taxable_amount = 0
	# tax_category = 0
	# tax_rate =0
	# tax_scheme_id = 0
	# tax_scheme_name = 0
	# tax_exemption = 0
	
	# # Extract Monetary Totals
	# line_ext_amount = 0
	# tax_exclus_amount = 0
	# tax_includ_amount = 0
	# prepaid_amount = 0
	# payable_amount = 0
	
	# # Extract Item Details
	# #print(ET.tostring(root, encoding='utf8').decode('utf8'))
	
	# #item_line_excl_allowance_charge_amount = root.find("cac:InvoiceLine/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/puf:PageroExtension/puf:LineExtension/puf:LineExclAllowanceChargeAmount", namespaces).text
	# #item_line_ext_uri = findall("cac:InvoiceLine/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionURI", namespaces).text
	# item_id = ""
	# item_quantity = ""
	# #item_tax_amount = root.find("cac:InvoiceLine/cac:Taxtotal/cbc:TaxAmount", namespaces).text
	# #item_tax_sub_amount = root.find("cac:InvoiceLine/cac:Taxtotal/cac:TaxSubtotal/cbc:TaxAmount", namespaces).text
	# #item_tax_category_id = root.find("cac:InvoiceLine/cac:Taxtotal/cac:TaxSubtotal/cac:TaxCategory/cbc:ID", namespaces).text
	# #item_tax_category_name = root.find("cac:InvoiceLine/cac:Taxtotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Name", namespaces).text
	# item_name = ""
	# #item_commodity_classification = root.find("cac:InvoiceLine/cac:Item/cac:CommodityClassification/cbc:CommodityClassificationCode", namespaces).text
	# item_unit_price = 0
	print(f"Invoice ID: {document_id}")
	print(response_code)
	print(clearance_reference_id)
	print(clearance_qrcode)
	print(clearance_status_code)
	print(clearance_reason)
	
	
	# Connect to SQLite database (adjust path if needed)
	conn = sqlite3.connect("/home/pi/mydjango/e_invoice/db.sqlite3")
	cursor = conn.cursor()
	
	# (Optional) Create table with the expected schema if not exists.
	# Make sure this schema matches your existing table if the table already exists.
	# Create table if not exists
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS e_invoices_invoice (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			status TEXT,
			document_id TEXT UNIQUE,
			invoicetypecode TEXT,
			issue_date TEXT,
			issue_time TEXT,
			document_currency TEXT,
			self_billing TEXT,
			buyer_reference TEXT,
			supplier_name TEXT,
			supplier_tin_id TEXT,
			supplier_brn_id TEXT,
			supplier_id TEXT,
			supplier_addr1 TEXT,
			supplier_addr2 TEXT NULL,
			supplier_addr3 TEXT NULL,
			supplier_addr4 TEXT NULL,
			supplier_country TEXT,
			supplier_scheme_id TEXT, 
			supplier_legal_name TEXT,
			supplier_phone TEXT,
			buyer_name TEXT,
			buyer_supp_assign_id TEXT,
			buyer_id TEXT,
			buyer_tin_id TEXT,
			buyer_brn_id TEXT,
			buyer_addr1 TEXT,
			buyer_addr2 TEXT NULL,
			buyer_addr3 TEXT NULL,
			buyer_addr4 TEXT NULL,
			buyer_scheme_id TEXT,
			buyer_legal_name TEXT,
			buyer_phone TEXT,
			buyer_email TEXT,
			buyer_country TEXT,
			buyer_account_name TEXT,
			buyer_account_phone TEXT,
			buyer_account_email TEXT,
			delivery_addr1 TEXT,
			delivery_addr2 TEXT NULL,
			delivery_addr3 TEXT NULL,
			delivery_addr4 TEXT NULL,
			delivery_country TEXT,
			delivery_tin_id TEXT,
			delivery_name TEXT,
			delivery_id TEXT,
			delivery_scheme_id TEXT,
			tax_amount REAL,
			taxable_amount REAL,
			tax_category TEXT,
			tax_rate REAL,
			tax_scheme_id TEXT,
			tax_scheme_name TEXT,
			tax_exemption TEXT,
			line_ext_amount REAL,
			tax_exclus_amount REAL,
			tax_includ_amount REAL,
			prepaid_amount REAL,
			payable_amount REAL,
			item_id TEXT,
			item_quantity INTEGER,
			item_name TEXT,
			item_unit_price REAL,
			response_code TEXT,
			clearance_reference_id TEXT NULL,
			clearance_qrcode TEXT NULL,
			clearance_status_code TEXT NULL,
			clearance_reason TEXT NULL,
			xml_file_path TEXT
		)
	""")
	conn.commit()
	
	# Insert or Update record based on document_id
	cursor.execute("SELECT COUNT(*) FROM e_invoices_invoice WHERE document_id = ?", (document_id,))
	exists = cursor.fetchone()[0] > 0
	
	if exists:
	    # Prepare update query dynamically based on non-empty values
	    update_fields = ["status = 'completed'"]  # Always update status to "completed"
	    update_values = []
	
	    if response_code:
	        update_fields.append("response_code = ?")
	        update_values.append(response_code)
	    if clearance_reference_id:
	        update_fields.append("clearance_reference_id = ?")
	        update_values.append(clearance_reference_id)
	    if clearance_qrcode:
	        update_fields.append("clearance_qrcode = ?")
	        update_values.append(clearance_qrcode)
	    if clearance_status_code:
	        update_fields.append("clearance_status_code = ?")
	        update_values.append(clearance_status_code)
	    if clearance_reason:
	        update_fields.append("clearance_reason = ?")
	        update_values.append(clearance_reason)
	
	    if update_fields:  # Only execute if there are fields to update
	        update_query = f"UPDATE e_invoices_invoice SET {', '.join(update_fields)} WHERE document_id = ?"
	        update_values.append(document_id)  # Append document_id to values
	
	        cursor.execute(update_query, update_values)
	        conn.commit()
	        print(f"Updated record for document_id: {document_id}")
	    else:
	        print(f"No new values to update for document_id: {document_id}")
	else:
	    print(f"document_id {document_id} not found in database. No updates made.")
	
	# Close database connection
	conn.close()
	print("Database operations complete.")
	
	
