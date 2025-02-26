import os
import xml.etree.ElementTree as ET
from datetime import datetime
import sqlite3

# Define XML namespaces
namespaces = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:pagero:CommonAggregateComponents:1.0",
    "default": "urn:pagero:PageroUniversalFormat:Invoice:1.0",
    "ext": "urn:oasis:name:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "puf": "urn:pagero:ExtensionComponent:1.0",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance" 
}

# Path to XML file in Downloads folder
downloads_folder = os.path.expanduser("/home/pi/Downloads/OriginalXml/")

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
    document_id = root.find("cbc:ID", namespaces).text  # Invoice ID
    invoicetypecode = root.find("cbc:InvoiceTypeCode", namespaces).text
    issue_date = root.find("cbc:IssueDate", namespaces).text
    issue_time = root.find("cbc:IssueTime", namespaces).text
    document_currency = root.find("cbc:DocumentCurrencyCode", namespaces).text
    buyer_reference = root.find("cbc:BuyerReference", namespaces).text

    self_billing_element = root.find("ext:ExtensionContent/puf:PageroExtension/puf:SelfBilled", namespaces)
    self_billing = self_billing_element.text if self_billing_element is not None else ""

    # Extract Supplier Details

    supplier_name = root.find("cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name", namespaces).text
    supplier_tin_id = root.find("cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='MY:TIN']", namespaces).text
    supplier_brn_id = root.find("cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='MY:BRN']", namespaces).text
    supplier_id_element = root.find("cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID", namespaces)
    supplier_id = supplier_id_element.text if supplier_id_element is not None else ""
    supplier_addr1 = root.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:StreetName", namespaces).text
    supplier_addr2 = root.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:CityName", namespaces).text
    supplier_addr3 = root.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:PostalZone", namespaces).text
    supplier_addr4 = root.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:CountrySubentityCode", namespaces).text
    supplier_country = root.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode", namespaces).text
    supplier_scheme_id_element = root.find("cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID", namespaces)
    supplier_scheme_id = supplier_scheme_id_element.text if supplier_scheme_id_element is not None else ""
    supplier_Legal_name = root.find("cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName", namespaces).text 
    supplier_phone_element= root.find("cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:cbc:Telephone", namespaces)
    supplier_phone = supplier_phone_element.text if supplier_phone_element is not None else ""



    # Extract Buyer Details
    buyer_name = root.find("cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name", namespaces).text
    buyer_supp_assign_id_element = root.find("cac:AccountingCustomerParty/cbc:SupplierAssignedAccountID", namespaces)
    buyer_supp_assign_id = buyer_supp_assign_id_element.text if buyer_supp_assign_id_element is not None else ""
    buyer_id = root.find("cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID", namespaces).text 
    buyer_tin_id = root.find("cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='MY:TIN']", namespaces).text
    buyer_brn_id = root.find("cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='MY:BRN']", namespaces).text
    buyer_addr1 = root.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:StreetName", namespaces).text
    buyer_addr2 = root.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:CityName", namespaces).text
    buyer_addr3 = root.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:PostalZone", namespaces).text
    buyer_addr4 = root.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:CountrySubentityCode", namespaces).text
    buyer_scheme_id = root.find("cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID", namespaces).text 
    buyer_Legal_name = root.find("cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName", namespaces).text
    buyer_phone_element = root.find("cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:cbc:Telephone", namespaces)
    buyer_phone = buyer_phone_element.text if buyer_phone_element is not None else ""
    buyer_email_element = root.find("cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:cbc:ElectronicMail", namespaces)
    buyer_email= buyer_email_element.text if buyer_email_element is not None else ""
    buyer_country = root.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode", namespaces).text

    #AccountingContact
    buyer_account_name_element = root.find("cac:AccountingCustomerParty/cac:AccountingContact/cbc:Name", namespaces)
    buyer_account_name =  buyer_email_element.text if buyer_email_element is not None else ""
    buyer_account_phone_element = root.find("cac:AccountingCustomerParty/cac:AccountingContact/cbc:Telephone", namespaces)
    buyer_account_phone =  buyer_account_phone_element.text if buyer_account_phone_element is not None else ""    
    buyer_account_email_element = root.find("cac:AccountingCustomerParty/cac:AccountingContact/cbc:ElectronicMail", namespaces)
    buyer_account_email =  buyer_account_email_element.text if buyer_account_email_element is not None else ""

    #Delivery Details
    delivery_addr1_element = root.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:StreetName", namespaces)
    delivery_addr1  = delivery_addr1_element.text if delivery_addr1_element is not None else ""
    delivery_addr2_element = root.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:CityName", namespaces)
    delivery_addr2  = delivery_addr2_element.text if delivery_addr2_element is not None else ""
    delivery_addr3_element = root.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:PostalZone", namespaces)
    delivery_addr3  = delivery_addr3_element.text if delivery_addr3_element is not None else ""
    delivery_addr4_element = root.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:CountrySubentityCode", namespaces)
    delivery_addr4  = delivery_addr4_element.text if delivery_addr4_element is not None else ""
    delivery_country_element = root.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cac:Country/cbc:IdentificationCode", namespaces)
    delivery_country  = delivery_country_element.text if delivery_country_element is not None else ""
    delivery_tin_id_element = root.find("cac:Delivery/cac:DeliveryParty/cac:PartyIdentification/cbc:ID[@schemeID='MY:TIN']", namespaces)
    delivery_tin_id  = delivery_tin_id_element.text if delivery_tin_id_element is not None else ""
    delivery_name_element = root.find("cac:Delivery/cac:DeliveryParty/cac:PartyName/cbc:Name", namespaces)
    delivery_name  = delivery_name_element.text if delivery_name_element is not None else ""
    delivery_id_element = root.find("cac:Delivery/cac:DeliveryParty/cac:PartyTaxScheme/cbc:CompanyID", namespaces)
    delivery_id  = delivery_id_element.text if delivery_id_element is not None else ""
    delivery_scheme_id_element = root.find("cac:Delivery/cac:DeliveryParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID", namespaces)
    delivery_scheme_id = delivery_scheme_id_element.text if delivery_scheme_id_element is not None else ""


    # Extract Tax Details
    tax_amount = root.find("cac:TaxTotal/cbc:TaxAmount", namespaces).text
    taxable_amount = root.find("cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount", namespaces).text
    tax_category = root.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:ID", namespaces).text
    tax_rate = root.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent", namespaces).text
    tax_scheme_id = root.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID", namespaces).text
    tax_scheme_name = root.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name", namespaces).text
    tax_exemption_element = root.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TaxExemptionReason", namespaces)
    tax_exemption = tax_exemption_element.text if tax_exemption_element is not None else ""


    # Extract Monetary Totals
    line_ext_amount = root.find("cac:LegalMonetaryTotal/cbc:LineExtensionAmount", namespaces).text
    tax_exclus_amount = root.find("cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount", namespaces).text
    tax_includ_amount = root.find("cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount", namespaces).text
    prepaid_amount_element = root.find("cac:LegalMonetaryTotal/cbc:PrepaidAmount", namespaces)
    prepaid_amount = prepaid_amount_element.text if prepaid_amount_element is not None else ""

    payable_amount_element = root.find("cac:LegalMonetaryTotal/cbc:PayableAmount", namespaces)
    payable_amount = payable_amount_element.text if payable_amount_element is not None else ""

    # Extract Item Details
    #print(ET.tostring(root, encoding='utf8').decode('utf8'))

    #item_line_excl_allowance_charge_amount = root.find("cac:InvoiceLine/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/puf:PageroExtension/puf:LineExtension/puf:LineExclAllowanceChargeAmount", namespaces).text
    #item_line_ext_uri = findall("cac:InvoiceLine/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionURI", namespaces).text
    item_id = root.find("cac:InvoiceLine/cbc:ID", namespaces).text
    item_quantity = root.find("cac:InvoiceLine/cbc:InvoicedQuantity", namespaces).text
    #item_tax_amount = root.find("cac:InvoiceLine/cac:Taxtotal/cbc:TaxAmount", namespaces).text
    #item_tax_sub_amount = root.find("cac:InvoiceLine/cac:Taxtotal/cac:TaxSubtotal/cbc:TaxAmount", namespaces).text
    #item_tax_category_id = root.find("cac:InvoiceLine/cac:Taxtotal/cac:TaxSubtotal/cac:TaxCategory/cbc:ID", namespaces).text
    #item_tax_category_name = root.find("cac:InvoiceLine/cac:Taxtotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Name", namespaces).text
    item_name = root.find("cac:InvoiceLine/cac:Item/cbc:Name", namespaces).text
    #item_commodity_classification = root.find("cac:InvoiceLine/cac:Item/cac:CommodityClassification/cbc:CommodityClassificationCode", namespaces).text
    item_unit_price = root.find("cac:InvoiceLine/cac:Price/cbc:PriceAmount", namespaces).text
    response_code = ""
    clearance_reference_id = ""
    clearance_qrcode = ""
    clearance_status_code = ""
    clearance_reason = ""


    # Print extracted data
    # Print all parsed values in a structured way

    print("----- Document Details -----")
    print(f"Invoice ID: {document_id}")
    print(f"Invoice Type: {invoicetypecode}")
    print(f"Posting Date: {issue_date}")
    print(f"Issue Time: {issue_time}")
    print(f"Document Currency: {document_currency}")
    print(f"Buyer Reference: {buyer_reference}")
    print(f"Self-Billing: {self_billing}")

    print("\n----- Supplier Details -----")
    print(f"Supplier Name: {supplier_name}")
    print(f"Supplier TIN ID: {supplier_tin_id}")
    print(f"Supplier BRN ID: {supplier_brn_id}")
    print(f"Supplier Company ID: {supplier_id}")
    print(f"Supplier Address: {supplier_addr1}, {supplier_addr2}, {supplier_addr3}, {supplier_addr4}")
    print(f"Supplier Country: {supplier_country}")
    print(f"Supplier Legal Name: {supplier_Legal_name}")
    print(f"Supplier Phone: {supplier_phone}")

    print("\n----- Buyer Details -----")
    print(f"Buyer Name: {buyer_name}")
    print(f"Buyer ID: {buyer_id}")
    print(f"Buyer TIN ID: {buyer_tin_id}")
    print(f"Buyer BRN ID: {buyer_brn_id}")
    print(f"Buyer Address: {buyer_addr1}, {buyer_addr2}, {buyer_addr3}, {buyer_addr4}")
    print(f"Buyer Scheme ID: {buyer_scheme_id}")
    print(f"Buyer Legal Name: {buyer_Legal_name}")
    print(f"Buyer Phone: {buyer_phone}")
    print(f"Buyer Email: {buyer_email}")
    print(f"Buyer Country: {buyer_country}")

    print("\n----- Accounting Contact -----")
    print(f"Buyer Account Name: {buyer_account_name}")
    print(f"Buyer Account Phone: {buyer_account_phone}")
    print(f"Buyer Account Email: {buyer_account_email}")

    print("\n----- Delivery Details -----")
    print(f"Delivery Name: {delivery_name}")
    print(f"Delivery Address: {delivery_addr1}, {delivery_addr2}, {delivery_addr3}, {delivery_addr4}")
    print(f"Delivery Country: {delivery_country}")
    print(f"Delivery TIN ID: {delivery_tin_id}")
    print(f"Delivery ID: {delivery_id}")
    print(f"Delivery Scheme ID: {delivery_scheme_id}")

    print("\n----- Tax Details -----")
    print(f"Tax Amount: {tax_amount}")
    print(f"Taxable Amount: {taxable_amount}")
    print(f"Tax Rate: {tax_rate}")
    print(f"Tax Category: {tax_category}")
    print(f"Tax Scheme ID: {tax_scheme_id}")
    print(f"Tax Scheme Name: {tax_scheme_name}")
    print(f"Tax Exemption Reason: {tax_exemption}")

    print("\n----- Monetary Totals -----")
    print(f"Line Extension Amount: {line_ext_amount}")
    print(f"Tax Exclusive Amount: {tax_exclus_amount}")
    print(f"Tax Inclusive Amount: {tax_includ_amount}")
    print(f"Prepaid Amount: {prepaid_amount}")
    print(f"Payable Amount: {payable_amount}")

    print("\n----- Item Details -----")
    print(f"Item ID: {item_id}")
    print(f"Item Name: {item_name}")
    print(f"Item Quantity: {item_quantity}")
    print(f"Item Unit Price: {item_unit_price}")






    # Connect to SQLite database (adjust path if needed)
    conn = sqlite3.connect("/home/pi/mydjango/e_invoice/db.sqlite3")
    cursor = conn.cursor()

