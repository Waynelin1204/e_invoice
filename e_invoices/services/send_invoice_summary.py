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

def send_invoice_canceled_email(to_email, success_count, excluded_count, success_list, excluded_list):
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

    html_body = render_to_string(r"C:\Users\waylin\mydjango\e_invoice\templates\email_template\invoice_canceled.html", context)

    subject = f"本次成功作廢 {success_count} 張發票，排除 {excluded_count} 張"

    send_email_outlook(
        subject=subject,
        to_email=to_email,
        html_body=html_body
    )

def send_allowance_summary_email(to_email, success_count, excluded_count, success_list, excluded_list):
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

    html_body = render_to_string(r"C:\Users\waylin\mydjango\e_invoice\templates\email_template\allowance_summary.html", context)

    subject = f"本次成功開立 {success_count} 張折讓單，排除 {excluded_count} 張"

    send_email_outlook(
        subject=subject,
        to_email=to_email,
        html_body=html_body
    )

def send_allowance_canceled_email(to_email, success_count, excluded_count, success_list, excluded_list):
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

    html_body = render_to_string(r"C:\Users\waylin\mydjango\e_invoice\templates\email_template\allowance_canceled.html", context)

    subject = f"本次成功作廢 {success_count} 張折讓單，排除 {excluded_count} 張"

    send_email_outlook(
        subject=subject,
        to_email=to_email,
        html_body=html_body
    )

def send_insufficient_number_email(to_email, company_id, total_available, count_needed):
    """
    寄送發票開立摘要報告郵件

    :param to_email: 收件者信箱
    :param success_count: 開立成功的發票數量
    :param excluded_count: 被排除的發票數量
    :param success_list: 成功發票清單（公司 + 發票號碼）
    :param excluded_list: 排除發票清單（公司 + 發票號碼 + 原因）
    """

    context = {
        "company_id": company_id,
        "total_available": total_available,
        "count_needed": count_needed,
    }

    html_body = render_to_string(r"C:\Users\waylin\mydjango\e_invoice\templates\email_template\insufficient_number.html", context)

    subject = f"公司 {company_id} 的發票號碼存量不足提醒，需開立 {count_needed} 張，剩餘 {total_available} 張"
    send_email_outlook(
        subject=subject,
        to_email=to_email,
        html_body=html_body
    )

def send_number_low_storage_remind_email(to_email, company_id, total_available):
    """
    寄送發票開立摘要報告郵件

    :param to_email: 收件者信箱
    :param success_count: 開立成功的發票數量
    :param excluded_count: 被排除的發票數量
    :param success_list: 成功發票清單（公司 + 發票號碼）
    :param excluded_list: 排除發票清單（公司 + 發票號碼 + 原因）
    """

    context = {
        "company_id": company_id,
        "total_available": total_available,
    }

    html_body = render_to_string(r"C:\Users\waylin\mydjango\e_invoice\templates\email_template\number_low_storage.html", context)

    subject = f"公司 {company_id} 的發票號碼存量過低提醒,剩 {total_available} 張"
    send_email_outlook(
        subject=subject,
        to_email=to_email,
        html_body=html_body
    )
def send_invoice_deleted_email(to_email, deleted_count, deleted_list):
    
    context = {
        "deleted_count": deleted_count,
        "deleted_list": deleted_list,
    }

    html_body = render_to_string(r"C:\Users\waylin\mydjango\e_invoice\templates\email_template\deleted_number.html", context)

    subject = f"已刪除 {deleted_count} 張發票，請確認"
    send_email_outlook(
        subject=subject,
        to_email=to_email,
        html_body=html_body
    )

def send_allowance_deleted_email(to_email, deleted_count, deleted_list):
    
    context = {
        "deleted_count": deleted_count,
        "deleted_list": deleted_list,
    }

    html_body = render_to_string(r"C:\Users\waylin\mydjango\e_invoice\templates\email_template\deleted_allowance_number.html", context)

    subject = f"已刪除 {deleted_count} 張發票，請確認"
    send_email_outlook(
        subject=subject,
        to_email=to_email,
        html_body=html_body
    )