import os
import win32com.client as win32
import pythoncom
def send_email_outlook(subject, to_email, html_body, attachment_path=None):
    """
    使用 Outlook 寄送 email，支援 HTML 內容與附件。
    
    :param subject: 郵件主旨
    :param to_email: 收件者 email（可為逗號分隔字串）
    :param html_body: HTML 內容
    :param attachment_path: 檔案路徑（選填）
    """
    pythoncom.CoInitialize()
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0: 郵件類型

    mail.Subject = subject
    mail.To = to_email
    mail.HTMLBody = html_body  # 使用 HTML 格式內容

    if attachment_path and os.path.exists(attachment_path):
        mail.Attachments.Add(os.path.abspath(attachment_path))

    mail.Send()

def send_email_to_customer_outlook(subject, to_email, html_body, attachment_path=None):
    """
    使用 Outlook 寄送 email，支援 HTML 內容與附件。
    
    :param subject: 郵件主旨
    :param to_email: 收件者 email（可為逗號分隔字串）
    :param html_body: HTML 內容
    :param attachment_path: 檔案路徑（選填）
    """
    pythoncom.CoInitialize()
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0: 郵件類型

    mail.Subject = subject
    mail.To = to_email
    mail.HTMLBody = html_body  # 使用 HTML 格式內容

    if attachment_path and os.path.exists(attachment_path):
        mail.Attachments.Add(os.path.abspath(attachment_path))

    mail.Send()
