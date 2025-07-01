# e_invoices/services/email_summary_service.py

from e_invoices.services.auto_send_email_service import send_email_to_customer_outlook
from django.template.loader import render_to_string

def send_invoice_summary_to_customer_email(to_email, invoice, company_name, company_identifier, company_address, buyer_name,invoice_number, invoice_date,invoice_time, random_code, total_amount, buyer_identifier, line_description,line_quantity, unit_price):
    """
    寄送發票開立摘要報告郵件

    :param to_email: 收件者信箱
    :param success_count: 開立成功的發票數量
    :param excluded_count: 被排除的發票數量
    :param success_list: 成功發票清單（公司 + 發票號碼）
    :param excluded_list: 排除發票清單（公司 + 發票號碼 + 原因）
    """
    invoice_year = invoice_date.year
    invoice_month = invoice_date.month


    context = {
        "buyer_name": buyer_name,
        "invoice_year": invoice_year,
        "invoice_month": invoice_month,
        "invoice_date" :  invoice_date,
        "invoice_time" : invoice_time,
        "random_code" : random_code,
        "total_amount" : total_amount,
        "buyer_identifier" : buyer_identifier,
        "description" : line_description,
        "quantity" : line_quantity,
        "unit_price" : unit_price,
        "company_name": company_name,
        "company_identifier":company_identifier,
        "company_address":company_address,
        "invoice_number":invoice_number 
    }

    html_body = render_to_string(r"C:\Users\waylin\mydjango\e_invoice\templates\email_template\invoice_summary_to_custmer.html", context)


    send_email_to_customer_outlook(
        subject="發票開立通知",
        to_email=to_email,
        html_body=html_body,
        attachment_path="attachment_path",
        #inline_image_path="C:\\path\\to\\qrcode.png"
    )