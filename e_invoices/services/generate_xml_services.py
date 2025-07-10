import lxml.etree as LET
from io import BytesIO
from django.conf import settings
from e_invoices.models import TWB2BMainItem
import os

def generate_F0401_xml_files(invoice, output_dir, xsd_path, random_code):
    output_paths = []

    # Load XSD schema once
    with open(xsd_path, 'rb') as f:
        schema_doc = LET.parse(f)
        schema = LET.XMLSchema(schema_doc)

    nsmap = {
        None: "urn:GEINV:eInvoiceMessage:F0401:4.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        
    }
    root = LET.Element("Invoice", nsmap=nsmap)
    root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "urn:GEINV:eInvoiceMessage:F0401:4.0 F0401.xsd")


    # ─── Main ───
    main = LET.SubElement(root, "Main")
    LET.SubElement(main, "InvoiceNumber").text = invoice.invoice_number
    LET.SubElement(main, "InvoiceDate").text = invoice.invoice_date.strftime("%Y%m%d")  # Format fixed
    LET.SubElement(main, "InvoiceTime").text = invoice.invoice_time

    seller = LET.SubElement(main, "Seller")
    LET.SubElement(seller, "Identifier").text = invoice.company.company_identifier.zfill(8)  # Ensure minLength=8
    LET.SubElement(seller, "Name").text = invoice.company.company_name
    if invoice.company.company_address:
        LET.SubElement(seller, "Address").text = invoice.company.company_address  # Fix: was 'Adress'

    buyer = LET.SubElement(main, "Buyer")
    LET.SubElement(buyer, "Identifier").text = invoice.buyer_identifier.zfill(8)
    LET.SubElement(buyer, "Name").text = invoice.buyer_name

    if invoice.buyer_remark:
        LET.SubElement(main, "BuyerRemark").text = invoice.buyer_remark
    if invoice.main_remark:
        LET.SubElement(main, "MainRemark").text = invoice.main_remark
    LET.SubElement(main, "InvoiceType").text = invoice.invoice_type
    LET.SubElement(main, "DonateMark").text = invoice.donate_mark or "0"
    LET.SubElement(main, "PrintMark").text = invoice.print_mark or "Y"
    # if invoice.carrier_type:
    #     LET.SubElement(main, "CarrierType").text = invoice.carrier_type
    # if invoice.carrier_id1:
    #     LET.SubElement(main, "CarrierId1").text = invoice.carrier_id1
    # if invoice.carrier_id2:
    #     LET.SubElement(main, "CarrierId2").text = invoice.carrier_id2
    if random_code:
        LET.SubElement(main, "RandomNumber").text = random_code
    if invoice.bonded_area_confirm:
        LET.SubElement(main, "BondedAreaConfirm").text = invoice.bonded_area_confirm
    if invoice.zero_tax_rate_reason:
        LET.SubElement(main, "ZeroTaxRateReason").text = invoice.zero_tax_rate_reason

    # ─── Details ───
    details = LET.SubElement(root, "Details")
    for item in invoice.items.all():
        product = LET.SubElement(details, "ProductItem")
        LET.SubElement(product, "Description").text = item.line_description
        LET.SubElement(product, "Quantity").text = str(item.line_quantity)
        if item.line_unit:
            LET.SubElement(product, "Unit").text = item.line_unit
        LET.SubElement(product, "UnitPrice").text = str(item.line_unit_price)
        LET.SubElement(product, "TaxType").text = item.line_tax_type
        LET.SubElement(product, "Amount").text = str(item.line_amount)
        LET.SubElement(product, "SequenceNumber").text = str(item.line_sequence_number)
        if item.line_remark:
            LET.SubElement(product, "Remark").text = item.line_remark
        if item.line_relate_number:
            LET.SubElement(product, "RelateNumber").text = item.line_relate_number

    # ─── Amount ───
    amount = LET.SubElement(root, "Amount")
    LET.SubElement(amount, "SalesAmount").text = str(int(invoice.sales_amount))
    LET.SubElement(amount, "FreeTaxSalesAmount").text = str(int(invoice.freetax_sales_amount))
    LET.SubElement(amount, "ZeroTaxSalesAmount").text = str(int(invoice.zerotax_sales_amount))
    LET.SubElement(amount, "TaxType").text = invoice.tax_type
    LET.SubElement(amount, "TaxRate").text = str(invoice.tax_rate or 0.0)
    LET.SubElement(amount, "TaxAmount").text = str(int(invoice.total_tax_amount))
    LET.SubElement(amount, "TotalAmount").text = str(int(invoice.total_amount))
    if invoice.discount_amount:
        LET.SubElement(amount, "DiscountAmount").text = str(int(invoice.discount_amount))
    if invoice.original_currency_amount:
        LET.SubElement(amount, "OriginalCurrencyAmount").text = str(int(invoice.original_currency_amount))
    if invoice.exchange_rate:
        LET.SubElement(amount, "ExchangeRate").text = str(invoice.exchange_rate)
    if invoice.currency:
        LET.SubElement(amount, "Currency").text = invoice.currency

    # Convert XML tree to bytes
    xml_bytes = LET.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)

    # Validate XML against schema
    doc = LET.fromstring(xml_bytes)
    if not schema.validate(doc):
        errors = "\n".join([str(e) for e in schema.error_log])
        raise ValueError(f"XSD validation failed for invoice {invoice.invoice_number}:\n{errors}")

    # Write validated XML to file
    filename = f"F0401_{invoice.invoice_number}.xml"
    full_path = os.path.join(output_dir, filename)
    with open(full_path, "wb") as f:
        f.write(xml_bytes)

    output_paths.append(full_path)

    return output_paths

