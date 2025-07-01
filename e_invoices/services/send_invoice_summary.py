# e_invoices/services/email_summary_service.py

from e_invoices.services.auto_send_email_service import send_email_outlook
from django.template.loader import render_to_string

def send_invoice_summary_email(to_email, success_count, excluded_count, success_list, excluded_list):
    """
    寄送發票開立摘要報告郵件

    :param to_email: 收件者信箱
    :param success_count: 開立成功的發票數量
    :param excluded_count: 被排除的發票數量
    :param success_list: 成功發票清單（公司 + 發票號碼）
    :param excluded_list: 排除發票清單（公司 + 發票號碼 + 原因）
    """

    context = {
        "success_count": success_count,
        "excluded_count": excluded_count,
        "success_list": success_list,
        "excluded_list": excluded_list,
    }

    html_body = render_to_string(r"C:\Users\waylin\mydjango\e_invoice\templates\email_template\invoice_summary.html", context)

    subject = f"本次成功開立 {success_count} 張發票，排除 {excluded_count} 張"

    send_email_outlook(
        subject=subject,
        to_email=to_email,
        html_body=html_body
    )
