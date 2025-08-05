import os
import xml.etree.ElementTree as LET
from django.db import transaction
from e_invoices.models import Company, CompanyNotificationConfig, TWB2BMainItemInS, TWB2BLineItemInS
from django.utils.timezone import localtime, now
from datetime import timedelta, date
def process_all_E0502_xml():

    today = now().date()

    # 計算本期雙月期別（例：11408）
    if today.month % 2 == 0:
        current_month = today.month
    else:
        current_month = today.month + 1  # 奇數月則歸入下一個偶數月
    roc_year = today.year - 1911  # 民國年
    current_period = int(f"{roc_year}{str(current_month).zfill(2)}")  # 例如 11408

    # 計算前一期（往前推2個月）
    if current_month == 1:
        previous_roc_year = roc_year - 1
        previous_month = 11
    else:
        previous_roc_year = roc_year
        previous_month = current_month - 2

    previous_period = int(f"{previous_roc_year}{str(previous_month).zfill(2)}")  # 例如 11406

    # 快取兩期內所有發票號碼與對應實例
    invoice_cache = {
        i.invoice_number: i
        for i in TWB2BMainItemInS.objects.filter(
            invoice_period__in=[current_period, previous_period]
        )
    }

    companies = Company.objects.all()
    for company in companies:
        company_id = company.company_id
        configs = CompanyNotificationConfig.objects.filter(company__company_id=company_id).first()

        if configs:
            input_dir_E0502 = configs.input_dir_E0502
            ns = {'E0502': 'urn:GEINV:E0502:4.0'}
            files = [f for f in os.listdir(input_dir_E0502) if f.lower().endswith('.xml')]
            
            for filename in files:
                full_path = os.path.join(input_dir_E0502, filename)
                try:
                    ns = {"e0502": "urn:GEINV:eInvoiceMessage:E0502:4.0"}
                    tree = LET.parse(full_path)
                    root = tree.getroot()

                    main = root.find("e0502:Main", ns)
                    invoice_number = main.findtext("e0502:InvoiceNumber", namespaces=ns)
                    invoice_date = main.findtext("e0502:InvoiceDate", namespaces=ns)
                    invoice_time = main.findtext("e0502:InvoiceTime", namespaces=ns)
                    invoice_status = main.findtext("e0502:CurrentStatus", namespaces=ns)
                    seller_id = main.findtext("e0502:SellerId", namespaces=ns)
                    seller_name = main.findtext("e0502:SellerName", namespaces=ns) #option
                    buyer_id = main.findtext("e0502:BuyerId", namespaces=ns)
                    buyer_name = main.findtext("e0502:BuyerName", namespaces=ns) #option
                    buyer_remark = main.findtext("e0502:BuyerRemark", namespaces=ns) #option
                    main_remark = main.findtext("e0502:MainRemark",namepsaces=ns) #option
                    customs_clearance_mark = main.findtext("e0502:CustomsClearanceMark",namespaces=ns) #option
                    category = main.findtext("e0502:Category", namesapces=ns) #option <!-- 沖帳別 -->
                    relate_number = main.findtext("e0502:RelateNumber", namespaces=ns) #option
                    invoice_type = main.findtext("e0502:InvoiceType", namespaces=ns) #option
                    group_mark = main.findtext("e0502:GroupMark",namespaces=ns) #option
                    donate_mark = main.findtext("e0502:DonateMark", namespaces=ns) #option
                    carrier_type = main.findtext("e0502:CarrierType", namespaces=ns)#option
                    carrier_id1=main.findtext("e0502:CarrierId1", namespaces=ns)#option
                    carrier_id2=main.findtext("e0502:CarrierId2", namespaces=ns)#option
                    print_mark = main.findtext("e0502:PrintMark", namespaces=ns)#option
                    npoban = main.findtext("e0502:NPOBAN", namespaces=ns)#option
                    random_number = main.findtext("e0502:RandomNumber", namespaces=ns)#option
                    bonded_area_confirm = main.findtext("e0502:BondedAreaConfirm", namespaces=ns)#option
                    zero_tax_rate_reason = main.findtext("e0502:ZeroTaxRateReason", namespaces=ns)#option
                    reserved1 = main.findtext("e0502:Reserved1", namespaces=ns)
                    reserved2 = main.findtext("e0502:Reserved2", namespaces=ns)

                    details = root.find("e0502:Details", ns)
                    production_items = details.findall("e0502:ProductionItem", ns)
                    # for item in production_items:
                    #     # 逐一解析欄位
                    #     line_description = item.findtext("e0502:Description", namespaces=ns)
                    #     line_quantity = float(item.findtext("e0502:Quantity", namespaces=ns) or 0)
                    #     unit = item.findtext("e0502:Unit", namespaces=ns)
                    #     unit_price = float(item.findtext("e0502:UnitPrice", namespaces=ns) or 0)
                    #     tax_type = item.findtext("e0502:TaxType", namespaces=ns)
                    #     amount = float(item.findtext("e0502:Amount", namespaces=ns) or 0)
                    #     sequence_number = int(item.findtext("e0502:SequenceNumber", namespaces=ns) or 0)
                    #     remark = item.findtext("e0502:Remark", namespaces=ns)
                    
                    amount = root.find("e0502:Amount", ns)
                    sales_amount = amount.findtext("e0502:SalesAmount", namespaces=ns)
                    freetax_sales_amount = amount.findtext("e0502:FreeTaxSalesAmount", namespaces=ns)
                    zero_tax_rate_reason = amount.findtext("e0502:ZeroTaxSalesAmount", namespaces=ns)
                    tax_type = amount.findtext("e0502:TaxType", namespaces=ns)
                    tax_rate = amount.findtext("e0502:TaxRate", namespaces=ns)
                    tax_amount = amount.findtext("e0502:TaxAmount", namespaces=ns)
                    discount_amount = amount.findtext("e0502:DiscountAmount",namespaces=ns)
                    original_currency_amuont = amount.findtext("e0502:OriginalCurrencyAmount",namespaces=ns)
                    exchange_rate = amount.findtext("e0502:ExchangeRate", namespaces=ns)
                    currency = amount.findtext("e0502:Currency", namespaces=ns)
                    total_amount = amount.findtext("e0502:TotalAmount", namespaces=ns)

                    cancel = root.find("e0502:Cancel",ns)
                    cancel_date = cancel.findtext("e0502:CancelDate", namespaces=ns)
                    cancel_time = cancel.findtext("e0502:CancelTime", namespaces=ns)
                    cancel_reason = cancel.findtext("e0502:CancelReason", namespaces=ns)
                    returntax_document_number = cancel.findtext("e0502:ReturnTaxDocumentNumber", namespaces=ns) #option
                    cancel_remark = cancel.findtext("e0502:CancelRemark", namespaces=ns) #option
                    reserved1 = cancel.findtext("e0502:Reserved1", namespaces=ns) #option
                    reserved2 = cancel.findtext("e0502:Reserved2", namespaces=ns) #option

                    reject = root.find("e0502:Reject", ns)
                    reject_date = reject.findtext("e0502:RejectDate", namespaces = ns )
                    reject_time = reject.findtext("e0502:RejectTime", namespaces = ns )
                    reject_reason = reject.findtext("e0502:RejectReason", namespaces = ns) #option
                    reject_remark = reject.findtext("e0502:RejectReMark", namespaces = ns) #option


                    with transaction.atomic():
                        if invoice_number in invoice_cache:
                            invoice = invoice_cache[invoice_number]
                            invoice.invoice_status = invoice_status
                            invoice.cancel_date = cancel_date
                            invoice.cancel_time = cancel_time
                            invoice.cancel_reason = cancel_reason
                            returntax_document_number = returntax_document_number
                            cancel_remark = cancel_remark
                            invoice.reject_date = reject_date
                            invoice.reject_time = reject_time
                            invoice.reject_reason = reject_reason
                            invoice.reject_remark =reject_remark
                            invoice.save()
                        else:
                            invoice = TWB2BMainItemInS.objects.create(
                                company=company,
                                invoice_number=invoice_number,
                                invoice_date=invoice_date,
                                invoice_time=invoice_time,
                                invoice_status=invoice_status,
                                seller_id = seller_id,
                                seller_name = seller_name,
                                buyer_identifier=buyer_id,
                                buyer_name=buyer_name,
                                buyer_remark = buyer_remark,
                                customs_clearance_mark = customs_clearance_mark,
                                category = category,
                                relate_number = relate_number,
                                invoice_type = invoice_type,
                                group_mark = group_mark,
                                donate_mark = donate_mark,
                                carrier_type = carrier_type,
                                carrier_id1 = carrier_id1,
                                carrier_id2 = carrier_id2,
                                print_mark = print_mark,
                                npoban = npoban,
                                random_number = random_number,
                                bonded_area_confirm = bonded_area_confirm,
                                zero_tax_rate_reason = zero_tax_rate_reason,
                                reserved1 = reserved1,
                                reserved2 = reserved2,
                                main_remark = main_remark,
                                sales_amount = sales_amount,
                                freetax_sales_amount =freetax_sales_amount,
                                tax_type = tax_type,
                                tax_rate = tax_rate,
                                tax_amount = tax_amount,
                                discount_amount = discount_amount,
                                original_currency_amuont = original_currency_amuont,
                                exchange_rate = exchange_rate,
                                currency = currency,
                                total_amount=total_amount,
                                

                            )

                            invoice_cache[invoice_number] = invoice  # 立即補入快取
                            line_items = []

                            for item in production_items:
                                line_items.append(TWB2BLineItemInS(
                                    twb2bmainitemins=invoice,
                                    erp_number=invoice.erp_number,
                                    line_sequence_number=item.findtext("e0502:SequenceNumber", namespaces=ns),
                                    line_description=item.findtext("e0502:Description", namespaces=ns),
                                    line_quantity=item.findtext("e0502:Quantity", namespaces=ns),
                                    line_unit=item.findtext("e0502:Unit", namespaces=ns),
                                    line_unit_price=item.findtext("e0502:UnitPrice", namespaces=ns) or 0,
                                    line_tax_type=item.findtext("e0502:TaxType", namespaces=ns),
                                    line_amount=item.findtext("e0502:Amount", namespaces=ns) or 0,
                                    line_remark=item.findtext("e0502:Remark", namespaces=ns),
                                    line_relate_number=item.findtext("e0502:RelateNumber", namespaces=ns),
                                ))
                            TWB2BLineItemInS.objects.bulk_create(line_items)
                            invoice_cache[invoice_number] = invoice

                except Exception as e:
                    print(f"處理檔案 {filename} 時發生錯誤: {e}")