def generate_F0501_xml_files(invoice, output_dir, xsd_path):
    output_paths = []

    # Load XSD schema once
    with open(xsd_path, 'rb') as f:
        schema_doc = LET.parse(f)
        schema = LET.XMLSchema(schema_doc)

    nsmap = {
        None: "urn:GEINV:eInvoiceMessage:F0501:4.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        
    }
    root = LET.Element("CancelInvoice", nsmap=nsmap)
    root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "urn:GEINV:eInvoiceMessage:F0501:4.0 F0501.xsd")

    
    LET.SubElement(root, "CancelInvoiceNumber").text = invoice.invoice_number
    LET.SubElement(root, "InvoiceDate").text = invoice.invoice_date.strftime("%Y%m%d")
    LET.SubElement(root, "BuyerId").text = invoice.buyer_identifier.zfill(8)
    LET.SubElement(root, "SellerId").text = invoice.company.company_identifier.zfill(8)
    LET.SubElement(root, "CancelDate").text = invoice.cancel_date.strftime("%Y%m%d")
    LET.SubElement(root, "CancelTime").text = invoice.cancel_time.strftime("%H:%M:%S")
    LET.SubElement(root, "CancelReason").text = invoice.cancel_reason

    if invoice.returntax_document_number:
        LET.SubElement(root, "ReturnTaxDocumentNumber").text = invoice.returntax_document_number
    if invoice.cancel_remark:
        LET.SubElement(root, "Remark").text = invoice.cancel_remark

    # Convert XML tree to bytes
    xml_bytes = LET.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)

    doc = LET.fromstring(xml_bytes)
    if not schema.validate(doc):
        errors = "\n".join([str(e) for e in schema.error_log])
        raise ValueError(f"XSD validation failed for cancel invoice {invoice.invoice_number}:\n{errors}")

    # Write validated XML to file
    filename = f"F0501_{invoice.invoice_number}.xml"
    full_path = os.path.join(output_dir, filename)
    with open(full_path, "wb") as f:
        f.write(xml_bytes)

    return full_path