# (Optional) Create table with the expected schema if not exists.
# Make sure this schema matches your existing table if the table already exists.
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
            response_code, TEXT,
            clearance_referece_id, TEXT
            clearance_qrcode, TEXT
            clearance_status_code, TEXT
            clearance_reason, TEXT
            xml_file_path TEXT
        )
    """)
    conn.commit()
        #response_code, TEXT,
        #clearance_referece_id, TEXT
        #clearance_qrcode, TEXT
        #clearance_status_code, TEXT
        #clearance_resason, TEXT
# Insert extracted data into the table by supplying a value for status.
    cursor.execute("""
        INSERT OR IGNORE INTO e_invoices_invoice (
            status, document_id, invoicetypecode, issue_date, issue_time, document_currency, self_billing, buyer_reference,
            supplier_name, supplier_tin_id, supplier_brn_id, supplier_id, supplier_addr1, supplier_addr2,
            supplier_addr3, supplier_addr4, supplier_country, supplier_scheme_id, supplier_Legal_name,
            supplier_phone, buyer_name, buyer_supp_assign_id, buyer_id, buyer_tin_id, buyer_brn_id, buyer_addr1,
            buyer_addr2, buyer_addr3, buyer_addr4, buyer_scheme_id, buyer_Legal_name, buyer_phone, buyer_email,
            buyer_country, buyer_account_name, buyer_account_phone, buyer_account_email, delivery_addr1,
            delivery_addr2, delivery_addr3, delivery_addr4, delivery_country, delivery_tin_id, delivery_name,
            delivery_id, delivery_scheme_id, tax_amount, taxable_amount, tax_category, tax_rate, tax_scheme_id,
            tax_scheme_name, tax_exemption, line_ext_amount, tax_exclus_amount, tax_includ_amount, prepaid_amount,
            payable_amount, item_id, item_quantity, item_name, item_unit_price, response_code, clearance_reference_id,
            clearance_qrcode, clearance_status_code, clearance_reason, xml_file_path
        ) 
        VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
        ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "created", document_id, invoicetypecode, issue_date, issue_time, document_currency, self_billing, buyer_reference,
        supplier_name, supplier_tin_id, supplier_brn_id, supplier_id, supplier_addr1, supplier_addr2,
        supplier_addr3, supplier_addr4, supplier_country, supplier_scheme_id, supplier_Legal_name,
        supplier_phone, buyer_name, buyer_supp_assign_id, buyer_id, buyer_tin_id, buyer_brn_id, buyer_addr1,
        buyer_addr2, buyer_addr3, buyer_addr4, buyer_scheme_id, buyer_Legal_name, buyer_phone, buyer_email,
        buyer_country, buyer_account_name, buyer_account_phone, buyer_account_email, delivery_addr1,
        delivery_addr2, delivery_addr3, delivery_addr4, delivery_country, delivery_tin_id, delivery_name,
        delivery_id, delivery_scheme_id, tax_amount, taxable_amount, tax_category, tax_rate, tax_scheme_id,
        tax_scheme_name, tax_exemption, line_ext_amount, tax_exclus_amount, tax_includ_amount, prepaid_amount,
        payable_amount, item_id, item_quantity, item_name, item_unit_price, response_code, clearance_reference_id,
        clearance_qrcode, clearance_status_code, clearance_reason, xml_file_path
    ))


    conn.commit()

    # For debugging: print out rows in the table
    cursor.execute("SELECT * FROM e_invoices_invoice;")
    rows = cursor.fetchall()
    #print("Rows in e_invoices_invoice:", rows)

    conn.close()
    print("Database operations complete.") 
