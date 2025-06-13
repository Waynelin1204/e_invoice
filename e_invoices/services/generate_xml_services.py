import lxml.etree as LET
from io import BytesIO
from django.conf import settings
from e_invoices.models import TWB2BMainItem
import os

def generate_f0401_xml_files(invoice, output_dir, xsd_path, random_code):
    output_paths = []

    # Load XSD schema once
    with open(xsd_path, 'rb') as f:
        schema_doc = LET.parse(f)
        schema = LET.XMLSchema(schema_doc)

    nsmap = {None: "urn:GEINV:eInvoiceMessage:F0401:4.0"}
    root = LET.Element("Invoice", nsmap=nsmap)

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