def generate_F0701_xml_files(invoice, output_dir, xsd_path):
    output_paths = []

    # Load XSD schema once
    with open(xsd_path, 'rb') as f:
        schema_doc = LET.parse(f)
        schema = LET.XMLSchema(schema_doc)

    nsmap = {
        None: "urn:GEINV:eInvoiceMessage:F0701:4.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        
    }
    root = LET.Element("VoidInvoice", nsmap=nsmap)
    root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "urn:GEINV:eInvoiceMessage:F0701:4.0 F0701.xsd")

    
    LET.SubElement(root, "VoidInvoiceNumber").text = invoice.invoice_number
    LET.SubElement(root, "InvoiceDate").text = invoice.invoice_date.strftime("%Y%m%d")
    LET.SubElement(root, "BuyerId").text = invoice.buyer_identifier.zfill(8)
    LET.SubElement(root, "SellerId").text = invoice.company.company_identifier.zfill(8)
    LET.SubElement(root, "VoidDate").text = invoice.void_date.strftime("%Y%m%d")
    LET.SubElement(root, "VoidTime").text = invoice.void_time.strftime("%H:%M:%S")
    LET.SubElement(root, "VoidReason").text = invoice.void_reason
    if invoice.void_remark:
        LET.SubElement(root, "Remark").text = invoice.void_reason

    # Convert XML tree to bytes
    xml_bytes = LET.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)

    doc = LET.fromstring(xml_bytes)
    if not schema.validate(doc):
        errors = "\n".join([str(e) for e in schema.error_log])
        raise ValueError(f"XSD validation failed for cancel invoice {invoice.invoice_number}:\n{errors}")

    # Write validated XML to file
    filename = f"F0701_{invoice.invoice_number}.xml"
    full_path = os.path.join(output_dir, filename)
    with open(full_path, "wb") as f:
        f.write(xml_bytes)

    return full_path

def generate_G0401_xml_files(allowance, output_dir, xsd_path):
    output_paths = []

    # Load XSD schema once
    with open(xsd_path, 'rb') as f:
        schema_doc = LET.parse(f)
        schema = LET.XMLSchema(schema_doc)

    nsmap = {
        None: "urn:GEINV:eInvoiceMessage:G0401:4.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    root = LET.Element("Allowance", nsmap=nsmap)
    root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "urn:GEINV:eInvoiceMessage:G0401:4.0 G0401.xsd")
    # ─── Main ───
    main = LET.SubElement(root, "Main")
    LET.SubElement(main, "AllowanceNumber").text = allowance.allowance_number
    LET.SubElement(main, "AllowanceDate").text = allowance.allowance_date.strftime("%Y%m%d")  # Format fixed

    seller = LET.SubElement(main, "Seller")
    LET.SubElement(seller, "Identifier").text = allowance.company.company_identifier.zfill(8)  # Ensure minLength=8
    LET.SubElement(seller, "Name").text = allowance.company.company_name
    if allowance.company.company_address:
        LET.SubElement(seller, "Address").text = allowance.company.company_address  # Fix: was 'Adress'
    # if allowance.person_in_charge:
    #     LET.SubElement(seller, "PersonInCharge").text = allowance.person_in_charge
    # if allowance.telephone_number:
    #     LET.SubElement(seller, "TelephoneNumber").text = allowance.telephone_number
    # if allowance.facsimile_number:
    #     LET.SubElement(seller, "FacsimileNumber").text = allowance.facsimile
    # if allowance.email_address:
    #     LET.SubElement(seller, "EmailAddress").text = allowance.email_address
    # if allowance.customer_number:
    #     LET.SubElement(seller, "CustomerNumber").text = allowance.customer_number
    # if allowance.role_remark:
    #     LET.SubElement(seller, "RoleRemark").text = allowance.role_remark


    buyer = LET.SubElement(main, "Buyer")
    LET.SubElement(buyer, "Identifier").text = allowance.buyer_identifier.zfill(8)
    LET.SubElement(buyer, "Name").text = allowance.buyer_name
    # if allowance.buyer_address:
    #     LET.SubElement(buyer, "Address").text = allowance.buyer_address  # Fix: was 'Adress'
    # if allowance.person_in_charge:
    #     LET.SubElement(buyer, "PersonInCharge").text = allowance.person_in_charge
    # if allowance.telephone_number:
    #     LET.SubElement(buyer, "TelephoneNumber").text = allowance.buyer_telephone_number
    # if allowance.facsimile_number:
    #     LET.SubElement(buyer, "FacsimileNumber").text = allowance.buyer_facsimile
    # if allowance.email_address:
    #     LET.SubElement(buyer, "EmailAddress").text = allowance.buyer_email_address
    # if allowance.customer_number:
    #     LET.SubElement(buyer, "CustomerNumber").text = allowance.buyer_customer_number
    # if allowance.role_remark:
    #     LET.SubElement(buyer, "RoleRemark").text = allowance.role_remark

    LET.SubElement(main, "AllowanceType").text = allowance.allowance_type

    # ─── Details ───
    details = LET.SubElement(root, "Details")
    for item in allowance.items.all():
        product = LET.SubElement(details, "ProductItem")
        LET.SubElement(product, "OriginalInvoiceDate").text = item.line_original_invoice_date.strftime("%Y%m%d")  # Format fixed
        LET.SubElement(product, "OriginalInvoiceNumber").text = str(item.line_original_invoice_number)
        if item.line_sequence_number:
            LET.SubElement(product, "OriginalSequenceNumber").text = str(item.line_sequence_number)
        LET.SubElement(product, "OriginalDescription").text = str(item.line_description)
        if item.line_unit:
            LET.SubElement(product, "Unit").text = item.line_unit
        LET.SubElement(product, "Quantity").text = str(item.line_quantity)
        LET.SubElement(product, "UnitPrice").text = str(item.line_unit_price)
        LET.SubElement(product, "Amount").text = str(item.line_allowance_amount)
        LET.SubElement(product, "AllowanceSequenceNumber").text = str(item.line_sequence_number)
        LET.SubElement(product, "Tax").text = str(item.line_allowance_tax)
        LET.SubElement(product, "TaxType").text = str(item.line_tax_type)
    # ─── Amount ───
    amount = LET.SubElement(root, "Amount")
    LET.SubElement(amount, "TaxAmount").text = str(int(allowance.allowance_tax))
    LET.SubElement(amount, "TotalAmount").text = str(int(allowance.allowance_amount))

    # Convert XML tree to bytes
    xml_bytes = LET.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)

    # Validate XML against schema
    doc = LET.fromstring(xml_bytes)
    if not schema.validate(doc):
        errors = "\n".join([str(e) for e in schema.error_log])
        raise ValueError(f"XSD validation failed for allowance {allowance.allowance_number}:\n{errors}")

    # Write validated XML to file 
    filename = f"G0401_{allowance.allowance_number}.xml"
    full_path = os.path.join(output_dir, filename)
    with open(full_path, "wb") as f:
        f.write(xml_bytes)

    output_paths.append(full_path)

    return output_paths

def generate_G0501_xml_files(allowance, output_dir, xsd_path):
    output_paths = []

    # Load XSD schema once
    with open(xsd_path, 'rb') as f:
        schema_doc = LET.parse(f)
        schema = LET.XMLSchema(schema_doc)

    nsmap = {
        None: "urn:GEINV:eInvoiceMessage:G0501:4.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    root = LET.Element("CancelAllowance", nsmap=nsmap)
    root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "urn:GEINV:eInvoiceMessage:G0501:4.0 G0501.xsd")

    LET.SubElement(root, "CancelAllowanceNumber").text = allowance.allowance_number
    LET.SubElement(root, "AllowanceType").text = allowance.allowance_type
    LET.SubElement(root, "AllowanceDate").text = allowance.allowance_date.strftime("%Y%m%d")  # Format fixed
    LET.SubElement(root, "BuyerId").text = allowance.buyer_identifier.zfill(8)
    LET.SubElement(root, "SellerId").text = allowance.company.company_identifier.zfill(8)
    LET.SubElement(root, "CancelDate").text = allowance.allowance_cancel_date.strftime("%Y%m%d")
    LET.SubElement(root, "CancelTime").text = allowance.allowance_cancel_time.strftime("%H:%M:%S")
    LET.SubElement(root, "CancelReason").text = allowance.allowance_cancel_reason
    if allowance.allowance_cancel_remark:
        LET.SubElement(root, "Remark").text = allowance.allowance_cancel_remark

    # Convert XML tree to bytes
    xml_bytes = LET.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)

    doc = LET.fromstring(xml_bytes)
    if not schema.validate(doc):
        errors = "\n".join([str(e) for e in schema.error_log])
        raise ValueError(f"XSD validation failed for cancel invoice {allowance.allowance_number}:\n{errors}")

    # Write validated XML to file
    filename = f"G0501_{allowance.allowance_number}.xml"
    full_path = os.path.join(output_dir, filename)
    with open(full_path, "wb") as f:
        f.write(xml_bytes)

    return full_path
